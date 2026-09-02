# 英语学习资源站

- 根路径 `index.html` : 主页（单词表 + 听力精选入口）
- `my-tofel-1791words-words.html` : 1791 词版（带发音 + 剑桥官方释义）
- `my-tofel-1925-words.html` : 1925 词版（4 册合并 · 剑桥官方释义 + 朗读）
- `1675/index.html` : 1675 词版（带发音）
- `proper-nouns/index.html` : 专有名词（学科术语 + 例句发音 + 随机抽词造句）
- 对应 `.txt` 为原始数据
- `listening/index.html` : 英语听力精选播放器（200 集 · 逐句字幕 + 全文原文）

## 1925 词版（V1，4 册合并）

- 数据：`my-tofel-1925-1~4-words.txt`（Quizlet 4 册导出）合并去重得 `my-tofel-1925words-words.txt`（1661 词）
- 中文释义含 `[ph]`（短语）/ `[st]`（句子）/ `[mean]`（释义）标记
- 同 1791 V6：剑桥官方英英释义 + 音标 + 官方美音 mp3 + 释义句/例句在线朗读
- 生成脚本：`build_1925.py`

## 1791 词版（V7，本地真人音频 + 单词卡）

- 数据：`cambridge_fetch.py` 从 dictionary.cambridge.org 批量抓取（释义/音标/美音mp3/例句），输出 `output/cambridge_defs_1791.json`，再由 `build_v6.py` 合入页面
- 单词发音：**本地剑桥官方真人美音 mp3**（`1791_audio/w-*.mp3`，由 `gen_1791_audio.py` 批量下载），失败降级：剑桥在线 → 有道 → Google TTS
- 例句发音：**本地 edge-tts 神经语音**（`1791_audio/e-*.mp3`，接近真人，不依赖 Google/网络），例句朗读自动匹配本地音频，失败才走 Google TTS → speechSynthesis
- 官方释义：每词展示剑桥英英释义（多义项）+ 音标 + 官方例句，释义句/例句点击 🔊 朗读
- 单词卡模式（🃏 单词卡按钮）：全屏卡片显示单词/音标/释义/例句，▶ 播放先读单词再读例句，可选播放结束自动下一张（连播），支持 ← → 键翻卡
- 音频生成：`gen_1791_audio.py`（剑桥 mp3 下载 + edge-tts 神经语音合成，输出 `1791_audio/` + `1791_audio_map.js`），部署时需连同 `1791_audio/` 目录一起上传

## 专有名词（proper-nouns）

- 数据：`proper-nouns/data.js`（词条 + 中文释义 + 真实语料例句 + 来源标注 + 分类 + 音标）
- 例句来源：TPO 听力原文原句（约 40%）+ 词典风格改写（约 60%），每条标注来源（如 `TPO16-L2` / `词典风格`）
- 单词发音：`proper-nouns/audio/*.mp3` 为**剑桥词典真人美音**（由 `proper-nouns/fetch_audio.py` 抓取，418 词条中 400 个命中，其余走页面 TTS 兜底）
- 例句发音：本地无例句音频，页面用 Google TTS → 浏览器 speechSynthesis 朗读当前例句文本
- 功能：分类筛选（身体词 / 海洋 / 美国州名 / 历史运动 / 能源环境 / 乐器 / 多义词 / 地质化学 / 校园场景 等 19 类）、搜索、随机抽一个（自动朗读例句）

## 听力播放器

单文件页面，音频为公开 CDN 直链，无需登录即可播放；字幕与原文数据内嵌于页面。
构建脚本见 `bilibili_TPO听力原文200集/build_gh_player.py`。

## 学科词汇总表（merged-by-discipline · 按 2026 考场权重加权）

- 页面：`merged-by-discipline/index.html`，构建脚本 `build_merged_by_discipline.py`
- 数据：1791 + 1925 + 1675 三份词表合并去重，叠加 `new_scenario_words.json`（新题型场景词）、`high_frequency_discipline_words.json`（学科高频）与 `toefl2026_exam_terms.json`（**2026 真题学科词库**），共 5013 词 / 45 个学科
- 每个学科带 **2026 真实考场权重徽章**：数字是该学科在 2026 改版后 237 条去重讲座话题里的占比（🔥 讲座高频 / 📈 中频 / 💤 低频 / 🎓 对话·公告 / 🧩 全学科通用）
- 三个 2026 视图开关：`🆕 仅 2026 真题词`（614 词）、`🔥 仅 2026 高频学科`、`↕️ 按 2026 优先级排序`
- 权重与口径来源：`2026听力学科场景占比-2026-09-02.md`；新增学科必须同时在 `TOPIC_2026` 里登记权重，否则构建直接报错
