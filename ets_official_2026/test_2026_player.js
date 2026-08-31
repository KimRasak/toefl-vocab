// 2026 新格式听力练习页的无头回归测试。
// 和 TPO_listening/test_player.js 同一套路：极简 DOM 打桩 + vm 里跑页面脚本 + 断言。
// 用法: node test_2026_player.js   （退出码非 0 即失败）
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');

class El {
  constructor(tag) {
    this.tag = tag; this.children = []; this._html = ''; this.style = {}; this.dataset = {};
    this.value = ''; this.textContent = ''; this.className = ''; this.hidden = false;
    this._cls = new Set();
    this.classList = {
      add: c => this._cls.add(c),
      remove: c => this._cls.delete(c),
      toggle: (c, v) => { v === undefined ? (this._cls.has(c) ? this._cls.delete(c) : this._cls.add(c)) : (v ? this._cls.add(c) : this._cls.delete(c)); },
      contains: c => this._cls.has(c),
    };
  }
  set innerHTML(v) { this._html = v; if (v === '') this.children = []; }
  get innerHTML() { return this._html; }
  appendChild(c) { this.children.push(c); return c; }
  addEventListener(ev, fn) { (this._ev = this._ev || {})[ev] = fn; }
  // 选项点击：从 innerHTML 里把 data-q / data-k 还原成可点的元素
  querySelectorAll(sel) {
    const out = [];
    if (/\.opt/.test(sel)) {
      for (const m of this._html.matchAll(/data-q="(\d+)" data-k="([A-D])"/g)) {
        const e = new El('div'); e.dataset.q = m[1]; e.dataset.k = m[2]; out.push(e);
      }
    }
    return out;
  }
}
const ids = {};
for (const id of ['cnt', 'ft', 'fm', 'fd', 'cdsel', 'tt', 'sb', 'rs', 'tabs', 'list', 'stage',
  'hd', 'dr', 'ctl', 'pl', 'pd', 'cdwrap', 'cd', 'cdtxt', 'plays', 'err', 'qs', 'trbox', 'stats', 'banner']) ids[id] = new El(id);
globalThis.ids = ids;
globalThis.document = {
  getElementById: id => ids[id] || (ids[id] = new El(id)),
  createElement: t => new El(t),
  body: new El('body'),
  addEventListener: () => {},
};
globalThis.localStorage = { getItem: () => null, setItem: () => {} };
globalThis.confirm = () => true;
globalThis.fetch = () => Promise.resolve({ ok: true });
globalThis.location = { protocol: "http:" };
// Audio 打桩：记录 src，play() 立刻 resolve，onended 由测试手工触发
class FakeAudio {
  constructor() { this.src = ''; this.currentTime = 0; this.onended = null; this._played = 0; }
  play() { this._played++; return Promise.resolve(); }
  pause() {}
}
globalThis.Audio = FakeAudio;
globalThis.setInterval = () => 0;
globalThis.clearInterval = () => {};
globalThis.RESULTS = [];
globalThis.chk = (name, cond, extra) => {
  globalThis.RESULTS.push((cond ? 'ok   ' : 'FAIL ') + name + (extra !== undefined ? '  ' + extra : ''));
};
// 打桩的 appendChild 不会把子节点内容并进父节点的 innerHTML，
// 而页面是「先清空父节点、再 appendChild 一堆子 div」的写法，
// 所以断言里要看整棵子树的 HTML，得用这个聚合函数。
globalThis.htmlOf = el => (el.innerHTML || '') + (el.children || []).map(globalThis.htmlOf).join('');
globalThis.tick = () => new Promise(r => setImmediate(r));

const html = fs.readFileSync(path.join(__dirname, '..', 'listening-2026', 'index.html'), 'utf8');
const m = /<script>([\s\S]*)<\/script>/.exec(html);
if (!m) { console.error('找不到页面 <script>'); process.exit(2); }
const page = m[1].replace(/<\\\//g, '</');

const ASSERTS = 'globalThis.__T = (async () => {' + String.raw`
chk('161 个音频条目', ITEMS.length === 161, ITEMS.length);
const NQ = ITEMS.reduce((a, x) => a + x.qs.length, 0);
chk('238 道题', NQ === 238, NQ);
chk('meta 里的题数一致', DATA.meta.nq === 238, DATA.meta.nq);
chk('四类题型', KINDS.length === 4, KINDS.map(k => k.n).join('/'));
chk('7 套卷', TESTS.length === 7, TESTS.length);
chk('每条都有音频', ITEMS.every(x => x.au));
chk('每条都有时长', ITEMS.every(x => typeof x.d === 'number' && x.d > 0));
chk('每题都有答案且在 ABCD 内', ITEMS.every(x => x.qs.every(q => 'ABCD'.includes(q.a))));
chk('每题都有 4 个选项', ITEMS.every(x => x.qs.every(q => Object.keys(q.o).length === 4)));
chk('正确答案在选项里', ITEMS.every(x => x.qs.every(q => q.o[q.a] !== undefined)));
chk('听答题 112 条', ITEMS.filter(x => x.k === 'cr').length === 112, ITEMS.filter(x => x.k === 'cr').length);
chk('听答题每条 1 题', ITEMS.filter(x => x.k === 'cr').every(x => x.qs.length === 1));
chk('学术讲座 14 条 / 56 题',
    ITEMS.filter(x => x.k === 'at').length === 14
    && ITEMS.filter(x => x.k === 'at').reduce((a, x) => a + x.qs.length, 0) === 56);
chk('题号在各卷内不重复', TESTS.every(t => {
  const ns = ITEMS.filter(x => x.t === t.c).flatMap(x => x.qs.map(q => x.m + '-' + q.n));
  return new Set(ns).size === ns.length;
}));

// 默认打开听答题这一 tab
chk('默认 tab 是听答题', S.tab === 'cr', S.tab);
chk('tab 栏 4 个按钮', ids.tabs.children.length === 4, ids.tabs.children.length);

// 选一条听答题做答
const cr = ITEMS.find(x => x.k === 'cr');
open(cr);
chk('打开后播放了音频', au._played === 1, au._played);
await tick();
chk('播放次数计入', S.plays[cr.id] === 1, S.plays[cr.id]);
chk('未答时不显示原文', ids.trbox.className === '', '[' + ids.trbox.className + ']');
chk('选项渲染出 4 个', (htmlOf(ids.qs).match(/data-k="/g) || []).length === 4);
answer(cr.qs[0], cr.qs[0].a);
chk('答对被判对', S.ans[cr.id + '#' + cr.qs[0].n] === cr.qs[0].a);
chk('答完自动显示原文', ids.trbox.className === 'on', '[' + ids.trbox.className + ']');
chk('原文含听到的那句', ids.trbox.innerHTML.includes(cr.tr[0].slice(0, 20).replace(/[&<>"]/g, '')));
chk('答对后判定文案', htmlOf(ids.qs).includes('答对'));

// 答错
const cr2 = ITEMS.filter(x => x.k === 'cr')[1];
open(cr2);
const wrongKey = 'ABCD'.split('').find(k => k !== cr2.qs[0].a);
answer(cr2.qs[0], wrongKey);
chk('答错文案带正确答案', htmlOf(ids.qs).includes('答错 · 正确答案 ' + cr2.qs[0].a));
chk('答过的题不能改', (() => { answer(cr2.qs[0], cr2.qs[0].a); return S.ans[cr2.id + '#' + cr2.qs[0].n] === wrongKey; })());

// 超时：模拟 onended 后倒计时到点（这里直接写入 _TO_ 走同一条渲染路径）
const cr3 = ITEMS.filter(x => x.k === 'cr')[2];
open(cr3);
S.ans[cr3.id + '#' + cr3.qs[0].n] = '_TO_';
renderQs();
chk('超时文案', htmlOf(ids.qs).includes('超时未答 · 正确答案 ' + cr3.qs[0].a));

// 筛选
ids.fd.value = 'todo';
chk('仅未做筛掉已做的 3 条', pool().length === 112 - 3, pool().length);
ids.fd.value = 'wrong';
chk('仅错过筛出 2 条（答错 + 超时）', pool().length === 2, pool().length);
ids.fd.value = 'done';
chk('仅做过筛出 3 条', pool().length === 3, pool().length);
ids.fd.value = '';
ids.fm.value = '1';
chk('Module 1 听答题 56 条', pool().length === 56, pool().length);
ids.fm.value = '';
ids.ft.value = 's1';
chk('学生卷 1 的听答题 16 条', pool().length === 16, pool().length);
ids.ft.value = '';

// 多题条目：讲座
const at = ITEMS.find(x => x.k === 'at');
S.tab = 'at';
open(at);
chk('讲座有 3-4 题', at.qs.length >= 3, at.qs.length);
chk('讲座未答完不显示原文', ids.trbox.className === '', '[' + ids.trbox.className + ']');
at.qs.slice(0, at.qs.length - 1).forEach(q => answer(q, q.a));
chk('只答了一部分仍不显示原文', ids.trbox.className === '', '[' + ids.trbox.className + ']');
answer(at.qs[at.qs.length - 1], at.qs[at.qs.length - 1].a);
chk('全部答完才显示原文', ids.trbox.className === 'on', '[' + ids.trbox.className + ']');
chk('条目算作已做', isDone(at));
chk('全对计数正确', nRight(at) === at.qs.length, nRight(at));

// 手动显示原文
S.tab = 'cr';
const cr4 = ITEMS.filter(x => x.k === 'cr')[3];
open(cr4);
chk('新条目默认不显原文', ids.trbox.className === '');
S.showTr = true; renderTr();
chk('手动打开原文有警示', ids.trbox.innerHTML.includes('注意别提前看'));
S.showTr = false; renderTr();

// 成绩面板
document.body.classList.add('showstats');
renderStats();
chk('成绩表有合计行', ids.stats.innerHTML.includes('合计'));
chk('成绩表统计到超时 1 次', /<td><b>1<\/b><\/td>/.test(ids.stats.innerHTML) || ids.stats.innerHTML.includes('>1</td>'));

// 重置本类
S.tab = 'at';
const atCount = ITEMS.filter(x => x.k === 'at').length;
document.getElementById('rs').onclick();
chk('重置后讲座类无记录', ITEMS.filter(x => x.k === 'at').every(x => x.qs.every(q => !S.ans[x.id + '#' + q.n])));
chk('重置不影响听答题记录', S.ans[cr.id + '#' + cr.qs[0].n] === cr.qs[0].a);

// 音频缺失横幅：把 fetch 换成 404 再跑一次探测
chk('音频可取时不显示横幅', ids.banner.className === '', '[' + ids.banner.className + ']');
globalThis.fetch = () => Promise.resolve({ ok: false });
await probeAudio();
chk('音频 404 时弹出横幅', ids.banner.className === 'on', '[' + ids.banner.className + ']');
chk('横幅写明本地解压办法', ids.banner.innerHTML.includes('extract_audio.py'));
chk('横幅说明文本题仍可用', ids.banner.innerHTML.includes('原文都能用'));
`+ '})();';

vm.runInThisContext(page + '\n' + ASSERTS, { filename: 'listening-2026.js' });

globalThis.__T.then(() => {
  console.log(globalThis.RESULTS.join('\n'));
  const bad = globalThis.RESULTS.filter(x => x.startsWith('FAIL'));
  console.log(`\n${globalThis.RESULTS.length - bad.length}/${globalThis.RESULTS.length} 通过`);
  process.exit(bad.length ? 1 : 0);
}).catch(e => { console.error(e); process.exit(2); });
