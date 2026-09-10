#!/usr/bin/env python3
"""为 B 站合集 BV1ci421f7Lu 生成音频播放器 HTML（引用本地 audio/*.mp3，字幕内嵌）。"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
SUB_DIR = os.path.join(HERE, "subtitles")
META = "/tmp/bili_meta.json"
OUT = os.path.join(HERE, "托福TPO听力原文播放器.html")

def short_name(title, idx):
    # 与 download_bili.py 保持一致：TPO-25-L4 -> TPO-25_L4
    m = re.search(r"TPO-\d+[_-][A-Z]\d+", title)
    if m:
        return m.group(0).replace("-", "_").replace("_", "-", 1).upper()
    return f"p{idx:03d}"

def parse_srt(text):
    """把 SRT 文本解析为 [{start, end, text}]"""
    cues = []
    blocks = re.split(r"\n\s*\n", text.replace("\r", ""))
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip()]  # 去空行，保留序号
        # 找到时间行
        t_idx = None
        for i, l in enumerate(lines):
            if "-->" in l:
                t_idx = i
                break
        if t_idx is None:
            continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", lines[t_idx])
        if not m:
            continue
        def ts(g):
            return int(m.group(g*4-3))*3600 + int(m.group(g*4-2))*60 + int(m.group(g*4-1)) + int(m.group(g*4))/1000
        start, end = ts(1), ts(2)
        text = " ".join(lines[t_idx+1:])
        if text:
            cues.append({"start": start, "end": end, "text": text})
    return cues

def load_subs():
    """扫描 subtitles/ 目录，返回 {idx: cues}"""
    subs = {}
    if not os.path.isdir(SUB_DIR):
        return subs
    for fn in os.listdir(SUB_DIR):
        if not fn.endswith(".srt"):
            continue
        m = re.match(r"p(\d+)_", fn)
        if not m:
            continue
        idx = int(m.group(1))
        try:
            with open(os.path.join(SUB_DIR, fn), encoding="utf-8") as f:
                cues = parse_srt(f.read())
            if cues:
                subs[idx] = cues
        except Exception:
            pass
    return subs

def main():
    with open(META) as f:
        data = json.load(f)
    entries = sorted(data["entries"], key=lambda e: e["playlist_index"])

    items = []
    for e in entries:
        idx = e["playlist_index"]
        short = short_name(e["title"], idx)
        mp3 = os.path.join(AUDIO_DIR, f"p{idx:03d}_{short}.mp3")
        has = os.path.exists(mp3) and os.path.getsize(mp3) > 10000
        size_kb = os.path.getsize(mp3) // 1024 if has else 0
        dur = int(e.get("duration") or 0)
        mm, ss = divmod(dur, 60)
        items.append({
            "idx": idx,
            "short": short,
            "dur": f"{mm}:{ss:02d}",
            "dur_s": dur,
            "size": size_kb,
            "has": has,
        })

    json_data = json.dumps(items, ensure_ascii=False)
    subs = load_subs()
    subs_json = json.dumps(subs, ensure_ascii=False)
    n_sub = len(subs)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>托福 TPO 听力原文合集（B站 BV1ci421f7Lu · 200集）</title>
<style>
:root {{
  --bg: #f5f6f8; --panel: #ffffff; --accent: #2f6fed; --accent-dark: #1d4fc4;
  --text: #1a1d24; --muted: #6b7280; --border: #e3e6eb; --ok: #16a34a; --miss: #dc2626;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column;
}}
header {{
  background: var(--panel); border-bottom: 1px solid var(--border); padding: 12px 20px;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap; z-index: 10;
}}
header h1 {{ font-size: 17px; font-weight: 700; margin-right: auto; white-space: nowrap; }}
header h1 small {{ font-size: 12px; color: var(--muted); font-weight: 400; margin-left: 8px; }}
.controls {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
select, input[type="search"], button {{
  font-size: 13px; padding: 7px 12px; border: 1px solid var(--border); border-radius: 8px;
  background: #fff; color: var(--text); outline: none;
}}
select:focus, input[type="search"]:focus {{ border-color: var(--accent); }}
#searchBox {{ width: 220px; }}
.btn-primary {{ background: var(--accent); color: #fff; border-color: var(--accent); cursor: pointer; }}
.btn-primary:hover {{ background: var(--accent-dark); }}
main {{ flex: 1; display: flex; min-height: 0; }}
#listPanel {{
  width: 320px; min-width: 240px; background: var(--panel); border-right: 1px solid var(--border);
  overflow-y: auto; padding: 10px;
}}
#listPanel h2 {{ font-size: 12px; color: var(--muted); padding: 8px 6px 4px; }}
.ep {{ display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; cursor: pointer; }}
.ep:hover {{ background: #eef2fb; }}
.ep.active {{ background: #e0e9fb; }}
.ep .num {{ font-size: 11px; color: var(--muted); width: 34px; flex-shrink: 0; font-variant-numeric: tabular-nums; }}
.ep .name {{ flex: 1; font-size: 13px; font-weight: 600; }}
.ep .dur {{ font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; }}
.ep .st {{ font-size: 11px; }}
.ep .st.ok {{ color: var(--ok); }}
.ep .st.miss {{ color: var(--miss); }}
#playerPanel {{ flex: 1; display: flex; flex-direction: column; padding: 24px 28px; min-width: 0; }}
#nowTitle {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
#nowSub {{ font-size: 12px; color: var(--muted); margin-bottom: 18px; }}
audio {{ width: 100%; margin-bottom: 14px; }}
#progress {{ font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }}
#hint {{ margin-top: auto; font-size: 12px; color: var(--muted); line-height: 1.8; }}
footer {{ font-size: 11px; color: var(--muted); text-align: center; padding: 8px; background: var(--panel); border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<header>
  <h1>托福 TPO 听力原文合集 <small>B站 BV1ci421f7Lu · 共 200 集</small></h1>
  <div class="controls">
    <input type="search" id="searchBox" placeholder="搜索：TPO、L1、C2、25…">
    <select id="statusFilter">
      <option value="all">全部状态</option>
      <option value="ok">仅已下载</option>
      <option value="miss">仅缺失</option>
    </select>
    <button id="prevBtn" class="btn-primary">上一集</button>
    <button id="nextBtn" class="btn-primary">下一集</button>
  </div>
</header>
<main>
  <div id="listPanel">
    <h2 id="listCount"></h2>
    <div id="epList"></div>
  </div>
  <div id="playerPanel">
    <div id="nowTitle">请选择一集开始播放</div>
    <div id="nowSub"></div>
    <audio id="player" controls preload="metadata"></audio>
    <div id="progress"></div>
    <div id="hint">
      提示：点击左侧列表选择分集；播放进度会自动保存在本地浏览器（localStorage），刷新页面后继续。
      音频文件位于 audio/ 目录（p001_TPO-25_L4.mp3 等格式）。网页必须与 audio 文件夹放在同一目录下打开。
    </div>
  </div>
</main>
<footer>共 <span id="footTotal">0</span> 集 · 已下载 <span id="footOk">0</span> 集</footer>

<script>
const ITEMS = {json_data};
const audio = document.getElementById('player');
const epList = document.getElementById('epList');
const listCount = document.getElementById('listCount');
const searchBox = document.getElementById('searchBox');
const statusFilter = document.getElementById('statusFilter');
const nowTitle = document.getElementById('nowTitle');
const nowSub = document.getElementById('nowSub');
const progress = document.getElementById('progress');

let curIdx = null;
const LS_KEY = 'tofel_bili_audio_positions';
let positions = {{}};
try {{ positions = JSON.parse(localStorage.getItem(LS_KEY) || '{{}}'); }} catch(e) {{}}

function fmt(sec) {{
  if (!isFinite(sec) || sec < 0) sec = 0;
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return m + ':' + String(s).padStart(2, '0');
}}

function filtered() {{
  const q = searchBox.value.trim().toLowerCase();
  const st = statusFilter.value;
  return ITEMS.filter(it => {{
    const hay = (it.idx + ' ' + it.short).toLowerCase();
    if (q && !hay.includes(q)) return false;
    if (st === 'ok' && !it.has) return false;
    if (st === 'miss' && it.has) return false;
    return true;
  }});
}}

function render() {{
  const list = filtered();
  listCount.textContent = `共 ${{list.length}} 集`;
  epList.innerHTML = '';
  for (const it of list) {{
    const div = document.createElement('div');
    div.className = 'ep' + (it.idx === curIdx ? ' active' : '');
    const st = it.has ? '<span class="st ok">✓</span>' : '<span class="st miss">缺</span>';
    div.innerHTML = `<span class="num">p${{String(it.idx).padStart(3,'0')}}</span><span class="name">${{it.short}}</span><span class="dur">${{it.dur}}</span>${{st}}`;
    div.onclick = () => select(it.idx);
    epList.appendChild(div);
  }}
}}

function select(idx, autoplay) {{
  const it = ITEMS.find(x => x.idx === idx);
  if (!it) return;
  curIdx = idx;
  nowTitle.textContent = `p${{String(idx).padStart(3,'0')}} · ${{it.short}}`;
  nowSub.textContent = it.has ? `时长 ${{it.dur}} · 本地文件 audio/p${{String(idx).padStart(3,'0')}}_${{it.short}}.mp3` : '该集音频未下载';
  audio.src = it.has ? `audio/p${{String(idx).padStart(3,'0')}}_${{it.short}}.mp3` : '';
  if (autoplay && it.has) {{
    audio.currentTime = positions[idx] || 0;
    audio.play().catch(()=>{{}});
  }}
  render();
}}

audio.addEventListener('timeupdate', () => {{
  progress.textContent = `${{fmt(audio.currentTime)}} / ${{fmt(audio.duration || 0)}}`;
  if (curIdx) positions[curIdx] = audio.currentTime;
  localStorage.setItem(LS_KEY, JSON.stringify(positions));
}});

document.getElementById('prevBtn').onclick = () => {{
  const list = filtered();
  const i = list.findIndex(x => x.idx === curIdx);
  if (i > 0) select(list[i-1].idx, true);
}};
document.getElementById('nextBtn').onclick = () => {{
  const list = filtered();
  const i = list.findIndex(x => x.idx === curIdx);
  if (i >= 0 && i < list.length - 1) select(list[i+1].idx, true);
}};
audio.addEventListener('ended', () => {{
  const list = filtered();
  const i = list.findIndex(x => x.idx === curIdx);
  if (i >= 0 && i < list.length - 1) select(list[i+1].idx, true);
}});
searchBox.addEventListener('input', render);
statusFilter.addEventListener('change', render);

const ok = ITEMS.filter(x => x.has).length;
document.getElementById('footTotal').textContent = ITEMS.length;
document.getElementById('footOk').textContent = ok;
render();
</script>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成 {OUT}")
    print(f"共 {len(items)} 集，其中已下载 {sum(1 for x in items if x['has'])} 集")


if __name__ == "__main__":
    main()
