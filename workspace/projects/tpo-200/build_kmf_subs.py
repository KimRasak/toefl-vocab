#!/usr/bin/env python3
"""从 KMF 官方原文生成带时间轴的 SRT 字幕（按字数比例分配音频时长）。
输出: subtitles_kmf/pXXX_TPO-XX_LX.srt
"""
import json, re, os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))

SPEAKERS = [
    'MALE PROFESSOR', 'FEMALE PROFESSOR', 'MALE STUDENT', 'FEMALE STUDENT',
    'MALE ADVISOR', 'FEMALE ADVISOR', 'MALE INSTRUCTOR', 'FEMALE INSTRUCTOR',
    'MALE LIBRARIAN', 'FEMALE LIBRARIAN', 'MALE ADMINISTRATOR',
    'CAMPUS SECURITY OFFICER', 'PROFESSOR', 'STUDENT', 'INSTRUCTOR',
    'ADVISOR', 'LIBRARIAN', 'NARRATOR', 'WOMAN', 'MAN', 'REGISTRAR',
    'SECRETARY', 'MALE', 'FEMALE', 'HEAD'
]
SPEAKER_RE = re.compile(r'\b(' + '|'.join(re.escape(s) for s in SPEAKERS) + r')\s*:')
ABBREV_WORDS = {'U.S.', 'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'St.', 'etc.', 'e.g.', 'i.e.', 'vs.', 'No.', 'vol.'}


def normalize_boundaries(text):
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        out.append(ch)
        if ch in '.!?' and i + 1 < len(text):
            nxt = text[i + 1]
            is_abbrev = False
            if ch == '.':
                for ab in ABBREV_WORDS:
                    if text[max(0, i - len(ab) + 1):i + 1] == ab:
                        is_abbrev = True
                        break
                if not is_abbrev:
                    prev_word = re.findall(r'([A-Za-z]+)\.$', text[:i + 1])
                    if prev_word and len(prev_word[-1]) == 1:
                        is_abbrev = True
                if i > 0 and text[i - 1].isdigit() and nxt.isdigit():
                    is_abbrev = True
            if not is_abbrev and nxt not in ' \n\t':
                out.append(' ')
        i += 1
    return ''.join(out)


def split_into_sentences(text):
    text = normalize_boundaries(text)
    text2 = SPEAKER_RE.sub(r'\n@@\1:', text)
    result = []
    for line in text2.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('@@'):
            speaker = line[2:].split(':', 1)[0]
            content = line[2:].split(':', 1)[1] if ':' in line[2:] else ''
        else:
            speaker, content = None, line
        for p in re.split(r'(?<=[.!?])\s+', content.strip()):
            p = p.strip()
            if not p:
                continue
            result.append(f"{speaker}: {p}" if speaker else p)
    # 合并过短片段（<12字符且与上一句合计 <180）
    merged = []
    for s in result:
        if merged and len(s) < 12 and len(merged[-1]) + len(s) < 180:
            merged[-1] = merged[-1] + ' ' + s
        else:
            merged.append(s)
    return merged


def fmt_time(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def get_duration(fpath):
    if not os.path.exists(fpath):
        return None
    r = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', fpath], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return None


def build(idx, fname, original, audio_path, out_dir):
    sents = split_into_sentences(original)
    if not sents:
        return None
    dur = get_duration(audio_path)
    if not dur or dur < 10:
        return None
    total_chars = sum(len(s) for s in sents)
    t = 0.0
    lines = []
    for i, s in enumerate(sents):
        seg_dur = dur * len(s) / total_chars
        start, end = t, t + seg_dur
        lines.append(f"{i+1}\n{fmt_time(start)} --> {fmt_time(end)}\n{s}\n")
        t = end
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return len(lines)


def main():
    kmf = json.load(open('/tmp/kmf_originals.json'))
    mapping = json.load(open('/tmp/bili_kmf_mapping.json'))
    full_audio = json.load(open('/tmp/kmf_full_audio.json'))
    bili = json.load(open('/tmp/bili_meta.json'))
    entries = {e['playlist_index']: e for e in bili['entries']}

    # 每集文件名
    idx_to_fname = {}
    for idx in full_audio:
        e = entries[int(idx)]
        m = re.search(r'TPO-\d+[_-][A-Z]\d+', e['title'])
        short = m.group(0).replace('-', '_').replace('_', '-', 1).upper() if m else f'TPO-{idx}'
        idx_to_fname[idx] = f"p{int(idx):03d}_{short}"

    out_dir = os.path.join(BASE, 'subtitles_kmf')
    ok, fail = 0, []
    for idx in sorted(full_audio, key=int):
        fname = idx_to_fname[idx] + '.srt'
        audio_path = os.path.join(BASE, 'audio_kmf', idx_to_fname[idx] + '.mp3')
        original = kmf[mapping[idx]['kmf_url']]['original']
        n = build(idx, fname, original, audio_path, out_dir)
        if n:
            ok += 1
        else:
            fail.append(idx)
        if int(idx) % 25 == 0:
            print(f"  {idx}/200 完成={ok} 失败={len(fail)}", flush=True)

    print(f"\n完成: 成功={ok} 失败={len(fail)}")
    if fail:
        print("失败:", fail)


if __name__ == '__main__':
    main()
