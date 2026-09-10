#!/usr/bin/env python3
"""把 subtitles/*.srt 内嵌进播放器 HTML，使 file:// 打开也能显示字幕。"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(HERE, "subtitles")
HTML_PATH = os.path.join(HERE, "托福TPO听力原文播放器.html")


def parse_srt(text):
    cues = []
    blocks = re.split(r"\n\s*\n", text.replace("\r", ""))
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip()]
        t_idx = None
        for i, l in enumerate(lines):
            if "-->" in l:
                t_idx = i
                break
        if t_idx is None:
            continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", lines[t_idx])
        if not m:
            continue
        def ts(g):
            return int(m.group(g*4-3))*3600 + int(m.group(g*4-2))*60 + int(m.group(g*4-1)) + int(m.group(g*4))/1000
        start, end = ts(1), ts(2)
        text = " ".join(lines[t_idx+1:])
        if text:
            cues.append({"start": round(start, 3), "end": round(end, 3), "text": text})
    return cues


def normalize(t):
    """归一化：小写、去 OCR 杂音（*、多余空格），用于比较是否同一句"""
    t = t.lower().replace("*", "").replace("−", "-").replace("- ", " ")
    return re.sub(r"\s+", " ", t).strip()


def merge_cues(cues):
    """合并相邻重复字幕（OCR 抖动导致同一句拆成多段）"""
    if not cues:
        return cues
    merged = []
    for c in cues:
        key = normalize(c["text"])
        if merged and merged[-1]["key"] == key:
            prev = merged[-1]
            prev["end"] = max(prev["end"], c["end"])
            if "*" not in c["text"] and "*" in prev["text"]:
                prev["text"] = c["text"]
        else:
            merged.append({"start": c["start"], "end": c["end"], "text": c["text"], "key": key})
    # 去重相邻同 key（理论上第一轮已处理，防御性保留）
    final = []
    for i, m_ in enumerate(merged):
        if i > 0 and m_["key"] == merged[i-1]["key"]:
            continue
        final.append({"start": m_["start"], "end": m_["end"], "text": m_["text"]})
    return final


def load_subs():
    subs = {}
    if not os.path.isdir(SUB_DIR):
        return subs
    for fn in sorted(os.listdir(SUB_DIR)):
        if not fn.endswith(".srt"):
            continue
        m = re.match(r"p(\d+)_", fn)
        if not m:
            continue
        idx = int(m.group(1))
        try:
            with open(os.path.join(SUB_DIR, fn), encoding="utf-8") as f:
                cues = parse_srt(f.read())
            cues = merge_cues(cues)
            if cues:
                subs[idx] = cues
        except Exception as e:
            print(f"  warn: {fn}: {e}")
    return subs


def main():
    if not os.path.exists(HTML_PATH):
        print("HTML 不存在:", HTML_PATH)
        return
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()

    subs = load_subs()
    subs_json = json.dumps(subs, ensure_ascii=False)
    print(f"内嵌字幕: {len(subs)} 集")

    # 1) 在 const ITEMS 后插入 const SUBS
    if "const SUBS =" not in html:
        html = html.replace(
            "const ITEMS = ",
            f"const SUBS = {subs_json};\nconst ITEMS = ",
            1,
        )
    else:
        # SUBS 可能是数组或对象格式
        html = re.sub(r"const SUBS = (\[.*?\]|\{.*?\});\n(?=const ITEMS)", f"const SUBS = {subs_json};\n", html, count=1, flags=re.S)

    # 2) 把 loadSubs 改为读内嵌 SUBS（替换整个函数体）
    old_load = re.search(r"function loadSubs\(idx\) \{.*?\n\}", html, re.S)
    if old_load:
        new_load = """function loadSubs(idx) {
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
        html = html[:old_load.start()] + new_load + html[old_load.end():]
    else:
        print("  !! 未找到 loadSubs 函数")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("已更新:", HTML_PATH)


if __name__ == "__main__":
    main()
