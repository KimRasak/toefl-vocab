#!/usr/bin/env python3
"""把 listening_2026.json 引用到的听力音频从各 zip 里抽出来，摊平到 listening-2026/audio/。

为什么要摊平：zip 内部路径带空格和中文标点，直接当 URL 用会踩编码问题；而且七个 zip
里同名文件（Listening1_Question Response_Question1.ogg）互相冲突，必须按卷号加前缀。

命名规则  <卷号>_<模块>_<题型缩写><序号>[_d].<ext>
  卷号   s1 s2 = 学生卷 1/2；t1..t5 = 教师卷 1..5
  模块   m1 = Module 1（Router）；m2 = Module 2（自适应分支）
  题型   cr=听答题 cv=对话 an=公告 at=学术讲座
  _d     该题型的 directions 音频（指令），不是题目本身

用法: python3 extract_audio.py [--force]
输出: ../listening-2026/audio/*.ogg|mp3 + ../listening-2026/audio_map.json
"""
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "listening_2026.json")
OUTDIR = os.path.join(os.path.dirname(HERE), "listening-2026", "audio")
OUTMAP = os.path.join(os.path.dirname(HERE), "listening-2026", "audio_map.json")

TEST_CODE = {
    "toefl-ibt-full-length-practice-test-1": "s1",
    "toefl-ibt-full-length-practice-test-2": "s2",
    "toefl-ibt-teachers-resources-practice-test-1": "t1",
    "toefl-ibt-teachers-resources-practice-test-2": "t2",
    "toefl-ibt-teachers-resources-practice-test-3": "t3",
    "toefl-ibt-teachers-resources-practice-test-4": "t4",
    "toefl-ibt-teachers-resources-practice-test-5": "t5",
}
KIND_CODE = {"choose_response": "cr", "conversation": "cv",
             "announcement": "an", "academic_talk": "at"}

force = "--force" in sys.argv
os.makedirs(OUTDIR, exist_ok=True)
data = json.load(open(SRC, encoding="utf-8"))

# 先把要抽的文件按 zip 归拢，一个 zip 只打开一次
plan = []          # (zip 名, zip 内路径, 目标文件名)
seq = {}           # (卷, 模块, 题型) -> 已分配序号
for t in data["tests"]:
    code = TEST_CODE[t["test"]]
    for m in t["modules"]:
        mod = f"m{m['module']}"
        for it in m["items"]:
            kc = KIND_CODE[it["kind"]]
            k = (code, mod, kc)
            seq[k] = seq.get(k, 0) + 1
            base = f"{code}_{mod}_{kc}{seq[k]:02d}"
            for field, suffix in (("audio", ""), ("audio_directions", "_d")):
                ref = it.get(field)
                if not ref:
                    continue
                zname, inner = ref.split("::", 1)
                plan.append((zname, inner, base + suffix, ref))

byzip = {}
for zname, inner, out, ref in plan:
    byzip.setdefault(zname, []).append((inner, out, ref))


def sniff_ext(blob):
    """按内容定扩展名。zip 里有个 .ogg 其实是 MP3（s2 的听答题第 8 题），不能信后缀。"""
    if blob[:4] == b"OggS":
        return ".ogg"
    if blob[:3] == b"ID3" or (len(blob) > 1 and blob[0] == 0xFF and (blob[1] & 0xE0) == 0xE0):
        return ".mp3"
    return ".bin"


amap = {}          # 原始 "zip::path" -> 摊平后的文件名
written = skipped = 0
missing = []
mislabeled = []
for zname, jobs in sorted(byzip.items()):
    zpath = os.path.join(HERE, zname)
    if not os.path.exists(zpath):
        missing += [ref for _, _, ref in jobs]
        print(f"  !! 缺 zip {zname}，跳过 {len(jobs)} 条")
        continue
    with zipfile.ZipFile(zpath) as zf:
        names = set(zf.namelist())
        for inner, base_out, ref in jobs:
            if inner not in names:
                missing.append(ref)
                continue
            blob = zf.read(inner)
            ext = sniff_ext(blob)
            if ext != os.path.splitext(inner)[1].lower():
                mislabeled.append((inner, ext))
            out = base_out + ext
            dst = os.path.join(OUTDIR, out)
            if force or not os.path.exists(dst) or os.path.getsize(dst) != len(blob):
                with open(dst, "wb") as fo:
                    fo.write(blob)
                written += 1
            else:
                skipped += 1
            amap[ref] = out

json.dump(amap, open(OUTMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
total = sum(os.path.getsize(os.path.join(OUTDIR, f)) for f in os.listdir(OUTDIR)
            if not f.startswith("."))
print(f"引用 {len(plan)} 条音频 -> 落地 {len(amap)} 条"
      f"（新写 {written} / 已存在跳过 {skipped}），缺失 {len(missing)}")
print(f"目录 {OUTDIR}  合计 {total / 1024 / 1024:.1f} MB")
print(f"映射表 {OUTMAP}")
if mislabeled:
    print(f"  zip 内后缀与实际容器不符 {len(mislabeled)} 条（已按实际内容改名）:")
    for inner, ext in mislabeled[:5]:
        print(f"    {os.path.basename(inner)} -> {ext}")
if missing:
    for r in missing[:5]:
        print("  MISS", r)
