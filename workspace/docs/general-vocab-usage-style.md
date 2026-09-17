# 「通用词汇」高频用法补充 · 写作规范

学科总表页面 `site/vocab/disciplines/index.html` 里，每个词条有两个字段：

- `d`：列表里直接显示的**一行**短释义。
- `f`：点开词条后显示的展开内容（`white-space:pre-wrap`，换行按 `\n` 原样呈现）。

本任务只做一件事：给「📝 通用词汇」里那些 `f` 只有一行干释义的词，补上**高频用法**。

## f 字段的格式（严格照抄这个骨架）

```
<词性>. <释义>（可选：语域/可数性/强度/易错点等一句话补充）
高频用法一：<英文搭配骨架> —— <中文说明>
<English example sentence.> （<中文翻译>）
<English example sentence.> （<中文翻译>）
高频用法二：<英文搭配骨架> —— <中文说明>
<English example sentence.> （<中文翻译>）
用法提醒：<最容易错的点，如介词、可数性、时态、褒贬>
辨析：<与近义词的区别，只在真有必要时写>
派生：<高频派生词及其固定搭配，只在真有必要时写>
```

已定稿的样板（`acrimony`、`abhor`、`word of mouth`）就是这个样子：

```
n. 尖刻、恶言相向、剑拔弩张的敌意（不可数：不加冠词、无复数；专指争执、谈判、离婚这类场合的火气与恶意）
高频用法一：without acrimony / with acrimony —— 不带／带着敌意地
They divorced without acrimony. （他们离婚时没有闹得难看。）
The proposal was debated with considerable acrimony. （这项提案的辩论相当激烈难听。）
高频用法二：end in acrimony / break up in acrimony —— 以不欢而散收场（最常见的动词搭配）
The negotiations ended in acrimony. （谈判不欢而散。）
高频用法三：acrimony between A and B / acrimony over sth —— 双方之间的／因某事而起的敌意
There is deep acrimony between the two factions. （两派之间积怨很深。）
常见修饰：bitter / deep / considerable / much acrimony（不能说 an acrimony）。
派生：acrimonious adj. 尖刻的（本表另有词条），acrimonious divorce / debate / dispute 是固定高频搭配。
词源记忆：与 acrid（刺鼻的）同出拉丁语 acer「尖锐」——acrid 刺鼻子，acrimony 刺耳朵。
```

```
v. 憎恶、极度厌恶（正式书面语，强度远高于 dislike，比 hate 更书面；阅读里常与 detest / loathe 同义替换）
高频用法一：abhor + 名词 —— abhor violence / cruelty / injustice / discrimination（憎恶暴力／残忍／不公／歧视）
Most people abhor cruelty to animals. （多数人都憎恶虐待动物。）
高频用法二：abhor + doing sth —— 后面接动名词，不接不定式（✗ abhor to do）
He abhors being told what to do. （他极其反感被人指挥。）
用法提醒：abhor 是状态动词，一般不用进行时（✗ I am abhorring it）。
派生：abhorrent adj. 令人憎恶的（本表另有词条）；abhorrence n. 憎恶，hold sth in abhorrence（对某事深恶痛绝）。
```

## d 字段的格式

一行，把原短释义压紧后接上最关键的搭配，用 `；高频用法 ` 引出，中间用 `、` 分隔：

```
n. 尖刻、恶言相向（不可数，指争执中的敌意与火气）；高频用法 without / with acrimony、end in acrimony（不欢而散）、acrimony between A and B、acrimony over sth
```

`d` 控制在 100 个字符以内，不要换行。

## 硬性要求

1. **保留原有词性标签**。原来写 `adj. 代理的；临时的 / n. 表演；演技`，展开后第一行仍要把这两个词性都交代清楚，多义词按义项分别给用法。
2. **不许改变原释义的意思**；可以补充、修正明显不准确的中文（如把 `besides` 的 `adj.` 改成正确的 `prep./adv.`），但要在第一行说明。
3. 面向**托福**：搭配和例句取学术讲座、校园对话、阅读文章里真会出现的用法，不要生僻的文学用例。
4. 每个词写 **2–4 条高频用法**，每条 1–2 个例句；例句要短（10–20 词），英文句后空一格再写全角括号的中文翻译。
5. 不写任何 HTML 标签，不用 `<`、`>` 字符；`&` 尽量避免。
6. 只用真实、地道的搭配。不确定的搭配宁可不写，绝不编造。
7. 中文用简体，标点用中文全角标点；英文搭配骨架里的斜杠两边留空格（`without / with acrimony`）。
8. 短语词条（如 `a range of`、`be reserved to`）标签写 `phr.`，重点讲它在句子里的位置和常见主语／宾语。

## 输出

写一个 JSON 文件，结构：

```json
{
  "单词": {"d": "一行短释义…", "f": "多行展开释义…"},
  "另一个词": {"d": "…", "f": "…"}
}
```

`f` 里的换行在 JSON 里就是 `\n`。文件必须是合法 JSON、UTF-8、无 BOM、不带注释。
