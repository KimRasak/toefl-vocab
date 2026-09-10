#!/usr/bin/env python3
"""给播放器加字幕滑动模式：自动跟随 / 手动浏览。
用法: python3 add_scroll_mode.py
"""
import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, '托福TPO听力原文播放器.html')


def main():
    html = open(HTML, encoding='utf-8').read()
    changed = []

    # 1. subBox CSS: 固定高度 + 可滚动
    old_css = """#subBox {
  margin-top: 12px; padding: 14px 16px; background: #10131a; border-radius: 10px;
  color: #f3f4f6; font-size: 16px; line-height: 1.7; min-height: 76px;
  font-family: "Georgia", "Times New Roman", serif; display: none;
}"""
    new_css = """#subBox {
  margin-top: 12px; padding: 14px 16px; background: #10131a; border-radius: 10px;
  color: #f3f4f6; font-size: 16px; line-height: 1.7; min-height: 76px;
  font-family: "Georgia", "Times New Roman", serif; display: none;
  max-height: 320px; overflow-y: auto; overscroll-behavior: contain;
  scrollbar-width: thin; scrollbar-color: #444 #10131a;
}
#subBox::-webkit-scrollbar { width: 8px; }
#subBox::-webkit-scrollbar-track { background: #10131a; }
#subBox::-webkit-scrollbar-thumb { background: #444; border-radius: 4px; }"""
    if old_css in html:
        html = html.replace(old_css, new_css)
        changed.append("subBox CSS: 可滚动区域")
    else:
        print("WARN: 未找到 subBox CSS")

    # 2. 工具栏加滚动模式按钮（放在 srcToggle 后）
    old_btn = """    <button id="srcToggle" title="切换音频与字幕来源：KMF官方 / 原版B站" style="font-size:13px;padding:5px 10px;border:1px solid var(--border,#ccc);border-radius:6px;background:#fff;cursor:pointer;">来源：KMF官方</button>"""
    new_btn = old_btn + """
    <button id="scrollToggle" title="字幕滚动模式：自动跟随当前句 / 手动滑动浏览" style="font-size:13px;padding:5px 10px;border:1px solid var(--border,#ccc);border-radius:6px;background:#fff;cursor:pointer;">滚动：自动</button>"""
    if old_btn in html:
        html = html.replace(old_btn, new_btn)
        changed.append("滚动模式按钮")
    else:
        print("WARN: 未找到 srcToggle 按钮")

    # 3. 替换 updateSubs 的自动滚动逻辑（加模式判断）
    old_scroll = """  if (active >= 0) {
    const el = subBox.querySelector(`.cue[data-i="${active}"]`);
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }"""
    new_scroll = """  if (active >= 0 && scrollMode === 'auto') {
    const el = subBox.querySelector(`.cue[data-i="${active}"]`);
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }"""
    if old_scroll in html:
        html = html.replace(old_scroll, new_scroll)
        changed.append("updateSubs 滚动逻辑")
    else:
        print("WARN: 未找到 updateSubs 滚动代码")

    # 4. 加 scrollMode 状态 + 按钮逻辑（放在 srcMode 定义后）
    old_mode = """let srcMode = localStorage.getItem('tofel_kmf_src') !== '0' ? 'kmf' : 'bili';"""
    new_mode = """let srcMode = localStorage.getItem('tofel_kmf_src') !== '0' ? 'kmf' : 'bili';
let scrollMode = localStorage.getItem('tofel_sub_scroll') !== 'manual' ? 'auto' : 'manual';
function setScrollMode(mode) {
  scrollMode = mode;
  localStorage.setItem('tofel_sub_scroll', mode);
  const btn = document.getElementById('scrollToggle');
  if (btn) {
    btn.textContent = mode === 'auto' ? '滚动：自动' : '滚动：手动';
    btn.classList.toggle('manual', mode === 'manual');
  }
}"""
    if old_mode in html:
        html = html.replace(old_mode, new_mode)
        changed.append("scrollMode 状态")
    else:
        print("WARN: 未找到 srcMode 定义")

    # 5. 初始化按钮事件 + 设置初始模式（在 setSrcMode(srcMode) 附近）
    old_init = """const srcBtn = document.getElementById('srcToggle');
if (srcBtn) srcBtn.onclick = () => setSrcMode(srcMode === 'kmf' ? 'bili' : 'kmf');
setSrcMode(srcMode);"""
    new_init = """const srcBtn = document.getElementById('srcToggle');
if (srcBtn) srcBtn.onclick = () => setSrcMode(srcMode === 'kmf' ? 'bili' : 'kmf');
setSrcMode(srcMode);
const scrollBtn = document.getElementById('scrollToggle');
if (scrollBtn) scrollBtn.onclick = () => setScrollMode(scrollMode === 'auto' ? 'manual' : 'auto');
setScrollMode(scrollMode);"""
    if old_init in html:
        html = html.replace(old_init, new_init)
        changed.append("初始化逻辑")
    else:
        print("WARN: 未找到初始化代码")

    # 6. 手动模式下：用户滚动后暂停自动跟随（下次播放仍恢复）——保持简单：按钮切换即可
    # 7. 保存
    open(HTML, 'w', encoding='utf-8').write(html)
    print(f"改动完成: {changed}")
    print(f"文件大小: {os.path.getsize(HTML)/1024/1024:.2f} MB")


if __name__ == '__main__':
    main()
