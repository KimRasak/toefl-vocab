#!/usr/bin/env python3
"""Generate new_definitions.json for TOEFL vocabulary words."""
import json
import re

MANUAL = {
    "attribute": "n. 属性；特质 / v. 把…归因于",
    "conduct": "n. 行为；举止 / v. 引导；实施；传导",
    "content": "n. 内容；目录 / v. 使满足",
    "contract": "n. 合同；契约 / v. 收缩；订合同",
    "cozy": "adj. 舒适的；惬意的",
    "abolish": "v. 废除；废止（法律、制度等）",
    "abstruse": "adj. 深奥的；难以理解的",
    "abundant": "adj. 丰富的；大量的；充裕的",
    "acrimonious": "adj. 尖刻的；辛辣的（言语争论）",
    "abashed": "adj. 羞愧的；局促不安的",
    "abate": "v. 减弱；减轻（负面事物）",
    "abdicate": "v. 退位；放弃（职责、权力）",
    "abduct": "v. 绑架；诱拐",
    "abhor": "v. 憎恶；厌恶",
    "abhorrent": "adj. 令人憎恶的；可恶的",
    "abide": "v. 忍受；遵守（abide by）",
    "ablaze": "adj. 着火的；闪耀的；充满（情感）的",
    "aboriginal": "adj. 原住民的；土著的",
    "abortive": "adj. 失败的；夭折的",
    "abridge": "v. 删节；缩短；削减（权利）",
    "absolve": "v. 赦免；免除（责任、罪责）",
    "absorbing": "adj. 引人入胜的；极有趣的",
    "abstain": "v. 戒除；弃权（abstain from）",
    "abstinence": "n. 节制；禁欲",
    "accentuate": "v. 强调；使突出",
    "acclaim": "v./n. 称赞；欢呼",
    "accommodate": "v. 容纳；适应；提供住宿",
    "accomplice": "n. 同谋；帮凶",
    "accomplished": "adj. 技艺精湛的；有造诣的",
    "accost": "v. 上前搭话；搭讪",
    "accredit": "v. 授权；认可；委任",
    "accustom": "v. 使习惯（accustom to）",
    "acknowledge": "v. 承认；致谢",
    "acquire": "v. 获得；习得",
    "acquisitive": "adj. 贪婪的；渴求获取的",
    "acrid": "adj. 辛辣的；刺鼻的；尖刻的",
    "acrimony": "n. 尖刻；激烈（言语）",
    "acting": "adj. 代理的；临时的 / n. 表演；演技",
    "adage": "n. 谚语；格言",
    "adapt": "v. 适应；改编",
    "adaptable": "adj. 适应性强的；可改编的",
    "adaptation": "n. 适应；改编（作品）",
    "adept": "adj. 熟练的；擅长的 / n. 能手",
    "adequate": "adj. 足够的；适当的",
    "adhere": "v. 坚持；粘附（adhere to）",
    "adherence": "n. 坚持；遵守",
    "adhesive": "adj. 粘性的 / n. 粘合剂",
    "adjacent": "adj. 邻近的；毗连的",
    "adjoin": "v. 毗连；邻接",
    "adjoining": "adj. 毗邻的；相邻的",
    "adjourn": "v. 休会；延期",
    "adjust": "v. 调整；适应",
    "administer": "v. 管理；执行；给予（药物）",
    "administration": "n. 管理；行政；政府",
    "admirable": "adj. 令人钦佩的；值得赞赏的",
    "admonish": "v. 告诫；警告",
    "adore": "v. 崇拜；非常喜爱",
    "advance": "v./n. 前进；推进；提前",
    "adverse": "adj. 不利的；敌对的",
    "advice": "n. 建议；忠告",
    "aesthetic": "adj. 美学的；审美的",
    "affirm": "v. 断言；确认",
    "aggregate": "n. 总计；集合体 / adj. 合计的 / v. 聚集",
    "aggressive": "adj. 侵略性的；积极进取的",
    "agile": "adj. 敏捷的；灵活的",
    "agility": "n. 敏捷；灵活",
    "aim": "v./n. 瞄准；目标",
    "allege": "v. 声称；指控（无证据）",
    "alleviate": "v. 减轻；缓解",
    "allocate": "v. 分配；拨给",
    "ally": "n. 盟友 / v. 结盟",
    "alter": "v. 改变；修改",
    "alternate": "v. 交替；轮流 / adj. 交替的",
    "alternative": "n. 选择；替代品 / adj. 可供选择的",
    "amateur": "n. 业余爱好者 / adj. 业余的",
    "amazed": "adj. 惊讶的；惊奇的",
    "ambiguous": "adj. 模棱两可的；含糊的",
    "ambitious": "adj. 有雄心的；野心勃勃的",
    "amend": "v. 修正；改进（法律、文件）",
    "amplify": "v. 放大；详述；增强",
    "analysis": "n. 分析；解析",
    "annotate": "v. 注释；评注",
    "annoy": "v. 使恼怒；打扰",
    "annually": "adv. 每年；一年一次",
    "anonymous": "adj. 匿名的；无名的",
    "antique": "n. 古董 / adj. 古老的；古董的",
    "antiquity": "n. 古代；古物",
    "apathetic": "adj. 冷漠的；无动于衷的",
    "aperture": "n. 孔；光圈",
    "apex": "n. 顶点；顶峰",
    "apparel": "n. 服装；衣着",
    "appeal": "v./n. 呼吁；上诉；吸引",
    "applaud": "v. 鼓掌；称赞",
    "applicant": "n. 申请人；求职者",
    "application": "n. 申请；应用",
    "appoint": "v. 任命；指定；约定",
    "appraise": "v. 评估；估价",
    "appreciate": "v. 欣赏；感激；升值",
    "apprehend": "v. 逮捕；理解",
    "apprehension": "n. 忧虑；理解；逮捕",
    "apprentice": "n. 学徒 / v. 使当学徒",
    "appropriate": "adj. 适当的 / v. 挪用；拨款",
    "approve": "v. 批准；赞成",
    "approximate": "adj. 近似的 / v. 接近；估算",
    "apt": "adj. 恰当的；易于…的；聪明的",
    "compliment": "n./v. 称赞；恭维",
    "complimentary": "adj. 赞美的；免费赠送的",
    "licenced": "adj. 有执照的；许可的",
    "lown": "adj. 低洼的；低沉的",
    "limestone": "n. 石灰石",
    "limpid": "adj. 清澈的；透明的",
    "linguistics": "n. 语言学",
    "listless": "adj. 无精打采的；倦怠的",
    "lithe": "adj. 轻盈柔韧的；敏捷的",
    "luminous": "adj. 发光的；明亮的",
    "luster": "n. 光泽；光彩",
    "lusty": "adj. 强壮的；精力充沛的",
    "luxuriant": "adj. 繁茂的；丰富的",
    "luxurious": "adj. 奢侈的；豪华的",
    "impressionism": "n. 印象派（主义）",
    "indefatigable": "adj. 不知疲倦的；坚韧不拔的",
    "holocaust": "n. 大屠杀；浩劫",
    "heirship": "n. 继承权",
    "homogeneous": "adj. 同质的；均匀的",
    "hypothesis": "n. 假设；假说",
    "judgement": "n. 判断；判决",
    "juncture": "n. 关头；接合处",
    "ken": "n. 视野；知识范围（beyond one's ken）",
    "labyrinth": "n. 迷宫；错综复杂",
    "laudable": "adj. 值得称赞的",
    "liaison": "n. 联络；暧昧关系",
    "behaviour": "n. 行为；举止",
    "flavour": "n. 风味；口味 / v. 给…调味",
    "endeavour": "v./n. 努力；尽力",
    "gasoline": "n. 汽油",
    "christian": "n. 基督徒 / adj. 基督教的",
    "biochemistry": "n. 生物化学",
    "congressman": "n. 国会议员",
    "counterfeit": "adj. 伪造的 / v./n. 伪造；赝品",
    "distillation": "n. 蒸馏；精华",
    "dormitory": "n. 宿舍",
    "egoist": "n. 利己主义者",
    "entrepreneur": "n. 企业家",
    "eyewitness": "n. 目击者",
    "gangster": "n. 匪徒；歹徒",
    "hatchet": "n. 短柄小斧",
    "insubordinate": "adj. 不服从的；桀骜不驯的",
    "insufferable": "adj. 难以忍受的",
    "intermediary": "n. 中间人；媒介",
    "interlude": "n. 幕间休息；插曲",
    "irreconcilable": "adj. 不可调和的",
    "irrepressible": "adj. 抑制不住的",
    "irreproachable": "adj. 无可指责的",
    "irresistible": "adj. 不可抗拒的",
    "irresolute": "adj. 犹豫不决的",
    "irreverent": "adj. 不敬的；无礼的",
    "irrevocable": "adj. 不可撤销的",
    "itinerant": "adj. 巡回的；流动的",
    "aristocrat": "n. 贵族",
    "arithmetic": "n. 算术",
    "astronomy": "n. 天文学",
    "atheism": "n. 无神论",
    "barometer": "n. 气压计；晴雨表",
    "bankruptcy": "n. 破产",
    "circumference": "n. 周长；圆周",
    "cipher": "n. 密码；零",
    "comet": "n. 彗星",
    "concurrence": "n. 同时发生；同意",
    "connive": "v. 纵容；共谋",
    "consecrate": "v. 奉献；使神圣",
    "contemptible": "adj. 可鄙的；卑劣的",
    "continually": "adv. 不断地；频繁地",
    "contrive": "v. 设计；设法做到",
    "corps": "n. 军团；队",
    "corpse": "n. 尸体",
    "counterpart": "n. 对应物；职位相当的人",
    "cower": "v. 畏缩；蜷缩",
    "credential": "n. 凭证；资格证明",
    "creed": "n. 信条；信仰",
    "cubic": "adj. 立方的",
    "dab": "v./n. 轻触；涂抹",
    "dank": "adj. 阴湿冷的",
    "dauntless": "adj. 无畏的；勇敢的",
    "deceit": "n. 欺骗；欺诈",
    "deceitful": "adj. 欺骗性的",
    "decimal": "adj. 十进制的 / n. 小数",
    "defraud": "v. 诈骗；欺诈",
    "deft": "adj. 灵巧的；熟练的",
    "deity": "n. 神；神灵",
    "dictatorial": "adj. 独裁的；专横的",
    "disburse": "v. 支付；分配（款项）",
    "discrete": "adj. 离散的；不相关的",
    "dolphin": "n. 海豚",
    "drizzle": "v./n. 下毛毛雨；毛毛雨",
    "dungeon": "n. 地牢",
    "edible": "adj. 可食用的",
    "elapse": "v. （时间）流逝",
    "encroach": "v. 侵占；蚕食",
    "engrossed": "adj. 全神贯注的",
    "enslave": "v. 奴役；束缚",
    "enumerate": "v. 列举；枚举",
    "epoch": "n. 时代；纪元",
    "expeditious": "adj. 迅速的；敏捷的",
    "extravagant": "adj. 奢侈的；过度的",
    "fateful": "adj. 决定性的；宿命的",
    "fright": "n. 惊吓；恐惧",
    "fusion": "n. 融合；核聚变",
    "genre": "n. 类型；体裁",
    "geometry": "n. 几何学",
    "gratitude": "n. 感激；感谢",
    "impromptu": "adj./adv. 即兴的；即席的",
    "impurity": "n. 杂质；不纯",
    "inaugurate": "v. 开创；为…举行就职典礼",
    "inborn": "adj. 天生的；先天的",
    "incisive": "adj. 尖锐的；深刻的",
    "indent": "v./n. 缩排；订合同",
    "inure": "v. 使习惯（inure to）",
    "invalidate": "v. 使无效；证明…错误",
    "inventory": "n. 库存；清单",
    "inverse": "adj. 相反的 / n. 反数",
    "invoke": "v. 援引；唤起",
    "jeer": "v./n. 嘲笑；奚落",
    "jolt": "v./n. 震动；颠簸",
    "jumble": "v./n. 混杂；混乱",
    "junction": "n. 交叉点；连接处",
    "jurisdiction": "n. 司法权；管辖范围",
    "justly": "adv. 公正地；正当地",
    "juvenile": "adj. 青少年的 / n. 少年",
    "kindle": "v. 点燃；激起",
    "knowledgeable": "adj. 知识渊博的",
    "laborious": "adj. 艰苦的；费力的",
    "languish": "v. 憔悴；衰弱",
    "laud": "v. 赞扬；称赞",
    "lawsuit": "n. 诉讼",
    "legalize": "v. 使合法化",
    "legislate": "v. 立法",
    "lethal": "adj. 致命的",
    "levy": "v./n. 征收；征款",
    "liberate": "v. 解放；释放",
    "loathe": "v. 厌恶；憎恶",
    "lofty": "adj. 高耸的；崇高的",
    "lurk": "v. 潜伏；潜藏",
    "loot": "v./n. 抢劫；掠夺",
    "lottery": "n. 彩票；碰运气的事",
    "avoid": "v. 避免；回避；躲开",
    "bare": "adj. 赤裸的；空的；无遮盖的",
    "clip": "n. 夹子；修剪 / v. 夹住；修剪",
    "endorse": "v. 背书；支持；赞同",
    "hustle": "v./n. 催促；推搡；忙碌",
    "imprudent": "adj. 轻率的；不谨慎的",
    "jeopardy": "n. 危险；险境",
    "lament": "v./n. 哀悼；悲叹",
    "languid": "adj. 倦怠的；没精打采的",
    "legendary": "adj. 传奇的；大名鼎鼎的",
}


def load_1791():
    with open('/Users/jinzili/Documents/归档/tofel/my-tofel-1791words-words.html') as f:
        content = f.read()
    pairs = re.findall(
        r'\["([^"]+)","([^"]*(?:\\.[^"]*)*)"\]',
        re.search(r'const DEFAULT_WORDS = (\[\[.*?\]\]);', content, re.DOTALL).group(1),
    )
    return {w.lower(): d for w, d in pairs}


POS_MAP = {
    'vt.': 'v.', 'vi.': 'v.', 'a.': 'adj.', 'n.': 'n.', 'v.': 'v.',
    'adj.': 'adj.', 'adv.': 'adv.', 'prep.': 'prep.', 'conj.': 'conj.',
}


def simplify_def(raw: str) -> str:
    d = raw.strip()
    pos = ''
    lower = d.lower()
    for prefix in sorted(POS_MAP, key=len, reverse=True):
        if lower.startswith(prefix):
            pos = POS_MAP[prefix]
            d = d[len(prefix):].lstrip(' ,，')
            break

    # Stop at English example sentences / phrases
    d = re.split(
        r'[。.]\s*(?:[A-Z][a-z]|be |I |The |Water |He |A is |Abolish|withKidnap|smaller|Cataclysm)',
        d,
    )[0]
    d = re.split(
        r'\s*(?:be abducted|I can\'t|A is |Abolish|The |withKidnap|与Kidnap|非澳大利亚|Water dripped)',
        d,
    )[0]
    d = d.strip('，,；; ')

    # Fix wrong Chinese period used as separator
    d = d.replace('。', '；')
    # Normalize separators
    d = re.sub(r'[，,、]+', '；', d)
    d = re.sub(r';+', '；', d)
    d = re.sub(r'；+', '；', d).strip('；')
    # Fix wrong pos punctuation from source
    if pos:
        pass
    else:
        d = d.replace('adj。', '').replace('n。', '').replace('v。', '')

    if not d:
        return ''

    if pos:
        return f"{pos} {d}"
    return d


def load_words():
    words = []
    with open('/tmp/words_truly_needing_defs.txt') as f:
        for line in f:
            line = line.strip()
            if not line or '\t' in line:
                continue
            if '=' in line:
                line = line.split('=')[0]
            words.append(line.replace('`', '').lower())
    return sorted(set(words))


def main():
    src1791 = load_1791()
    words = load_words()
    out = {}
    missing = []

    for w in words:
        if w in MANUAL:
            out[w] = MANUAL[w]
        elif w in src1791:
            simplified = simplify_def(src1791[w])
            if simplified:
                out[w] = simplified
            else:
                missing.append(w)
        else:
            missing.append(w)

    if missing:
        print(f"MISSING ({len(missing)}): {missing}")
        raise SystemExit(1)

    out_path = '/Users/jinzili/Documents/归档/tofel/new_definitions.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(out)} definitions to {out_path}")


if __name__ == '__main__':
    main()
