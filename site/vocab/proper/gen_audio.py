#!/usr/bin/env python3
"""为 proper-nouns 生成所有音频（单词 + 例句），使用 edge-tts 神经语音。"""
import asyncio
import hashlib
import json
import os
import re
import sys

import edge_tts

VOICE = "en-US-AriaNeural"  # 美式英语女声，清晰自然
RATE = "+0%"               # 正常语速
BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE, "audio")
OUT_MAP = os.path.join(BASE, "audio_map.js")

WORD_FOR_PRON = {
    "Ordovician-Silurian extinction": "Ordovician-Silurian extinction",
    "The Great Dying": "the Great Dying",
}

# 需要特殊处理发音的条目（写句子里口播时更自然）
PRON_OVERRIDES = {
    "Cretaceous-Paleogene extinction": "Cretaceous-Paleogene extinction",
    "K-Pg": "K-Pg extinction",
}


def slugify(text: str) -> str:
    """生成稳定文件名：小写、去重、非字母数字转连字符。"""
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] or "x"


def sha8(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def norm_text(text: str) -> str:
    """TTS 输入规范化：去掉多余空白。"""
    return re.sub(r"\s+", " ", text).strip()


async def synth(text: str, out_path: str) -> bool:
    tts = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    await tts.save(out_path)
    return os.path.getsize(out_path) > 500


def load_data():
    src = open(os.path.join(BASE, "data.js"), encoding="utf-8").read()
    # 去掉 JS 行注释
    src = re.sub(r"//.*$", "", src, flags=re.M)
    # 取出 PROPER_NOUNS 数组，替换 const 声明为可执行的 Python 表达式
    m = re.search(r"const\s+PROPER_NOUNS\s*=\s*(\[.*\])\s*;?\s*$", src, re.S)
    if not m:
        raise RuntimeError("无法在 data.js 中找到 PROPER_NOUNS 数组")
    arr_text = m.group(1)
    ns = {}
    exec("PROPER_NOUNS = " + arr_text, ns)
    return ns["PROPER_NOUNS"]


async def main():
    entries = load_data()
    os.makedirs(AUDIO_DIR, exist_ok=True)
    mapping = {}          # w -> {w: file, s: file}
    errors = []

    for i, (w, c, s, cat, ipa) in enumerate(entries):
        # 单词发音文本：用原始词条（对词组/连字符更自然）
        w_text = PRON_OVERRIDES.get(w, w)
        w_file = f"{i:02d}-w-{slugify(w)}.mp3"
        w_path = os.path.join(AUDIO_DIR, w_file)

        s_file = f"{i:02d}-s-{slugify(w)}.mp3"
        s_path = os.path.join(AUDIO_DIR, s_file)

        if not os.path.exists(w_path):
            try:
                await synth(norm_text(w_text), w_path)
                print(f"[{i:02d}] word OK: {w} -> {w_file}")
            except Exception as e:
                errors.append((w, "word", str(e)))
                print(f"[{i:02d}] word FAIL: {w}: {e}")
        else:
            print(f"[{i:02d}] word skip (exists): {w}")

        if s and not os.path.exists(s_path):
            try:
                await synth(norm_text(s), s_path)
                print(f"[{i:02d}] sent OK: {s[:50]}...")
            except Exception as e:
                errors.append((w, "sent", str(e)))
                print(f"[{i:02d}] sent FAIL: {w}: {e}")
        elif s:
            print(f"[{i:02d}] sent skip (exists)")

        mapping[w] = {"w": w_file, "s": s_file if s else None}

    with open(OUT_MAP, "w", encoding="utf-8") as f:
        f.write("// 词条 -> 音频文件映射（自动生成）\nconst AUDIO_MAP = ")
        f.write(json.dumps(mapping, ensure_ascii=False, indent=1))
        f.write(";\n")

    print(f"\n生成完成：{len(mapping)} 条映射 -> {OUT_MAP}")
    total = sum(1 for v in mapping.values() for k in ("w", "s") if v.get(k))
    print(f"音频文件共 {total} 个，位于 {AUDIO_DIR}/")
    if errors:
        print(f"\n失败 {len(errors)} 项：")
        for e in errors:
            print("  ", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
