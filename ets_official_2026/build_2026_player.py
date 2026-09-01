#!/usr/bin/env python3
"""构建 2026 新格式听力练习页（单文件，数据内嵌）。

数据来源：
  listening_2026.json          -> 7 套 ETS 官方对版练习卷的听力部分（161 个音频条目 / 238 题）
  ../listening-2026/audio/     -> extract_audio.py 摊平出来的音频
  ../listening-2026/audio_map.json -> "zip::内部路径" -> 摊平文件名
  audio_len.py                 -> 不依赖 ffmpeg 的时长读取

要紧的口径：这 7 套是 ETS 自制的**对版练习卷**（PDF 原文 "This practice test aligns with
TOEFL iBT tests from January 21, 2026"），不是退役真题。页面上必须写清楚，别让人误以为是真题。

用法: python3 build_2026_player.py
输出: ../listening-2026/index.html
"""
import json
import os
import re
from collections import Counter, defaultdict

import audio_len

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "listening-2026")
SRC = os.path.join(HERE, "listening_2026.json")
AMAP = os.path.join(SITE, "audio_map.json")
AUDIO_DIR = os.path.join(SITE, "audio")
OUT = os.path.join(SITE, "index.html")

TEST_META = {
    "toefl-ibt-full-length-practice-test-1": ("s1", "学生卷 1"),
    "toefl-ibt-full-length-practice-test-2": ("s2", "学生卷 2"),
    "toefl-ibt-teachers-resources-practice-test-1": ("t1", "教师卷 1"),
    "toefl-ibt-teachers-resources-practice-test-2": ("t2", "教师卷 2"),
    "toefl-ibt-teachers-resources-practice-test-3": ("t3", "教师卷 3"),
    "toefl-ibt-teachers-resources-practice-test-4": ("t4", "教师卷 4"),
    "toefl-ibt-teachers-resources-practice-test-5": ("t5", "教师卷 5"),
}
KINDS = [
    ("choose_response", "cr", "听答题", "听一句话，从四个选项里选出最合适的回应。新格式独有题型，占比最大。"),
    ("conversation", "cv", "对话", "听一段日常对话，回答 2 道题。比旧格式的校园对话短得多。"),
    ("announcement", "an", "公告", "听一段校园/课堂公告，回答 2 道题。新格式新增题型。"),
    ("academic_talk", "at", "学术讲座", "听一段学术讲座或播客，回答 3–4 道题。比旧格式讲座短得多。"),
]
KIND_CODE = {k: c for k, c, _, _ in KINDS}
KIND_NAME = {c: n for _, c, n, _ in KINDS}

data = json.load(open(SRC, encoding="utf-8"))
amap = json.load(open(AMAP, encoding="utf-8"))

dur_cache = {}


def dur_of(fname):
    if fname not in dur_cache:
        sec, how = audio_len.duration(os.path.join(AUDIO_DIR, fname))
        dur_cache[fname] = (round(sec, 2) if sec else None, how)
    return dur_cache[fname]


items = []
seq = defaultdict(int)
missing_audio = []
for t in data["tests"]:
    tcode, tlabel = TEST_META[t["test"]]
    for m in t["modules"]:
        mod = m["module"]
        for it in m["items"]:
            kc = KIND_CODE[it["kind"]]
            seq[(tcode, mod, kc)] += 1
            iid = f"{tcode}_m{mod}_{kc}{seq[(tcode, mod, kc)]:02d}"
            au = amap.get(it.get("audio") or "")
            aud = amap.get(it.get("audio_directions") or "")
            if not au:
                missing_audio.append(iid)
            sec, how = dur_of(au) if au else (None, "fail")
            if it["kind"] == "choose_response":
                qs = [{"n": it["number"], "q": None,
                       "o": it["options"], "a": it["answer"]}]
                tr = [it["prompt"]]
                dirs = "听一句话，选出最合适的回应"
            else:
                qs = [{"n": q["number"], "q": q["question"],
                       "o": q["options"], "a": q["answer"]} for q in it["questions"]]
                tr = it["transcript"]
                dirs = it["prompt"]
            items.append({
                "id": iid, "t": tcode, "m": mod, "k": kc,
                "dr": dirs, "tr": tr, "qs": qs,
                "au": au, "ad": aud, "d": sec, "de": 1 if how == "estimate" else 0,
            })

nq = sum(len(x["qs"]) for x in items)
kcnt = Counter(x["k"] for x in items)
qcnt = Counter()
for x in items:
    qcnt[x["k"]] += len(x["qs"])
print(f"条目 {len(items)} 个 / 题目 {nq} 道")
for _, c, name, _ in KINDS:
    secs = [x["d"] for x in items if x["k"] == c and x["d"]]
    avg = sum(secs) / len(secs) if secs else 0
    print(f"  {name:<6} {kcnt[c]:>3} 条 / {qcnt[c]:>3} 题   平均音频 {avg:>6.1f} s"
          f"   区间 {min(secs):.1f}–{max(secs):.1f} s")
print(f"  音频总时长 {sum(x['d'] for x in items if x['d']) / 60:.1f} 分钟（不含 directions）")
if missing_audio:
    print(f"  !! 缺音频 {len(missing_audio)} 条: {missing_audio[:5]}")
ans = Counter(q["a"] for x in items for q in x["qs"])
print(f"  答案分布 {dict(sorted(ans.items()))}")
assert nq == 238, f"题目数应为 238，实际 {nq}"

payload = {
    "items": items,
    "kinds": [{"c": c, "n": n, "h": h} for _, c, n, h in KINDS],
    "tests": [{"c": TEST_META[t["test"]][0], "n": TEST_META[t["test"]][1]} for t in data["tests"]],
    "meta": {"nq": nq, "src": data["_meta"]["notice"]},
}
data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026 新格式听力练习 · 官方对版卷</title>
<style>
:root{--bg:#f5f6f8;--panel:#fff;--accent:#2f6fed;--accent-dark:#1d4fc4;--text:#1a1d24;
  --muted:#6b7280;--border:#e3e6eb;--ok:#16a34a;--bad:#dc2626;--warn:#d97706;--hl:#fff5d6}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
header{background:var(--panel);border-bottom:1px solid var(--border);padding:10px 16px;
  display:flex;align-items:center;gap:9px;flex-wrap:wrap;z-index:10}
header h1{font-size:16px;font-weight:700;white-space:nowrap}
header h1 small{font-size:12px;color:var(--muted);font-weight:400;margin-left:6px}
.sp{margin-left:auto}
select,button,input{font-size:13px;padding:6px 10px;border:1px solid var(--border);
  border-radius:8px;background:#fff;color:var(--text);outline:none}
select:focus{border-color:var(--accent)}
.btn{background:var(--accent);color:#fff;border-color:var(--accent);cursor:pointer}
.btn:hover{background:var(--accent-dark)}
.btn:disabled{background:#9db8ee;border-color:#9db8ee;cursor:default}
.btn.ghost{background:#fff;color:var(--text);border-color:var(--border);cursor:pointer}
.btn.ghost:hover{background:#f0f2f6}
#tabs{display:flex;gap:0;background:var(--panel);border-bottom:1px solid var(--border);padding:0 16px}
#tabs button{border:none;border-bottom:2px solid transparent;border-radius:0;padding:9px 14px;
  font-size:13.5px;color:var(--muted);cursor:pointer;background:none}
#tabs button.on{color:var(--accent);border-bottom-color:var(--accent);font-weight:700}
#tabs button b{font-weight:700}
main{flex:1;display:flex;min-height:0}
#list{width:250px;min-width:200px;background:var(--panel);border-right:1px solid var(--border);
  overflow-y:auto;padding:8px}
.grp{font-size:11px;color:var(--muted);padding:8px 6px 3px;font-weight:700;position:sticky;top:0;
  background:var(--panel)}
.it{display:flex;align-items:center;gap:7px;padding:6px 8px;border-radius:8px;cursor:pointer;
  font-size:12.5px}
.it:hover{background:#eef2fb}
.it.on{background:#e0e9fb}
.it .nm{flex:1;font-variant-numeric:tabular-nums}
.it .du{font-size:10.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.it .mk{width:14px;text-align:center;font-weight:700}
.it .mk.ok{color:var(--ok)}
.it .mk.bad{color:var(--bad)}
#stage{flex:1;overflow-y:auto;padding:18px 24px;min-width:0}
#hd{font-size:12.5px;color:var(--muted);margin-bottom:4px}
#dr{font-size:15px;font-weight:700;margin-bottom:12px}
#ctl{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}
#cdwrap{flex:1;min-width:160px;max-width:320px;height:8px;background:#e5e7eb;border-radius:5px;
  overflow:hidden;display:none}
#cdwrap.on{display:block}
#cd{height:100%;background:var(--warn);transition:width .1s linear}
#cdtxt{font-size:12px;color:var(--warn);font-variant-numeric:tabular-nums;display:none}
#cdtxt.on{display:inline}
#plays{font-size:12px;color:var(--muted)}
.q{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px 16px;
  margin-bottom:12px}
.q .qh{font-size:13.5px;font-weight:700;margin-bottom:9px}
.q .qh span{color:var(--muted);font-weight:400;margin-right:6px;font-variant-numeric:tabular-nums}
.opt{display:flex;gap:9px;align-items:flex-start;padding:8px 10px;border:1px solid var(--border);
  border-radius:8px;margin-bottom:6px;cursor:pointer;font-size:14px;line-height:1.5}
.opt:hover{background:#f0f2f6}
.opt.pick{border-color:var(--accent);background:#eef2fb}
.opt.right{border-color:var(--ok);background:#eefbf1}
.opt.wrong{border-color:var(--bad);background:#fdefef}
.opt .ky{font-weight:700;color:var(--muted);flex-shrink:0;width:14px}
.opt.locked{cursor:default}
.verdict{font-size:13px;font-weight:700;margin-top:4px}
.verdict.ok{color:var(--ok)}
.verdict.bad{color:var(--bad)}
.verdict.to{color:var(--warn)}
#trbox{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px 16px;
  margin-bottom:12px;line-height:1.8;font-size:14.5px;display:none}
#trbox.on{display:block}
#trbox h3{font-size:12px;color:var(--muted);margin-bottom:8px;font-weight:700}
#trbox p{margin-bottom:6px}
#stats{background:var(--panel);border-top:1px solid var(--border);padding:10px 24px;font-size:12.5px;
  display:none}
body.showstats #stats{display:block}
#stats table{border-collapse:collapse}
#stats th,#stats td{padding:3px 12px 3px 0;text-align:left;font-variant-numeric:tabular-nums}
#stats th{color:var(--muted);font-weight:600;font-size:11.5px}
#note{padding:10px 24px;font-size:12px;color:var(--muted);background:#fffdf3;
  border-top:1px solid var(--border);line-height:1.7}
#note b{color:var(--warn)}
#banner{display:none;padding:10px 24px;font-size:12.5px;background:#fdefef;color:#991b1b;
  border-bottom:1px solid #f5c2c2;line-height:1.7}
#banner.on{display:block}
#banner.info{background:#eef4ff;color:#1e40af;border-bottom-color:#c7d8f7}
#banner code{background:#fff;padding:1px 5px;border-radius:4px;font-size:12px}
#banner a{color:inherit;text-decoration:underline}
.err{color:var(--bad);font-size:13px;margin-top:6px}
#sceneSummary{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 24px 16px;line-height:1.6}
#sceneSummary .sumHead{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}
#sceneSummary h2{font-size:15px}
#sceneSummary .sumHint{font-size:11.5px;color:var(--muted)}
#sceneSummary .sumNote{font-size:12px;color:var(--muted);margin-bottom:10px}
.sceneGrid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.scene{border:1px solid var(--border);border-radius:8px;padding:9px 10px;background:#fafbfc}
.scene strong{display:block;font-size:12.5px;margin-bottom:2px}
.scene span{display:block;font-size:12px;color:var(--muted)}
.scene.social strong{color:#2563eb}.scene.nav strong{color:#7c3aed}.scene.acad strong{color:#059669}
.scene p{font-size:11.5px;color:var(--muted);margin-top:6px}
.scene .topics{color:var(--text);font-size:12px;margin-top:5px}
.sceneLinks{margin-top:10px;font-size:11.5px;color:var(--muted)}
.sceneLinks a{color:var(--accent);margin-right:12px}
@media(max-width:800px){.sceneGrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:520px){#sceneSummary{padding:11px 14px}.sceneGrid{grid-template-columns:1fr 1fr}.scene{padding:7px}.scene span,.scene .topics{font-size:11.5px}.sceneLinks a{display:inline-block;margin:2px 10px 2px 0}}
</style>
</head>
<body>
<div id="banner"></div>
<header>
  <h1>2026 新格式听力 <small id="cnt"></small></h1>
  <select id="ft"><option value="">全部卷</option></select>
  <select id="fm"><option value="">全部模块</option><option value="1">Module 1（Router）</option><option value="2">Module 2（分支）</option></select>
  <select id="fd"><option value="">全部进度</option><option value="todo">仅未做</option><option value="wrong">仅错过</option><option value="done">仅做过</option></select>
  <span class="sp"></span>
  <select id="cdsel" title="听答题音频播完后的作答时限。这是本页自设的练习节奏，不是官方公布的时限。">
    <option value="0">听答题不限时</option>
    <option value="5">听答题 5 秒</option>
    <option value="8" selected>听答题 8 秒</option>
    <option value="12">听答题 12 秒</option>
  </select>
  <button class="btn ghost" id="tt">显示原文</button>
  <button class="btn ghost" id="sb">成绩</button>
  <button class="btn ghost" id="rs">重置本类</button>
</header>
<div id="sceneSummary">
  <div class="sumHead"><h2>🧭 2026 新托福听力：场景与话题范围</h2><span class="sumHint">ETS 蓝图 + 2026 公开考情回忆的保守归纳</span></div>
  <div class="sumNote">最确定的变化是日常生活和职场沟通明显增加、学术音频缩短；公开回忆可用来确认“考过哪些范围”，但样本仍不足以估计各学科占比。</div>
  <div class="sceneGrid">
    <div class="scene social"><strong>日常社交 · 15–19 题</strong><span>Listen and Choose a Response</span><p class="topics">购物与客服、餐饮、公交/火车/机场、旅行、健身、天气、维修、预约、邀请、时间安排、请求和建议。</p><p>重点：听懂问句意图、否定问句、婉拒和自然回应。</p></div>
    <div class="scene social"><strong>短对话 · 10 题</strong><span>Listen to a Conversation</span><p class="topics">超市与农夫市场、租房、电脑/手机/汽车、健身房、读书会、聚会旅行；也包括会议、报告、营销演示等职场沟通。</p><p>旧式三分钟校园对话不再占主导。</p></div>
    <div class="scene nav"><strong>校园公告 · 6–10 题</strong><span>Listen to an Announcement</span><p class="topics">课程与作业截止、课堂调整、教授办公时间、图书馆/休息室、社团、讲座、校园活动、门户信息、设施维护。</p><p>重点：目的、时间地点、变化和行动要求。</p></div>
    <div class="scene acad"><strong>短学术讲座 · 8–16 题</strong><span>Listen to an Academic Talk</span><p class="topics">仍覆盖自然科学、人文与社会科学：生物生态、环境气候、心理/神经、经济社会、天文地质、化学工程、历史考古、艺术文学、语言教育。</p><p>常见结构：概念定义 → 原因/分类 → 例子或研究发现。传统学科没有证据表明被取消。</p></div>
  </div>
  <div class="sceneLinks">公开考情参考：
    <a href="http://sh.yuloo.com/toefl/listening/369166.html" target="_blank" rel="noopener">1 月 21 日首考</a>
    <a href="http://sh.yuloo.com/toefl/listening/369488.html" target="_blank" rel="noopener">2 月 1 日</a>
    <a href="http://sh.yuloo.com/toefl/listening/373811.html" target="_blank" rel="noopener">4 月 11 日</a>
    <a href="http://sh.yuloo.com/toefl/listening/376142.html" target="_blank" rel="noopener">5 月 9 日</a>
    <a href="https://www.qulexue.cn/lxks/10908.shtml" target="_blank" rel="noopener">8 月 19 日</a>
  </div>
</div>
<div id="tabs"></div>
<main>
  <div id="list"></div>
  <div id="stage">
    <div id="hd"></div>
    <div id="dr">请从左侧选择一条</div>
    <div id="ctl">
      <button class="btn" id="pl">播放</button>
      <button class="btn ghost" id="pd" hidden>播放指令</button>
      <div id="cdwrap"><div id="cd"></div></div>
      <span id="cdtxt"></span>
      <span id="plays"></span>
    </div>
    <div id="err" class="err"></div>
    <div id="qs"></div>
    <div id="trbox"></div>
  </div>
</main>
<div id="stats"></div>
<div id="note">
  <b>听答题的作答倒计时是本页自设的练习节奏</b>，官方从未公布这一题型的作答时限，别把它当考场标准。<br>
  Module 1 = Router（人人都做，据此决定分支），Module 2 = 按 Module 1 表现走的上/下分支，
  所以 M1 与 M2 的难度不可直接比较。<br>
  音频为 ETS 原始文件（多数是 22 kHz 单声道 Ogg Vorbis，Copyright © 2025 ETS），
  优先读本页同级的 <code>audio/</code>，没有就从
  <a href="https://huggingface.co/datasets/xxfasdf/toefl-2026-official-listening-audio" target="_blank" rel="noopener">HuggingFace 公开镜像</a>
  流式播放；原始文件在 <a href="https://www.ets.org/toefl/test-takers/ibt/prepare.html" target="_blank" rel="noopener">ETS 官网</a>免费公开下载。
  Ogg 在 Chrome/Firefox/Edge 与 Safari 17+ 可播；更老的 Safari 会报解码失败。做题记录存在本机浏览器。
</div>
<script>
const DATA = __DATA__;
const ITEMS = DATA.items, KINDS = DATA.kinds, TESTS = DATA.tests;
const KEY = 'hl2026_v1';
let S = {};
try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { S = {}; }
S.ans = S.ans || {};      // "itemId#qn" -> 选的字母，或 '_TO_' 表示超时未答
S.plays = S.plays || {};  // itemId -> 播放次数
S.tab = S.tab || KINDS[0].c;
S.showTr = S.showTr || false;
S.stats = S.stats || false;
S.cd = (S.cd === undefined) ? 8 : S.cd;
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };

const $ = id => document.getElementById(id);
const au = new Audio();
let cur = null, timer = null, deadline = 0;

// 音频两个来源：本页同级的 audio/（本地/离线优先），和 HF 公开镜像（线上兜底）。
const HF_BASE = 'https://huggingface.co/datasets/xxfasdf/toefl-2026-official-listening-audio/resolve/main/audio/';
let AUBASE = 'audio/';
const auURL = name => AUBASE + encodeURIComponent(name);
let mirrorNoted = false;
function showMirrorNote() {
  if (mirrorNoted) return;
  mirrorNoted = true;
  $('banner').className = 'on info';
  $('banner').innerHTML = '本页同级没有 <code>audio/</code> 目录，音频改从 '
    + '<a href="https://huggingface.co/datasets/xxfasdf/toefl-2026-official-listening-audio" target="_blank" rel="noopener">'
    + 'HuggingFace 公开镜像</a> 直接流式播放（196 个文件 / 28 MB，ETS 原始音频，Copyright © 2025 ETS）。'
    + '想离线用就把音频放到本页同级的 <code>audio/</code> 目录，本地文件优先。';
}

const fmt = s => (s == null ? '--' : (s < 60 ? s.toFixed(1) + 's'
  : Math.floor(s / 60) + ':' + String(Math.round(s % 60)).padStart(2, '0')));
const qkey = (it, q) => it.id + '#' + q.n;
// 一个条目「做过」= 它下面所有题都有记录（选了或超时）
const isDone = it => it.qs.every(q => S.ans[qkey(it, q)]);
const nRight = it => it.qs.filter(q => S.ans[qkey(it, q)] === q.a).length;
const hasWrong = it => it.qs.some(q => S.ans[qkey(it, q)] && S.ans[qkey(it, q)] !== q.a);

TESTS.forEach(t => {
  const o = document.createElement('option');
  o.value = t.c; o.textContent = t.n; $('ft').appendChild(o);
});
$('cdsel').value = String(S.cd);

function renderTabs() {
  $('tabs').innerHTML = '';
  KINDS.forEach(k => {
    const all = ITEMS.filter(x => x.k === k.c);
    const dn = all.filter(isDone).length;
    const b = document.createElement('button');
    b.className = S.tab === k.c ? 'on' : '';
    b.innerHTML = '<b>' + k.n + '</b> ' + dn + '/' + all.length;
    b.onclick = () => { S.tab = k.c; save(); stop(); cur = null; renderTabs(); render(); blank(); };
    $('tabs').appendChild(b);
  });
}

function pool() {
  const t = $('ft').value, m = $('fm').value, d = $('fd').value;
  return ITEMS.filter(x => {
    if (x.k !== S.tab) return false;
    if (t && x.t !== t) return false;
    if (m && String(x.m) !== m) return false;
    if (d === 'todo' && isDone(x)) return false;
    if (d === 'done' && !isDone(x)) return false;
    if (d === 'wrong' && !hasWrong(x)) return false;
    return true;
  });
}

function render() {
  const L = pool();
  const kind = KINDS.find(k => k.c === S.tab);
  const all = ITEMS.filter(x => x.k === S.tab);
  const nq = all.reduce((a, x) => a + x.qs.length, 0);
  const got = all.reduce((a, x) => a + nRight(x), 0);
  const ansd = all.reduce((a, x) => a + x.qs.filter(q => S.ans[qkey(x, q)]).length, 0);
  $('cnt').textContent = kind.n + ' ' + L.length + '/' + all.length + ' 条 · 已答 '
    + ansd + '/' + nq + ' 题' + (ansd ? ' · 正确率 ' + (100 * got / ansd).toFixed(0) + '%' : '');
  $('list').innerHTML = '';
  let lastT = null;
  L.forEach(it => {
    if (it.t !== lastT) {
      lastT = it.t;
      const g = document.createElement('div');
      g.className = 'grp';
      g.textContent = TESTS.find(t => t.c === it.t).n;
      $('list').appendChild(g);
    }
    const el = document.createElement('div');
    el.className = 'it' + (cur && cur.id === it.id ? ' on' : '');
    let mk = '';
    if (isDone(it)) {
      const r = nRight(it), n = it.qs.length;
      mk = r === n ? '<span class="mk ok">✓</span>'
        : (r === 0 ? '<span class="mk bad">✗</span>'
          : '<span class="mk bad">' + r + '/' + n + '</span>');
    } else mk = '<span class="mk"></span>';
    el.innerHTML = mk + '<span class="nm">M' + it.m + ' · ' + it.id.split('_').pop()
      + (it.qs.length > 1 ? ' <span style="color:#6b7280">(' + it.qs.length + '题)</span>' : '')
      + '</span><span class="du">' + fmt(it.d) + (it.de ? '~' : '') + '</span>';
    el.onclick = () => open(it);
    $('list').appendChild(el);
  });
  if (document.body.classList.contains('showstats')) renderStats();
}

function blank() {
  $('hd').textContent = ''; $('dr').textContent = '请从左侧选择一条';
  $('qs').innerHTML = ''; $('trbox').className = ''; $('trbox').innerHTML = '';
  $('plays').textContent = ''; $('err').textContent = ''; $('pd').hidden = true;
}

function stop() {
  if (timer) { clearInterval(timer); timer = null; }
  $('cdwrap').className = ''; $('cdtxt').className = '';
  au.pause();
}

function open(it) {
  stop();
  cur = it;
  $('err').textContent = '';
  const tn = TESTS.find(t => t.c === it.t).n;
  const kind = KINDS.find(k => k.c === it.k);
  $('hd').textContent = tn + ' · Module ' + it.m + ' · ' + kind.n
    + ' · 音频 ' + fmt(it.d) + (it.de ? '（估算）' : '') + ' · 第 '
    + it.qs.map(q => q.n).join('/') + ' 题';
  $('dr').textContent = it.dr;
  $('pd').hidden = !it.ad;
  $('plays').textContent = S.plays[it.id] ? '已播 ' + S.plays[it.id] + ' 次' : '未播放';
  renderQs();
  renderTr();
  render();
  play();
}

function play() {
  if (!cur || !cur.au) return;
  stop();
  au.src = auURL(cur.au);
  au.currentTime = 0;
  au.play().then(() => {
    S.plays[cur.id] = (S.plays[cur.id] || 0) + 1; save();
    $('plays').textContent = '已播 ' + S.plays[cur.id] + ' 次';
    render();
  }).catch(e => {
    // 本地目录没有音频时退到 HF 公开镜像再试一次，只退一次
    if (AUBASE !== HF_BASE) { AUBASE = HF_BASE; showMirrorNote(); play(); return; }
    $('err').textContent = '音频播不了：' + e.message + '（Ogg 需要 Chrome/Firefox 或 Safari 17+）';
  });
}

$('pl').onclick = play;
$('pd').onclick = () => {
  if (!cur || !cur.ad) return;
  stop();
  au.src = auURL(cur.ad);
  au.play().catch(e => { $('err').textContent = '指令音频播不了：' + e.message; });
};

// 听答题：音频播完就开始倒计时，到点没答记为超时。其他题型不限时。
au.onended = () => {
  if (!cur || cur.k !== 'cr' || !S.cd) return;
  const q = cur.qs[0];
  if (S.ans[qkey(cur, q)]) return;
  const total = S.cd * 1000;
  deadline = Date.now() + total;
  $('cdwrap').className = 'on'; $('cdtxt').className = 'on';
  timer = setInterval(() => {
    const left = deadline - Date.now();
    $('cd').style.width = Math.max(0, 100 * left / total) + '%';
    $('cdtxt').textContent = Math.max(0, left / 1000).toFixed(1) + 's';
    if (left <= 0) {
      stop();
      if (!S.ans[qkey(cur, q)]) { S.ans[qkey(cur, q)] = '_TO_'; save(); renderQs(); renderTr(); render(); }
    }
  }, 100);
};

function renderQs() {
  $('qs').innerHTML = '';
  if (!cur) return;
  cur.qs.forEach(q => {
    const k = qkey(cur, q), picked = S.ans[k];
    const box = document.createElement('div');
    box.className = 'q';
    let h = '<div class="qh"><span>第 ' + q.n + ' 题</span>'
      + (q.q ? q.q : '选出最合适的回应') + '</div>';
    Object.keys(q.o).forEach(ky => {
      let cls = 'opt';
      if (picked) {
        cls += ' locked';
        if (ky === q.a) cls += ' right';
        else if (ky === picked) cls += ' wrong';
      }
      h += '<div class="' + cls + '" data-q="' + q.n + '" data-k="' + ky + '">'
        + '<span class="ky">' + ky + '</span><span>' + esc(q.o[ky]) + '</span></div>';
    });
    if (picked) {
      h += picked === '_TO_' ? '<div class="verdict to">超时未答 · 正确答案 ' + q.a + '</div>'
        : (picked === q.a ? '<div class="verdict ok">答对</div>'
          : '<div class="verdict bad">答错 · 正确答案 ' + q.a + '</div>');
    }
    box.innerHTML = h;
    box.querySelectorAll('.opt').forEach(o => {
      if (picked) return;
      o.onclick = () => answer(q, o.dataset.k);
    });
    $('qs').appendChild(box);
  });
}

function answer(q, ky) {
  const k = qkey(cur, q);
  if (S.ans[k]) return;
  S.ans[k] = ky; save();
  if (cur.k === 'cr') stop();
  renderQs(); renderTr(); render();
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

// 原文默认藏起来——听力练习里提前看到原文等于白练。全部题答完后自动可见。
function renderTr() {
  const box = $('trbox');
  if (!cur) { box.className = ''; box.innerHTML = ''; return; }
  const show = S.showTr || isDone(cur);
  if (!show) { box.className = ''; box.innerHTML = ''; return; }
  box.className = 'on';
  box.innerHTML = '<h3>音频原文' + (S.showTr && !isDone(cur) ? '（你手动打开的，注意别提前看）' : '') + '</h3>'
    + cur.tr.map(p => '<p>' + esc(p) + '</p>').join('');
}

function renderStats() {
  let rows = '', tq = 0, tr = 0, tto = 0;
  KINDS.forEach(k => {
    const all = ITEMS.filter(x => x.k === k.c);
    const qs = all.flatMap(x => x.qs.map(q => [x, q]));
    const ansd = qs.filter(([x, q]) => S.ans[qkey(x, q)]);
    const right = ansd.filter(([x, q]) => S.ans[qkey(x, q)] === q.a).length;
    const to = ansd.filter(([x, q]) => S.ans[qkey(x, q)] === '_TO_').length;
    tq += ansd.length; tr += right; tto += to;
    rows += '<tr><td>' + k.n + '</td><td>' + ansd.length + ' / ' + qs.length + '</td>'
      + '<td>' + (ansd.length ? (100 * right / ansd.length).toFixed(0) + '%' : '—') + '</td>'
      + '<td>' + (to || '') + '</td></tr>';
  });
  $('stats').innerHTML = '<table><tr><th>题型</th><th>已答 / 总</th><th>正确率</th><th>超时</th></tr>'
    + rows + '<tr><td><b>合计</b></td><td><b>' + tq + ' / ' + DATA.meta.nq + '</b></td><td><b>'
    + (tq ? (100 * tr / tq).toFixed(0) + '%' : '—') + '</b></td><td><b>' + (tto || '') + '</b></td></tr></table>';
}

['ft', 'fm', 'fd'].forEach(id => $(id).addEventListener('change', () => { render(); }));
$('cdsel').onchange = () => { S.cd = Number($('cdsel').value); save(); };
$('tt').onclick = () => {
  S.showTr = !S.showTr; save();
  $('tt').textContent = S.showTr ? '隐藏原文' : '显示原文';
  renderTr();
};
$('sb').onclick = () => {
  S.stats = !S.stats; save();
  document.body.classList.toggle('showstats', S.stats);
  $('sb').textContent = S.stats ? '收起成绩' : '成绩';
  if (S.stats) renderStats();
};
$('rs').onclick = () => {
  const kind = KINDS.find(k => k.c === S.tab);
  if (!confirm('清掉「' + kind.n + '」这一类的全部作答记录？播放次数也会一起清。')) return;
  ITEMS.filter(x => x.k === S.tab).forEach(x => {
    x.qs.forEach(q => { delete S.ans[qkey(x, q)]; });
    delete S.plays[x.id];
  });
  save(); stop(); cur = null; renderTabs(); render(); blank();
};

// 键盘：A/B/C/D 选项、空格重播、N 下一条
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
  const k = e.key.toUpperCase();
  if (k === ' ' || e.code === 'Space') { e.preventDefault(); play(); return; }
  if (k === 'N') {
    const L = pool();
    const i = cur ? L.findIndex(x => x.id === cur.id) : -1;
    if (L.length) open(L[(i + 1) % L.length]);
    return;
  }
  if (!cur || !'ABCD'.includes(k)) return;
  const q = cur.qs.find(q2 => !S.ans[qkey(cur, q2)]);
  if (q && q.o[k]) { e.preventDefault(); answer(q, k); }
});

$('tt').textContent = S.showTr ? '隐藏原文' : '显示原文';
document.body.classList.toggle('showstats', !!S.stats);
$('sb').textContent = S.stats ? '收起成绩' : '成绩';
renderTabs();
render();
blank();

// 音频来源：优先本页同级的 audio/ 目录（本地开发、离线可用），
// 取不到就退到 HF 公开镜像。镜像用 <audio> 直连没有 CORS 问题
// （最终 CDN 响应带 access-control-allow-origin: *，且支持 Range 206），
// 但 fetch 探测 HF 会在 302 那一跳被 CORS 拦掉，所以只探本地、不探镜像。
function probeAudio() {
  const first = ITEMS.find(x => x.au);
  if (!first || location.protocol === 'file:') return Promise.resolve();
  return fetch('audio/' + encodeURIComponent(first.au), { method: 'HEAD' })
    .then(r => { if (!r.ok) { AUBASE = HF_BASE; showMirrorNote(); } })
    .catch(() => { AUBASE = HF_BASE; showMirrorNote(); });
}
probeAudio();
</script>
</body>
</html>
"""

os.makedirs(SITE, exist_ok=True)
html = HTML.replace("__DATA__", data_json)
open(OUT, "w", encoding="utf-8").write(html)
# 页面上不该出现 TPO / 旧格式字样混淆口径；这里只做一个粗查
leak = re.findall(r"TPO", html)
print(f"已生成 {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)"
      + (f"  !! 出现 {len(leak)} 处 TPO 字样" if leak else ""))
