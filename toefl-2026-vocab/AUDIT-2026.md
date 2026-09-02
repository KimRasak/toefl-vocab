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

## 依据

- [ETS 2026 TOEFL iBT Test Specifications](https://www.ets.org/content/dam/ets-org/pdfs/toefl/toefl-ibt-test-specifications-2026.pdf)
- [ETS China Test Content and Structure](https://www.cn.ets.org/toefl/china/toefl/content-structure.html)
- 本地研究：`../TPO调研-2026-08-31.md`、`../ets_official_2026/README.md`
