#!/usr/bin/env python3
"""构建 GitHub Pages 版英语听力播放器（单文件，公开 CDN 直链，无鉴权）。
用法: python3 build_gh_player.py
输出: gh_listening_player.html（数据内嵌）
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "gh_player_data.json")
OUT = os.path.join(BASE, "gh_listening_player.html")

with open(DATA, encoding="utf-8") as f:
    payload = json.load(f)

# ---- 数据脱敏：去掉 TOEFL/TPO/Official 等暴露考试意图的字样 ----
_HTML_ENT = re.compile(r"&#0*39;|&#x27;")
for it in payload["items"]:
    # s: TPO-25_L4 -> 25-L4；直接去掉 TPO- 前缀
    it["s"] = it["s"].replace("TPO-", "", 1)
    # t: "Official 25 Set 2 Animal Play 动物的玩耍行为" -> "25 Set 2 Animal Play 动物的玩耍行为"
    it["t"] = re.sub(r"^Official\s+", "", it["t"])
    # 清理 HTML 实体
    it["t"] = _HTML_ENT.sub("'", it["t"])
    # yn（出题时间备注，会显示在 tooltip 里）同样脱敏
    if it.get("yn"):
        yn = it["yn"]
        for pat, rep in (
            (r"新东方在线|太原新东方|新东方", "某机构"),
            (r"TOEFL|Official|托福", ""),
            (r"ETS", "官方"),
            (r"TPO-?", ""),
        ):
            yn = re.sub(pat, rep, yn)
        it["yn"] = re.sub(r"\s{2,}", " ", yn).strip()
    # 移除未在 UI 使用的 KMF 页面链接（含 toefl.kmf.com，暴露意图）
    it.pop("p", None)
    # 移除匹配分字段（内部信息，非 UI 所需）
    it.pop("m", None)

data_json = json.dumps(payload, ensure_ascii=False)
n_items = len(payload["items"])
n_subs = len(payload["subs"])
print(f"数据: {n_items} 集, 字幕 {n_subs} 集, {len(data_json)/1024/1024:.2f} MB")

# 安全转义 </script>
data_json = data_json.replace("</", "<\\/")

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>英语听力精选 · 200 集</title>
<style>
:root {
  --bg: #f5f6f8; --panel: #ffffff; --accent: #2f6fed; --accent-dark: #1d4fc4;
  --text: #1a1d24; --muted: #6b7280; --border: #e3e6eb;
  --ok: #16a34a; --warn: #d97706; --hl: #fff8dc;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column;
}
header {
  background: var(--panel); border-bottom: 1px solid var(--border); padding: 10px 16px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; z-index: 10;
}
header h1 { font-size: 16px; font-weight: 700; margin-right: auto; white-space: nowrap; }
header h1 small { font-size: 12px; color: var(--muted); font-weight: 400; margin-left: 6px; }
.controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
select, input[type="search"], button {
  font-size: 13px; padding: 6px 10px; border: 1px solid var(--border); border-radius: 8px;
  background: #fff; color: var(--text); outline: none;
}
select:focus, input[type="search"]:focus { border-color: var(--accent); }
#searchBox { width: 200px; }
.btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); cursor: pointer; }
.btn-primary:hover { background: var(--accent-dark); }
.btn-primary:disabled { background: #9db8ee; cursor: default; }
main { flex: 1; display: flex; min-height: 0; }
#listPanel {
  width: 330px; min-width: 250px; background: var(--panel); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 8px;
}
#listPanel h2 { font-size: 12px; color: var(--muted); padding: 6px 6px 4px; }
.ep { display: flex; align-items: center; gap: 8px; padding: 7px 9px; border-radius: 8px; cursor: pointer; }
.ep:hover { background: #eef2fb; }
.ep.active { background: #e0e9fb; }
.ep .num { font-size: 11px; color: var(--muted); width: 30px; flex-shrink: 0; font-variant-numeric: tabular-nums; }
.ep .name { flex: 1; font-size: 13px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ep .exam { font-size: 11px; color: #7a4ec4; font-variant-numeric: tabular-nums; flex-shrink: 0; }
.ep .exam.guess { color: #a9a2b8; }
.ep .rel { font-size: 11px; color: #8a9299; font-variant-numeric: tabular-nums; flex-shrink: 0; }
.ep .date { font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
.ep .date.hot { color: var(--accent); font-weight: 700; }
.ep .dur { font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; flex-shrink: 0; }
#playerPanel { flex: 1; display: flex; flex-direction: column; min-width: 0; padding: 16px 22px; }
#nowTitle { font-size: 15px; font-weight: 700; margin-bottom: 2px; }
#nowSub { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
#audioWrap { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
audio { flex: 1; min-width: 240px; }
#progress { font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
#viewTabs { display: flex; gap: 6px; margin-bottom: 10px; }
#viewTabs button { font-size: 13px; padding: 5px 14px; border-radius: 8px; cursor: pointer; }
#viewTabs button.on { background: var(--accent); color: #fff; border-color: var(--accent); }
#capBox {
  flex: 1; overflow-y: auto; background: var(--panel); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 18px; line-height: 1.75; font-size: 15px; min-height: 0;
}
/* 长按选中复制：正文可选，时间戳/说话人不可选、不参与复制 */
.cue { padding: 6px 8px; border-radius: 6px; cursor: pointer; -webkit-user-select: text; user-select: text; -webkit-touch-callout: default; }
.cue .st, .cue .speaker { -webkit-user-select: none; user-select: none; -webkit-touch-callout: none; }
.cue:hover { background: #f1f4fb; }
.cue.on { background: var(--hl); outline: 1px solid #f0d98c; }
.cue .speaker { font-weight: 700; color: var(--accent); }
.cue .st { font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; margin-right: 8px; }
#transBox { display: none; flex: 1; overflow-y: auto; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; line-height: 1.9; font-size: 15px; white-space: pre-wrap; min-height: 0; }
#transBox .tr-line { padding: 3px 0; }
#transBox .tr-line.on { background: var(--hl); }
#hint { margin-top: 10px; font-size: 12px; color: var(--muted); line-height: 1.7; }
footer { font-size: 11px; color: var(--muted); text-align: center; padding: 7px; background: var(--panel); border-top: 1px solid var(--border); }
@media (max-width: 760px) {
  main { flex-direction: column; }
  #listPanel { width: 100%; max-height: 34vh; border-right: none; border-bottom: 1px solid var(--border); }
  #playerPanel { padding: 12px 14px; }
  #searchBox { width: 140px; }
  /* 手机端：播放器条吸顶，翻看逐句字幕时暂停键始终可见 */
  #audioWrap {
    position: sticky;
    top: 0;
    z-index: 30;
    background: var(--bg);
    padding: 10px 0;
    margin: -10px 0 10px;
    border-bottom: 1px solid var(--border);
  }
}
</style>
</head>
<body>
<header>
  <h1>英语听力精选 <small>200 集 · 免登录</small></h1>
  <div class="controls">
    <input type="search" id="searchBox" placeholder="搜索：编号、L1、C2、25、2009…">
    <select id="statusFilter">
      <option value="all">全部</option>
      <option value="done">仅已听完</option>
      <option value="played">仅已播放</option>
    </select>
    <select id="sortBy">
      <option value="idx">按编号</option>
      <option value="recent">最近播放</option>
      <option value="exam">按出题时间（新→旧）</option>
      <option value="examAsc">按出题时间（旧→新）</option>
    </select>
    <button id="prevBtn" class="btn-primary">上一集</button>
    <button id="nextBtn" class="btn-primary">下一集</button>
  </div>
</header>
<main>
  <div id="listPanel">
    <h2 id="listCount"></h2>
    <div id="epList"></div>
  </div>
  <div id="playerPanel">
    <div id="nowTitle">请选择一集开始播放</div>
    <div id="nowSub"></div>
    <div id="audioWrap">
      <audio id="player" controls preload="metadata"></audio>
      <div id="progress"></div>
    </div>
    <label for="endMode" style="font-size:13px;color:var(--muted);display:flex;align-items:center;gap:6px;margin-bottom:10px;">播放结束后
      <select id="endMode" style="font-size:13px;padding:5px 10px;border:1px solid var(--border);border-radius:8px;background:#fff;color:var(--text);outline:none;">
        <option value="stop">停止</option>
        <option value="next">播放下一个</option>
        <option value="loop">重播</option>
      </select>
    </label>
    <div style="font-size:13px;color:var(--muted);display:flex;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap;">
      播放范围
      <select id="rangeFrom" title="范围起点" style="font-size:13px;padding:5px 10px;border:1px solid var(--border);border-radius:8px;background:#fff;color:var(--text);outline:none;max-width:150px;"></select>
      <span>至</span>
      <select id="rangeTo" title="范围终点" style="font-size:13px;padding:5px 10px;border:1px solid var(--border);border-radius:8px;background:#fff;color:var(--text);outline:none;max-width:150px;"></select>
      <button id="clearRangeBtn" type="button" style="font-size:12px;padding:4px 10px;">清除</button>
    </div>
    <div id="viewTabs">
      <button id="tabSubs" class="on">逐句字幕</button>
      <button id="tabTrans">全文原文</button>
      <button id="copyTransBtn" type="button" title="复制全文" style="margin-left:auto;">复制全文</button>
    </div>
    <div id="capBox"></div>
    <div id="transBox"></div>
    <div id="hint">
      提示：单击左侧列表选集；字幕单击播放该句、双击复制该句；全文原文视图可一键"复制全文"；"播放结束后"设为"播放下一个"时，可配合"播放范围"只在指定编号区间内循环；
      列表会记录每集最后播放的日期，可按"最近播放"排序；播放进度自动保存在本地浏览器（localStorage）。共 200 集，编号越大越靠前（倒序）。<br>
      紫色小字是该集<b>听力部分的出题时间</b>（原始考试年月）；带 <b>?</b> 且显示为灰色的，是不同版本互相矛盾、仅供参考的值。
      灰色 <b>↑年份</b> 表示出题时间查无数据、只能给<b>上线时间</b>。两者都可用于排序和搜索（如输入 2009 或 2015）。<br>
      注意：一套题<b>不等于</b>一场考试——它是跨年份、跨科目的拼盘（已核实实例：第 71 套阅读来自 2016-03-19、口语来自 2014/2015/2017 年三场、综合写作来自 2013 年），
      所以这里的日期只代表<b>听力</b>。且这些日期全部来自民间整理的对照表，官方从未公布过套号与考期的对应。
    </div>
  </div>
</main>
<footer>共 <span id="footTotal">0</span> 集 · 已播放 <span id="footPlayed">0</span> 集 · 已听完 <span id="footDone">0</span> 集</footer>

<script>
const DATA = __DATA__;
const ITEMS = DATA.items;
const SUBS = DATA.subs;
const audio = document.getElementById('player');
const epList = document.getElementById('epList');
const listCount = document.getElementById('listCount');
const searchBox = document.getElementById('searchBox');
const statusFilter = document.getElementById('statusFilter');
const sortBy = document.getElementById('sortBy');
const nowTitle = document.getElementById('nowTitle');
const nowSub = document.getElementById('nowSub');
const progress = document.getElementById('progress');
const capBox = document.getElementById('capBox');
const transBox = document.getElementById('transBox');
const copyTransBtn = document.getElementById('copyTransBtn');
const rangeFromSel = document.getElementById('rangeFrom');
const rangeToSel = document.getElementById('rangeTo');
const clearRangeBtn = document.getElementById('clearRangeBtn');

let curIdx = null;
let viewMode = 'subs'; // subs | trans
const LS_KEY = 'en_listening_player';
let state = {};
try { state = JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch(e) { state = {}; }
if (!state.positions) state.positions = {};
if (!state.done) state.done = {};
if (!state.endMode) state.endMode = 'stop'; // stop | next | loop
if (!state.lastPlayed) state.lastPlayed = {}; // idx -> ISO 时间戳
if (!state.range) state.range = {}; // {from: idx|null, to: idx|null} 播放范围

function fmt(sec) {
  if (!isFinite(sec) || sec < 0) sec = 0;
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return m + ':' + String(s).padStart(2, '0');
}
function save() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch(e) {}
}

function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  if (sameDay) return '今天 ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
  const yesterday = new Date(now); yesterday.setDate(now.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return '昨天 ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
  const sameYear = d.getFullYear() === now.getFullYear();
  const md = (d.getMonth()+1) + '/' + d.getDate();
  const hm = String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
  return sameYear ? `${md} ${hm}` : `${d.getFullYear()}/${md} ${hm}`;
}

function itByIdx(idx) { return ITEMS.find(x => x.i === idx); }

/* ---------- 播放范围 ---------- */
function fillRangeSelects() {
  // 下拉选项倒序（编号大在前，与列表一致），仅用编号+简短名称
  const opts = ITEMS.slice().sort((a, b) => b.i - a.i).map(it =>
    `<option value="${it.i}">p${String(it.i).padStart(3,'0')} · ${it.s}</option>`);
  rangeFromSel.innerHTML = '<option value="">起点</option>' + opts.join('');
  rangeToSel.innerHTML = '<option value="">终点</option>' + opts.join('');
  // 恢复已保存的范围
  if (state.range && state.range.from) rangeFromSel.value = String(state.range.from);
  if (state.range && state.range.to) rangeToSel.value = String(state.range.to);
}
function rangeBounds() {
  // 返回 [lo, hi] 编号区间；未设置范围返回 null
  const r = state.range || {};
  const from = r.from, to = r.to;
  if (!from && !to) return null;
  const lo = from && to ? Math.min(from, to) : (from || to);
  const hi = from && to ? Math.max(from, to) : (from || to);
  return [lo, hi];
}
function inRange(idx) {
  const b = rangeBounds();
  if (!b) return true;
  return idx >= b[0] && idx <= b[1];
}
function saveRange() {
  const r = state.range || {};
  if (!r.from && !r.to) delete state.range;
  save();
}
rangeFromSel.addEventListener('change', () => {
  state.range = state.range || {};
  state.range.from = rangeFromSel.value ? Number(rangeFromSel.value) : null;
  saveRange();
});
rangeToSel.addEventListener('change', () => {
  state.range = state.range || {};
  state.range.to = rangeToSel.value ? Number(rangeToSel.value) : null;
  saveRange();
});
clearRangeBtn.addEventListener('click', () => {
  delete state.range;
  rangeFromSel.value = '';
  rangeToSel.value = '';
  save();
});

function filtered() {
  const q = searchBox.value.trim().toLowerCase();
  const st = statusFilter.value;
  let list = ITEMS.filter(it => {
    const hay = (it.i + ' ' + it.s + ' ' + it.t + ' ' + (it.y || '') + ' ' + (it.r || '')).toLowerCase();
    if (q && !hay.includes(q)) return false;
    if (st === 'done' && !state.done[it.i]) return false;
    if (st === 'played' && !state.lastPlayed[it.i]) return false;
    return true;
  });
  if (sortBy.value === 'recent') {
    list = list.slice().sort((a, b) => {
      const ta = state.lastPlayed[a.i] || 0;
      const tb = state.lastPlayed[b.i] || 0;
      // 未播放的排最后；已播放的按时间新->旧
      if (!ta && !tb) return 0;
      if (!ta) return 1;
      if (!tb) return -1;
      return tb.localeCompare(ta);
    });
  } else if (sortBy.value === 'exam' || sortBy.value === 'examAsc') {
    // 按年代排序：优先用出题时间，没有的退回上线时间（去掉 ≤ 等前缀再比）；两者都无的排最后
    const desc = sortBy.value === 'exam';
    const dkey = it => it.y || (it.r ? String(it.r).replace(/[^0-9-]/g, '') : '');
    list = list.slice().sort((a, b) => {
      const ya = dkey(a), yb = dkey(b);
      if (!ya && !yb) return a.i - b.i;
      if (!ya) return 1;
      if (!yb) return -1;
      if (ya !== yb) return desc ? yb.localeCompare(ya) : ya.localeCompare(yb);
      return a.i - b.i;
    });
  }
  return list;
}

function render() {
  const list = filtered();
  listCount.textContent = `共 ${list.length} 集`;
  epList.innerHTML = '';
  const now = Date.now();
  for (const it of list) {
    const div = document.createElement('div');
    div.className = 'ep' + (it.i === curIdx ? ' active' : '');
    const mark = state.done[it.i] ? ' ✓' : '';
    const lp = state.lastPlayed[it.i];
    const dateStr = fmtDate(lp);
    // 今天播放过的显示高亮
    const hot = lp && new Date(lp).toDateString() === new Date().toDateString() ? ' hot' : '';
    div.innerHTML = `<span class="num">p${String(it.i).padStart(3,'0')}</span><span class="name">${it.s}${mark}</span>${it.y ? `<span class="exam${it.yq ? ' guess' : ''}" title="出题时间 ${it.y}${it.yq ? '（版本有冲突，仅供参考）' : ''}${it.yn ? '\\n' + it.yn : ''}">${it.y}${it.yq ? '?' : ''}</span>` : (it.r ? `<span class="rel" title="出题时间查无数据；这是上线时间 ${it.r}${it.yn ? '\\n' + it.yn : ''}">↑${it.r}</span>` : '')}${dateStr ? `<span class="date${hot}">${dateStr}</span>` : ''}<span class="dur">${fmt(it.d)}</span>`;
    div.onclick = () => select(it.i, true);
    epList.appendChild(div);
  }
  const doneN = Object.keys(state.done).length;
  const playedN = Object.keys(state.lastPlayed).length;
  document.getElementById('footTotal').textContent = ITEMS.length;
  document.getElementById('footDone').textContent = doneN;
  const footPlayed = document.getElementById('footPlayed');
  if (footPlayed) footPlayed.textContent = playedN;
}

function select(idx, autoplay) {
  const it = itByIdx(idx);
  if (!it) return;
  curIdx = idx;
  state.lastIdx = idx;
  save();
  nowTitle.textContent = `p${String(idx).padStart(3,'0')} · ${it.s}`;
  const examTxt = it.y
    ? `出题时间 ${it.y}${it.yq ? '（版本有冲突，仅供参考）' : ''}`
    : (it.r ? `出题时间查无数据 · 上线 ${it.r}` : (it.yn ? `出题时间未知` : ''));
  nowSub.textContent = [it.t || '', examTxt, `时长 ${fmt(it.d)}`].filter(Boolean).join(' · ');
  nowSub.title = it.yn || '';
  audio.src = it.a;
  if (autoplay) {
    // 若上次的浮标已停在末尾（或接近末尾），说明该集已听完：从头播放，
    // 避免一加载就触发 ended，导致自动播放时每集都在末尾"闪现"、最终无一集在播
    let pos = state.positions[idx] || 0;
    if (pos > 0 && it.d > 0 && pos >= it.d - 0.5) pos = 0;
    audio.currentTime = pos;
    audio.play().catch(() => {});
  }
  renderCues();
  renderTranscript();
  render();
  capBox.scrollTop = 0;
}

/* ---------- 字幕 ---------- */
function cueTime(c) {
  return `${fmt(c[0])} – ${fmt(c[1])}`;
}
function speakerColor(s) {
  const sp = (s || '').toLowerCase();
  if (sp.includes('professor') || sp.includes('instructor')) return '#b34700';
  if (sp.includes('student')) return '#1a6e42';
  if (sp.includes('narrator')) return '#5b5bd6';
  if (sp.includes('male')) return '#1a5f9e';
  if (sp.includes('female')) return '#a11f6e';
  return '#7a2fbf';
}
function speakerName(s) {
  if (!s) return '';
  const m = s.match(/^([A-Z][A-Z ]+):/);
  return m ? m[1] : '';
}

function cueCleanText(c) {
  // 单句干净文本：去掉时间戳与说话人前缀
  const sp = speakerName(c[2]);
  const rest = sp ? c[2].slice(sp.length + 1).trim() : c[2];
  return rest.replace(/\\s+/g, ' ').trim();
}

function renderCues() {
  const cues = SUBS[String(curIdx)] || SUBS[curIdx] || [];
  capBox.innerHTML = '';
  if (!cues.length) {
    capBox.innerHTML = '<div class="cue" style="color:var(--muted)">本集暂无字幕</div>';
    return;
  }
  cues.forEach((c, i) => {
    const div = document.createElement('div');
    div.className = 'cue';
    const sp = speakerName(c[2]);
    const rest = sp ? c[2].slice(sp.length + 1).trim() : c[2];
    div.innerHTML = `<span class="st">${cueTime(c)}</span>${sp ? `<span class="speaker" style="color:${speakerColor(sp)}">${sp}:</span> ` : ''}${rest}`;
    // 单击 = 播放该句；双击 = 复制整句（250ms 内第二次点击判定为双击）
    let clickTimer = null;
    div.addEventListener('click', (e) => {
      e.preventDefault();
      if (clickTimer) {
        // 双击：取消单击播放，复制整句
        clearTimeout(clickTimer);
        clickTimer = null;
        copyText(cueCleanText(c), { toast: '已复制该句 ✓' });
        return;
      }
      clickTimer = setTimeout(() => {
        clickTimer = null;
        if (hasSelection()) return;
        audio.currentTime = c[0];
        if (audio.paused) audio.play().catch(() => {});
      }, 250);
    });
    div.dataset.i = i;
    capBox.appendChild(div);
  });
  updateCueHighlight();
}

/* ---------- 选区检测 ---------- */
function hasSelection() {
  const sel = window.getSelection();
  return !!sel && sel.toString().trim().length > 0;
}
/* ---------- 复制 ---------- */
function copyText(t, opts) {
  opts = opts || {};
  const done = () => toast(opts.toast || '已复制 ✓');
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(t).then(done, () => fallbackCopy(t, done));
  } else {
    fallbackCopy(t, done);
  }
}
function toast(msg) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.style.cssText = 'position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:rgba(34,38,47,.92);color:#fff;padding:8px 16px;border-radius:8px;font-size:13px;z-index:60;pointer-events:none;transition:opacity .25s;';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.opacity = '1';
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.style.opacity = '0'; }, 1200);
}
function fallbackCopy(t, done) {
  const ta = document.createElement('textarea');
  ta.value = t;
  ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0;';
  document.body.appendChild(ta);
  ta.focus(); ta.select();
  try { document.execCommand('copy'); } catch (e) {}
  document.body.removeChild(ta);
  done();
}

function updateCueHighlight() {
  const cues = SUBS[String(curIdx)] || SUBS[curIdx] || [];
  if (!cues.length || !curIdx) return;
  let onIdx = -1;
  const t = audio.currentTime;
  for (let i = 0; i < cues.length; i++) {
    if (t >= cues[i][0] && t < cues[i][1]) { onIdx = i; break; }
  }
  const kids = capBox.children;
  for (let i = 0; i < kids.length; i++) {
    kids[i].classList.toggle('on', i === onIdx);
  }
  if (onIdx >= 0) {
    // 用户正在长按选中文字：不自动滚动，避免打断选择
    if (hasSelection()) return;
    const el = kids[onIdx];
    const box = capBox.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    if (r.top < box.top || r.bottom > box.bottom) el.scrollIntoView({ block: 'nearest' });
  }
}

/* ---------- 原文 ---------- */
function renderTranscript() {
  const it = itByIdx(curIdx);
  if (!it) { transBox.innerHTML = ''; return; }
  const lines = it.tr && it.tr.length ? it.tr : ['（暂无原文）'];
  transBox.innerHTML = '';
  lines.forEach((ln, i) => {
    const div = document.createElement('div');
    div.className = 'tr-line';
    const m = ln.match(/^([A-Z][A-Z ]+?):\\s*(.*)$/);
    if (m) {
      div.innerHTML = `<span class="speaker" style="color:${speakerColor(m[1])};font-weight:700">${m[1]}:</span> ${m[2]}`;
    } else {
      div.textContent = ln;
    }
    div.dataset.i = i;
    transBox.appendChild(div);
  });
}

/* ---------- 视图切换 ---------- */
function setView(mode) {
  viewMode = mode;
  document.getElementById('tabSubs').classList.toggle('on', mode === 'subs');
  document.getElementById('tabTrans').classList.toggle('on', mode === 'trans');
  capBox.style.display = mode === 'subs' ? 'block' : 'none';
  transBox.style.display = mode === 'trans' ? 'block' : 'none';
  copyTransBtn.style.display = mode === 'trans' ? 'inline-block' : 'none';
  if (mode === 'trans' && curIdx) renderTranscript();
}

function transcriptCleanText() {
  const it = itByIdx(curIdx);
  if (!it) return '';
  const lines = it.tr && it.tr.length ? it.tr : [];
  return lines.map(ln => {
    const m = ln.match(/^([A-Z][A-Z ]+?):\\s*(.*)$/);
    return m ? m[2].trim() : ln.trim();
  }).join('\\n');
}

copyTransBtn.addEventListener('click', () => {
  const t = transcriptCleanText();
  if (!t) { toast('暂无原文'); return; }
  copyText(t, { toast: '已复制全文 ✓' });
});

document.getElementById('tabSubs').onclick = () => setView('subs');
document.getElementById('tabTrans').onclick = () => setView('trans');

/* ---------- 播放事件 ---------- */
audio.addEventListener('play', () => {
  if (curIdx) {
    state.lastPlayed[curIdx] = new Date().toISOString();
    save();
    render();
  }
});
audio.addEventListener('timeupdate', () => {
  progress.textContent = `${fmt(audio.currentTime)} / ${fmt(audio.duration || 0)}`;
  if (curIdx) state.positions[curIdx] = audio.currentTime;
  save();
  updateCueHighlight();
});
audio.addEventListener('loadedmetadata', () => {
  progress.textContent = `0:00 / ${fmt(audio.duration || 0)}`;
});
const endModeSel = document.getElementById('endMode');
endModeSel.value = state.endMode;
endModeSel.addEventListener('change', () => {
  state.endMode = endModeSel.value;
  save();
});

audio.addEventListener('ended', () => {
  if (curIdx) {
    state.done[curIdx] = 1;
    // 听完后清除进度浮标，下次自动播放从开头开始，而不是停在末尾
    delete state.positions[curIdx];
    save(); render();
  }
  const mode = state.endMode;
  if (mode === 'loop') {
    audio.currentTime = 0;
    audio.play().catch(() => {});
    return;
  }
  if (mode === 'next') {
    const list = filtered().filter(x => inRange(x.i));  // 只在范围内找下一集
    const i = list.findIndex(x => x.i === curIdx);
    if (i >= 0 && i < list.length - 1) {
      select(list[i+1].i, true);      // 范围内下一集
    } else if (i >= 0 && list.length > 1) {
      select(list[0].i, true);        // 范围末尾 -> 回到范围开头（循环）
    } else if (i < 0) {
      // 当前集不在范围内：按完整列表推进
      const full = filtered();
      const j = full.findIndex(x => x.i === curIdx);
      if (j >= 0 && j < full.length - 1) select(full[j+1].i, true);
      else audio.currentTime = 0;     // 已是最后一集：回到开头停止
    } else {
      audio.currentTime = 0;          // 范围内只有一集：重播当前集
    }
    return;
  }
  // stop：什么都不做（已标记听完）
});

document.getElementById('prevBtn').onclick = () => {
  const list = filtered();
  const i = list.findIndex(x => x.i === curIdx);
  if (i > 0) select(list[i-1].i, true);
};
document.getElementById('nextBtn').onclick = () => {
  const list = filtered();
  const i = list.findIndex(x => x.i === curIdx);
  if (i >= 0 && i < list.length - 1) select(list[i+1].i, true);
};
searchBox.addEventListener('input', render);
statusFilter.addEventListener('change', render);
sortBy.addEventListener('change', render);

fillRangeSelects();
render();
setView('subs');
// 恢复上次播放
const last = state.lastIdx;
if (last && itByIdx(last)) select(last, false);
</script>
</body>
</html>
"""

html = html.replace("__DATA__", data_json)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"已生成 {OUT} ({os.path.getsize(OUT)/1024/1024:.2f} MB)")
