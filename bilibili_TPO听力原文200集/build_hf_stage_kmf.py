#!/usr/bin/env python3
"""构建 KMF 数据 HF 上传结构：kmf/pXXX_XXX/ 每集一个文件夹。
包含: audio.mp3 (KMF官方音频), transcript.txt (官方原文), subtitles.srt (带时间轴), metadata.json
用法: python3 build_hf_stage_kmf.py
"""
import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_AUDIO = os.path.join(BASE, "audio_kmf")
SRC_SUBS = os.path.join(BASE, "subtitles_kmf")
MAPPING = "/tmp/bili_kmf_mapping.json"
ORIGINALS = "/tmp/kmf_originals.json"
AUDIO_URLS = "/tmp/kmf_full_audio.json"
META = "/tmp/bili_meta.json"
STAGE = "/tmp/hf_stage/bilibili-tofel-tpo-listening-audio/kmf"


def short_name(title, idx):
    m = re.search(r"TPO-\d+[_-][A-Z]\d+", title)
    if m:
        return m.group(0).replace("-", "_").replace("_", "-", 1).upper()
    return f"p{idx:03d}"


def main():
    with open(MAPPING) as f:
        mapping = json.load(f)
    with open(ORIGINALS) as f:
        originals = json.load(f)
    with open(AUDIO_URLS) as f:
        audio_urls = json.load(f)
    with open(META) as f:
        data = json.load(f)
    entries = {e["playlist_index"]: e for e in data["entries"]}

    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    ok = 0
    for idx in sorted(mapping, key=int):
        short = short_name(entries[int(idx)]["title"], int(idx))
        folder = f"p{int(idx):03d}_{short}"
        d = os.path.join(STAGE, folder)
        os.makedirs(d, exist_ok=True)

        # 音频
        src = os.path.join(SRC_AUDIO, f"{folder}.mp3")
        if not os.path.exists(src):
            print(f"WARN: 缺音频 {folder}")
            continue
        shutil.copy2(src, os.path.join(d, "audio.mp3"))

        # 字幕 SRT
        srt_src = os.path.join(SRC_SUBS, f"{folder}.srt")
        if os.path.exists(srt_src):
            shutil.copy2(srt_src, os.path.join(d, "subtitles.srt"))

        # 官方原文
        v = mapping[idx]
        kmf_url = v["kmf_url"]
        original = originals.get(kmf_url, {}).get("original", "")
        with open(os.path.join(d, "transcript.txt"), "w", encoding="utf-8") as f:
            f.write(original)

        # metadata
        kmf_title = v["kmf_title"]
        meta = {
            "episode": int(idx),
            "total_episodes": 200,
            "tpo_part": short,
            "kmf_page": f"https://toefl.kmf.com{kmf_url}",
            "kmf_title": kmf_title,
            "kmf_audio_url": audio_urls.get(idx, ""),
            "match_score": v["score"],
            "bilibili_source": f"https://www.bilibili.com/video/BV1ci421f7Lu?p={int(idx)}",
            "bilibili_title": entries[int(idx)]["title"],
            "audio_file": f"kmf/{folder}/audio.mp3",
            "transcript_file": f"kmf/{folder}/transcript.txt",
            "subtitles_file": f"kmf/{folder}/subtitles.srt",
        }
        with open(os.path.join(d, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        ok += 1

    print(f"构建完成: {ok} 集")
    total_size = sum(os.path.getsize(os.path.join(dp, f))
                     for dp, _, fns in os.walk(STAGE) for f in fns)
    print(f"总大小: {total_size/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
