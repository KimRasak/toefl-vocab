# -*- coding: utf-8 -*-
"""Assign each TPO lecture/conversation a subject discipline based on its title,
then compute per-discipline high-frequency words.

Outputs:
  /tmp/tpo_discipline.json        {filename: discipline}
  /tmp/tpo_discipline_freq.json   {discipline: {lemma: {freq, docs, top_form}}}
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
OUT_DISC = "/tmp/tpo_discipline.json"
OUT_FREQ = "/tmp/tpo_discipline_freq.json"

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
more most least less
up down out off
thing things stuff way ways lot lots bit kind kinds sort sorts
actually basically really probably maybe perhaps
gonna wanna gotta
one two three four five six seven eight nine ten
first second third next last
""".split())


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


# Discipline classifier: keyword -> discipline, checked in order (first match wins)
DISCIPLINE_RULES = [
    # (discipline, [keywords])
    ("天文学 Astronomy", ["planet", "star", "galax", "comet", "astronom", "solar", "universe",
                          "sun", "moon", "saturn", "venus", "uranium", "exoplanet", "aurora",
                          "helio", "meteor", "asteroid", "cosmic", "earth radiation", "heliu",
                          "interferometer", "zircon", "51 pegasi", "crater", "geocentric",
                          "bode", "faint young sun", "gas planet", "cme", "snowflake and ozone",
                          "the discovery of 51", "aurora's", "comets"]),
    ("地质学 Geology", ["geology", "rock", "soil", "glacier", "volcano", "sediment", "climate",
                        "earthquake", "mineral", "fossil", "erosion", "cave", "desert", "lake",
                        "ocean", "sea", "river", "ice", "plate", "continental", "formation of",
                        "hydrothermal", "geologic", "milankovitch", "permian", "sahara",
                        "tundra", "microclimate", "sand", "cape cod", "copper basin",
                        "petroleum", "soil formation", "water", "copper", "jarosite",
                        "paleo", "meteorite", "geothermal", "glacial movement",
                        "interglacial", "greenhouse effect", "role of wind", "thaw lake",
                        "ice age", "earth's", "origin of life", "continental polar",
                        "cape cod house", "soil", "shields", "flood", "canyon",
                        "formation of some special volcanos", "ocean energy", "iceland",
                        "craters and age", "encounter of galaxies", "snowflakes and ozone"]),
    ("生物学 Biology", ["animal", "plant", "species", "evolution", "bird", "insect", "fish",
                        "cell", "gene", "ecosystem", "mammal", "reptile", "frog", "whale",
                        "octopus", "dolphin", "bat", "coral", "fungi", "pollinator", "marmot",
                        "beaver", "hare", "albatross", "reindeer", "lizard", "sauropod",
                        "oviraptor", "t-cell", "bacteria", "virus", "organism", "biology",
                        "migration", "habitat", "behavior", "endotherm", "ectotherm",
                        "maize", "teosinte", "banana", "hemp", "oak", "shrub", "tree",
                        "leaf", "photosynthesis", "carbon", "zooplankton", "notothenioid",
                        "gila", "fiddler", "bower", "maple", "domestication", "dinosaur",
                        "archaeopteryx", "megafauna", "rewilding", "displacement activity",
                        "foraging", "navigation system", "homing", "vocalization",
                        "theory of mind", "sleep", "neocortex", "salt marsh", "snowshoe",
                        "phosphorus cycle", "biological community", "interrelationships",
                        "gause", "mutualism", "classification of creatures", "pest",
                        "decaffeinating", "lens of human eyes", "organic compounds",
                        "resilience", "vegetation discoloration", "tulip-breaking",
                        "migration of zooplankton", "algae", "reverberation", "cognition",
                        "animal behavior patterns", "fish movement", "warm blooded",
                        "dinosaurs are warm", "fiddler crab", "maple sap", "infant communication",
                        "mammals", "neocortex size", "courting behavior", "bower bird",
                        "origin of life", "gila lizard", "two kinds of pollution",
                        "distraction display", "distraction", "crocodile", "oviraptor"]),
    ("艺术史/艺术 Art History", ["art", "painting", "artist", "music", "sculpture", "museum",
                        "theater", "dance", "film", "photography", "architect", "opera",
                        "piano", "violin", "guitar", "fresco", "pottery", "glass", "stained",
                        "renaissance", "impression", "realism", "portrait", "still-life",
                        "modern", "dada", "photograph", "poetry", "literature", "novel",
                        "author", "story", "poem", "writing", "play", "drama", "folk tale",
                        "fairy tale", "memoir", "autobiography", "theater", "broadway",
                        "movie", "screen dance", "audubon", "seuss", "pollock", "okeefe",
                        "emerson", "thoreau", "aristotle", "hemingway", "artists",
                        "wallpaper", "paint", "pigment", "architecture", "housing",
                        "building design", "suburb", "landscape architecture", "gardens",
                        "perspective", "hieroglyph", "illuminat", "cezanne", "beaux",
                        "bartok", "neel", "morrison", "greek sculptures", "statues",
                        "theater structure", "sound", "film industry", "hollywood",
                        "rose frantzen", "jean painleve", "character sketch", "chauvet",
                        "palimpsest", "archimedes palimpsest", "primary colors", "hernani",
                        "sentimental comedy", "method acting", "sounds in the film",
                        "community-determined film", "found sound", "congruent and incongruent",
                        "music in ancient greece", "electric guitar", "cremonese violins",
                        "piano", "renaissance gardens", "theodor seuss", "georgia o'keeffe",
                        "still-life painting", "how to convey a personal point of view in painting",
                        "new wallpaper designs", "perspective in painting", "vasari",
                        "copies of greek sculptures", "greece and roman statues", "opera",
                        "advertising", "green marketing", "the structure of theater",
                        "william wheatley and broadway theaters", "first public art museum",
                        "harlem renaissance", "how business leaders get political power",
                        "jackson pollock", "emotional connection", "preference in portrait painting",
                        "precious blue pigment", "american realism", "government support for arts",
                        "well-made play", "folk tales and fairy tales", "folk tales",
                        "medieval poetry", "music", "screen dance", "alice neel",
                        "harriet morrison", "cecilia beaux", "bela bartok", "formal analysis of art",
                        "ownership of works of art", "techniques used during the renaissance",
                        "frescos", "modern dance", "dadasim", "reverberation", "paintings",
                        "mural", "portrait painting", "sculptures", "photographs exhibited",
                        "photography", "museum", "jean painleve", "philippe jacques de loutherbour",
                        "character sketch", "perspective in painting", "emotional connection"]),
    ("历史学/考古学 History & Archaeology", ["ancient", "civilization", "century", "artifact",
                        "excavation", "empire", "dynasty", "history", "culture", "rome",
                        "egypt", "greece", "archeolog", "archaeolog", "indigenous", "clovis",
                        "iroquois", "inuits", "mayan", "maya", "olmec", "botai", "catalhoyuk",
                        "gonur", "pyramid", "hieroglyph", "settlement", "mound", "pottery",
                        "banana", "agriculture", "crop", "farming", "domesticat", "paleolithic",
                        "prehistoric", "passage grave", "state formation", "irwin",
                        "columbus", "new west", "harlem", "american", "political power",
                        "treaty", "government", "arctic cultures", "antikythera", "mechanism",
                        "calendar", "number system", "transmission", "tea", "spice", "trade",
                        "salt", "copper", "glass", "steel", "oil paint", "renaissance",
                        "the new west", "monarch", "king", "pharaoh", "hatshepsut",
                        "meme", "new guinea", "passage graves", "earliest permanent settlement",
                        "gonur-depe", "botai culture", "clovis people", "maya civilization",
                        "olmec civilization", "the houses of the inuit", "state formation",
                        "ancient egyptian calendar", "ancient egyptian glass", "egyptian hieroglyphs",
                        "great pyramid", "statue of hatshepsut", "history of tea", "spices",
                        "the copper basin", "copper", "ancient bananas", "american food crops",
                        "the new west", "harlem renaissance", "how business leaders get political power in 19th",
                        "two ancient arctic cultures", "earliest permanent settlement",
                        "a group of mostly undisturbed archaeological sites", "the transmission of a number system",
                        "seafarers and stars", "homeric", "illiad", "odyssey", "greek and roman statues",
                        "theodor seuss geisel", "christopher columbus", "international trade",
                        "pedestrian malls", "state formation", "plateau", "medieval",
                        "hearing and read the ancient text", "the statue of hatshepsut", "maya"]),
    ("心理学/认知科学 Psychology & Cognition", ["psycholog", "cognition", "memory", "child",
                        "behavior", "metacognition", "amnesia", "emotion", "perception",
                        "attention", "learning", "intelligence", "approximate number sense",
                        "theory of mind", "infant", "language acquisition", "vocabulary development",
                        "sleep", "cognition", "exercise and cognition", "advertising",
                        "consumer", "marketing", "green marketing", "brand", "economic",
                        "economy", "market", "business", "industry", "company", "management",
                        "infrastructure", "privatization", "trade", "service failure",
                        "leadership", "globalization", "childhood amnesia", "metacognition",
                        "infant communication and vocabulary development",
                        "investigations about infants' ability to retain information",
                        "foundationalism", "gricean maxims", "features of human language",
                        "psychological development", "emotional connection", "whether animals have a theory of mind",
                        "memoir", "autobiography and memoir", "reverberation", "how to convey a personal point of view",
                        "attention", "distraction", "cognition", "interrelationships",
                        "managing by wandering around", "the life cycle of innovation",
                        "software development", "things coaches should know", "service failures",
                        "montessori method", "boom and bust", "international trade",
                        "business", "economic", "economy"]),
    ("物理学/化学 Physics & Chemistry", ["physics", "chemist", "atom", "molecule", "carbon",
                        "chemical", "element", "radiation", "wave", "electron", "magnet",
                        "electric", "energy", "spectroscopy", "nanotube", "nanotechnolog",
                        "muon", "electromagnetic", "interferometer", "helium", "cellulose",
                        "organic compound", "periodic table", "spectrum", "faint young sun",
                        "ozone", "snowflake", "aurora", "cme", "radiation budget", "gas planet",
                        "uranium-lead", "uranium", "leaves turn color", "carbon cycling",
                        "carbon nanotubes", "electromagnetic waves", "an application of nanotechnology",
                        "benefits of muon detectors", "periodic table of elements",
                        "solar energy", "renewable energy sources", "greenhouse effect",
                        "snowflakes and ozone", "light", "color", "vision correction",
                        "the lens of human eyes", "spectroscopy", "comets", "earth radiation budget",
                        "potential alternative source of energy-cellulose",
                        "potential energy source - helium-3", "the formation of gas planets",
                        "organic compounds", "exoplanets", "aurora", "the process of aurora's formation",
                        "origin of life", "astronomy", "the discovery of 51 pegasi"]),
]

DISCIPLINE_FALLBACK = "校园对话 Campus"

# Title-based manual overrides for passages whose titles are too generic
MANUAL_OVERRIDES = {
    "tpo34 lec2 aps digestion": "生物学 Biology",          # digestion physiology
    "tpo70 lec1 to present a theory and an argument that refutes it": "心理学/认知科学 Psychology & Cognition",
}

# normalize: strip .txt, lowercase
def normalize(name: str) -> str:
    # strip common accents for keyword matching
    accent_map = {"é": "e", "è": "e", "ê": "e", "ë": "e", "á": "a", "à": "a",
                  "â": "a", "ä": "a", "í": "i", "î": "i", "ï": "i", "ó": "o",
                  "ò": "o", "ô": "o", "ö": "o", "ú": "u", "ù": "u", "û": "u",
                  "ü": "u", "ç": "c", "ñ": "n"}
    for a, b in accent_map.items():
        name = name.replace(a, b)
    return name


def classify(filename: str) -> str:
    name = os.path.basename(filename).lower().replace(".txt", "")
    name = name.replace("_", " ")  # match keywords containing spaces
    name = normalize(name)
    if name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[name]
    for disc, kws in DISCIPLINE_RULES:
        for kw in kws:
            if kw in name:
                return disc
    return DISCIPLINE_FALLBACK


def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.txt")))
    lemmatizer = WordNetLemmatizer()

    disc_of = {}
    disc_freq = defaultdict(Counter)          # disc -> lemma -> freq
    disc_docs = defaultdict(lambda: defaultdict(set))  # disc -> lemma -> set docidx

    docidx = 0
    for fp in files:
        disc = classify(fp)
        disc_of[os.path.basename(fp)] = disc
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        doc_lemmas = set()
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
                disc_freq[disc][lemma] += 1
                doc_lemmas.add(lemma)
        for lemma in doc_lemmas:
            disc_docs[disc][lemma].add(docidx)
        docidx += 1

    out_freq = {}
    for disc, counter in disc_freq.items():
        out_freq[disc] = {}
        for lemma, freq in counter.items():
            out_freq[disc][lemma] = {
                "freq": freq,
                "docs": len(disc_docs[disc][lemma]),
            }

    with open(OUT_DISC, "w", encoding="utf-8") as f:
        json.dump(disc_of, f, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT_FREQ, "w", encoding="utf-8") as f:
        json.dump(out_freq, f, ensure_ascii=False, indent=1, sort_keys=True)

    from collections import Counter as C
    dist = C(disc_of.values())
    print("discipline distribution:")
    for d, n in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {d}: {n} passages")
    print("outputs:", OUT_DISC, OUT_FREQ)


if __name__ == "__main__":
    main()
