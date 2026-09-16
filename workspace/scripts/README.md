# 脚本

所有脚本都以仓库根目录为基准解析路径，可从任意当前目录调用。

- `build_*.py`：生成词汇页及学科汇总页
- `gen_*.py`、`cambridge_fetch.py`：释义与音频数据生成
- `measure_*.py`：听力语速分析
- `prepare_corpus.py`、`classify_disciplines.py`、`count_freq.py`、`merge_defs.py`：TPO 词频流水线

注意：`build_v6.py` 是从旧版 1791 页面升级到 V6 的迁移脚本，不应重复应用到当前已升级页面。
