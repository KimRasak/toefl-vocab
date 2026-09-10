#!/usr/bin/env python3
"""从剑桥词典（dictionary.cambridge.org）抓取单词的官方释义与美音音频。

输出（写到一个 JSON 文件）：
  {
    "abate": {
      "word": "abate",
      "ipa": "əˈbeɪt",
      "us_mp3_url": "https://dictionary.cambridge.org/media/english/us_pron/...",
      "defs": ["to become less strong:", ...],           # 官方释义（英文）
      "examples": ["The wind has now abated.", ...],     # 官方例句
      "source": "https://dictionary.cambridge.org/dictionary/english/abate"
    },
    ...
  }

用法：
  python3 cambridge_fetch.py words.txt out.json
  words.txt 每行一个单词（可含词性前缀会被忽略，如 "abate	vt. ..."）

说明：
- 剑桥网页上的例句没有官方朗读音频（只有单词本身的英美发音 mp3），
  所以本脚本只负责"官方释义 + 官方例句文本 + 单词官方美音 mp3 链接"，
  例句音频由页面用 Google TTS / speechSynthesis 朗读。
"""
import json
import re
import sys
import time

import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
CAM_URL = "https://dictionary.cambridge.org/dictionary/english/{word}"
MP3_BASE = "https://dictionary.cambridge.org"

# 剑桥 slug 与词条文本不一致时的手工映射（多词/特殊词）
URL_OVERRIDES = {
    "abate": "abate",
}


def slug_for(word: str) -> str:
    w = word.strip().lower()
    if w in URL_OVERRIDES:
        return URL_OVERRIDES[w]
    return re.sub(r"[^a-z0-9]+", "-", w).strip("-")


def slug_variants(word: str) -> list[str]:
    """生成剑桥 URL slug 候选（按优先级）：原形 → 去连字符 → 去特殊字符。

    规则（实测）：
    - 反引号 ` 是重音标记（`conduct / con`duct 同词），去掉即可
    - 剑桥对很多连字符词用无连字符拼写：baby-sit -> babysit, figure-head -> figurehead
    - = 连接英美变体（cozy=cosy），两个都试
    - 大写 / 撇号等统一小写去除非字母数字
    """
    w = word.strip().lower().replace("`", "")
    # = 变体：拆成多个
    parts = [p.strip() for p in w.split("=") if p.strip()] or [w]
    cands = []
    for p in parts:
        cands.append(re.sub(r"[^a-z0-9]+", "-", p).strip("-"))      # 带连字符
        cands.append(re.sub(r"[^a-z0-9]+", "", p))                  # 去连字符
    # 去重保序
    seen = set(); out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c); out.append(c)
    return out


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_cambridge(html: str, word: str) -> dict:
    d = {"word": word, "ipa": "", "us_mp3_url": "", "defs": [], "examples": []}

    # 1) 美音 mp3（us_pron 优先，取第一个）
    m = re.search(r'"(/media/english/us_pron/[^"]+\.mp3)"', html)
    if not m:
        m = re.search(r'"(/media/english/[^"]+\.mp3)"', html)
    if m:
        d["us_mp3_url"] = MP3_BASE + m.group(1)

    # 2) 美音音标（第一个 us 发音的 ipa）
    # 页面结构：<span class="us dpron-i ">...<span class="ipa dipa ...">əˈbeɪt</span>
    m = re.search(
        r'<span class="us dpron-i[^"]*">.*?<span class="ipa dipa[^"]*">(.*?)</span>',
        html, re.S,
    )
    if m:
        d["ipa"] = strip_tags(m.group(1))

    # 3) 官方释义（英英）：div.def.ddef_d 内的文本，全部取（多义项）
    defs = re.findall(r'<div class="def ddef_d db">(.*?)</div>', html, re.S)
    d["defs"] = [strip_tags(x) for x in defs if strip_tags(x)]

    # 4) 官方例句：span.eg.deg（每个释义块下的例句）
    exs = re.findall(r'<span class="eg deg[^"]*">(.*?)</span>', html, re.S)
    d["examples"] = [strip_tags(x) for x in exs if strip_tags(x)]

    return d


def fetch_word(session, word: str) -> dict | None:
    # 依次尝试各 slug 变体；某个变体页面有释义就算命中
    for cam in slug_variants(word):
        url = CAM_URL.format(word=cam)
        try:
            r = session.get(url, timeout=25)
            if r.status_code != 200:
                continue
            html = r.text
        except Exception as e:
            print(f"[warn] {word}: {e}")
            continue
        # 词条不存在页（无释义块）→ 换变体
        if 'class="def ddef_d db"' not in html:
            continue
        d = parse_cambridge(html, word)
        d["source"] = url
        if d["defs"]:
            print(f"[ok]   {word}: {d['defs'][0][:55]} | mp3={'yes' if d['us_mp3_url'] else 'NO'} | 例句 {len(d['examples'])} | {cam}")
            return d
    print(f"[miss] {word}: 所有变体均无释义")
    return None


def fetch_word_retry(session, word: str, retries: int = 1) -> dict | None:
    """抓取一个词，失败可重试一次（网络抖动兜底）。"""
    d = fetch_word(session, word)
    if d is None and retries > 0:
        time.sleep(2)
        d = fetch_word(session, word)
    return d


def load_words(path: str):
    words = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        # 词表行格式："abate\tvt. (负面事物)减弱、减轻" —— 取第一列，再去掉词性前缀
        w = line.split("\t")[0].strip()
        w = re.sub(r"^[a-z]+\s*\.\s*", "", w, flags=re.I)  # 去掉 "vt." "adj." 等词性
        w = w.replace("`", "")  # 去掉重音标记（`conduct -> conduct）
        if w and w not in words:
            words.append(w)
    return words


def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "sample_words.txt"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "cambridge_defs.json"
    words = load_words(in_path)
    print(f"共 {len(words)} 个单词\n")

    out = {}
    session = requests.Session()
    session.headers.update(UA)
    for i, w in enumerate(words):
        d = fetch_word_retry(session, w)
        if d:
            out[w] = d
        if i % 5 == 4:
            time.sleep(1)  # 温和限流
        # 每 50 词增量写盘（中断也有部分结果）
        if i % 50 == 49:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
            print(f"  ...进度 {i+1}/{len(words)}，已收录 {len(out)}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n完成：{len(out)}/{len(words)} 写入 {out_path}")


if __name__ == "__main__":
    main()
