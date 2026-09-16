# 英语学习资源站

目录已收敛为两个主体：

| 目录 | 用途 |
| --- | --- |
| `site/` | 可直接打开使用的网页、音频和同步进度数据 |
| `workspace/` | 构建脚本、源数据、报告、归档、原始素材和本地实验 |

## 使用入口

打开 `site/index.html`。站内页面分为：

- `site/vocab/`：1675、1791、1925、短语、场景词、专有名词、学科总表和 2026 词汇卡
- `site/listening/`：200 集精选、424 集全库、2026 官方对版练习和 TOEIC 补充
- `site/data/card-progress.json`：1675、1791、1925 与专有名词共享的掌握进度

1791 的本地真人发音及例句音频位于 `site/vocab/1791/audio/`；专有名词音频位于
`site/vocab/proper/audio/`。词条、释义、例句、来源和分类标注均随各页面保留。

## 开发材料

- `workspace/scripts/`：词表、音频、语速与学科页构建脚本
- `workspace/data/`：词表、分析数据和人工释义修订
- `workspace/projects/`：TPO 全库、200 集听力素材与 ETS 2026 构建源
- `workspace/docs/`：报告、计划和参考资料
- `workspace/archive/`：历史页面、备份和导入快照
- `workspace/_local/`：不入 Git 的抓取语料、中间产物与实验

常用构建命令：

```bash
python3 workspace/scripts/build_1925.py
python3 workspace/scripts/build_merged_by_discipline.py
python3 workspace/scripts/gen_1791_audio.py
```
