# 英语学习资源站

- 根路径 `index.html` : 主页（单词表 + 听力精选入口）
- `my-tofel-1791words-words.html` : 1791 词版（带发音）
- `1675/index.html` : 1675 词版（带发音）
- `proper-nouns/index.html` : 专有名词（学科术语 + 例句发音 + 随机抽词造句）
- 对应 `.txt` 为原始数据
- `listening/index.html` : 英语听力精选播放器（200 集 · 逐句字幕 + 全文原文）

## 专有名词（proper-nouns）

- 数据：`proper-nouns/data.js`（词条 + 中文释义 + 例句 + 分类 + 音标）
- 音频：`proper-nouns/audio/*.mp3` 由 `proper-nouns/gen_audio.py` 用 edge-tts 预生成（单词 + 例句），
  页面优先播放本地音频，失败降级有道词典 / Google TTS / 浏览器 speechSynthesis
- 功能：分类筛选、搜索、随机抽一个（自动朗读例句）

## 听力播放器

单文件页面，音频为公开 CDN 直链，无需登录即可播放；字幕与原文数据内嵌于页面。
构建脚本见 `bilibili_TPO听力原文200集/build_gh_player.py`。
