#!/usr/bin/env python3
"""为 1791 词表批量生成本地音频（单词 + 首例句）。

- 单词发音：下载剑桥官方真人美音 mp3（真实人声），失败则用 edge-tts 神经语音兜底
- 例句发音：edge-tts 神经语音（en-US-AriaNeural，接近真人）
- 输出：1791_audio/ 目录 + 1791_audio_map.js（词 -> {w, e} 本地路径）

用法:
  python3 gen_1791_audio.py
"""
import asyncio
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE, "1791_audio")
OUT_MAP = os.path.join(BASE, "1791_audio_map.js")
HTML_PATH = os.path.join(BASE, "my-tofel-1791words-words.html")
DATA_PATH = os.path.join(BASE, "output", "cambridge_defs_1791.json")

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://dictionary.cambridge.org/",
}
VOICE = "en-US-AriaNeural"  # 美式英语女声，自然清晰
RATE = "+0%"
CONCURRENCY = 10

os.makedirs(AUDIO_DIR, exist_ok=True)


def slugify(text: str) -> str:
    s = text.lower().strip().replace("`", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] or "x"


def parse_html_words(html_path: str):
    """从 HTML 里解析 DEFAULT_WORDS（保序）与 CAMBRIDGE 对象。"""
    html = open(html_path, encoding="utf-8").read()
    m = re.search(r"const DEFAULT_WORDS = (\[\[.*?\]\]);", html, re.S)
    words = eval(m.group(1))
    cam = {}
    for mm in re.finditer(r"  '((?:[^'\\]|\\.)+)': \{\n((?:.*?\n)*?)  \},", html):
        key = mm.group(1)
        body = mm.group(2)
        ipa = re.search(r"ipa: '((?:[^'\\]|\\.)*)'", body)
        mp3 = re.search(r"mp3: '((?:[^'\\]|\\.)*)'", body)
        exs = re.search(r"exs: \[(.*?)\]", body, re.S)
        cam[key] = {
            "ipa": ipa.group(1) if ipa else None,
            "mp3": mp3.group(1) if mp3 else None,
            "exs": [x for x in re.findall(r"'((?:[^'\\]|\\.)*)'", exs.group(1))] if exs else [],
        }
    return words, cam


def norm_example(text: str) -> str:
    text = text.replace("\\'", "'").replace("\\n", " ").replace("\\u", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def synth_edge(text: str, out_path: str) -> bool:
    import edge_tts
    tts = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    await tts.save(out_path)
    return os.path.getsize(out_path) > 500


def download_sync(url: str, out_path: str, timeout: float = 20.0) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        if len(data) < 500:
            return False
        with open(out_path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


async def download_many(urls):
    """并发下载：urls 为 [(word, url, out_path)]，返回成功集合。"""
    import aiohttp
    ok = set()
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(word, url, out_path):
        async with sem:
            try:
                async with aiohttp.ClientSession(
                    headers=UA, timeout=aiohttp.ClientTimeout(total=25)
                ) as sess:
                    async with sess.get(url) as r:
                        if r.status != 200:
                            return
                        data = await r.read()
                        if len(data) < 500:
                            return
                        with open(out_path, "wb") as f:
                            f.write(data)
                        ok.add(word)
            except Exception:
                return

    await asyncio.gather(*(one(w, u, p) for w, u, p in urls))
    return ok


async def main():
    words, cam = parse_html_words(HTML_PATH)
    print(f"词表 {len(words)} 词, CAMBRIDGE 命中 {len(cam)}")
    data = {}
    if os.path.exists(DATA_PATH):
        data = json.load(open(DATA_PATH, encoding="utf-8"))

    # ---- 阶段 1：下载剑桥真人单词 mp3 ----
    to_dl = []
    for i, (w, _zh) in enumerate(words):
        info = cam.get(w) or {}
        mp3_url = info.get("mp3") or (data.get(w.replace("`", "")) or {}).get("us_mp3_url")
        if not mp3_url:
            continue
        out = os.path.join(AUDIO_DIR, f"{i:04d}-w-{slugify(w)}.mp3")
        if os.path.exists(out) and os.path.getsize(out) > 500:
            continue
        to_dl.append((w, mp3_url, out))
    print(f"待下载单词 mp3: {len(to_dl)}")
    if to_dl:
        ok = await download_many(to_dl)
        print(f"剑桥下载成功: {len(ok)}/{len(to_dl)}")
    else:
        ok = set()

    # ---- 阶段 2：edge-tts 生成单词（剑桥失败/缺失）与首例句 ----
    pending = []
    for i, (w, _zh) in enumerate(words):
        info = cam.get(w) or {}
        wpath = os.path.join(AUDIO_DIR, f"{i:04d}-w-{slugify(w)}.mp3")
        if not (os.path.exists(wpath) and os.path.getsize(wpath) > 500):
            pending.append(("w", w, i, info.get("ipa") or ""))
        exs = info.get("exs") or []
        first_ex = norm_example(exs[0]) if exs else ""
        epath = os.path.join(AUDIO_DIR, f"{i:04d}-e-{slugify(w)}.mp3")
        if first_ex and not (os.path.exists(epath) and os.path.getsize(epath) > 500):
            pending.append(("e", w, i, first_ex))
    print(f"待 edge-tts 合成: {len(pending)}")

    import edge_tts
    sem = asyncio.Semaphore(CONCURRENCY)

    async def one(kind, w, i, text):
        async with sem:
            try:
                out = os.path.join(AUDIO_DIR, f"{i:04d}-{kind}-{slugify(w)}.mp3")
                tts = edge_tts.Communicate(text if kind == "e" else w.replace("`", ""), voice=VOICE, rate=RATE)
                await tts.save(out)
                return (kind, w, os.path.getsize(out) > 500)
            except Exception:
                return (kind, w, False)

    results = await asyncio.gather(*(one(*p) for p in pending))
    ok_edge = sum(1 for k, _w, s in results if s)
    print(f"edge-tts 成功: {ok_edge}/{len(pending)}")

    # ---- 阶段 3：写出音频映射 ----
    mapping = {}
    for i, (w, _zh) in enumerate(words):
        wpath = f"1791_audio/{i:04d}-w-{slugify(w)}.mp3"
        epath = f"1791_audio/{i:04d}-e-{slugify(w)}.mp3"
        entry = {}
        if os.path.exists(os.path.join(BASE, wpath)) and os.path.getsize(os.path.join(BASE, wpath)) > 500:
            entry["w"] = wpath
        if os.path.exists(os.path.join(BASE, epath)) and os.path.getsize(os.path.join(BASE, epath)) > 500:
            entry["e"] = epath
        if entry:
            mapping[w] = entry
            # 同时收录去重音符号的 key（con`duct -> conduct）
            clean = w.replace("`", "")
            if clean != w and clean not in mapping:
                mapping[clean] = entry

    lines = ["// 1791 词表本地音频映射（单词真人美音 + 例句神经语音）", "const AUDIO_1791 = {"]
    for w in mapping:
        entry = mapping[w]
        parts = []
        if "w" in entry:
            parts.append("w: '" + entry["w"] + "'")
        if "e" in entry:
            parts.append("e: '" + entry["e"] + "'")
        lines.append("  " + json.dumps(w, ensure_ascii=False) + ": {" + ", ".join(parts) + "},")
    lines.append("};")
    with open(OUT_MAP, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    n_w = sum(1 for v in mapping.values() if "w" in v)
    n_e = sum(1 for v in mapping.values() if "e" in v)
    total_mb = sum(
        os.path.getsize(os.path.join(BASE, p))
        for v in mapping.values() for p in v.values()
        if os.path.exists(os.path.join(BASE, p))
    ) / 1024 / 1024
    print(f"映射词条: {len(mapping)} (单词 {n_w}, 例句 {n_e}), 音频共 {total_mb:.1f} MB -> {OUT_MAP}")


if __name__ == "__main__":
    asyncio.run(main())
