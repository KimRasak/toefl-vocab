# -*- coding: utf-8 -*-
"""Merge 1791 + 1925 + 1675 word lists → single HTML grouped by discipline.

Usage:  python build_merged_by_discipline.py
Output: merged-by-discipline/index.html
"""
import os, re, json
from collections import defaultdict

# Legacy source lists carry stress marks and typos in a few headwords; map them
# onto the real spelling so definitions merge and pronunciation lookups work.
WORD_ALIASES = {
    'con`duct': 'conduct',
    'con`tent': 'content',
    'con`tract': 'contract',
    'con`vict': 'convict',
    'discerm': 'discern',
    'figure-head': 'figurehead',
}


def canonical_word(word):
    word = (word or '').strip().lower()
    return WORD_ALIASES.get(word, word)

# Curated definition corrections and expansions.  This file is deliberately
# kept separate from the generated HTML so it can be reviewed and backed up.
DEFINITION_OVERRIDES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overrides.json')
try:
    with open(DEFINITION_OVERRIDES_PATH, encoding='utf-8') as _f:
        DEFINITION_OVERRIDES = {canonical_word(k): str(v).strip() for k, v in json.load(_f).items()}
except (FileNotFoundError, json.JSONDecodeError):
    DEFINITION_OVERRIDES = {}
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pos_overrides.json'), encoding='utf-8') as _f:
        POS_OVERRIDES = {canonical_word(k): str(v).strip() for k, v in json.load(_f).items()}
except (FileNotFoundError, json.JSONDecodeError):
    POS_OVERRIDES = {}
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pos_review_candidates.json'), encoding='utf-8') as _f:
        # Candidate reviews are lower priority than already audited overrides.
        POS_REVIEW_CANDIDATES = {canonical_word(k): str(v).strip() for k, v in json.load(_f).items()}
except (FileNotFoundError, json.JSONDecodeError):
    POS_REVIEW_CANDIDATES = {}
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'definition_corrections.json'), encoding='utf-8') as _f:
        # New corrections intentionally take precedence over the older review table.
        DEFINITION_OVERRIDES.update({canonical_word(k): str(v).strip() for k, v in json.load(_f).items()})
except (FileNotFoundError, json.JSONDecodeError):
    pass

# High-frequency discipline expansions are kept as a separate, reviewable
# source so topic growth does not get mixed with the legacy word lists.
HIGH_FREQ_DISCIPLINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'high_frequency_discipline_words.json')
try:
    with open(HIGH_FREQ_DISCIPLINE_PATH, encoding='utf-8') as _f:
        _high_freq_data = json.load(_f)
        HIGH_FREQ_WORDS = {canonical_word(k): str(v).strip() for k, v in _high_freq_data.get('words', {}).items()}
        HIGH_FREQ_TOPICS = {str(k).lower(): str(v) for k, v in _high_freq_data.get('topics', {}).items()}
except (FileNotFoundError, json.JSONDecodeError):
    HIGH_FREQ_WORDS, HIGH_FREQ_TOPICS = {}, {}

BASE = os.path.dirname(os.path.abspath(__file__))

# ── 2026 新格式听力 Academic Talk 真题学科词库 ──
# 权重来源：2026听力学科场景占比-2026-09-02.md（237 条去重讲座话题 / 29 个考试日）。
# 该文件按学科分组，因此词→学科的映射不必逐词重复书写。
EXAM2026_PATH = os.path.join(BASE, 'toefl2026_exam_terms.json')
EXAM2026_WORDS, EXAM2026_TOPICS, EXAM2026_GROUPS = {}, {}, {}
try:
    with open(EXAM2026_PATH, encoding='utf-8') as _f:
        _exam2026 = json.load(_f)
    for _g in _exam2026.get('groups', []):
        _topic = _g['topic']
        EXAM2026_GROUPS[_topic] = {
            'weight': _g.get('weight_2026'),
            'rank': _g.get('rank_2026'),
            'note': _g.get('weight_note', ''),
            'evidence': _g.get('evidence', ''),
        }
        for _w, _d in _g.get('words', {}).items():
            _cw = canonical_word(_w)
            EXAM2026_WORDS[_cw] = str(_d).strip()
            EXAM2026_TOPICS[_cw] = _topic
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    EXAM2026_WORDS, EXAM2026_TOPICS, EXAM2026_GROUPS = {}, {}, {}

# 每个页面学科在 2026 真实考场里的地位。
# weight = 该学科在 237 条 2026 讲座话题中的占比（%）；None = 2026 回忆件里没有独立出现。
# tier   = 复习优先级标签，直接决定页面上的徽章与「只看高频学科」筛选。
# note   = 口径说明；凡多个页面学科共享同一统计桶都必须写清楚，避免把占比读成互斥的。
TOPIC_2026 = {
    "艺术与文学 Art & Literature": (23.2, "讲座高频", "2026 第 1 大类：艺术/音乐 21.9% + 文学 1.3%（旧格式 19.8%）"),
    "考古与历史 Archaeology & History": (11.4, "讲座高频", "考古/人类学 6.3% + 历史 5.1%；与「人类学与社会学」共享考古/人类学"),
    "人类学与社会学 Anthropology & Sociology": (10.9, "讲座高频", "考古/人类学 6.3% + 社会学 4.6%；与「考古与历史」共享考古/人类学"),
    "经济与商业 Economics & Business": (10.1, "讲座高频", "旧格式仅 3.0% → 2026 翻三倍，涨幅最大的学科"),
    "科技与计算 Technology & Computing": (9.3, "讲座高频", "技术/工程 9.3%（仿生、纳米、发明史、GIS）；与「工具与劳动」共享"),
    "工具与劳动 Tools & Labor": (9.3, "讲座中频", "技术/工程 9.3% 里的发明与手工艺部分；与「科技与计算」共享"),
    "动物与生态 Zoology & Ecology": (7.2, "讲座中频", "生物/动物 7.2%（旧格式 21.1%，已腰斩但仍在考）；与「生物学」共享"),
    "生物学 Biology": (7.2, "讲座中频", "生物/动物 7.2%；与「动物与生态」共享"),
    "情绪与心理 Emotions & Psychology": (6.8, "讲座中频", "心理/认知 6.8%；官方 14 篇练习卷里心理+神经科学占 35.7%，是官方最偏重方向"),
    "心理健康 Mental Health": (6.8, "讲座中频", "心理/认知 6.8%；与「情绪与心理」共享"),
    "建筑与住所 Architecture & Dwellings": (5.9, "讲座中频", "城市规划/建筑 5.9%（工业城市改造、公共空间与意识形态）"),
    "环境科学 Environmental Science": (5.1, "讲座中频", "环境/生态 5.1%；官方练习卷里 environmental science 占 3/14"),
    "政治与社会制度 Politics & Social Systems": (4.6, "讲座中频", "社会学/社会科学 4.6%（soft power、公共政策）；与「人类学与社会学」共享"),
    "植物学 Botany": (4.2, "讲座低频", "植物/农业 4.2%；与「农业」共享"),
    "农业 Agriculture": (4.2, "讲座低频", "植物/农业 4.2%；与「植物学」共享"),
    "化学与材料 Chemistry & Materials": (3.4, "讲座低频", "化学/物理 3.4%（旧格式 8.7%）；与「物理学」共享"),
    "物理学 Physics": (3.4, "讲座低频", "化学/物理 3.4%；与「化学与材料」共享"),
    "地理与地质 Geography & Geology": (3.4, "讲座低频", "地质/地球科学 3.4%（旧格式 8.9%）"),
    "运动与流体 Motion & Fluids": (3.4, "讲座低频", "并入化学/物理 3.4% 统计"),
    "医学与健康 Medicine & Health": (1.7, "讲座低频", "医学/健康 1.7%"),
    "天文学 Astronomy": (1.7, "讲座低频", "旧格式 11.1% → 2026 仅 1.7%，掉幅最大的学科"),
    "语言与写作 Language & Writing": (1.3, "讲座低频", "语言/教育 1.3%；与「教育」共享"),
    "教育 Education": (1.3, "讲座低频", "语言/教育 1.3%；与「语言与写作」共享"),
    "气象与气候 Weather & Climate": (None, "讲座低频", "2026 回忆件里没有独立气象讲座，相关内容并入环境/地质"),
    "宗教与哲学 Religion & Philosophy": (None, "讲座低频", "2026 官方与回忆件均未出现；第三方新题库里出现过 philosophy class"),
    "数学与几何 Mathematics & Geometry": (None, "讲座低频", "2026 回忆件未出现独立数学讲座（阿拉伯数字那篇按历史归类）"),
    "法律与制度 Law & Governance": (None, "讲座低频", "2026 回忆件未出现独立法律讲座"),
    "军事 Military": (None, "讲座低频", "2026 回忆件未出现独立军事讲座"),
    "校园生活 Campus Life": (None, "对话·公告", "自适应低分支只有对话+公告、没有学术讲座，这部分全员必备"),
    "日常生活 Daily Life": (None, "对话·公告", "短对话与公告的主场景"),
    "社会关系 Social Relations": (None, "对话·公告", "听答题与短对话的高频语域"),
    "礼仪与情感 Etiquette & Emotions": (None, "对话·公告", "听答题最常考的应答语域"),
    "交通与旅行 Travel & Transport": (None, "对话·公告", "短对话高频场景"),
    "饮食 Food & Cooking": (None, "对话·公告", "短对话与公告高频场景"),
    "日常器物 Everyday Objects": (None, "对话·公告", "短对话高频场景"),
    "核心学术概念 Core Academic Concepts": (None, "全学科通用", "任何讲座都会用到的学术论述词，优先级等同高频学科"),
    "职业与人物 Professions & People": (None, "全学科通用", "讲座与对话都会出现"),
    "时间与变化 Time & Change": (None, "全学科通用", "讲座里描述过程与演变的高频词"),
    "欺诈与犯罪 Fraud & Crime": (None, "通用", "非独立讲座学科"),
    "品性（褒义）Positive Traits": (None, "通用", "非独立讲座学科"),
    "品性（贬义）Negative Traits": (None, "通用", "非独立讲座学科"),
    "品性与状态 Character & States": (None, "通用", "非独立讲座学科"),
    "身体动作 Body Movements": (None, "通用", "非独立讲座学科"),
    "名望与成就 Fame & Achievement": (None, "通用", "非独立讲座学科"),
    "通用词汇 General Vocabulary": (None, "通用", "未归入学科的词"),
}

# 徽章：emoji + 颜色。排序权重让「2026 优先级」视图能把高频学科顶到前面。
TIER_META = {
    "讲座高频": ("🔥", "#ff6b4a", 0),
    "全学科通用": ("🧩", "#b07cff", 1),
    "讲座中频": ("📈", "#4c8dff", 2),
    "对话·公告": ("🎓", "#2ecc71", 3),
    "讲座低频": ("💤", "#8b93a1", 4),
    "通用": ("", "#8b93a1", 5),
}

# ── 1. Topic ranges in 1675 list (line numbers, 1-based) ──
# The 1675 file is implicitly organized by topic.
TOPIC_RANGES_1675 = [
    (1,   69,  "地理与地质 Geography & Geology"),
    (70,  109, "动物与生态 Zoology & Ecology"),
    (110, 149, "动物与生态 Zoology & Ecology"),
    (150, 229, "法律与制度 Law & Governance"),
    (230, 279, "化学与材料 Chemistry & Materials"),
    (280, 289, "环境科学 Environmental Science"),
    (290, 299, "教育 Education"),
    (300, 339, "经济与商业 Economics & Business"),
    (340, 379, "军事 Military"),
    (380, 399, "考古与历史 Archaeology & History"),
    (400, 429, "农业 Agriculture"),
    (430, 461, "气象与气候 Weather & Climate"),
    (462, 469, "人类学与社会学 Anthropology & Sociology"),
    (470, 479, "人类学与社会学 Anthropology & Sociology"),
    (480, 509, "职业与人物 Professions & People"),
    (510, 569, "职业与人物 Professions & People"),
    (570, 589, "政治与社会制度 Politics & Social Systems"),
    (590, 609, "生物学 Biology"),
    (610, 629, "生物学 Biology"),
    (630, 669, "数学与几何 Mathematics & Geometry"),
    (670, 709, "天文学 Astronomy"),
    (710, 769, "物理学 Physics"),
    (770, 789, "物理学 Physics"),
    (790, 809, "医学与健康 Medicine & Health"),
    (810, 849, "艺术与文学 Art & Literature"),
    (850, 879, "语言与写作 Language & Writing"),
    (880, 919, "政治与社会制度 Politics & Social Systems"),
    (920, 959, "植物学 Botany"),
    (960, 979, "宗教与哲学 Religion & Philosophy"),
    (980, 999, "品性（贬义）Negative Traits"),
    (1000,1019,"品性（褒义）Positive Traits"),
    (1020,1039,"品性（褒义）Positive Traits"),
    (1040,1069,"品性（褒义）Positive Traits"),
    (1070,1099,"品性（贬义）Negative Traits"),
    (1100,1119,"品性（褒义）Positive Traits"),
    (1120,1139,"饮食 Food & Cooking"),
    (1140,1159,"核心学术概念 Core Academic Concepts"),
    (1160,1199,"核心学术概念 Core Academic Concepts"),
    (1200,1219,"核心学术概念 Core Academic Concepts"),
    (1220,1239,"核心学术概念 Core Academic Concepts"),
    (1240,1259,"时间与变化 Time & Change"),
    (1260,1279,"时间与变化 Time & Change"),
    (1280,1299,"运动与流体 Motion & Fluids"),
    (1300,1319,"日常器物 Everyday Objects"),
    (1320,1339,"欺诈与犯罪 Fraud & Crime"),
    (1340,1359,"欺诈与犯罪 Fraud & Crime"),
    (1360,1399,"工具与劳动 Tools & Labor"),
    (1400,1419,"社会关系 Social Relations"),
    (1420,1439,"建筑与住所 Architecture & Dwellings"),
    (1440,1469,"名望与成就 Fame & Achievement"),
    (1470,1499,"礼仪与情感 Etiquette & Emotions"),
    (1500,1529,"身体动作 Body Movements"),
    (1530,1559,"日常生活 Daily Life"),
    (1560,1599,"品性与状态 Character & States"),
    (1600,1629,"情绪与心理 Emotions & Psychology"),
    (1630,1669,"情绪与心理 Emotions & Psychology"),
    (1670,1675,"情绪与心理 Emotions & Psychology"),
]

# ── 2. Keyword-based classifier for words NOT in 1675 ──
# Each rule: (topic, keywords_in_word_or_definition)
CLASSIFY_RULES = [
    ("地理与地质 Geography & Geology", [
        "geograph", "geolog", "terrain", "topograph", "continent", "peninsula", "island",
        "mountain", "volcano", "earthquake", "glacier", "canyon", "cave", "cavern",
        "plateau", "valley", "cliff", "coast", "shore", "desert", "tundra", "prairie",
        "erosion", "sediment", "stratum", "strata", "crust", "magma", "fault",
        "latitude", "longitude", "equator", "hemisphere", "meridian", "elevation",
        "avalanche", "landslide", "arid", "barren", "terrain", "limestone", "granite",
        "mineral", "ore", "quarry", "quartz", "fossil", "iceberg", "glacial",
    ]),
    ("天文学 Astronomy", [
        "astrono", "stellar", "interstellar", "comet", "meteor", "asteroid",
        "constellation", "galaxy", "cosmos", "cosmic", "nebula", "orbit",
        "celestial", "solar", "lunar", "planet", "saturn", "venus", "jupiter",
        "neptune", "pluto", "uranus", "telescope", "spacecraft", "corona",
        "chromosphere", "photosphere", "magnetosphere", "ionosphere",
    ]),
    ("物理学 Physics", [
        "physic", "electron", "proton", "neutron", "atom", "nuclear", "fusion",
        "magnet", "electr", "conductor", "semiconductor", "insulator", "transistor",
        "voltage", "amplif", "oscillat", "gravit", "velocity", "accelerat",
        "thermometer", "thermodynamic", "optic", "spectrum", "lens",
        "transparent", "opaque", "translucent", "ultraviolet", "ultrasonic",
        "sonar", "acoustic", "microwave", "relativity", "vibrat",
        "equilibrium", "density", "elastic",
    ]),
    ("化学与材料 Chemistry & Materials", [
        "chemi", "molecule", "ion", "solvent", "dissolve", "compound", "element",
        "sulfur", "dioxide", "nitrogen", "oxygen", "hydrogen", "carbon",
        "sodium", "calcium", "helium", "silicon", "ammonia", "iodine",
        "zinc", "nickel", "platinum", "mercury", "copper", "tin", "alumin",
        "acid", "alkali", "bleach", "catalys", "polymer", "synthetic",
        "gasoline", "petroleum", "hydrocarbon", "methane", "silica", "silicate",
        "adhesive", "alchemy", "impurity",
    ]),
    ("生物学 Biology", [
        "biolog", "organism", "species", "evolv", "evolution", "cell",
        "gene", "dna", "photosynthes", "metabolism", "morpholog",
        "glucose", "protein", "symbi", "parasite", "parasit",
        "propagat", "ferment", "respirat", "secreti", "assimilat",
        "immune", "immunit", "reproduct", "regenerat", "microscope",
    ]),
    ("动物与生态 Zoology & Ecology", [
        "carnivo", "herbivo", "omnivo", "predator", "predatory", "prey",
        "vertebr", "invertebr", "reptil", "amphibi", "mammal", "primate",
        "insect", "mollusk", "plankton", "coral", "dolphin", "whale",
        "rodent", "flock", "herd", "swarm", "spawn", "dormant", "hibernate",
        "camouflage", "monogam", "niche", "rhinocer", "chimpanz", "gorilla",
        "lizard", "moth", "canary", "dinosaur", "larva", "aquatic", "fowl",
        "scavenger", "finch", "baboon", "chameleon",
        "ecosystem", "ecolog", "habitat", "fauna",
    ]),
    ("植物学 Botany", [
        "botan", "flora", "petal", "pollen", "starch", "foliage",
        "germinate", "sprout", "timber", "bark", "twig", "bough", "trunk",
        "stem", "stalk", "leaflet", "husk", "crossbreed", "necrosis",
        "pollinat", "luxuriant", "orchid", "fern", "sequoia", "rosette",
        "seedling", "shrub", "bud", "vine",
    ]),
    ("医学与健康 Medicine & Health", [
        "medic", "diagnos", "symptom", "fracture", "surgeon", "surgery",
        "contagious", "infectious", "feverish", "morbid", "malady",
        "remedy", "prescri", "hygiene", "sanitat", "anatomy", "dissect",
        "sterile", "acute", "chronic", "intoxicat", "relapse", "fester",
        "vaccine", "vaccinat",
    ]),
    ("气象与气候 Weather & Climate", [
        "meteorolog", "climate", "hurricane", "tornado", "cyclone", "blizzard",
        "drizzle", "downpour", "tempest", "barometer", "troposphere",
        "precipitat", "humid", "drought", "monsoon",
    ]),
    ("数学与几何 Mathematics & Geometry", [
        "mathemat", "geometr", "arithmet", "statistic", "calculus",
        "triangle", "rectangle", "polygon", "circle", "sphere", "cone",
        "cylinder", "cube", "cubic", "diameter", "radius", "circumferen",
        "decimal", "fraction", "ratio", "percent", "numeral", "digit",
        "equation", "function", "variable",
    ]),
    ("农业 Agriculture", [
        "agricultur", "husbandry", "cultivat", "irrigat", "manure",
        "horticultur", "hydropon", "insecticid", "livestock", "poultry",
        "ranch", "pasture", "orchard", "plantation", "fodder", "haystack",
        "sorghum", "buffalo", "cattle", "cowshed", "granary", "sheepfold",
        "tractor", "pigpen", "pigsty",
    ]),
    ("经济与商业 Economics & Business", [
        "econom", "commerce", "commerc", "enterprise", "currency", "inflation",
        "surplus", "deficit", "tariff", "quota", "bankruptcy", "audit",
        "invest", "stock", "bond", "commission", "revenue", "profit",
        "merchand", "barter", "deposit", "patronage", "collateral",
        "depreciat", "reimburse", "subsid", "retail",
    ]),
    ("法律与制度 Law & Governance", [
        "jurisdict", "arbitrat", "confiscat", "verdict", "indemnit",
        "imprison", "captiv", "detain", "extenu", "authorize",
        "empower", "oath", "pledge", "plaintiff", "proscribe",
        "abstinen", "veto", "stipulat", "testif", "substanti",
        "impeach", "indictment", "incriminat", "prosecut", "denounc",
        "lawsuit", "interrogat", "impunit", "exempt", "condone",
        "liberat", "remit", "absolve", "acquit", "abolish",
        "legislat", "enact", "decree", "constitution", "clause",
    ]),
    ("军事 Military", [
        "militar", "naval", "armament", "armor", "fortress", "siege",
        "expedition", "recruit", "enlist", "squad", "raid", "encroach",
        "repulse", "morale", "mandate", "tactics", "corps",
    ]),
    ("考古与历史 Archaeology & History", [
        "archeolog", "archaeolog", "excavat", "paleolith", "neolith",
        "mesolith", "chronolog", "archaic", "primitive", "antiquit",
        "artifact", "porcelain", "remnant",
    ]),
    ("政治与社会制度 Politics & Social Systems", [
        "democra", "republic", "monarch", "autocrat", "anarchi",
        "congress", "senate", "parliament", "ballot", "election",
        "diplomat", "sovereign", "autonomy", "municipal",
        "govern", "administr", "institut",
    ]),
    ("人类学与社会学 Anthropology & Sociology", [
        "anthropolog", "ethnolog", "ethnic", "tribe", "tribal",
        "aboriginal", "indigenous", "clan", "patriarch", "matriarch",
    ]),
    ("艺术与文学 Art & Literature", [
        "painting", "sculpt", "portrait", "impressioni", "fresco",
        "embroider", "tragedy", "rehearse", "prelude", "renaissanc",
        "aesthetic", "euphoni", "orchestra", "chorus", "percussion",
        "mural", "opera", "theater", "drama", "ballet",
    ]),
    ("语言与写作 Language & Writing", [
        "linguist", "glossar", "slogan", "verse", "fable",
        "maxim", "satire", "farce", "adage", "synopsis",
        "compile", "emend", "paraphrase", "excerpt", "abridge",
        "rhetoric", "metaphor",
    ]),
    ("宗教与哲学 Religion & Philosophy", [
        "religion", "deity", "oracle", "atheism", "heresy",
        "creed", "dogma", "pious", "devout", "consecrat",
        "invoke", "enchant", "preach", "rite", "ritual",
    ]),
    ("饮食 Food & Cooking", [
        "cabbage", "celery", "cereal", "cucumber", "lettuce",
        "spinach", "wheat", "barley", "broccoli", "millet",
        "mustard", "oats", "rye", "sesame", "soybean",
        "edible", "condiment", "cuisine", "dessert", "beverage",
        "nutriment", "nibble",
    ]),
    ("教育 Education", [
        "curriculum", "tuition", "semester", "scholarship",
        "pedagog", "didactic", "edify", "instill",
    ]),
    ("环境科学 Environmental Science", [
        "pollut", "contamin", "sewage", "noxious", "ozone",
        "decibel", "smog", "emission", "sustainab", "biodegradab",
        "deforest", "reforest", "greenhouse", "compost", "landfill",
        "fossil fuel", "biodiversity", "endangered", "desertif",
        "ecological footprint", "carbon neutral", "zero waste",
        "coral bleach",
    ]),
    ("科技与计算 Technology & Computing", [
        "algorithm", "software", "digital", "virtual reality",
        "augmented reality", "simulat", "interface", "automat",
        "neural network", "machine learning", "artificial intellig",
        "computing", "coding", "programm", "cloud comput",
        "bandwidth", "server", "database", "cybersecur", "encrypt",
        "browser", "download", "upload", "backup", "debug",
        "blockchain", "big data", "robotics", "3d print",
        "sensor", "processor", "fiber optic", "wireless",
        "bluetooth", "drone", "autonomous", "self-driving",
        "startup", "silicon valley",
    ]),
    ("心理健康 Mental Health", [
        "therapy", "counseling", "mindful", "burnout",
        "self-care", "mental health", "resilien", "coping",
        "well-being", "meditat", "psycholog", "psychiatr",
        "cognitive behav", "disorder", "adhd", "insomnia",
        "phobia", "panic attack", "self-esteem", "procrastinat",
        "work-life balance", "support group", "wellness",
    ]),
    ("校园生活 Campus Life", [
        "librarian", "checkout", "overdue", "interlibrary",
        "periodical", "bibliograph", "citation", "thesis defense",
        "enrollment", "elective", "syllabus", "advisor",
        "orientation", "registrar", "commencement",
        "freshman", "sophomore", "junior", "senior",
        "undergraduate", "graduate school", "provost",
        "roommate", "cafeteria", "meal plan", "move-in",
        "residence hall", "off-campus", "on-campus",
        "extracurricular", "student union", "bulletin board",
        "study abroad", "exchange program", "career fair",
    ]),
]

# Emoji per discipline
EMOJI = {
    "地理与地质 Geography & Geology": "🌍",
    "天文学 Astronomy": "🔭",
    "物理学 Physics": "⚡",
    "化学与材料 Chemistry & Materials": "🧪",
    "生物学 Biology": "🧬",
    "动物与生态 Zoology & Ecology": "🐾",
    "植物学 Botany": "🌿",
    "医学与健康 Medicine & Health": "🏥",
    "气象与气候 Weather & Climate": "🌦️",
    "数学与几何 Mathematics & Geometry": "📐",
    "农业 Agriculture": "🌾",
    "经济与商业 Economics & Business": "💰",
    "法律与制度 Law & Governance": "⚖️",
    "军事 Military": "🛡️",
    "考古与历史 Archaeology & History": "🏺",
    "政治与社会制度 Politics & Social Systems": "🏛️",
    "人类学与社会学 Anthropology & Sociology": "👥",
    "艺术与文学 Art & Literature": "🎨",
    "语言与写作 Language & Writing": "✍️",
    "宗教与哲学 Religion & Philosophy": "🕊️",
    "饮食 Food & Cooking": "🍽️",
    "教育 Education": "📚",
    "环境科学 Environmental Science": "♻️",
    "职业与人物 Professions & People": "👤",
    "品性（褒义）Positive Traits": "✨",
    "品性（贬义）Negative Traits": "⚠️",
    "核心学术概念 Core Academic Concepts": "🔬",
    "时间与变化 Time & Change": "⏳",
    "运动与流体 Motion & Fluids": "💧",
    "日常器物 Everyday Objects": "🔧",
    "欺诈与犯罪 Fraud & Crime": "🚨",
    "工具与劳动 Tools & Labor": "🔨",
    "社会关系 Social Relations": "🤝",
    "建筑与住所 Architecture & Dwellings": "🏠",
    "名望与成就 Fame & Achievement": "🏆",
    "礼仪与情感 Etiquette & Emotions": "🎭",
    "身体动作 Body Movements": "🏃",
    "日常生活 Daily Life": "🏡",
    "品性与状态 Character & States": "🧘",
    "情绪与心理 Emotions & Psychology": "🧠",
    "交通与旅行 Travel & Transport": "🚀",
    "科技与计算 Technology & Computing": "💻",
    "心理健康 Mental Health": "🧘‍♀️",
    "校园生活 Campus Life": "🎓",
    "通用词汇 General Vocabulary": "📝",
}

# ── Direct word→topic mappings for words without definitions ──
# Built with first-assignment-wins to avoid later groups overwriting earlier ones
def _build_word_topic_map():
    m = {}
    groups = [
    ("情绪与心理 Emotions & Psychology", [
        'abashed','agonize','aghast','amazed','anguish','anxious','apathetic',
        'astonish','astonished','astound','awe','awkward','bashful','bewilder',
        'bliss','boredom','boring','chill','chilly','cheerless','cower','crazy',
        'dauntless','daze','dazzle','dazzling','dejected','despair','disdain',
        'dismay','doleful','downcast','dread','drowsy','dubious','eager',
        'ecstasy','elation','embarrass','enchant','enrage','enrapture',
        'enthral','enthusiasm','exasperate','excitement','exultant','faint',
        'famish','fanatic','fanaticism','fantasy','fatigue','fester','feverish',
        'fickle','flustered','forlorn','formidable','frenzy','fret','fright',
        'frustrated','fury','giddy','gloom','gloomy','gratify','grief','grin',
        'groan','grudge','guilty','happiness','heartache','horror','hostile',
        'humiliate','hysterical','impatient','indifferent','indignant',
        'infuriate','insecure','irritable','irritate','jealous','jeer',
        'joyful','keen','lament','languor','listless','livid','loneliness',
        'lonely','lonesome','lull','mad','malaise','manic','melancholy',
        'mellow','miserable','moody','mope','morose','mortify','mournful',
        'nervous','nostalgia','nostalgic','numb','obsess','offend','outrage',
        'overwhelm','panic','passionate','pathetic','peevish','perplexed',
        'pessimistic','petulant','pity','placid','pleased','poignant',
        'provoke','rage','rapture','regret','relish','reluctant','remorse',
        'resentful','restless','revere','revel','revulsion','rue','rueful',
        'sarcasm','satisfaction','scared','scorn','sentimental','serene',
        'shame','shiver','shock','shudder','sigh','smirk','sneer','sober',
        'solemn','somber','sorrow','spellbound','startled','stress','stricken',
        'stupefy','suffer','sulk','sullen','surprise','tense','terrify',
        'thrill','timid','torment','tranquil','trauma','tremor','triumph',
        'uneasy','unhappy','upset','vex','weary','wistful','woe','wonder',
        'worried','worship','wrath','yearn','zest',
    ]),
    ("品性（褒义）Positive Traits", [
        'able','accomplish','accomplished','acumen','adaptable','adept','adequate','admirable',
        'adroit','affable','agile','agility','agreeable','alert','amiable','amicable','apt',
        'ardent','articulate','astute','attentive','authentic','available','becoming',
        'beneficial','benevolent','benign','bold','brave','brilliant','brisk','calm','candid',
        'capable','careful','charitable','charming','chaste','clean','clever','cogent',
        'coherent','competent','composed','composure','confident','conscientious',
        'considerate','constant','cooperative','cordial','correct','courteous','credible',
        'cunning','curious','daring','decent','dedicated','deft','delicate','delicious',
        'diligent','diplomatic','discreet','distinguished','earnest','effective','efficient',
        'elegant','eloquent','eminent','energetic','ethical','excellent','exemplary',
        'experienced','expert','exquisite','faithful','feasible','firm','fit','fitting',
        'flexible','fluent','forthright','frank','gallant','generous','generously','genial',
        'gentle','genuine','gifted','glorious','good','gracious','grand','hardy','harmless',
        'helpful','heroic','honest','honorable','hospitable','humane','humble','illustrious',
        'imaginative','impeccable','impressive','industrious','ingenious','innocent',
        'innovative','insightful','inspiring','integrity','intelligent','intrepid','inventive',
        'judicious','just','keen','kind','knowledgeable','laudable','leading','liberal',
        'logical','loyal','lusty','magnificent','matchless','meek','merciful','meritorious',
        'meticulous','moderate','modest','moral','neat','nice','nimble','noble','noteworthy',
        'objective','observant','optimistic','organized','original','outstanding','patient',
        'peaceful','perceptive','persistent','persuasive','philanthropic','pleasant','polite',
        'positive','powerful','practical','precise','principled','productive','professional',
        'proficient','profound','progressive','promising','proper','prudent','punctual','pure',
        'qualified','rational','reasonable','refined','reliable','remarkable','renowned',
        'resilient','resolute','resourceful','respectful','responsible','robust','sagacious',
        'sane','scrupulous','selfless','sensible','sharp','shrewd','sincere','skillful',
        'smart','sociable','sophisticated','spirited','spontaneous','stable','steadfast',
        'steady','stout','sturdy','subtle','superb','supreme','swift','tactful','talented',
        'tender','thorough','thoughtful','thrifty','tolerant','tough','trustworthy','truthful',
        'unflinching','unique','universal','upright','urbane','valiant','versatile','viable',
        'vigorous','virtuous','vivid','warm','wholesome','wise','witty','worthy','zealous',
    ]),
    ("品性（贬义）Negative Traits", [
        'abhorrent','abortive','absurd','aggressive','arrogant','avarice','avaricious',
        'belligerent','bigoted','blunt','boastful','bombastic','brutal','callous','careless',
        'caustic','clumsy','coarse','conceited','contemptible','contemptuous','covetous',
        'crafty','crooked','crude','cruel','cynical','deceitful','deceptive','defiant',
        'designing','despicable','devious','dictatorial','difficult','dingy','dogmatic',
        'domineering','envious','extravagant','fatuous','fickle','filthy','flighty','foolish',
        'fraudulent','frivolous','fussy','gauche','greedy','grouchy','hackneyed','haughty',
        'hostile','hypocritical','idiotic','ignorant','illegitimate','illicit','immoral',
        'impertinent','imprudent','impudent','inconsiderate','indecent','indifferent','inept',
        'inferior','inflexible','inhumane','insolent','insular','intolerant','irrational',
        'irresponsible','lazy','malevolent','malicious','mean','mediocre','monotonous',
        'morbid','naive','narrow','negligent','notorious','noxious','obstinate','offensive',
        'overbearing','paranoid','partisan','passive','pedantic','presumptuous','pretentious',
        'prodigal','profane','reckless','rigid','rude','ruthless','selfish','shameless',
        'sinister','sly','snobbish','spineless','stingy','stubborn','superficial','suspicious',
        'tedious','treacherous','trivial','tyrannical','unjust','unruly','unscrupulous','vain',
        'vicious','violent','vulgar','wasteful','wicked',
    ]),
    ("身体动作 Body Movements", [
        'amble','ascend','ascent','batter','beat','bend','bite','blink','bow','brace','brag',
        'brawl','breeze','bruise','budge','butt','chafe','choke','chop','clap','clasp',
        'cleanse','clinch','cling','clip','clutch','collide','crash','crawl','creep','crouch',
        'crush','dab','dance','dart','dash','dodge','drag','drip','duck','dump','embrace',
        'erect','escape','explode','flay','flee','fling','flip','float','frown','gasp','gaze',
        'gesture','glare','glide','gnaw','grab','grasp','grind','grip','grope','halt','handle',
        'harness','hasten','haul','heave','hew','hike','hoist','hurl','jerk','jolt','jump',
        'kick','kneel','lash','launch','lean','leap','limp','march','nod','nudge','peck',
        'plunge','press','propel','pull','punch','push','rattle','recoil','rip','roam','roll',
        'rotate','run','rush','scratch','seize','shake','shatter','shear','shift','shove',
        'shuffle','skip','slam','slap','slide','sling','slip','slouch','smash','snap','snatch',
        'sneak','soar','spin','splash','sprint','squeeze','stagger','stalk','stamp','stand',
        'stare','step','stick','sting','stomp','stoop','stride','strike','strip','stroll',
        'stumble','sway','sweep','swim','swing','tap','tear','throw','thrust','tilt','toss',
        'tow','trample','tread','trudge','tug','tumble','turn','twist','wade','walk','wander',
        'wave','whisk','wring','yawn',
    ]),
    ("社会关系 Social Relations", [
        'accomplice','acquaintance','affiliate','alliance','ally','amend','antagonism',
        'antagonist','appeal','appoint','associate','association','banish','befriend','belie',
        'belittle','benefactor','beneficiary','betray','blame','bond','boon','bribe',
        'celebrate','celebrity','champion','chide','collaborate','colleague','community',
        'companion','compassion','compatible','compliment','compromise','concede','confer',
        'confide','confine','confront','congregate','connect','consent','consort','conspire',
        'consultation','contend','cooperate','correspond','counsel','courtship','delegate',
        'devote','devotion','disciple','discord','dispute','divorce','dominate','embrace',
        'empathy','endorse','enemy','entertain','escort','esteem','exclude','exploit','expel',
        'faithful','farewell','fellowship','flattery','foe','forgive','fraternal','friend',
        'gossip','gratify','greet','grudge','harass','harmony','intimate','intimidate',
        'invite','kinship','loyal','marriage','mediate','mentor','mutual','neighbor','nurture',
        'obey','oppose','partner','patron','peer','persuade','pledge','praise','quarrel',
        'rapport','reconcile','relation','rely','repel','respect','reunion','rival','rivalry',
        'scorn','seduce','separate','serve','shame','snub','solidarity','spouse','subordinate',
        'submit','support','surrender','sympathy','sympathize','sympathetic','tension',
        'tolerate','treason','trust','unite','unity','volunteer','wed','welcome','worship',
    ]),
    ("语言与写作 Language & Writing", [
        'abridge','abstain','accentuate','acclaim','accost','acknowledge','address','admonish',
        'adore','affirm','allege','allude','allusion','announce','annotate','anonymous',
        'answer','apologize','appeal','applaud','argue','articulate','assert','assure','avow',
        'babble','beg','beseech','boast','broadcast','call','censure','chat','chatter','chide',
        'chuckle','circulate','cite','claim','clamour','clarify','coax','comment',
        'communicate','commend','complain','complaint','concede','confess','congratulate',
        'converse','convince','correspond','curse','debate','declaim','declare','defame',
        'defend','define','demand','deny','describe','designate','dictate','disclose',
        'discourse','discuss','dismiss','divulge','elaborate','eloquence','emphasize',
        'endorse','enunciate','exaggerate','exclaim','exhort','explain','express','flatter',
        'gabble','gossip','greet','grumble','hint','holler','implore','imply','inform',
        'inquire','insist','instruct','interpret','interrupt','interview','jeer','jest','joke',
        'justify','lecture','laud','mention','mimic','mock','mumble','murmur','narrate','nag',
        'negotiate','notify','object','observe','orate','order','outcry','persuade','plead',
        'preach','proclaim','profess','promise','prompt','pronounce','propose','protest',
        'provoke','query','question','quote','rant','rebuke','recite','recommend','recount',
        'refute','reiterate','remark','remind','reply','report','reprimand','reproach',
        'request','respond','retort','reveal','rumor','say','scold','shout','silence','speak',
        'specify','stammer','state','stutter','suggest','summarize','summon','swear','talk',
        'taunt','tell','testify','threaten','translate','utter','voice','warn','whisper',
        'yell',
    ]),
    ("核心学术概念 Core Academic Concepts", [
        'abate','abolish','abound','absorb','abstract','abundant','accelerate','accommodate',
        'accumulate','achieve','acquire','adapt','adaptation','adequate','adhere','adherence',
        'adjacent','adjoin','adjoining','adjust','advance','affirm','aggregate','allocate',
        'allot','alter','alternate','alternative','altruism','amalgamate','amass','ample',
        'amplify','analogous','analogy','analysis','annex','annihilate','annual','annually',
        'anomalous','anomaly','anticipate','apparent','application','appreciate','apprehend',
        'apprehension','appropriate','approximate','arbitrary','arrange','array','ascertain',
        'aspect','aspire','aspiration','assemble','assembly','assess','assessment','asset',
        'assign','assimilate','assist','assume','assumption','attain','attainment','attribute',
        'augment','authority','balance','basis','bear','calculate','capacity','categorical',
        'categorize','category','cause','cease','ceaseless','circulate','circulation',
        'circumscribe','circumvent','classify','coexist','coincide','combination','combine',
        'commence','commission','commodity','compact','comparable','comparative','compare',
        'compel','compensate','compensation','compile','complement','complementary','complete',
        'complex','complicate','component','compose','comprehensive','comprise','compute',
        'conceive','concentrate','concept','concern','conclude','conclusive','concrete',
        'concurrent','condition','conduct','confine','confirm','confound','consequence',
        'consequent','conserve','consider','considerable','consist','consistent','consolidate',
        'constant','constitute','constrain','construct','consult','consume','consumer',
        'contain','container','contemplate','context','continual','continually','contract',
        'contradict','contrary','contrast','contribute','controversial','controversy',
        'convenient','convention','conventional','convert','convey','convince','coordinate',
        'correlate','correspond','criterion','crucial','cumulative','curious','curiosity',
        'current','decline','dedicate','deduce','deduction','deem','define','definite',
        'deliberate','demonstrate','denote','depend','dependent','derive','designate','detect',
        'determination','determine','develop','deviate','devise','differentiate','diminish',
        'direct','discard','discover','discriminate','disposition','dispute','distinct',
        'distinction','distinguish','distribute','diverge','divergent','diverse','diversify',
        'divide','division','document','domain','dominant','dominate','dual','durable',
        'duration','dynamic','effect','effective','elaborate','element','elementary','elevate',
        'eliminate','emerge','emergence','emphasis','empirical','enable','encounter',
        'endeavour','endorse','enforce','engage','enhance','enormous','ensure','entity',
        'entry','equal','equate','equation','equip','equipment','equivalent','erect','err',
        'erratic','erroneous','essential','establish','estimate','evaluate','eventual',
        'evidence','evident','evolve','exact','examine','exceed','excess','excessive',
        'exchange','exclude','exclusive','execute','exemplify','exempt','exert','exhibit',
        'exist','exit','expand','expansion','expedient','expertise','explicit','exploit',
        'explore','expose','exposure','extend','extension','extensive','external','extract',
        'extreme','facilitate','factor','feature','final','focus','formal','formula',
        'formulate','foundation','framework','function','fundamental','furthermore','generate',
        'grant','guarantee','hypothesis','identical','identify','ideology','ignore',
        'illustrate','impact','implement','implication','implicit','imply','impose','incline',
        'inclined','incorporate','indicate','individual','induce','inevitable','infer',
        'influence','influential','inform','inherent','initial','initiate','innovate',
        'innovation','input','insert','inspect','instance','institute','integral','integrate',
        'integrity','intellect','intellectual','intelligence','intelligent','intend','intense',
        'interact','interior','intermediate','internal','interpret','interval','intervene',
        'intricate','intrinsic','invest','investigate','involve','isolate','issue','item',
        'label','layer','link','locate','logic','logical','maintain','major','manifest',
        'margin','material','mature','maximize','mechanism','mediate','medium','method',
        'migrate','minimize','minor','modify','monitor','motive','mutual','negative','neutral',
        'norm','normal','notion','objective','obtain','obvious','occupy','occur','offset',
        'orient','origin','outcome','output','overall','overlap','parallel','parameter',
        'participate','perceive','period','perpetual','persist','perspective','phase',
        'phenomenon','philosophy','physical','pose','positive','potential','precede','precise',
        'precision','predict','predominant','preliminary','presume','prevalent','previous',
        'primary','prime','principal','principle','prior','priority','proceed','process',
        'project','promote','proportion','prospect','provide','publish','pursue','qualify',
        'range','react','recover','reduce','refer','reflect','reform','region','register',
        'regulate','reinforce','reject','relate','relative','release','relevant','rely',
        'remove','require','research','resolve','resource','respond','restore','restrain',
        'restrict','retain','reveal','reverse','revise','revolution','role','route','scheme',
        'section','sector','secure','seek','select','series','significant','similar',
        'simulate','site','sole','solely','somewhat','source','specific','sphere','stabilize',
        'standard','structure','style','submit','substitute','sufficient','summarize',
        'supplement','survey','survive','sustain','symbol','target','task','technique',
        'technology','temporary','terminate','theme','theory','thereby','thesis','topic',
        'trace','tradition','transfer','transform','transition','transmit','transport','trend',
        'trigger','ultimate','undergo','underlie','undertake','uniform','utility','utilize',
        'valid','validity','variable','variation','vary','version','volume','widespread',
    ]),
    ("建筑与住所 Architecture & Dwellings", [
        'architecture','auditorium','balcony','barn','barracks','basement','bedroom',
        'building','bungalow','cabin','canopy','castle','cathedral','ceiling','cellar',
        'cement','chimney','church','closet','column','corridor','cottage','courtyard','depot',
        'dome','door','dormitory','dwelling','entrance','facade','fixture','floor','fort',
        'fortress','foundation','garage','gate','greenhouse','hall','hallway','harbor','hut',
        'inn','interior','kitchen','labyrinth','landmark','lodge','mansion','monument',
        'mosque','palace','parlor','pavilion','pier','pillar','porch','prison','pyramid',
        'residence','residential','roof','ruin','ruins','shack','shanty','shed','shelter',
        'shrine','skyscraper','staircase','stable','stall','structure','suburb','suburban',
        'tavern','temple','terrace','threshold','tower','tunnel','vault','warehouse','wing',
    ]),
    ("交通与旅行 Travel & Transport", [
        'abroad','aircraft','airplane','arrival','automobile','aviation','aviator','baggage',
        'boat','bridge','bus','cab','canal','cargo','carriage','carrier','chariot','commute',
        'convoy','cruise','destination','detour','dock','embark','emigrate','ferry','flight',
        'freeway','freight','fuel','gasoline','harbor','highway','immigrate','itinerant',
        'journey','lane','locomotive','luggage','mast','migrate','navigation','navigate','oar',
        'passport','pedestrian','pier','pilot','port','railroad','railway','route','sail',
        'sailor','seaport','ship','shipment','shuttle','stagecoach','steer','subway','taxi',
        'terminal','terminus','ticket','tour','tourism','tourist','traffic','trail','train',
        'transit','transport','travel','trek','truck','turnpike','van','vehicle','vessel',
        'voyage','wagon',
    ]),
    ("日常生活 Daily Life", [
        'baby-sit','baggage','bait','bald','ban','banquet','bar','bare','barely','basin',
        'bask','bath','battery','bedroom','bench','blanket','board','bottle','box','breakfast',
        'bridge','bucket','building','bulky','burn','bus','butter','butterfly','cabinet',
        'cage','camp','candle','cap','carpet','carriage','cart','cash','chair','chamber',
        'chimney','church','city','clock','closet','cloth','clothing','coach','coal','coat',
        'coffee','coin','collar','column','comfort','cook','cooking','cozy','cup','curtain',
        'cushion','dairy','deed','desk','dinner','dish','door','dormitory','dress','drink',
        'drive','dwelling','envelope','fabric','fan','farm','fence','fire','floor','food',
        'fork','frame','fuel','furniture','garden','garment','gate','gift','glass','glove',
        'goods','grocery','guest','gutter','habit','hall','hammer','hat','home','hotel',
        'house','housing','inn','key','kitchen','knife','lamp','laundry','lawn','lease',
        'leather','letter','library','lid','light','linen','lock','lodge','luggage','lunch',
        'mail','map','market','mat','match','meal','mirror','money','mug','nail','needle',
        'net','newspaper','oven','package','pad','pan','paper','parcel','park','parlor','path',
        'payment','pen','pencil','phone','pillow','pipe','plate','pocket','pot','prize',
        'purse','quilt','radio','railroad','rain','receipt','rent','repair','restaurant',
        'ring','road','roof','room','rope','rug','salt','sand','sauce','seat','sheet','shelf',
        'shirt','shoe','shop','silk','soap','socket','sofa','soup','spoon','stamp','stair',
        'staircase','stove','street','sugar','suit','suitcase','supper','table','tape','taxi',
        'tent','ticket','tire','tool','towel','tower','town','train','travel','truck',
        'umbrella','vacation','van','village','wagon','wall','wardrobe','wash','waste','watch',
        'water','wheel','window','wine','wood','yard','chore','errand','household','leisure',
        'pastime','recreation','recreational','relaxation','routine','apparel','costume',
        'attire','garb','outfit','scissors','saucer','utensil','steak','rinse','chalk',
        'screen','screw','screwdriver','sack','rod','tube','tub','stitch','strap','thread',
        'threadlike','yarn','wool','woolen','woolly','waist','wrist','wristwatch','wrinkle',
        'slipper','sunglasses','fingertip','thigh','toe','toed','dye','wax','waxy','wavy',
        'knapsack','purse','wallet','sponge','canopy','glassware','hardware','tableware',
        'earthenware','ware','wedding','dagger','hatchet','shovel','spade','sickle','razor',
        'needle','tray','fixture','gear','loot','trash','wreck','shipwreck','ruins','rubble',
        'pebble','flake','foam','snippet','skull','skeleton','shell','eggshell',
    ]),
    ("地理与地质 Geography & Geology", [
        'bay','beach','bleak','bog','bush','cascade','coast','coastline','countryside','cove',
        'creek','dale','delta','dune','field','fjord','forest','glen','gorge','grove','gulf',
        'heath','highland','hill','isle','islet','jungle','lagoon','lake','landscape',
        'lowland','marsh','marshy','meadow','moor','mound','oasis','ocean','peak','peninsula',
        'picturesque','plain','pond','prairie','puddle','range','ravine','reef','ridge',
        'riverbank','rural','rustic','scenery','scenic','seashore','seaside','slope','steep',
        'stream','summit','swamp','swampy','terrain','topsoil','tropical','undergrowth',
        'upland','valley','volcano','waterfall','watercourse','waterproof','wilderness',
        'wildlife','woodland','woods','vista','stark','barren',
    ]),
    ("医学与健康 Medicine & Health", [
        'acupuncture','airsickness','antiseptic','bleed','bruise','clinic','cure','diet',
        'disease','disorder','dose','drug','epidemic','fever','flu','fracture','gash',
        'headache','heal','healthful','hospital','illness','immune','infection','infirmary',
        'injury','medicine','nurse','operate','operation','pain','patient','pharmacy',
        'physician','pill','plague','poison','pulse','remedy','scar','sick','sickness','sore',
        'spinal','spinal cord','spine','surgery','surgeon','swelling','therapy','treatment',
        'wound','homesick','tissue','malnourished','sterile','unconscious','invalid',
    ]),
    ("动物与生态 Zoology & Ecology", [
        'beaver','butterfly','caterpillar','clam','crab','eagle','elephant','falcon','fox',
        'frog','giraffe','goat','hawk','hen','horse','jellyfish','kitten','lamb','lion',
        'lobster','monkey','mosquito','mouse','octopus','osprey','owl','ox','oyster','parrot',
        'penguin','pigeon','pig','puppy','quail','rabbit','rat','raven','rooster','salmon',
        'scorpion','shark','sheep','shrimp','snake','sparrow','spider','squirrel','starfish',
        'swan','termite','tiger','toad','turkey','turtle','whale','wolf','worm','zebra',
        'shellfish','rattlesnake','tapeworm','locoweed',
    ]),
    ("气象与气候 Weather & Climate", [
        'sunrise','sunset','sunshine','sunlight','sunlit','sunburn','sundial','sunflower',
        'solar cell','space shuttle','spaceship','thunderstorm','tide','torrential',
        'torrential rain','tornado','cyclone','rainfall','snowflake','snowdrift','fog','hail',
        'lightning','rainbow','temperature','thermal','weather','weathering',
    ]),
    ("经济与商业 Economics & Business", [
        'accountant','administrator','agenda','apprentice','assignment','boss','brand',
        'budget','bureau','bureaucracy','career','clerk','client','colleague','company',
        'competition','competitor','corporate','corporation','customer','deadline','deal',
        'department','director','dismiss','employ','employee','employer','employment',
        'executive','expert','factory','firm','hire','industry','interview','job','labor',
        'laborious','manager','manufacture','marketing','meeting','merchant','negotiate',
        'occupation','office','official','operate','personnel','position','practice',
        'practitioner','profession','professional','professionalism','profit','profitable',
        'promotion','proprietor','proprietorship','resign','resignation','retirement','salary',
        'secretary','staff','supervisor','trade','trading','unemployed','vacancy','wage',
        'workforce','workshop',
    ]),
    ("物理学 Physics", [
        'axis','asymmetrical','calibre','dimension','friction','spiral','three-dimensional',
        'torque','vacuum','traction','wavelength','thermal','telescope','radar','semimolten',
        'viscosity','viscous',
    ]),
    ("艺术与文学 Art & Literature", [
        'symphony','studio','stanza','trilogy','troupe','trumpet','trumpeter','lyric','prose',
        'fiction','dialogue','anecdote','allegory','riddle','epic','novel','anthology',
        'biography','comedy','farce','genre','legend','manuscript','memoir','myth','narrative',
        'parody','plot','rhyme','rhythm','saga','screenplay','sonnet','stylized','tapestry',
        'artistic',
    ]),
    ("政治与社会制度 Politics & Social Systems", [
        'ambassador','authority','campaign','census','citizen','civil','civilian','colonial',
        'colony','congress','conquest','constitution','coup','crown','democracy','dictator',
        'diplomat','dominion','dynasty','emperor','empire','exile','federation','flag',
        'government','governor','independence','kingdom','king','law','leader','liberty',
        'mayor','minister','nation','national','nationality','parliament','patriot','policy',
        'political','politics','president','prince','princess','province','queen','rebel',
        'rebellion','reform','regime','republic','revolution','senator','slavery','state',
        'throne','treaty','union','vote','voter','warrior','welfare','walkout','upheaval',
    ]),
    ("时间与变化 Time & Change", [
        'abiding','age','ancient','annual','antique','antiquity','beforehand','belated',
        'brief','ceaseless','change','chronic','constant','contemporary','continual','dated',
        'dawn','delay','duration','dynasty','early','elapse','endure','endless','epoch','era',
        'eternal','everlasting','expire','extinct','extinction','final','former','forthcoming',
        'frequent','hasty','immediate','immortal','imminent','impromptu','inaugural','instant',
        'instantaneous','interim','intermittent','last','lasting','lately','late','linger',
        'long','medieval','modern','momentary','obsolete','occasional','ongoing','onset',
        'overdue','passing','past','patience','pending','perennial','permanent','perpetual',
        'persist','postpone','prehistoric','premature','present','pressing','previous',
        'primitive','primordial','prior','pristine','prolong','prompt','punctual','recent',
        'recurring','remote','renew','renewal','routine','schedule','seasonal','senior',
        'sequence','session','short','simultaneous','sojourn','sporadic','subsequent',
        'succession','successive','sudden','swift','tardy','temporary','transient',
        'transitory','urgent','vintage','wane',
    ]),
    ("物理学 Physics", [
        'axis','asymmetrical','calibre','dimension','friction','spiral','three-dimensional',
        'torque','vacuum','traction','wavelength','radar','semimolten','viscosity','viscous',
    ]),
    ("艺术与文学 Art & Literature", [
        'symphony','studio','stanza','trilogy','troupe','trumpet','trumpeter','lyric','prose',
        'fiction','dialogue','anecdote','allegory','riddle','epic','novel','anthology',
        'biography','comedy','genre','legend','manuscript','memoir','myth','narrative',
        'parody','plot','rhyme','rhythm','saga','screenplay','sonnet','stylized','tapestry',
        'artistic','ragtime',
    ]),
    ("政治与社会制度 Politics & Social Systems", [
        'ambassador','campaign','census','citizen','civil','colonial','colony','conquest',
        'coup','crown','dictator','dominion','dynasty','emperor','empire','exile','federation',
        'flag','governor','independence','kingdom','king','liberty','mayor','minister',
        'nation','patriot','policy','political','politics','president','prince','princess',
        'province','queen','rebellion','reform','republic','slavery','state','throne','treaty',
        'union','vote','voter','warrior','welfare','walkout','upheaval','chivalry','soldier',
    ]),
    ("医学与健康 Medicine & Health", [
        'acupuncture','airsickness','antiseptic','bleed','clinic','cure','diet','disease',
        'disorder','dose','drug','epidemic','fever','flu','headache','heal','healthful',
        'hospital','illness','medicine','nurse','pain','patient','pharmacy','physician','pill',
        'plague','poison','pulse','scar','sick','sickness','sore','therapy','wound','homesick',
        'tissue','unconscious','invalid',
    ]),
    ("动物与生态 Zoology & Ecology", [
        'beaver','caterpillar','crab','eagle','elephant','falcon','fox','frog','giraffe',
        'goat','hawk','hen','horse','jellyfish','kitten','lamb','lion','lobster','monkey',
        'mosquito','mouse','octopus','osprey','owl','ox','oyster','parrot','penguin','pigeon',
        'pig','puppy','quail','rabbit','rat','raven','rooster','salmon','scorpion','shark',
        'sheep','shrimp','snake','sparrow','spider','squirrel','starfish','swan','termite',
        'tiger','toad','turkey','turtle','whale','wolf','worm','zebra','shellfish',
        'rattlesnake','tapeworm','locoweed','butterfly','wildlife',
    ]),
    ("地理与地质 Geography & Geology", [
        'bay','beach','bog','bush','cascade','coast','coastline','countryside','cove','creek',
        'dale','delta','dune','fjord','forest','glen','gulf','heath','highland','hill','isle',
        'islet','jungle','lagoon','lake','landscape','lowland','marsh','marshy','meadow',
        'moor','mound','oasis','ocean','peak','plain','pond','prairie','puddle','ravine',
        'reef','riverbank','rural','rustic','scenery','scenic','seashore','seaside','slope',
        'stream','summit','swamp','swampy','waterfall','watercourse','wilderness','woodland',
        'woods','vista','stark','barren','steep','upland','tableland',
    ]),
    ("气象与气候 Weather & Climate", [
        'sunrise','sunset','sunshine','sunlight','sunlit','sunburn','sundial','sunflower',
        'solar cell','space shuttle','spaceship','thunderstorm','tide','torrential',
        'torrential rain','rainfall','snowflake','snowdrift','fog','lightning','rainbow',
        'temperature','weather','weathering',
    ]),
    ("核心学术概念 Core Academic Concepts", [
        'absorbing','accredit','accustom','aggravate','aim','alleviate','allure','amateur',
        'ambiguous','ambitious','amenable','annul','aperture','apex','appraise','approve',
        'arouse','article','assuage','attachment','average','avert','avoid','balk','barricade',
        'barrier','benefit','block','breach','breakdown','brighten','broaden','cancel',
        'capacious','cardinal','castigate','casual','catastrophe','cautious','charge','check',
        'chiefly','choice','choose','circular','climax','close','cohere','coil','collapse',
        'colloquial','colossal','commodious','compulsive','conceal','conceit','concerned',
        'concert','concession','conciliatory','concoct','condemn','confuse','congested',
        'conscience','conscious','consecutive','console','conspicuous','constraint',
        'constrict','construe','contempt','contender','contingent','contravene','contrite',
        'controvert','convene','copy','correspondence','corresponding','corroborate','corrode',
        'countless','court','cover','coverage','crave','credit','credulous','crisp','critical',
        'crumble','crumple','cryptic','crystal','culmination','culpable','curb','curtail',
        'dangerous','dead','deadly','debatable','debt','decadence','decay','decide','decry',
        'defect','defection','defective','defer','defile','deform','defy','degenerate',
        'degrade','delete','deleterious','delineate','demolish','demur','dense','depart',
        'depict','deprecate','depress','deride','deserve','design','desirable','desire',
        'desirous','despatch','destine','destiny','destructive','detach','detached',
        'deterrent','detest','detract','detriment','detrimental','devastate','device','devoid',
        'devoted','devour','dexterous','dilate','dilemma','diminutive','disarm','disarming',
        'disarray','disaster','disband','disclaim','discount','disfigure','disgrace','disgust',
        'disinterested','disparage','dispatch','dispensable','displace','dispose',
        'disproportionate','disprove','disrepute','disrespect','disrupt','dissemble',
        'disseminate','dissimilar','dissipate','distant','distasteful','distort','distract',
        'distressed','disunite','domestic','donate','donor','doom','doubt','doubtful',
        'drawback','drift','due','dumb','dungeon','dwindle','eccentric','edge','effectuate',
        'effuse','elite','elucidate','elude','elusive','emaciate','emaciated','embellish',
        'emphatic','empty','emulate','encompass','encourage','encumber','endanger','energize',
        'enervate','engender','engross','engrossed','engulf','enigma','enigmatic','enlighten',
        'enrich','enslave','entail','entangle','entice','entrap','entrenched','envelop',
        'envision','equitable','equivocal','equivocate','erase','erode','erupt','eschew',
        'evacuate','evade','evasion','evasive','evoke','exception','exceptional','excuse',
        'exhale','exhaust','exhaustive','expansive','expound','extricate','fallible',
        'familiarize','fascinate','fashionable','feeble','feign','ferret','fertile',
        'fertilizer','fervent','fetter','feud','fidelity','figment','figure-head','finance',
        'fine','fishy','fitful','fixed','flaw','flicker','flimsy','flout','foil','foment',
        'forbid','foremost','forestall','foretell','forsake','forte','forth','fortify',
        'fortitude','fortuitous','fortunate','fortune','foul','fragment','fragmentary',
        'fragrant','frail','fraught','fray','fund','further','futile','fuzz','gainful',
        'gainsay','gallery','gap','garnish','general','generally','gibe','gist','glamorous',
        'glamour','glaring','glean','gorgeous','graduate','graft','grievance','grotty',
        'guileless','habituate','haggle','hamper','handicap','handy','haphazard','hardly',
        'harry','harvest','hatch','haunt','haven','hazard','hazardous','head','headquarters',
        'headstrong','heedless','helpless','heredity','heritage','heyday','highlight','hinder',
        'hubbub','human','hypersensitive','idiosyncrasy','ignite','ignoble','illegible',
        'illuminate','illusion','imaginary','immense','immobile','impair','impale','impart',
        'impartial','impassioned','impassive','impel','imperative','impervious','imposing',
        'impressively','impropriety','impure','incandescent','incapacitate','incessant',
        'incipient','incite','incoherent','incompetent','incongruity','incorruptible',
        'incredulity','indefinite','indent','indignity','indomitable','ineligible','inertial',
        'infallible','inflict','informal','inject','injure','injurious','innumerable',
        'inordinate','inquiry','insignificant','insinuate','install','instigate','instrument',
        'instrumental','insubordinate','insufferable','insufficient','insult','insurmountable',
        'intelligible','intensify','intensive','intercede','intercept','interest','interfere',
        'interject','inure','invade','involuntary','irradiate','irreconcilable',
        'irrepressible','irreproachable','irresistible','irresolute','irreverence',
        'irreverent','irreversible','irrevocable','jeopardy','judgement','jumble','junction',
        'justly','ken','kidnap','lag','land','languish','lead','leak','legacy','liaison',
        'licenced','lifesaver','literate','lithe','loan','long-standing','loose','lown','lurk',
        'mainspring','mirage','opportunity','presence','preserve','pressure','presumably',
        'pretense','pretension','prevailing','probe','proceeding','proceeds','proclivity',
        'prod','prodigious','prodigy','produce','proficiency','profoundly','progress',
        'progression','prohibit','prohibitive','prohibitively','projecting','projectionist',
        'projector','prominence','promoter','prone','pronounced','proof','proofread',
        'propellant','propensity','property','proponent','proposal','propulsion','prospecting',
        'prospector','prosper','protagonist','protectionist','prototype','prototypical',
        'protruding','provincialism','provocative','pry open','psychology','publicity',
        'publicize','pueblo','pulp','pump','puncture','pungent','pupil','purification',
        'purified','purify','purple','puzzle','puzzling','quaint','qualification',
        'quantitative','quarterly','quench','quest','questionable','questionnaire','quilter',
        'radiant','radiate','radiation','radically','raft','rally','rank','rare','rarefy',
        'rarely','raucous','readjust','realization','rebellious','recall','reception',
        'receptionist','receptive','receptor','recession','recipe','recital','reckon',
        'reclaim','recognition','recognize','recollection','recommendation','reconstruct',
        'reconstruction','rectangular','recycle','redirect','reed','refine','refinement',
        'reflection','reformer','reformism','refreshing','refrigerant','refrigerate',
        'refrigerator','refurbish','regardless','regardless of','regime','regulation',
        'regulatory','rehabilitation','reigning','reinterpretation','rejection','rejuvenate',
        'rekindle','relax','relaxed','relay','relevance','reliability','reliance','reliant',
        'relic','relieve','relieved','religious','remainder','remaining','remarkably',
        'reminder','rendering','rendition','renewable','renounce','renovate','rentable',
        'rental','renunciation','reorient','repetition','replace','replica','replicate',
        'represent','representation','representative','repress','reproduce','repute','reputed',
        'reschedule','rescue','resemblance','resent','reserve','reservoir','resident',
        'residual','resist','resistant','resolution','resort','respectively','responsibility',
        'responsive','restraint','restriction','restrictive','retentive','retire','retool',
        'retract','retreat','retrieve','retriever','retrospect','retrospective','revered',
        'reverently','reversible','revision','revolt','ridicule','ridiculous','rigidity',
        'riot','ripe','ripen','risky','roast','rotation','rote','rough','roughly','routinely',
        'rubbery','rumble','rupture','rust','rustproof','sacred','sake','salient','saliva',
        'saltiness','sample','sanctimonious','sanction','sanctuary','sap','sapphire',
        'sarcastic','satisfactory','saturated','save','savings','scan','scarce','scarcely',
        'scare','scarlet','scene','scent','scholar','scholarly','scotch','scour','scramble',
        'scrape','scraping','scruple','scrupulously','scuba','seam','seamen','seasoning',
        'seclude','seclusion','secondary','secret','sectional','securely','security',
        'sedentary','segregate','self-sufficient','sensation','sensational','sensibility',
        'sensitivity','sensory','sentimentalize','sequester','serious','seriously','serrated',
        'set aside for','setting','sewer','shallow','sharply','shepherd','shield','shifting',
        'shine','shingle','shining','shiny','shrink','shrivel','sidestep','significance',
        'signify','silly','simplicity','skeptical','skepticism','skimp','skip class','slander',
        'slash','slender','slice','slight','slightly','slime','slip','smash','smother',
        'snap','snare','soar','sober','sole','solely','solicit','solid','solitary',
        'solve','sophisticate','spacious','span','spark','spawn','specimen','spectacle',
        'spectacular','speculate','spin','splendid','spontaneous','sprint','spur','square',
        'squeeze','stabilize','stagnant','stagnate','stake','stale','stall','stampede',
        'standpoint','standstill','stark','startling','static','steadfast','steadily',
        'steep','stem','stern','stimulate','stint','stir','strategic','strenuous',
        'stride','striking','stringent','strip','strive','stubborn','stumble','stun',
        'stunning','subdue','subject','sublime','submit','subordinate','subsequent',
        'subside','substantial','substantiate','substitute','subtle','subtract','succeed',
        'succession','successive','succinct','succumb','sufficient','suffocate','summit',
        'summon','superb','superficial','superfluous','supplement','suppress','surmount',
        'surplus','surrender','susceptible','suspect','suspend','sustain','swagger',
        'sway','swift','symmetry','sympathy','synchronize','synthetic','tactic','taint',
        'tangible','tardy','tedious','tempt','tenacious','tentative','terminal','terminate',
        'terrain','terrific','testify','testimony','thorough','thrive','thrust','tolerate',
        'torment','toxic','trail','trait','transcend','transform','transient','transition',
        'transmit','transparent','transport','traverse','tremendous','trespass','trivial',
        'tumble','turbulent','turn','ultimate','unanimous','underestimate','underlie',
        'undermine','undoubtedly','unfold','unify','unique','universal','unprecedented',
        'unveil','uphold','urgent','utmost','utter','vacant','vague','valid','vanish',
        'variable','vast','venture','verify','versatile','veteran','viable','vibrant',
        'vigorous','vindicate','violate','virtual','virtue','vivid','volatile','volume',
        'voluntary','vulnerable','wander','warrant','wary','waver','whirl','wholesome',
        'widespread','wield','wither','withstand','worsen','worthy','wreck','yield','zeal',
    ]),
    ]
    for topic, words in groups:
        for w in words:
            if w not in m:
                m[w] = topic
    return m

WORD_TOPIC_MAP = _build_word_topic_map()


TOPIC_ORDER = [
    "地理与地质 Geography & Geology",
    "天文学 Astronomy",
    "气象与气候 Weather & Climate",
    "物理学 Physics",
    "化学与材料 Chemistry & Materials",
    "生物学 Biology",
    "动物与生态 Zoology & Ecology",
    "植物学 Botany",
    "环境科学 Environmental Science",
    "医学与健康 Medicine & Health",
    "数学与几何 Mathematics & Geometry",
    "农业 Agriculture",
    "饮食 Food & Cooking",
    "考古与历史 Archaeology & History",
    "人类学与社会学 Anthropology & Sociology",
    "政治与社会制度 Politics & Social Systems",
    "法律与制度 Law & Governance",
    "军事 Military",
    "经济与商业 Economics & Business",
    "教育 Education",
    "艺术与文学 Art & Literature",
    "语言与写作 Language & Writing",
    "宗教与哲学 Religion & Philosophy",
    "职业与人物 Professions & People",
    "品性（褒义）Positive Traits",
    "品性（贬义）Negative Traits",
    "核心学术概念 Core Academic Concepts",
    "时间与变化 Time & Change",
    "运动与流体 Motion & Fluids",
    "情绪与心理 Emotions & Psychology",
    "社会关系 Social Relations",
    "名望与成就 Fame & Achievement",
    "礼仪与情感 Etiquette & Emotions",
    "身体动作 Body Movements",
    "工具与劳动 Tools & Labor",
    "日常器物 Everyday Objects",
    "建筑与住所 Architecture & Dwellings",
    "交通与旅行 Travel & Transport",
    "日常生活 Daily Life",
    "品性与状态 Character & States",
    "欺诈与犯罪 Fraud & Crime",
    "科技与计算 Technology & Computing",
    "心理健康 Mental Health",
    "校园生活 Campus Life",
    "通用词汇 General Vocabulary",
]


# ── Parse helpers ──

def parse_word(line):
    """Extract word from a line (strip definitions after tab)."""
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None
    # Remove line-number prefix like "   10|"
    line = re.sub(r'^\s*\d+\|', '', line)
    line = line.strip()
    if not line:
        return None, None
    # Some words have backtick prefixes like `attribute
    line = line.lstrip('`')
    parts = line.split('\t', 1)
    word = parts[0].strip()
    defn = parts[1].strip() if len(parts) > 1 else ''
    # Clean word
    word = word.strip('`').strip()
    if not word or not re.match(r'^[A-Za-z]', word):
        return None, None
    # Some have =alternate like "cozy=cosy"
    word = word.split('=')[0].strip()
    # Skip "..." placeholder lines
    if word == '...':
        return None, None
    return canonical_word(word), defn


def parse_1791():
    """Parse simple word list."""
    words = {}
    # Prefer the maintained 1791 source with definitions; the legacy file is
    # only a bare word inventory.
    path = os.path.join(BASE, 'my-tofel-1791words-words.txt')
    if not os.path.exists(path):
        path = os.path.join(BASE, 'tofel_words_1791.txt')
    with open(path, encoding='utf-8') as f:
        for line in f:
            w, d = parse_word(line)
            if w:
                words[w] = d or ''
    return words


def parse_1925():
    """Parse word+definition list."""
    words = {}
    path = os.path.join(BASE, 'my-tofel-1925words-words.txt')
    with open(path, encoding='utf-8') as f:
        for line in f:
            w, d = parse_word(line)
            if w:
                words[w] = d
    return words


def parse_1675():
    """Parse word+definition list, return {word: defn} and {word: topic}."""
    words = {}
    topics = {}
    path = os.path.join(BASE, 'my-tofel-1675words-words.txt')
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        w, d = parse_word(line)
        if not w:
            continue
        words[w] = d
        # Find topic from ranges
        for start, end, topic in TOPIC_RANGES_1675:
            if start <= i <= end:
                topics[w] = topic
                break
    return words, topics


# ── Manual overrides: highest priority corrections ──
MANUAL_FIXES = {
    # Weather → correct topic
    "spaceship": "天文学 Astronomy", "space shuttle": "天文学 Astronomy",
    "spacecraft": "天文学 Astronomy", "solar cell": "物理学 Physics",
    "sunflower": "植物学 Botany", "trough": "农业 Agriculture",
    "plantation": "农业 Agriculture", "ranch": "农业 Agriculture",
    "serene": "情绪与心理 Emotions & Psychology",
    # Remove clear keyword-based classification false positives.
    "aggression": "核心学术概念 Core Academic Concepts",
    "assault": "欺诈与犯罪 Fraud & Crime",
    "clot": "医学与健康 Medicine & Health",
    "clutter": "日常生活 Daily Life",
    "circuitous": "通用词汇 General Vocabulary",
    "discrete": "核心学术概念 Core Academic Concepts",
    "dual": "核心学术概念 Core Academic Concepts",
    "facet": "核心学术概念 Core Academic Concepts",
    "plumb": "核心学术概念 Core Academic Concepts",
    "qualitative": "核心学术概念 Core Academic Concepts",
    "harsh": "通用词汇 General Vocabulary",
    "intoxicate": "通用词汇 General Vocabulary",
    "regimentation": "核心学术概念 Core Academic Concepts",
    "sunburn": "医学与健康 Medicine & Health", "sundial": "日常器物 Everyday Objects",
    "tide": "地理与地质 Geography & Geology",
    # Math
    "divide": "数学与几何 Mathematics & Geometry",
    "fraction": "数学与几何 Mathematics & Geometry",
    "percentage": "数学与几何 Mathematics & Geometry",
    "quarter": "数学与几何 Mathematics & Geometry",
    "numeral": "数学与几何 Mathematics & Geometry",
    "cubic": "数学与几何 Mathematics & Geometry",
    "equation": "数学与几何 Mathematics & Geometry",
    "proportion": "数学与几何 Mathematics & Geometry",
    # Geography
    "erosion": "地理与地质 Geography & Geology",
    "canyon": "地理与地质 Geography & Geology",
    "creek": "地理与地质 Geography & Geology",
    "gorge": "地理与地质 Geography & Geology",
    "summit": "地理与地质 Geography & Geology",
    "scenic": "地理与地质 Geography & Geology",
    "ridge": "地理与地质 Geography & Geology",
    "avalanche": "地理与地质 Geography & Geology",
    "precipitous": "地理与地质 Geography & Geology",
    "hydrosphere": "地理与地质 Geography & Geology",
    # Astronomy
    "universe": "天文学 Astronomy", "telescope": "天文学 Astronomy",
    # Agriculture
    "crossbreed": "农业 Agriculture", "agrarian": "农业 Agriculture",
    "barley": "农业 Agriculture", "beet": "农业 Agriculture",
    "fertile": "农业 Agriculture", "fertilizer": "农业 Agriculture",
    "harvest": "农业 Agriculture", "arable": "农业 Agriculture",
    "aquaculture": "农业 Agriculture",
    # Food
    "eggplant": "饮食 Food & Cooking", "squash": "饮食 Food & Cooking",
    "cabbage": "饮食 Food & Cooking", "celery": "饮食 Food & Cooking",
    "cereal": "饮食 Food & Cooking", "broccoli": "饮食 Food & Cooking",
    "butter": "饮食 Food & Cooking", "brew": "饮食 Food & Cooking",
    "banquet": "饮食 Food & Cooking", "sustenance": "饮食 Food & Cooking",
    "delicious": "饮食 Food & Cooking",
    # Zoology
    "fauna": "动物与生态 Zoology & Ecology",
    "buffalo": "动物与生态 Zoology & Ecology",
    "clam": "动物与生态 Zoology & Ecology",
    "coral": "动物与生态 Zoology & Ecology",
    "oyster": "动物与生态 Zoology & Ecology",
    "plankton": "动物与生态 Zoology & Ecology",
    "parasite": "动物与生态 Zoology & Ecology",
    "nocturnal": "动物与生态 Zoology & Ecology",
    "flounder": "动物与生态 Zoology & Ecology",
    "wildlife": "动物与生态 Zoology & Ecology",
    "butterfly": "动物与生态 Zoology & Ecology",
    # Botany
    "graft": "植物学 Botany", "locoweed": "植物学 Botany",
    "spined": "植物学 Botany",
    # Biology
    "hybrid": "生物学 Biology", "heredity": "生物学 Biology",
    "skeleton": "生物学 Biology", "skull": "生物学 Biology",
    "mold": "生物学 Biology",
    # Medicine
    "anatomy": "医学与健康 Medicine & Health",
    "diagnose": "医学与健康 Medicine & Health",
    "diagnosis": "医学与健康 Medicine & Health",
    "dissect": "医学与健康 Medicine & Health",
    "fracture": "医学与健康 Medicine & Health",
    "fester": "医学与健康 Medicine & Health",
    "hygiene": "医学与健康 Medicine & Health",
    "malnourished": "医学与健康 Medicine & Health",
    "prescription": "医学与健康 Medicine & Health",
    "remedy": "医学与健康 Medicine & Health",
    "sterile": "医学与健康 Medicine & Health",
    "recur": "医学与健康 Medicine & Health",
    "relapse": "医学与健康 Medicine & Health",
    "chronic": "医学与健康 Medicine & Health",
    "necrosis": "医学与健康 Medicine & Health",
    "cranial": "医学与健康 Medicine & Health",
    "sanitary": "医学与健康 Medicine & Health",
    "vessel": "医学与健康 Medicine & Health",
    # Physics
    "decibel": "物理学 Physics", "lens": "物理学 Physics",
    "magnifier": "物理学 Physics", "spectrum": "物理学 Physics",
    "optical": "物理学 Physics", "ductile": "物理学 Physics",
    # Chemistry
    "slag": "化学与材料 Chemistry & Materials",
    # Economics
    "exorbitant": "经济与商业 Economics & Business",
    "bonus": "经济与商业 Economics & Business",
    "commission": "经济与商业 Economics & Business",
    "revenue": "经济与商业 Economics & Business",
    "deposit": "经济与商业 Economics & Business",
    "barter": "经济与商业 Economics & Business",
    "bond": "经济与商业 Economics & Business",
    "custom": "经济与商业 Economics & Business",
    "asset": "经济与商业 Economics & Business",
    "prosperity": "经济与商业 Economics & Business",
    "prosperous": "经济与商业 Economics & Business",
    "toll": "经济与商业 Economics & Business",
    "finance": "经济与商业 Economics & Business",
    "incentive": "经济与商业 Economics & Business",
    "auditor": "经济与商业 Economics & Business",
    "subsidiary": "经济与商业 Economics & Business",
    # Politics
    "constituent": "政治与社会制度 Politics & Social Systems",
    "municipal": "政治与社会制度 Politics & Social Systems",
    "scandal": "政治与社会制度 Politics & Social Systems",
    "partisan": "政治与社会制度 Politics & Social Systems",
    "protest": "政治与社会制度 Politics & Social Systems",
    "strike": "政治与社会制度 Politics & Social Systems",
    "walkout": "政治与社会制度 Politics & Social Systems",
    # Law
    "counsel": "法律与制度 Law & Governance",
    # Military
    "soldier": "军事 Military", "warrior": "军事 Military",
    "headquarters": "军事 Military",
    # Education
    "didactic": "教育 Education", "graduate": "教育 Education",
    "coach": "教育 Education",
    # Art & Literature
    "sculptural": "艺术与文学 Art & Literature",
    "gallery": "艺术与文学 Art & Literature",
    "playwright": "艺术与文学 Art & Literature",
    "craft": "艺术与文学 Art & Literature",
    "impromptu": "艺术与文学 Art & Literature",
    "improvise": "艺术与文学 Art & Literature",
    "audition": "艺术与文学 Art & Literature",
    "rhythmic": "艺术与文学 Art & Literature",
    "rhythmical": "艺术与文学 Art & Literature",
    # Language
    "hackneyed": "语言与写作 Language & Writing",
    "news coverage": "语言与写作 Language & Writing",
    # Religion
    "sermon": "宗教与哲学 Religion & Philosophy",
    "veneration": "宗教与哲学 Religion & Philosophy",
    "clergy": "宗教与哲学 Religion & Philosophy",
    "sect": "宗教与哲学 Religion & Philosophy",
    "doctrine": "宗教与哲学 Religion & Philosophy",
    # Emotions
    "homesick": "情绪与心理 Emotions & Psychology",
    "solitude": "情绪与心理 Emotions & Psychology",
    # Archaeology
    "archeology": "考古与历史 Archaeology & History",
    # Anthropology
    "cosmopolitan": "人类学与社会学 Anthropology & Sociology",
    # Everyday objects
    "microwave": "日常器物 Everyday Objects",
    "jar": "日常器物 Everyday Objects",
    "lampshade": "日常器物 Everyday Objects",
    "spectacle": "日常器物 Everyday Objects",
    "textile": "日常器物 Everyday Objects",
    "waterproof": "日常器物 Everyday Objects",
    # Architecture
    "cement": "建筑与住所 Architecture & Dwellings",
    "fixture": "建筑与住所 Architecture & Dwellings",
    # Body movements
    "quiver": "身体动作 Body Movements",
    "trot": "身体动作 Body Movements",
    "grip": "身体动作 Body Movements",
    # Environment
    "sanitation": "环境科学 Environmental Science",
    # Transport
    "navigation": "交通与旅行 Travel & Transport",
    # Negative traits
    "brutal": "品性（贬义）Negative Traits",
    "crooked": "品性（贬义）Negative Traits",
    "grumpy": "品性（贬义）Negative Traits",
    "imprudent": "品性（贬义）Negative Traits",
    "impudent": "品性（贬义）Negative Traits",
    "indolent": "品性（贬义）Negative Traits",
    "prodigal": "品性（贬义）Negative Traits",
    "sluggish": "品性（贬义）Negative Traits",
    "sly": "品性（贬义）Negative Traits",
    "snobbish": "品性（贬义）Negative Traits",
    "spineless": "品性（贬义）Negative Traits",
    "stingy": "品性（贬义）Negative Traits",
    "sloth": "品性（贬义）Negative Traits",
    "slothful": "品性（贬义）Negative Traits",
    "idiocy": "品性（贬义）Negative Traits",
    "moron": "品性（贬义）Negative Traits",
    "brag": "品性（贬义）Negative Traits",
    # Positive traits
    "auspicious": "品性（褒义）Positive Traits",
    "boon": "品性（褒义）Positive Traits",
    "stamina": "品性（褒义）Positive Traits",
    "vigor": "品性（褒义）Positive Traits",
    # Tools
    "gear": "工具与劳动 Tools & Labor",
    # Weather (correct moves INTO weather)
    "breeze": "气象与气候 Weather & Climate",
    "atmosphere": "气象与气候 Weather & Climate",
    # Definition-based placement corrections (override source-list ranges).
    "aluminum": "化学与材料 Chemistry & Materials", "aluminium": "化学与材料 Chemistry & Materials",
    "desalination": "环境科学 Environmental Science", "endemic": "生物学 Biology",
    "magnitude": "物理学 Physics", "moist": "气象与气候 Weather & Climate",
    "fieldstone": "建筑与住所 Architecture & Dwellings", "weathering": "地理与地质 Geography & Geology",
    "astrology": "宗教与哲学 Religion & Philosophy", "pseudoscience": "宗教与哲学 Religion & Philosophy",
    "emission": "物理学 Physics", "condense": "物理学 Physics", "current": "物理学 Physics",
    "droplet": "运动与流体 Motion & Fluids", "sunlight": "物理学 Physics",
    "dilute": "化学与材料 Chemistry & Materials", "particle": "物理学 Physics",
    "proliferation": "生物学 Biology", "revolve": "天文学 Astronomy",
    "ventilation": "建筑与住所 Architecture & Dwellings", "chafe": "身体动作 Body Movements",
    "biochemistry": "生物学 Biology", "explosive": "军事 Military", "blend": "饮食 Food & Cooking",
    "sear": "饮食 Food & Cooking", "stale": "饮食 Food & Cooking", "symmetry": "数学与几何 Mathematics & Geometry",
    "induction": "核心学术概念 Core Academic Concepts", "inference": "核心学术概念 Core Academic Concepts",
    "microbe": "生物学 Biology", "regeneration": "生物学 Biology", "squirt": "运动与流体 Motion & Fluids",
    "starch": "化学与材料 Chemistry & Materials", "scatter": "核心学术概念 Core Academic Concepts",
    "opaque": "物理学 Physics", "transparent": "物理学 Physics", "translucent": "物理学 Physics",
    "rectify": "核心学术概念 Core Academic Concepts", "refraction": "物理学 Physics",
    "refrigeration": "日常器物 Everyday Objects", "silt": "地理与地质 Geography & Geology",
    "ascend": "身体动作 Body Movements", "indigenous": "人类学与社会学 Anthropology & Sociology",
    "invaluable": "品性（褒义）Positive Traits", "prolific": "品性（褒义）Positive Traits",
    "smuggle": "欺诈与犯罪 Fraud & Crime", "clan": "人类学与社会学 Anthropology & Sociology",
    "territory": "地理与地质 Geography & Geology", "observance": "宗教与哲学 Religion & Philosophy",
    "prescribe": "医学与健康 Medicine & Health", "credential": "教育 Education",
    "domineering": "品性（贬义）Negative Traits", "ransom": "欺诈与犯罪 Fraud & Crime",
    "onset": "时间与变化 Time & Change", "array": "数学与几何 Mathematics & Geometry",
    "cipher": "语言与写作 Language & Writing", "corpse": "生物学 Biology", "dagger": "日常器物 Everyday Objects",
    "career": "职业与人物 Professions & People", "staff": "职业与人物 Professions & People",
    "exponent": "数学与几何 Mathematics & Geometry", "inertia": "物理学 Physics",
    "quotation": "语言与写作 Language & Writing", "redress": "法律与制度 Law & Governance",
    "renovation": "建筑与住所 Architecture & Dwellings", "residue": "化学与材料 Chemistry & Materials",
    "retirement": "时间与变化 Time & Change", "dialogue": "语言与写作 Language & Writing",
    "movement": "物理学 Physics", "sentimentalism": "情绪与心理 Emotions & Psychology",
    "wind": "气象与气候 Weather & Climate", "tense": "语言与写作 Language & Writing",
    "ascetic": "宗教与哲学 Religion & Philosophy", "facility": "核心学术概念 Core Academic Concepts",
    "ravenous": "情绪与心理 Emotions & Psychology", "stunt": "身体动作 Body Movements",
    "temperament": "情绪与心理 Emotions & Psychology", "economical": "经济与商业 Economics & Business",
    "economize": "经济与商业 Economics & Business", "avidity": "品性（褒义）Positive Traits",
    "accomplished": "品性（褒义）Positive Traits", "adept": "品性（褒义）Positive Traits",
    "aptitude": "品性（褒义）Positive Traits", "deft": "品性（褒义）Positive Traits",
    "skillful": "品性（褒义）Positive Traits", "avid": "品性（褒义）Positive Traits",
    "designing": "品性（贬义）Negative Traits", "drastic": "核心学术概念 Core Academic Concepts",
    "stringent": "核心学术概念 Core Academic Concepts", "ordeal": "品性与状态 Character & States",
    "stocky": "身体动作 Body Movements", "stern": "品性（贬义）Negative Traits",
    "facetious": "品性（贬义）Negative Traits",
    "virus": "生物学 Biology", "captivate": "情绪与心理 Emotions & Psychology",
    "projection": "核心学术概念 Core Academic Concepts", "suspect": "欺诈与犯罪 Fraud & Crime",
    "uniform": "日常器物 Everyday Objects", "yield": "核心学术概念 Core Academic Concepts",
    "astronaut": "天文学 Astronomy", "astronomer": "天文学 Astronomy",
    "botanist": "植物学 Botany", "ecologist": "动物与生态 Zoology & Ecology",
    "anthropologist": "人类学与社会学 Anthropology & Sociology",
    "advocate": "法律与制度 Law & Governance", "arbitrator": "法律与制度 Law & Governance",
    "alumni": "教育 Education", "educator": "教育 Education", "superintendent": "教育 Education",
    "monarch": "政治与社会制度 Politics & Social Systems", "rebel": "政治与社会制度 Politics & Social Systems",
    "debtor": "经济与商业 Economics & Business", "orator": "语言与写作 Language & Writing",
    "satirist": "语言与写作 Language & Writing", "veteran": "军事 Military",
    "domesticate": "农业 Agriculture", "fertilize": "植物学 Botany", "gasp": "身体动作 Body Movements",
    "peck": "身体动作 Body Movements", "regeneration": "生物学 Biology", "spleen": "医学与健康 Medicine & Health",
    "grease": "日常器物 Everyday Objects", "hide": "动物与生态 Zoology & Ecology",
    "restoration": "建筑与住所 Architecture & Dwellings", "meadow": "地理与地质 Geography & Geology",
    "puddle": "运动与流体 Motion & Fluids", "trickle": "运动与流体 Motion & Fluids",
    "cooperation": "社会关系 Social Relations", "deduction": "核心学术概念 Core Academic Concepts",
    "estimate": "核心学术概念 Core Academic Concepts", "functional": "核心学术概念 Core Academic Concepts",
    "conservatory": "建筑与住所 Architecture & Dwellings", "roost": "动物与生态 Zoology & Ecology",
    "saline": "化学与材料 Chemistry & Materials", "invaluable": "品性（褒义）Positive Traits",
    "prolific": "品性（褒义）Positive Traits", "household": "日常生活 Daily Life",
    "exodus": "考古与历史 Archaeology & History", "fatalism": "宗教与哲学 Religion & Philosophy",
    "immerse": "核心学术概念 Core Academic Concepts", "limpid": "品性（褒义）Positive Traits",
    "exotic": "通用词汇 General Vocabulary", "unconventional": "通用词汇 General Vocabulary",
}


def classify_word(word, defn, known_topics):
    """Classify a word into a discipline."""
    # Manual fixes have highest priority
    if word in MANUAL_FIXES:
        return MANUAL_FIXES[word]
    if word in known_topics:
        return known_topics[word]
    # Check direct word→topic map
    if word in WORD_TOPIC_MAP:
        return WORD_TOPIC_MAP[word]
    text = (word + ' ' + defn).lower()
    for topic, keywords in CLASSIFY_RULES:
        for kw in keywords:
            # For short keywords (<=4 chars), use word-boundary matching
            if len(kw) <= 4:
                if re.search(r'\b' + re.escape(kw) + r'\b', text):
                    return topic
            else:
                if kw in text:
                    return topic
    return "通用词汇 General Vocabulary"


# A part-of-speech label must carry its dot (``n.``), otherwise plain English
# words such as ``a`` or ``n`` in example sentences are mistaken for labels.
POS_LABEL_RE = re.compile(
    r'(?<![A-Za-z])(?:(adj|adv|prep|conj|pron|num|phr\.?\s*v|phr|noun|verb|vt|vi|a|n|v)\.'
    r'|(idiom))',
    re.I,
)


def normalize_pos(label):
    label = label.lower().replace(' ', '')
    return {'a': 'adj.', 'adj': 'adj.', 'adjective': 'adj.',
            'adv': 'adv.', 'adverb': 'adv.', 'noun': 'n.', 'n': 'n.',
            'verb': 'v.', 'vt': 'v.', 'vi': 'v.', 'v': 'v.',
            'phr': 'phr.', 'phrv': 'phr. v.', 'idiom': 'idiom',
            'prep': 'prep.', 'conj': 'conj.', 'pron': 'pron.',
            'num': 'num.'}.get(label, label + '.')


def explicit_pos(definitions):
    found = []
    for definition in definitions:
        for match in POS_LABEL_RE.finditer(definition or ''):
            label = match.group(1) or match.group(2)
            pos = normalize_pos(label)
            if pos not in found:
                found.append(pos)
    # Keep conventional order and avoid treating a phrase marker as a word POS.
    order = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.', 'num.', 'phr.', 'phr. v.', 'idiom']
    return [p for p in order if p in found]


SENSE_SPLIT_RE = re.compile(r'[；;，,、/／]')

# ``-ly`` words that are adjectives rather than adverbs.
ADJ_LY_WORDS = {
    'deadly', 'friendly', 'lonely', 'likely', 'unlikely', 'lively', 'lovely',
    'costly', 'orderly', 'stately', 'scholarly', 'timely', 'ugly', 'silly',
    'holy', 'cowardly', 'elderly', 'worldly', 'portly', 'burly', 'godly',
    'homely', 'manly', 'curly', 'surly', 'oily', 'jolly', 'lowly', 'kindly',
    'motherly', 'brotherly', 'sisterly', 'leisurely', 'unruly', 'saintly',
    'princely', 'heavenly', 'earthly', 'ghastly', 'sprightly', 'unsightly',
}


def _senses(text):
    """Chinese sense fragments of a definition, without labels or notes."""
    text = re.sub(r'\[(?:ph|st|syn|mean|def|ex|n|v|adj|adv)\][\s\S]*$', '', text or '')
    text = text.split('\n')[0]
    text = re.sub(r'(?<![A-Za-z])(?:adj|adv|prep|conj|pron|num|phr|noun|verb|vt|vi|n|v)[ \t]?\.', '', text, flags=re.I)
    text = re.sub(r'[（(][^）)]*[）)]', '', text)
    out = []
    for part in SENSE_SPLIT_RE.split(text):
        part = part.strip(' \t。.:："“”\'')
        if re.search(r'[\u4e00-\u9fff]', part) and len(part) <= 12:
            out.append(part)
    return out


def gloss_pos_hint(definition):
    """Guess a part of speech from the shape of the Chinese gloss."""
    senses = _senses(definition)
    if not senses:
        return None
    if all(s.endswith('地') for s in senses):
        return 'adv.'
    if all(s.endswith('的') for s in senses):
        return 'adj.'
    if all(re.match(r'^(?:使|把|予以|加以)', s) for s in senses):
        return 'v.'
    return None


# Cambridge dumps give a reliable clue: verb senses are phrased "to ...".
CAMBRIDGE_POS = {}


def _load_cambridge_pos():
    for name in ('cambridge_defs_1791.json', 'cambridge_defs_1925.json'):
        path = os.path.join(BASE, 'output', name)
        try:
            with open(path, encoding='utf-8') as handle:
                data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        for word, entry in data.items():
            defs = [d for d in (entry.get('defs') or []) if d]
            if not defs:
                continue
            first = defs[0].strip().lower()
            if first.startswith(('to ', 'to(', '(of ', 'if ')) and ' to ' in f' {first} ':
                pos = 'v.' if first.startswith(('to ', 'to(')) else None
            elif first.startswith(('a ', 'an ', 'the ', 'someone ', 'something ',
                                   'a person', 'any ', 'one of')):
                pos = 'n.'
            else:
                pos = None
            if pos:
                CAMBRIDGE_POS.setdefault(word.lower(), pos)


_load_cambridge_pos()


def inferred_pos(word, definition=''):
    """Conservative fallback: provide a reviewable POS instead of a blank label."""
    hint = gloss_pos_hint(definition)
    if hint:
        return [hint]
    if ' ' in word or '-' in word:
        return ['phr.']
    lower = word.lower()
    if lower in CAMBRIDGE_POS:
        return [CAMBRIDGE_POS[lower]]
    if lower.endswith('ly') and not lower.endswith(('ply', 'uly', 'lly', 'ily')):
        return ['adv.']
    # Noun and verb suffixes are checked before adjective ones, because endings
    # such as ``-ment`` and ``-ity`` also end in an adjective-looking letter.
    if lower.endswith(('tion', 'sion', 'ment', 'ness', 'ity', 'ism', 'ship', 'ance',
                       'ence', 'hood', 'dom', 'ist', 'ology', 'graphy', 'ure', 'age',
                       'ency', 'ancy', 'acy', 'sis', 'tude', 'ee')):
        return ['n.']
    if lower.endswith(('ize', 'ise', 'ify', 'fy', 'en')):
        return ['v.']
    if lower.endswith(('ous', 'ful', 'less', 'ive', 'ical', 'able', 'ible', 'ish',
                       'ary', 'ory', 'ic', 'al', 'ent', 'ant', 'ile', 'ate')):
        return ['adj.']
    if lower.endswith(('er', 'or')):
        return ['n.']
    if lower.endswith('ed'):
        return ['adj.']
    return ['n.']


LEGACY_POS_MAP = {
    'a': 'adj.', 'ad': 'adv.', 'adj': 'adj.', 'adv': 'adv.',
    'vt': 'v.', 'vi': 'v.', 'cn': 'n.', 'un': 'n.', 'n': 'n.', 'v': 'v.',
}

# Only rewrite a legacy label when Chinese text follows it, so that English
# articles and abbreviations (``emend a text``) are never touched.
LEGACY_POS_RE = re.compile(
    r'(?<![A-Za-z])(a|ad|vt|vi|cn|un)[ \t]?\.[ \t]*(?=[\u4e00-\u9fff])',
    re.I,
)

# ``maritime  a 海的``: a dotless legacy label only counts at a segment start.
LEGACY_POS_BARE_RE = re.compile(
    r'(?:(?<=^)|(?<=\n)|(?<=[；;，,、/]))([ \t]*)(a|ad|vt|vi|cn|un)[ \t]+(?=[\u4e00-\u9fff])',
    re.I,
)

# ``n.a.`` and ``n./a.``: a legacy label glued to another label is unambiguous.
LEGACY_POS_ADJACENT_RE = re.compile(
    r'(?<=[./、,，])(a|ad|vt|vi|cn|un)[ \t]?\.',
    re.I,
)


def normalize_definition_pos(definition):
    """Normalize legacy labels such as ``a.``, ``vt.`` and ``cn.``."""
    if not definition:
        return definition

    def _sub(match):
        return LEGACY_POS_MAP[match.group(1).lower()] + ' '

    result = LEGACY_POS_RE.sub(_sub, definition)
    result = LEGACY_POS_BARE_RE.sub(
        lambda m: m.group(1) + LEGACY_POS_MAP[m.group(2).lower()] + ' ', result)
    return LEGACY_POS_ADJACENT_RE.sub(lambda m: LEGACY_POS_MAP[m.group(1).lower()], result)


def complete_pos(word, selected_def, all_defs):
    selected_def = normalize_definition_pos(selected_def)
    found = explicit_pos([selected_def] + all_defs)
    if not found:
        found = inferred_pos(word, selected_def)
    elif len(found) == 1 and found[0] in ('adj.', 'adv.'):
        # A legacy ``ad.``/``a.`` label is ambiguous: the word shape decides
        # first, then the shape of the Chinese gloss.
        lower = word.lower()
        if lower.endswith('ly') and lower not in ADJ_LY_WORDS and len(lower) > 4:
            hint = 'adv.'
        else:
            hint = gloss_pos_hint(selected_def)
        if hint in ('adj.', 'adv.') and hint != found[0]:
            selected_def = re.sub(
                r'^(\s*)(?:adj|adv)[ \t]?\.', lambda m: m.group(1) + hint,
                selected_def, count=1, flags=re.I)
            found = [hint]
    # If the selected definition has no label, make the evidence visible in the card.
    if not POS_LABEL_RE.match(selected_def.lstrip()):
        return ' '.join(found) + ' ' + selected_def
    return selected_def


def merge_definitions(defs_list):
    """Merge multiple definitions, preferring the longest/most detailed."""
    defs = [d for d in defs_list if d]
    if not defs:
        return ''
    return max(defs, key=len)


# ── Main ──

def main():
    print("Parsing word lists...")
    w1791 = parse_1791()
    w1925 = parse_1925()
    w1675, topics_1675 = parse_1675()

    # Load new scenario words (2026 new TOEFL listening gaps)
    scenario_path = os.path.join(BASE, 'new_scenario_words.json')
    scenario_topics = {}
    scenario_words = {}
    try:
        with open(scenario_path, encoding='utf-8') as f:
            scenario_data = json.load(f)
            scenario_words = {k.lower(): v for k, v in scenario_data.get('words', {}).items()}
            scenario_topics = {k.lower(): v for k, v in scenario_data.get('topics', {}).items()}
        print(f"  Scenario words: {len(scenario_words)} words loaded")
    except (FileNotFoundError, json.JSONDecodeError):
        print("  Scenario words: not found, skipping")
    # Add curated high-frequency discipline terminology separately from scenario words.
    scenario_words.update(HIGH_FREQ_WORDS)
    scenario_topics.update(HIGH_FREQ_TOPICS)
    print(f"  High-frequency discipline additions: {len(HIGH_FREQ_WORDS)} words loaded")
    print(f"  2026 exam-derived terms: {len(EXAM2026_WORDS)} words loaded "
          f"across {len(EXAM2026_GROUPS)} disciplines")

    print(f"  1791: {len(w1791)} words")
    print(f"  1925: {len(w1925)} words")
    print(f"  1675: {len(w1675)} words")

    # Merge: collect all words
    all_words = set()
    all_words.update(w1791.keys())
    all_words.update(w1925.keys())
    all_words.update(w1675.keys())
    all_words.update(scenario_words.keys())
    all_words.update(EXAM2026_WORDS.keys())
    print(f"  Merged (unique): {len(all_words)} words")

    # Merge scenario_topics into topics_1675 for classify_word
    known_topics = dict(topics_1675)
    known_topics.update(scenario_topics)
    # 2026 分组只给「本来没有明确归属」的词定学科，不搬动既有词，避免这次改动
    # 顺带把老词表的分类结果洗一遍。
    for w, t in EXAM2026_TOPICS.items():
        known_topics.setdefault(w, t)

    # For each word, pick best definition and classify
    word_data = {}
    for w in sorted(all_words):
        defs = []
        sources = []
        if w in w1675:
            defs.append(w1675[w])
            sources.append('1675')
        if w in w1925:
            defs.append(w1925[w])
            sources.append('1925')
        if w in w1791:
            defs.append(w1791[w])
            sources.append('1791')
        if w in scenario_words:
            defs.append(scenario_words[w])
            sources.append('scenario')
        if w in EXAM2026_WORDS:
            # 词条来自 2026 真实考场讲座话题所需术语；标签让页面能筛出这批词。
            defs.append(EXAM2026_WORDS[w])
            sources.append('2026')
        # Reviewed POS overrides have highest priority, followed by general
        # definition corrections and then the merged legacy source definitions.
        defn = POS_OVERRIDES.get(w, POS_REVIEW_CANDIDATES.get(w, DEFINITION_OVERRIDES.get(w, merge_definitions(defs))))
        # Normalize and guarantee a visible POS even when an override replaced
        # the source definition (legacy overrides may use a./vt./cn. labels).
        defn = complete_pos(w, defn, defs)
        topic = classify_word(w, defn, known_topics)
        word_data[w] = {
            'word': w,
            'defn': defn,
            'topic': topic,
            'sources': sources,
        }

    # Group by topic
    grouped = defaultdict(list)
    for w, data in word_data.items():
        grouped[data['topic']].append(data)

    # Sort each group alphabetically
    for topic in grouped:
        grouped[topic].sort(key=lambda x: x['word'])

    # Stats
    print("\nTopics:")
    missing_2026 = [t for t in TOPIC_ORDER if t not in TOPIC_2026]
    if missing_2026:
        # 新增学科必须同时登记 2026 权重，否则页面徽章会静默退化成「通用」。
        raise SystemExit(f"TOPIC_2026 缺少这些学科的 2026 权重登记: {missing_2026}")
    for topic in TOPIC_ORDER:
        if topic in grouped:
            print(f"  {EMOJI.get(topic, '📝')} {topic}: {len(grouped[topic])} words")
    if "通用词汇 General Vocabulary" in grouped:
        print(f"  📝 通用词汇 General Vocabulary: {len(grouped['通用词汇 General Vocabulary'])} words")

    total = sum(len(v) for v in grouped.values())
    print(f"\nTotal: {total} words across {len(grouped)} topics")

    # Generate HTML
    generate_html(grouped, total)
    print("Done! Output: merged-by-discipline/index.html")


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


POS_TOKEN_RE = re.compile(
    r'(?<![A-Za-z])(?:adj|adv|prep|conj|pron|num|phr\.?\s*v|phr|noun|verb|vt|vi|n|v)[ \t]?\.'
    r'|(?<![A-Za-z])idiom\b',
    re.I,
)

# Separators that may sit between two labels of the same group (``n./v.``).
POS_JOINER_RE = re.compile(r'^[\s/、,，&]*$')

HAN_RE = re.compile(r'[\u4e00-\u9fff]')
ENGLISH_RUN_RE = re.compile(r'[A-Za-z]{3,}[A-Za-z\s\'\-]*')

# Explanatory lead-ins that turn a gloss into a sentence about the word.
META_LEAD_RE = re.compile(
    r'^[\s:：的]*'
    r'(?:[（(][^）)]*[）)][\s:：]*)?'          # leading usage note: （不可数名词）：
    r'(?:\d+%[^：:，,。]{0,6}[：:，,]?)?'        # 95%情况：
    r'(?:是?[^，,。]{0,10}?(?:形式|词性)[，,])?'  # 的抽象名词形式，
    r'(?:是一个[^，,。]{0,10}[，,]?)?'          # 是一个名词，
    r'(?:有[^，,。]{0,8}含义[，,])?'             # 有多个含义，
    r'(?:可以表示|可以指|可指|亦可指|亦指)?'
    r'(?:指的是|意思是|意为|表示|用于形容|用于指|用于|形容|核心含义是|核心意思是|'
    r'核心意为|核心是|核心在于|本义是|字面意思是|字面意为|'
    r'指(?![挥导定数标示南责令派控甲纹环出向针])'
    r')?[\s:：、]*'
)
NOTE_TAIL_RE = re.compile(r'[（(][^（()）]*[\d%％][^（()）]*[)）]')
BREAK_RE = re.compile(
    r'[，,](?=用来|通常|尤其|常用|常指|常见|一般|多用|强调|核心|它|也可以|还可以|'
    r'在[^，,。]{0,6}中)'
)
WORD_NOTE_RE = re.compile(r'(?:这个词|该词|此词|这词).*$')
FUNCTION_ONLY_RE = re.compile(r'^[是的和或与也就即为把被在]{1,3}$')


def _drop_unbalanced_brackets(text):
    """Remove bracket fragments left behind after cutting example text."""
    openers = {'(': ')', '（': '）', '【': '】', '[': ']', '“': '”'}
    closers = {v: k for k, v in openers.items()}
    stack = []
    drop = set()
    for i, ch in enumerate(text):
        if ch in openers:
            stack.append(i)
        elif ch in closers:
            if stack:
                stack.pop()
            else:
                drop.add(i)
    if stack:
        # An unclosed bracket means its content was truncated: cut it away.
        text = text[:stack[0]]
    return ''.join(c for i, c in enumerate(text) if i not in drop)


def _tidy_gloss(text, limit=40):
    """Turn one raw Chinese fragment into a compact gloss."""
    text = text.strip().strip('|·-—–').replace('“', '').replace('”', '').replace('"', '')
    text = META_LEAD_RE.sub('', text, count=1)
    text = WORD_NOTE_RE.sub('', text)
    text = NOTE_TAIL_RE.sub('', text)
    # Keep only the first sentence: what follows is usage commentary.
    text = re.split(r'[。!！?？]', text)[0]
    text = BREAK_RE.split(text)[0]
    text = _drop_unbalanced_brackets(text).strip()
    if len(text) > 2 and text[0] in '“"\'' and text[-1] in '”"\'':
        text = text[1:-1]
    text = text.strip(' \t，,、；;：:./／-—')
    # Stray ASCII letters at either edge are leftovers of a cut example.
    text = re.sub(r'^[A-Za-z\s]+|[A-Za-z\s]+$', '', text)
    if len(text) > limit:
        cut = max(text.rfind(sep, 0, limit + 1) for sep in ('；', '，', '、', ';'))
        text = text[:cut] if cut > 8 else text[:limit]
    return text.strip(' \t，,、；;：:./／')


def _chinese_fragments(text):
    """Split a line into Chinese fragments, dropping embedded English text."""
    for raw in ENGLISH_RUN_RE.split(text):
        if raw and len(HAN_RE.findall(raw)) >= 1:
            yield raw


def _gloss_from_region(region, limit=40):
    """Find the gloss that belongs to a label, ignoring example sentences."""
    for index, line in enumerate(region.splitlines()):
        line = line.strip()
        if not line:
            continue
        if index and not HAN_RE.match(line[0]):
            # A continuation line that starts in English is an example, not a gloss.
            break
        for fragment in _chinese_fragments(line):
            stripped = fragment.strip()
            # A fully bracketed fragment is the translation of an example.
            if stripped.startswith(('（', '(')) and stripped.endswith(('）', ')')):
                continue
            gloss = _tidy_gloss(fragment, limit)
            if HAN_RE.search(gloss) and not FUNCTION_ONLY_RE.match(gloss):
                return gloss
    return ''


def _label_groups(text):
    """Group adjacent part-of-speech labels found in ``text``."""
    groups = []
    for match in POS_TOKEN_RE.finditer(text):
        if groups and POS_JOINER_RE.match(text[groups[-1][-1].end():match.start()]):
            groups[-1].append(match)
        else:
            groups.append([match])
    return groups


def extract_short_def(defn):
    """Build a compact default definition that keeps its part-of-speech labels."""
    if not defn:
        return ''
    # Ignore examples, notes, and collocations kept for the expanded view.
    body = re.split(r'\[(?:ph|st|syn|mean|def|ex|n|v|adj|adv)\]', defn)[0].strip()
    groups = _label_groups(body)

    segments = []
    seen_labels = set()
    for index, group in enumerate(groups):
        labels = []
        for match in group:
            pos = normalize_pos(match.group(0).replace(' ', '').rstrip('.'))
            if pos not in labels:
                labels.append(pos)
        label = '/'.join(labels)
        if all(pos in seen_labels for pos in labels):
            # A repeated label introduces commentary, not a new sense.
            continue
        stop = groups[index + 1][0].start() if index + 1 < len(groups) else len(body)
        gloss = _gloss_from_region(body[group[-1].end():stop], 40 if not segments else 24)
        if not gloss:
            continue
        seen_labels.update(labels)
        segments.append(f'{label} {gloss}')

    if segments:
        compact = '；'.join(segments)
        if len(compact) > 60 and len(segments) > 1:
            # Keep every sense visible by shortening each gloss instead of one.
            trimmed = []
            for segment in segments:
                label, _, gloss = segment.partition(' ')
                trimmed.append(f'{label} {_tidy_gloss(gloss, 18)}'.strip())
            compact = '；'.join(trimmed)
        return compact[:60]

    # No label produced a gloss: keep the labels and the first Chinese fragment.
    label = '/'.join(dict.fromkeys(
        normalize_pos(m.group(0).replace(' ', '').rstrip('.'))
        for group in groups for m in group
    ))
    gloss = _gloss_from_region(body)
    if gloss:
        return f'{label} {gloss}'.strip()
    return label or _tidy_gloss(body)


def generate_html(grouped, total):
    out_dir = os.path.join(BASE, 'merged-by-discipline')
    os.makedirs(out_dir, exist_ok=True)

    # Build data JS
    data_topics = []
    for topic in TOPIC_ORDER:
        if topic not in grouped:
            continue
        words = []
        for item in grouped[topic]:
            short_def = extract_short_def(item['defn'])
            full_def = item['defn']
            words.append({
                'w': item['word'],
                'd': short_def,
                'f': full_def,
                's': item['sources'],
            })
        weight, tier, note = TOPIC_2026.get(topic, (None, "通用", ""))
        emoji_badge, color, order = TIER_META.get(tier, ("", "#8b93a1", 5))
        data_topics.append({
            'name': topic,
            'emoji': EMOJI.get(topic, '📝'),
            'words': words,
            # 2026 真实考场权重（见 2026听力学科场景占比-2026-09-02.md）
            'w26': weight,
            'tier': tier,
            'tierEmoji': emoji_badge,
            'tierColor': color,
            'tierOrder': order,
            'note': note,
            'n2026': sum(1 for x in words if '2026' in x['s']),
        })

    total_2026 = sum(t['n2026'] for t in data_topics)

    data_js = json.dumps(data_topics, ensure_ascii=False, separators=(',', ':'))

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="theme-color" content="#0f1115">
<title>TOEFL 学科词汇总表 ({total} 词)</title>
<style>
:root {{
  --bg:#0f1115; --card:#1a1d24; --card2:#22262f; --fg:#e6e8eb;
  --muted:#8b93a1; --accent:#4c8dff; --accent2:#2a5fc0; --border:#2a2f3a;
}}
@media(prefers-color-scheme:light){{
  :root{{--bg:#f4f6fa;--card:#fff;--card2:#eef1f6;--fg:#1a1d24;--muted:#5f6672;--accent:#2a5fc0;--accent2:#1c4499;--border:#dde2eb;}}
}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
html,body{{margin:0;padding:0}}
body{{
  background:var(--bg);color:var(--fg);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  min-height:100vh;padding-bottom:env(safe-area-inset-bottom);
}}
header{{
  position:sticky;top:0;z-index:20;background:var(--bg);
  padding:12px 16px 10px;padding-top:max(12px,env(safe-area-inset-top));
  border-bottom:1px solid var(--border);
}}
.top-row{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.title{{font-weight:800;font-size:18px;flex:0 0 auto}}
.search-wrap{{
  flex:1 1 200px;display:flex;align-items:center;
  background:var(--card);border:1px solid var(--border);border-radius:10px;padding:6px 10px;
}}
.search-wrap input{{flex:1;border:0;outline:0;background:transparent;color:var(--fg);font-size:14px}}
.stats{{font-size:12px;color:var(--muted);margin-top:6px}}
.home-btn{{
  flex:0 0 auto;background:var(--card);border:1px solid var(--border);color:var(--accent);
  border-radius:10px;padding:6px 10px;font-size:12px;cursor:pointer;text-decoration:none;font-weight:600;white-space:nowrap;
}}
main{{padding:12px 16px;max-width:800px;margin:0 auto}}

/* Topic nav */
.topic-nav{{
  display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;
}}
.topic-chip{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:5px 10px;font-size:12px;cursor:pointer;color:var(--fg);
  transition:border-color .15s;white-space:nowrap;text-decoration:none;
}}
.topic-chip:hover{{border-color:var(--accent)}}
.topic-chip .cnt{{color:var(--muted);font-size:11px;margin-left:3px}}

/* 2026 权重徽章 */
.w26{{
  display:inline-flex;align-items:center;gap:3px;font-size:10px;font-weight:700;
  border-radius:6px;padding:1px 5px;margin-left:4px;white-space:nowrap;
  border:1px solid currentColor;opacity:.95;
}}
.sec-w26{{font-size:11px;padding:2px 7px}}
.sec-note{{
  font-size:11px;color:var(--muted);line-height:1.5;
  margin:-2px 0 8px;padding:6px 10px;background:var(--card);
  border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:8px;
}}
.sec-note b{{color:var(--fg);font-weight:600}}
.prio-banner{{
  font-size:12px;color:var(--muted);line-height:1.6;
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:10px 12px;margin-bottom:12px;
}}
.prio-banner b{{color:var(--fg)}}
.prio-banner a{{color:var(--accent)}}

/* Section */
.section{{margin-bottom:28px}}
.sec-head{{
  position:sticky;top:55px;z-index:10;background:var(--bg);
  padding:10px 0 6px;display:flex;align-items:center;gap:8px;
  border-bottom:1px solid var(--border);margin-bottom:8px;
}}
.sec-emoji{{font-size:22px}}
.sec-title{{font-weight:700;font-size:16px}}
.sec-cnt{{color:var(--muted);font-size:13px}}
.sec-toggle{{
  margin-left:auto;background:var(--card);border:1px solid var(--border);
  color:var(--muted);border-radius:8px;padding:3px 10px;font-size:12px;cursor:pointer;
}}

/* Word list */
.wlist{{display:flex;flex-direction:column;gap:6px}}
.witem{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:10px 14px;display:flex;align-items:flex-start;gap:10px;
}}
.witem .ww{{
  font-size:16px;font-weight:600;flex:0 0 auto;min-width:100px;
  display:flex;align-items:center;gap:6px;
}}
.witem .wd{{font-size:13px;color:var(--muted);flex:1;line-height:1.5}}
.witem .wsrc{{font-size:10px;color:var(--accent);flex:0 0 auto;opacity:.6}}
.widx{{font-size:11px;color:var(--muted);opacity:.5;margin-right:6px;font-weight:400;font-variant-numeric:tabular-nums}}
.spk-btn{{
  background:none;border:0;padding:0;cursor:pointer;color:var(--accent);
  font-size:14px;display:inline-flex;align-items:center;flex:0 0 auto;
}}
.spk-btn:hover{{opacity:.7}}

/* Expand */
.witem .full{{display:none;font-size:12px;color:var(--muted);margin-top:6px;line-height:1.6;word-break:break-word;white-space:pre-wrap}}
.witem.expanded .full{{display:block}}

/* Search highlight */
.witem mark{{background:rgba(76,141,255,.28);color:inherit;border-radius:3px;padding:0 2px}}

.empty{{text-align:center;color:var(--muted);padding:40px;font-size:14px}}
.foot{{text-align:center;margin:32px 0;color:var(--muted);font-size:12px}}

/* Auto-play bar */
.autobar{{
  position:fixed;bottom:0;left:0;right:0;z-index:30;
  background:var(--card);border-top:1px solid var(--border);
  padding:10px 16px;padding-bottom:max(10px,env(safe-area-inset-bottom));
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;
  box-shadow:0 -2px 12px rgba(0,0,0,.15);
  transition:transform .25s;
}}
.autobar.hidden{{transform:translateY(100%)}}
.autobar .ab-row{{display:flex;align-items:center;gap:8px;width:100%}}
.autobar .ab-word{{
  font-size:18px;font-weight:700;flex:1;min-width:0;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.autobar .ab-def{{
  font-size:12px;color:var(--muted);width:100%;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}}
.autobar .ab-pos{{font-size:12px;color:var(--muted);white-space:nowrap}}
.autobar button{{
  background:var(--card2);border:1px solid var(--border);color:var(--fg);
  border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer;
  white-space:nowrap;
}}
.autobar button:hover{{border-color:var(--accent)}}
.autobar button.primary{{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}}
.autobar select,.autobar input[type=number]{{
  background:var(--card2);border:1px solid var(--border);color:var(--fg);
  border-radius:8px;padding:5px 8px;font-size:12px;
}}
.autobar input[type=number]{{width:60px}}
.ab-toggle{{
  position:fixed;bottom:16px;right:16px;z-index:29;
  background:var(--accent);color:#fff;border:0;border-radius:50%;
  width:48px;height:48px;font-size:22px;cursor:pointer;
  box-shadow:0 2px 12px rgba(76,141,255,.4);
  display:flex;align-items:center;justify-content:center;
  margin-bottom:env(safe-area-inset-bottom);
}}
.ab-toggle:hover{{opacity:.85}}
.witem.playing{{border-color:var(--accent);background:var(--accent2);background:rgba(76,141,255,.08)}}
body.autobar-open{{padding-bottom:100px}}

/* Mark / hard words */
.mark-btn{{
  background:none;border:0;padding:0;cursor:pointer;font-size:14px;
  display:inline-flex;align-items:center;flex:0 0 auto;opacity:.35;
  transition:opacity .15s;
}}
.mark-btn:hover{{opacity:.7}}
.mark-btn.marked{{opacity:1}}
.witem.is-hard{{border-left:3px solid #f5a623}}
.filter-bar{{
  display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap;
}}
.filter-btn{{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:5px 12px;font-size:12px;cursor:pointer;color:var(--fg);
  transition:border-color .15s;
}}
.filter-btn:hover{{border-color:var(--accent)}}
.filter-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.hard-count{{font-size:12px;color:var(--muted)}}

/* Sync modal */
.sync-modal{{
  display:none;position:fixed;inset:0;z-index:50;
  background:rgba(0,0,0,.6);align-items:center;justify-content:center;
  padding:20px;
}}
.sync-modal.open{{display:flex}}
.sync-box{{
  background:var(--card);border:1px solid var(--border);border-radius:16px;
  padding:24px;max-width:440px;width:100%;
}}
.sync-box h3{{margin:0 0 12px;font-size:16px}}
.sync-box input[type=password],.sync-box input[type=text]{{
  width:100%;background:var(--card2);border:1px solid var(--border);
  border-radius:8px;color:var(--fg);font-size:13px;padding:10px;
  font-family:monospace;
}}
.sync-box .sync-btns{{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}}
.sync-box .sync-btns button{{
  background:var(--card2);border:1px solid var(--border);color:var(--fg);
  border-radius:8px;padding:6px 14px;font-size:13px;cursor:pointer;
}}
.sync-box .sync-btns button:hover{{border-color:var(--accent)}}
.sync-box .sync-btns button.primary{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.sync-hint{{font-size:12px;color:var(--muted);margin-top:10px;line-height:1.6}}
.sync-status{{font-size:12px;margin-top:8px;padding:6px 10px;border-radius:6px}}
.sync-status.ok{{background:rgba(52,199,89,.15);color:#34c759}}
.sync-status.err{{background:rgba(255,69,58,.15);color:#ff453a}}
.sync-status.info{{background:rgba(76,141,255,.12);color:var(--accent)}}

/* Focus mode */
.focus-overlay{{
  display:none;position:fixed;inset:0;z-index:25;
  background:var(--bg);
  flex-direction:column;align-items:center;justify-content:center;
  padding:24px;text-align:center;
}}
.focus-overlay.open{{display:flex}}
.focus-word{{font-size:clamp(32px,8vw,56px);font-weight:800;margin-bottom:12px;visibility:hidden}}
.focus-def{{font-size:16px;color:var(--muted);max-width:500px;line-height:1.6;margin-bottom:8px;visibility:hidden}}
.focus-full{{font-size:13px;color:var(--muted);max-width:500px;line-height:1.6;opacity:.7;margin-bottom:20px;word-break:break-word;white-space:pre-wrap;visibility:hidden}}
.focus-overlay.revealed .focus-word,.focus-overlay.revealed .focus-def,.focus-overlay.revealed .focus-full{{visibility:visible}}
.focus-pos{{font-size:13px;color:var(--muted);margin-bottom:20px}}
.focus-btns{{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}}
.focus-btns button{{
  background:var(--card);border:1px solid var(--border);color:var(--fg);
  border-radius:10px;padding:8px 16px;font-size:14px;cursor:pointer;
}}
.focus-btns button:hover{{border-color:var(--accent)}}
.focus-btns button.primary{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.focus-mark{{font-size:28px;cursor:pointer;margin-bottom:16px;opacity:.4;transition:opacity .15s}}
.focus-mark.marked{{opacity:1}}

/* hidden */
.hidden{{display:none!important}}

@media(max-width:600px){{
  .witem .ww{{min-width:80px;font-size:15px}}
  .witem .wd{{font-size:12px}}
}}
</style>
</head>
<body>
<header>
  <div class="top-row">
    <a class="home-btn" href="../">← 首页</a>
    <span class="title">📚 学科词汇总表</span>
    <div class="search-wrap">
      <input id="searchInput" type="text" placeholder="搜索单词或释义..." autocomplete="off">
    </div>
  </div>
  <div class="stats" id="stats">{total} 个词汇 · {len([t for t in TOPIC_ORDER if t in grouped])} 个学科</div>
</header>
<main id="main"></main>
<div class="foot">TOEFL 学科词汇总表 · 三大词表 + 2026新场景词汇 · 按学科分组</div>

<!-- Auto-play bar -->
<button class="ab-toggle" id="abToggle" title="连播模式">▶</button>
<div class="autobar hidden" id="autobar">
  <div class="ab-row">
    <button class="primary" id="abPlayBtn">▶ 连播</button>
    <span class="ab-word" id="abWord">—</span>
    <span class="ab-pos" id="abPos"></span>
  </div>
  <div class="ab-row">
    <div class="ab-def" id="abDef">&nbsp;</div>
  </div>
  <div class="ab-row">
    <label style="font-size:12px;color:var(--muted)">起始:</label>
    <input type="number" id="abStart" min="1" value="1" title="从第几个词开始">
    <label style="font-size:12px;color:var(--muted)">间隔:</label>
    <select id="abGap">
      <option value="0">无间隔</option>
      <option value="1000" selected>1 秒</option>
      <option value="2000">2 秒</option>
      <option value="3000">3 秒</option>
      <option value="5000">5 秒</option>
    </select>
    <button class="filter-btn" id="abHardOnly">⭐ 仅难词</button>
    <button class="filter-btn" id="abFocusBtn">🎯 专注</button>
    <button id="abPrev" title="上一个">⏮</button>
    <button id="abNext" title="下一个">⏭</button>
    <button id="abClose" title="关闭">✕</button>
  </div>
</div>

<!-- Sync modal -->
<div class="sync-modal" id="syncModal" onclick="if(event.target===this)syncClose()">
  <div class="sync-box">
    <h3>☁️ 云同步难词标记</h3>
    <input type="password" id="syncToken" placeholder="粘贴 GitHub Personal Access Token..." autocomplete="off">
    <div id="syncMsg"></div>
    <div class="sync-hint">
      只需一次设置：<a href="https://github.com/settings/tokens/new?scopes=gist&description=TOEFL-vocab-sync" target="_blank" style="color:var(--accent)">👉 点此创建 Token</a>（勾选 gist 权限即可）<br>
      输入后自动创建私密 Gist 保存星标，多设备输入同一 Token 即同步。
    </div>
    <div class="sync-btns">
      <button class="primary" onclick="syncLogin()">🔗 连接</button>
      <button onclick="syncNow()">🔄 立即同步</button>
      <button onclick="syncLogout()">退出登录</button>
      <button onclick="syncClose()">关闭</button>
    </div>
  </div>
</div>

<!-- Focus mode overlay -->
<div class="focus-overlay" id="focusOverlay">
  <div class="focus-topic" id="focusTopic" style="font-size:14px;color:var(--muted);margin-bottom:16px"></div>
  <div class="focus-reveal-area" id="focusRevealArea" style="cursor:pointer;padding:20px;min-height:120px;display:flex;flex-direction:column;align-items:center">
    <div class="focus-hint" id="focusHint" style="font-size:14px;color:var(--muted);opacity:.5">👆 点击此处揭晓答案</div>
    <div class="focus-word" id="focusWord">—</div>
  </div>
  <div class="focus-mark" id="focusMark" title="标记难词">⭐</div>
  <div class="focus-def" id="focusDef"></div>
  <div class="focus-full" id="focusFull"></div>
  <div class="focus-pos" id="focusPos"></div>
  <div class="focus-btns">
    <button onclick="focusPrev()">⏮ 上一个</button>
    <button onclick="focusSpeak()">🔊 发音</button>
    <button class="primary" id="focusPlayBtn" onclick="focusTogglePlay()">▶ 连播</button>
    <button onclick="focusNext()">⏭ 下一个</button>
    <button class="filter-btn" id="focusHardBtn" onclick="focusToggleHard()">⭐ 仅难词</button>
    <button onclick="focusClose()">✕ 退出</button>
  </div>
</div>

<script>
const DATA = {data_js};

const mainEl = document.getElementById('main');
const searchInput = document.getElementById('searchInput');
const statsEl = document.getElementById('stats');

let collapsed = {{}};
let hardWords = new Set();
let showHardOnly = false;
// 2026 视图状态：仅真题词 / 仅高频学科 / 按 2026 优先级排序
let show2026Only = false;
let showHighYieldOnly = false;
let prioSort = false;
const TOTAL_2026 = {total_2026};
const HARD_KEY = 'merged_hard_words';

function loadHard() {{
  try {{ hardWords = new Set(JSON.parse(localStorage.getItem(HARD_KEY) || '[]')); }} catch(e) {{ hardWords = new Set(); }}
}}
function saveHard() {{
  try {{ localStorage.setItem(HARD_KEY, JSON.stringify([...hardWords])); }} catch(e) {{}}
}}
function toggleHard(word, e) {{
  e.stopPropagation();
  if (hardWords.has(word)) hardWords.delete(word); else hardWords.add(word);
  saveHard();
  render(searchInput.value);
}}
loadHard();

// ─── Cloud Sync via GitHub Gist ───
const GIST_KEY = 'merged_gist_sync';
const GIST_DESC = 'TOEFL-vocab-hard-words-sync';
let gistToken = '', gistId = '';

function gistLoadCreds() {{
  try {{
    const s = JSON.parse(localStorage.getItem(GIST_KEY) || '{{}}');
    gistToken = s.token || '';
    gistId = s.gistId || '';
  }} catch(e) {{}}
}}
function gistSaveCreds() {{
  try {{ localStorage.setItem(GIST_KEY, JSON.stringify({{ token: gistToken, gistId }})); }} catch(e) {{}}
}}

function syncMsg(text, cls) {{
  const el = document.getElementById('syncMsg');
  el.className = 'sync-status ' + (cls || 'info');
  el.textContent = text;
}}

function syncOpen() {{
  document.getElementById('syncModal').classList.add('open');
  const inp = document.getElementById('syncToken');
  inp.value = gistToken;
  document.getElementById('syncMsg').textContent = '';
  if (gistToken && gistId) syncMsg('已连接 · Gist ID: ' + gistId.slice(0,8) + '...', 'ok');
}}
function syncClose() {{
  document.getElementById('syncModal').classList.remove('open');
}}

async function gistFetch(url, opts) {{
  const res = await fetch(url, {{
    ...opts,
    headers: {{ 'Authorization': 'token ' + gistToken, 'Accept': 'application/vnd.github.v3+json', ...(opts?.headers || {{}}) }},
  }});
  if (!res.ok) throw new Error(res.status + ' ' + (await res.text()).slice(0,100));
  return res.json();
}}

async function gistFindExisting() {{
  const gists = await gistFetch('https://api.github.com/gists?per_page=100');
  return gists.find(g => g.description === GIST_DESC);
}}

async function gistCreate() {{
  return gistFetch('https://api.github.com/gists', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{
      description: GIST_DESC,
      public: false,
      files: {{ 'hard-words.json': {{ content: JSON.stringify([...hardWords]) }} }}
    }})
  }});
}}

async function gistPush() {{
  if (!gistToken || !gistId) return;
  try {{
    await gistFetch('https://api.github.com/gists/' + gistId, {{
      method: 'PATCH',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ files: {{ 'hard-words.json': {{ content: JSON.stringify([...hardWords]) }} }} }})
    }});
  }} catch(e) {{ console.warn('Gist push failed:', e); }}
}}

async function gistPull() {{
  if (!gistToken || !gistId) return;
  try {{
    const g = await gistFetch('https://api.github.com/gists/' + gistId);
    const content = g.files['hard-words.json']?.content;
    if (content) {{
      const arr = JSON.parse(content);
      if (Array.isArray(arr)) {{
        arr.forEach(w => {{ if (typeof w === 'string') hardWords.add(w); }});
        saveHard();
      }}
    }}
  }} catch(e) {{ console.warn('Gist pull failed:', e); }}
}}

async function syncLogin() {{
  const inp = document.getElementById('syncToken');
  const token = inp.value.trim();
  if (!token) {{ syncMsg('请先粘贴 Token', 'err'); return; }}
  gistToken = token;
  syncMsg('连接中...', 'info');
  try {{
    // Verify token
    await gistFetch('https://api.github.com/user');
    // Find existing Gist
    const existing = await gistFindExisting();
    if (existing) {{
      gistId = existing.id;
      gistSaveCreds();
      syncMsg('已找到已有同步 Gist，正在拉取...', 'info');
      await gistPull();
      render(searchInput.value);
      syncMsg('✅ 同步成功！已合并 ' + hardWords.size + ' 个难词', 'ok');
    }} else {{
      syncMsg('创建同步 Gist...', 'info');
      const g = await gistCreate();
      gistId = g.id;
      gistSaveCreds();
      syncMsg('✅ 已连接！' + hardWords.size + ' 个难词已上传', 'ok');
    }}
  }} catch(e) {{
    gistToken = ''; gistId = '';
    syncMsg('❌ 连接失败: ' + e.message, 'err');
  }}
}}

async function syncNow() {{
  if (!gistToken || !gistId) {{ syncMsg('请先连接', 'err'); return; }}
  syncMsg('同步中...', 'info');
  try {{
    await gistPull();
    await gistPush();
    render(searchInput.value);
    syncMsg('✅ 同步完成！共 ' + hardWords.size + ' 个难词', 'ok');
  }} catch(e) {{
    syncMsg('❌ 同步失败: ' + e.message, 'err');
  }}
}}

function syncLogout() {{
  gistToken = ''; gistId = '';
  localStorage.removeItem(GIST_KEY);
  document.getElementById('syncToken').value = '';
  syncMsg('已退出', 'info');
}}

// Auto-push on hard word changes
const _origSaveHard = saveHard;
saveHard = function() {{
  _origSaveHard();
  if (gistToken && gistId) {{
    clearTimeout(saveHard._t);
    saveHard._t = setTimeout(gistPush, 2000);
  }}
}};

// Auto-pull on page load
gistLoadCreds();
if (gistToken && gistId) {{
  gistPull().then(() => render(searchInput.value)).catch(() => {{}});
}}

let audioEl = null;
let audioRequestId = 0;
const ttsPreferred = new Map();   // word -> url that actually played
function ttsUrls(word) {{
  const cached = ttsPreferred.get(word);
  const w = encodeURIComponent(word);
  const youdaoUs = "https://dict.youdao.com/dictvoice?audio=" + w + "&type=2";
  const youdaoUk = "https://dict.youdao.com/dictvoice?audio=" + w + "&type=1";
  const google = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q=" + w;
  // Keep one voice for everything that Youdao can pronounce, then fall back:
  // Youdao returns an error for ~50 multi-word terms, which Google can read.
  const chain = [youdaoUs, youdaoUk, google];
  if (cached) return [cached].concat(chain.filter(u => u !== cached));
  return chain;
}}
function pickVoice() {{
  if (!window.speechSynthesis) return null;
  const voices = speechSynthesis.getVoices().filter(v => /^en/i.test(v.lang));
  const liked = ['Samantha', 'Ava', 'Allison', 'Karen', 'Serena', 'Google US English',
                 'Microsoft Aria', 'Microsoft Jenny', 'Microsoft Guy', 'Alex', 'Daniel'];
  for (const name of liked) {{
    const hit = voices.find(v => v.name.indexOf(name) !== -1);
    if (hit) return hit;
  }}
  return voices.find(v => /en[-_]US/i.test(v.lang)) || voices[0] || null;
}}
function synthSpeak(word, requestId, done) {{
  // Last resort: the local system voice, so no word is ever silent.
  if (!window.speechSynthesis) {{ done(); return; }}
  try {{
    const utter = new SpeechSynthesisUtterance(word);
    utter.lang = 'en-US';
    utter.rate = 0.95;
    const voice = pickVoice();
    if (voice) utter.voice = voice;
    utter.onend = () => {{ if (requestId === audioRequestId) done(); }};
    utter.onerror = () => {{ if (requestId === audioRequestId) done(); }};
    speechSynthesis.cancel();
    speechSynthesis.speak(utter);
  }} catch (e) {{ done(); }}
}}
function playChain(word, requestId, done) {{
  const urls = ttsUrls(word);
  let index = 0;
  const next = () => {{
    if (requestId !== audioRequestId) return;
    if (index >= urls.length) {{
      audioEl = null;
      synthSpeak(word, requestId, done);
      return;
    }}
    const url = urls[index++];
    const audio = new Audio(url);
    audioEl = audio;
    audio.onerror = next;
    audio.onended = () => {{
      if (requestId !== audioRequestId) return;
      audioEl = null;
      done();
    }};
    audio.onplaying = () => {{ ttsPreferred.set(word, url); }};
    audio.play().catch(next);
  }};
  next();
}}
function stopAudio() {{
  audioRequestId++;
  if (window.speechSynthesis) {{ try {{ speechSynthesis.cancel(); }} catch(e) {{}} }}
  if (audioEl) {{
    audioEl.onerror = null; audioEl.onended = null; audioEl.onplaying = null;
    try {{ audioEl.pause(); audioEl.currentTime = 0; }} catch(e) {{}}
    audioEl = null;
  }}
}}
function speak(word) {{
  const clean = word.replace(/['’]/g, "'");
  stopAudio();
  if (!clean) return;
  playChain(clean, audioRequestId, () => {{}});
}}

function escHtml(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function highlight(text, q) {{
  if (!q) return escHtml(text);
  const esc = q.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
  return escHtml(text).replace(new RegExp('(' + esc + ')', 'gi'), '<mark>$1</mark>');
}}

function render(query) {{
  const q = (query || '').trim().toLowerCase();
  let html = '';
  let totalShown = 0;
  const hardCnt = hardWords.size;

  // 词条级筛选：搜索 → 难词 → 2026 真题词
  const wordFilter = (ws) => {{
    let r = ws;
    if (q) r = r.filter(w => w.w.includes(q) || w.d.includes(q) || w.f.toLowerCase().includes(q));
    if (showHardOnly) r = r.filter(w => hardWords.has(w.w));
    if (show2026Only) r = r.filter(w => w.s.indexOf('2026') >= 0);
    return r;
  }};
  // 学科级筛选：只看 2026 讲座高频（含全学科通用词）
  const topicPass = (t) => !showHighYieldOnly || t.tier === '讲座高频' || t.tier === '全学科通用';

  // 视图顺序：DATA 本身不动（连播索引依赖它），只在展示层排序
  let view = DATA.map((t, i) => ({{ t, i }}));
  if (prioSort) {{
    view.sort((a, b) =>
      (a.t.tierOrder - b.t.tierOrder) ||
      ((b.t.w26 || 0) - (a.t.w26 || 0)) ||
      (a.i - b.i));
  }}

  // Filter bar
  html += '<div class="filter-bar">';
  html += `<button class="filter-btn${{showHardOnly ? ' active' : ''}}" onclick="showHardOnly=!showHardOnly;render(searchInput.value)">⭐ 仅看难词</button>`;
  html += `<button class="filter-btn${{show2026Only ? ' active' : ''}}" onclick="show2026Only=!show2026Only;render(searchInput.value)">🆕 仅 2026 真题词</button>`;
  html += `<button class="filter-btn${{showHighYieldOnly ? ' active' : ''}}" onclick="showHighYieldOnly=!showHighYieldOnly;render(searchInput.value)">🔥 仅 2026 高频学科</button>`;
  html += `<button class="filter-btn${{prioSort ? ' active' : ''}}" onclick="prioSort=!prioSort;render(searchInput.value)">${{prioSort ? '↕️ 按 2026 优先级' : '↕️ 按原学科顺序'}}</button>`;
  html += `<span class="hard-count">已标记 ${{hardCnt}} 个难词</span>`;
  html += `<button class="filter-btn" onclick="syncOpen()">☁️ 云同步</button>`;
  if (hardCnt > 0) {{
    html += `<button class="filter-btn" onclick="if(confirm('确定清空所有难词标记？')){{hardWords.clear();saveHard();showHardOnly=false;render(searchInput.value)}}">清空标记</button>`;
  }}
  html += '</div>';

  // 2026 权重说明
  if (!q) {{
    html += `<div class="prio-banner">🔥 <b>徽章＝2026 真实考场权重</b>：数字是该学科在 2026 改版后 237 条去重讲座话题（29 个考试日）里的占比。`
      + `<b>艺术 23.2%</b> 居首，<b>经济商业 10.1%</b>（旧格式仅 3.0%），而<b>天文只剩 1.7%</b>（旧格式 11.1%）。`
      + `🎓 对话·公告类不参与讲座统计，但自适应低分支<b>只有</b>对话和公告，属全员必备。`
      + `🆕 标签 = 从 2026 真题话题反推出来的新增术语（本表 ${{TOTAL_2026}} 词）。`
      + `口径与样本局限见仓库内 <code>2026听力学科场景占比-2026-09-02.md</code>。</div>`;
  }}

  // Topic nav
  html += '<div class="topic-nav">';
  view.forEach(({{ t, i }}) => {{
    if (!topicPass(t)) return;
    const filtered = wordFilter(t.words);
    if (filtered.length > 0) {{
      const badge = t.w26 != null
        ? `<span class="w26" style="color:${{t.tierColor}}">${{t.tierEmoji}}${{t.w26}}%</span>`
        : (t.tierEmoji ? `<span class="w26" style="color:${{t.tierColor}}">${{t.tierEmoji}}</span>` : '');
      html += `<a class="topic-chip" href="#sec${{i}}">${{t.emoji}} ${{t.name.split(' ')[0]}}<span class="cnt">${{filtered.length}}</span>${{badge}}</a>`;
    }}
  }});
  html += '</div>';

  view.forEach(({{ t, i: ti }}) => {{
    if (!topicPass(t)) return;
    const items = wordFilter(t.words);
    if (items.length === 0) return;
    totalShown += items.length;

    const isCollapsed = collapsed[ti] && !q;
    const secBadge = t.w26 != null
      ? `<span class="w26 sec-w26" style="color:${{t.tierColor}}">${{t.tierEmoji}} 2026 讲座 ${{t.w26}}%</span>`
      : `<span class="w26 sec-w26" style="color:${{t.tierColor}}">${{t.tierEmoji}} ${{t.tier}}</span>`;
    html += `<div class="section" id="sec${{ti}}">`;
    html += `<div class="sec-head">`;
    html += `<span class="sec-emoji">${{t.emoji}}</span>`;
    html += `<span class="sec-title">${{escHtml(t.name)}}</span>`;
    html += secBadge;
    html += `<span class="sec-cnt">${{items.length}} 词</span>`;
    html += `<button class="sec-toggle" onclick="toggleSec(${{ti}})">${{isCollapsed ? '展开' : '折叠'}}</button>`;
    html += `</div>`;
    if (t.note && t.tier !== '通用') {{
      const newTag = t.n2026 > 0 ? ` · 本组含 <b>${{t.n2026}}</b> 个 2026 真题词` : '';
      html += `<div class="sec-note"><b>${{t.tier}}</b>｜${{escHtml(t.note)}}${{newTag}}</div>`;
    }}

    if (!isCollapsed) {{
      html += '<div class="wlist">';
      items.forEach(w => {{
        const srcBadge = w.s.join('+');
        const isHard = hardWords.has(w.w);
        const gIdx = WORD_IDX[w.w];
        const is2026 = w.s.indexOf('2026') >= 0;
        html += `<div class="witem${{isHard ? ' is-hard' : ''}}" onclick="this.classList.toggle('expanded')">`;
        html += `<div class="ww"><span class="widx">${{gIdx + 1}}</span>${{highlight(w.w, q)}}${{is2026 ? '<span class="w26" style="color:#ff6b4a" title="2026 真实考场讲座话题反推出的术语">🆕</span>' : ''}}<button class="spk-btn" onclick="event.stopPropagation();speak('${{w.w}}')" title="发音">🔊</button><button class="mark-btn${{isHard ? ' marked' : ''}}" onclick="toggleHard('${{w.w}}',event)" title="${{isHard ? '取消标记' : '标记为难词'}}">⭐</button></div>`;
        html += `<div class="wd">${{highlight(w.d, q)}}</div>`;
        html += `<div class="wsrc">${{srcBadge}}</div>`;
        if (w.f) {{
          html += `<div class="full">${{highlight(w.f, q)}}</div>`;
        }}
        html += '</div>';
      }});
      html += '</div>';
    }}
    html += '</div>';
  }});

  if (totalShown === 0) {{
    html += `<div class="empty">${{showHardOnly ? '还没有标记难词，点击单词旁 ⭐ 标记' : (show2026Only || showHighYieldOnly ? '当前筛选下没有词汇，试着关掉 🆕 / 🔥 筛选' : '未找到匹配的单词')}}</div>`;
  }}

  mainEl.innerHTML = html;
  statsEl.textContent = q
    ? `找到 ${{totalShown}} 个词汇`
    : showHardOnly
      ? `⭐ ${{totalShown}} 个难词`
      : show2026Only || showHighYieldOnly
        ? `当前筛选 ${{totalShown}} 个词汇`
        : `{total} 个词汇 · {len([t for t in TOPIC_ORDER if t in grouped])} 个学科 · 🆕 {total_2026} 个 2026 真题词`;
}}

function toggleSec(idx) {{
  collapsed[idx] = !collapsed[idx];
  render(searchInput.value);
}}

let debounceTimer;
searchInput.addEventListener('input', () => {{
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => render(searchInput.value), 200);
}});

// ─── Build indexes ───
const ALL_WORDS = [];
const WORD_TOPIC = {{}};
const WORD_IDX = {{}};
DATA.forEach(t => t.words.forEach(w => {{
  WORD_IDX[w.w] = ALL_WORDS.length;
  ALL_WORDS.push(w);
  WORD_TOPIC[w.w] = t.emoji + ' ' + t.name.split(' ')[0];
}}));

render('');

// ─── Auto-play ───

let abPlaying = false, abIdx = 0, abToken = 0, abHardOnly = false;
function abGetList() {{ return abHardOnly ? ALL_WORDS.filter(w => hardWords.has(w.w)) : ALL_WORDS; }}
let abWake = null, abTimer = null;
const abBar = document.getElementById('autobar');
const abToggleBtn = document.getElementById('abToggle');
const abPlayBtn = document.getElementById('abPlayBtn');
const abWordEl = document.getElementById('abWord');
const abPosEl = document.getElementById('abPos');
const abDefEl = document.getElementById('abDef');
const abStartInput = document.getElementById('abStart');
const abGapSel = document.getElementById('abGap');

// Load saved position
const AB_KEY = 'merged_autoplay';
function abLoad() {{
  try {{
    const s = JSON.parse(localStorage.getItem(AB_KEY) || '{{}}');
    if (s.idx >= 0 && s.idx < ALL_WORDS.length) abIdx = s.idx;
    if (s.gap) abGapSel.value = String(s.gap);
  }} catch(e) {{}}
}}
function abSave() {{
  try {{
    localStorage.setItem(AB_KEY, JSON.stringify({{ idx: abIdx, gap: parseInt(abGapSel.value) }}));
  }} catch(e) {{}}
}}

function speakAsync(word) {{
  return new Promise(resolve => {{
    const clean = word.replace(/['’]/g, "'");
    if (!clean) {{ resolve(); return; }}
    stopAudio();
    playChain(clean, audioRequestId, resolve);
  }});
}}

function sleepCancelable(ms) {{
  return new Promise(resolve => {{
    abWake = resolve;
    abTimer = setTimeout(resolve, ms);
  }});
}}

function abUpdateUI() {{
  const list = abGetList();
  const w = list[abIdx];
  abPlayBtn.textContent = abPlaying ? '⏸ 暂停' : '▶ 连播';
  abToggleBtn.textContent = abPlaying ? '⏸' : '▶';
  abWordEl.textContent = w ? w.w : '—';
  abDefEl.textContent = w ? (w.d || w.f || '') : '';
  abPosEl.textContent = list.length ? (abIdx + 1) + '/' + list.length : '0/0';
  abStartInput.value = list.length ? abIdx + 1 : 0;
  document.getElementById('abHardOnly').classList.toggle('active', abHardOnly);

  // Highlight current word in list
  document.querySelectorAll('.witem.playing').forEach(el => el.classList.remove('playing'));
  if (w) {{
    const items = document.querySelectorAll('.witem');
    items.forEach(el => {{
      const ww = el.querySelector('.ww');
      if (ww && ww.textContent.replace(/🔊|⭐/g,'').trim() === w.w) {{
        el.classList.add('playing');
      }}
    }});
  }}
}}

async function abLoop() {{
  const token = ++abToken;
  while (abPlaying && token === abToken) {{
    const list = abGetList();
    if (!list.length) {{ abStop(); return; }}
    if (abIdx >= list.length) {{
      abIdx = 0; abSave(); abStop();
      return;
    }}
    abUpdateUI();
    const playing = document.querySelector('.witem.playing');
    if (playing) playing.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

    await speakAsync(list[abIdx].w);
    if (!abPlaying || token !== abToken) return;

    const gap = parseInt(abGapSel.value, 10) || 0;
    if (gap) {{
      await sleepCancelable(gap);
      if (!abPlaying || token !== abToken) return;
    }}

    abIdx++; abSave(); abUpdateUI();
    if (abIdx >= abGetList().length) continue;
  }}
}}

function abStart() {{
  if (abPlaying) return;
  const list = abGetList();
  if (!list.length) {{ return; }}
  if (abIdx >= list.length) abIdx = 0;
  abPlaying = true;
  abUpdateUI();
  abLoop();
}}

function abStop() {{
  abPlaying = false;
  abToken++;
  if (abTimer) {{ clearTimeout(abTimer); abTimer = null; }}
  if (abWake) {{ const w = abWake; abWake = null; w(); }}
  if (audioEl) {{ try {{ audioEl.pause(); }} catch(e) {{}} audioEl.onended = null; audioEl.onerror = null; }}
  abUpdateUI();
}}

// Toggle bar visibility
abToggleBtn.onclick = () => {{
  const show = abBar.classList.contains('hidden');
  abBar.classList.toggle('hidden', !show);
  document.body.classList.toggle('autobar-open', show);
  abToggleBtn.style.display = show ? 'none' : '';
  if (show) abUpdateUI();
}};

abPlayBtn.onclick = () => {{ abPlaying ? abStop() : abStart(); }};

document.getElementById('abClose').onclick = () => {{
  abStop();
  abBar.classList.add('hidden');
  document.body.classList.remove('autobar-open');
  abToggleBtn.style.display = '';
}};

document.getElementById('abPrev').onclick = () => {{
  if (abIdx > 0) {{ abIdx--; abSave(); }}
  if (abPlaying) {{ abStop(); abStart(); }}
  else abUpdateUI();
}};

document.getElementById('abNext').onclick = () => {{
  const list = abGetList();
  if (abIdx < list.length - 1) {{ abIdx++; abSave(); }}
  if (abPlaying) {{ abStop(); abStart(); }}
  else abUpdateUI();
}};

abStartInput.onchange = () => {{
  const list = abGetList();
  const v = parseInt(abStartInput.value, 10);
  if (v >= 1 && v <= list.length) {{
    abIdx = v - 1; abSave();
    if (abPlaying) {{ abStop(); abStart(); }}
    else abUpdateUI();
  }}
}};

abGapSel.onchange = () => {{ abSave(); }};

document.getElementById('abHardOnly').onclick = () => {{
  abHardOnly = !abHardOnly;
  abIdx = 0; abSave();
  if (abPlaying) {{ abStop(); abStart(); }}
  else abUpdateUI();
}};

// Click a word's speaker button to set autoplay position
mainEl.addEventListener('click', (e) => {{
  const btn = e.target.closest('.spk-btn');
  if (!btn) return;
  const word = btn.getAttribute('onclick')?.match(/speak\\('([^']+)'\\)/)?.[1];
  if (!word) return;
  const list = abGetList();
  const idx = list.findIndex(w => w.w === word);
  if (idx >= 0) {{
    abIdx = idx; abSave(); abUpdateUI();
  }}
}});

abLoad();
abUpdateUI();

// ─── Focus mode ───
let focusOpen = false;
const focusOverlay = document.getElementById('focusOverlay');
const focusWordEl = document.getElementById('focusWord');
const focusDefEl = document.getElementById('focusDef');
const focusFullEl = document.getElementById('focusFull');
const focusPosEl = document.getElementById('focusPos');
const focusMarkEl = document.getElementById('focusMark');
const focusPlayBtn = document.getElementById('focusPlayBtn');

function focusUpdateUI(keepRevealed) {{
  const list = abGetList();
  const w = list[abIdx];
  focusWordEl.textContent = w ? w.w : '—';
  focusDefEl.textContent = w ? (w.d || '') : '';
  focusFullEl.textContent = w ? (w.f && w.f !== w.d ? w.f : '') : '';
  focusPosEl.textContent = list.length ? (abIdx + 1) + ' / ' + list.length : '';
  document.getElementById('focusTopic').textContent = w ? (WORD_TOPIC[w.w] || '') : '';
  focusMarkEl.classList.toggle('marked', w ? hardWords.has(w.w) : false);
  focusPlayBtn.textContent = abPlaying ? '⏸ 暂停' : '▶ 连播';
  document.getElementById('focusHardBtn').classList.toggle('active', abHardOnly);
  if (!keepRevealed) {{
    focusOverlay.classList.remove('revealed');
    document.getElementById('focusHint').style.display = '';
  }}
}}

function focusEnter() {{
  focusOpen = true;
  focusOverlay.classList.add('open');
  document.querySelector('header').style.display = 'none';
  mainEl.style.display = 'none';
  document.querySelector('.foot').style.display = 'none';
  abBar.style.display = 'none';
  abToggleBtn.style.display = 'none';
  focusUpdateUI();
}}

function focusClose() {{
  focusOpen = false;
  focusOverlay.classList.remove('open');
  document.querySelector('header').style.display = '';
  mainEl.style.display = '';
  document.querySelector('.foot').style.display = '';
  abBar.style.display = '';
  abBar.classList.remove('hidden');
  document.body.classList.add('autobar-open');
  abUpdateUI();
}}

function focusSpeak() {{
  const list = abGetList();
  const w = list[abIdx];
  if (w) speak(w.w);
}}

function focusPrev() {{
  if (abIdx > 0) {{ abIdx--; abSave(); }}
  if (abPlaying) {{ abStop(); abStart(); }}
  focusUpdateUI();
}}

function focusNext() {{
  const list = abGetList();
  if (abIdx < list.length - 1) {{ abIdx++; abSave(); }}
  if (abPlaying) {{ abStop(); abStart(); }}
  focusUpdateUI();
}}

function focusTogglePlay() {{
  abPlaying ? abStop() : abStart();
  focusUpdateUI();
}}

focusMarkEl.onclick = () => {{
  const list = abGetList();
  const w = list[abIdx];
  if (w) {{
    if (hardWords.has(w.w)) hardWords.delete(w.w); else hardWords.add(w.w);
    saveHard();
    focusUpdateUI();
  }}
}};

document.getElementById('abFocusBtn').onclick = () => {{ focusEnter(); }};

// Reveal only on a genuine click. A drag is reserved for selecting/copying text.
const focusRevealArea = document.getElementById('focusRevealArea');
let focusPointerDown = null;
focusRevealArea.addEventListener('pointerdown', (e) => {{
  focusPointerDown = {{ x: e.clientX, y: e.clientY }};
}});
focusRevealArea.addEventListener('click', (e) => {{
  const selection = window.getSelection();
  const moved = focusPointerDown && Math.hypot(e.clientX - focusPointerDown.x, e.clientY - focusPointerDown.y) > 6;
  focusPointerDown = null;
  if (moved || (selection && !selection.isCollapsed)) return;
  const revealed = focusOverlay.classList.toggle('revealed');
  document.getElementById('focusHint').style.display = revealed ? 'none' : '';
}});

function focusToggleHard() {{
  abHardOnly = !abHardOnly;
  abIdx = 0; abSave();
  document.getElementById('focusHardBtn').classList.toggle('active', abHardOnly);
  document.getElementById('abHardOnly').classList.toggle('active', abHardOnly);
  if (abPlaying) {{ abStop(); abStart(); }}
  focusUpdateUI();
}}

// Update focus UI when autoplay advances
const _origAbUpdateUI = abUpdateUI;
abUpdateUI = function() {{
  _origAbUpdateUI();
  if (focusOpen) focusUpdateUI();
}};

// Keyboard shortcuts in focus mode
document.addEventListener('keydown', (e) => {{
  if (!focusOpen) return;
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{ e.preventDefault(); focusPrev(); }}
  else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {{ e.preventDefault(); focusNext(); }}
  else if (e.key === ' ') {{ e.preventDefault(); focusTogglePlay(); }}
  else if (e.key === 's' || e.key === 'S') {{ e.preventDefault(); focusSpeak(); }}
  else if (e.key === 'Enter' || e.key === 'r' || e.key === 'R') {{
    e.preventDefault();
    const revealed = focusOverlay.classList.toggle('revealed');
    document.getElementById('focusHint').style.display = revealed ? 'none' : '';
  }}
  else if (e.key === 'Escape') {{ focusClose(); }}
}});
</script>
</body>
</html>'''

    out_path = os.path.join(out_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == '__main__':
    main()
