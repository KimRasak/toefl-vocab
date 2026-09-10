#!/usr/bin/env python3
"""下载 B 站合集 BV1ci421f7Lu 全部 200 集音频为 mp3，使用简短文件名。"""
import json
import os
import re
import subprocess
import sys
import time

BILI_URL = "https://www.bilibili.com/video/BV1ci421f7Lu/"
YTDLP = "/tmp/yt-dlp"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
META = "/tmp/bili_meta.json"

def short_name(title: str, idx: int) -> str:
    """从标题提取 TPO-XX-Ln/Cn 作为短名；失败则退回 pNN。"""
    m = re.search(r"TPO-\d+[_-][A-Z]\d+", title)
    if m:
        return m.group(0).replace("-", "_").replace("_", "-", 1).upper()
    return f"p{idx:03d}"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(META) as f:
        data = json.load(f)
    entries = sorted(data["entries"], key=lambda e: e["playlist_index"])

    # 1) 预检查哪些已存在
    todo = []
    for e in entries:
        idx = e["playlist_index"]
        short = short_name(e["title"], idx)
        mp3 = os.path.join(OUT_DIR, f"p{idx:03d}_{short}.mp3")
        if os.path.exists(mp3) and os.path.getsize(mp3) > 10000:
            print(f"[skip] {mp3}")
            continue
        todo.append((idx, short, mp3))

    print(f"待下载: {len(todo)} 集")
    if not todo:
        print("全部已完成。")
        return

    fails = []
    for i, (idx, short, mp3) in enumerate(todo, 1):
        url = f"https://www.bilibili.com/video/BV1ci421f7Lu?p={idx}"
        tmpdir = os.path.join(OUT_DIR, f".tmp_p{idx:03d}")
        os.makedirs(tmpdir, exist_ok=True)
        cmd = [
            YTDLP, "-x", "--audio-format", "mp3", "--audio-quality", "0",
            "--no-playlist", "--no-warnings", "--newline",
            "-o", os.path.join(tmpdir, "f.%(ext)s"),
            url,
        ]
        print(f"\n[{i}/{len(todo)}] p{idx:03d} {short} ...", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        # 找到生成的 mp3
        produced = None
        if os.path.isdir(tmpdir):
            for fn in os.listdir(tmpdir):
                if fn.endswith(".mp3"):
                    produced = os.path.join(tmpdir, fn)
                    break
        if r.returncode == 0 and produced and os.path.getsize(produced) > 10000:
            os.replace(produced, mp3)
            print(f"  -> {os.path.basename(mp3)} ({os.path.getsize(mp3)//1024} KB)")
        else:
            fails.append(idx)
            print(f"  !! 失败 p{idx:03d}: {r.stderr[-500:]}")
        # 清理临时目录
        if os.path.isdir(tmpdir):
            for fn in os.listdir(tmpdir):
                try:
                    os.remove(os.path.join(tmpdir, fn))
                except OSError:
                    pass
            try:
                os.rmdir(tmpdir)
            except OSError:
                pass
        time.sleep(0.8)  # 避免触发限流

    print(f"\n完成。成功 {len(todo)-len(fails)}/{len(todo)}，失败: {fails}")
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
