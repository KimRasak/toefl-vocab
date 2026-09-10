# -*- coding: utf-8 -*-
"""Extract pure-English speech from TPO listening transcripts.

Each transcript line looks like:
    [[00:00.00]] NARRATOR: Listen to a conversation ...
          旁白：请听一段...
or a plain English line (no timestamp) followed by a Chinese translation line.

We keep only the English side: lines with a timestamp or English content,
dropping the Chinese translation line that immediately follows.
"""
import glob
import os
import re
import sys

SRC_DIR = "TPO_listening/transcripts"
OUT_FILE = "/tmp/tpo_listening_corpus.txt"

# Chinese-range regex: covers CJK unified ideographs, full-width forms, etc.
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
# Lines that are purely metadata / narration cues we don't need
SKIP_PREFIX = ("# ", "// ", "NARRATOR:", "Narrator:")

EN_COUNT = 0
CH_COUNT = 0


def looks_chinese(line: str) -> bool:
    return bool(CJK_RE.search(line))


def clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if line.startswith(SKIP_PREFIX):
        return ""
    # strip timestamp
    line = re.sub(r"^\[\[\d{1,2}:\d{2}(?:\.\d{1,3})?\]\]\s*", "", line)
    # strip speaker prefix like "MALE PROFESSOR:" / "FEMALE STUDENT:"
    line = re.sub(r"^(?:[A-Z]+ )*[A-Z][A-Z ]*:\s*", "", line)
    # drop anything that's still mostly Chinese
    if looks_chinese(line):
        return ""
    # normalize whitespace
    line = " ".join(line.split())
    return line


def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.txt")))
    if not files:
        print("no transcript files found", file=sys.stderr)
        sys.exit(1)
    print(f"{len(files)} transcript files")

    out_lines = []
    global EN_COUNT, CH_COUNT
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        # Some transcripts may not be line-oriented; split robustly.
        raw_lines = text.splitlines()
        for raw in raw_lines:
            ln = clean_line(raw)
            if not ln:
                continue
            if looks_chinese(ln):
                CH_COUNT += 1
                continue
            out_lines.append(ln)
            EN_COUNT += 1

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")

    print(f"english lines: {EN_COUNT}, dropped chinese lines: {CH_COUNT}")
    print(f"output: {OUT_FILE}")


if __name__ == "__main__":
    main()
