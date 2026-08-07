# Active-learning evidence contract 1.0

这份合同用于“文献 + 主动学习代码 + 候选空间 + 推荐结果”的混合输入。它把计算流程整理成可追溯的研究资产，但不把模型输出升级为实验事实。

## 角色分层

| 资产 | 默认角色 | 可以说什么 | 不能直接说什么 |
|---|---|---|---|
| `labeled.csv` | 已有标签记录 | 文件中存在某些坐标与目标列 | 不能仅因列名 `z` 就称为实测材料性能 |
| `init_unlabeled.csv` | 初始候选空间 | 哪些输入坐标进入了候选池 | 不能称为已制备样品或已验证路线 |
| `curr_unlabeled.csv` | 当前待选择池 | 哪些候选被送入下一轮选择 | 不能称为实验结果 |
| `recommended_*.csv` | 单模型推荐 | 哪个模型/采集函数把哪些候选排在前面 | 不能把 `acquisition_value` 当成性能值 |
| `qbc_recommended.csv` | QBC 推荐 | 哪些候选的模型间分歧较高 | 不能把 `qbc_variance` 当成实验不确定度 |
| `*.py` | 方法/流程来源 | 输入、模型、采集函数、更新和写出路径 | 不能把代码注释或函数名当成已执行实验 |
| `sample_distribution_*.png` | 选择诊断图 | 点的空间分布和可视化检查入口 | 不能替代原始 CSV 或数据来源 |

## 复现完整性与写入边界

仓库随附的主动学习示例包含 `test_function.py`。它实现的是与已提供 CSV 一致的
Müller–Brown 合成目标函数 `max(0, -V(x, y))`，用于检查 QBC/贝叶斯优化流程是否能
运行；它不是 Ti-6Al-4V 的实测性能模型，也不能把候选点变成实验事实。若用户替换
为真实实验，应把该模块替换为有来源、单位、条件和测量谱系的目标函数或数据接口。

`run_sample_and_update.py` 默认将新标签写入 `iterations/iteration_<timestamp>/`，不
覆盖输入目录中的 `labeled.csv`。`run_all.py` 会先复制代码和起始记录到独立的
`runs/run_<timestamp>/`，只在该运行副本内推进下一轮；因此原始数据可直接回滚和比较。
若输出目录已存在，脚本会停止而不是混入旧运行结果。画像中的“写入风险”仍保留，
因为其他用户提供的脚本可能有不同的副作用。

如果推荐文件不在代码目录（例如随附示例把它放在相邻的“结果”目录），单轮采样时
显式传入：`python run_sample_and_update.py --input-dir <code-dir> --qbc-file <qbc.csv> --output-dir <new-iteration>`。

## 最小交接要求

Agent 应先运行：

```text
python scripts/prepare_intake.py <input-folder> --output intake-output
python scripts/profile_active_learning.py <input-folder> --output active-learning-profile
```

若同一目录还含论文 PDF，再运行 `extract_sources.py`；PDF 的 Docling/PyMuPDF 状态以 source bundle 为准。画像脚本会使用本文件旁的 `active-learning-field-lexicon.json`，关键词只生成候选语义提示，最终仍需根据论文、代码和实验记录 adjudicate。

## 代码与数据的关键审查

- 区分“模型输入”“模型预测/采集分数”“实际测量/可信模拟输出”。
- 记录变量的物理含义、单位、范围、归一化方式、目标方向（maximize/minimize）和约束来源；`x/y/z` 只是占位符。
- 记录推荐点是否已经出现在标签数据中；重复点可提示流程或去重问题，但不自动判定错误。
- 检查脚本是否依赖未提供的本地模块、是否使用硬编码相对路径、是否会覆盖 `labeled.csv` 或其他输入。
- 记录模型/核/采集函数/随机种子/版本和运行时间；缺失时写入信息缺口，不凭结果反推。
- 推荐点只有在有独立的实验或可信模拟记录（含条件、单位、来源和证据定位）后，才可进入 `property_records` 或 `locally-validated` 机制关系。

## 交付语气

优先使用：`模型推荐`、`候选点`、`模型间分歧`、`待实验验证`、`尚无物理单位/目标来源`。

避免使用：`最优工艺`、`已证明`、`实验不确定度`、`性能提升`，除非有相应的实验或可信模拟证据和来源定位。
