#!/usr/bin/env python3
"""生成 1925 词表独立页面（V6 同款：剑桥官方释义 + 美音 + 朗读）。

用法：
  python3 build_1925.py output/cambridge_defs_1925.json my-tofel-1925words-words.txt my-tofel-1925-words.html

模板复用 1791 V6 页面骨架，替换：
  - 标题/徽标/链接（1791 -> 1925）
  - DEFAULT_WORDS 数据
  - CAMBRIDGE 数据
"""
import json
import re
import sys


def js_str(s: str) -> str:
    s = s.replace("\\", "\\\\").replace("'", "\\'")
    s = s.replace("\n", "\\n").replace("\r", "")
    out = []
    for ch in s:
        o = ord(ch)
        if o < 0x20:
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    return "'" + "".join(out) + "'"


def load_words(path):
    """读 my-tofel-1925words-words.txt -> [(word_orig, word_clean, zh)]"""
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        w = parts[0].strip()
        zh = parts[1].strip() if len(parts) > 1 else ""
        w2 = re.sub(r"^[a-z]+\s*\.\s*", "", w, flags=re.I).replace("`", "")
        out.append((w, w2, zh))
    return out


def build_default_words(words_order):
    """生成 DEFAULT_WORDS JS（保持原词条文本 + 中文释义，含 [ph]/[st]/[mean] 标记原样）。"""
    entries = [f"[{js_str(w)},{js_str(zh)}]" for w, _w2, zh in words_order]
    return "const DEFAULT_WORDS = [" + ",".join(entries) + "];"


def build_cambridge_js(data, words_order):
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


def main():
    cam_path = sys.argv[1] if len(sys.argv) > 1 else "output/cambridge_defs_1925.json"
    txt_path = sys.argv[2] if len(sys.argv) > 2 else "my-tofel-1925words-words.txt"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "my-tofel-1925-words.html"
    tpl_path = sys.argv[4] if len(sys.argv) > 4 else "my-tofel-1791words-words.html"

    cam_data = json.load(open(cam_path, encoding="utf-8"))
    words_order = load_words(txt_path)
    tpl = open(tpl_path, encoding="utf-8").read()

    # 1) 替换 DEFAULT_WORDS
    default_js = build_default_words(words_order)
    m = re.search(r"const DEFAULT_WORDS = \[.*?\];", tpl, re.S)
    if not m:
        raise RuntimeError("模板中找不到 DEFAULT_WORDS")
    tpl = tpl[:m.start()] + default_js + tpl[m.end():]

    # 2) 替换 CAMBRIDGE
    cam_js = build_cambridge_js(cam_data, words_order)
    m = re.search(r"const CAMBRIDGE = \{.*?\n\};", tpl, re.S)
    if not m:
        raise RuntimeError("模板中找不到 CAMBRIDGE")
    tpl = tpl[:m.start()] + cam_js + tpl[m.end():]

    # 3) 标题
    tpl = tpl.replace("<title>TOEFL 1791 单词本</title>", "<title>TOEFL 1925 单词本</title>", 1)
    # 4) 标题栏徽标
    tpl = re.sub(
        r'<div class="title">单词本 <span[^>]*>V6</span></div>',
        '<div class="title">1925 单词本 <span style="font-size:11px;color:#34c77b;background:rgba(52,199,123,.15);border:1px solid rgba(52,199,123,.4);border-radius:6px;padding:1px 6px;margin-left:4px">V1</span></div>',
        tpl, count=1,
    )
    # 5) 导航链接
    tpl = tpl.replace('<a class="link-btn" href="my-tofel-1675-words.html">→ 1675</a>',
                      '<a class="link-btn" href="my-tofel-1791words-words.html">→ 1791</a>', 1)

    n = len(re.findall(r"^\s{2}'[^']+': \{", cam_js, re.M))
    open(out_path, "w", encoding="utf-8").write(tpl)
    print(f"1925 页面生成完成：{len(words_order)} 词，{n} 词命中剑桥释义 -> {out_path}")


if __name__ == "__main__":
    main()
