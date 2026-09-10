#!/usr/bin/env python3
"""修正字幕时间戳：用 bilibili 真实时间轴（subtitles/*.srt）做内容进度锚点，
按词数进度插值重新分配官方原文句子的起止时间。

背景：当前 gh_player_data.json 的 subs 时间戳是"按字数比例估算"的
（build_kmf_subs.py 的 seg_dur = 总时长 × 句字数占比），越往后偏差越大。
本脚本用真实对齐的 bilibili 字幕时间轴修正，保留官方原文文本不变。

用法: python3 fix_subtitle_timing.py
输出: 直接更新 gh_player_data.json（先备份）
"""
import json
import os
import re
import glob

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "gh_player_data.json")

# 备份
bak = DATA + ".bak_timing"
if not os.path.exists(bak):
    with open(DATA, encoding="utf-8") as f:
        with open(bak, "w", encoding="utf-8") as g:
            g.write(f.read())
    print(f"已备份原数据 -> {bak}")


def srt_data(f):
    """解析 SRT 文件，返回 [(start, end, text)]"""
    items = []
    cur_time = None
    cur_text = []
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", line)
        if m:
            if cur_time and cur_text:
                items.append((cur_time[0], cur_time[1], " ".join(cur_text)))
            g = [int(x) for x in m.groups()]
            cur_time = (g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                        g[4]*3600+g[5]*60+g[6]+g[7]/1000)
            cur_text = []
        elif line and not line.isdigit() and cur_time:
            cur_text.append(line)
    if cur_time and cur_text:
        items.append((cur_time[0], cur_time[1], " ".join(cur_text)))
    return items


def norm_words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def build_timeline(bili, official_sents):
    """内容进度插值：把官方句子按词数进度映射到 bili 真实时间轴"""
    bili_words = [norm_words(t[2]) for t in bili]
    bili_cum = [0]
    for w in bili_words:
        bili_cum.append(bili_cum[-1] + len(w))
    tb = bili_cum[-1]
    if tb == 0:
        return None

    off_words = [norm_words(t) for t in official_sents]
    off_cum = [0]
    for w in off_words:
        off_cum.append(off_cum[-1] + len(w))
    to = off_cum[-1]
    if to == 0:
        return None

    def time_at(p):
        target = p * tb
        for j in range(len(bili)):
            if bili_cum[j] <= target <= bili_cum[j+1]:
                frac = (target - bili_cum[j]) / max(1, bili_cum[j+1] - bili_cum[j])
                return bili[j][0] + frac * (bili[j][1] - bili[j][0])
        return bili[-1][1]

    times = []
    for k in range(len(official_sents)):
        s0 = time_at(off_cum[k] / to)
        e0 = time_at(off_cum[k+1] / to)
        times.append((round(s0, 1), round(e0, 1)))
    return times


# 建立 编号 -> SRT 文件 的映射
files = {}
for f in glob.glob(os.path.join(BASE, "subtitles", "p*.srt")):
    idx = int(os.path.basename(f)[1:4])
    files[idx] = f

with open(DATA, encoding="utf-8") as f:
    payload = json.load(f)

fixed = 0
skipped = []
for it in payload["items"]:
    i = it["i"]
    f = files.get(i)
    if not f:
        skipped.append((i, "no_srt"))
        continue
    bili = srt_data(f)
    if not bili:
        skipped.append((i, "empty_srt"))
        continue
    subs = payload["subs"].get(str(i)) or payload["subs"].get(i)
    if not subs:
        skipped.append((i, "no_subs"))
        continue

    # 官方句子文本（去掉说话人前缀用于词数统计）
    official_sents = []
    for c in subs:
        t = re.sub(r"^[A-Z][A-Z ]+:", "", c[2]).strip()
        official_sents.append(t)

    times = build_timeline(bili, official_sents)
    if not times:
        skipped.append((i, "empty_text"))
        continue

    # 回写时间戳（保留文本 c[2] 不变）
    for k, c in enumerate(subs):
        c[0], c[1] = times[k][0], times[k][1]
    fixed += 1

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

print(f"已修正 {fixed} 集字幕时间戳")
if skipped:
    print("跳过:", skipped[:10])
