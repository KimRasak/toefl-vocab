#!/usr/bin/env python3
"""批量提取 B 站合集 BV1ci421f7Lu 的硬字幕（OCR），生成 SRT 到 subtitles/。"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

BILI_URL = "https://www.bilibili.com/video/BV1ci421f7Lu/"
YTDLP = "/tmp/yt-dlp"
SWIFT_BATCH = "/tmp/vision_ocr_batch.swift"
HERE = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(HERE, "subtitles")
WORK = "/tmp/sub_work"
META = "/tmp/bili_meta.json"

# 需要处理的集范围（可传参数：--from N --to M，或 --idx N）
ARGV = sys.argv[1:]


def parse_args():
    opts = {"from": 2, "to": 200}
    i = 0
    while i < len(ARGV):
        if ARGV[i] == "--from" and i + 1 < len(ARGV):
            opts["from"] = int(ARGV[i+1]); i += 2
        elif ARGV[i] == "--to" and i + 1 < len(ARGV):
            opts["to"] = int(ARGV[i+1]); i += 2
        elif ARGV[i] == "--idx" and i + 1 < len(ARGV):
            idx = int(ARGV[i+1])
            opts["from"] = idx; opts["to"] = idx; i += 2
        else:
            i += 1
    return opts


def short_name(title, idx):
    m = re.search(r"TPO-\d+[_-][A-Z]\d+", title)
    if m:
        return m.group(0).replace("-", "_").replace("_", "-", 1).upper()
    return f"p{idx:03d}"


def parse_srt_blocks(cues):
    """把 cues 列表转成 SRT 文本"""
    out = []
    for i, c in enumerate(cues, 1):
        def fmt(t):
            h = int(t // 3600); mi = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
            if ms >= 1000: s += 1; ms -= 1000
            return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"
        out.append(f"{i}\n{fmt(c['start'])} --> {fmt(c['end'])}\n{c['text']}\n")
    return "\n".join(out)


def normalize(t):
    t = t.lower().replace("*", "").replace("−", "-").replace("- ", " ")
    t = t.replace("|", "").replace("| ", "")  # OCR 竖线杂音
    # 数字序数词 OCR 变体归一: "2l st" / "2lst" / "21st" -> "21st"
    t = re.sub(r"(\d)l\s*st", r"\1st", t)
    # 常见 OCR 混淆: 1->l 出现在数字里（如 "2l" -> "21"）
    t = re.sub(r"(?<=\d)l(?=\d)", "1", t)
    t = t.replace('"', "").replace(",,", ",").replace(".,", ",")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def merge_cues(cues):
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
    final = []
    for i, m_ in enumerate(merged):
        if i > 0 and m_["key"] == merged[i-1]["key"]:
            continue
        final.append({"start": m_["start"], "end": m_["end"], "text": m_["text"]})
    return final


def process_one(idx, short, force=False):
    srt_path = os.path.join(SUB_DIR, f"p{idx:03d}_{short}.srt")
    if os.path.exists(srt_path) and not force:
        print(f"[skip] p{idx:03d} 已有字幕")
        return True

    ep_dir = os.path.join(WORK, f"ep{idx:03d}")
    frames_dir = os.path.join(ep_dir, "frames")
    ocr_dir = os.path.join(ep_dir, "ocr")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(ocr_dir, exist_ok=True)

    # 1) 下载视频（低清即可，字幕清晰度足够）
    url = f"https://www.bilibili.com/video/BV1ci421f7Lu?p={idx}"
    vpath = os.path.join(ep_dir, "v.mp4")
    if not os.path.exists(vpath):
        r = subprocess.run([
            YTDLP, "-f", "bv*[height<=480]+ba", "--merge-output-format", "mp4",
            "--no-warnings", "-o", vpath, url
        ], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(vpath):
            print(f"  !! 下载失败 p{idx:03d}: {r.stderr[-300:]}")
            return False

    # 2) 抽帧（每秒 1 帧）
    r = subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", vpath, "-vf", "fps=1",
        "-q:v", "3", os.path.join(frames_dir, "f_%04d.png")
    ], capture_output=True, text=True)
    n_frames = len([f for f in os.listdir(frames_dir) if f.endswith(".png")])
    if r.returncode != 0 or n_frames == 0:
        print(f"  !! 抽帧失败 p{idx:03d}")
        return False

    # 3) 批量 OCR
    r = subprocess.run([
        "swift", SWIFT_BATCH, frames_dir, ocr_dir
    ], capture_output=True, text=True)
    n_ocr = len([f for f in os.listdir(ocr_dir) if f.endswith(".json")])
    if r.returncode != 0 or n_ocr == 0:
        print(f"  !! OCR 失败 p{idx:03d}: {r.stderr[-300:]}")
        return False

    # 4) 合并成字幕
    cues = []
    for j in range(1, n_frames + 1):
        jp = os.path.join(ocr_dir, f"f_{j:04d}.json")
        if not os.path.exists(jp):
            continue
        try:
            with open(jp, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        lines = [d["text"].strip() for d in data if d["text"].strip()]
        if lines:
            clean = " ".join(lines).replace("|", "")
            cues.append({"start": j - 1, "end": j, "text": clean})
    merged = merge_cues(cues)
    if not merged:
        print(f"  !! 无识别结果 p{idx:03d}")
        return False

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(parse_srt_blocks(merged))
    print(f"  -> p{idx:03d}_{short}.srt ({len(merged)} 段, {n_frames} 帧)")
    return True


def main():
    opts = parse_args()
    with open(META) as f:
        data = json.load(f)
    entries = sorted(data["entries"], key=lambda e: e["playlist_index"])
    os.makedirs(SUB_DIR, exist_ok=True)

    todo = [e for e in entries if opts["from"] <= e["playlist_index"] <= opts["to"]]
    print(f"待处理 {len(todo)} 集 (p{opts['from']}-p{opts['to']})")

    ok = fail = 0
    for e in todo:
        idx = e["playlist_index"]
        short = short_name(e["title"], idx)
        t0 = time.time()
        if process_one(idx, short):
            ok += 1
        else:
            fail += 1
        dt = time.time() - t0
        print(f"  [{idx}/{opts['to']}] 用时 {dt:.0f}s", flush=True)
        # 清理该集临时文件
        shutil.rmtree(os.path.join(WORK, f"ep{idx:03d}"), ignore_errors=True)

    print(f"\n完成: 成功 {ok}, 失败 {fail}")


if __name__ == "__main__":
    main()
