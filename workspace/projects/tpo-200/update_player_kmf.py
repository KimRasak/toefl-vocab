#!/usr/bin/env python3
"""把 KMF 官方原文嵌入播放器，支持 KMF/原版 来源切换。
用法: python3 update_player_kmf.py
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, '托福TPO听力原文播放器.html')
SUBS_DIR = os.path.join(BASE, 'subtitles_kmf')


def parse_srt(srt_text):
    cues = []
    for block in srt_text.strip().split('\n\n'):
        lines = block.split('\n')
        if len(lines) < 2:
            continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', lines[1])
        if not m:
            continue
        start = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                 + int(m.group(4)) / 1000)
        end = (int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7))
               + int(m.group(8)) / 1000)
        text = ' '.join(l.strip() for l in lines[2:] if l.strip())
        cues.append({"start": round(start, 1), "end": round(end, 1), "text": text})
    return cues


def main():
    html = open(HTML, encoding='utf-8').read()

    # 1. 生成 SUBS_kmf
    subs_kmf = {}
    for f in sorted(os.listdir(SUBS_DIR)):
        if not f.endswith('.srt'):
            continue
        idx = str(int(re.match(r'p(\d+)', f).group(1)))  # 无前导零
        cues = parse_srt(open(os.path.join(SUBS_DIR, f), encoding='utf-8').read())
        if cues:
            subs_kmf[idx] = cues
    json_kmf = json.dumps(subs_kmf, ensure_ascii=False)
    print(f"SUBS_kmf: {len(subs_kmf)} 集, {len(json_kmf)/1024/1024:.2f} MB")

    # 检查危险字符
    if '</script' in json_kmf.lower():
        # 转义
        json_kmf = json_kmf.replace('</script', '<\\/script')
        print("  已转义 </script>")

    # 2. 现有 SUBS 改名 SUBS_bili
    m = re.search(r'const SUBS = (\{.*?\});\n(?=const ITEMS)', html, re.S)
    if not m:
        print("ERROR: 未找到 const SUBS")
        return
    bili_json = m.group(1)
    html = html[:m.start()] + f'const SUBS_bili = {bili_json};\nconst SUBS_kmf = {json_kmf};\n' + html[m.end():]
    print(f"SUBS_bili 保留: {len(bili_json)/1024/1024:.2f} MB")

    # 3. 修改 loadSubs: 用来源切换
    old_load = """function loadSubs(idx) {
  cues = [];
  subBox.innerHTML = '';
  const it = ITEMS.find(x => x.idx === idx);
  if (!it || !subOn) { subBox.classList.remove('show'); return; }
  const list = SUBS[idx];
  if (list && list.length) {
    cues = list;
    subBox.innerHTML = cues.map((c, i) => `<div class="cue" data-i="${i}">${c.text}</div>`).join('');
    subBox.classList.add('show');
  } else {
    subBox.innerHTML = '（本集暂无字幕）';
    subBox.classList.add('show');
  }
}"""
    new_load = """let srcMode = localStorage.getItem('tofel_kmf_src') !== '0' ? 'kmf' : 'bili';
function setSrcMode(mode) {
  srcMode = mode;
  localStorage.setItem('tofel_kmf_src', mode === 'kmf' ? '1' : '0');
  const btn = document.getElementById('srcToggle');
  if (btn) {
    btn.textContent = mode === 'kmf' ? '来源：KMF官方' : '来源：原版';
    btn.classList.toggle('kmf', mode === 'kmf');
  }
  if (curIdx) select(curIdx, false);
}
function loadSubs(idx) {
  cues = [];
  subBox.innerHTML = '';
  const it = ITEMS.find(x => x.idx === idx);
  if (!it || !subOn) { subBox.classList.remove('show'); return; }
  const list = srcMode === 'kmf' ? (SUBS_kmf[idx] || SUBS_bili[idx]) : (SUBS_bili[idx] || SUBS_kmf[idx]);
  if (list && list.length) {
    cues = list;
    subBox.innerHTML = cues.map((c, i) => `<div class="cue" data-i="${i}">${c.text}</div>`).join('');
    subBox.classList.add('show');
  } else {
    subBox.innerHTML = '（本集暂无字幕）';
    subBox.classList.add('show');
  }
}"""
    if old_load not in html:
        print("WARNING: 未匹配 loadSubs 旧代码")
    else:
        html = html.replace(old_load, new_load)
        print("loadSubs 已更新")

    # 4. 修改 select(): 音频路径用 audio_kmf/，标题显示来源
    old_sel = """  nowTitle.textContent = `p${String(idx).padStart(3,'0')} · ${it.short}`;
  nowSub.textContent = it.has ? `时长 ${it.dur} · 本地文件 audio/p${String(idx).padStart(3,'0')}_${it.short}.mp3` : '该集音频未下载';
  audio.src = it.has ? `audio/p${String(idx).padStart(3,'0')}_${it.short}.mp3` : '';"""
    new_sel = """  nowTitle.textContent = `p${String(idx).padStart(3,'0')} · ${it.short}`;
  const srcDir = srcMode === 'kmf' ? 'audio_kmf' : 'audio';
  const srcLabel = srcMode === 'kmf' ? 'KMF官方' : '原版';
  nowSub.textContent = it.has ? `时长 ${it.dur} · ${srcLabel} audio_${srcMode === 'kmf' ? 'kmf' : 'bili'}/p${String(idx).padStart(3,'0')}_${it.short}.mp3` : '该集音频未下载';
  audio.src = it.has ? `${srcDir}/p${String(idx).padStart(3,'0')}_${it.short}.mp3` : '';"""
    if old_sel not in html:
        print("WARNING: 未匹配 select 旧代码")
    else:
        html = html.replace(old_sel, new_sel)
        print("select 已更新")

    # 5. 加来源切换按钮到工具栏（在 endMode 后）
    old_btn = """    <label for="endMode" style="font-size:13px;color:var(--muted);display:flex;align-items:center;gap:6px;">播放结束后
      <select id="endMode">"""
    new_btn = """    <button id="srcToggle" title="切换音频与字幕来源：KMF官方 / 原版B站" style="font-size:13px;padding:5px 10px;border:1px solid var(--border,#ccc);border-radius:6px;background:#fff;cursor:pointer;">来源：KMF官方</button>
    <label for="endMode" style="font-size:13px;color:var(--muted);display:flex;align-items:center;gap:6px;">播放结束后
      <select id="endMode">"""
    if old_btn not in html:
        print("WARNING: 未匹配按钮位置")
    else:
        html = html.replace(old_btn, new_btn)
        print("来源按钮已添加")

    # 6. 在初始化部分调用 setSrcMode
    old_init = """render();"""
    # 找初始化 render() 的位置（文件末尾附近）
    idx_init = html.rfind(old_init)
    if idx_init < 0:
        print("WARNING: 未找到初始化 render()")
    else:
        # 在 render() 前加 setSrcMode 初始化 + 按钮事件
        insert = """const srcBtn = document.getElementById('srcToggle');
if (srcBtn) srcBtn.onclick = () => setSrcMode(srcMode === 'kmf' ? 'bili' : 'kmf');
setSrcMode(srcMode);
render();"""
        html = html[:idx_init] + insert + html[idx_init + len(old_init):]
        print("初始化已添加")

    # 7. 保存
    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n已保存: {HTML} ({os.path.getsize(HTML)/1024/1024:.2f} MB)")


if __name__ == '__main__':
    main()
