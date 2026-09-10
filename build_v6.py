#!/usr/bin/env python3
"""把剑桥官方释义数据合入 1791 词页面，生成 V6（官方释义 + 释义句朗读）。

用法：
  python3 build_v6.py output/cambridge_defs_1791.json my-tofel-1791words-words.html my-tofel-1791words-words.html

V6 改动：
1. 数据：新增内嵌 CAMBRIDGE 对象（词 -> {ipa, mp3, defs, examples}）
2. playWord：剑桥官方美音 mp3 -> 有道 -> Google TTS（三级降级）
3. 列表项：中文释义下方新增"剑桥官方释义"区块（音标 + 释义列表 + 例句，均带朗读按钮）
4. 朗读：Google TTS -> speechSynthesis 兜底
"""
import json
import re
import sys


def read_words_txt(path: str):
    """从 1791 txt 读出 [(word, zh)] 保序列表（用于与剑桥数据对齐 + 中文释义）。"""
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        w = line.split("\t")[0].strip()
        zh = line.split("\t")[1].strip() if "\t" in line else ""
        w2 = re.sub(r"^[a-z]+\s*\.\s*", "", w, flags=re.I).replace("`", "")
        out.append((w, w2, zh))
    return out


def js_str(s: str) -> str:
    """转成 JS 单引号字符串字面量（安全）。"""
    s = s.replace("\\", "\\\\").replace("'", "\\'")
    s = s.replace("\n", "\\n").replace("\r", "")
    # 控制字符转 \uXXXX
    out = []
    for ch in s:
        o = ord(ch)
        if o < 0x20:
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    return "'" + "".join(out) + "'"


def build_cambridge_js(data: dict, words_order: list) -> str:
    """生成 CAMBRIDGE 对象 JS 源码，按词表顺序排列（命中才收录）。"""
    lines = ["const CAMBRIDGE = {"]
    for w, w2, _zh in words_order:
        if w2 not in data:
            continue
        d = data[w2]
        lines.append("  " + js_str(w) + ": {")
        if d.get("ipa"):
            lines.append("    ipa: " + js_str(d["ipa"]) + ",")
        if d.get("us_mp3_url"):
            lines.append("    mp3: " + js_str(d["us_mp3_url"]) + ",")
        defs = [x for x in d.get("defs", []) if x]
        if defs:
            lines.append("    defs: [" + ",".join(js_str(x) for x in defs) + "],")
        exs = [x for x in d.get("examples", []) if x][:4]
        if exs:
            lines.append("    exs: [" + ",".join(js_str(x) for x in exs) + "]")
        lines.append("  },")
    lines.append("};")
    return "\n".join(lines)


def build_v6(cam_data: dict, src_html: str, words_order: list) -> str:
    cam_js = build_cambridge_js(cam_data, words_order)
    n = len(re.findall(r"^\s{2}'[^']+': \{", cam_js, re.M))

    # 1) 在 DEFAULT_WORDS 声明之后插入 CAMBRIDGE 数据
    anchor = "const SPEAKER_SVG"
    assert anchor in src_html, "找不到 SPEAKER_SVG 锚点"
    src_html = src_html.replace(anchor, cam_js + "\n\n" + anchor, 1)

    # 2) 替换 playWord：剑桥官方美音优先三级降级
    old_play = '''function playWord(word, btn){
  const clean = word.replace(/'/g, "").replace(/^[^A-Za-z]+/, "").replace(/[^A-Za-z-].*$/, "");
  if(!clean){ toast("无法播放：" + word); return; }
  const url = "https://dict.youdao.com/dictvoice?audio=" + encodeURIComponent(clean) + "&type=2";
  if(audioEl){
    audioEl.onerror = null; audioEl.onended = null;
    audioEl.pause();
  } else {
    audioEl = new Audio();
  }
  let fallback = false;
  audioEl.onerror = () => {
    if(fallback) return;
    fallback = true;
    audioEl.src = "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=" + encodeURIComponent(clean);
    audioEl.play().catch(() => {});
  };
  audioEl.onended = () => {
    if(btn){ btn.classList.remove("playing"); }
  };
  audioEl.src = url;
  if(btn) btn.classList.add("playing");
  audioEl.play().catch(() => {
    if(btn) btn.classList.remove("playing");
    if(!fallback){ audioEl.onerror && audioEl.onerror(); }
  });
}'''
    new_play = '''function playWord(word, btn){
  const clean = word.replace(/'/g, "").replace(/^[^A-Za-z]+/, "").replace(/[^A-Za-z-].*$/, "");
  if(!clean){ toast("无法播放：" + word); return; }
  if(audioEl){
    audioEl.onerror = null; audioEl.onended = null;
    audioEl.pause();
  } else {
    audioEl = new Audio();
  }
  // 发音三级降级：剑桥官方美音 -> 有道美音 -> Google TTS
  const urls = [];
  const cam = CAMBRIDGE[word];
  if(cam && cam.mp3){ urls.push(cam.mp3); }
  urls.push("https://dict.youdao.com/dictvoice?audio=" + encodeURIComponent(clean) + "&type=2");
  urls.push("https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=" + encodeURIComponent(clean));
  let i = 0;
  function tryNext(){
    if(i >= urls.length){
      if(btn){ btn.classList.remove("playing"); }
      toast("发音不可用：" + word);
      return;
    }
    audioEl.onerror = () => { i++; tryNext(); };
    audioEl.onended = () => { if(btn){ btn.classList.remove("playing"); } };
    audioEl.src = urls[i];
    if(btn){ btn.classList.add("playing"); }
    audioEl.play().catch(() => { i++; tryNext(); });
  }
  tryNext();
}

// 朗读整句（官方释义/例句）：Google TTS -> speechSynthesis 兜底
function speakSentence(text, btn){
  const clean = String(text).replace(/\\s+/g, " ").trim();
  if(!clean){ return; }
  if(audioEl){
    audioEl.onerror = null; audioEl.onended = null;
    audioEl.pause();
  } else {
    audioEl = new Audio();
  }
  let fallback = false;
  audioEl.onerror = () => {
    if(fallback) return;
    fallback = true;
    if(btn){ btn.classList.remove("playing"); }
    try {
      const u = new SpeechSynthesisUtterance(clean);
      u.lang = "en-US"; u.rate = 0.95;
      u.onend = () => { if(btn){ btn.classList.remove("playing"); } };
      u.onerror = () => { if(btn){ btn.classList.remove("playing"); } };
      if(btn){ btn.classList.add("playing"); }
      speechSynthesis.cancel();
      speechSynthesis.speak(u);
    } catch(e){ if(btn){ btn.classList.remove("playing"); } }
  };
  audioEl.onended = () => { if(btn){ btn.classList.remove("playing"); } };
  audioEl.src = "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=" + encodeURIComponent(clean);
  if(btn){ btn.classList.add("playing"); }
  audioEl.play().catch(() => { audioEl.onerror && audioEl.onerror(); });
}'''
    assert old_play in src_html, "找不到原 playWord"
    src_html = src_html.replace(old_play, new_play, 1)

    # 3) 渲染列表项：中文释义下方加官方释义区块
    old_render = '''      return '<div class="item"><div class="w">'+ idx +'. '+ hi(w, query) +
             '<span class="wtext" style="display:none">' + esc(w) + '</span>' +
             '<button class="wbtn" type="button" data-word="' + esc(w) + '" title="播放发音" aria-label="播放 ' + esc(w) + '">' + SPEAKER_SVG + '</button>' + EDIT_BTN_HTML + '</div>' +
             '<div class="m">'+ hi(m, query) +'</div></div>';'''
    new_render = '''      const cam = CAMBRIDGE[w];
      let extra = "";
      if(cam){
        let defRows = "";
        if(cam.defs && cam.defs.length){
          defRows = cam.defs.map(function(d, j){
            return '<div class="drow"><span class="dnum">' + (j+1) + '</span>' +
              '<span class="dtxt">' + hi(d, query) + '</span>' +
              '<button class="sbtn" type="button" data-speak="' + esc(d) + '" title="朗读释义" aria-label="朗读释义">' + SPEAKER_SVG + '</button></div>';
          }).join("");
        }
        let exRows = "";
        if(cam.exs && cam.exs.length){
          exRows = cam.exs.map(function(e){
            return '<div class="exrow"><span class="ext">' + hi(e, query) + '</span>' +
              '<button class="sbtn" type="button" data-speak="' + esc(e) + '" title="朗读例句" aria-label="朗读例句">' + SPEAKER_SVG + '</button></div>';
          }).join("");
        }
        extra = '<div class="camsec">' +
          (cam.ipa ? '<div class="camh"><span class="cipa">/' + esc(cam.ipa) + '/</span><span class="ctag">Cambridge</span></div>' : '<div class="camh"><span class="ctag">Cambridge</span></div>') +
          (defRows ? '<div class="dlist">' + defRows + '</div>' : '') +
          (exRows ? '<div class="exsec2"><div class="exlabel">例句</div>' + exRows + '</div>' : '') +
          '</div>';
      }
      return '<div class="item"><div class="w">'+ idx +'. '+ hi(w, query) +
             '<span class="wtext" style="display:none">' + esc(w) + '</span>' +
             '<button class="wbtn" type="button" data-word="' + esc(w) + '" title="播放发音" aria-label="播放 ' + esc(w) + '">' + SPEAKER_SVG + '</button>' + EDIT_BTN_HTML + '</div>' +
             '<div class="m">'+ hi(m, query) +'</div>' + extra + '</div>';'''
    assert old_render in src_html, "找不到原 render 列表项"
    src_html = src_html.replace(old_render, new_render, 1)

    # 4) 点击事件：加 sbtn 朗读
    old_click = '''document.addEventListener("click", e => {
  const btn = e.target.closest(".wbtn");
  if(btn && btn.dataset.word){
    playWord(btn.dataset.word, btn);
  }
});'''
    new_click = '''document.addEventListener("click", e => {
  const btn = e.target.closest(".wbtn");
  if(btn && btn.dataset.word){
    playWord(btn.dataset.word, btn);
    return;
  }
  const sb = e.target.closest(".sbtn");
  if(sb && sb.dataset.speak){
    speakSentence(sb.dataset.speak, sb);
  }
});'''
    assert old_click in src_html, "找不到原点击事件"
    src_html = src_html.replace(old_click, new_click, 1)

    # 5) CSS：官方释义区块样式（插到 .item .m 规则后）
    old_css = "  .item .m { font-size:14px; color:var(--muted); margin-top:4px; line-height:1.5; }"
    new_css = old_css + """
  .camsec { margin-top:10px; border-top:1px dashed var(--border); padding-top:9px; }
  .camh { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
  .cipa { font-size:13px; color:var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; }
  .ctag { font-size:11px; color:var(--accent); background:rgba(76,141,255,.13); border-radius:5px; padding:1px 7px; font-weight:600; letter-spacing:.3px; }
  .dlist { display:flex; flex-direction:column; gap:4px; }
  .drow { display:flex; align-items:flex-start; gap:7px; font-size:13.5px; line-height:1.5; background:var(--card2); border:1px solid var(--border); border-radius:8px; padding:5px 9px; }
  .dnum { color:var(--muted); font-size:11px; flex:0 0 auto; margin-top:2px; font-family: ui-monospace, monospace; }
  .dtxt { flex:1 1 auto; min-width:0; }
  .sbtn { flex:0 0 auto; background:none; border:0; padding:2px; cursor:pointer; color:var(--accent); display:inline-flex; align-items:center; opacity:.8; }
  .sbtn:hover { opacity:1; }
  .sbtn svg { display:block; }
  .sbtn.playing circle { fill:#34c77b; }
  .exsec2 { margin-top:7px; }
  .exlabel { font-size:11px; color:var(--muted); margin-bottom:3px; font-weight:600; }
  .exrow { display:flex; align-items:flex-start; gap:7px; font-size:12.5px; line-height:1.5; color:var(--muted); padding:2px 0 2px 2px; }
  .ext { flex:1 1 auto; min-width:0; }"""
    assert old_css in src_html, "找不到 .item .m CSS"
    src_html = src_html.replace(old_css, new_css, 1)

    # 6) 版本号 V5 -> V6
    src_html = src_html.replace(">V5<", ">V6<", 1)

    return src_html, n


def main():
    cam_path = sys.argv[1] if len(sys.argv) > 1 else "output/cambridge_defs_1791.json"
    src_path = sys.argv[2] if len(sys.argv) > 2 else "my-tofel-1791words-words.html"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "my-tofel-1791words-words.html"
    txt_path = sys.argv[4] if len(sys.argv) > 4 else "my-tofel-1791words-words.txt"

    cam_data = json.load(open(cam_path, encoding="utf-8"))
    words_order = read_words_txt(txt_path)
    src_html = open(src_path, encoding="utf-8").read()

    html, n = build_v6(cam_data, src_html, words_order)
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"V6 生成完成：{n} 词命中剑桥释义 -> {out_path}")


if __name__ == "__main__":
    main()
