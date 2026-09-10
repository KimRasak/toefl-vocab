# -*- coding: utf-8 -*-
"""Merge subagent-generated definitions into the final vocab Markdown + JSON.

Inputs:
  /tmp/tpo_def/covered.json   existing defs (word -> def)
  /tmp/tpo_def/groups_4/*.tsv subagent outputs (word<TAB>/ipa/<TAB>def)
  /tmp/tpo_final_vocab.json   vocab data with freq/docs/example
Output:
  tpo_listening_vocab.md      final study sheet
  tpo_listening_vocab.json    final structured data
"""
import glob
import json
import os
import re

FINAL = "/tmp/tpo_final_vocab.json"
COVERED = "/tmp/tpo_def/covered.json"
DEF_DIR = "/tmp/tpo_def"
OUT_MD = "tpo_listening_vocab.md"
OUT_JSON = "tpo_listening_vocab.json"


def parse_def_line(line: str):
    """Parse 'word<TAB>/ipa/<TAB>def' or 'word<TAB>/ipa/<TAB>def'."""
    line = line.strip()
    if not line:
        return None
    parts = line.split("\t")
    if len(parts) < 3:
        return None
    word, ipa, meaning = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if not word or not meaning:
        return None
    return word.lower(), ipa, meaning


def load_subagent_defs():
    defs = {}
    for fp in glob.glob(os.path.join(DEF_DIR, "def_*.tsv")):
        with open(fp, encoding="utf-8") as f:
            for line in f:
                r = parse_def_line(line)
                if r:
                    w, ipa, meaning = r
                    if w not in defs:
                        defs[w] = {"ipa": ipa, "def": meaning}
    return defs


def main():
    data = json.load(open(FINAL, encoding="utf-8"))
    covered = json.load(open(COVERED, encoding="utf-8"))
    sub_defs = load_subagent_defs()
    print("subagent defs loaded:", len(sub_defs))

    # merge: existing covered first, then subagent
    merged = {}
    for w, d in covered.items():
        merged[w] = {"ipa": "", "def": d}
    for w, d in sub_defs.items():
        merged[w] = d
    # specie is the WordNet lemma of "species" — reuse its def (incl. IPA)
    if "species" in merged:
        if "specie" not in merged:
            merged["specie"] = merged["species"]
        elif not merged["specie"].get("ipa") and merged["species"].get("ipa"):
            merged["specie"]["ipa"] = merged["species"]["ipa"]

    missing = []
    for disc, rows in data.items():
        for r in rows:
            if r["word"] not in merged:
                missing.append(r["word"])
    missing = sorted(set(missing))
    print("words still missing def:", len(missing))
    if missing:
        print("  ", ", ".join(missing))

    # --- write final JSON ---
    out_json = {}
    for disc, rows in data.items():
        out_json[disc] = []
        for r in rows:
            w = r["word"]
            info = merged.get(w, {"ipa": "", "def": ""})
            out_json[disc].append({
                "word": w,
                "ipa": info.get("ipa", ""),
                "def": info.get("def", ""),
                "freq": r["freq"],
                "docs": r["docs"],
                "listening_specific": r["listening_specific"],
                "example": r["example"],
            })
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_json, f, ensure_ascii=False, indent=1, sort_keys=False)

    # --- write final Markdown ---
    def smart_snippet(sentence, word, maxlen=130):
        low = sentence.lower()
        pos = low.find(word)
        if pos == -1:
            return sentence[:maxlen] + ("..." if len(sentence) > maxlen else "")
        start = max(0, pos - 25)
        end = min(len(sentence), pos + len(word) + 55)
        snip = sentence[start:end]
        if start > 0:
            snip = "…" + snip
        if end < len(sentence):
            snip = snip + "…"
        return snip

    md = []
    md.append("# 托福听力高频词汇表（基于 TPO 1–58 / 60–75 真实听力原文统计）\n")
    md.append("> **统计来源**：本地 424 篇 TPO 听力原文（讲座 335 篇 + 对话 89 篇），词形还原后按学科统计词频与跨篇分布。\n")
    md.append("> **排序说明**：每学科内按“出现篇数 × 词频”综合排序，★ = 你现有词表（1675/1925/1791）未收录的**听力特有词**，优先背诵。\n")
    md.append("> **例句**：均摘自真实 TPO 听力原文，自动截取含目标词的片段。\n")
    md.append("> **音标**：美式 IPA。\n")
    md.append("> **使用方法**：先过一遍 ★ 词，再精听对应学科讲座时主动捕捉这些词；对话部分侧重校园场景词。\n")

    stats_total = 0
    for disc, rows in out_json.items():
        stats_total += len(rows)
    md.append(f"\n---\n\n**共 {stats_total} 词**。\n")

    for disc, rows in out_json.items():
        n_special = sum(1 for r in rows if r["listening_specific"])
        md.append(f"\n## {disc}（{len(rows)} 词，★特有 {n_special}）\n")
        md.append("| 单词 | 音标 | 释义 | 频次 | 篇数 | 特有 | 原文例句 |")
        md.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in rows:
            star = "★" if r["listening_specific"] else ""
            ipa = r["ipa"] or "—"
            meaning = r["def"] or "—"
            meaning = meaning.replace("|", "\\|")
            ex = smart_snippet(r["example"], r["word"]) if r["example"] else "—"
            ex = ex.replace("|", "\\|")
            md.append(f"| {r['word']} | {ipa} | {meaning} | {r['freq']} | {r['docs']} | {star} | {ex} |")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("wrote", OUT_MD, "and", OUT_JSON)


if __name__ == "__main__":
    main()
