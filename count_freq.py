# -*- coding: utf-8 -*-
"""Count word frequencies in TPO listening transcripts with lemmatization.

Reads each transcript file directly (so we keep document boundaries),
extracts the English side, and counts:
  - freq: total occurrences across the whole corpus
  - docs: in how many distinct passages (lectures/conversations) the word appears
Output: /tmp/tpo_word_freq.json
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

import nltk

NLTK_DATA = "/tmp/nltk_data"
nltk.data.path.insert(0, NLTK_DATA)

from nltk.stem import WordNetLemmatizer

SRC_DIR = "TPO_listening/transcripts"
OUT = "/tmp/tpo_word_freq.json"

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
SKIP_PREFIX = ("# ", "// ")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")

STOPWORDS = set("""
a an the and or but if then else when while because although though since unless
of in on at by with from to for as into onto upon about against between among
through during over under across beyond via
is are was were be been being am do does did done doing have has had having
i you he she it we they me him her us them my your his its our their mine yours hers ours theirs
this that these those there here
what which who whom whose where why how
can could will would shall should may might must
not no nor don't doesn't didn't isn't aren't wasn't weren't haven't hasn't hadn't
won't wouldn't can't couldn't shouldn't
yes yeah uh um okay ok well
very really quite rather just only also too so such
more most less least
up down out off
""".split())

# Common words that are NOT stopwords but mostly fillers in lectures
EXTRA_STOP = set("""
thing things stuff way ways lot lots bit kind kinds sort sorts
actually basically basically really probably maybe perhaps
gonna wanna gotta
""".split())
STOPWORDS |= EXTRA_STOP


def clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if line.startswith(SKIP_PREFIX):
        return ""
    line = re.sub(r"^\[\[\d{1,2}:\d{2}(?:\.\d{1,3})?\]\]\s*", "", line)
    line = re.sub(r"^(?:[A-Z]+ )*[A-Z][A-Z ]*:\s*", "", line)
    if CJK_RE.search(line):
        return ""
    return " ".join(line.split())


def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.txt")))
    lemmatizer = WordNetLemmatizer()
    word_counter = Counter()
    doc_counter = defaultdict(set)
    form_counter = defaultdict(Counter)

    total_docs = 0
    for fp in files:
        doc_idx = total_docs
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        doc_words = set()  # lemmas appearing in this doc
        for raw in text.splitlines():
            ln = clean_line(raw)
            if not ln:
                continue
            for tok in TOKEN_RE.findall(ln):
                w = tok.lower().strip("'-")
                if len(w) < 2 or w in STOPWORDS:
                    continue
                if w.endswith("'s"):
                    w = w[:-2]
                if not w or w in STOPWORDS:
                    continue
                lemma = lemmatizer.lemmatize(w)
                word_counter[lemma] += 1
                form_counter[lemma][w] += 1
                doc_words.add(lemma)
        for lemma in doc_words:
            doc_counter[lemma].add(doc_idx)
        total_docs += 1

    result = {}
    for lemma, freq in word_counter.items():
        result[lemma] = {
            "freq": freq,
            "docs": len(doc_counter[lemma]),
            "top_form": form_counter[lemma].most_common(1)[0][0],
        }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1, sort_keys=True)

    print(f"docs: {total_docs}, unique lemmas: {len(result)}")
    print(f"output: {OUT}")


if __name__ == "__main__":
    main()
