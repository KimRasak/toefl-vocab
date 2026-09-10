#!/usr/bin/env python3
"""把远程 whisper 对齐结果合并进 gh_player_data.json。
用法: python3 merge_alignment.py /path/to/alignment.json
- 用 whisper 对齐时间戳替换 subs 的 [start, end]
- 保留官方文本 c[2] 不变
- 处理零时长/异常值：用相邻句插值
- 备份原数据
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "gh_player_data.json")
ALIGN = sys.argv[1] if len(sys.argv) > 1 else "/tmp/alignment.json"

with open(DATA, encoding="utf-8") as f:
    payload = json.load(f)
with open(ALIGN, encoding="utf-8") as f:
    align = json.load(f)

# 备份
bak = DATA + ".bak_whisper"
if not os.path.exists(bak):
    with open(DATA, encoding="utf-8") as f:
        with open(bak, "w", encoding="utf-8") as g:
            g.write(f.read())

def fix_times(cues):
    """处理异常：零时长、负时长、非单调"""
    n = len(cues)
    # 第一遍：替换时间戳，记录异常
    times = [(c[0], c[1]) for c in cues]
    # 零时长或异常（start>=end 或 start<0）标记为 None
    for i in range(n):
        s, e = times[i]
        if s < 0 or e < 0 or e <= s:
            times[i] = None
    # 第二遍：异常值用前后有效值插值
    result = []
    for i, c in enumerate(cues):
        t = times[i]
        if t is not None:
            result.append([round(t[0], 1), round(t[1], 1), c[2]])
            continue
        # 找前后有效值
        prev_t = next_t = None
        for j in range(i - 1, -1, -1):
            if times[j] is not None:
                prev_t = times[j]
                break
        for j in range(i + 1, n):
            if times[j] is not None:
                next_t = times[j]
                break
        if prev_t and next_t:
            # 插值
            start = prev_t[1]
            end = next_t[0]
            mid = (start + end) / 2
            result.append([round(start, 1), round(max(mid, start + 0.1), 1), c[2]])
        elif prev_t:
            result.append([round(prev_t[1], 1), round(prev_t[1] + 2, 1), c[2]])
        elif next_t:
            result.append([round(max(0, next_t[0] - 2), 1), round(next_t[0], 1), c[2]])
        else:
            result.append([0.0, 2.0, c[2]])
    return result

# 合并
merged = 0
for key, cues in align.items():
    if key not in payload["subs"]:
        continue
    # 校验句子数一致
    old_cues = payload["subs"][key]
    if len(cues) != len(old_cues):
        print(f"[{key}] 句数不一致: align={len(cues)} subs={len(old_cues)}，跳过")
        continue
    # 用 align 的时间戳 + 原 subs 的文本
    fixed = fix_times(cues)
    # 保留原文本（官方），只换时间
    for i, c in enumerate(fixed):
        c[2] = old_cues[i][2]
    payload["subs"][key] = fixed
    merged += 1

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

print(f"已合并 {merged} 集 whisper 对齐时间戳")
