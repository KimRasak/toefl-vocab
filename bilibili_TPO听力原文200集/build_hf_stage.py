#!/usr/bin/env python3
"""构建 HF 数据集上传结构：每集一个文件夹（audio.mp3 + metadata.json）。"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_AUDIO = os.path.join(HERE, "audio")
META = "/tmp/bili_meta.json"
STAGE = "/tmp/hf_stage/bilibili-tofel-tpo-listening-audio"

def short_name(title, idx):
    m = re.search(r"TPO-\d+[_-][A-Z]\d+", title)
    if m:
        return m.group(0).replace("-", "_").replace("_", "-", 1).upper()
    return f"p{idx:03d}"

def main():
    with open(META) as f:
        data = json.load(f)
    entries = sorted(data["entries"], key=lambda e: e["playlist_index"])

    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)

    for e in entries:
        idx = e["playlist_index"]
        short = short_name(e["title"], idx)
        folder = f"p{idx:03d}_{short}"
        d = os.path.join(STAGE, folder)
        os.makedirs(d, exist_ok=True)

        src = os.path.join(SRC_AUDIO, f"{folder}.mp3")
        shutil.copy2(src, os.path.join(d, "audio.mp3"))

        meta = {
            "episode": idx,
            "total_episodes": 200,
            "tpo_part": short,
            "title": e["title"],
            "duration_seconds": e.get("duration"),
            "source": "https://www.bilibili.com/video/BV1ci421f7Lu/",
            "source_page": f"https://www.bilibili.com/video/BV1ci421f7Lu?p={idx}",
            "audio_file": f"{folder}/audio.mp3",
        }
        with open(os.path.join(d, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    # README + dataset card
    readme = """---
license: cc-by-nc-4.0
task_categories:
  - automatic-speech-recognition
  - audio-classification
language:
  - en
tags:
  - toefl
  - tpo
  - listening
  - bilibili
---

# Bilibili 托福 TPO 听力原文合集音频

来自 B 站合集《【1000集全】英语口语听力实战 - 托福TPO听力原文》（BV1ci421f7Lu）的全部 **200 集**音频。

## 结构

每集一个文件夹：`p001_TPO-25_L4/` 内含：

- `audio.mp3` — 该集音频
- `metadata.json` — 编号、TPO 章节、标题、时长、来源链接

## 元数据字段

| 字段 | 说明 |
|---|---|
| `episode` | 分集编号 1-200 |
| `tpo_part` | TPO 章节标识，如 `TPO-25_L4`（L=lecture，C=conversation） |
| `title` | 完整标题 |
| `duration_seconds` | 时长（秒） |
| `source` / `source_page` | 来源 B 站链接 |

## 使用

```python
from datasets import load_dataset
ds = load_dataset("xxfasdf/bilibili-tofel-tpo-listening-audio", streaming=True)
```
"""
    with open(os.path.join(STAGE, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # 统计
    n = len(entries)
    size = sum(os.path.getsize(os.path.join(STAGE, d, "audio.mp3"))
               for d in os.listdir(STAGE) if os.path.isdir(os.path.join(STAGE, d)))
    print(f"构建完成: {n} 个文件夹, 共 {size/1024/1024:.0f} MB -> {STAGE}")


if __name__ == "__main__":
    main()
