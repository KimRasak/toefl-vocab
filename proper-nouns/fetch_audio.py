#!/usr/bin/env python3
"""从剑桥词典抓取真人美音 mp3（本地优先，缺失才下载）。

策略：
1. 从 data.js 读取全部词条
2. 对每个词条请求 Cambridge 词典页面，解析美音（us_pron）mp3 链接
3. 下载到 proper-nouns/audio/ 下，命名为 {index}-w-{slug}.mp3（覆盖 edge-tts 合成版）
4. 例句音频保留：edge-tts 或降级链（词典无例句朗读音频）
5. 生成 audio_map.js
"""
import asyncio
import json
import os
import re
import sys

import aiohttp

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.environ.get("AUDIO_DIR", os.path.join(BASE, "audio"))
OUT_MAP = os.environ.get("OUT_MAP", os.path.join(BASE, "audio_map.js"))
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
CAM_URL = "https://dictionary.cambridge.org/dictionary/english/{word}"

# 需要特殊 URL 词的映射（剑桥词典 slug 与词条文本不一致时）
URL_OVERRIDES = {
    "the transverse flute": "transverse-flute",
    "transverse flute": "transverse-flute",
    "French horn": "french-horn",
    "English horn": "english-horn",
    "double bass": "double-bass",
    "pan flute": "pan-flute",
    "snare drum": "snare-drum",
    "bass drum": "bass-drum",
    "shuttle bus": "shuttle-bus",
    "track meet": "track-meet",
    "meal plan": "meal-plan",
    "term paper": "term-paper",
    "career fair": "career-fair",
    "office hours": "office-hours",
    "check out": "check-out",
    "instead of": "instead-of",
    "rather than": "rather-than",
    "Lechuguilla Cave": "lechuguilla",
    "the Renaissance": "renaissance",
    "the Reformation": "reformation",
    "the Scientific Revolution": "scientific-revolution",
    "sulfuric acid": "sulfuric-acid",
    "carbon dioxide": "carbon-dioxide",
    "carbon monoxide": "carbon-monoxide",
    "carbon footprint": "carbon-footprint",
    "carbon cycle": "carbon-cycle",
    "carbon sequestration": "carbon-sequestration",
    "greenhouse gas": "greenhouse-gas",
    "greenhouse effect": "greenhouse-effect",
    "global warming": "global-warming",
    "climate change": "climate-change",
    "fossil fuel": "fossil-fuel",
    "natural gas": "natural-gas",
    "renewable energy": "renewable-energy",
    "solar panel": "solar-panel",
    "wind turbine": "wind-turbine",
    "geothermal energy": "geothermal-energy",
    "nuclear power": "nuclear-power",
    "hydraulic fracturing": "hydraulic-fracturing",
    "shale gas": "shale-gas",
    "methane hydrate": "methane-hydrate",
    "acid rain": "acid-rain",
    "ultraviolet radiation": "ultraviolet-radiation",
    "financial aid": "financial-aid",
    "interlibrary loan": "interlibrary-loan",
    "dining hall": "dining-hall",
    "student union": "student-union",
    "bulletin board": "bulletin-board",
    "work-study": "work-study",
    "off-campus": "off-campus",
    "State of Alabama": "alabama",
}


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] or "x"


def load_data():
    data_file = os.environ.get("DATA_FILE", os.path.join(BASE, "data.js"))
    src = open(data_file, encoding="utf-8").read()
    src = re.sub(r"//.*$", "", src, flags=re.M)
    m = re.search(r"const\s+PROPER_NOUNS\s*=\s*(\[.*\])\s*;?\s*$", src, re.S)
    if not m:
        raise RuntimeError("无法在 data.js 中找到 PROPER_NOUNS 数组")
    ns = {}
    exec("PROPER_NOUNS = " + m.group(1), ns)
    return ns["PROPER_NOUNS"]


def cam_candidates(word: str):
    """生成剑桥词典 URL slug 候选列表（按优先级）。"""
    w = word.strip().lower()
    if word in URL_OVERRIDES:
        return [URL_OVERRIDES[word]]
    cands = []
    w2 = re.sub(r"\s*/\s*", "-", w)  # "semester / term" -> "semester-term"
    cands.append(re.sub(r"[^a-z0-9]+", "-", w2).strip("-"))
    # State of X -> X（核心词）
    m = re.match(r"state of (.+)", w)
    if m:
        cands.append(re.sub(r"[^a-z0-9]+", "-", m.group(1)).strip("-"))
    # Strait of X / Gulf of X / Bay of X -> X
    m = re.match(r"(strait|gulf|bay|sea) of (.+)", w)
    if m:
        cands.append(re.sub(r"[^a-z0-9]+", "-", m.group(2)).strip("-"))
    # the X -> X
    if w.startswith("the "):
        cands.append(re.sub(r"[^a-z0-9]+", "-", w[4:]).strip("-"))
    # X-Y extinction -> X（如 Ordovician-Silurian -> ordovician）
    m = re.match(r"([a-z]+)-[a-z]+ extinction", w)
    if m:
        cands.append(m.group(1))
    # 多词组合：取第一个实词（去 of / the）
    if " " in w:
        first = w.split()[0]
        if first not in ("of", "the", "a"):
            cands.append(first)
    # 去重保留顺序
    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


async def fetch_mp3(session, word, out_path, sem):
    """抓取一个词的美音 mp3（含核心词回退 + 限流重试）。返回 True 成功 / False 失败。"""
    # 已有真人版（v1, 48kHz）则跳过
    if os.path.exists(out_path) and os.path.getsize(out_path) > 500:
        try:
            with open(out_path, "rb") as f:
                head = f.read(4)
            # MPEG v1 特征：帧头第2字节高2位为 11（v1）
            if head[1] & 0x18 == 0x18:
                return True  # 已是真人版
        except Exception:
            pass
        # 否则视为 edge-tts 合成版，删除重新下载
        try:
            os.remove(out_path)
        except Exception:
            pass
    for cam in cam_candidates(word):
        for attempt in range(3):
            if await try_fetch(session, cam, out_path, sem):
                return True
            if attempt < 2:
                await asyncio.sleep(3)  # 限流退避
    return False


async def try_fetch(session, cam, out_path, sem):
    """尝试抓取一个剑桥 slug 的美音 mp3。"""
    url = CAM_URL.format(word=cam)
    try:
        async with sem:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return False
                html = await resp.text()
        # 美音优先：us_pron；没有则任意 mp3
        mp3s = re.findall(r'"(/media/english/us_pron/[^"]+\.mp3)"', html)
        if not mp3s:
            mp3s = re.findall(r'"(/media/english/[^"]+\.mp3)"', html)
        if not mp3s:
            return False
        mp3 = mp3s[0]
        async with sem:
            async with session.get(
                "https://dictionary.cambridge.org" + mp3,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status != 200:
                    return False
                data = await resp.read()
        if len(data) < 500:
            return False
        with open(out_path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


async def main():
    entries = load_data()
    os.makedirs(AUDIO_DIR, exist_ok=True)
    sem = asyncio.Semaphore(4)  # 并发 6，避免触发反爬

    mapping = {}
    ok = 0
    fail = []
    async with aiohttp.ClientSession(headers=UA) as session:
        for i, (w, c, s, cat, ipa) in enumerate(entries):
            w_file = f"{i:02d}-w-{slugify(w)}.mp3"
            w_path = os.path.join(AUDIO_DIR, w_file)
            s_file = f"{i:02d}-s-{slugify(w)}.mp3"
            s_path = os.path.join(AUDIO_DIR, s_file)

            # 例句音频：保留 edge-tts 已有的；没有就留给页面降级链
            if not os.path.exists(s_path):
                s_file = None

            # fetch_mp3 内部判断：已是真人版(MPEG v1)则跳过，edge-tts 合成版删除重下
            if await fetch_mp3(session, w, w_path, sem):
                ok += 1
                if not os.path.exists(w_path) or os.path.getsize(w_path) <= 500:
                    print(f"[{i:02d}] real OK: {w}")
            else:
                fail.append((w, i))
                print(f"[{i:02d}] real FAIL: {w}")
                # 保留 edge-tts 合成版作兜底
                if not os.path.exists(w_path):
                    w_file = None
            mapping[w] = {"w": w_file, "s": s_file}

    with open(OUT_MAP, "w", encoding="utf-8") as f:
        f.write("// 词条 -> 音频文件映射（真人发音优先，edge-tts 兜底；自动生成）\nconst AUDIO_MAP = ")
        f.write(json.dumps(mapping, ensure_ascii=False, indent=1))
        f.write(";\n")

    print(f"\n真人美音获取成功 {ok}/{len(entries)}，失败 {len(fail)}")
    if fail:
        print("失败列表（这些将回退 edge-tts 合成或页面降级链）：")
        for w, i in fail:
            print(f"  [{i}] {w}")
    print(f"映射 -> {OUT_MAP}")


if __name__ == "__main__":
    asyncio.run(main())
