#!/usr/bin/env python3
"""在 measure_speech_rate.py 的基础上再做一层：把静音剔掉后再算语速。

三个口径，逐层收紧：
- gross WPM   词数 / 整段音频时长（含首尾静音、含句间停顿）
- trimmed WPM 词数 / (最后一个有声帧 - 第一个有声帧)  → 剔掉首尾静音
- artic WPM   词数 / 有声帧总时长（articulation rate，语音学口径）→ 再剔掉句间停顿

解码走 macOS 自带 afconvert（CoreAudio 能解 ogg vorbis 与 mp3），不需要 ffmpeg。
静音判定：20ms 帧 RMS < max(峰值帧 RMS 的 3%, 噪声底 * 2) 记为静音。
"""
import json
import os
import random
import re
import subprocess
import struct
import sys
import tempfile
import wave
from statistics import mean, median

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
MEASURED = os.path.join(ROOT, "speech_rate_measured.json")
NEW_AUDIO = os.path.join(ROOT, "listening-2026", "audio")
TPO_AUDIO = os.path.join(ROOT, "TPO_listening", "audio")
FRAME_MS = 20


def decode(path, tmpdir):
    out = os.path.join(tmpdir, "d.wav")
    r = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", path, out],
                       capture_output=True)
    if r.returncode != 0 or not os.path.exists(out):
        return None
    return out


def frame_rms(wav_path):
    with wave.open(wav_path, "rb") as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        raw = w.readframes(n)
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    fl = int(sr * FRAME_MS / 1000)
    if fl <= 0 or len(x) < fl:
        return None, None
    x = x[: len(x) // fl * fl].reshape(-1, fl)
    return np.sqrt((x ** 2).mean(axis=1)), fl / sr


def timings(path, tmpdir):
    """返回 (总时长, 首尾修剪后时长, 有声时长)，单位秒。"""
    wav = decode(path, tmpdir)
    if not wav:
        return None
    rms, fdur = frame_rms(wav)
    os.remove(wav)
    if rms is None or len(rms) < 5:
        return None
    peak = np.percentile(rms, 99)
    floor = np.percentile(rms, 5)
    thr = max(peak * 0.03, floor * 2.0, 1.0)
    voiced = rms > thr
    idx = np.flatnonzero(voiced)
    if len(idx) < 3:
        return None
    total = len(rms) * fdur
    trimmed = (idx[-1] - idx[0] + 1) * fdur
    speech = int(voiced.sum()) * fdur
    return total, trimmed, speech


def stat(name, vals):
    v = sorted(x for x in vals if x)
    if not v:
        print(f"{name:<30} 无数据")
        return
    n = len(v)
    print(f"{name:<30}n={n:<4} 均值{mean(v):6.1f} 中位{median(v):6.1f} "
          f"p10 {v[int(n*.1)]:6.1f} p90 {v[min(n-1,int(n*.9))]:6.1f} 区间 {v[0]:.0f}-{v[-1]:.0f}")


if __name__ == "__main__":
    tpo_sample = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    data = json.load(open(MEASURED))
    tmp = tempfile.mkdtemp(prefix="wpm_")

    def enrich(rows, audio_dir):
        out = []
        for i, r in enumerate(rows):
            t = timings(os.path.join(audio_dir, r["id"]), tmp)
            if not t:
                continue
            total, trimmed, speech = t
            r = dict(r)
            r["total_sec"] = total
            r["trimmed_sec"] = trimmed
            r["speech_sec"] = speech
            r["silence_ratio"] = 1 - speech / total
            r["gross_wpm2"] = r["words"] / total * 60
            r["trim_wpm"] = r["words"] / trimmed * 60
            r["artic_wpm"] = r["words"] / speech * 60
            out.append(r)
        return out

    new = enrich(data["new"], NEW_AUDIO)

    # 旧格式抽样（保持类型均衡），先按之前的清洗规则过滤掉坏件
    def ok(r):
        return (r["span_wpm"] and abs(r["gross_wpm"] / r["span_wpm"] - 1) <= 0.3
                and r["span_wpm"] >= 110)
    pool = [r for r in data["tpo"] if ok(r)]
    random.seed(20260902)
    convs = [r for r in pool if r["kind"] == "conv"]
    lecs = [r for r in pool if r["kind"] == "lec"]
    k = max(1, tpo_sample // 2)
    sample = random.sample(convs, min(k, len(convs))) + random.sample(lecs, min(k, len(lecs)))
    old = enrich(sample, TPO_AUDIO)

    print("=== 新格式 2026（官方对版练习卷 7 套，全量）===")
    for kk, lab in [("choose_response", "听答题"), ("conversation", "短对话"),
                    ("announcement", "公告"), ("academic_talk", "学术讲座")]:
        sub = [r for r in new if r["kind"] == kk]
        if not sub:
            continue
        stat(f"{lab} gross", [r["gross_wpm2"] for r in sub])
        stat(f"{lab} trimmed", [r["trim_wpm"] for r in sub])
        stat(f"{lab} artic", [r["artic_wpm"] for r in sub])
        print(f"{'':32}静音占比 {mean(r['silence_ratio'] for r in sub)*100:.0f}%  "
              f"平均 {mean(r['total_sec'] for r in sub):.1f}s")

    print("\n=== 旧格式 TPO（抽样）===")
    for kk, lab in [("conv", "对话"), ("lec", "讲座")]:
        sub = [r for r in old if r["kind"] == kk]
        if not sub:
            continue
        stat(f"{lab} gross", [r["gross_wpm2"] for r in sub])
        stat(f"{lab} trimmed", [r["trim_wpm"] for r in sub])
        stat(f"{lab} artic", [r["artic_wpm"] for r in sub])
        print(f"{'':32}静音占比 {mean(r['silence_ratio'] for r in sub)*100:.0f}%  "
              f"平均 {mean(r['total_sec'] for r in sub):.1f}s")

    json.dump({"new": new, "tpo_sample": old},
              open(os.path.join(ROOT, "speech_rate_articulation.json"), "w"),
              ensure_ascii=False, indent=1)
    print("\n明细已写入 speech_rate_articulation.json")
