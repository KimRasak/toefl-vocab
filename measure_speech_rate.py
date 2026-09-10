#!/usr/bin/env python3
"""实测语速：2026 新格式官方练习卷听力 vs 旧格式 TPO 听力。

口径说明（别混为一谈）：
- gross WPM = 英文词数 / 整段音频时长（含句间停顿、含首尾静音）——这是"听起来多快"的宏观值
- span WPM = 英文词数 / (末句时间戳 - 首句时间戳)，只有 TPO 转写带时间戳时可算，
  用来剔掉音频尾部静音的影响
时长统一用 macOS 自带 afinfo（CoreAudio）读，ogg/mp3 都支持。
"""
import json
import os
import re
import subprocess
import sys
from statistics import mean, median

ROOT = os.path.dirname(os.path.abspath(__file__))
TPO_DIR = os.path.join(ROOT, "TPO_listening")
NEW_JSON = os.path.join(ROOT, "ets_official_2026", "listening_2026.json")
NEW_AUDIO = os.path.join(ROOT, "listening-2026", "audio")
NEW_MAP = os.path.join(ROOT, "listening-2026", "audio_map.json")

TS_RE = re.compile(r"^\[\[(\d+):(\d+(?:\.\d+)?)\]\]\s*(.*)$")
SPEAKER_RE = re.compile(r"^[A-Z][A-Za-z' ]{0,30}:\s*")
WORD_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")


def duration(path):
    """afinfo 读时长，秒。"""
    out = subprocess.run(["afinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"estimated duration:\s*([\d.]+)\s*sec", out)
    return float(m.group(1)) if m else None


def count_words(text):
    return len(WORD_RE.findall(text))


def strip_speaker(line):
    return SPEAKER_RE.sub("", line)


# ---------- 旧格式：TPO ----------
def tpo_rows(limit=None):
    manifest = json.load(open(os.path.join(TPO_DIR, "manifest.json")))
    rows = []
    for ent in manifest:
        if not ent.get("has_transcript"):
            continue
        tpath = os.path.join(TPO_DIR, "transcripts", ent["transcript_file"])
        apath = os.path.join(TPO_DIR, "audio", ent["audio_file"])
        if not (os.path.exists(tpath) and os.path.exists(apath)):
            continue
        segs = []  # (t, words, is_narrator)
        for raw in open(tpath, encoding="utf-8"):
            m = TS_RE.match(raw.strip())
            if not m:
                continue  # 注释行 / 中文译文行（译文行不带时间戳，缩进两格）
            t = int(m.group(1)) * 60 + float(m.group(2))
            body = m.group(3)
            is_narr = bool(re.match(r"\s*(Narrator|NARRATOR)\s*:", body))
            segs.append((t, count_words(strip_speaker(body)), is_narr))
        if len(segs) < 5:
            continue
        dur = duration(apath)
        if not dur:
            continue
        # 剔掉开头的旁白句（"Listen to part of a lecture in a ... class"）
        body_segs = [s for s in segs if not s[2]]
        if len(body_segs) < 5:
            continue
        words = sum(s[1] for s in body_segs)
        t0, t1 = body_segs[0][0], body_segs[-1][0]
        # 末句自身时长未知：按本篇除末句外的平均语速反推，避免高估
        inner_words = sum(s[1] for s in body_segs[:-1])
        span = t1 - t0
        rate_inner = inner_words / span if span > 0 else None
        tail = (body_segs[-1][1] / rate_inner) if rate_inner else 0
        # manifest 里的 "tpo" 字段其实是平台文章 id，不是套号；套号从文件名取
        mset = re.match(r"TPO(\d+)_", ent["audio_file"])
        rows.append({
            "id": ent["audio_file"],
            "tpo": int(mset.group(1)) if mset else 0,
            "kind": "conv" if "_conv" in ent["audio_file"] else "lec",
            "words": words,
            "audio_sec": dur,
            "span_sec": span + tail,
            "gross_wpm": words / dur * 60,
            "span_wpm": words / (span + tail) * 60 if span + tail > 0 else None,
        })
        if limit and len(rows) >= limit:
            break
    return rows


# ---------- 新格式：2026 官方练习卷 ----------
def new_rows():
    data = json.load(open(NEW_JSON))
    amap = json.load(open(NEW_MAP))
    rows = []
    for test in data["tests"]:
        for mod in test["modules"]:
            for item in mod["items"]:
                kind = item["kind"]
                if kind == "choose_response":
                    text = strip_speaker(item.get("prompt", ""))
                elif "transcript" in item:
                    text = " ".join(strip_speaker(l) for l in item["transcript"])
                else:
                    continue
                key = item.get("audio")
                fn = amap.get(key)
                if not fn:
                    continue
                apath = os.path.join(NEW_AUDIO, fn)
                if not os.path.exists(apath):
                    continue
                dur = duration(apath)
                if not dur:
                    continue
                w = count_words(text)
                if w == 0:
                    continue
                rows.append({
                    "id": fn,
                    "test": test["test"],
                    "module": mod["module"],
                    "kind": kind,
                    "words": w,
                    "audio_sec": dur,
                    "gross_wpm": w / dur * 60,
                })
    return rows


def describe(name, vals):
    vals = sorted(v for v in vals if v)
    if not vals:
        return f"{name}: 无数据"
    n = len(vals)
    p10 = vals[int(n * 0.10)]
    p90 = vals[min(n - 1, int(n * 0.90))]
    return (f"{name:<28} n={n:<4} 均值 {mean(vals):6.1f}  中位 {median(vals):6.1f}  "
            f"p10 {p10:6.1f}  p90 {p90:6.1f}  区间 {vals[0]:.0f}–{vals[-1]:.0f}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    new = new_rows()
    old = tpo_rows(limit)

    print("=== 新格式（2026 官方对版练习卷，7 套）===")
    for k, label in [("conversation", "短对话 conversation"),
                     ("announcement", "公告 announcement"),
                     ("academic_talk", "学术讲座 academic talk"),
                     ("choose_response", "听答题 choose a response")]:
        sub = [r for r in new if r["kind"] == k]
        print(describe(label + " gross", [r["gross_wpm"] for r in sub]))
        if sub:
            print(f"{'':30}平均时长 {mean(r['audio_sec'] for r in sub):5.1f}s  "
                  f"平均词数 {mean(r['words'] for r in sub):5.1f}")
    long_new = [r for r in new if r["kind"] in ("conversation", "announcement", "academic_talk")]
    print(describe("新格式三类长音频合计 gross", [r["gross_wpm"] for r in long_new]))

    print("\n=== 旧格式（TPO 1–75，小站转写 + 官方音频）===")
    for k, label in [("conv", "对话 conversation"), ("lec", "讲座 lecture")]:
        sub = [r for r in old if r["kind"] == k]
        print(describe(label + " gross", [r["gross_wpm"] for r in sub]))
        print(describe(label + " span ", [r["span_wpm"] for r in sub]))
        if sub:
            print(f"{'':30}平均时长 {mean(r['audio_sec'] for r in sub):6.1f}s  "
                  f"平均词数 {mean(r['words'] for r in sub):6.1f}")
    print(describe("TPO 全部 gross", [r["gross_wpm"] for r in old]))
    print(describe("TPO 全部 span ", [r["span_wpm"] for r in old]))

    # 按年代分组看旧题语速漂移
    print("\n=== TPO 按套号分段（span WPM）===")
    for lo, hi in [(1, 26), (27, 45), (46, 58), (60, 75)]:
        sub = [r for r in old if lo <= r["tpo"] <= hi]
        print(describe(f"TPO {lo}-{hi}", [r["span_wpm"] for r in sub]))

    json.dump({"new": new, "tpo": old}, open(os.path.join(ROOT, "speech_rate_measured.json"), "w"),
              ensure_ascii=False, indent=1)
    print("\n明细已写入 speech_rate_measured.json")
