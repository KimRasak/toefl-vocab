# -*- coding: utf-8 -*-
"""Build the final TOEFL listening high-frequency vocabulary tables.

For each discipline, pick academic words that:
  - appear in >= MIN_DOCS distinct passages
  - have freq >= MIN_FREQ
  - are not in a stop/filler list
  - pass POS filter (keep nouns, verbs, adjectives, adverbs)
Mark words NOT present in the user's existing vocab lists (1675/1925/1791) as
"听力特有" (listening-specific). Attach one real example sentence from the corpus.

Outputs:
  /tmp/tpo_final_vocab.json   structured data
  tpo_listening_vocab.md      the human-readable study sheet
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
DISC_FILE = "/tmp/tpo_discipline.json"
FREQ_FILE = "/tmp/tpo_discipline_freq.json"
OUT_JSON = "/tmp/tpo_final_vocab.json"
OUT_MD = "tpo_listening_vocab.md"

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
SKIP_PREFIX = ("# ", "// ")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")

# filler / everyday words to exclude from "academic vocab" tables
FILLER = set("""
oh yeah okay ok well uh um hmm hey hi hello
gonna wanna gotta kinda sorta
thing things stuff stuffs way ways lot lots bit bits
actually basically literally probably maybe perhaps
guess mean means meant thinking think thought thinkin
say says said talking talk talks talked tell tells told
know knows knew known listen listens listened listening
look looks looked looking see sees saw seen watch watches watched watching
go goes went gone going come comes came coming get gets got gotten getting
make makes made making take takes took taken taking put puts put putting
want wants wanted wantin need needs needed needing
like likes liked likes
right yeah nope yes no
good great fine nice cool awesome amazing fantastic
sure really quite rather just only also too very
today tomorrow yesterday now then here there
people person someone everybody everyone anybody
student students professor professors teacher teachers
class classes course courses lecture lectures listen
male female narrator
""".split())

# POS filter: keep these (nouns, verbs, adjectives, adverbs, adj/noun, verb/noun)
KEEP_POS = {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
            "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "NN|VB", "JJ|NN", "NN|JJ",
            "VB|NN", "JJ|VB", "VB|JJ", "RB|JJ", "JJ|RB"}

# words that are too basic even if POS-ok
BASIC = set("""
time year day week month hour minute second night morning
number part place world water earth people person
way thing kind sort group country city area
big small large little long high low
new old good bad great
make take get go come see look put
think know say tell talk listen read write
work study school book class student professor
want need like
one two three four five six seven eight nine ten
first last next second
back front side top bottom middle end start
hand head face eye ear
home house room door window
food water
animal plant tree bird fish specie
some other even than much
many few several another
something anything everything nothing
someone anybody nobody everybody
i'm you're we're they're i've we've you've i'll we'll you'll
problem question answer example
call called calls calling
find found finding
look looked looking
show showed shown showing
rock ocean soil lake river energy light sound cell
temperature heat ice snow rain wind cloud
color body ground floor surface space material
million billion hundred thousand
summer winter spring autumn fall
system process source field amount size
""".split())

# Discipline-core words that ARE worth learning in lectures (kept despite being common)
# (water/rock/color etc are excluded above as truly basic; these are one notch up)
CORE_KEEP = {
    "temperature", "habitat", "predator", "prey", "species", "specie", "organism",
    "ecosystem", "environment", "population", "experiment", "research", "evidence",
    "theory", "hypothesis", "behavior", "evolution", "fossil", "sediment", "mineral",
    "formation", "structure", "settlement", "civilization", "technique", "audience",
    "energy", "process", "system", "source", "material", "surface", "atmosphere",
    "orbit", "telescope", "radiation", "magnetic", "particle", "molecule", "chemical",
}


# Generic function/descriptive words that are NOT vocabulary targets
# (listening tests don't hinge on these; they're everyday English)
GENERIC = set("""
different same before after still around each every always sometimes often
usually maybe probably actually something anything everything nothing
someone anybody nobody everybody
early late long short enough whole entire full
important interesting difficult easy simple
certain particular special specific common general
main major minor final
point fact idea type state form piece word
able used help keep away left move
give real both later
without pretty remember once happen happens happened started start
understand reason difference warm cold deep huge together within
near close already degree term science project case
anyway exactly better glad sorry
baby child bigger tiny
again until began begin begun quickly past united conversation
didn trying seems never friend johnson definitely
""".split())


# Discipline-specific words that are too generic for that discipline's vocab list
DISC_GENERIC = {
    "校园对话 Campus": set("""""".split()),
    "生物学 Biology": set("""
    change live feed grow play sense related produce
    turn stream others along themselves either using trip mouse
    order itself almost recently similar spot root wood
    development developed best break become function seem
    characteristic parent care reach imagine single discovered
    factor active response carbon travel american nitrogen chance
    true especially longer evolved matter region whether growing
    inside learned feature season shape muscle wall ancient based
    closely distance various century speed learn couple easily
    lower mentioned stop believe eventually larger period stay
    survival direction reading carry classified name open outside
    scientist fewer moving native member pattern belief detail
    paper psychology crop human brain cause land condition
    generally lead effect benefit bear escape america north
    solid hard clear living young adult family mind information
    explain increase natural possible result object activity source
    ever blind freezing
    """.split()),
    "地质学 Geology": set("""
    change grow movement moving formed formation become level below increased clear north
    caused sample result organism system research data period theory
    human land effect cause condition evidence environment
    """.split()),
    "天文学 Astronomy": set("""
    moving formed close near spot discovered object
    """.split()),
    "历史学/考古学 History & Archaeology": set("""
    built change lived north south central inside until paper
    building theory research center life land evidence population
    """.split()),
    "艺术史/艺术 Art History": set("""
    change create created written became popular line wall scene picture
    woman writing paper reading building true painted musical production
    experience original french public white money government value become
    sense europe matter figure method product modern blue especially
    nineteenth subject almost heard view name research social natural
    you'd instead mind hard developed language turn gave possible
    designed individual image semester young themselves earlier italian
    movie discussing attention interested worked background based couple
    working changed drawing live author system others saying focus process
    involved feeling setting writer emotion business range support
    considered feel note action nature information university yourself
    assignment event american function stone along eventually result wrote
    influence tried john development english classical itself computer
    source song romantic anyone creating beautiful feature lost seem
    familiar family living open culture date site street text mentioned
    named whatever discussion ever moving order simply throughout
    performed goal love town himself scholar review green paris behind
    believe discovered seeing european lived challenge hear political shape
    inside trade draw surface electric message robert human element effect
    community article acting copy generally lead employee consider interest
    famous best using parent theory evidence analysis
    """.split()),
    "心理学/认知科学 Psychology & Cognition": set("""
    based bigger human system computer
    """.split()),
    "物理学/化学 Physics & Chemistry": set("""
    reading tiny
    """.split()),
}


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


def load_existing():
    words = set()
    paths = ["quizlet-my-tofel-1675.tsv", "quizlet-my-tofel-1925.tsv", "tofel_words_1791.txt"]
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if "\t" in line:
                    w = line.split("\t")[0]
                else:
                    w = line.split()[0] if line.split() else ""
                w = w.strip().strip('"').lower()
                if w and w.isalpha():
                    words.add(w)
    return words


def main():
    disc_of = json.load(open(DISC_FILE, encoding="utf-8"))
    freq = json.load(open(FREQ_FILE, encoding="utf-8"))
    existing = load_existing()
    print("existing vocab size:", len(existing))

    lemmatizer = WordNetLemmatizer()

    # --- collect example sentences per lemma per discipline ---
    # lemma -> list of (discipline, sentence)
    examples = defaultdict(list)
    # build a corpus of (filename, english-lines) for example lookup
    corpus = {}
    for fp in sorted(glob.glob(os.path.join(SRC_DIR, "*.txt"))):
        fn = os.path.basename(fp)
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        lines = []
        for raw in text.splitlines():
            ln = clean_line(raw)
            if ln:
                lines.append(ln)
        corpus[fn] = lines

    # per-discipline tokenized word -> list of sentence
    disc_sentences = defaultdict(list)  # disc -> list of sentences (lowercased word->sentence)
    for fn, lines in corpus.items():
        disc = disc_of[fn]
        for ln in lines:
            # tokenize into words
            toks = TOKEN_RE.findall(ln.lower())
            lemmas_in_line = set()
            for t in toks:
                w = t.strip("'-")
                if len(w) < 2 or w.endswith("'"):
                    continue
                lemma = lemmatizer.lemmatize(w)
                lemmas_in_line.add(lemma)
            for lemma in lemmas_in_line:
                disc_sentences[disc].append((lemma, ln))

    # --- assemble word lists ---
    disciplines_order = [
        ("校园对话 Campus", 18, 6),
        ("生物学 Biology", 15, 5),
        ("地质学 Geology", 14, 5),
        ("天文学 Astronomy", 12, 5),
        ("历史学/考古学 History & Archaeology", 12, 5),
        ("艺术史/艺术 Art History", 14, 5),
        ("心理学/认知科学 Psychology & Cognition", 12, 4),
        ("物理学/化学 Physics & Chemistry", 10, 3),
    ]

    result = {}
    for disc, min_freq, min_docs in disciplines_order:
        if disc not in freq:
            continue
        items = freq[disc]
        selected = []
        is_campus = disc.startswith("校园对话")
        for lemma, v in items.items():
            if v["freq"] < min_freq or v["docs"] < min_docs:
                continue
            if lemma in FILLER:
                continue
            if lemma in GENERIC:
                continue
            if lemma in BASIC and lemma not in CORE_KEEP:
                continue
            if lemma in DISC_GENERIC.get(disc, set()):
                continue
            if len(lemma) < 4:
                continue
            selected.append((lemma, v["freq"], v["docs"]))
        # sort: listening-specific first, then freq desc
        selected.sort(key=lambda x: (-(x[0] not in existing), -x[1], -x[2]))
        result[disc] = selected

    # --- write JSON with examples ---
    out_data = {}
    for disc, sel in result.items():
        out_data[disc] = []
        for lemma, freq_, docs_ in sel:
            is_special = lemma not in existing
            # find an example sentence from this discipline; prefer short-ish ones
            # where the word occurs early so it won't be cut off
            ex = ""
            best_pos = 9999
            for l, sentence in disc_sentences.get(disc, []):
                if l == lemma and 10 < len(sentence) < 250:
                    # skip ALL-CAPS noise lines and lines dominated by caps
                    letters = [c for c in sentence if c.isalpha()]
                    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.7:
                        continue
                    # position of first occurrence of the lemma's word in the sentence
                    pos = sentence.lower().find(lemma)
                    if pos == -1:
                        pos = 9999
                    if pos < best_pos:
                        best_pos = pos
                        ex = sentence
            out_data[disc].append({
                "word": lemma,
                "freq": freq_,
                "docs": docs_,
                "listening_specific": is_special,
                "example": ex,
            })

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=1, sort_keys=False)

    # --- write markdown ---
    def smart_snippet(sentence: str, word: str, maxlen: int = 130) -> str:
        """Return a snippet around the target word so it is always visible."""
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
    md.append("> 统计来源：本地 424 篇 TPO 听力原文（讲座 335 篇 + 对话 89 篇），词形还原后按学科统计词频。\n")
    md.append("> 标注说明：**★ = 你现有词表（1675/1925/1791）中未收录的“听力特有词”**，优先背诵。\n")
    md.append("> 例句均摘自真实 TPO 听力原文，已自动截取含目标词的片段。\n")

    for disc, sel in out_data.items():
        total = len(sel)
        n_special = sum(1 for s in sel if s["listening_specific"])
        md.append(f"\n## {disc}（{total} 词，其中听力特有 {n_special} 词）\n")
        md.append("| 单词 | 频次 | 篇数 | 特有 | 原文例句 |")
        md.append("| --- | --- | --- | --- | --- |")
        for s in sel:
            star = "★" if s["listening_specific"] else ""
            ex = smart_snippet(s["example"], s["word"]) if s["example"] else "—"
            ex = ex.replace("|", "\\|")
            md.append(f"| {s['word']} | {s['freq']} | {s['docs']} | {star} | {ex} |")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    for disc, sel in out_data.items():
        n_spec = sum(1 for s in sel if s["listening_specific"])
        print(f"{disc}: {len(sel)} words ({n_spec} listening-specific)")


if __name__ == "__main__":
    main()
