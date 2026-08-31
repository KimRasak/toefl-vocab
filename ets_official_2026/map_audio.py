#!/usr/bin/env python3
"""把 ETS 官方音频 ZIP 里的文件与 listening_2026.json 的题目对应起来。

命名规律（两种批次混用 .ogg / .mp3，目录名也不统一）：
  Listening{M}_Question Response_Question{K}     单条听答题（M=Module, K=1..8）
  Listening{M}_..._Questions_{a}-{b}             一个原文块，覆盖第 a..b 题
  Listening{M}_..._Directions_{a}-{b}            该块的指导语（不含原文，仅作参考）

在每个条目上写入：
  choose_response → "audio": "<zip>::<内部路径>"
  其它三类        → "audio": "...Questions...", "audio_directions": "...Directions..."
"""
import json, os, re, zipfile, glob

BASE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(BASE, "listening_2026.json")

# 卷名 → 音频 zip
ZIP_FOR = {
    "toefl-ibt-full-length-practice-test-1": "student-practice-test-1-audio-files.zip",
    "toefl-ibt-full-length-practice-test-2": "student-practice-test-2-audio-files.zip",
    "toefl-ibt-teachers-resources-practice-test-1": "teacher-practice-test-1-audio-file.zip",
    "toefl-ibt-teachers-resources-practice-test-2": "teacher-practice-test-2-audio-file.zip",
    "toefl-ibt-teachers-resources-practice-test-3": "teacher-practice-test-3-audio.zip",
    "toefl-ibt-teachers-resources-practice-test-4": "teacher-practice-test-4-audio-files.zip",
    "toefl-ibt-teachers-resources-practice-test-5": "teacher-practice-test-5-audio-files.zip",
}

AUD = re.compile(r"\.(ogg|mp3|wav|m4a)$", re.I)
MOD = re.compile(r"Listening(\d)", re.I)
SINGLE = re.compile(r"Question(\d+)\s*$", re.I)
RANGE = re.compile(r"(?:Questions?|Directions?)_?\s*(\d+)\s*-\s*(\d+)", re.I)


def index_zip(path):
    """返回 (单条听答题索引, 原文块索引)。"""
    single, blocks = {}, []
    if not os.path.exists(path):
        return single, blocks
    for n in zipfile.ZipFile(path).namelist():
        if not AUD.search(n) or "/Speaking/" in n:
            continue
        stem = os.path.splitext(os.path.basename(n))[0]
        mm = MOD.search(stem)
        if not mm:
            continue
        mod = int(mm.group(1))
        mr = RANGE.search(stem)
        if mr:
            blocks.append({"module": mod, "lo": int(mr.group(1)), "hi": int(mr.group(2)),
                           "directions": "direction" in stem.lower(), "path": n})
            continue
        ms = SINGLE.search(stem)
        if ms:
            single[(mod, int(ms.group(1)))] = n
    return single, blocks


def main():
    d = json.load(open(JSON, encoding="utf-8"))
    hit = miss = 0
    for t in d["tests"]:
        zname = ZIP_FOR.get(t["test"])
        single, blocks = index_zip(os.path.join(BASE, zname or ""))
        t["audio_zip"] = zname
        for mo in t["modules"]:
            m = mo["module"]
            for it in mo["items"]:
                if it["kind"] == "choose_response":
                    p = single.get((m, it["number"]))
                    it["audio"] = f"{zname}::{p}" if p else None
                    hit += bool(p); miss += (not p)
                else:
                    nums = [q["number"] for q in it["questions"]]
                    if not nums:
                        continue
                    lo, hi = min(nums), max(nums)
                    for b in blocks:
                        if b["module"] != m or b["lo"] > lo or b["hi"] < hi:
                            continue
                        key = "audio_directions" if b["directions"] else "audio"
                        it[key] = f"{zname}::{b['path']}"
                    hit += bool(it.get("audio")); miss += (not it.get("audio"))
    d["_meta"]["audio_mapping"] = (
        "每个条目的 audio 字段格式为 \"<zip 文件名>::<zip 内部路径>\"；"
        "Listening1/Listening2 = Module 1（Router）与 Module 2（自适应分支）。"
        "教师卷 1 为 .mp3，其余为 .ogg。"
    )
    json.dump(d, open(JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"已映射 {hit} 个条目，未匹配 {miss} 个")
    print(f"写回 {JSON}")


if __name__ == "__main__":
    main()
