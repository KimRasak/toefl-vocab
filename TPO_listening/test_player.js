// 全库播放器的无头回归测试。
// 做法：把播放器 <script> 原样抠出来，前面挂一个极简 DOM 打桩（全部挂到 globalThis，
// 这样 vm.runInThisContext 里的代码才能看到），后面拼上断言，一起交给 vm 跑。
// 不用 jsdom 是因为播放器只用到十来个 DOM API，打桩比引依赖便宜。
// 用法: node test_player.js   （退出码非 0 即失败）
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');

// ---- 极简 DOM 打桩 ----
class El {
  constructor(tag) {
    this.tag = tag; this.children = []; this._html = ''; this.style = {}; this.dataset = {};
    this._cls = new Set(); this.value = ''; this.textContent = ''; this.title = '';
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
  addEventListener() {}
  querySelector() { return new El('x'); }
  querySelectorAll(sel) {
    const out = [];
    if (/a\[data-dom\]/.test(sel)) {
      for (const m of this._html.matchAll(/data-dom="([^"]+)"/g)) {
        const e = new El('a'); e.dataset.dom = m[1]; out.push(e);
      }
    }
    return out;
  }
  scrollIntoView() {}
  play() { return Promise.resolve(); }
}
const ids = {};
for (const id of ['list', 'au', 'txt', 'cnt', 'q', 'fk', 'fg', 'fd', 'fr', 'st', 'zh', 'mk', 'pg', 'prog', 'tt', 'sub', 'empty']) ids[id] = new El(id);
ids.st.value = 'num';
globalThis.ids = ids;
globalThis.document = {
  getElementById: id => ids[id] || (ids[id] = new El(id)),
  createElement: t => new El(t),
  body: new El('body'),
};
globalThis.localStorage = {
  getItem: k => (k === 'en_listening_player' ? JSON.stringify(globalThis.SEL_STATE) : null),
  setItem: () => {},
};
// 模拟「精选页已听完 p1–p121」这一真实状态，用来验证进度迁移
globalThis.SEL_STATE = { done: {} };
for (let i = 1; i <= 121; i++) globalThis.SEL_STATE.done[i] = 1;
globalThis.alert = () => {};
globalThis.RESULTS = [];
globalThis.chk = (name, cond, extra) => {
  globalThis.RESULTS.push((cond ? 'ok   ' : 'FAIL ') + name + (extra !== undefined ? '  ' + extra : ''));
};

// ---- 载入播放器脚本 + 断言，同一个作用域执行 ----
const html = fs.readFileSync(path.join(__dirname, 'gh_full_player.html'), 'utf8');
const m = /<script>([\s\S]*)<\/script>/.exec(html);
if (!m) { console.error('找不到播放器 <script>'); process.exit(2); }
const player = m[1].replace(/<\\\//g, '</');

const ASSERTS = String.raw`
chk('424 集', ITEMS.length === 424, ITEMS.length);
chk('每集都有领域', ITEMS.every(x => x.g));
chk('没有落到「其他」的', ITEMS.filter(x => x.g === '其他').length === 0);
chk('讲座都带学科来源标记', ITEMS.filter(x => x.k === 'lec').every(x => x.og));
chk('领域下拉 12 项', ids.fg.children.length === 12, ids.fg.children.length);
chk('校园对话排最后', ids.fg.children[ids.fg.children.length - 1].value === '校园对话');

ids.fg.value = '艺术/音乐/文学/戏剧';
chk('艺术类筛出 66 集', filtered().length === 66, filtered().length);
ids.fd.value = 'todo';
chk('全新状态下未听 = 66', filtered().length === 66, filtered().length);
ids.fd.value = 'done';
chk('全新状态下已听 = 0', filtered().length === 0, filtered().length);
const art = ITEMS.filter(x => x.g === '艺术/音乐/文学/戏剧');
S.done[art[0].i] = 1; S.done[art[1].i] = 1;
chk('标记两集后已听 = 2', filtered().length === 2, filtered().length);
ids.fd.value = 'todo';
chk('标记两集后未听 = 64', filtered().length === 64, filtered().length);

ids.fg.value = ''; ids.fd.value = '';
const it75 = ITEMS.find(x => x.n === 75), it1 = ITEMS.find(x => x.n === 1);
chk('第 75 套组标题写明出题时间未知',
    grpLabel(it75) === '第 75 套 · 上线 2022-12-27 · 出题时间未知', grpLabel(it75));
chk('有出题时间的套仍显示出题时间', grpLabel(it1).indexOf('出题 2005-11-05') > 0, grpLabel(it1));

ids.st.value = 'dom';
const L = filtered();
chk('按领域排序首组是艺术', L[0].g === '艺术/音乐/文学/戏剧', L[0].g);
chk('按领域排序末组是校园对话', L[L.length - 1].g === '校园对话', L[L.length - 1].g);
chk('按领域排序不丢条目', L.length === 424, L.length);

ids.st.value = 'num';
ids.q.value = 'art history';
chk('可按旁白学科搜索', filtered().length > 0, filtered().length);
ids.q.value = '考古';
chk('可按中文领域搜索（考古 24 集）', filtered().length === 24, filtered().length);
ids.q.value = '';

document.body.classList.add('showprog');
renderProg();
chk('进度表渲染出合计行', ids.prog.innerHTML.includes('合计'));
chk('进度表 12 行', (ids.prog.innerHTML.match(/data-dom=/g) || []).length === 12);
chk('进度表算出 2 / 66', ids.prog.innerHTML.includes('2 / 66'));
render();
chk('标题栏显示已听数', ids.cnt.textContent.includes('已听 2'), ids.cnt.textContent);

// ---- 精选页进度迁移 ----
chk('迁移表 200 条', Object.keys(MAP200).length === 200, Object.keys(MAP200).length);
S.done = {};
refreshImp();
chk('导入按钮可见', ids.imp.hidden === false);
chk('导入按钮标出 121 集待导入', ids.imp.textContent === '导入精选页进度（121 集）', ids.imp.textContent);
$('imp').onclick();
const dn = ITEMS.filter(x => S.done[x.i]);
chk('导入后已听 121 集', dn.length === 121, dn.length);
const dSets = [...new Set(dn.map(x => x.n))].sort((a, b) => a - b);
chk('导入的 121 集落在第 5–25 套', dSets[0] === 5 && dSets[dSets.length - 1] === 25, dSets.join(','));
chk('第 5 套只导入 1 集', dn.filter(x => x.n === 5).length === 1, dn.filter(x => x.n === 5).length);
chk('第 55–75 套一集都没听', dn.filter(x => x.n >= 55).length === 0, dn.filter(x => x.n >= 55).length);
refreshImp();
chk('再次导入变为已同步', ids.imp.textContent === '精选页进度已同步' && ids.imp.disabled === true, ids.imp.textContent);
$('imp').onclick();
chk('重复导入幂等', ITEMS.filter(x => S.done[x.i]).length === 121, ITEMS.filter(x => S.done[x.i]).length);
renderProg();
chk('导入后艺术类进度 20/66', ids.prog.innerHTML.includes('20 / 66'));
chk('导入后植物/农业 0/10', ids.prog.innerHTML.includes('0 / 10'));
chk('导入后合计 121 / 424', ids.prog.innerHTML.includes('121 / 424'));
`;

vm.runInThisContext(player + '\n' + ASSERTS, { filename: 'gh_full_player.js' });

console.log(globalThis.RESULTS.join('\n'));
const bad = globalThis.RESULTS.filter(x => x.startsWith('FAIL'));
console.log(`\n${globalThis.RESULTS.length - bad.length}/${globalThis.RESULTS.length} 通过`);
process.exit(bad.length ? 1 : 0);
