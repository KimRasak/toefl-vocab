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

## 第四轮：按用户水平的已知词降权 + 混淆音连读 + 跨页登录统一

用户水平：CET-4 554 / CET-6 555，正在备考 2026 托福。核心动作是「把用户**肯定已会的词**从每日新词队列里移出，让队列优先出现可能不会的词」。

### 97 条 CET 级已知词降权到 P1

逐条核对 `data.js` 中 r≥3 的听力场景词，把六级考生**无疑已掌握**的基础词全部降到 `r=1`（权重 0.2，队列最后出现，仍可在分类一览中查到）：

- 烹饪/餐饮：`bake grill steam stir-fry chop microwave homemade`；`tip takeout vegetarian beverage appetizer`
- 医疗：`fever headache cough dizzy clinic pharmacy treatment insurance`
- 健身/家务/休闲：`yoga stretch workout`；`vacuum recycle iron laundry do the dishes take out the trash`；`picnic camping board game sold out`
- 运动/节日：`score season gear cycling`；`Thanksgiving fireworks barbecue decoration gift card`
- 交通/旅行/酒店：`delay platform departure arrival`；`passport`；`front desk luggage`
- 购物/邮局/银行：`receipt refund exchange discount coupon checkout aisle on sale out of stock`（购物客服副本；超市同词本就是 r2/3）；`package parcel`；`ATM PIN`
- 租房/天气/科技：`rent roommate move in move out`；`forecast humidity thunderstorm breeze`；`app download upload log in sign out inbox spam bluetooth screenshot`；`crash backup Wi-Fi charger battery storage`
- 发音陷阱中过于日常的：`women towel drawer vegetable comfortable temperature interesting`
- 保留不降权（虽是熟词但是 2026 考点/难点）：`entrée side dish specials`、`produce`（农产品义项）、`drizzle overcast heatwave`、`precipitation`、`overdue fine` 等。

`r` 分布从 `{1:411, 4:1088}` 变为 `{1:508, 4:994}`；纯字段改动，索引与云端进度编码完全不受影响（82/82 测试全绿）。

### 混淆音卡片 TTS 双词连读

此前 `speak()` 用 `cleanForSpeech` 按 ` / ` 切分只读前半，`dessert / desert` 永远只能听到 `dessert`，听不到对比。现在 `speak()` 检测斜杠成对词，把两部分拼成 `dessert, desert` 连读，让用户亲耳听到重音/音位差异（17 条混淆音 + `Slight / slightly`、`Um / Uh` 都受益）。

### 跨页登录统一（难词页）

`merged-by-discipline/index.html`（难词页）原本用独立单页凭证 key，与词库页不互通。现将其迁移到与词库页相同的**跨页面共享 Gist 凭证块**（`test_sync.js` 断言两份逐字一致）：token 共享，两页各用独立 `gistId` slot（`toefl2026-progress` / `hard-words`），任一一页登录后另一页自动共用、自动认领本页 Gist；登出会同时断开两页。旧单页凭证自动迁移。修好了此前 3 条失败断言，测试恢复到 82/82。

### 过短释义补全

`layer`（层）、`grill/steam/stir-fry`（烤/蒸/炒）的释义从单字扩到带烹饪/层级语境的中文说明。

### 仍待办（下一轮候选）

- 最薄的 2026 场景分类：`听力-体育设施`(3)、`听力-学业支持`(3)、`听力-可持续环保`(3)、`听力-理发美容`(3)、`阅读-社交短文`(3) —— 若要扩充，须像第三轮那样用 `ets_official_2026/` 官方材料逐条验证，避免重回低频具体名词。
- `听力-医疗健康` 剩余词的产出率复核、12 条占位符句型的 TTS 处理。

## 第五轮：补齐 2026 两大写作/口语任务语块 + 稀有零命中词降权

基于官方 7 套卷（`ets_official_2026/txt/`，约 4.2 万词）的语料证据，补齐此前缺失的两大 2026 任务语块：

### 新增「写作-邮件」23 条（r=5）

官方卷中 `email` 出现 83 次、`dear` 16 次、`regards` 15 次、`schedule` 39 次、`meeting` 35 次——Write an Email 是 2026 写作必考任务，且 "Read an email" 也是阅读新题。按任务结构补齐功能语块：称呼（`Dear Professor`、`Dear Sir or Madam`）、说明目的（`I am writing to`、`I would like to`）、礼貌请求（`I was wondering if`、`Could you please`、`I would appreciate it if`）、致歉（`I apologize for`、`I am sorry for`）、追问（`Could you let me know`、`Please let me know`、`At your earliest convenience`）、附件（`Please find attached`、`I have attached`）、结尾（`Thank you for your time`、`I look forward to hearing from you`、`Please feel free to contact me`）、落款（`Best regards`、`Regards`、`Sincerely`）、`ASAP`。`Would it be possible to`、`Unfortunately`、`due to` 已在听力分类，不重复收。

### 新增「口语-虚拟面试」18 条 + 口语顶层宏

2026 口语 Virtual Interview 必考（经历/优势/困难/选择理由/团队合作）。补齐：`reliable adaptable prioritize collaborate teamwork leadership problem-solving motivated self-motivated detail-oriented relevant experience take the initiative step up meet deadlines work under pressure strengths and weaknesses career goal contribute to`。同时在 `index.html` 增加 `speaking` 顶层宏（`口语-` 前缀 → 口语表达卡片，图标 🗣️），仪表盘自动新增一张卡片，`test_sync.js` 82 条断言全绿。

### 稀有零命中词降权 14 条

对第三轮诊断出的「低频具体名词」做收敛式处理：只降权**确实稀有且 2026 价值低**的 14 条（`bellhop optometrist kayaking matinee haircut trim blow-dry gratuity turnstile intramural study carrel potluck fortnight groundskeeper`）到 P1；**保留**官方高频/中频通用词（`allergy ingredient landlord engine symptom` 等零命中但通用）、全部发音陷阱/混淆音/连读缩略（教学价值不受语料命中影响），以及 P0 明确要的图书馆词（`e-journal call number interlibrary loan`）。

词库总量 3243 → 3284；云端进度索引（`wordToIndex`）对既有 3243 条逐字保持不动，仅追加，进度编码完全兼容。

## 第六轮：补齐最薄场景分类 + 全库释义/音标抽查修正

### 补齐 4 个最薄场景分类 17 条（官方语料逐条验证）

上一轮「仍待办」里最薄的 2026 场景分类已补齐（`ets_official_2026/txt/` 语料佐证产出率）：

- **听力-学业支持** 7 条：`workshop`（22 次）、`tutoring session`、`help session`、`supplemental instruction`
- **听力-可持续环保** 7 条：`renewable`（6 次）、`zero waste`、`eco-friendly`、`compostable`（校园环保话题）
- **听力-体育设施** 7 条：`pickup game`、`home game`、`away game`、`rec center`
- **阅读-社交短文** 8 条：`caption`、`hashtag`、`direct message`、`trending`、`viral`（新阅读题"Read a social media post"）

均避开低频具体名词，只收官方材料中真实出现的高频场景表达。

### 全库释义/音标抽查（4 个子代理并行审 2258 条）

按分类抽样 2258 条（发音陷阱 109 / 听力场景 1194 / 学术词 955）交由子代理逐条核对 IPA、中文释义与词性标签，采纳修正 **8 条客观错误 + 1 条自查收窄**（其余为可接受释义或风格问题，从宽原则未改）：

| 词 | 分类 | 原释义 | 修正 |
|---|---|---|---|
| `plough` | 听力-发音陷阱 | [plaʊ 不是"普劳"] | [plaʊ]（gh 不发音，不是"普劳格"）——原纠错自相矛盾，"普劳"本就是正确近似 |
| `gratuity` | 听力-餐饮 | 服务费（已含小费） | 小费；酬金（账单自动加收的小费也称 gratuity）——原释义颠倒概念 |
| `fender bender` | 听力-紧急意外 | 轻微追尾 | 轻微交通事故；小刮蹭（不一定是追尾）——原释义范围过窄 |
| `registrar` | 学科-校园 | 教务处 | 注册主任；教务主任——registrar 指"人/职位"，"教务处"是机构 |
| `I take your point, but` | 听力-同意反对 | 我听到了你的观点，但 | 我明白你的意思，但 / 你说得有道理，但——原文丢失"理解并认可"核心义 |
| `eye exam` | 听力-眼科配镜 | 验光 | 眼科检查；视力检查——"验光"仅测屈光度，范围过窄 |
| `flat tire` | 听力-科技汽车 | 爆胎 | 瘪胎；轮胎没气——爆胎是 blowout，范围过窄 |
| `return address` | 听力-邮局快递 | 退回地址 | 寄件人地址；回邮地址——原文易与"退货地址"混淆 |
| `tutoring session` | 听力-学业支持 | 辅导课（一对多辅导） | 辅导课；辅导时段——"一对多"属未证实的假设，收窄为中性表述 |

另复核 r=5 全量 853 条（无低价值词混入）、易混淆对、发音陷阱全量（除上述 1 条外均准确）。顺带将 58 条此前以带空格格式追加的词条统一为全库一致的紧凑 JSON 格式（内容逐字段验证不变）。

### 回归测试 82 → 96 条

新增 14 条断言锁定本轮成果：`写作-邮件`/`口语-虚拟面试` 等 6 个任务分类的存在性与宏归属、邮件/面试语块示例、薄分类宏正确性。全部 96/96 通过。

词库总量 3284 → 3301；`wordToIndex` 索引对既有词逐字不动，仅追加，进度编码完全兼容。

## 第七轮：句型占位卡 TTS 修复 + 学术功能词补齐 + 全库覆盖率复核

### 句型占位卡 TTS 修复（`patternSpeak()`）

12 条占位符句型（`Take ... for example`、`While X ..., Y ...` 等）此前点🔊会被 TTS 生硬读成 "dot dot dot"。新增 `patternSpeak()`：省略号槽位读作 `blank`（保留停顿），单字拖长 `Well...` 直接去掉省略号，`You mean ...?` 读成 `You mean blank?`，X/Y 占位字母由 TTS 自然读出。示例：

- `Take ... for example` → "Take blank, for example"
- `not only ... but also` → "not only blank, but also"
- `The first is ... the second ...` → "The first is blank, the second blank"

### 学术功能词补齐 8 条（写作/阅读论证核心）

按官方语料 + AWL 词表核对，`功能词-*` 各子类补齐缺失的论证/分析核心词（这些正是 555 分与 600+ 在阅读写作上的分水岭）：

| 词 | 分类 | 释义 |
|---|---|---|
| `claim` | 功能词-论证 | 主张；声称（学术义：提出论点）；断言 |
| `suggest` | 功能词-论证 | 表明；暗示（数据/证据 suggest...）——不同于"建议" |
| `propose` | 功能词-论证 | 提议；提出（propose that...） |
| `assumption` | 功能词-抽象名词 | 假设；前提（未经证实的假定） |
| `correlate` | 功能词-分析 | 与…相关；相互关联（correlate A with B） |
| `originate` | 功能词-因果 | 源于；起源于（originate from...） |
| `cause` | 功能词-因果 | 原因；导致（CET-4 已知词 → r=1 不进队列，仅补数据洞） |
| `peak` | 功能词-变化量 | 峰值；最高点；达到顶峰（图表描述） |

### 全库覆盖率复核（对官方语料的高频内容词）

对 `ets_official_2026/` 全量语料（约 4.2 万词）做逐词比对：**所有有意义的高频内容词均已收录**（独立或作为短语成分），仅 `woman`、`able` 两个指令/基础词未收录。同时复核 r=4/5 无基础词混入（仅 `like` 语气填充属教学必要）。词库对官方材料的覆盖面已相当完整。

### 回归测试 96 → 109 条

新增 13 条断言：句型占位卡 TTS 8 条（槽位读 blank、句尾省略号处理、X/Y 双占位、全量 11 卡可朗读）+ 学术功能词 5 条（含宏归属、cause 不进队列）。全部 109/109 通过。

词库总量 3301 → 3309；`wordToIndex` 索引对既有词逐字不动，仅追加，进度编码完全兼容。

## 第八轮：按 555 分水平的双向优先级校准（AWL 难词提权 + CET 已知词降权）

针对"只保留我可能不会的词"这一目标，做双向校准：

### 提权：AWL-1/2/3 高子表中 555 分可能不会的学术词进入队列（27 条）

此前 AWL-1/2/3（最高频学术词）整体按"高频骨架=已知"设计为 r=1 不进队列。但其中相当一部分（`constitute`、`legislate`、`negate`、`criterion`、`consequent`、`constrain` 等）是 555 分考生**并不扎实掌握**的高价值学术词——高频 + 不会 = 阅读写作必考。按难度提权：

- **r=3（7 条）**：`constitute legislate negate convene criterion consequent constrain`
- **r=2（20 条）**：`derive proceed sector administrate equate institute perceive regulate reside secure compensate consent considerable coordinate deduce scheme sequence specify evident proportion`

### 降权：CET-4/6 级必会词移出队列（27 条）

从 r=2/3/4 中找出 555 分考生**肯定掌握**的基础词降为 r=1（不进队列，权重 0.2 仅浏览可见）：`borrow discount exchange receipt reception shelf`、`colleague coupon confirm file grade schedule team`、`appointment cancel deadline deposit reserve return salary terminal withdraw`。其中 `job lecture project`（AWL-4/6）与 `team grade file schedule confirm colleague`（AWL-7/8/9/10）此前因身处 AWL 高子表而滞留队列，现与 AWL-1/2/3 的"已知骨架"处理对齐。

**保留不动**（教学价值 > 已知与否）：全部发音陷阱（如 `garage`）、功能语气标记（`Look/Now/Right/like` 的口语用法）、`prescription` 等医疗边界词。

### 回归测试 109 → 112 条

新增 3 条断言锁定：AWL 难词提权不回落、CET 已知词全分类不得高于 r=1、AWL-1/2/3 不再全是 r=1。全部 112/112 通过。

词库总量保持 3309；`wordToIndex` 索引对既有词逐字不动（仅改 r 字段，无增删），进度编码完全兼容。

## 第九轮：剩余未审查分类的释义抽查（短语动词/学术搭配/同义替换/学科深度等 700 条）

继第三/六轮之后，把此前未审查的分类全部纳入 5 个子代理并行抽查（700 条），每条约 130-150 条、单次读取：

| 切片 | 覆盖 | 结果 |
|---|---|---|
| D1（127 条） | 短语动词 87 + 学术搭配 40 | 全部正确 |
| D2（130 条） | 同义替换 + 态度词 + 填词 + 词缀派生 | `impressed` 1 处修正 |
| D3（145 条） | 学科/深度 前半 | `artifact`、`aesthetic` 2 处修正 |
| D4（145 条） | 学科/深度 后半 | 全部正确 |
| D5（153 条） | 补充高频词 + 语气动词 + 写作/功能词 | 全部正确 |

### 采纳修正 3 处（均为客观问题）

| 词 | 分类 | 原释义 | 修正 |
|---|---|---|---|
| `impressed` | 态度词-积极 | 印象深刻的 | 被打动的；深感佩服的——原译与 impressive（令人印象深刻的）混淆，主动/被动方向颠倒 |
| `artifact` | 学科-人类学 | 手工艺品 | 人工制品；文物——人类学/考古学中指任何人造物（石器、陶片、工具），"手工艺品"范围过窄 |
| `aesthetic` | 学科-艺术建筑 | 美学的 | 美学的；审美的；审美观（n.）——标签 adj/n 但缺名词义 |

另对阅读-标识告示、阅读-社交短文、口语-虚拟面试、写作-邮件、听力-理发美容逐条人工复核均准确；全库 lint（过短释义/跨分类释义冲突/乱码/词性异常）无异常。至此全库 3309 条已 100% 过审查。

词库总量保持 3309；`wordToIndex` 索引逐字不动，进度编码完全兼容。

## 第十轮：仪表盘卡片重组——技能向分类归入对应卡片（其他 277→66）

此前 25 个学习分类（含 124+ 个词）被笼统塞进「其他」卡片，用户难以定位。按 2026 各任务技能归属扩展 `getMacro()`：

- **→ 阅读**：`填词-*`（新题 Complete the words）、`词缀派生-*`（构词法）→ 阅读卡片 17→78 词
- **→ 听力**：`讲座信号词-*`、`态度词-*`、`语气动词` → 听力卡片 1954→2021 词
- **→ 写作**：`同义替换-*`（学术换词）、`学术搭配` → 写作卡片 96→179 词
- **留在「其他」**：仅剩 `补充高频词`、`易混淆对`（跨技能通用）→ 66 词

仪表盘现在按技能归位，浏览/学习流自动按新分组生效（`browseGroups`/`renderBrowse` 均为通用逻辑）。**数据零改动**——仅改 `getMacro` 映射函数，词条、索引、进度编码均不变。

### 回归测试 112 → 117 条

新增 5 条断言锁定新映射（填词/词缀→阅读、信号词/态度词/语气动词→听力、同义替换/学术搭配→写作、补充高频词/易混淆对→其他）。全部 117/117 通过。另实测 GitHub Pages 线上部署已是最新版（3309 词 + patternSpeak 均在线）。

## 第十一轮：排序一致性修复（词表/一览按优先级降序）+ 学习流复核

发现并修复一个 UX 不一致：**学习队列**按权重把 r=5 排最前（最高优先级先学），但**词表「默认（优先级）」排序却是升序（r=1 已知词在前）**，一览组内也按数据插入序。修复：

- 词表「优先级」排序 → 降序（r=5 在前、r=1 已知词在后），与学习队列一致
- 词表「按分类」排序的组内 tie-break → 同分类内高优先级在前
- 一览各子场景组内 → 按 r 降序排列（r=5 词在前，点击进入也从高优先级开始）

**数据零改动**——仅改排序逻辑。另复核 SRS 记忆曲线（`isDue`/`answer`/`INTERVALS` 1/3/7 天）、复习计数、学习小结、跨页 gist 同步均正常，无其它问题。

### 回归测试 117 → 121 条

新增 4 条断言：优先级排序 r=5 在前且单调不升、错误率排序首位最高、一览组内高优先级在前。全部 121/121 通过。线上部署已确认为最新。

## 第十二轮：可持续环保主题词补齐（语料实证 +6，3309→3315）

复查官方语料（7 套真题 4.2 万词）时发现「ecological footprint（生态足迹）」出现 16 次——正是真题阅读材料直接讨论的概念，但词库完全没有。据此为 **听力-可持续环保** 补齐 6 个真题高频、555 分水平可能不熟的可持续主题词：

| 词 | 词性 | 释义 | 优先级 |
|---|---|---|---|
| ecological footprint | n | 生态足迹（衡量资源消耗对环境的影响） | r=4 |
| emissions | n | 排放（物）（carbon emissions 碳排放） | r=3 |
| carbon emissions | n | 碳排放 | r=3 |
| greenhouse gas | n | 温室气体 | r=3 |
| environmental impact | n | 环境影响 | r=3 |
| recyclable | adj | 可回收的；可循环利用的 | r=3 |

分类 7 → 13 词。仅**尾部追加**（索引逐字不动，进度兼容）；未引入任何已知词（pollution/climate change 等 555 水平已知的基础词不收入）。

另复核 2026「听力-选择回复」六类即时应答训练（72 条：反问确认/疑问词匹配/请求许可/建议安排/问题求助/信息核对）质量高、语块教学注记完整，无缺项。

### 回归测试 121 → 124 条

新增 3 条断言（可持续词已补齐、分类≥12 条、生态足迹高优先级）。全部 124/124 通过。词库 3315 词。

## 第十三轮：跨学科语料概念词补齐 +4（3315→3319）

继续做语料实证找缺口（bigram/专题概念扫描，过滤考试指令语），再补 4 个真题材料实际出现、555 分水平可能不熟的学术概念词：

| 词 | 词性 | 释义 | 分类 | 优先级 |
|---|---|---|---|---|
| language acquisition | n | 语言习得（语言学讲座核心概念） | 深度-认知语言 | r=4 |
| genetics | n | 遗传学 | 学科-生物 | r=4 |
| pottery | n | 陶器（考古/工艺品的常见出土物） | 学科-历史考古 | r=4 |
| livestock farming | n | 畜牧业（温室气体排放的重要来源） | 听力-可持续环保 | r=3 |

前两词均有真题语料命中（language acquisition 10 次——语言学讲座主题；genetics 2 次——生物因素），后两词来自真题考古/可持续材料。**仅尾部追加**，索引/进度兼容；已核对的已知词（marketing/architecture/emotion/agriculture 等 555 已掌握者）不收入。学科主题覆盖面复查：生物/生态/考古/经济/艺术/心理学等 40+ 概念词抽查基本全覆盖。

### 回归测试 124 → 129 条

新增 5 条断言（4 词补齐 + 各归位分类正确）。全部 129/129 通过。词库 3319 词。

## 第十四轮：AWL 词表完整性校验——补全 5 个缺失头词（3319→3324）

对照官方 Academic Word List（eapfoundation 全量 570 头词表）逐子表比对，发现词库 AWL 部分有 5 个头词缺失（部分仅有相关形式）：

| 缺失头词 | 词性 | 释义 | 子表 | 优先级 |
|---|---|---|---|---|
| sex | n | 性别；性（学术语境常与 gender 区分） | AWL-3 | r=1 |
| ignorant | adj | 无知的；（be ignorant of 对…一无所知） | AWL-6 | r=2 |
| intelligent | adj | 聪明的；智能的 | AWL-6 | r=2 |
| globe | n | 地球；球体；地球仪 | AWL-7 | r=3 |
| append | v | 附加；添加（append to 附在…后） | AWL-8 | r=3 |

词库原有 `ignorance/intelligence/global/appendix`（相关形式）但缺头词本身；现家族齐全。**仅尾部追加**，索引/进度兼容。至此 **AWL 全部 570 头词 100% 覆盖**（含相关形式共 574 条）。

### 回归测试 129 → 134 条

新增 5 条断言（各子表头词齐全 + 头词分位正确 + AWL 总数≥570）。全部 134/134 通过。词库 3324 词。

## 第十五轮：邮件正式连接词 + 易混淆对扩充 +11（3324→3335）

复核 2026「写邮件」与「虚拟面试」两大新题分类（口语-虚拟面试 18 条、写作-邮件 23 条均质量高、语块注记完整）。补：

- **写作-邮件** +1：`regarding`（关于；正式书面连接词，语料 3 次命中）r=5
- **易混淆对** +10（5 对经典形近/义近易混词，均含「≠」对照标注，555 水平常见混淆点）：

  moral 道德 ≠ morale 士气；historic 有历史意义 ≠ historical 历史；continual 频繁 ≠ continuous 连续；
  council 委员会 ≠ counsel 律师；economic 经济 ≠ economical 节俭

均为**尾部追加**，索引/进度兼容；已核实基础易混对（fewer/less、farther/further 等）用户已掌握不收入。

### 回归测试 134 → 137 条

新增 3 条断言（regarding 归位、易混词补齐、均含对照标注）。全部 137/137 通过。词库 3335 词。

## 第十六轮：学术连接词补齐 +3（3335→3338）

复查「Complete the words」阅读新题与写作功能词覆盖，发现 3 个经典学术连接词/短语缺失，按功能归位（均 r=5，与所在分类一致）：

| 词 | 词性 | 释义 | 分类 |
|---|---|---|---|
| thus | adv | 因此；如此（正式书面语，表因果） | 填词-转折连接 |
| namely | adv | 即；也就是（用于具体说明/举例） | 写作精准-举例 |
| in conclusion | phr | 总之；综上所述（总结段开头） | 写作精准-总结 |

其余学术连接词已确认覆盖（consequently/furthermore/nonetheless/whereas/despite/hence/for instance 等均在库）。**仅尾部追加**，索引/进度兼容。

### 回归测试 137 → 141 条

新增 4 条断言（三词归位 + 高优先级）。全部 141/141 通过。词库 3338 词。

## 第十七轮：校园习语补齐 +6（3338→3344）

复查三个听力习语分类（听力-习语 30 + 习语2 15 + 习语补充 23，共 68 条均质量高、r=5），发现 6 个高频校园场景习语缺失，补入 听力-习语补充：

- pull an all-nighter 熬夜赶工（通宵赶作业）
- a lot on my plate 手头有很多事要忙
- brush up on 复习；温习提高
- get the most out of 充分利用（机会/时间）
- cut it close 勉强赶上；时间很紧
- burn the midnight oil 开夜车；熬夜工作学习

已核实 catch up 在 短语动词 已覆盖故不重复收入。**仅尾部追加**，索引/进度兼容。

### 回归测试 141 → 144 条

新增 3 条断言（习语补齐 + 高优先级 + 分类≥29）。全部 144/144 通过。词库 3344 词。

## 第十八轮：仪表盘新增「重点词进度（P4+P5）」

学习卡片按优先级 r 分档（P1-P5），P4+P5 正是 2026 备考的核心目标词（可能是你不会的）。仪表盘原来只显示总体掌握进度，无法一眼看出核心目标还剩多少。本轮在 `renderDashboard()` 增加第二行进度条：

- **重点词进度（P4+P5）**：已掌握 / 总数 · 百分比（橙色 warn 色）
- 直接对应备考核心：剩余未掌握的 P4+P5 即最该攻克的词

**数据零改动**——仅页面渲染增强。复用现有 `.progress-wrap/.label/.bar` 样式，无 CSS 改动。回归测试 144 → 146 条全绿（含仪表盘重点词进度断言）。

## 第十九轮：即时应答训练专用入口（2026 听力 70% 题型的练习路径）

复查发现：Listen and Choose a Response 是官方听力**占比最大的题型（112/161 题，70%）**，其 72 条训练卡（听力-应答-* 六类）全部为 r=1——这是有意为之（训练句不含生僻词，考的是应答模式而非生词），但也意味着这些模式在普通队列里几乎抽不到，用户没有便捷练习入口。

本轮新增**专用训练入口**：

- 仪表盘新增「🎯 即时应答训练 · 72 个模式」按钮（accent 色）
- `buildSession` 支持 `mode='train'`：**全量抽取**（含已掌握的），每轮最多 30 条，覆盖 2026 听力最大题型
- `startResponseTraining()` 进入学习视图；「再来一轮」可反复练习全部模式
- `train-count` 显示应答训练条目数

**数据零改动**——仅页面功能。回归测试 146 → 151 条全绿（新增：仪表盘按钮存在、计数=应答条目数、训练队列全为应答句且含已掌握词、train 模式可抽取）。修复一处类型问题（textContent 需字符串）。
