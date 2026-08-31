#!/usr/bin/env python3
"""从听力转写文本里提取讲座学科，并归并成粗领域。

为什么要两级：
  一级 = 原始学科字符串，直接来自旁白句 "Listen to part of a lecture in a ___ class"。
         这是 ETS 自己写的标签，比按标题猜关键词可靠。
  二级 = 粗领域（11 类），用来和考场回忆的领域分布做对照。

难点：第 66-71 套（2019 年后格式）的转写普遍没有旁白句，第 41 套也没有，
      共 22 集必须退回按 标题+开头正文 的关键词判定。所以 origin 字段
      区分 'narrator'（ETS 原始标签）和 'keyword'（本地推断），别把两者混为一谈。
"""
import re

# ---- 一级：从旁白句里抠出学科名 ----
_SUBJ_PATS = [
    r"\bin an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+class\b",
    r"\bin the\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+class\b",
    r"\bfrom an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+class\b",
    r"\bclass on\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)[\.\,]",
    r"\bin an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+lecture\b",
    r"\bpart of an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+lecture\b",
    r"\bin an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+course\b",
    r"\bin an?\s+([A-Za-z][A-Za-z\s'&-]{2,40}?)\s+seminar\b",
]


def raw_subject(head: str):
    """head = 转写前 3 句拼起来的英文。返回小写学科名或 None。"""
    for p in _SUBJ_PATS:
        m = re.search(p, head, re.I)
        if m:
            s = re.sub(r"\s{2,}", " ", m.group(1).lower().strip())
            # "class on theater history" 之类会带上冠词残留
            s = re.sub(r"^(the|a|an)\s+", "", s)
            return s
    return None


# ---- 二级：学科名 -> 粗领域（顺序即优先级，先命中先算）----
DOMAINS = [
    ("艺术/音乐/文学/戏剧",
     r"art|music|literat|theat|drama|film|poet|dance|choreo|acting|creative writing|design|photograph"),
    ("植物/农业",
     r"botan|plant|agricultur|horticultur|forest|food science"),
    ("生物/动物",
     r"biolog|zoolog|animal|entomolog|ornitholog|paleontol|genetic|physiolog|marine"),
    ("天文/航天", r"astronom|astrophys|space science|cosmolog"),
    ("地质/地球/气象", r"geolog|earth science|meteorol|oceanograph|geograph|climat"),
    ("考古/人类学", r"archae|anthropol|prehistor"),
    ("历史/社会/政治",
     r"histor|sociolog|government|politic|civilizat|urban studies|city planning|law"),
    ("环境/生态", r"environment|ecolog|conservat|sustainab"),
    ("心理/语言/教育", r"psycholog|linguist|educat|pedagog|cognitive|philosoph"),
    ("商业/经济", r"business|econom|market|advertis|management|finance|accounting"),
    ("工程/技术/理化",
     r"engineer|chemis|physic|material|computer|technolog|architect|astronautic|health|medic|nutrition"),
]

# ---- 关键词兜底：给没有旁白句的 22 集用。顺序即优先级 ----
_FALLBACK = [
    ("艺术/音乐/文学/戏剧",
     r"work of art|works of art|art histor|painter|painting|paint\b|sculpt|wallpaper|"
     r"design|composer|symphon|melod|novel|poem|playwright|theater|theatre|museum|"
     r"portrait|canvas|brushstroke|aesthetic"),
    ("考古/人类学",
     r"archaeolog|excavat|artifact|potter[y|s]|ancient culture|ancient cultures|"
     r"prehistor|inuit|dwelling|shelter.*climate|burial|settlement"),
    ("天文/航天",
     r"exoplanet|planet\b|planets|orbit around|aurora|solar system|star\b|stars\b|"
     r"telescope|galaxy|comet|asteroid|pegas"),
    ("地质/地球/气象",
     r"mineral|geolog|earth crust|tectonic|plate\b|plates\b|volcan|hydrothermal|"
     r"sediment|erosion|rock formation|strata|magma"),
    ("环境/生态",
     r"ecosystem|savanna|biodiversity|conservation|habitat loss|wildfire|"
     r"deforest|pollut|sustainab"),
    ("植物/农业",
     r"desert plant|plants|photosynthe|seed|leaf|leaves|root system|crop|"
     r"cultivat|tree\b|trees\b|flower"),
    ("生物/动物",
     r"animal|fish\b|crab|bird|insect|mammal|evolutionary biolog|evolution|"
     r"species|organism|sleep|vision|predator|prey|behavior|cell|dna|gene"),
    ("心理/语言/教育",
     r"emotion|memor(y|ies)|theory of mind|cognit|perception|learning|"
     r"language acquisition|psycholog"),
    ("历史/社会/政治",
     r"columbus|industrial revolution|empire|dynasty|colon|war\b|revolution|"
     r"culture in the united states|social class|migration of people"),
    ("商业/经济", r"market|consumer|profit|company|industry|trade\b|economic"),
    ("工程/技术/理化", r"engineer|machine|chemical|molecul|atom|physics|material"),
]


def domain_from_subject(subj: str):
    for name, pat in DOMAINS:
        if re.search(pat, subj, re.I):
            return name
    return None


def domain_from_text(*tiers: str):
    """分层匹配：标题命中优先于开头命中，开头命中优先于正文命中。

    不分层的话正文里一句无关的 "plants" 就能把「招潮蟹的视野」判成植物学——
    实测确实发生过，所以必须按可信度分层，而不是把文本拼起来一把搜。
    """
    for t in tiers:
        if not t:
            continue
        for name, pat in _FALLBACK:
            if re.search(pat, t, re.I):
                return name
    return None


# 关键词兜底判错、需要手工钉住的条目。key = (套号, 讲座序号)
# 每条都读过开头正文，理由写在注释里；只对 22 条无旁白句的讲座生效。
OVERRIDE = {
    (67, 1): "生物/动物",       # Animal Behavior Patterns：动物行为与环境的互动
    (67, 2): "心理/语言/教育",   # Emotional Connection：情绪与记忆的关系
    (68, 1): "考古/人类学",      # Two Ancient Arctic Cultures：北极两支古代文化
    (69, 3): "生物/动物",       # the fiddler crab's visual field：招潮蟹的视觉
    (70, 1): "生物/动物",       # 进化生物学中一个 19 世纪提出的原理及对它的反驳
}


def classify(head: str, title: str, body: str = "", key=None):
    """返回 (原始学科 或 None, 粗领域, 来源)。key=(套号, 序号) 用于查手工修正表。"""
    subj = raw_subject(head)
    if subj:
        d = domain_from_subject(subj)
        if d:
            return subj, d, "narrator"
        # 有标签但没归上类：仍然保留标签，领域走关键词
        d2 = domain_from_text(title, head, body[:1500])
        return subj, d2 or "其他", "narrator"
    if key and key in OVERRIDE:
        return None, OVERRIDE[key], "manual"
    d = domain_from_text(title, head, body[:1500])
    return None, d or "其他", "keyword"
