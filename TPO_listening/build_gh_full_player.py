#!/usr/bin/env python3
"""构建可部署到 GitHub Pages 的全库听力播放器（1-75 套，424 集，单文件内嵌）。

数据来源：
  TPO听力播放器.html   -> ITEMS（424 集双语逐句 cues，复用已解析好的结果）
  manifest.json        -> 每集的远端音频直链（audio_url）
  tpo_dates.json       -> 每套的出题时间 / 上线时间
  subjects.py          -> 讲座学科提取 + 粗领域归并（旁白句优先，无旁白句才退关键词）

关键点：远端音频源 file-corpus.zhan.com 有 Referer 白名单，
        带外站 Referer 会返回 403，不带 Referer 则正常 200/206。
        因此页面必须声明 <meta name="referrer" content="no-referrer">。

用法: python3 build_gh_full_player.py
输出: gh_full_player.html, subjects.json（学科映射，供审计与复用）
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import subjects as SJ  # noqa: E402

SRC_PLAYER = os.path.join(HERE, "TPO听力播放器.html")
MANIFEST = os.path.join(HERE, "manifest.json")
DATES = os.path.join(HERE, "tpo_dates.json")
OUT = os.path.join(HERE, "gh_full_player.html")
OUT_SUBJ = os.path.join(HERE, "subjects.json")

# ---- 读入三份数据 ----
raw = open(SRC_PLAYER, encoding="utf-8").read()
m = re.search(r"const ITEMS\s*=\s*(\[.*?\]);", raw, re.S)
if not m:
    raise SystemExit("在 TPO听力播放器.html 里找不到 ITEMS")
items = json.loads(m.group(1))

audio_by_file = {x["audio_file"]: x["audio_url"] for x in json.load(open(MANIFEST, encoding="utf-8"))}
dates = json.load(open(DATES, encoding="utf-8"))["sets"]

# ---- 脱敏：与 gh_listening_player 保持一致，不在页面上暴露考试名称 ----
_STRIP = ((r"新东方在线|太原新东方|新东方", "某机构"), (r"TOEFL|Official|托福", ""), (r"ETS", "官方"), (r"TPO-?", ""))


def clean(s):
    for pat, rep in _STRIP:
        s = re.sub(pat, rep, s)
    return re.sub(r"\s{2,}", " ", s).strip()


CONV_DOMAIN = "校园对话"

out_items = []
missing_audio = []
subj_dump = []
for it in items:
    url = audio_by_file.get(it["file"])
    if not url:
        missing_audio.append(it["file"])
        continue
    n = str(it["tpo"])
    d = dates.get(n, {})
    cues = it.get("cues") or []
    o = {
        "n": it["tpo"],                                   # 套号
        "k": it["kind"],                                  # conv / lec
        "q": it["seq"],                                   # 该类型内序号
        "t": it["title"],                                 # 英文标题
        "a": url,                                         # 远端音频直链
        "d": round(cues[-1][0] + 8) if cues else 0,        # 估算时长（末句时间 +8s）
        "c": cues,                                        # [[秒, 英文, 中文], ...]
    }
    if it["kind"] == "lec":
        head = " ".join(c[1] for c in cues[:3])
        body = " ".join(c[1] for c in cues[:40])
        sj, dom, origin = SJ.classify(head, it["title"], body, key=(it["tpo"], it["seq"]))
        o["g"] = dom
        if sj:
            o["sj"] = sj
        o["og"] = {"narrator": "n", "keyword": "k", "manual": "m"}[origin]
        subj_dump.append({"set": it["tpo"], "seq": it["seq"], "title": it["title"],
                          "subject": sj, "domain": dom, "origin": origin})
    else:
        o["g"] = CONV_DOMAIN
    if d.get("exam"):
        o["y"] = d["exam"]
        if d.get("conf") == "low":
            o["yq"] = 1
    if d.get("release"):
        o["r"] = d["release"]
    if d.get("note"):
        o["yn"] = clean(d["note"])
    out_items.append(o)

out_items.sort(key=lambda x: (x["n"], 0 if x["k"] == "conv" else 1, x["q"]))
for i, o in enumerate(out_items, 1):
    o["i"] = i

sets = sorted({o["n"] for o in out_items})
n_exam = sum(1 for o in out_items if o.get("y"))
n_rel = sum(1 for o in out_items if not o.get("y") and o.get("r"))
print(f"条目 {len(out_items)} 集，覆盖 {len(sets)} 套（{min(sets)}-{max(sets)}，缺 "
      f"{[n for n in range(min(sets), max(sets) + 1) if n not in sets]}）")
print(f"  有出题时间 {n_exam} 集 / 仅上线时间 {n_rel} 集")
if missing_audio:
    print(f"  !! 缺远端音频直链 {len(missing_audio)} 集: {missing_audio[:3]}")

# ---- 学科映射统计 + 落盘（供审计与其他脚本复用）----
from collections import Counter  # noqa: E402

lecs = [o for o in out_items if o["k"] == "lec"]
dom_cnt = Counter(o["g"] for o in lecs)
org_cnt = Counter(o["og"] for o in lecs)
print(f"  讲座 {len(lecs)} 集 学科来源: 旁白句 {org_cnt['n']} / 关键词 {org_cnt['k']} / 手工 {org_cnt['m']}")
if dom_cnt.get("其他"):
    print(f"  !! 有 {dom_cnt['其他']} 集未归入任何领域")
for d, c in dom_cnt.most_common():
    print(f"    {d:<20} {c:>3} 集  {100 * c / len(lecs):>5.1f}%")
json.dump(sorted(subj_dump, key=lambda r: (r["set"], r["seq"])),
          open(OUT_SUBJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"  学科映射已写入 {os.path.basename(OUT_SUBJ)}")

data_json = json.dumps({"items": out_items}, ensure_ascii=False, separators=(",", ":"))

# ---- 200 集精选页的进度迁移表 ----
# 两个页面同源（同一个 GitHub Pages 域名），localStorage 是共享的，所以全库页可以
# 直接读精选页的 key，把「已听」标记搬过来。精选页用 s 字段（如 "25_L4"）标识条目，
# 需要换算成全库的 i。找不到精选页文件时留空表，页面会自动隐藏导入按钮。
SEL_PLAYER = os.path.join(os.path.dirname(HERE), "listening", "index.html")
SEL_KEY = "en_listening_player"
map200 = {}
if os.path.exists(SEL_PLAYER):
    sel_raw = open(SEL_PLAYER, encoding="utf-8").read()
    mm = re.search(r"const DATA = (\{.*?\});\s*\n", sel_raw, re.S)
    if mm:
        sel = json.loads(mm.group(1))
        by_key = {(o["n"], o["k"], o["q"]): o["i"] for o in out_items}
        unmatched = []
        for o in sel["items"]:
            ms = re.match(r"^(\d+)_([CL])(\d+)$", o["s"])
            if not ms:
                unmatched.append(o["s"])
                continue
            k = (int(ms.group(1)), "conv" if ms.group(2) == "C" else "lec", int(ms.group(3)))
            if k in by_key:
                map200[o["i"]] = by_key[k]
            else:
                unmatched.append(o["s"])
        print(f"  精选页进度迁移表: {len(map200)}/{len(sel['items'])} 条可对应"
              + (f"，对不上 {unmatched[:5]}" if unmatched else ""))
    else:
        print("  !! 精选页里找不到 DATA，进度迁移表留空")
else:
    print("  !! 找不到精选页 listening/index.html，进度迁移表留空")

# 脱敏自检：区分「可见文本泄露」（必须为 0）与「音频直链路径里的字样」（第三方 CDN 路径，无法改写）
vis = json.dumps([{k: v for k, v in o.items() if k not in ("c", "a")} for o in out_items], ensure_ascii=False)
leak_vis = re.findall(r"TPO|TOEFL|Official|托福", vis)
leak_url = sum(1 for o in out_items if re.search(r"TPO|TOEFL|Official|toefl", o["a"]))
print(f"  可见文本脱敏: {'通过' if not leak_vis else '发现 ' + str(len(leak_vis)) + ' 处泄露'}")
print(f"  音频直链含考试字样: {leak_url} 集（第三方 CDN 路径，与既有播放器同一情况，无法改写）")
data_json = data_json.replace("</", "<\\/")

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- 音频源有 Referer 白名单：带外站 Referer 会 403，必须整页不发 Referer -->
<meta name="referrer" content="no-referrer">
<title>英语听力全库 · 424 集</title>
<style>
:root {
  --bg:#f5f6f8; --panel:#fff; --accent:#2f6fed; --accent-dark:#1d4fc4;
  --text:#1a1d24; --muted:#6b7280; --border:#e3e6eb; --hl:#fff5d6;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
header{background:var(--panel);border-bottom:1px solid var(--border);padding:10px 16px;
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;z-index:10}
header h1{font-size:16px;font-weight:700;margin-right:auto;white-space:nowrap}
header h1 small{font-size:12px;color:var(--muted);font-weight:400;margin-left:6px}
select,input[type=search],button{font-size:13px;padding:6px 10px;border:1px solid var(--border);
  border-radius:8px;background:#fff;color:var(--text);outline:none}
select:focus,input:focus{border-color:var(--accent)}
#q{width:190px}
.btn{background:var(--accent);color:#fff;border-color:var(--accent);cursor:pointer}
.btn:hover{background:var(--accent-dark)}
.btn.ghost{background:#fff;color:var(--text);border-color:var(--border)}
main{flex:1;display:flex;min-height:0}
#list{width:340px;min-width:260px;background:var(--panel);border-right:1px solid var(--border);
  overflow-y:auto;padding:8px}
.grp{font-size:11px;color:var(--muted);padding:8px 6px 3px;font-weight:700;position:sticky;top:0;
  background:var(--panel)}
.ep{display:flex;align-items:center;gap:7px;padding:6px 8px;border-radius:8px;cursor:pointer}
.ep:hover{background:#eef2fb}
.ep.on{background:#e0e9fb}
.ep .tag{font-size:10px;padding:1px 5px;border-radius:4px;flex-shrink:0;font-weight:700}
.ep .tag.conv{background:#dcfce7;color:#166534}
.ep .tag.lec{background:#e0e7ff;color:#3730a3}
.ep .nm{flex:1;font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ep .ex{font-size:10.5px;color:#7a4ec4;flex-shrink:0;font-variant-numeric:tabular-nums}
.ep .ex.guess{color:#a9a2b8}
.ep .rel{font-size:10.5px;color:#8a9299;flex-shrink:0;font-variant-numeric:tabular-nums}
.ep .du{font-size:10.5px;color:var(--muted);flex-shrink:0;font-variant-numeric:tabular-nums}
.ep .ok{color:#16a34a;font-weight:700;flex-shrink:0}
.ep .dm{font-size:10px;padding:1px 5px;border-radius:4px;flex-shrink:0;background:#f1f3f7;color:#4b5563}
.ep .dm.kw{background:#fdf0e3;color:#9a5b13}
#right{flex:1;display:flex;flex-direction:column;min-width:0}
#bar{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 18px}
#tt{font-size:15px;font-weight:700}
#sub{font-size:12px;color:var(--muted);margin-top:3px}
#au{width:100%;margin-top:10px}
#txt{flex:1;overflow-y:auto;padding:16px 22px;line-height:1.75}
.cue{padding:5px 8px;border-radius:6px;cursor:pointer;border-left:3px solid transparent}
.cue:hover{background:#f0f2f6}
.cue.on{background:var(--hl);border-left-color:var(--accent)}
.cue .en{font-size:14.5px}
.cue .zh{font-size:13px;color:var(--muted);margin-top:2px}
body.nozh .cue .zh{display:none}
#empty{padding:40px;text-align:center;color:var(--muted)}
#tip{padding:10px 22px;font-size:12px;color:var(--muted);background:#fffdf3;
  border-top:1px solid var(--border);line-height:1.7}
/* 进度面板：按领域看还剩多少没听，用来找知识盲区 */
#prog{display:none;padding:14px 22px;background:#f8fafc;border-bottom:1px solid var(--border);
  font-size:12.5px;overflow-y:auto;max-height:46vh}
body.showprog #prog{display:block}
#prog table{border-collapse:collapse;width:100%;max-width:640px}
#prog th,#prog td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--border);
  font-variant-numeric:tabular-nums}
#prog th{color:var(--muted);font-weight:600;font-size:11.5px}
#prog td.n,#prog th.n{text-align:right}
#prog .bar{display:inline-block;width:90px;height:7px;background:#e5e7eb;border-radius:4px;
  overflow:hidden;vertical-align:middle}
#prog .bar i{display:block;height:100%;background:var(--accent)}
#prog tr.tot td{font-weight:700;border-top:2px solid var(--border)}
#prog a{color:var(--accent);cursor:pointer;text-decoration:none}
#prog a:hover{text-decoration:underline}
</style>
</head>
<body>
<header>
  <h1>英语听力全库 <small id="cnt"></small></h1>
  <input type="search" id="q" placeholder="搜索：套号、标题、学科、年份…">
  <select id="fk"><option value="">全部类型</option><option value="conv">仅对话</option><option value="lec">仅讲座</option></select>
  <select id="fg"><option value="">全部领域</option></select>
  <select id="fd"><option value="">全部进度</option><option value="todo">仅未听</option><option value="done">仅已听</option></select>
  <select id="fr"><option value="">全部套数</option></select>
  <select id="st">
    <option value="num">按套号（小→大）</option>
    <option value="numDesc">按套号（大→小）</option>
    <option value="era">按年代（新→旧）</option>
    <option value="eraAsc">按年代（旧→新）</option>
    <option value="dom">按学科领域</option>
  </select>
  <button class="btn ghost" id="pg">进度</button>
  <button class="btn ghost" id="imp" hidden>导入精选页进度</button>
  <button class="btn ghost" id="zh">隐藏中文</button>
  <button class="btn ghost" id="mk">标记听完</button>
</header>
<main>
  <div id="list"></div>
  <div id="right">
    <div id="prog"></div>
    <div id="bar">
      <div id="tt">请从左侧选择</div>
      <div id="sub"></div>
      <audio id="au" controls preload="none"></audio>
    </div>
    <div id="txt"><div id="empty">选择一集后显示中英逐句原文，点句子可跳转播放</div></div>
    <div id="tip">
      紫色小字 = <b>听力部分的出题时间</b>（原始考试年月，仅前 26 套有数据；带 <b>?</b> 的是不同版本互相矛盾的值）。
      灰色 <b>↑</b> = <b>上线时间</b>（该套被放出的时间，多数只能给上界或区间）。两者都可搜索、可排序。<br>
      灰色学科标签来自转写开头的旁白句（"a lecture in a ___ class"），是原始标签；
      <b style="color:#9a5b13">橙色</b>标签表示该集转写没有旁白句、领域是按标题和正文关键词推断的，可信度低一档。<br>
      <b>要紧的前提</b>：一套题<b>不等于</b>一场考试——它是跨年份、跨科目的拼盘，四科可能来自四个不同年份的不同场次
      （已核实的实例：第 71 套阅读来自 2016-03-19、口语来自 2014/2015/2017 年三场、综合写作来自 2013 年）。
      所以这里的日期只代表<b>听力</b>，不代表该套其他科目。出题时间全部来自民间整理的对照表，官方从未公布过套号与考期的对应。<br>
      进度与"听完"标记保存在本机浏览器。音频为远端直链，首次播放需缓冲。
    </div>
  </div>
</main>
<script>
const DATA = __DATA__;
const ITEMS = DATA.items;
// 精选页条目序号 -> 全库条目序号。两个页面同源，localStorage 共享，可以直接搬进度。
const MAP200 = __MAP200__;
const SEL_KEY = '__SELKEY__';
const KEY = 'hl_full_v1';
let S = {};
try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { S = {}; }
S.pos = S.pos || {}; S.done = S.done || {}; S.last = S.last || null; S.nozh = S.nozh || false;
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} };

const $ = id => document.getElementById(id);
const list = $('list'), au = $('au'), txt = $('txt');
let cur = null, cues = [], nodes = [], active = -1;

const fmt = s => { s = Math.max(0, Math.round(s)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
const label = it => it.n + ' · ' + (it.k === 'conv' ? 'C' : 'L') + it.q;
// 年代排序键：出题时间优先，否则用上线时间（剥掉 ≤ ~ 等符号）
const era = it => it.y || (it.r ? String(it.r).replace(/[^0-9-]/g, '').slice(0, 7) : '');

// 套号筛选下拉：按 10 套一档
const sets = [...new Set(ITEMS.map(x => x.n))].sort((a, b) => a - b);
for (let lo = Math.floor(sets[0] / 10) * 10 || 1; lo <= sets[sets.length - 1]; lo += 10) {
  const hi = lo + 9, has = sets.some(n => n >= lo && n <= hi);
  if (has) { const o = document.createElement('option'); o.value = lo + '-' + hi; o.textContent = lo + '–' + hi + ' 套'; $('fr').appendChild(o); }
}

// 领域筛选下拉：讲座领域按集数降序，校园对话固定放最后
const domCount = {};
ITEMS.forEach(x => { domCount[x.g] = (domCount[x.g] || 0) + 1; });
const DOMS = Object.keys(domCount)
  .filter(d => d !== '校园对话')
  .sort((a, b) => domCount[b] - domCount[a]);
DOMS.concat(domCount['校园对话'] ? ['校园对话'] : []).forEach(d => {
  const o = document.createElement('option');
  o.value = d; o.textContent = d + ' (' + domCount[d] + ')';
  $('fg').appendChild(o);
});
const domOrder = {};
DOMS.concat(['校园对话']).forEach((d, i) => { domOrder[d] = i; });

function filtered() {
  const q = $('q').value.trim().toLowerCase(), k = $('fk').value, r = $('fr').value;
  const g = $('fg').value, dn = $('fd').value;
  let L = ITEMS.filter(it => {
    if (k && it.k !== k) return false;
    if (g && it.g !== g) return false;
    if (dn === 'done' && !S.done[it.i]) return false;
    if (dn === 'todo' && S.done[it.i]) return false;
    if (r) { const [lo, hi] = r.split('-').map(Number); if (it.n < lo || it.n > hi) return false; }
    if (q) {
      const hay = (it.n + ' ' + label(it) + ' ' + it.t + ' ' + it.g + ' ' + (it.sj || '') + ' ' + (it.y || '') + ' ' + (it.r || '')).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  const s = $('st').value;
  if (s === 'numDesc') L = L.slice().sort((a, b) => b.n - a.n || a.i - b.i);
  else if (s === 'dom') L = L.slice().sort((a, b) => (domOrder[a.g] - domOrder[b.g]) || a.i - b.i);
  else if (s === 'era' || s === 'eraAsc') {
    const desc = s === 'era';
    L = L.slice().sort((a, b) => {
      const x = era(a), y = era(b);
      if (!x && !y) return a.i - b.i;
      if (!x) return 1; if (!y) return -1;
      if (x !== y) return desc ? y.localeCompare(x) : x.localeCompare(y);
      return a.i - b.i;
    });
  }
  return L;
}

// 组标题：出题时间是「听力这一篇来自哪场考试」，上线时间只是这套题被放出的时间。
// 两者不能混说，所以只有上线时间的套必须明确写出「出题时间未知」。
function grpLabel(it) {
  if (it.y) return '第 ' + it.n + ' 套 · 出题 ' + it.y + (it.yq ? '?（版本冲突）' : '');
  if (it.r) return '第 ' + it.n + ' 套 · 上线 ' + it.r + ' · 出题时间未知';
  return '第 ' + it.n + ' 套 · 年代未知';
}

function render() {
  const L = filtered();
  const doneAll = ITEMS.filter(x => S.done[x.i]).length;
  $('cnt').textContent = L.length + ' / ' + ITEMS.length + ' 集 · 已听 ' + doneAll
    + '（' + (100 * doneAll / ITEMS.length).toFixed(0) + '%）';
  list.innerHTML = '';
  let lastGrp = null;
  const mode = $('st').value;
  const byNum = mode.startsWith('num'), byDom = mode === 'dom';
  L.forEach(it => {
    const gk = byNum ? 'n' + it.n : (byDom ? 'd' + it.g : null);
    if (gk && gk !== lastGrp) {
      lastGrp = gk;
      const g = document.createElement('div');
      g.className = 'grp';
      if (byDom) {
        const tot = ITEMS.filter(x => x.g === it.g).length;
        const dn = ITEMS.filter(x => x.g === it.g && S.done[x.i]).length;
        g.textContent = it.g + ' · ' + dn + '/' + tot + ' 已听';
      } else {
        g.textContent = grpLabel(it);
      }
      list.appendChild(g);
    }
    const el = document.createElement('div');
    el.className = 'ep' + (cur && cur.i === it.i ? ' on' : '');
    const era_ = it.y
      ? '<span class="ex' + (it.yq ? ' guess' : '') + '" title="出题时间 ' + it.y + (it.yq ? '（版本有冲突，仅供参考）' : '') + (it.yn ? '\n' + it.yn : '') + '">' + it.y.slice(0, 7) + (it.yq ? '?' : '') + '</span>'
      : (it.r ? '<span class="rel" title="出题时间查无数据；上线时间 ' + it.r + (it.yn ? '\n' + it.yn : '') + '">↑' + it.r + '</span>' : '');
    const dm = it.k === 'lec'
      ? '<span class="dm' + (it.og === 'n' ? '' : ' kw') + '" title="'
        + (it.sj ? '旁白原始学科：' + it.sj : '转写无旁白句，领域按标题/正文关键词推断')
        + (it.og === 'm' ? '（关键词判错，已手工修正）' : '') + '">' + it.g + '</span>'
      : '';
    el.innerHTML = '<span class="tag ' + it.k + '">' + (it.k === 'conv' ? '对话' : '讲座') + '</span>'
      + '<span class="nm">' + label(it) + ' ' + it.t + '</span>'
      + (S.done[it.i] ? '<span class="ok">✓</span>' : '') + dm + era_
      + '<span class="du">' + fmt(it.d) + '</span>';
    el.onclick = () => select(it.i, true);
    list.appendChild(el);
  });
  if (document.body.classList.contains('showprog')) renderProg();
}

// 进度面板：领域 × 已听/总数。点领域名直接筛到该领域的未听条目。
function renderProg() {
  const order = DOMS.concat(domCount['校园对话'] ? ['校园对话'] : []);
  let tD = 0, tT = 0, tSec = 0, tSecD = 0;
  let rows = '';
  order.forEach(d => {
    const L = ITEMS.filter(x => x.g === d);
    const dn = L.filter(x => S.done[x.i]).length;
    const sec = L.reduce((a, x) => a + x.d, 0);
    const secD = L.filter(x => S.done[x.i]).reduce((a, x) => a + x.d, 0);
    tD += dn; tT += L.length; tSec += sec; tSecD += secD;
    const pct = L.length ? 100 * dn / L.length : 0;
    rows += '<tr><td><a data-dom="' + d + '">' + d + '</a></td>'
      + '<td class="n">' + dn + ' / ' + L.length + '</td>'
      + '<td><span class="bar"><i style="width:' + pct.toFixed(0) + '%"></i></span> ' + pct.toFixed(0) + '%</td>'
      + '<td class="n">' + ((sec - secD) / 3600).toFixed(1) + ' h</td></tr>';
  });
  const pctAll = tT ? 100 * tD / tT : 0;
  $('prog').innerHTML = '<table><tr><th>领域</th><th class="n">已听 / 总</th><th>进度</th>'
    + '<th class="n">剩余时长</th></tr>' + rows
    + '<tr class="tot"><td>合计</td><td class="n">' + tD + ' / ' + tT + '</td>'
    + '<td><span class="bar"><i style="width:' + pctAll.toFixed(0) + '%"></i></span> ' + pctAll.toFixed(0) + '%</td>'
    + '<td class="n">' + ((tSec - tSecD) / 3600).toFixed(1) + ' h</td></tr></table>';
  $('prog').querySelectorAll('a[data-dom]').forEach(a => {
    a.onclick = () => { $('fg').value = a.dataset.dom; $('fd').value = 'todo'; render(); };
  });
}

function select(i, play) {
  const it = ITEMS.find(x => x.i === i);
  if (!it) return;
  cur = it; S.last = i; save();
  $('tt').textContent = '第 ' + it.n + ' 套 · ' + (it.k === 'conv' ? '对话' : '讲座') + it.q + ' — ' + it.t;
  const eraTxt = it.y
    ? '出题时间 ' + it.y + (it.yq ? '（版本有冲突，仅供参考）' : '')
    : (it.r ? '出题时间未知 · 上线 ' + it.r : '年代未知');
  const sjTxt = it.k === 'lec'
    ? ' · ' + it.g + (it.sj ? '（' + it.sj + '）' : '（领域按关键词推断）')
    : ' · 校园对话';
  $('sub').textContent = eraTxt + sjTxt + ' · 共 ' + it.c.length + ' 句 · ' + fmt(it.d);
  $('sub').title = it.yn || '';
  au.src = it.a;
  cues = it.c; active = -1;
  txt.innerHTML = ''; nodes = [];
  cues.forEach((c, idx) => {
    const d = document.createElement('div');
    d.className = 'cue';
    d.innerHTML = '<div class="en"></div>' + (c[2] ? '<div class="zh"></div>' : '');
    d.querySelector('.en').textContent = c[1];
    if (c[2]) d.querySelector('.zh').textContent = c[2];
    d.onclick = () => { au.currentTime = c[0]; au.play(); };
    txt.appendChild(d); nodes.push(d);
  });
  const p = S.pos[i] || 0;
  au.onloadedmetadata = () => { if (p > 2 && p < au.duration - 3) au.currentTime = p; };
  if (play) au.play().catch(() => {});
  render();
}

au.addEventListener('timeupdate', () => {
  if (!cur) return;
  S.pos[cur.i] = au.currentTime;
  let lo = 0, hi = cues.length - 1, k = -1;
  while (lo <= hi) { const mid = (lo + hi) >> 1; if (cues[mid][0] <= au.currentTime + 0.25) { k = mid; lo = mid + 1; } else hi = mid - 1; }
  if (k !== active) {
    if (nodes[active]) nodes[active].classList.remove('on');
    active = k;
    if (nodes[k]) { nodes[k].classList.add('on'); nodes[k].scrollIntoView({ block: 'center', behavior: 'smooth' }); }
  }
});
let tick = 0;
au.addEventListener('timeupdate', () => { if (++tick % 40 === 0) save(); });
au.addEventListener('ended', () => { if (cur) { S.done[cur.i] = 1; save(); render(); } });

$('zh').onclick = () => { S.nozh = !S.nozh; document.body.classList.toggle('nozh', S.nozh); $('zh').textContent = S.nozh ? '显示中文' : '隐藏中文'; save(); };
$('mk').onclick = () => { if (!cur) return; S.done[cur.i] = S.done[cur.i] ? 0 : 1; save(); render(); };
$('pg').onclick = () => {
  S.prog = !S.prog;
  document.body.classList.toggle('showprog', S.prog);
  $('pg').textContent = S.prog ? '收起进度' : '进度';
  save();
  if (S.prog) renderProg();
};
['q', 'fk', 'fg', 'fd', 'fr', 'st'].forEach(id => $(id).addEventListener('input', render));
$('st').addEventListener('change', render);

// 从 200 集精选页搬「已听」标记。只增不减，重复点击安全（幂等）。
function selDone() {
  try {
    const st = JSON.parse(localStorage.getItem(SEL_KEY) || '{}');
    return st && st.done ? st.done : null;
  } catch (e) { return null; }
}
function refreshImp() {
  const d = selDone();
  if (!d) { $('imp').hidden = true; return; }
  const ids = Object.keys(d).filter(k => d[k] && MAP200[k]).map(k => MAP200[k]);
  const pending = ids.filter(i => !S.done[i]);
  $('imp').hidden = ids.length === 0;
  $('imp').textContent = pending.length ? '导入精选页进度（' + pending.length + ' 集）' : '精选页进度已同步';
  $('imp').disabled = pending.length === 0;
  $('imp').title = '精选页共有 ' + ids.length + ' 集标记为听完，其中 ' + pending.length + ' 集本页还没标记';
}
$('imp').onclick = () => {
  const d = selDone();
  if (!d) return;
  let n = 0;
  Object.keys(d).forEach(k => {
    const i = MAP200[k];
    if (d[k] && i && !S.done[i]) { S.done[i] = 1; n++; }
  });
  save(); refreshImp(); render();
  alert('已从精选页导入 ' + n + ' 集「听完」标记。');
};

document.body.classList.toggle('nozh', S.nozh);
$('zh').textContent = S.nozh ? '显示中文' : '隐藏中文';
document.body.classList.toggle('showprog', !!S.prog);
$('pg').textContent = S.prog ? '收起进度' : '进度';
refreshImp();
render();
if (S.last && ITEMS.find(x => x.i === S.last)) select(S.last, false);
</script>
</body>
</html>
"""

html = (HTML.replace("__DATA__", data_json)
        .replace("__MAP200__", json.dumps({str(k): v for k, v in sorted(map200.items())}, separators=(",", ":")))
        .replace("__SELKEY__", SEL_KEY))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"已生成 {OUT} ({os.path.getsize(OUT) / 1024 / 1024:.2f} MB)")
