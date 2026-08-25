# 英语学习资源站

- 根路径 `index.html` : 主页（单词表 + 听力精选入口）
- `my-tofel-1791words-words.html` : 1791 词版（带发音 + 剑桥官方释义）
- `1675/index.html` : 1675 词版（带发音）
- `proper-nouns/index.html` : 专有名词（学科术语 + 例句发音 + 随机抽词造句）
- 对应 `.txt` 为原始数据
- `listening/index.html` : 英语听力精选播放器（200 集 · 逐句字幕 + 全文原文）

## 1791 词版（V6，剑桥官方释义）

- 数据：`cambridge_fetch.py` 从 dictionary.cambridge.org 批量抓取（释义/音标/美音mp3/例句），输出 `output/cambridge_defs_1791.json`，再由 `build_v6.py` 合入页面
- 单词发音：**剑桥官方真人美音 mp3**（三级降级：剑桥 → 有道 → Google TTS）
- 官方释义：每词展示剑桥英英释义（多义项）+ 音标 + 官方例句，释义句/例句点击 🔊 在线朗读（Google TTS → speechSynthesis 兜底）
- 说明：剑桥网页例句无官方朗读音频，故句子朗读为合成语音

## 专有名词（proper-nouns）

- 数据：`proper-nouns/data.js`（词条 + 中文释义 + 真实语料例句 + 来源标注 + 分类 + 音标）
- 例句来源：TPO 听力原文原句（约 40%）+ 词典风格改写（约 60%），每条标注来源（如 `TPO16-L2` / `词典风格`）
- 单词发音：`proper-nouns/audio/*.mp3` 为**剑桥词典真人美音**（由 `proper-nouns/fetch_audio.py` 抓取，418 词条中 400 个命中，其余走页面 TTS 兜底）
- 例句发音：本地无例句音频，页面用 Google TTS → 浏览器 speechSynthesis 朗读当前例句文本
- 功能：分类筛选（身体词 / 海洋 / 美国州名 / 历史运动 / 能源环境 / 乐器 / 多义词 / 地质化学 / 校园场景 等 19 类）、搜索、随机抽一个（自动朗读例句）

## 听力播放器

单文件页面，音频为公开 CDN 直链，无需登录即可播放；字幕与原文数据内嵌于页面。
构建脚本见 `bilibili_TPO听力原文200集/build_gh_player.py`。
