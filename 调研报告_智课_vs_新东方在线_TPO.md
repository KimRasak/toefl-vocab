# 智课(smartstudy) vs 新东方在线(koolearn) 托福 TPO 在线练习调研

调研日期：2026-08-31（所有 curl 抓取均在当日完成，服务器返回 `date: Mon, 31 Aug 2026`）

---

## 一、新东方在线（koolearn）

平台现状：**正常运营，且已完成 2026 改版适配**。托福业务主站已从旧版 `toefl.koolearn.com`
迁移/并行到新版 `liuxue.koolearn.com/toefl/`（Next.js SSR，可直接抓到正文）。

### 1. TPO/Official 收录到第几套 + 是否运营

| 板块 | 收录范围 | 来源 |
|---|---|---|
| 旧题型 Official（=TPO）分项练习 | **Official 30 - 58**（筛选器分组：Official 58-51 / 50-41 / 40-31 / 30），最高 **58** | [阅读](https://liuxue.koolearn.com/toefl/read/) / [听力](https://liuxue.koolearn.com/toefl/listen/) / [口语](https://liuxue.koolearn.com/toefl/speak/) / [写作](https://liuxue.koolearn.com/toefl/write/) |
| 26 改革新题练习 | 按**题型**组织，不再按 TPO 套数编号 | [题库](https://liuxue.koolearn.com/toefl/new/read/) |
| 付费"TPO 官方在线练习题" | 页面在售、标价 ¥299/套，**但未登录时商品列表为空** | [tpoModeTest](https://liuxue.koolearn.com/toefl/tpoModeTest/) |

- 旧题型页明确标注："以下为2026年1月托福改革前的阅读题型……题型设置、题目数量与答题时间均与改革后存在差异"。
- 旧的"TPO30-58 免费刷题"短链（`l.koolearn.com/L08G1OF`、`hBGSjrS`、`VrIYtHr`、`MsMbKbe`）
  现分别 302 到 `/toefl/read/ /listen/ /speak/ /write/`，仍然有效。
- `https://liuxue.koolearn.com/toefl/tpo/` 返回 HTTP 200 但 `__NEXT_DATA__` 内为
  `{"code":404,"text":"找不到页面啦"}`；`https://toefl.koolearn.com/tpo/`、`https://tpo.koolearn.com/`
  均 404 —— 新平台已无 TPO 编号入口。
- 二手说法（非官方口径）：新东方在线 2025-08-04 文章称"官方 TPO 已更新至 **75 套**"
  （[m.koolearn.com/toefl/20250804/860010.html](https://m.koolearn.com/toefl/20250804/860010.html)）；
  2023-12-20 文章称"TPO 已更新到第 **74** 套"，并称"新东方在线免费提供 TPO30-58 全部试题"
  （[toefl.koolearn.com/20231220/857833.html](https://toefl.koolearn.com/20231220/857833.html)）。

### 2. 免费 / 付费

- **免费**：Official 30-58 四科分项练习 + 题目详解页（题目、选项、**正确答案**、音频、原文/译文/精听文本）可未登录直接查看。
- **VIP**：官方口径"升级为新东方托福VIP，您还可解锁每道题目的**专业解析与教师范例答案**"
  （[860925](https://m.koolearn.com/toefl/20251225/860925.html)）。VIP 具体价格未在公开页面找到。
- **TPO 官方在线练习题：¥299 / 套**（[tpoModeTest](https://liuxue.koolearn.com/toefl/tpoModeTest/)）。
- **新题型口语 AI 评分券：¥59.00/次；¥212.00/4次（9折）**
  （[/toefl/speak/newScore/buy/](https://liuxue.koolearn.com/toefl/speak/newScore/buy/)）。
- **人工批改**（读取产品页 `__NEXT_DATA__` 得到价格）：
  - 托福口语精批1次（**面试题**）= **¥99**，1课时，有效期30天，3-5个工作日出结果
    （[c_7_246481](https://www.koolearn.com/liuxue/product/c_7_246481/)）
  - 托福写作批改服务包-自选1篇 = **¥99**，批改范围"**邮件**或者**学术讨论**题"，3-5个工作日
    （[c_7_246484](https://www.koolearn.com/liuxue/product/c_7_246484/)）
- 新东方托福Pro APP：App Store 标注"**免费 · App 内购买**"，唯一公开内购项为"8K币 ¥8.00"
  （[App Store id1470941866](https://apps.apple.com/cn/app/id1470941866)）。

### 3. 听力音频 + 原文 + 题目 + 答案解析 / 口语写作批改

实测未登录抓取 [Official 55 Con 1 详解页](https://liuxue.koolearn.com/toefl/listen/1125-11111-q0.html)：
- 页面标题即"托福TPO/Official 55 Con 1听力原答案解析-音频翻译"
- 含 5 道题干 + 四选项 + "正确答案：B"
- 含 mp3 直链（`daxue-cos.koocdn.com/upload/ti/sardine/.../*.mp3`，含整篇音频与逐句音频）
- 含"隐藏原文 / 译文 / 精听文本"三个页签 → **音频 + 原文 + 译文 + 逐句精听**齐全
- 听力列表每篇均有"精听"按钮；口语/写作列表每题有"范例"
- **逐题文字解析**属于 VIP 权益（见上）
- 口语/写作**人工批改**：各 ¥99（见上）；新题型口语另有 AI 评分券

### 4. 2026-01-21 改版新题型模考

**已上线，且题型覆盖 ETS 官方 12 种任务全部对应**。

koolearn 自述题型（[/toefl/new/read/](https://liuxue.koolearn.com/toefl/new/read/)、
[首页](https://toefl.koolearn.com/)）与
[ETS 官方 content.html](https://www.ets.org/toefl/test-takers/ibt/about/content.html) 对照：

| ETS 官方任务名 | koolearn 中文题型 |
|---|---|
| Complete the Words | 阅读填空 |
| Read in Daily Life | 日常生活阅读 |
| Read an Academic Passage | 学术阅读 |
| Listen and Choose a Response | 听答 |
| Listen to a Conversation | 对话 |
| Listen to an Announcement | 公告 |
| Listen to an Academic Talk | 学术讲座 |
| Build a Sentence | 造句 |
| Write an Email | 邮件 |
| Write for an Academic Discussion | 学术讨论 |
| Listen and Repeat | 听与复述 |
| Take an Interview | 虚拟面试 |

（注：用户提到的"Read and Complete"，ETS 官网当前写法是 **Complete the Words**；
"Listen and Speak"对应 ETS 的 **Listen and Repeat**。）

其他证据：
- [模考页](https://liuxue.koolearn.com/toefl/mock/)："26年改革新题模考练习……阅读与听力适配自适应算法，
  模拟动态难度切换。口语与写作涵盖所有题型，配合 AI 即时评分。"
- 首页"26年改革新题练习 / 全科机考 / 一键获取机考评分 / 进入机考"
- 新东方托福Pro APP 版本历史：**4.4.0（2026-02-13）"26改革新题上线"**；
  **4.5.1（2026-07-29）"支持26改革新题听说读写全科全题型练习"**
- 付费 TPO 页标注"**已更新为改革新题**"（`__NEXT_DATA__` 中 `"tpo":"已更新为改革新题"`）
- 新题型口语评分券页："解锁'听与复述'及'虚拟面试'新题型诊断报告"

**未能核实**：改革新题模考具体有几套。模考列表接口
`/chuguoapi/toefl/mockTest/reform26/study/mock/list` 需签名，未登录返回
`{"message":"time check error","status":602}`；新题练习列表未登录显示"共 0 小题 / 立即登录"。

### 5. ETS 官方授权 / 合作证据（较强）

- App Store 应用名直接叫"**新东方托福Pro-ETS官方合作伙伴**"，开发者"北京新东方彼岸科技有限公司"
  （[链接](https://apps.apple.com/cn/app/id1470941866)）
- 2025-12-25 官方文章：2025-12-18 ETS 在广州举办中国合作伙伴大会，新东方在线获
  **2025-2026 年度托福全球合作伙伴"钻石伙伴"（最高级）**，**连续第七年**；文中同时称
  "作为 ETS 官方授权合作伙伴，我们提供正版题库"、"现已开放 ETS 官方研发的 TPO 真题练习"
  （[860925](https://m.koolearn.com/toefl/20251225/860925.html)）
- 官网页脚："新东方官方网校 21 年专业学习平台，**ETS官方合作伙伴**"（[toefl.koolearn.com](https://toefl.koolearn.com/)）
- 付费 TPO 页："**ETS中国大陆地区官方授权**，托福官方推荐在线练习题"，口语 SpeechRater、写作 E-rater
  24h 内返回成绩（[tpoModeTest](https://liuxue.koolearn.com/toefl/tpoModeTest/)）

> 说明：以上"授权/钻石伙伴"均为新东方在线自述 + App Store 应用名，我**未在 ETS 官网找到**
> 列出合作机构名单的公开页面来交叉验证。

---

## 二、智课（smartstudy / 智课网 / 智课教育）

结论：**官网域名当前不可访问，托福 TPO 模考产品已无法确认在运营；App Store 中国区已无智课托福类 App。**

### 1. 收录套数 + 是否运营

- **域名解析正常但服务不可达**：`smartstudy.com` / `www.smartstudy.com` / `toefl.smartstudy.com`
  DNS 均解析到 `47.94.107.3`（阿里云），但 80 / 443 端口 **TCP 连接超时**（Python socket 直连
  与 `curl` 均超时，`curl` 退出码 28，HTTP code `000`）。同一环境下
  `toefl.koolearn.com:443`、`www.baidu.com:443` 正常 → 不是本地网络问题。
- 第三方代理二次确认：`https://api.codetabs.com/v1/proxy?quest=https://www.smartstudy.com/`
  返回 **522（Cloudflare 连接源站超时）**。
- Wayback Machine：`www.smartstudy.com` 最后一次 200 快照为 **2025-12-09**
  （[快照](http://web.archive.org/web/20251209084022/https://www.smartstudy.com/)），
  **2026 年整年 0 条快照**（`cdx?from=2026` 返回空）。`toefl.smartstudy.com` 在 Wayback 中
  **从无任何存档记录**（域名级 CDX 共 91,102 条记录里没有该子域）。
- 2025-09-08 的存档 API 仍返回"智课网SmartStudy.com - 同样的时间,更高的分数"
  （[archived /api/seo](http://web.archive.org/web/20250908094627if_/https://www.smartstudy.com/api/seo?type=1&filter=%2Fwww.smartstudy.com%2F)）
  → 站点在 2025 年 9 月还活着，之后失联。
- 线下主体已停运：多知网 2025-06-11 报道"**上海智课出国一站式规划中心**停运，新航道国际教育
  已无偿接收在读学员全部剩余课时"，原因"外部环境和内部经营问题"
  （[duozhi.com](http://www.duozhi.com/industry/overseas/2025061117361.shtml)）。
- 桌面端"智课托福TPO模考软件"只在第三方下载站有镜像：华军软件园版本 **1.0.3**，91.05MB，
  安装包名 `SmartTOEFL-1.0.3.zip`，页面"更新时间 2024-12-26"，但同页"TPO模考软件大全"专题里
  该软件的**更新日期为 2016-07-21**，下载次数 0
  （[onlinedown.net/soft/580447.htm](https://www.onlinedown.net/soft/580447.htm)）。
  另有天极/最需网等镜像标"1.0 官方正式版"
  （[mydown.yesky.com](https://mydown.yesky.com/pcsoft/103242184/versions/)、
  [m.zuixu.com](https://m.zuixu.com/down/324261.html)）。
- App Store 中国区：`itunes.apple.com/search` 以「智课」「智课斩托福」「智课网」「smartstudy」
  四组关键词检索 `entity=software&country=cn`，**结果中没有任何智课/SmartStudy 托福 App**
  （同一接口能正常返回"新东方托福Pro 4.5.1 / 2026-07-29"、"小站托福TPO"、"托福考满分"等）。

**→ TPO 收录到第几套：不确定 / 未找到公开信息。** 官网不可达，第三方下载站的介绍文案里
只有"全网最全的模考题目"这种宣传语，**没有任何套数数字**；Wayback 里 2020 年后的
smartstudy.com 页面全是 SPA 空壳（`umi` 单页应用，静态资源托管在 `static.uskid.com`），
抓不到题库清单。

### 2. 免费 / 付费

- 第三方下载站把 PC 版"智课托福TPO模考软件"标为"**免费软件**"（[onlinedown](https://www.onlinedown.net/soft/580447.htm)）。
- 智课网课程/会员的价格：**不确定**，官网与商城均不可达，无法核实。

### 3. 功能（听力音频/原文/答案解析/批改）

只能引用第三方下载站转载的**厂商宣传文案**（无法实机验证）：
"1:1还原TOEFL考试场景；即时出分的模考软件，写作和口语同步ETS算法打分；试题详细报告和解析；
全网最全的模考题目；支持离线使用；全面适配 Windows/Mac OS"
（[onlinedown](https://www.onlinedown.net/soft/580447.htm)）。

- 是否含听力原文/逐题解析：宣传语提到"试题详细报告和解析"，但**未能验证**。
- 口语/写作批改：宣传语称"写作和口语同步ETS算法打分"；Wayback 存档的旧导航里有
  "外教批改"栏目（[2019 存档](http://web.archive.org/web/20191022094344/https://www.smartstudy.com/mk)），
  **当前是否可用：不确定**。

### 4. 2026 改版新题型模考

**无任何证据，基本可判定没有。** 该软件公开可见的最新版本号是 1.0.3（镜像站标注 2016 / 2024），
官网自 2025-12 后无快照、当前不可达，App Store 无对应 App，也未找到任何智课发布
"26 改革新题/新托福 1-6 分制"模考的公开说明。

### 5. ETS 官方授权 / 合作声明

**未找到任何智课的 ETS 官方授权或官方合作声明。**
第三方下载页仅有"写作和口语同步 ETS 算法打分"这类技术描述，**不构成授权声明**。
Wayback 存档的智课旧导航中虽有"授权合作"栏目，但为 SPA 空壳，抓不到内容。

---

## 三、尝试过但失败/受限的 URL 记录

| URL | 结果 |
|---|---|
| `http://toefl.smartstudy.com/` | curl code=000，连接超时（DNS→47.94.107.3，80/443 不响应） |
| `https://www.smartstudy.com/` `https://smartstudy.com/` | 同上，TCP 超时；第三方代理返回 522 |
| `http://smartpigai.com/smartstudy_innobuddy/questionbankinfo/` | curl code=000，连接超时 |
| `http://web.archive.org/cdx/...url=www.smartstudy.com&from=2026` | 返回空（2026 年无快照） |
| `http://web.archive.org/cdx/...url=toefl.smartstudy.com*` | 返回空（该子域无存档） |
| `https://liuxue.koolearn.com/toefl/tpo/` | HTTP 200 外壳 + 内部 404「找不到页面啦」 |
| `https://toefl.koolearn.com/tpo/`、`https://tpo.koolearn.com/`、`https://toefl.koolearn.com/mklist/` | 404 |
| `https://liuxue.koolearn.com/toefl/tpoModeTest/` | 200，但 SSR `productList` 为 `{"tpoNum":"","list":[]}`（未登录看不到在售套题） |
| `https://liuxue.koolearn.com/chuguoapi/toefl/mockTest/reform26/study/mock/list` | `{"message":"time check error","status":602}`（需签名/登录） |
| `https://liuxue.koolearn.com/toefl/new/read/` | 200，但未登录显示「共 0 小题 / 立即登录」 |
| `https://www.koolearn.com/liuxue/product/c_7_246481/` 等 | HTML 无价格，价格在 `__NEXT_DATA__` 里（已提取） |
| `https://www.ets.org/toefl/test-takers/ibt/scores/understand.html` | 404（改用 content.html 取到官方题型表） |
| `https://r.jina.ai/...`、`https://www.so.com/s?...` | 空响应 / 验证码拦截 |
| `web_search` 工具 | 后半程返回 `Insufficient Balance`，改用 Baidu + 直接 curl |
