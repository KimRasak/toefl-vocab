#!/usr/bin/env python3
"""把 TPO 各套的「出题时间」（原始真实考试日期）标注到播放器数据里。

读取:  tpo_exam_dates.json      各套 TPO -> 考试日期 / 可信度 / 备注
改写:  gh_playlist.json         加 exam_date / exam_conf / exam_note 字段
       gh_player_data.json      加紧凑字段 y(日期) / yq(1=低可信) / yn(备注)

用法: python3 add_exam_dates.py
之后需重新执行 build_gh_player.py 生成 gh_listening_player.html。
"""
import json
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
DATES = os.path.join(BASE, "tpo_exam_dates.json")
PLAYLIST = os.path.join(BASE, "gh_playlist.json")
PLAYER = os.path.join(BASE, "gh_player_data.json")


def tpo_num(short: str):
    """'TPO-06_C1' / '06_C1' -> '06'（两位补零）"""
    m = re.match(r"(?:TPO-)?(\d+)_", short)
    return f"{int(m.group(1)):02d}" if m else None


def main():
    with open(DATES, encoding="utf-8") as f:
        sets = json.load(f)["sets"]

    stats = {"dated": 0, "low": 0, "none": 0, "release_only": 0, "unmapped": 0}
    missing = set()

    def annotate(item, compact):
        n = tpo_num(item.get("short") or item.get("s") or "")
        if n is None:
            stats["unmapped"] += 1
            return
        info = sets.get(n)
        if info is None:
            missing.add(n)
            stats["none"] += 1
            return
        exam, conf, note = info["exam"], info["conf"], info.get("note") or ""
        release = info.get("release")
        if compact:
            # 紧凑键名，减小内嵌 HTML 体积
            if exam:
                item["y"] = exam
                if conf == "low":
                    item["yq"] = 1
            # r 只在没有考试日期时才用于显示（考试日期优先），但两者都存下来
            if release:
                item["r"] = release
            if note:
                item["yn"] = note
        else:
            item["exam_date"] = exam
            item["exam_conf"] = conf
            item["release"] = release
            item["exam_note"] = note
        if exam:
            stats["dated"] += 1
            if conf == "low":
                stats["low"] += 1
        else:
            stats["none"] += 1
            if release:
                stats["release_only"] += 1

    # ---- gh_playlist.json（可读版，字段名完整）----
    shutil.copyfile(PLAYLIST, PLAYLIST + ".bak_predate")
    with open(PLAYLIST, encoding="utf-8") as f:
        playlist = json.load(f)
    for it in playlist:
        annotate(it, compact=False)
    with open(PLAYLIST, "w", encoding="utf-8") as f:
        json.dump(playlist, f, ensure_ascii=False, indent=1)

    # ---- gh_player_data.json（播放器内嵌版，紧凑字段）----
    stats.update(dated=0, low=0, none=0, release_only=0, unmapped=0)  # 只统计一遍
    shutil.copyfile(PLAYER, PLAYER + ".bak_predate")
    with open(PLAYER, encoding="utf-8") as f:
        payload = json.load(f)
    for it in payload["items"]:
        annotate(it, compact=True)
    with open(PLAYER, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    total = len(playlist)
    print(f"共 {total} 集（gh_playlist.json 与 gh_player_data.json 各写一份）")
    print(f"  有出题时间      : {stats['dated']}  （其中低可信 {stats['low']}）")
    print(f"  无出题时间/查无 : {stats['none']}  （其中 {stats['release_only']} 集有上线时间可显示）")
    print(f"  编号无法解析    : {stats['unmapped']}")
    if missing:
        print(f"  tpo_exam_dates.json 里缺少这些套: {sorted(missing)}")
    print("已备份 *.bak_predate；下一步执行 python3 build_gh_player.py")


if __name__ == "__main__":
    main()
