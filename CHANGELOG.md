# Changelog

## 4.6.12

- Added a unified Agent output contract so README, SKILL, Schema, validators, reports, dashboards, and mechanism exports share one handoff.
- Added active-learning profiling for labeled data, candidate pools, Bayesian-optimization recommendations, QBC scores, static code dependencies, and in-place write risks.
- Added an Apple-style offline active-learning dashboard and a maintainable active-learning field lexicon.
- Ignored macOS archive metadata during intake/source extraction and treated Python source as readable text instead of binary-only manifest input.
- Added MIT licensing and a separate data/source notice for the reproducible raw-data folder.

## 4.6.8

- 修复离线 viewer 选择 JSON 时的错误可读性：报告行号、列号、字符位置和附近内容，不自动猜测截断的科研数据。
- 增强本地 JSON/CSV/TSV 读取，兼容 UTF-8 BOM 与 UTF-16LE/BE 文件。

## 4.6.7

- PDF 默认 profile 首次运行自动尝试下载当前需要的 Docling 模型，并将缓存、缺失模型、下载结果和失败原因写入 bundle。
- 新增 `--model-cache`、`--no-model-download` 和 `--force-model-download`；`auto` 下载失败可回退文本后端，显式 Docling 保留失败状态。
- 模型准备在批处理开始时执行一次，并通过 `artifacts_path` 复用缓存，避免每个 PDF 重复初始化或隐式下载。

## 4.6.6

- 环境报告增加 PDF/XML/HTML/DOCX/XLSX/JSON profile 状态、OCR/首次运行提示和直接可执行的下一步命令。
- JSON 对象数组全部分别导出，DOCX 在 `--extract-figures` 下提取嵌入图像；文档 manifest 增加 `review_status`、内容信号和复核动作。
- source review dashboard 统一为克制的 Apple HIG 风格，并显示“可交给 LLM/需要复核/失败”分层。
- 通用 viewer 的概览优先显示 blocker，导航显示各视图条目数，窄屏图形保持科学文字可读。

## 4.6.5

### 完整审查修复

- 修复 CSV 引号字段中的换行被拆行的问题，intake 与文献补充表均保持原始记录边界。
- 扫描型 PDF 无内容时明确提示 OCR/页图复核；显式文本后端收到 `--ocr` 时记录未执行 OCR，不再静默误导。
- 修复输入目录摄入自身输出目录、危险 URI 路径和来源检查台缺少原始文件回查入口的问题。
- 改善窄屏查看器表格的横向阅读，并把文献 SHA-256、后端尝试和原始文件链接纳入检查台。

## 4.6.4

### 可维护路由与可复现产物

- 路由关键词、同义词、排除词、歧义词和任务意图移到外部 JSON；`concept` 语义匹配优先，字符串只做召回。
- 新增路由维护合同和知识资产校验，防止词典漂移、重复术语、注册表断链和 intake 别名冲突。
- intake/source bundle/artifact manifest 统一使用 `path_base: "."` 和相对路径，环境审计仍保留可复现所需的运行时信息。
- 离线产物继续由同一份已验证 JSON 派生，补充科研人员从环境、输入、证据到行动的导览入口。

## 4.6.3

### 提取链收口

- PDF OCR 改为显式 `--ocr` 开启；默认不把 OCR 结果混入 born-digital 文本路径。
- Docling PDF 保留阅读顺序和章节归属，可选导出 `figures/*.png`；manifest 增加图像路径和更完整的空/部分状态判断。
- 文献环境报告补充 `jsonschema`，提取入口增加内容嗅探以识别扩展名错误的 PDF/XML/HTML/DOCX/XLSX，并接入 CSV/TSV/JSON 补充数据。
- 新增 `render_source_dashboard.py`，用离线页面检查提取环境、文件状态、fallback/OCR 警告以及 Markdown/JSON/CSV/页图/图像回查入口。

## 4.6.2

### 文献处理环境

- 新增 `scripts/extract_sources.py`，记录当前 Python/依赖/外部工具并选择 Docling、PyMuPDF、pdfplumber、lxml、BeautifulSoup、python-docx、openpyxl 等公开库。
- PDF 默认采用 `Docling → PyMuPDF → pdfplumber`，支持严格离线文本优先后端和可选页图渲染；XML/JATS/HTML/DOCX/XLSX 生成带章节、表格、图注或工作表锚点的 Markdown/JSON/CSV。
- 新增 `source-extraction-contract.md` 与 bundle Schema；提取失败、fallback、OCR 和模型依赖均显式记录，不把转换文本升级为独立证据。
- `prepare_intake.py` 识别 XML、HTML、DOCX、EPUB 类型，继续保持轻量盘点职责。

## 4.6.1

### 科研上手与可视化闭环

- 概览页增加四步阅读引导和结果/参照数值比较图，沿用 property/baseline 的原始单位与条件边界。
- 偏差页增加误差预算分量、观测效应和综合不确定度的并列图示；不改变底层统计含义。
- 异常传播链和 PSPP 关系支持逐条展开证据、反证、Falsifier、边界与 Mechanism Graph 链接。
- 信息缺口页增加验证项 × 缺口/假设 coverage matrix；PSPP 页改为保留全部节点的多阶段关系图。
- 结构化记录页不再遗漏条件、来源、证据、基准、可比性、偏差、验证和诊断对象。
- 浏览器 smoke test 增加新视图、暗色模式和 360px 窄屏回归检查；Schema 仍保持 4.6，未改变事实合同。

## 4.6.0

### 证据约束机理图谱

- 新增 `mechanism_graphs[]`、`mechanism_nodes[]`、`mechanism_edges[]` 和 `mechanism_updates[]`，将一次性假设与跨实验可复用机制知识分离。
- 机制边强制记录来源证据、条件边界、反证、可推翻条件、迁移级别、科学状态和版本。
- Stage 6 先执行条件化图谱检索，再生成新假设；Stage 8 通过提案—审核—新 artifact 写入更新图谱，禁止静默覆盖历史。
- 异常传播链、假设、PSPP 关系和经验更新均可链接机制边，但不得因此自动升级证据等级。

### 工程与可视化

- 新增 `scripts/mechanism_graph.py`，支持摘要、查询、索引、JSON/CSV/DOT 导出、版本 diff 和受控更新。
- 新增 `scripts/audit_mechanism_graph.py` 和 `references/mechanism-graph-contract.md`。
- 离线查看器重构为克制、层级清晰的系统界面，新增交互式机理图谱、节点/边审计、状态筛选、搜索、缩放、暗色模式、减少动态与降低透明度适配。
- Schema、报告生成器、验证器、示例与 artifact manifest 升级到 4.6。

### 防护

- 增加跨材料错误迁移、无证据机制边、推断边越权升级、图谱反向引用断裂、未审批写入和图谱注入等对抗回归。

## 4.5.0

### 诊断深度

- 新增 Stage 3.5 误差预算：在共同方差/不确定度基准上分解测量、样品、批次、工艺控制和模型贡献。
- 新增 Stage 5.5 异常传播链：逐节点记录材料属性、加工、结构、性质、性能及其证据、反证和边界。
- Stage 7 改为信息缺口驱动的最小实验集，增加覆盖矩阵、停止规则和资源约束。
- Stage 8 强制使用标准 PSPP（Processing–Structure–Properties–Performance）经验图；材料属性作为可选上游节点。

### 工程实现

- 输出 Schema 升级到 4.5，新增 `error_budgets[]`、`anomaly_propagation_chains[]`、`information_gaps[]`、`experiment_sets[]` 和 `pspp_maps[]`。
- 新增 `references/error-anomaly-pspp-contract.md` 和 `scripts/analyze_error_budget.py`。
- 报告与离线查看器新增误差预算、传播链、信息缺口、最小实验集和 PSPP 页面。
- 输入助手新增重复层级、仪器/校准、分析版本、设定值/实测值和中间结构/性质缺失提醒。
- 新增 E26–E30 与相应对抗回归。

## 4.4.0

### 重新组织

- 将人类使用说明移至 `README.md`，`SKILL.md` 收敛为 Agent 执行控制器。
- 建立 README（L1）—SKILL/合同（L2）—Schema/适配器/脚本/查看器（L3）三层结构。
- 将领域适配器完整清单保留在 `references/adapter-registry.json`，按任务加载。

### 输入侧

- 新增 `scripts/prepare_intake.py`，支持 CSV、TSV、JSON、XLSX、文本和文件清单。
- 保留原文件、原列、原值、公式和文件哈希；不静默补值。
- 新增中文与英文表头别名、歧义字段候选和缺失信息优先级。
- 新增 `references/input-contract.md`、`input-schema.json`、`intake-field-aliases.json`。
- 新增跨域输入示例和规范化输出。

### 输出侧

- 默认人类报告行动优先，不在聊天中铺开完整 JSON。
- 新增 `condition_registry[]` 和 `[Cond-*]` 条件别名。
- 新增 `scripts/render_report.py` 和 `references/report-contract.md`。
- 新增离线通用查看器 `viewer/index.html` 和单文件仪表盘生成器。
- 所有派生报告和仪表盘必须来自同一份通过验证的 JSON。

### 契约与防护

- 输出 Schema 升级到 4.4，加入 `input_assessment`、`condition_registry`、`artifact_manifest`。
- 新增 E21–E25：输入丢失、缺失项误分级、条件别名冲突、呈现越权和不安全渲染。
- 增强不可比闸门，禁止在 `not-comparable` 情况下显示残差或材料偏差结论。
- 对 Excel 公式、隐藏行列、伪 PDF、畸形 JSON、脚本注入和中文歧义表头增加回归测试。

### 验证

- 22 个领域适配器、112 个路由信号、97 个记录合同。
- 132 个明确标记为非金标准的合成路由案例。
- 11 个覆盖全部适配器的真实来源案例目录，仍不冒充人工裁决金标准。
- 30 项确定性对抗测试全部通过。
## 4.6.9

- 定义 `output-field-aliases.json` 与结构 Schema，明确 canonical 输出接口和旧结果兼容边界。
- 新增 `scripts/normalize_output.py`，旧假设/验证计划字段可确定性映射到 viewer，且不伪造 evidence ID。
- viewer 支持旧结果的兼容阅读，显示支持证据文本、反证、falsifier、实验标题、预期结果和判定规则，并保留原始 JSON 导出。
- 增加 `result(3).json` alias 回归测试；严格 4.6 校验器仍不接受旧合同。
## 4.6.10

- 结果/参照图卡增加键盘可访问的“查看记录详情”入口，展示原始记录、条件、来源和证据引用。
- 文件加载支持页面级拖拽，避免文件被浏览器直接打开；继续保留点击选择和格式/大小提示。
- 增加 viewer 交互回归检查。
## 4.6.11

- 新增单篇文献 `literature-first` 用户工作流，明确从上传文献到报告、source dashboard、结果 JSON 和后续实验的使用路径。
- 增加可直接复制的单篇文献请求模板，并要求 Agent 在最终交付中说明阅读顺序、证据边界和后续接入方式。
