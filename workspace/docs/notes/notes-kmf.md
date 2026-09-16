# 考满分 / 学而思国际（toefl.kmf.com）实测记录 — 2026-08-31

## 站点现状
- 首页 title 已改为「【TOEFL 托福】在线直播课…学而思国际（原考满分）」，主站 SPA 在 `/n/*`。
  https://toefl.kmf.com/
- 老版单项练习页仍在：`/practice/listening`、`/practice/reading`、`/practice/speaking`（`/practice/writing` 也在）。
  `/practice/listen`（用户给的 URL）返回 404。

## 老版「官方真题 Official」= TPO 1–54（收录上限 54）
- 听力：https://toefl.kmf.com/listen/ets/new-order/1/0 → 标题「Official 54-51 全部听力真题」；页内筛选分组为
  Official 54-51 / 50-46 / 45-41 / 40-36 / 35-31 / 30-26 / 25-21 / 20-16 / 15-11 / 10-6 / 5-1；「顺序练习 包含 Official 1-54」。
  分页 `/listen/ets/new-order/N/0`：N=1..11 有效，N=12 返回 500/404 → 上限确认为 54。
- 阅读：https://toefl.kmf.com/read/ets/new-order/1/0 → 同样「包含 Official 1-54」。
- 口语：https://toefl.kmf.com/speak/ets/new-order/1/0 → 「Official 54-51」。
- 写作 `/write/ets/new-order/1/0` → 404。
- 页面原话：「官方授权改革版：Official27~30，Official41~54 为 ETS 官方授权提供的改革后真题材料」
  「官方真题，由ETS授权考满分（学而思托福）使用」。
- 页面另注：「ETS于2023年7月26号再次进行托福改革，如需体验2023年后改革版阅读真题, 请前往考满分新模考练习」。

## 新版（2026 改版）模考体系
- 首页导航：「全真自适应模考 / 海量新题」+「TPO官方套题 / 学而思×ETS，官方真考」。
- 老练习页横幅：「学而思独家自研新题库，全面匹配托福26年改革」，并列出新题型：
  阅读=填词题、日常生活读、学术文章阅读；听力=听答题、听短对话、听公告、听学术讲座；
  写作=造句子、写邮件、学术讨论；口语=复读题、模拟面试。
- API（无需登录）`https://api.kmf.com/toefl-app/practice/condition` 返回新题型枚举：
  27 阅读：填词题 GapFilling / 日常生活 DailyLife / 学术文章 AcademicArticle
  28 听力：听答题 SingleChoice / 短对话 ShortConversation / 学术公告 AcademicNotice / 学术讲座 AcademicLecture
  29 口语：复述题 Repeat / 模拟面试 Interview
  30 写作：造句题 Sentence / 写邮件 Email / 学术讨论 Academic
  `daily_all_nums.current_all_num = 11557`（题库总量），`incr_num = 2247`。
- API `https://api.kmf.com/toefl-app/mock/2026/home` 返回自适应模考配置：
  规则=自适应 / 固定难度-Lower / 固定难度-Upper；单阶段练习 Stage1 / Stage2 Lower / Stage2 Upper；
  加试=随机加试 / 固定加试-阅读学术文章 / 固定加试-阅读日常生活。→ 已完整适配 2026 自适应两阶段结构。

## TPO 官方套题数量（新体系）
- API `https://api.kmf.com/toefl-app/tpo/list`（无需登录）→ `total: 6`，titles = TPO1…TPO6。
  加 page / page_size / size / limit / per_page / type / source 参数结果不变，仍为 6 套。
- 每套含 settings.read_stage1_sec / read_stage2_lower_sec / read_stage2_upper_sec（两阶段自适应字段），
  subject_scores 的 avg_score 为 4~5（1–6 分制）→ 判定为新版（2026 格式）套题，编号从 1 重新起算。

## 价格（API 实测，2026-08-31）
- TPO 解锁 `https://api.kmf.com/toefl-app/tpo/shop-config`：
  解锁 1 套 ¥188 / 解锁 3 套 ¥399 / 解锁 6 套 ¥699（has_discount: true）。
- 会员 `https://api.kmf.com/toefl-app/vip/config`：
  7 日 ¥39（口语批改10次/写作10次/模考10次）；30 日 ¥69（18/18/40）；
  90 日 ¥129（50/50/80）；180 日 ¥199（96/96/模考不限）。

## App Store（iOS）
- 「托福考满分-ETS官方合作TOEFL正版真题」https://apps.apple.com/cn/app/id898568936
  免费+App内购；5.1.7/5.1.8（2026-07）更新日志：「【新托福全面适配】目标分数升级6分制，新老版本自由切换；
  【首页焕新】TPO真题、自适应模考、词汇背记一键触达；【权益升级】独家口写机评」。
  简介：「6分制评分体系已正式上线」「上万道新托福真题，每日更新，12大题型全覆盖」
  「90天会员再加TPO官方套题」。
