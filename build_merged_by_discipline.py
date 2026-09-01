# -*- coding: utf-8 -*-
"""Merge 1791 + 1925 + 1675 word lists → single HTML grouped by discipline.

Usage:  python build_merged_by_discipline.py
Output: merged-by-discipline/index.html
"""
import os, re, json
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

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
        "decibel", "smog", "emission",
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
    return word.lower(), defn


def parse_1791():
    """Parse simple word list."""
    words = {}
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


def classify_word(word, defn, known_topics):
    """Classify a word into a discipline."""
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

    print(f"  1791: {len(w1791)} words")
    print(f"  1925: {len(w1925)} words")
    print(f"  1675: {len(w1675)} words")

    # Merge: collect all words
    all_words = set()
    all_words.update(w1791.keys())
    all_words.update(w1925.keys())
    all_words.update(w1675.keys())
    print(f"  Merged (unique): {len(all_words)} words")

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
        defn = merge_definitions(defs)
        topic = classify_word(w, defn, topics_1675)
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


def extract_short_def(defn):
    """Extract a short Chinese definition from a full definition string."""
    if not defn:
        return ''
    # Take first meaningful segment (before [ph], [st], [syn], [mean])
    d = re.split(r'\[(?:ph|st|syn|mean)\]', defn)[0].strip()
    # Remove leading "n./v./adj./adv." etc
    d = re.sub(r'^[nvadc]+[\./]\s*', '', d, flags=re.I)
    # Take just the Chinese part if mixed
    parts = re.findall(r'[\u4e00-\u9fff\uff0c\u3001\uff1b\uff08\uff09（）；，、]+', d)
    if parts:
        result = ''.join(parts)[:30]
        return result
    # Fallback: first 40 chars
    return d[:40] if d else ''


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
        data_topics.append({
            'name': topic,
            'emoji': EMOJI.get(topic, '📝'),
            'words': words,
        })

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
  padding:24px;max-width:420px;width:100%;
}}
.sync-box h3{{margin:0 0 12px;font-size:16px}}
.sync-box textarea{{
  width:100%;height:120px;background:var(--card2);border:1px solid var(--border);
  border-radius:8px;color:var(--fg);font-size:12px;padding:10px;resize:vertical;
  font-family:monospace;
}}
.sync-box .sync-btns{{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}}
.sync-box .sync-btns button{{
  background:var(--card2);border:1px solid var(--border);color:var(--fg);
  border-radius:8px;padding:6px 14px;font-size:13px;cursor:pointer;
}}
.sync-box .sync-btns button:hover{{border-color:var(--accent)}}
.sync-box .sync-btns button.primary{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.sync-hint{{font-size:12px;color:var(--muted);margin-top:8px;line-height:1.5}}

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
<div class="foot">TOEFL 学科词汇总表 · 1791 + 1925 + 1675 合并 · 按学科分组</div>

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
    <h3 id="syncTitle">📲 同步难词标记</h3>
    <textarea id="syncText" placeholder="粘贴从另一台设备导出的内容..."></textarea>
    <div class="sync-hint">在 PC 上导出 → 复制内容 → 手机上粘贴导入，即可跨设备同步。</div>
    <div class="sync-btns">
      <button class="primary" onclick="syncExport()">📋 导出并复制</button>
      <button class="primary" onclick="syncImport()">📥 导入</button>
      <button onclick="syncClose()">关闭</button>
    </div>
  </div>
</div>

<!-- Focus mode overlay -->
<div class="focus-overlay" id="focusOverlay">
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

// ─── Sync ───
function syncOpen() {{
  const modal = document.getElementById('syncModal');
  const ta = document.getElementById('syncText');
  ta.value = hardWords.size ? JSON.stringify([...hardWords]) : '';
  modal.classList.add('open');
}}
function syncClose() {{
  document.getElementById('syncModal').classList.remove('open');
}}
function syncExport() {{
  const ta = document.getElementById('syncText');
  const data = JSON.stringify([...hardWords]);
  ta.value = data;
  ta.select();
  try {{
    navigator.clipboard.writeText(data).then(() => {{
      alert('已复制 ' + hardWords.size + ' 个难词到剪贴板！\\n在另一台设备上打开此页面 → 点📲同步 → 粘贴导入');
    }}).catch(() => {{
      document.execCommand('copy');
      alert('已复制！请在另一台设备粘贴导入。');
    }});
  }} catch(e) {{
    document.execCommand('copy');
    alert('已选中，请手动复制 (Ctrl+C)');
  }}
}}
function syncImport() {{
  const ta = document.getElementById('syncText');
  const text = ta.value.trim();
  if (!text) {{ alert('请先粘贴内容'); return; }}
  try {{
    const arr = JSON.parse(text);
    if (!Array.isArray(arr)) throw new Error('格式错误');
    const before = hardWords.size;
    arr.forEach(w => {{ if (typeof w === 'string') hardWords.add(w); }});
    saveHard();
    syncClose();
    render(searchInput.value);
    alert('导入成功！新增 ' + (hardWords.size - before) + ' 个难词，当前共 ' + hardWords.size + ' 个');
  }} catch(e) {{
    alert('格式错误，请粘贴从另一台设备导出的内容');
  }}
}}

let audioEl = null;
function ttsUrls(word) {{
  const w = encodeURIComponent(word);
  return [
    "https://dict.youdao.com/dictvoice?audio=" + w + "&type=2",
    "https://dict.youdao.com/dictvoice?audio=" + w + "&type=1",
    "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=" + w,
  ];
}}
function speak(word) {{
  const clean = word.replace(/['']/g, "'");
  if (audioEl) {{ audioEl.onerror = null; audioEl.onended = null; try {{ audioEl.pause(); }} catch(e) {{}} }}
  const urls = ttsUrls(clean);
  let idx = 0;
  function tryNext() {{
    if (idx >= urls.length) return;
    audioEl = new Audio();
    audioEl.onerror = () => {{ idx++; tryNext(); }};
    audioEl.src = urls[idx];
    audioEl.play().catch(() => {{ idx++; tryNext(); }});
  }}
  tryNext();
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

  // Filter bar
  html += '<div class="filter-bar">';
  html += `<button class="filter-btn${{showHardOnly ? ' active' : ''}}" onclick="showHardOnly=!showHardOnly;render(searchInput.value)">⭐ 仅看难词</button>`;
  html += `<span class="hard-count">已标记 ${{hardCnt}} 个难词</span>`;
  html += `<button class="filter-btn" onclick="syncOpen()">📲 同步</button>`;
  if (hardCnt > 0) {{
    html += `<button class="filter-btn" onclick="if(confirm('确定清空所有难词标记？')){{hardWords.clear();saveHard();showHardOnly=false;render(searchInput.value)}}">清空标记</button>`;
  }}
  html += '</div>';

  // Topic nav
  html += '<div class="topic-nav">';
  DATA.forEach((t, i) => {{
    let filtered = t.words;
    if (q) filtered = filtered.filter(w => w.w.includes(q) || w.d.includes(q) || w.f.toLowerCase().includes(q));
    if (showHardOnly) filtered = filtered.filter(w => hardWords.has(w.w));
    if (filtered.length > 0) {{
      html += `<a class="topic-chip" href="#sec${{i}}">${{t.emoji}} ${{t.name.split(' ')[0]}}<span class="cnt">${{filtered.length}}</span></a>`;
    }}
  }});
  html += '</div>';

  DATA.forEach((t, ti) => {{
    let items = t.words;
    if (q) items = items.filter(w => w.w.includes(q) || w.d.includes(q) || w.f.toLowerCase().includes(q));
    if (showHardOnly) items = items.filter(w => hardWords.has(w.w));
    if (items.length === 0) return;
    totalShown += items.length;

    const isCollapsed = collapsed[ti] && !q;
    html += `<div class="section" id="sec${{ti}}">`;
    html += `<div class="sec-head">`;
    html += `<span class="sec-emoji">${{t.emoji}}</span>`;
    html += `<span class="sec-title">${{escHtml(t.name)}}</span>`;
    html += `<span class="sec-cnt">${{items.length}} 词</span>`;
    html += `<button class="sec-toggle" onclick="toggleSec(${{ti}})">${{isCollapsed ? '展开' : '折叠'}}</button>`;
    html += `</div>`;

    if (!isCollapsed) {{
      html += '<div class="wlist">';
      items.forEach(w => {{
        const srcBadge = w.s.join('+');
        const isHard = hardWords.has(w.w);
        html += `<div class="witem${{isHard ? ' is-hard' : ''}}" onclick="this.classList.toggle('expanded')">`;
        html += `<div class="ww">${{highlight(w.w, q)}}<button class="spk-btn" onclick="event.stopPropagation();speak('${{w.w}}')" title="发音">🔊</button><button class="mark-btn${{isHard ? ' marked' : ''}}" onclick="toggleHard('${{w.w}}',event)" title="${{isHard ? '取消标记' : '标记为难词'}}">⭐</button></div>`;
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
    html += `<div class="empty">${{showHardOnly ? '还没有标记难词，点击单词旁 ⭐ 标记' : '未找到匹配的单词'}}</div>`;
  }}

  mainEl.innerHTML = html;
  statsEl.textContent = q
    ? `找到 ${{totalShown}} 个词汇`
    : showHardOnly
      ? `⭐ ${{totalShown}} 个难词`
      : `{total} 个词汇 · {len([t for t in TOPIC_ORDER if t in grouped])} 个学科`;
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

render('');

// ─── Auto-play ───
const ALL_WORDS = [];
DATA.forEach(t => t.words.forEach(w => ALL_WORDS.push(w)));

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
    const clean = word.replace(/['']/g, "'");
    if (!clean) {{ resolve(); return; }}
    if (audioEl) {{ audioEl.onerror = null; audioEl.onended = null; try {{ audioEl.pause(); }} catch(e) {{}} }}
    const urls = ttsUrls(clean);
    let idx = 0;
    const finish = () => {{ if (audioEl) {{ audioEl.onended = null; audioEl.onerror = null; }} resolve(); }};
    function tryNext() {{
      if (idx >= urls.length) {{ finish(); return; }}
      audioEl = new Audio();
      audioEl.onended = finish;
      audioEl.onerror = () => {{ idx++; tryNext(); }};
      audioEl.src = urls[idx];
      audioEl.play().catch(() => {{ idx++; tryNext(); }});
    }}
    tryNext();
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

document.getElementById('focusRevealArea').onclick = () => {{
  const revealed = focusOverlay.classList.toggle('revealed');
  document.getElementById('focusHint').style.display = revealed ? 'none' : '';
}};

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
