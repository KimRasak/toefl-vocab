#!/usr/bin/env python3
"""把高亮版 KMF 字幕（**困难短语**）嵌入播放器，加「标红短语」开关。
用法: python3 update_player_hl.py
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, '托福TPO听力原文播放器.html')
HL_DIR = os.path.join(BASE, 'subtitles_kmf_hl')


def parse_srt(srt_text):
    cues = []
    for block in srt_text.strip().split('\n\n'):
        lines = block.split('\n')
        if len(lines) < 2:
            continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', lines[1])
        if not m:
            continue
        start = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                 + int(m.group(4)) / 1000)
        end = (int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7))
               + int(m.group(8)) / 1000)
        text = ' '.join(l.strip() for l in lines[2:] if l.strip())
        cues.append({"start": round(start, 1), "end": round(end, 1), "text": text})
    return cues


def main():
    html = open(HTML, encoding='utf-8').read()

    # 1. 生成 SUBS_kmf_hl（从高亮 SRT）
    subs_hl = {}
    for f in sorted(os.listdir(HL_DIR)):
        if not f.endswith('.srt'):
            continue
        idx = str(int(re.match(r'p(\d+)', f).group(1)))
        cues = parse_srt(open(os.path.join(HL_DIR, f), encoding='utf-8').read())
        if cues:
            subs_hl[idx] = cues
    json_hl = json.dumps(subs_hl, ensure_ascii=False)
    if '</script' in json_hl.lower():
        json_hl = json_hl.replace('</script', '<\\/script')
    print(f"SUBS_kmf_hl: {len(subs_hl)} 集, {len(json_hl)/1024/1024:.2f} MB")

    # 2. 在 SUBS_kmf 后插入 SUBS_kmf_hl
    m = re.search(r'(const SUBS_kmf = \{.*?\});\n(?=const ITEMS)', html, re.S)
    if not m:
        print("ERROR: 未找到 SUBS_kmf")
        return
    html = html[:m.end()] + f'\nconst SUBS_kmf_hl = {json_hl};' + html[m.end():]

    # 3. 修改 loadSubs: 支持标红开关
    old_load = """  const list = srcMode === 'kmf' ? (SUBS_kmf[idx] || SUBS_bili[idx]) : (SUBS_bili[idx] || SUBS_kmf[idx]);"""
    new_load = """  const hlOn = localStorage.getItem('tofel_sub_hl') !== '0';
  let list;
  if (srcMode === 'kmf') {
    list = (hlOn && SUBS_kmf_hl[idx]) ? SUBS_kmf_hl[idx] : (SUBS_kmf[idx] || SUBS_bili[idx]);
  } else {
    list = SUBS_bili[idx] || SUBS_kmf[idx];
  }"""
    if old_load not in html:
        print("WARN: 未匹配 loadSubs list 行")
    else:
        html = html.replace(old_load, new_load)
        print("loadSubs 已更新")

    # 4. 渲染时把 **...** 转成 <span class="hl">
    old_render = """    subBox.innerHTML = cues.map((c, i) => `<div class="cue" data-i="${i}">${c.text}</div>`).join('');"""
    new_render = """    subBox.innerHTML = cues.map((c, i) => `<div class="cue" data-i="${i}">${renderCueText(c.text)}</div>`).join('');"""
    if old_render not in html:
        print("WARN: 未匹配渲染行")
    else:
        html = html.replace(old_render, new_render)
        print("渲染已更新")

    # 5. 加 renderCueText 函数 + 标红开关按钮逻辑（放 loadSubs 前）
    anchor = "function loadSubs(idx) {"
    helper = """function renderCueText(t) {
  if (!t) return '';
  // **...** -> <span class="hl">
  return t.replace(/\\*\\*([^\\*]+)\\*\\*/g, '<span class="hl">$1</span>');
}

function setHlToggle(on) {
  localStorage.setItem('tofel_sub_hl', on ? '1' : '0');
  const btn = document.getElementById('hlToggle');
  if (btn) {
    btn.textContent = on ? '标红：开' : '标红：关';
    btn.classList.toggle('on', on);
  }
  if (curIdx) loadSubs(curIdx);
}

""" + anchor
    if anchor not in html:
        print("WARN: 未找到 loadSubs anchor")
    else:
        html = html.replace(anchor, helper, 1)
        print("renderCueText 已添加")

    # 6. 工具栏加标红开关按钮（scrollToggle 后）
    old_btn = """    <button id="scrollToggle" title="字幕滚动模式：自动跟随当前句 / 手动滑动浏览" style="font-size:13px;padding:5px 10px;border:1px solid var(--border,#ccc);border-radius:6px;background:#fff;cursor:pointer;">滚动：自动</button>"""
    new_btn = old_btn + """
    <button id="hlToggle" title="标红困难短语（KMF官方字幕）" style="font-size:13px;padding:5px 10px;border:1px solid var(--border,#ccc);border-radius:6px;background:#fff;cursor:pointer;">标红：开</button>"""
    if old_btn not in html:
        print("WARN: 未找到 scrollToggle 按钮")
    else:
        html = html.replace(old_btn, new_btn)
        print("标红按钮已添加")

    # 7. CSS 加 .hl 样式（红色高亮）
    old_css = """#subBox::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }"""
    new_css = old_css + """
#subBox .hl { color: #ff6b6b; font-weight: 600; }"""
    if old_css not in html:
        print("WARN: 未找到 scrollbar CSS")
    else:
        html = html.replace(old_css, new_css)
        print(".hl 样式已添加")

    # 8. 初始化按钮事件（scrollBtn 后）
    old_init = """const scrollBtn = document.getElementById('scrollToggle');
if (scrollBtn) scrollBtn.onclick = () => setScrollMode(scrollMode === 'auto' ? 'manual' : 'auto');
setScrollMode(scrollMode);"""
    new_init = old_init + """
const hlBtn = document.getElementById('hlToggle');
if (hlBtn) hlBtn.onclick = () => setHlToggle(localStorage.getItem('tofel_sub_hl') === '0');
setHlToggle(localStorage.getItem('tofel_sub_hl') !== '0');"""
    if old_init not in html:
        print("WARN: 未找到初始化代码")
    else:
        html = html.replace(old_init, new_init)
        print("初始化已更新")

    # 保存
    open(HTML, 'w', encoding='utf-8').write(html)
    print(f"\n已保存: {os.path.getsize(HTML)/1024/1024:.2f} MB")


if __name__ == '__main__':
    main()
