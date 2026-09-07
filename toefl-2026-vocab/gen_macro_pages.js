// 生成各技能卡独立子路径页：awl/ listening/ reading/ subject/ phrasal/ writing/ speaking/ other/
// 每个子路径页 = 该宏过滤后的 data.js（每条附主站全量索引 i）+ 主站 index.html 的最小适配副本。
// 用法: node gen_macro_pages.js   （幂等，可重复运行；主站 data.js/index.html 不变）
'use strict';
const fs = require('fs'), path = require('path');
const HERE = __dirname;
const mainData = fs.readFileSync(path.join(HERE, 'data.js'), 'utf8');
const mainHtml = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8');
const VOCAB = eval(mainData.match(/const VOCAB\s*=\s*(\[.*\]);/s)[1]);

function getMacro(c) {
  if (c.startsWith('AWL')) return 'awl';
  if (c.startsWith('听力-')) return 'listening';
  if (c.startsWith('阅读-')) return 'reading';
  if (c.startsWith('口语-')) return 'speaking';
  if (c.startsWith('学科-') || c.startsWith('深度-')) return 'subject';
  if (c === '短语动词') return 'phrasal';
  if (c.includes('写作') || c.startsWith('功能词')) return 'writing';
  if (c.startsWith('填词-') || c.startsWith('词缀派生-')) return 'reading';
  if (c.startsWith('讲座信号词-') || c.startsWith('态度词-') || c === '语气动词') return 'listening';
  if (c.startsWith('同义替换-') || c === '学术搭配') return 'writing';
  return 'other';
}

const MACROS = [
  ['awl', 'AWL学术词'], ['listening', '听力场景'], ['reading', '日常阅读'],
  ['subject', '学科主题'], ['phrasal', '短语动词'], ['writing', '写作表达'],
  ['speaking', '口语表达'], ['other', '其他'],
];

const ser = e => '{' + ['w', 'p', 'm', 'c', 'i', 'r'].map(k => JSON.stringify(k) + ':' + JSON.stringify(e[k])).join(',') + '}';

let total = 0;
for (const [key, name] of MACROS) {
  const dir = path.join(HERE, key);
  fs.mkdirSync(dir, { recursive: true });
  const filtered = VOCAB.map((e, i) => Object.assign({}, e, { i })).filter(e => getMacro(e.c) === key);
  fs.writeFileSync(path.join(dir, 'data.js'), 'const VOCAB=[' + filtered.map(ser).join(',') + '];');
  let html = mainHtml
    .replace('<title>2026 新托福词汇卡</title>', '<title>2026 新托福 · ' + name + '词汇卡</title>')
    .replace('<h1>2026 词汇卡</h1>', '<h1>' + name + '词汇卡</h1>')
    .replace('← 返回 TOEFL 单词本', '← 完整词表')
    .replace(/const MACRO_SUBPATH = \{[^}]*\};/, 'const MACRO_SUBPATH = {};')
    .replace('let wordToIndex = {};\nlet progress = {};',
      'let wordToIndex = {};\nlet byFullIdx = {};\nlet progress = {};')
    .replace('const entry = vocab[idx];', 'const entry = byFullIdx[idx];')
    .replace('vocab.forEach((e, i) => { wordToIndex[e.w] = i; });',
      'vocab.forEach(e => { wordToIndex[e.w] = e.i; if (typeof e.i === \'number\') byFullIdx[e.i] = e; });')
    // 子路径页一打开直接落在「分类一览」（该部分的单词表），不经过总览
    .replace(/  if \(settings\.tab\) currentTab = settings\.tab;\n  if \(currentTab === 'browse'\) \{\n    browseMacro = settings\.browseMacro \|\| '';\n    if \(!MACRO\[browseMacro\]\) currentTab = 'dashboard';\n  \}/,
      "  currentTab = 'browse';\n  browseMacro = '" + key + "';");
  fs.writeFileSync(path.join(dir, 'index.html'), html);
  total += filtered.length;
  console.log(key.padEnd(10) + filtered.length + ' 词  →  ' + key + '/');
}
console.log('合计 ' + total + '（主站 ' + VOCAB.length + '，应相等）');
