# 托福 TPO 听力材料（音频 + 字幕文档）

本目录包含从**小站备考（top.zhan.com）**公开平台抓取的托福 TPO 听力真题材料：
**TPO 1–58、TPO 60–75** 的听力 passage（conversation 对话 + lecture 讲座）。

> TPO 59 在该平台没有听力内容（页面为空），因此缺失。

## 目录结构

```
TPO_listening/
├── README.md            # 本说明
├── manifest.json        # 全部条目清单（id、TPO、标题、音频 URL、文件路径）
├── article_index.json   # 文章 ID → 标题 索引
├── audio/               # 424 个 MP3 音频（共约 850 MB）
├── transcripts/         # 424 个对应字幕文档（.txt）
├── subjects.py          # 讲座学科提取 + 粗领域归并（构建脚本用）
├── subjects.json        # 276 篇讲座的学科映射（可审计、可复用）
├── build_gh_full_player.py  # 构建 ../listening-all/index.html
├── test_player.js       # 全库播放器的无头回归测试（node test_player.js）
└── gh_full_player.html  # 构建产物，需拷到 ../listening-all/index.html
```

## 全库播放器的构建与验证

```bash
python3 build_gh_full_player.py     # -> gh_full_player.html
node test_player.js                 # 34 条断言，退出码非 0 即失败
cp gh_full_player.html ../listening-all/index.html
```

播放器功能：按套号/年代/学科领域排序，按类型、学科领域、进度（未听/已听）筛选，
搜索覆盖套号、标题、学科名与年份，进度面板按领域给出已听数与剩余时长，
另有一键把 200 集精选页（`../listening/`）的「听完」标记搬过来的按钮
（两个页面同源，localStorage 共享，映射表在构建时生成，200/200 全部可对应）。

## 讲座学科分类

一级学科取自转写开头的旁白句 `Listen to part of a lecture in a ___ class`——这是 ETS
自己写的标签，比按标题猜关键词可靠。276 篇讲座里 **254 篇**有这句旁白。

剩下 22 篇没有旁白句（第 41 套和第 66–71 套的转写普遍缺失），退回按标题 + 开头正文的
关键词判定；其中 5 篇关键词判错，用 `subjects.py` 里的 `OVERRIDE` 表手工钉住，
每条都写了理由。`subjects.json` 的 `origin` 字段区分 `narrator` / `keyword` / `manual`，
页面上也用颜色区分（灰色 = 原始标签，橙色 = 本地推断），不要把两者混为一谈。

粗领域分布（276 篇讲座）：

| 领域 | 篇数 | 占比 |
|---|---|---|
| 艺术/音乐/文学/戏剧 | 66 | 23.9% |
| 生物/动物 | 54 | 19.6% |
| 考古/人类学 | 24 | 8.7% |
| 历史/社会/政治 | 24 | 8.7% |
| 天文/航天 | 23 | 8.3% |
| 环境/生态 | 20 | 7.2% |
| 心理/语言/教育 | 17 | 6.2% |
| 地质/地球/气象 | 15 | 5.4% |
| 工程/技术/理化 | 14 | 5.1% |
| 植物/农业 | 10 | 3.6% |
| 商业/经济 | 9 | 3.3% |

艺术类是全库第一大领域，这和考场回忆的分布一致（艺术占讲座约 19.8%，而阅读只占 4.9%）——
艺术史是听力独有的偏向，值得优先补。

## 文件命名

```
TPO{编号}_{conv|lec}{序号}_{主题}.mp3 / .txt
例：TPO1_conv1_Find_articles_in_the_library.mp3
    TPO37_lec1_Soil_Formation.txt
```

- `conv` = 对话（conversation），`lec` = 讲座（lecture）
- 每套 TPO 听力包含 6 篇（TPO1–54）或 5 篇（TPO55+ 新版缩短后的题量）

## 字幕文档格式

每个 `.txt` 包含：

1. 标题行（`# TPO{n} 听力 ...`）
2. 音频原始 URL（`# Audio: ...`）
3. 逐句内容，带时间戳：

```
[[00:00.00]] NARRATOR: Listen to a conversation between a student and his anthropology professor.
      旁白：请听一段学生和他的人类学教授之间的对话。
[[00:05.64]] FEMALE PROFESSOR: Well, Mathew. Good to see you.
      教授：Mathew，很高兴见到你。
```

即：**英文原文 + 时间戳 + 中文翻译**，可用于精听、跟读与复习。

## 数据统计

- 音频文件：424 个（MP3）
- 字幕文档：424 个
- 总大小：约 852 MB
- 单篇音频时长：约 2.5–6 分钟（对话约 2.5–3 分钟，讲座约 4–5.5 分钟）

## 来源说明

- 数据来源：小站备考（[top.zhan.com/toefl/listen/alltpo{n}.html](http://top.zhan.com/toefl/listen/alltpo4.html)）
- 音频 CDN：
  - TPO1–4：`https://tikustorage-sh.oss-cn-shanghai.aliyuncs.com/TPO_Audio/...`
  - TPO5+：`https://file-corpus.zhan.com/prod/audio/...`
- 材料为官方 TPO 真题的听力音频与原文，仅用于个人学习。
