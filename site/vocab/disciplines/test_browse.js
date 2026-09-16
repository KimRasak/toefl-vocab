'use strict';
// merged-by-discipline 连播/专注「🆕 仅新词」的无头回归测试。
// 与 toefl-2026-vocab/test_sync.js 同一套路：极简 DOM 打桩 + vm 跑页面脚本 + 断言。
// 用法: node test_browse.js   （退出码非 0 即失败）
const fs = require('fs'), path = require('path'), vm = require('vm');

const HERE = __dirname;
const html = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

// 每个 boot() 一个独立元件注册表；El.appendChild 动态创建的元件
// （如 abToast）也要注册进当前 boot 的表里。
let CUR_REG = null;
class El {
  constructor(tag) {
    this.tagName = tag; this.children = []; this._html = '';
    this.style = {}; this.dataset = {};
    this.value = ''; this.textContent = ''; this.className = '';
    this.options = [];                       // abLoad 里 [...abTopicSelect.options] 需要可迭代
    this.offsetHeight = 60;
    this._cls = new Set(); this._ev = {};
    this.classList = {
      add: c => { this._cls.add(c); },
      remove: c => { this._cls.delete(c); },
      toggle: (c, v) => { const on = v === undefined ? !this._cls.has(c) : !!v; on ? this._cls.add(c) : this._cls.delete(c); return on; },
      contains: c => this._cls.has(c),
    };
  }
  set innerHTML(v) { this._html = v; if (v === '') this.children = []; }
  get innerHTML() { return this._html; }
  appendChild(c) { this.children.push(c); if (c && c.id && CUR_REG) CUR_REG[c.id] = c; return c; }
  setAttribute() {} removeAttribute() {}
  addEventListener(ev, fn) { this._ev[ev] = fn; }
  removeEventListener() {}
  querySelectorAll() { return []; }
  querySelector() { return null; }
  contains() { return false; }
  closest() { return null; }
  scrollIntoView() {}
  focus() {} blur() {}
}

const results = [];
const chk = (name, cond, extra) => {
  results.push((cond ? 'ok   ' : 'FAIL ') + name + (extra !== undefined ? '  ' + extra : ''));
};

function memStore() {
  const m = new Map();
  return {
    getItem: k => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => m.set(k, String(v)),
    removeItem: k => m.delete(k),
  };
}

function boot(ls) {
  const reg = Object.create(null);
  CUR_REG = reg;
  const gel = id => reg[id] || (reg[id] = new El('div'));
  const htmlEl = new El('html');
  htmlEl.style = { setProperty() {}, removeProperty() {} };
  const sandbox = {
    console,
    // 打桩定时器：abFlashMsg 的自动消失、连播间隔都不需要真触发
    setTimeout: () => 0, clearTimeout: () => {},
    setInterval, clearInterval,
    localStorage: ls, sessionStorage: memStore(),
    fetch: () => Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve('') }),
    Audio: class { constructor() { this.src = ''; } play() { return Promise.resolve(); } pause() {} load() {} },
    document: {
      getElementById: gel,
      createElement: t => new El(t),
      querySelector: sel => (sel === 'header' || sel === '.foot' ? gel('_' + sel) : null),
      querySelectorAll: () => [],
      addEventListener: () => {},
      removeEventListener: () => {},
      documentElement: htmlEl,
      body: new El('body'),
    },
  };
  sandbox.window = sandbox;
  sandbox.addEventListener = () => {};
  sandbox.removeEventListener = () => {};
  sandbox.globalThis = sandbox;
  const ctx = vm.createContext(sandbox);
  vm.runInContext(script, ctx);
  const run = expr => vm.runInContext(expr, ctx);
  return { run, reg, ls };
}

// ── 场景一：干净环境（无历史进度）─────────────────────────────
const ls1 = memStore();
const s1 = boot(ls1);
const run = s1.run;

const IS26 = 'w => w.s.indexOf("2026") >= 0';
chk('HTML 含连播条/专注模式两个 🆕 按钮',
  html.includes('id="ab2026Only"') && html.includes('id="focus2026Btn"'));
chk('初始列表 = 全部词汇', run('abGetList().length') === run('ALL_WORDS.length'));
const total2026 = run(`ALL_WORDS.filter(${IS26}).length`);
chk('2026 新词总数 > 0', total2026 > 0, total2026);

run('toggle2026Only()');
chk('开启后 ab2026Only = true', run('ab2026Only') === true);
chk('开启后列表只剩 🆕 词', run('abGetList().every(w => w.s.indexOf("2026") >= 0)') === true);
chk('开启后列表长度 = 全部 🆕 词数', run('abGetList().length') === total2026);
chk('就近跳转：落在第一个 🆕 词上（当前词非 🆕）',
  run('abGetList()[abIdx].w') === run(`ALL_WORDS.find(${IS26}).w`));
const savedAb = JSON.parse(ls1.getItem('merged_autoplay') || '{}');
chk('localStorage only2026 持久化', savedAb.only2026 === true, JSON.stringify(savedAb));

// 「下一个」在过滤列表内步进（专注模式 + 连播条两个入口）
const w0 = run('abGetList()[abIdx].w');
run('focusNext()');
chk('focusNext 后 abIdx +1', run('abIdx') === 1);
chk('focusNext 后仍是 🆕 词', run('abGetList()[abIdx].w') !== w0 && run('abGetList()[abIdx].s.indexOf("2026")>=0') === true);
run('document.getElementById("abNext").onclick()');
chk('连播条 ⏭ 后 abIdx +1', run('abIdx') === 2);
chk('⏭ 后仍是 🆕 词', run('abGetList()[abIdx].s.indexOf("2026")>=0') === true);

// 按钮态同步
chk('ab2026Only 按钮高亮', s1.reg['ab2026Only'].classList.contains('active') === true);
chk('focus2026Btn 高亮', s1.reg['focus2026Btn'].classList.contains('active') === true);
chk('连播词显示与列表一致', s1.reg['abWord'].textContent === run('abGetList()[abIdx].w'));

// 关闭：保持位置回到完整列表
const curWord = run('abGetList()[abIdx].w');
run('focusToggle2026()');
chk('focusToggle2026 关闭后 ab2026Only = false', run('ab2026Only') === false);
chk('关闭后按钮不再高亮', s1.reg['focus2026Btn'].classList.contains('active') === false);
chk('关闭后原地保留当前词', run('abGetList()[abIdx].w') === curWord);

// 当前词本身就是 🆕 时开启：原地不动
run(`abIdx = ALL_WORDS.findIndex(${IS26})`);
const cur2026 = run('abGetList()[abIdx].w');
run('toggle2026Only()');
chk('当前词是 🆕：开启后停在原词', run('abGetList()[abIdx].w') === cur2026);
run('toggle2026Only()'); // 关掉，还原

// ── 场景二：选定无 🆕 词的学科 → 自动放宽 ─────────────────────
const zeroTopic = run(`(function(){
  const t = DATA.find(t => t.words.every(w => w.s.indexOf("2026") < 0));
  return t ? t.emoji + ' ' + t.name.split(' ')[0] : null;
})()`);
if (zeroTopic) {
  run('ab2026Only = false');
  run('abTopic = ' + JSON.stringify(zeroTopic));
  s1.reg['abTopicSelect'].value = zeroTopic;
  run('abIdx = 0');
  run('toggle2026Only()');
  chk('无 🆕 学科：开启后自动清空学科范围', run('abTopic') === null);
  chk('无 🆕 学科：仍成功进入 🆕 列表', run('ab2026Only') === true && run('abGetList().length') === total2026);
  const toast = s1.reg['abToast'] ? s1.reg['abToast'].textContent : '';
  chk('提示已放宽到全部学科', toast.indexOf('放宽') >= 0, toast);
  run('abTopicSelect.value = ""');
  run('toggle2026Only()');
} else {
  chk('（跳过）不存在完全没有 🆕 词的学科', true);
}

// ── 场景三：⭐ 与 🆕 无交集 → 保护性回退 ──────────────────────
run('ab2026Only = false');
run('abHardOnly = true');
run('hardWords.add(ALL_WORDS.find(w => w.s.indexOf("2026") < 0).w)');
run('abIdx = 0');
run('toggle2026Only()');
chk('⭐∩🆕 为空：过滤被回退关闭', run('ab2026Only') === false);
const toast3 = s1.reg['abToast'] ? s1.reg['abToast'].textContent : '';
chk('提示没有既是 ⭐ 又是 🆕 的词', toast3.indexOf('⭐') >= 0 && toast3.indexOf('🆕') >= 0, toast3);
run('abHardOnly = false');
run('hardWords.clear()');
run('saveHard()');

// ── 场景四：跳转非 🆕 词 → 自动放宽 🆕 过滤 ───────────────────
run('ab2026Only = false');
run('toggle2026Only()'); // 开
const plainWord = run('ALL_WORDS.find(w => w.s.indexOf("2026") < 0).w');
s1.reg['abStart'].value = plainWord;
run('abJumpToInput()');
chk('跳转非 🆕 词后自动放宽过滤', run('ab2026Only') === false);
chk('跳转落在目标词上', run('abGetList()[abIdx].w') === plainWord, run('abGetList()[abIdx].w') + ' vs ' + plainWord);

// ── 场景五：持久化恢复（含越界序号夹回）───────────────────────
{
  const ls2 = memStore();
  ls2.setItem('merged_autoplay', JSON.stringify({
    idx: 99999, gap: 1000, topic: '', rangeStart: 1, rangeEnd: null, only2026: true,
  }));
  const s2 = boot(ls2);
  chk('恢复 only2026 = true', s2.run('ab2026Only') === true);
  chk('越界序号夹回 0', s2.run('abIdx') === 0, s2.run('abIdx'));
  chk('恢复后列表仍是 🆕 过滤', s2.run('abGetList().every(w => w.s.indexOf("2026") >= 0)') === true);
  chk('恢复后按钮高亮', s2.reg['ab2026Only'].classList.contains('active') === true);
  chk('恢复后连播词与列表一致', s2.reg['abWord'].textContent === s2.run('abGetList()[abIdx].w'));
}

// ── 汇总 ─────────────────────────────────────────────────────
console.log(results.join('\n'));
const fails = results.filter(r => r.startsWith('FAIL'));
console.log('\n' + (fails.length ? '✗ ' + fails.length + ' 项失败' : '✓ 全部通过') + '（共 ' + results.length + ' 项）');
process.exit(fails.length ? 1 : 0);
