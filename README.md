# TOEFL 单词本（1791 + 1675）

- 根路径 `index.html` : 主页（单词表 + TPO 听力入口）
- `my-tofel-1791words-words.html` : 1791 词版（带发音）
- `1675/index.html` : 1675 词版（带发音）
- 对应 `.txt` 为原始数据
- `listening/index.html` : TPO 听力播放器（KMF 官方 · 200 集 · 逐句字幕 + 全文原文，音频为 KMF 公开 CDN 直链，无需登录）

## 听力播放器

数据来源：[HuggingFace 数据集 xxfasdf/bilibili-tofel-tpo-listening-audio](https://huggingface.co/datasets/xxfasdf/bilibili-tofel-tpo-listening-audio)（私有）。
播放器内嵌了 KMF 官方 200 集音频的公开 CDN 直链 + 字幕 + 原文，页面为单文件，数据构建脚本见 `bilibili_TPO听力原文200集/build_gh_player.py`。
