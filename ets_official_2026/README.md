# ETS 官方 2026 改版对版材料（本地归档）

抓取日期：2026-08-31　总计 25 个文件 / 139 MB / 291 个音频

来源（全部免费公开，无需登录）：
- 考生页 <https://www.ets.org/toefl/test-takers/ibt/prepare.html>
- 教师页 <https://www.ets.org/toefl/teachers-advisors-agents/ibt/teaching/preparing-students.html>
- CDN 前缀 `https://www.ets.org/content/dam/ets-org/pdfs/toefl/`

PDF 首页原文：**"This practice test aligns with TOEFL iBT tests from January 21, 2026. It is not an exact
replica of the actual test; directions and questions have been adapted for paper format usability."**
Copyright © 2025 by ETS。

> 性质说明：这些**不是退役真题**（不是 TPO 那种回收考卷），而是 ETS 为 2026 新格式自制的官方练习卷。
> 但它们是目前唯一 100% 对版、且免费的官方材料。

---

## 一、七套完整模拟卷（这是核心资产）

| # | 题目 PDF | 音频 ZIP | 音频数 |
|---|---|---|---|
| 学生卷 1 | `toefl-ibt-full-length-practice-test-1.pdf` | `student-practice-test-1-audio-files.zip` | 39 |
| 学生卷 2 | `toefl-ibt-full-length-practice-test-2.pdf` | `student-practice-test-2-audio-files.zip` | 39 |
| 教师卷 1 | `toefl-ibt-teachers-resources-practice-test-1.pdf` | `teacher-practice-test-1-audio-file.zip` | 36 |
| 教师卷 2 | `toefl-ibt-teachers-resources-practice-test-2.pdf` | `teacher-practice-test-2-audio-file.zip` | 36 |
| 教师卷 3 | `toefl-ibt-teachers-resources-practice-test-3.pdf` | `teacher-practice-test-3-audio.zip` | 39 |
| 教师卷 4 | `toefl-ibt-teachers-resources-practice-test-4.pdf` | `teacher-practice-test-4-audio-files.zip` | 39 |
| 教师卷 5 | `toefl-ibt-teachers-resources-practice-test-5.pdf` | `teacher-practice-test-5-audio-files.zip` | 39 |

每套 PDF 都含 **Module 1 / Module 2 两阶段结构说明 + 全部题目 + Answer Key**。
「Listen and Choose a Response」在 PDF 里**给出了完整文字脚本**（Woman/Man 的原句 + 四个选项），
所以不听音频也能当文本题刷。

### 每套听力音频的题型分布

学生卷（目录名 `Listening/`）：

| 子目录 | 数量 | 对应官方任务 |
|---|---|---|
| `Question Response/` | 16 | Listen and Choose a Response |
| `Conversations/` | 6 | Listen to a Conversation |
| `Announcements/` | 4 | Listen to an Announcement |
| `Academic Talks/` | 4 | Listen to an Academic Talk |
| `Speaking/Listen and Repeat/` | 8 | 口语复述题 |
| `Speaking/Interview/` | 1 | 模拟面试 |

教师卷同构，仅目录名不同：`Listen and Response/`（16）、`Short Conversation/`、`Announcements/`、`Academic Talk/`。

文件命名带 `Listening1_` / `Listening2_` 前缀 = **Module 1（Router）与 Module 2（自适应分支）**，
可据此还原两阶段顺序。音频格式为 **.ogg**。

**「Listen and Choose a Response」合计 7 × 16 = 112 道**，音频与文字脚本齐全。
这是新听力里题量最大（15–19 题/场）的题型，而 TPO 1–75 里一道都没有。

---

## 二、四科分技能 Lesson Plans

`toefl-ibt-lesson-plan-listening.pdf` / `-reading.pdf` / `-speaking.pdf` / `-writing.pdf`
配套音频：`listening-lesson-plans-audio.zip`（7）、`speaking-lesson-plans-audio.zip`（11）

## 三、评分标准与范例

- `speaking-rubrics.pdf`、`writing-rubrics.pdf`、`speaking-performance-levels.pdf`
- `sample-responses-audio-files.zip`（6 个口语范例录音）
- `teacher-faq.pdf`

---

## 四、衍生文件

- `txt/`：7 套模拟卷的 `pdftotext -layout` 纯文本版，便于 grep / 二次加工
- `extract_listening.py`：从 `txt/` 抽取听力题，生成下面的 JSON
- `map_audio.py`：把 ZIP 里的音频与 JSON 条目一一对应（161/161 全部命中）
- `listening_2026.json`：**结构化听力题库（含音频路径）**
- `extract_audio.py`：把 JSON 引用的 196 个音频从 ZIP 解出并摊平到 `../listening-2026/audio/`
- `audio_len.py`：不依赖 ffmpeg 读音频时长（ogg 走 granulepos 精确值，mp3 按比特率估算）
- `build_2026_player.py`：生成 `../listening-2026/index.html` 练习页
- `test_2026_player.js`：练习页的无头回归测试（`node test_2026_player.js`，48 条断言）
- `urls.txt`：下载清单（文件名，前缀见上）
- `download.log`：抓取时的 HTTP 状态与字节数

### `listening_2026.json` 内容

7 卷 × 2 个 Module，共 **238 题，答案 100% 齐全**（与 PDF 内 Answer Key 逐题核对一致：
每卷 Module 1 = 18 题、Module 2 = 16 题）。238 题全部是 4 选项。

> 修过的抽取 bug：pdftotext 会把过长的选项折成两行（中间还夹空行），旧版解析一见到非选项
> 正文行就收尾，于是教师卷 4 Module 1 第 17 题的 (C) 被截断、(D) 整条丢失，只剩 3 个选项。
> 现在 `collect_options()` 按「上一行没有句末标点 + 下一行以小写开头」判定折行续接，
> 全库重跑后差异只有这一处，其余 237 题逐字未变。

| 条目类型 | 数量 | 对应官方任务 |
|---|---|---|
| `choose_response` | 112 | Listen and Choose a Response（听答题） |
| `conversation` | 21 | Listen to a Conversation（短对话） |
| `announcement` | 14 | Listen to an Announcement（学术公告） |
| `academic_talk` | 14 | Listen to an Academic Talk（学术讲座） |

结构：

```json
{ "tests": [ { "test": "...", "modules": [ { "module": 1, "items": [
  { "kind": "choose_response", "number": 1,
    "prompt": "Woman: Didn't I just see you in the library an hour ago?",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answer": "A" },
  { "kind": "conversation", "prompt": "Listen to a conversation.",
    "transcript": ["Woman: ...", "Man: ..."],
    "questions": [ {"number": 9, "question": "...", "options": {...}, "answer": "A"} ] }
] } ] } ] }
```

`choose_response` 直接自带完整文字脚本，可当纯文本题刷，不依赖音频。

每个条目还带 `audio` 字段，格式为 `<zip 文件名>::<zip 内部路径>`（161 个条目全部命中，
另有 35 个条目带 `audio_directions` 指导语音频）。文件名里的
`Listening1_` / `Listening2_` 即 Module 1（Router）与 Module 2（自适应分支）。
教师卷 1 是 `.mp3`，其余是 `.ogg`。

重新生成：`python3 extract_listening.py && python3 map_audio.py`（需要 poppler 的 `pdftotext`）。

> ⚠️ 顺序有依赖：`extract_listening.py` 会**整份重写** JSON，把 `map_audio.py` 写进去的
> `audio` / `audio_directions` 字段冲掉。所以只要重跑抽取，就必须紧接着重跑映射。

## 五、生成练习页

```bash
python3 extract_listening.py     # txt/ -> listening_2026.json（会清掉 audio 字段）
python3 map_audio.py             # 补回 audio / audio_directions
python3 extract_audio.py         # zip -> ../listening-2026/audio/ + audio_map.json
python3 build_2026_player.py     # -> ../listening-2026/index.html
node test_2026_player.js         # 48 条断言，退出码非 0 即失败
```

页面在 `listening-2026/`：按四类题型分 tab，可按卷 / Module / 进度筛选，
听答题音频播完后有可调作答倒计时（5/8/12 秒或不限，**这是本页自设的练习节奏，
官方从未公布该题型的作答时限**），全部题答完才自动显示原文，成绩按题型统计。
键盘 A/B/C/D 选项、空格重播、N 下一条。做题记录存本机 localStorage（键 `hl2026_v1`）。

音频**不入库**（见根目录 `.gitignore`）：196 个文件 / 28 MB 是 ETS 原始音频，
放进公开仓库属于二次分发。线上部署缺音频时页面会自己弹横幅说明获取办法。

### 音频备份：HuggingFace 私有 dataset

<https://huggingface.co/datasets/xxfasdf/toefl-2026-listening-audio>（**private**，需本人账号）

| 路径 | 内容 |
|---|---|
| `audio/` | 摊平后的 196 个音频，练习页直接引用的那份 |
| `original-zips/` | ETS 官方原始音频 zip（7 套模拟卷 + lesson plan + 口语范例） |

恢复本地音频（两种都行）：

```bash
# A. 从私有备份拉（快）
hf download xxfasdf/toefl-2026-listening-audio --repo-type=dataset \
  --include "audio/*" --local-dir listening-2026/

# B. 从官方 zip 重解（无需 HF 账号，但要先按第六节重新下载 zip）
python3 ets_official_2026/extract_audio.py
```

> macOS 上若 `hf` 报 `Operation not permitted ... /xet/staging`，是沙箱不让写
> `~/.cache/huggingface`；加 `HF_XET_CACHE=$PWD/.hf_cache/xet` 即可。

### 实测音频时长（`audio_len.py`，ogg 按 granulepos 精确计算）

| 题型 | 条数 | 题数 | 平均 | 区间 |
|---|---|---|---|---|
| 听答题 | 112 | 112 | **2.3 s** | 1.1–6.1 s |
| 短对话 | 21 | 42 | **24.9 s** | 17.2–33.2 s |
| 公告 | 14 | 28 | **22.8 s** | 13.2–31.6 s |
| 学术讲座 | 14 | 56 | **89.2 s** | 67.5–119.0 s |

听力音频合计 39.1 分钟（不含 directions）。答案分布 A 64 / B 67 / C 52 / D 55，
没有明显偏向某个选项。

> 对比：旧格式（TPO）讲座普遍 3–5 分钟，新格式学术讲座只有 1.5 分钟左右，短对话更是
> 从 3 分钟压到 25 秒。**篇幅是新旧格式差别最大的一处**，用 TPO 练长听力的耐力对新格式意义不大。

## 六、重新抓取

```bash
B=https://www.ets.org/content/dam/ets-org/pdfs/toefl
while read -r f; do curl -sSL -o "$f" "$B/$f"; done < urls.txt
```
