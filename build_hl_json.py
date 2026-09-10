# -*- coding: utf-8 -*-
"""Build TOEFL lecture difficult-phrase highlight JSON files."""
import json, os, re, sys

SRC_DIR = "/tmp/hl_src"
OUT_DIR = "/tmp/hl_out"

# line number -> list of phrases (case-insensitive; actual form taken from source)
ANNOTATIONS = {
    "p113_TPO-07_C2.txt": {
        3: ["student orientation", "pointers"],
        11: ["concentrate in"],
        13: ["transfer student"],
        16: ["loan period"],
        17: ["inter-library loan service"],
        18: ["get hold"],
        22: ["way in advance"],
        27: ["hook it up"],
        29: ["plug it in"],
        33: ["photocopiers"],
        35: ["copy card"],
        41: ["rare books"],
        44: ["access"],
    },
    "p114_TPO-07_C1.txt": {
        17: ["overheard"],
        20: ["Dean"],
        22: ["Anthropology Department", "bulletin board"],
        27: ["pitch in"],
        28: ["low-key", "flashy"],
        33: ["got it covered"],
        38: ["compiling"],
        39: ["glory"],
        43: ["kinda"],
        47: ["field research"],
        50: ["versatile"],
        51: ["ethnology"],
        52: ["speciation"],
        53: ["uninformed"],
        55: ["distinct species", "populations", "isolated"],
        57: ["linguistic"],
    },
    "p115_TPO-06_L4.txt": {
        2: ["drastic"],
        3: ["occurrences"],
        9: ["tropical paradise"],
        19: ["greenery"],
        20: ["un-desert-like", "pre-historic art", "hippopotamuses"],
        21: ["hippos", "hence"],
        23: ["year round"],
        27: ["in principle"],
        29: ["aquifers"],
        36: ["fossilized pollen", "shrubs"],
        40: ["vegetated"],
        46: ["literature", "monsoon"],
        51: ["monsoon", "seasonal wind"],
        54: ["dynamics"],
        55: ["tilting"],
        56: ["parameters"],
        57: ["gradual variations", "abrupt"],
        60: ["compounded"],
        64: ["runaway drying effect"],
        66: ["vegetation", "in turn"],
        67: ["retain"],
        68: ["moisture", "evaporate"],
        81: ["flourish"],
        83: ["hypothesize", "temporary drought"],
        84: ["impetus"],
        85: ["stay tuned"],
    },
    "p116_TPO-06_L3.txt": {
        3: ["come up with", "character sketch"],
        11: ["pull them from thin air"],
        13: ["traits", "attributes"],
        23: ["bits and pieces"],
        24: ["sketch out"],
        26: ["formulate"],
        28: ["dominant attributes"],
        30: ["solidify"],
        37: ["defer to"],
        47: ["portray"],
        58: ["setting"],
        59: ["pitfall"],
        60: ["stereotype"],
        64: ["cliché", "ragged mountain dweller"],
        65: ["throw out", "terminology"],
        69: ["round characters"],
        70: ["flat"],
        79: ["show off"],
        85: ["humiliates"],
    },
}

def parse_source(path):
    """Return {line_no: sentence} from 'N|sentence' lines."""
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.rstrip("\n")
            m = re.match(r"^(\d+)\|(.*)$", raw)
            if m:
                out[int(m.group(1))] = m.group(2)
    return out

def build(fname):
    sentences = parse_source(os.path.join(SRC_DIR, fname))
    cues = []
    for lineno, phrases in sorted(ANNOTATIONS[fname].items()):
        sentence = sentences.get(lineno)
        if sentence is None:
            sys.exit(f"ERROR: line {lineno} not found in {fname}")
        actual = []
        for p in phrases:
            m = re.search(re.escape(p), sentence, re.IGNORECASE)
            if not m:
                sys.exit(f"ERROR: phrase '{p}' not in line {lineno} of {fname}\n  sentence: {sentence}")
            actual.append(m.group(0))
        cues.append({"line": lineno, "sentence": sentence, "phrases": actual})
    return {"file": fname, "cues": cues}

os.makedirs(OUT_DIR, exist_ok=True)
for fname in ANNOTATIONS:
    data = build(fname)
    with open(os.path.join(OUT_DIR, fname.replace(".txt", ".json")), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"OK {fname}: {len(data['cues'])} lines flagged")
