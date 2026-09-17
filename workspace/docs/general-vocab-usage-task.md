# 「通用词汇」高频用法补充 · 子任务作业流程

仓库根目录：`/Users/jinzili/Documents/归档/tofel`（可写）。

## 步骤

1. 用 read 工具完整读 `workspace/docs/general-vocab-usage-style.md`，严格照里面的骨架和样板写作。
2. 运行 `python3 workspace/scripts/apply_general_usage.py --list-pending`，
   拿到 `bare` 数组（尚未补用法的词，已按字母序排好）。按派给你的**下标区间**（1-based）取词。
3. 从页面数据里读出这些词现有的 `d` / `f`，用来保留原有词性标签和释义方向：

   ```bash
   python3 - <<'PY'
   import re, json
   h = open('site/vocab/disciplines/index.html', encoding='utf-8').read()
   data = json.loads(re.search(r'const DATA = (\[.*?\]);\n', h, re.S).group(1))
   gen = [t for t in data if t['name'].startswith('通用词汇')][0]
   idx = {w['w']: w for w in gen['words']}
   for w in ['词1', '词2']:
       print(json.dumps(idx[w], ensure_ascii=False))
   PY
   ```

4. 为每个词写出新的 `d`（一行短释义）和 `f`（多行展开），写进指定的 JSON 文件。
5. 自检 `python3 -c "import json,sys;d=json.load(open('文件路径'));print(len(d))"` 能跑通、键数正确。

## 通用写作要求

- 每词 **2–4 条**「高频用法」，每条 1–2 个短例句（10–20 词），英文句后**空一格**再写全角括号中文翻译。
- 多义词按义项分列，先写托福里更高频的那个义项。
- 必须交代清楚这些容易考的点（有则写，无则略）：
  - 可数性（不可数就写明 ✗ a xxx / ✗ xxxs，以及怎么论「个」）；
  - 固定介词（compete with / for / in 这类）；
  - 及物 / 不及物，后面接 doing 还是 to do；
  - 语域与强度（正式书面 / 口语 / 比 hate 更书面之类）；
  - 褒贬色彩。
- 原表词性标注明显标错的（例如把 `besides` 标成 `adj.`），改对，并在 `f` 第一行说明原标注有误。
- 如果这个**词形本身**在真实语料里低频（典型是 -ing 形容词、抽象名词化形式），就在第一行说明，然后把高频用法落在真正常用的同族形式上（如 `afflicting` → `be afflicted with`；`briskness` → `brisk`）。
- 形近易混词加一行「辨析：」（complimentary / complementary、vocation / avocation、beside / besides 这类）。
- 学科术语（`prime number`、`quantum theory`、`neurotransmitter` 之类）不要硬凑生活化例句，给该术语在讲座和阅读里真实出现的搭配与句式。
- 只写真实、地道的搭配。**不确定的搭配宁可不写，绝不编造。**
- 禁止 HTML 标签，禁止出现 `<`、`>` 字符。
- `d` 一行、100 字符以内，格式：`词性. 压缩释义（要点）；高频用法 搭配1、搭配2、搭配3`。

## 交付

只新增指定的那个 JSON 文件，**不要改动仓库里的其他文件**（包括页面本身，套用由主控统一执行）。

## 附录：第三类词（早期手工润色词，需统一格式）

这类词的 `f` 已有若干条用法行，但用的是更早的手写格式：没有「高频用法一/二/三」标签、英文例句多数没有中文翻译、`d` 往往只剩一个干释义（没有「；高频用法 …」这一段）。它们**不在** `--list-pending` 的输出里，词表由主控直接给出。

处理要求：
1. 用 read 从 `site/vocab/disciplines/index.html` 的 `const DATA` 里取出该词现有的 `d` / `f` 作为素材。
2. **原有信息一条都不能丢**：已有的搭配、句式、语域标注（如「极正式书面语」「议论文句式」）、辨析要全部保留，改写进规范骨架。
3. 补足规范要求的部分：每条用法配 1–2 个短例句并加全角括号中文翻译；`d` 改写成 `词性. 释义；高频用法 搭配1、搭配2`（一行，≤100 字符）。
4. 其余格式要求（`f` 必须多行、禁止 `<` `>`、可数性与介词提醒、必要时「辨析：」「派生：」行）与正文一致。
