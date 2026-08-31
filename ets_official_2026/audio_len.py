#!/usr/bin/env python3
"""读音频时长，不依赖 ffmpeg。

ogg：Vorbis 的最后一个 Ogg page 里 granulepos = 总采样数，除以采样率就是精确时长。
     从文件尾部倒着找最后一个 "OggS" 同步字即可，不用解码。
mp3：读第一帧帧头拿到比特率，用 文件大小 * 8 / 比特率 估算（CBR 下够准）。
     返回值第二项标出是精确还是估算，别把两者混为一谈。
"""
import os
import struct

_MP3_BITRATES_V1_L3 = [None, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None]
_MP3_BITRATES_V2_L3 = [None, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None]
_MP3_RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def ogg_duration(path):
    """返回 (秒, 'exact') 或 (None, 'fail')。"""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        # 采样率在第一个 page 的 Vorbis identification header 里，偏移固定
        head = f.read(64)
        if not head.startswith(b"OggS"):
            return None, "fail"
        i = head.find(b"\x01vorbis")
        if i < 0:
            return None, "fail"
        rate = struct.unpack("<I", head[i + 12:i + 16])[0]
        if not rate:
            return None, "fail"
        # 尾部倒查最后一个 page 头
        tail_len = min(65536, size)
        f.seek(size - tail_len)
        tail = f.read(tail_len)
        j = tail.rfind(b"OggS")
        if j < 0:
            return None, "fail"
        granule = struct.unpack("<q", tail[j + 6:j + 14])[0]
        if granule <= 0:
            return None, "fail"
        return granule / rate, "exact"


def mp3_duration(path):
    """返回 (秒, 'estimate') 或 (None, 'fail')。"""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        buf = f.read(8192)
    # 跳过 ID3v2
    off = 0
    if buf[:3] == b"ID3":
        off = 10 + ((buf[6] & 0x7F) << 21 | (buf[7] & 0x7F) << 14 |
                    (buf[8] & 0x7F) << 7 | (buf[9] & 0x7F))
    for p in range(off, len(buf) - 4):
        if buf[p] != 0xFF or (buf[p + 1] & 0xE0) != 0xE0:
            continue
        ver = (buf[p + 1] >> 3) & 0x03          # 3=MPEG1, 2=MPEG2, 0=MPEG2.5
        layer = (buf[p + 1] >> 1) & 0x03        # 1 = Layer III
        if layer != 1 or ver == 1:
            continue
        bi = (buf[p + 2] >> 4) & 0x0F
        ri = (buf[p + 2] >> 2) & 0x03
        if ri == 3:
            continue
        table = _MP3_BITRATES_V1_L3 if ver == 3 else _MP3_BITRATES_V2_L3
        br = table[bi]
        if not br or ver not in _MP3_RATES:
            continue
        return (size - off) * 8 / (br * 1000), "estimate"
    return None, "fail"


def sniff(path):
    """按内容判定容器，不信扩展名。

    实测 student-practice-test-2 的 zip 里有一个 .ogg 其实是 MP3
    （s2_m1_cr08），只看后缀会漏掉。
    """
    with open(path, "rb") as f:
        head = f.read(4)
    if head[:4] == b"OggS":
        return "ogg"
    if head[:3] == b"ID3" or (len(head) > 1 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0):
        return "mp3"
    return os.path.splitext(path)[1].lower().lstrip(".")


def duration(path):
    kind = sniff(path)
    if kind == "ogg":
        return ogg_duration(path)
    if kind == "mp3":
        return mp3_duration(path)
    return None, "fail"


if __name__ == "__main__":
    import sys
    from collections import Counter
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    c = Counter()
    tot = 0.0
    for name in sorted(os.listdir(d)):
        if name.startswith("."):
            continue
        sec, how = duration(os.path.join(d, name))
        c[how] += 1
        if sec:
            tot += sec
        print(f"{name:<24}{'--' if sec is None else format(sec, '7.2f')}  {how}")
    print(f"\n{dict(c)}  合计 {tot / 60:.1f} 分钟")
