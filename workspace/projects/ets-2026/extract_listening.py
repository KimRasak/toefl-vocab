#!/usr/bin/env python3
"""从 ETS 官方 2026 免费练习卷 PDF 文本中抽取听力题，输出结构化 JSON。

输入：ets_official_2026/txt/*.txt （由 pdftotext -layout 生成）
输出：ets_official_2026/listening_2026.json

四类任务：
  choose_response  Listen and Choose a Response（听答题）
  conversation     Listen to a Conversation（短对话）
  announcement     Listen to an Announcement（学术公告）
  academic_talk    Listen to an Academic Talk（学术讲座）
"""
import re, json, glob, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(BASE, "txt")
OUT = os.path.join(BASE, "listening_2026.json")

FOOTER = re.compile(r"^\s*TOEFL iBT®.*?\d+\s*$", re.M)
OPT = re.compile(r"^\s*\(([A-D])\)\s*(.+?)\s*$")
QNUM = re.compile(r"^\s*(\d+)\.\s*(.*)$")
CR_ITEM = re.compile(r"^\s*(\d+)\.\s+(Woman|Man|Boy|Girl)\s*:\s*(.*)$")
PROMPT = re.compile(
    r"^\s*Listen to (a|an)\s+(short conversation|conversation|announcement|talk|lecture|discussion|podcast)"
    r"(.*?)\.\s*$", re.I)
SPEAKER = re.compile(r"^\s*([A-Z][A-Za-z .'’\-]{1,40}?)\s*:\s*(.*)$")
# 页眉页脚：选项有时跨页，遇到这些行要跳过而不是当成选项结束
NOISE = re.compile(r"^\s*(TOEFL iBT|Listening Section|Reading Section|Copyright|Module \d|\d{1,3})\s*$"
                   r"|^\s*TOEFL iBT.*\d+\s*$", re.I)


def kind_of(prompt_line: str) -> str:
    p = prompt_line.lower()
    if "announcement" in p:
        return "announcement"
    if "conversation" in p:
        return "conversation"
    return "academic_talk"


def strip_noise(block: str) -> list:
    block = FOOTER.sub("", block)
    return [ln.rstrip() for ln in block.split("\n")]


def is_question_head(lines: list, j: int, n: int) -> bool:
    """判断 lines[j] 是不是一道无编号题的题干：非空、不是选项/提示语，
    且往后跳过空行后紧接着出现 (A) 选项。"""
    ln = lines[j]
    if not ln.strip() or OPT.match(ln) or PROMPT.match(ln) or QNUM.match(ln):
        return False
    if SPEAKER.match(ln):
        return False
    k = j + 1
    steps = 0
    while k < n and steps < 4:
        if not lines[k].strip():
            k += 1
            continue
        mo = OPT.match(lines[k])
        return bool(mo and mo.group(1) == "A")
    return False


def collect_options(lines: list, start: int, n: int):
    """从 lines[start] 开始收 (A)-(D) 四个选项，返回 (opts, 下一行下标, 溢出文本)。

    要处理的坑：pdftotext 会把过长的选项折成两行，中间还夹一个空行，例如
        (C) Children with increased exposure to a second language are more motivated to
        <空行>
        learn it.
        <空行>
        (D) Formal education does not ...
    旧写法一见到非选项的正文行就 break，于是 (C) 被截断、(D) 整条丢掉
    （实测 t4 Module 1 的第 17 题就这样只剩 3 个选项）。

    续行判定：当前选项文本没有句末标点，且下一非空行不是选项/题干/说明/页眉，
    并且以小写字母或标点开头——这时才当续行接上去。宁可漏接也不要错吞正文。
    溢出文本 = 在收到第一个选项之前遇到的正文行，交给调用方决定是否续到题干上。
    """
    opts = {}
    cur = None
    overflow = []
    i = start
    while i < n:
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        mo = OPT.match(ln)
        if mo:
            cur = mo.group(1)
            opts[cur] = mo.group(2).strip()
            i += 1
            continue
        if QNUM.match(ln) or PROMPT.match(ln) or SPEAKER.match(ln) or NOISE.match(ln):
            if NOISE.match(ln):      # 页眉页脚：跳过，选项可能跨页
                i += 1
                continue
            break
        txt = ln.strip()
        if cur and not opts[cur][-1:] in ".!?\"”" and (txt[:1].islower() or txt[:1] in "(,;"):
            opts[cur] += " " + txt          # 折行续接
            i += 1
            continue
        if not opts:
            overflow.append(txt)            # 还没开始收选项，属于题干折行
            i += 1
            continue
        break                                # 四个选项之后的正文，收尾
    return opts, i, overflow


def renumber(items: list) -> None:
    """按文档顺序补齐缺失的题号（教师卷 3–5 的题号在 PDF 抽取时丢失）。"""
    last = 0
    for it in items:
        if it["kind"] == "choose_response":
            last = it["number"]
        else:
            for q in it["questions"]:
                if q.get("number"):
                    last = q["number"]
                else:
                    last += 1
                    q["number"] = last


def parse_answer_keys(section: str) -> list:
    """返回该 section 内每个 Answer Key 表格的 {题号: 答案} 字典，按出现顺序。"""
    keys = []
    for m in re.finditer(r"Answer Key(.*?)(?=Answer Key|\Z)", section, re.S):
        body = m.group(1)
        d = {}
        for ln in body.split("\n"):
            mm = re.match(r"^\s*(\d{1,2})\s+([A-D])\s*$", ln)
            if mm:
                d[int(mm.group(1))] = mm.group(2)
        if d:
            keys.append(d)
    return keys


def parse_module(lines: list) -> list:
    """解析一个 Module 内的所有听力条目。"""
    items = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]

        # --- 听答题：N. Woman: ... 然后紧跟 (A)-(D)
        m = CR_ITEM.match(ln)
        if m:
            num = int(m.group(1))
            stem = f"{m.group(2)}: {m.group(3)}".strip()
            opts, j, _ = collect_options(lines, i + 1, n)
            if len(opts) == 4:
                items.append({"kind": "choose_response", "number": num,
                              "prompt": stem, "options": opts})
                i = j
                continue

        # --- 带原文的三类：Listen to ...
        mp = PROMPT.match(ln)
        if mp:
            kind = kind_of(ln)
            prompt = ln.strip()
            j = i + 1
            transcript = []
            # 收原文，直到遇到第一道题（编号题，或"问句 + (A)"这种无编号题）
            while j < n:
                if QNUM.match(lines[j]) and not CR_ITEM.match(lines[j]):
                    break
                if PROMPT.match(lines[j]):
                    break
                if is_question_head(lines, j, n):
                    break
                ms = SPEAKER.match(lines[j])
                if ms:
                    transcript.append(f"{ms.group(1)}: {ms.group(2)}".strip())
                elif lines[j].strip():
                    if transcript:
                        transcript[-1] += " " + lines[j].strip()
                    else:
                        transcript.append(lines[j].strip())
                j += 1
            # 收题目：教师卷 3–5 的题号在 pdftotext 里丢失，需支持无编号题
            qs = []
            while j < n:
                if PROMPT.match(lines[j]):
                    break
                mq = QNUM.match(lines[j])
                unnumbered = mq is None and is_question_head(lines, j, n)
                if mq or unnumbered:
                    if mq:
                        qnum = int(mq.group(1))
                        qtext = mq.group(2).strip()
                    else:
                        qnum = None
                        qtext = lines[j].strip()
                        # 无编号题可能换行：把紧邻的前几行续上（跳过空行）
                        back, b = [], j - 1
                        while b >= 0 and len(back) < 3:
                            cand = lines[b]
                            if not cand.strip():
                                b -= 1
                                continue
                            if (OPT.match(cand) or PROMPT.match(cand)
                                    or QNUM.match(cand) or SPEAKER.match(cand)):
                                break
                            # 只续接明显被折行的题干：整句结尾（. ! ?）说明是原文段落，不要吞进来
                            if cand.strip()[-1:] in ".!?":
                                break
                            back.insert(0, cand.strip())
                            b -= 1
                        if back:
                            qtext = " ".join(back + [qtext])
                    opts, k, overflow = collect_options(lines, j + 1, n)
                    if overflow:
                        qtext += " " + " ".join(overflow)
                    if opts:
                        qs.append({"number": qnum, "question": qtext.strip(),
                                   "options": opts})
                        j = k
                        continue
                j += 1
            if transcript:
                items.append({"kind": kind, "prompt": prompt,
                              "transcript": transcript, "questions": qs})
            i = j
            continue
        i += 1
    return items


def main():
    files = sorted(glob.glob(os.path.join(TXT, "*.txt")))
    if not files:
        sys.exit(f"未找到文本文件，请先运行 pdftotext -layout：{TXT}")
    tests = []
    for f in files:
        s = open(f, encoding="utf-8", errors="replace").read()
        m = re.search(r"Listening Section(.*?)(?=Speaking Section)", s, re.S)
        if not m:
            print(f"  ! 跳过（未找到听力 section）：{os.path.basename(f)}")
            continue
        section = m.group(1)
        keys = parse_answer_keys(section)

        # 教师卷把 "Listening Section, Module N" 当页眉重复印在每一页，
        # 因此不能按它切分；改为单遍扫描 + 记住最近一次出现的 Module 号。
        MODHDR = re.compile(r"^\s*Listening Section,\s*Module\s*(\d)\s*$")
        buckets = {}   # module -> 行缓冲
        cur = None
        for ln in strip_noise(section):
            mh = MODHDR.match(ln)
            if mh:
                cur = int(mh.group(1))
                buckets.setdefault(cur, [])
                continue
            if cur is not None:
                buckets[cur].append(ln)

        modules = []
        for n_i, mod_no in enumerate(sorted(buckets)):
            items = parse_module(buckets[mod_no])
            renumber(items)
            key = keys[n_i] if n_i < len(keys) else {}
            for it in items:
                if it["kind"] == "choose_response":
                    it["answer"] = key.get(it["number"])
                else:
                    for q in it["questions"]:
                        q["answer"] = key.get(q["number"])
            modules.append({"module": mod_no, "items": items})
        tests.append({
            "test": os.path.basename(f).replace(".txt", ""),
            "modules": modules,
        })

    data = {
        "_meta": {
            "source": "ETS 官方免费 2026 对版练习卷（2 套学生用 + 5 套教师用）",
            "origin": "https://www.ets.org/content/dam/ets-org/pdfs/toefl/",
            "notice": "PDF 原文：This practice test aligns with TOEFL iBT tests from January 21, 2026. "
                      "Copyright © 2025 by ETS. 非退役真题，是 ETS 自制的对版官方练习卷。",
            "extracted": "2026-08-31",
            "audio": "音频在同目录 *-audio*.zip 内，.ogg 格式；"
                     "Listening1_/Listening2_ 前缀对应 Module 1（Router）与 Module 2（自适应分支）。",
        },
        "tests": tests,
    }
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 统计
    from collections import Counter
    c = Counter()
    nq = 0
    for t in tests:
        for mo in t["modules"]:
            for it in mo["items"]:
                c[it["kind"]] += 1
                if it["kind"] == "choose_response":
                    nq += 1 if it.get("answer") else 0
                else:
                    nq += sum(1 for q in it["questions"] if q.get("answer"))
    print(f"卷数 {len(tests)}")
    for k, v in sorted(c.items()):
        print(f"  {k:<16} {v}")
    print(f"带答案的题目数 {nq}")
    print(f"输出 {OUT}")


if __name__ == "__main__":
    main()
