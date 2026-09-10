#!/usr/bin/env python3
"""后处理所有 SRT：清洗 OCR 杂音 + 合并重复字幕（含数字变体）。"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(HERE, "subtitles")


def clean_text(t):
    """修复 OCR 常见错误"""
    # 数字序数词变体: "2l st" / "2lst" / "21st" -> "21st"
    t = re.sub(r"(\d)l\s*st", r"\1st", t, flags=re.I)
    t = re.sub(r"(?<=\d)l(?=\d)", "1", t)  # 2l -> 21
    t = re.sub(r"(?<=\d)o(?=\d)", "0", t)  # 2o -> 20
    # 标点杂音
    t = t.replace("|", "").replace(",,", ",").replace("..", ".")
    t = re.sub(r"[•¾§¶†‡]", "", t)  # 特殊符号
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)  # 标点前空格
    t = re.sub(r"\s+", " ", t).strip()
    return t


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
        text = clean_text(" ".join(lines[t_idx+1:]))
        if text:
            cues.append({"start": start, "end": end, "text": text})
    return cues


def norm(t):
    # 去掉所有非字母数字字符（保留撇号），用于比较
    t = t.lower()
    t = re.sub(r"[^a-z0-9']+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def similarity(a, b):
    """编辑距离相似度（0-1）"""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def merge(cues):
    """合并重复：相邻同文合并；相邻高相似度合并；非相邻近距同文合并"""
    if not cues:
        return cues
    merged = []
    for c in cues:
        key = norm(c["text"])
        if merged and merged[-1]["key"] == key:
            merged[-1]["end"] = max(merged[-1]["end"], c["end"])
            if "*" not in c["text"] and "*" in merged[-1]["text"]:
                merged[-1]["text"] = c["text"]
        else:
            merged.append({"start": c["start"], "end": c["end"], "text": c["text"], "key": key})
    # 第二遍：合并相邻高相似度段（OCR 变体，如 d/a、quietitime/quiet time）
    merged2 = []
    for c in merged:
        if merged2 and merged2[-1]["end"] >= c["start"] - 0.5 and similarity(merged2[-1]["key"], c["key"]) > 0.92:
            # 选更长的文本（通常更完整）
            if len(c["text"]) > len(merged2[-1]["text"]):
                merged2[-1]["text"] = c["text"]
            merged2[-1]["end"] = max(merged2[-1]["end"], c["end"])
        else:
            merged2.append(c)
    # 第三遍：合并同 key 且间隔 < 3s
    final = []
    i = 0
    while i < len(merged2):
        cur = merged2[i]
        j = i + 1
        while j < len(merged2):
            nxt = merged2[j]
            if nxt["key"] == cur["key"] and nxt["start"] - cur["end"] < 3:
                cur["end"] = max(cur["end"], nxt["end"])
                j += 1
            else:
                break
        final.append({"start": cur["start"], "end": cur["end"], "text": cur["text"]})
        i = j
    return final


def to_srt(cues):
    out = []
    for i, c in enumerate(cues, 1):
        def fmt(t):
            h = int(t // 3600); mi = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
            if ms >= 1000: s += 1; ms -= 1000
            return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"
        out.append(f"{i}\n{fmt(c['start'])} --> {fmt(c['end'])}\n{c['text']}\n")
    return "\n".join(out)


def main():
    files = sorted(glob.glob(os.path.join(SUB_DIR, "*.srt")))
    total_before = total_after = 0
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        cues = parse_srt(text)
        total_before += len(cues)
        merged = merge(cues)
        total_after += len(merged)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(to_srt(merged))
    print(f"处理 {len(files)} 个 SRT: 段数 {total_before} -> {total_after}")


if __name__ == "__main__":
    main()
