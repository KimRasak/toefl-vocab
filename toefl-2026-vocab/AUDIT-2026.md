# 2026 新托福词库审计（第一轮）

## 结论

当前词库共 **2,670 条、无重复词条**，已经覆盖大量旧 TPO 学科词和校园听力场景；不建议粗暴删除整批 AWL 或学科词。2026-01-21 起考试重点转向短任务与真实校园/学术沟通，因此应采用“核心保留、低价值降权、场景补齐”的策略。

## 已修复的发音可靠性

- 单词卡和词表点击均经过同一个播放函数。
- 优先使用设备可用的英文系统语音（较慢、较自然的 `en-US/en-GB` 声音）；系统语音不可用时再尝试 Youdao、Google。
- 为两个网络音频候选增加 `onerror` 与 `play()` rejected 双重降级；最终失败会提示用户重试。
- 用播放代次 token 防止快速连点时旧请求覆盖新请求。
- 移除无音频源的全局 autoplay 解锁 hack，并取消答题后抢播下一词；发音只由明确的 🔊/词表点击触发。

## 不建议直接删除（保留但可降权）

1. **泛学术 AWL 词**：`area, individual, issue, function, approach` 等在短阅读、学术讨论和讲座中仍是高频骨架词；建议降低展示优先级，而不是删除。
2. **旧 TPO 深度学科词**：古生物、海洋、天文、生态、艺术史词可作为阅读/讲座扩展层，不应伪装成 2026 高频核心；建议标记为“扩展”。
3. **大量生活服务场景**：租房、银行、汽车、理发等对新题型不是同等高频，但能支持 `Read in Daily Life` 和校园对话，建议合并重复模板、降权而非删除。
4. **发音陷阱、连读缩略、回应模式**：虽然不是传统“词汇”，却直接服务短听力和 `Listen and Choose a Response`，应保留。

## 应优先人工复核/降权的候选

- 过于泛化或不构成识别难点的模板：`Well...`, `Not much, you`, `Same old, same old`, `Sure, why not`。
- 非校园优先、且已有同义覆盖的生活细节：`理发美容`、`服装购物`、`汽车服务`、部分 `节日假期`。
- 需要拆成独立发音卡的斜杠条目：`dessert / desert`、`accept / except`、`advice / advise`、`breath / breathe`、`quite / quiet` 等。当前播放逻辑只播放斜杠前一项，不能把它们当作一个完整单词卡。
- 含占位符的句型：`Take ... for example`、`Does ... work for you`、`While X ..., Y ...`。应作为句型卡单独处理，或在发音字段中提供自然例句，而不是按字面 TTS。
- `L1 transfer` 等术语应补充中文解释与明确的学术语境，否则优先级应低于新制核心任务词。

## 2026 新制最重要的缺口

根据本地 `TPO调研-2026-08-31.md` 和 `ets_official_2026/README.md`，旧 TPO 1–75 没有现行听力占比最大的 **Listen and Choose a Response**；词库应新增“听到问题/意图后立即作自然回应”的功能语块，而不能只扩充长讲座名词。

### P0：短听力即时回应

- 请求/许可：`Could you ...?`, `Would you mind ...?`, `Is it okay if ...?`, `Sure, go ahead.`, `I'm afraid I can't.`
- 澄清/确认：`Could you say that again?`, `What I mean is ...`, `So you're saying ...?`, `Exactly.`, `Not quite.`
- 建议/安排：`Why don't we ...?`, `How about ...?`, `That works for me.`, `I'll check and get back to you.`
- 问题/解决：`I can't access ...`, `Have you tried ...?`, `That should fix it.`, `I'll put in a request.`
- 意图识别：`The point is ...`, `What she's getting at is ...`, `It turns out ...`, `I didn't realize ...`

### P0：新阅读任务

`Complete the Words` 需要词族和词内形态线索：`-tion/-sion, -ment, -ity, -ive, -al, -ize/-ise, un-, re-, over-`，以及高频词族如 `analyze/analysis/analytical`、`vary/variety/various`、`respond/response/responsive`。现有词缀类可保留，但应增加“词族互换 + 句中词性”而不只是孤立词。

`Read in Daily Life` 应补校园短文本词群：`deadline, eligibility, prerequisite, enrollment, fee waiver, office hours, room reservation, maintenance request, appointment, vaccination, accessibility, lost and found, student ID, transcript`。

### P1：新口语与写作

- `Listen and Repeat`：连读、弱读、数字/日期/专名、校园地点和课程信息短句。
- `Virtual Interview`：经历、优势、困难、选择理由、计划、团队合作：`reliable, adaptable, prioritize, collaborate, resolve, outcome, motivated, relevant experience`。
- `Build a Sentence`：基础句法连接：主谓一致、从句、被动、比较、因果、让步、限定性关系从句。
- `Write an Email`：称呼、请求、解释、道歉、改期、附件、结尾礼貌表达：`I am writing to ask..., Would it be possible..., I apologize for..., Please find attached..., Thank you for your consideration.`
- `Academic Discussion`：立场、让步、证据、回应同学观点：`I agree to some extent..., A stronger reason is..., This is consistent with..., However, this overlooks...`

## 本轮已补充的新场景词汇

在不新增完整题型练习系统的前提下，已向 `data.js` 补充 105 条场景词汇，其中 77 条是此前不存在的独立 `w`；其余是同一词在不同场景下的复习入口（不将总记录数误称为独立词数），重点覆盖：

- 超市：过道、结账、自助结账、优惠券、收据、退款、缺货、过敏饮食等；
- 图书馆：馆藏检索、索书号、电子期刊、全文、安静区、小组学习室、打印扫描等；
- 校园服务：迎新、注册退课、学位要求、成绩单、门禁卡、费用减免、维修申请、失物招领等；
- 医疗健康：预约、处方、保险、过敏反应、症状和复诊等；
- 交通：公交线路、时刻表、绕行、道路封闭、换乘、无障碍入口等；
- 租房、邮局快递、银行金融：租赁协议、杂费、物业、包裹柜、追踪号码、账户、手续费等。

这些词被放入现有场景分类，优先级以 `r=2/3` 为主，便于在原有学习流程中直接复习；没有把它们伪装成完整 2026 新题型题库。

## 第二轮：以出题官视角新增的话题场景

再补 87 条、19 个新分类，全部按 2026 官方场景域（educational / academic navigational / social interpersonal / public）选取，而不是按旧 TPO 学科名词扩张：

| 新分类 | 覆盖的出题情境 |
| --- | --- |
| 听力-课程安排 | 研讨课、补考、出勤与参与分、小组项目 |
| 听力-学术规范 | 学术诚信、引用格式、改写转述、引用文献 |
| 听力-实验课 | 实验安全、操作步骤、数据记录、实验搭档 |
| 听力-科研参与 | 海报展示、研究助理、问卷、同意书 |
| 听力-学业支持 | 同伴辅导、免预约辅导、学习方法讲座 |
| 听力-在线学习 | 提交系统、课程网站、讨论区、共享文档、重置密码 |
| 听力-学费账单 | 学费账单、分期方案、滞纳金、退款政策 |
| 听力-校园餐饮 | 学生餐厅、餐卡次数、饮食限制、打包 |
| 听力-宿舍生活 | 宿舍楼、室友约定、安静时段、洗衣房 |
| 听力-社团活动 | 社团招新、学生组织、志愿机会、报名表 |
| 听力-讲座活动 | 报告厅、主题演讲、专题讨论、回复出席 |
| 听力-求职实习 | 招聘会、推荐信、简历讲座、申请截止 |
| 听力-海外交流 | 交换项目、寄宿家庭、签证申请 |
| 听力-无障碍支持 | 字幕、辅助技术、延时考试、代记笔记 |
| 听力-紧急通告 | 恶劣天气、停课、就地避险、疏散路线 |
| 听力-可持续环保 | 一次性用品、节能、堆肥 |
| 听力-体育设施 | 场地预订、校内联赛、健身课 |
| 阅读-标识告示 | 宣传单、服务窗口、施工中、暂时关闭、禁止进入 |
| 阅读-社交短文 | 社交帖子、评论串、转发 |

同时给页面新增 `日常阅读` 这一顶层分类（`getMacro` 支持 `阅读-` 前缀），让标识、告示和社交短文本不再被归入“其他”。

## 执行建议

1. 先将条目增加 `type/priority` 或独立元数据，不破坏用户已有学习进度；不要直接从 `VOCAB` 删除。
2. 把斜杠词拆成两张卡，或新增 `speak` 字段，确保每个可学习目标各有声音。
3. P0 先补 100–150 条短回应/校园短文本词语，再补口语面试和邮件/学术讨论语块。
4. 使用 ETS 2026 官方规格和样题逐条复核，旧 TPO 只作为能力训练，不作为现行题型覆盖证明。

## 第三轮：以官方对版卷为判分标准的 P0 补齐

前两轮补词靠的是「场景推演」，这一轮改成**用 `../ets_official_2026/` 的 7 套 ETS 官方 2026 对版练习卷（42k 词全文 + `listening_2026.json` 的 161 道结构化听力题）做逐条检索**，只补真正出现在官方材料里的层级。

### 诊断：稀有度错配

把「日常社交 / 校园事务」两个话题域下的词条逐条在 7 套卷全文里做词形还原检索：

| 话题域 | 零命中条数 |
| --- | --- |
| 日常社交（购物/餐饮/交通/旅行/健身/维修/预约/活动安排） | 195 |
| 校园事务（课程/作业/图书馆/社团/校园活动/设施维护） | 131 |

典型零命中词：`bellhop`、`optometrist`、`blow-dry`、`kayaking`、`matinee`、`doggie bag`、`intramural`、`study carrel`、`interlibrary loan`、`e-journal`、`call number`、`meal swipe`、`no admittance`。

问题不是词不够多，而是**收词层级错了**：词库偏向低频具体名词，官方卷真正用的是中频通用词。反例最刺眼的一组 —— `lounge` 在官方卷出现 9 次、`downtown` 13 次、`fitness` 16 次，此前一条没收；而 `bellhop`、`optometrist` 收了。

另外，`作业` 和 `设施维护` 这两个子话题**此前完全没有对应分类**，而设施维护通告恰恰是官方 announcement 题（14 道）的主力题材。

### 本轮实际改动：+381 条 / 21 个分类行

| 新分类 | 条数 | 依据 |
| --- | --- | --- |
| 听力-设施维护 | 59 | announcement 题主力题材；`closure` `scheduled maintenance` `technician` `alternate entrance` `we apologize for the inconvenience` |
| 听力-时间日期 | 43 | 官方卷星期名 67 次、月份名 86 次、时刻表达 40 次；预约与通告题的答案点几乎都落在时间信息上 |
| 听力-作业任务 | 35 | 此前无独立分类；`due` `draft` `turn in` `partial credit` `handout` `slides` |
| 听力-应答-疑问词匹配 | 14 | Listen and Choose a Response |
| 听力-应答-反问确认 | 12 | 同上 |
| 听力-应答-请求许可 | 12 | 同上 |
| 听力-应答-建议安排 | 12 | 同上 |
| 听力-应答-问题求助 | 12 | 同上 |
| 听力-应答-信息核对 | 10 | 同上 |
| 补进既有 12 个场景分类 | 172 | 官方卷高频、原先缺失的中频通用词 |

补进既有分类的分布：社团活动 +24（原仅 4 条）、课程安排 +23（原仅 5 条）、健身 +18、交通 +17、讲座活动 +14、餐饮 +13、旅行 +13、超市 +12、图书馆 +12、预约 +11、制定计划 +10、校园服务 +5。

中频词的收录标准是二选一，避免稀释队列：**(a) 词形本身陌生**（`gratuity` `custodian` `turnstile` `curbside pickup`），或 **(b) 熟词在该场景下的特定义项就是考点**（`check` = 餐厅账单、`due` = 应上交、`fix` = 解决、`formal` = 正式文体、`wing` = 楼翼、`recall` = 图书被召回）。纯基础词（`lunch` `coffee` `kitchen` `healthy`）一律不收。

### 即时应答训练层的编码方式

Listen and Choose a Response 是官方听力占比最大的题型（**112 / 161 题，70%**），考的是听懂意图后选自然回应，正确答案往往不含任何生僻词 —— 官方卷第 1 题的干扰项 B 恰恰是含 `reference section` 的那个，**背这个词反而会被诱导选错**。

这一层不新增字段，直接复用现有的「听音 → 回想 → 翻卡」卡片机制：

- `w` = 播放的刺激句（TTS 朗读的就是它）
- `m` = `✅ 正确回应｜干扰项套路提示`
- `p` = 应答类型标签（反问确认 / 疑问词匹配 / …）

配套的两处页面改动：`isSentenceCard()` 判定整句卡走小一号排版，并用 flex `order` 把刺激句排在正确回应之前；`.chip .cw` 加省略号截断，避免一览页里整句 chip 撑成多行。

### 数据安全约束

云端进度是**按 `VOCAB` 索引编码**的（`encodeProgress` 用 `wordToIndex`），所以：

- 新条目一律**追加到末尾**，绝不插入中间；测试断言既有词索引仍落在原有 2862 区间内。
- 发现的 2 处历史重复（`tracking number`、`signature required` 在 `听力-邮局快递` 各出现两次）**没有删除**，而是就地改写成 `delivery confirmation` 和 `hold for pickup` —— 删除会让后续所有索引前移，已同步的进度会整体错位。

### 回归测试

`node test_sync.js` 从 41 条断言扩到 **66 条**，新增 25 条覆盖：新分类归属与条数、应答层 6 个子类齐全、每条都有正确回应与干扰项提示、刺激句不被 `cleanForSpeech` 的斜杠规则截断、整句卡判定、既有词索引未移动、新词进度编解码往返、全库「词+分类」组合唯一、官方高频中频词已补齐、一览页列出新分类。

### 仍未做（下一轮）

- **例句字段**：3243 条仍全部没有例句。日常社交词的考点是搭配和语域（`fix` vs `repair`、`store` vs `shop`），孤立中文释义训练不出来。
- **20 条斜杠条目 TTS 只读前半**：`dessert / desert`、`accept / except` 这类，后半永远听不到（第一轮已记录，仍未修）。
- **12 条占位符条目**：`Let's meet at`、`Does ... work for you` 直接送 TTS 会读出不自然的断句，且在官方卷里全部零命中。
- **326 条零命中词未降权**：应加 `低产出` 标记从默认队列移出（保留可查），`听力-医疗健康` 31 条建议压到 10 条左右。
- `Write an Email` 功能语块（官方卷 `email` 87 次、`Dear` 16 次、`Regards` 15 次）。

## 依据

- [ETS 2026 TOEFL iBT Test Specifications](https://www.ets.org/content/dam/ets-org/pdfs/toefl/toefl-ibt-test-specifications-2026.pdf)
- [ETS China Test Content and Structure](https://www.cn.ets.org/toefl/china/toefl/content-structure.html)
- 本地研究：`../TPO调研-2026-08-31.md`、`../ets_official_2026/README.md`
