// toefl-2026-vocab 云同步 + 分类一览的无头回归测试。
// 与 ets_official_2026/test_2026_player.js 同一套路：极简 DOM 打桩 + vm 跑页面脚本 + 断言。
// 用法: node test_sync.js   （退出码非 0 即失败）
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');

const HERE = __dirname;
const html = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8');
const dataJs = fs.readFileSync(path.join(HERE, 'data.js'), 'utf8');

class El {
  constructor(id) {
    this.id = id; this.children = []; this._html = ''; this.style = {}; this.dataset = {};
    this.value = ''; this.textContent = ''; this.className = ''; this.checked = true;
    this._cls = new Set();
    this._ev = {};
    this.classList = {
      add: c => this._cls.add(c),
      remove: c => this._cls.delete(c),
      toggle: (c, v) => { v ? this._cls.add(c) : this._cls.delete(c); },
      contains: c => this._cls.has(c),
    };
  }
  set innerHTML(v) { this._html = v; if (v === '') this.children = []; }
  get innerHTML() { return this._html; }
  appendChild(c) { this.children.push(c); return c; }
  removeAttribute() {}
  addEventListener(ev, fn) { this._ev[ev] = fn; }
  removeEventListener() {}
  querySelectorAll() { return []; }
  querySelector() { return null; }
  click() { if (this._ev.click) this._ev.click({ stopPropagation() {}, target: { closest: () => null } }); }
}

const ids = {};
const getEl = id => ids[id] || (ids[id] = new El(id));

function memStore() {
  const m = new Map();
  return {
    getItem: k => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => m.set(k, String(v)),
    removeItem: k => m.delete(k),
    _map: m,
  };
}

const results = [];
const chk = (name, cond, extra) => {
  results.push((cond ? 'ok   ' : 'FAIL ') + name + (extra !== undefined ? '  ' + extra : ''));
};

// ── 打桩环境 ──────────────────────────────────────────────
const localStorage = memStore();
const sessionStorage = memStore();

let fetchLog = [];
let gistStore = null; // 模拟远端 gist 文件内容

function fakeFetch(url, opts) {
  fetchLog.push({ url, method: (opts && opts.method) || 'GET', body: opts && opts.body });
  const json = body => Promise.resolve({ ok: true, json: () => Promise.resolve(body), text: () => Promise.resolve('') });
  if (url === 'https://api.github.com/user') return json({ login: 'tester' });
  if (url.startsWith('https://api.github.com/gists?')) {
    return json(gistStore ? [{ id: 'gid123456789', description: 'TOEFL-2026-vocab-progress-sync' }] : []);
  }
  if (url === 'https://api.github.com/gists' && opts && opts.method === 'POST') {
    gistStore = JSON.parse(opts.body).files['toefl2026-progress.json'].content;
    return json({ id: 'gid123456789' });
  }
  if (url.startsWith('https://api.github.com/gists/')) {
    if (opts && opts.method === 'PATCH') {
      gistStore = JSON.parse(opts.body).files['toefl2026-progress.json'].content;
      return json({ id: 'gid123456789' });
    }
    return json({ files: { 'toefl2026-progress.json': { content: gistStore, truncated: false } } });
  }
  return Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve('not found') });
}

const sandbox = {
  console,
  setTimeout, clearTimeout, setInterval, clearInterval,
  URLSearchParams, JSON, Math, Date, Object, Array, String, Number, Boolean, Error, Promise,
  btoa: s => Buffer.from(s, 'binary').toString('base64'),
  atob: s => Buffer.from(s, 'base64').toString('binary'),
  escape, unescape, encodeURIComponent, decodeURIComponent,
  localStorage, sessionStorage,
  fetch: fakeFetch,
  confirm: () => true,
  location: { search: '', pathname: '/toefl-2026-vocab/', hash: '', origin: 'https://example.test' },
  history: { replaceState() {} },
  navigator: { clipboard: { writeText: () => Promise.resolve() } },
  Blob: class { constructor() {} },
  URL: { createObjectURL: () => 'blob:x', revokeObjectURL() {} },
  FileReader: class { readAsText() {} },
  Audio: class { constructor() { this.src = ''; } play() { return Promise.resolve(); } pause() {} load() {} },
  document: {
    getElementById: getEl,
    createElement: t => new El(t),
    createDocumentFragment: () => new El('frag'),
    querySelectorAll: () => [],
    querySelector: () => null,
    addEventListener: () => {},
    removeEventListener: () => {},
    readyState: 'complete',
    body: new El('body'),
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;

const ctx = vm.createContext(sandbox);
// data.js 用 const 声明，属于 vm 上下文的词法绑定而不是 sandbox 属性，需在上下文里读取
vm.runInContext(dataJs + '\nvar __vocabLen = VOCAB.length; globalThis.VOCAB = VOCAB;', ctx);
const vocabLen = vm.runInContext('__vocabLen', ctx);
chk('data.js 定义 VOCAB', typeof vocabLen === 'number' && vocabLen > 2800, vocabLen);

// 取出页面脚本，去掉 IIFE 外壳，让内部函数暴露到 vm 上下文里以便断言
let script = html.split('<script>')[1].split('</script>')[0];
script = script.replace(/^\s*\(function\(\)\s*\{/, '').replace(/\}\)\(\);\s*$/, '');
vm.runInContext(script, ctx);
vm.runInContext('init();', ctx);

// ── 断言 ─────────────────────────────────────────────────
const run = expr => vm.runInContext(expr, ctx);

chk('云同步函数已定义', ['gistLogin', 'gistSyncNow', 'gistLogout', 'gistPull', 'gistPush', 'gistSchedulePush']
  .every(f => typeof run('typeof ' + f) === 'function' || run('typeof ' + f) === 'function'));

chk('日常阅读分类已注册', run("getMacro('阅读-标识告示')") === 'reading');

(async () => {
  // 1. 首次连接：远端没有 gist → 创建
  getEl('gist-token').value = 'ghp_faketoken';
  getEl('gist-remember').checked = true;
  run("progress['area'] = { box: 5, right: 1, wrong: 0, lastSeen: 1 }; ");
  await run('gistLogin()');
  chk('连接后创建了私密 gist', gistStore !== null);
  chk('上传内容包含本机进度', gistStore && JSON.parse(gistStore).progress.area.box === 5);
  chk('remember=true 时 Token 存 localStorage', !!localStorage.getItem('toefl2026_gist_sync'));
  chk('remember=true 时不写 sessionStorage', sessionStorage.getItem('toefl2026_gist_sync') === null);
  chk('连接成功提示', /同步|已连接/.test(getEl('gist-msg').textContent), getEl('gist-msg').textContent);

  // 2. 远端有更多练习次数的记录 → 拉取时合并
  gistStore = JSON.stringify({
    version: 1,
    progress: {
      area: { box: 5, right: 1, wrong: 0, lastSeen: 1 },
      aisle: { box: 3, right: 4, wrong: 2, lastSeen: 2 },
    },
  });
  const merged = await run('gistPull()');
  chk('gistPull 返回远端条目数', merged === 2, merged);
  chk('远端新词已合并', run("progress['aisle'] && progress['aisle'].box") === 3);
  chk('合并结果已落地 localStorage', JSON.parse(localStorage.getItem('toefl2026-progress')).aisle.right === 4);

  // 3. 练习次数少的远端记录不会覆盖本机
  run("progress['aisle'] = { box: 5, right: 9, wrong: 1, lastSeen: 9 }; saveProgress();");
  await run('gistPull()');
  chk('本机更高练习次数不被覆盖', run("progress['aisle'].right") === 9);

  // 4. 自动推送：saveProgress 触发去抖上传
  fetchLog = [];
  run("progress['seminar'] = { box: 1, right: 0, wrong: 1, lastSeen: 3 }; saveProgress();");
  await new Promise(r => setTimeout(r, 2300));
  const pushed = fetchLog.filter(f => f.method === 'PATCH');
  chk('saveProgress 后自动 PATCH 一次', pushed.length === 1, pushed.length);
  chk('自动推送内容含新词', gistStore && !!JSON.parse(gistStore).progress.seminar);

  // 5. remember=false → 只写 sessionStorage
  getEl('gist-remember').checked = false;
  run('gistRemember = false; gistSaveCreds();');
  chk('remember=false 时写 sessionStorage', !!sessionStorage.getItem('toefl2026_gist_sync'));
  chk('remember=false 时清掉 localStorage', localStorage.getItem('toefl2026_gist_sync') === null);

  // 6. 退出登录：清凭证但保留本机进度
  run('gistLogout()');
  chk('退出后清空 Token', run('gistToken') === '' && run('gistId') === '');
  chk('退出后两处凭证都已清除',
    localStorage.getItem('toefl2026_gist_sync') === null && sessionStorage.getItem('toefl2026_gist_sync') === null);
  chk('退出后本机进度保留', !!run("progress['aisle']"));
  fetchLog = [];
  run("progress['flyer'] = { box: 1, right: 0, wrong: 1, lastSeen: 4 }; saveProgress();");
  await new Promise(r => setTimeout(r, 2300));
  chk('退出后不再自动上传', fetchLog.length === 0, fetchLog.length);

  // 7. 未连接时点「立即同步」给出提示
  await run('gistSyncNow()');
  chk('未连接时提示先连接', /请先连接/.test(getEl('gist-msg').textContent), getEl('gist-msg').textContent);

  // 8. Token 无效时不留下半连接状态
  getEl('gist-token').value = '';
  await run('gistLogin()');
  chk('空 Token 报错', /请先粘贴/.test(getEl('gist-msg').textContent));

  // ── 分类一览 → 单词卡 ──────────────────────────────
  // 9. 总览的分类卡片提供「一览全部」而不是直接开卡
  const macroHtml = getEl('macro-list').innerHTML;
  chk('分类卡片有一览按钮', /data-browse="listening"/.test(macroHtml));
  chk('分类卡片保留记忆曲线入口', /data-macro="listening"/.test(macroHtml));

  // 10. 打开「听力场景」一览：全部词都在，按子场景分组
  run("openBrowse('listening')");
  chk('打开一览后切到 browse 视图', run('currentTab') === 'browse');
  const flatLen = run('(renderBrowse._flat || []).length');
  const listeningTotal = run("vocab.filter(e => getMacro(e.c) === 'listening').length");
  chk('一览列出该分类全部单词', flatLen === listeningTotal && flatLen > 1500, flatLen + '/' + listeningTotal);
  chk('一览不受 30 词会话上限影响', flatLen > 30);
  const groupCount = run("browseGroups('listening').length");
  chk('按子场景分组', groupCount > 100, groupCount);
  chk('一览渲染了子场景标题', getEl('browse-head').innerHTML.includes('个子场景'));
  chk('browseMacro 已持久化', JSON.parse(localStorage.getItem('toefl2026-settings')).browseMacro === 'listening');

  // 11. 点击某个词才进入单词卡模式，并从该词开始
  chk('一览阶段还没进入卡片模式', run('studyStarted') === false || run("currentTab") === 'browse');
  run('startStudyAt(7)');
  chk('点词后进入 study 视图', run('currentTab') === 'study');
  chk('从被点击的词开始', run('studyIdx') === 7, run('studyIdx'));
  chk('队列 = 整个分类', run('studyQueue.length') === listeningTotal, run('studyQueue.length'));
  chk('当前卡片就是被点的词',
    run('studyQueue[studyIdx].w') === run("browseGroups('listening').flatMap(g => g.items)[7].w"),
    run('studyQueue[studyIdx].w'));
  chk('卡片区已渲染', /flashcard/.test(getEl('study-area').innerHTML));

  // 12. 越界点击被夹到有效范围
  run('startStudyAt(999999)');
  chk('越界索引夹到末尾', run('studyIdx') === listeningTotal - 1, run('studyIdx'));

  // 13. 一览页的返回与「按记忆曲线学」仍可用
  run("openBrowse('reading')");
  chk('切换到另一分类', run('currentTab') === 'browse' && run('browseMacro') === 'reading');
  const readingTotal = run("vocab.filter(e => getMacro(e.c) === 'reading').length");
  chk('日常阅读一览词数正确', run('(renderBrowse._flat || []).length') === readingTotal, readingTotal);
  run("startStudy('reading', 'new')");
  chk('记忆曲线入口仍走会话上限', run('studyQueue.length') <= 30, run('studyQueue.length'));

  // 14. 未选分类时 browse 给出提示而不是崩溃
  run("browseMacro = ''; renderBrowse();");
  chk('未选分类时有兜底提示', /请从总览选择/.test(getEl('browse-list').innerHTML));

  console.log(results.join('\n'));
  const failed = results.filter(r => r.startsWith('FAIL'));
  console.log('\n' + (results.length - failed.length) + '/' + results.length + ' 通过');
  process.exit(failed.length ? 1 : 0);
})();
