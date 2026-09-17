# -*- coding: utf-8 -*-
"""把「通用词汇」词条的高频用法补充写回学科总表页面。

用法：
    python3 workspace/scripts/apply_general_usage.py <patch.json> [--topic 通用词汇]
    python3 workspace/scripts/apply_general_usage.py --list-pending

patch.json 结构：{"acting": {"d": "短释义", "f": "展开释义"}, ...}
  - d 省略时保留原短释义；f 必填。

页面 site/vocab/disciplines/index.html 已经与 build_merged_by_discipline.py
的输出长期分叉（人工逐词精修过 100+ 词条），所以这里直接改成品页面，不重跑构建。
同一批内容会另存一份到 workspace/data/overrides/general_usage_expansions.json，
即便将来重新生成页面也不会丢。
"""
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
BASE = os.path.dirname(WORKSPACE)
PAGE = os.path.join(BASE, 'site', 'vocab', 'disciplines', 'index.html')
SIDECAR = os.path.join(WORKSPACE, 'data', 'overrides', 'general_usage_expansions.json')
DATA_RE = re.compile(r'(const DATA = )(\[.*?\])(;\n)', re.S)
TAG_RE = re.compile(r'\[(?:ph|st|syn|mean|def|ex|n|v|adj|adv|sth)\]')
DEFAULT_TOPIC = '通用词汇'


def load_page():
    html = open(PAGE, encoding='utf-8').read()
    match = DATA_RE.search(html)
    if not match:
        raise SystemExit('找不到 const DATA = [...] 数据块')
    return html, match, json.loads(match.group(2))


def dump_data(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def find_topic(data, topic):
    for entry in data:
        if entry['name'].startswith(topic):
            return entry
    raise SystemExit(f'页面里没有「{topic}」这一栏')


def pending(words):
    """尚未补充用法的词：释义只有一行，且没有 [ph] 之类的旧标记。"""
    bare, tagged = [], []
    for word in words:
        full = word['f']
        if '\n' in full:
            continue
        (tagged if TAG_RE.search(full) else bare).append(word['w'])
    return bare, tagged


def save_sidecar(patch):
    try:
        with open(SIDECAR, encoding='utf-8') as handle:
            store = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        store = {}
    store.update(patch)
    with open(SIDECAR, 'w', encoding='utf-8') as handle:
        json.dump(store, handle, ensure_ascii=False, indent=1, sort_keys=True)
        handle.write('\n')
    return len(store)


def main(argv):
    topic = DEFAULT_TOPIC
    if '--topic' in argv:
        index = argv.index('--topic')
        topic = argv[index + 1]
        del argv[index:index + 2]

    html, match, data = load_page()
    section = find_topic(data, topic)

    if '--list-pending' in argv:
        bare, tagged = pending(section['words'])
        print(json.dumps({'topic': section['name'], 'total': len(section['words']),
                          'bare': bare, 'tagged_only': tagged},
                         ensure_ascii=False, indent=1))
        return 0

    if not argv:
        raise SystemExit(__doc__)

    with open(argv[0], encoding='utf-8') as handle:
        patch = json.load(handle)

    index = {word['w']: word for word in section['words']}
    missing = [w for w in patch if w not in index]
    if missing:
        raise SystemExit(f'这些词不在「{section["name"]}」里: {missing}')

    changed = []
    for word, fields in patch.items():
        target = index[word]
        full = str(fields['f']).strip()
        if not full:
            raise SystemExit(f'{word}: f 不能为空')
        if '\n' not in full:
            raise SystemExit(f'{word}: f 只有一行，等于没补用法')
        target['f'] = full
        short = fields.get('d')
        if short:
            target['d'] = str(short).strip()
        changed.append(word)

    new_html = html[:match.start()] + match.group(1) + dump_data(data) + match.group(3) + html[match.end():]
    # 数据块必须仍能被同一个正则与 JSON 解析器读回，否则页面会白屏。
    verify = DATA_RE.search(new_html)
    if not verify:
        raise SystemExit('写回后数据块无法再次匹配，已放弃')
    json.loads(verify.group(2))
    with open(PAGE, 'w', encoding='utf-8') as handle:
        handle.write(new_html)

    total = save_sidecar({w: {'d': index[w]['d'], 'f': index[w]['f']} for w in changed})
    bare, tagged = pending(section['words'])
    print(f'已更新 {len(changed)} 词: {", ".join(sorted(changed))}')
    print(f'sidecar 累计 {total} 词 -> {os.path.relpath(SIDECAR, BASE)}')
    print(f'「{section["name"]}」剩余待补: 无用法 {len(bare)} 词 / 仅旧标记 {len(tagged)} 词')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
