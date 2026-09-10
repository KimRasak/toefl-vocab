#!/usr/bin/env python3
"""把困难短语标注 JSON 应用到 KMF 字幕，生成带 **标记 的高亮版 SRT。
输入: /tmp/hl_out/*.json (标注) + subtitles_kmf/*.srt (原字幕)
输出: subtitles_kmf_hl/*.srt (困难短语用 **...** 包裹)
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE, "subtitles_kmf")
HL_DIR = os.path.join(BASE, "subtitles_kmf_hl")
OUT_JSON = "/tmp/hl_out"


def apply_hl(sentence, phrases):
    """在句子中用 ** 包裹困难短语"""
    result = sentence
    for ph in sorted(phrases, key=len, reverse=True):
        if not ph:
            continue
        # 精确匹配（忽略大小写），替换时保留原文大小写
        pattern = re.compile(r'(?<!\*)\b' + re.escape(ph) + r'\b(?!\*)', re.IGNORECASE)
        result = pattern.sub(lambda m: f"**{m.group(0)}**", result)
    return result


def main():
    os.makedirs(HL_DIR, exist_ok=True)
    src_files = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".srt"))
    ok, no_hl, miss_json = 0, 0, []

    for fname in src_files:
        base = fname[:-4]  # 去掉 .srt
        json_path = os.path.join(OUT_JSON, base + ".json")
        if not os.path.exists(json_path):
            miss_json.append(base)
            continue

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        cues_map = {c["line"]: c.get("phrases", []) for c in data.get("cues", [])}

        srt = open(os.path.join(SRC_DIR, fname), encoding="utf-8").read()
        blocks = srt.strip().split("\n\n")
        out_blocks = []
        hl_count = 0
        for block in blocks:
            lines = block.split("\n")
            if len(lines) < 3:
                out_blocks.append(block)
                continue
            # 找序号行
            try:
                num = int(lines[0].strip())
            except ValueError:
                out_blocks.append(block)
                continue
            text = " ".join(l.strip() for l in lines[2:] if l.strip())
            phrases = cues_map.get(num, [])
            if phrases:
                text = apply_hl(text, phrases)
                hl_count += 1
            out_lines = lines[:2] + [text]
            out_blocks.append("\n".join(out_lines))

        with open(os.path.join(HL_DIR, fname), "w", encoding="utf-8") as f:
            f.write("\n\n".join(out_blocks) + "\n")
        if hl_count:
            ok += 1
        else:
            no_hl += 1

    print(f"生成完成: 有标注 {ok}, 无标注 {no_hl}, 缺JSON {len(miss_json)}")
    if miss_json:
        print("缺 JSON:", miss_json[:20])


if __name__ == "__main__":
    main()
