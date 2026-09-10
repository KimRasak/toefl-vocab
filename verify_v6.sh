#!/usr/bin/env bash
# V6 验证脚本：跑完抓取后执行
set -e
cd "$(dirname "$0")"

echo "=== 1. 抓取数据检查 ==="
python3 - <<'EOF'
import json
d = json.load(open('output/cambridge_defs_1791.json', encoding='utf-8'))
total = len(d)
with_def = sum(1 for v in d.values() if v.get('defs'))
with_mp3 = sum(1 for v in d.values() if v.get('us_mp3_url'))
with_ipa = sum(1 for v in d.values() if v.get('ipa'))
with_ex = sum(1 for v in d.values() if v.get('examples'))
print(f"总词数: {total}")
print(f"有释义: {with_def} ({with_def/total*100:.1f}%)")
print(f"有美音mp3: {with_mp3} ({with_mp3/total*100:.1f}%)")
print(f"有音标: {with_ipa} ({with_ipa/total*100:.1f}%)")
print(f"有例句: {with_ex} ({with_ex/total*100:.1f}%)")
# 无释义的词
missing = [w for w,v in d.items() if not v.get('defs')]
print(f"无释义词({len(missing)}): {missing[:20]}")
EOF

echo ""
echo "=== 2. 生成 V6 ==="
python3 build_v6.py output/cambridge_defs_1791.json my-tofel-1791words-words.html my-tofel-1791words-words.html my-tofel-1791words-words.txt

echo ""
echo "=== 3. JS 语法检查 ==="
python3 - <<'EOF'
import re
html = open('my-tofel-1791words-words.html', encoding='utf-8').read()
m = re.search(r'<script>(.*?)</script>', html, re.S)
open('/tmp/v6-check.js','w',encoding='utf-8').write(m.group(1))
EOF
node --check /tmp/v6-check.js && echo "JS OK"
echo "=== 完成 ==="
