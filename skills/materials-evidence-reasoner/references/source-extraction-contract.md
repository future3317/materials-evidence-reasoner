# Source Extraction Contract 1.0

本合同定义“文献/文档先经过运行环境处理，再进入材料证据推理”的边界。它不负责判断机理、材料身份或因果关系；它负责把原始文件转换为可被 Agent 阅读和回查的中间资产。

## 1. 入口

在 PDF、XML/JATS、HTML、DOCX、XLSX 或补充 CSV/TSV/JSON 进入抽取阶段时，先运行：

```bash
python scripts/extract_sources.py --check-environment
python scripts/extract_sources.py <input-or-directory> --output source-extraction
```

环境报告必须保留 Python 可执行路径、库版本、PDF 后端、OCR/图像导出开关、外部工具和缺失依赖。不要把“机器上装过某包”写成“该包已经成功抽取当前文件”。

## 2. 后端选择

| 输入 | 默认后端 | 降级/显式后端 | 主要产物 |
|---|---|---|---|
| PDF | Docling | PyMuPDF → pdfplumber | 带页码锚点的 Markdown、结构 JSON、表格 CSV |
| XML/JATS/TEI | lxml 安全解析器（关闭外部实体/网络） | 失败则记录 failed，不猜测 | 标题、摘要、章节、表格、图注、参考文献 |
| HTML | BeautifulSoup | 纯文本仅作为受限降级 | 标题、章节、表格 |
| DOCX | python-docx | manifest-only | 段落、标题、表格；`--extract-figures` 时增加嵌入图像 |
| XLSX | openpyxl | `prepare_intake.py` 仍保留原值/公式盘点 | 工作表表格、表头、公式与缓存值、隐藏行列和合并单元格提示 |
| CSV/TSV | Python `csv` 标准库 | 记录编码和分隔符 | 原始表头、行和表格锚点 |
| JSON | Python `json` 标准库 | 结构无法转成对象数组时保留格式化文本 | 每个对象数组分别导出为表格，或保留格式化 JSON 块 |

PDF 默认优先布局感知抽取，因为材料论文的双栏、表格、图注和扫描页不能只靠普通文本拼接。需要严格离线、已知是 born-digital PDF 或只做快速预览时，可使用：

```bash
python scripts/extract_sources.py paper.pdf --pdf-backend pymupdf --output source-extraction
```

Docling 的默认 PDF profile 在首次运行时会自动尝试下载当前 profile 必需的 layout 与 table-structure 模型；启用 `--ocr` 且环境有 RapidOCR/onnxruntime 时，还会准备 RapidOCR 中文模型。模型缓存默认使用 Docling 的 `cache/models`，也可用相对的 `--model-cache .cache/docling-models` 指定环境缓存；缓存位置只属于复现信息，不是用户 artifact 路径。`source-extraction.json` 的 `policy.model_download` 和 `environment.model_cache` 必须记录状态、缺失模型、是否下载及失败原因。需要严格离线时使用 `--no-model-download`，模型缺失时 `auto` 会尝试 PyMuPDF/pdfplumber 回退；显式 `--pdf-backend docling` 则保留失败状态，不把不完整结果写成完整抽取。`--force-model-download` 用于修复或重建当前 profile 缓存。

OCR 通过 `--ocr` 显式开启，默认关闭，避免把 OCR 结果误当作原始文字。这里的 OCR 仅由 Docling 后端执行；显式使用 `--pdf-backend pymupdf` 或 `pdfplumber` 时，`--ocr` 不会静默生效，bundle 会记录警告。扫描 PDF 的 OCR 文本需要降低直接性并回看原页；默认无 OCR 且没有可提取内容时，bundle 会明确提示这一缺口。需要提取 Docling 识别到的图像时，追加 `--extract-figures`；这会生成 `figures/*.png`，但仍不替代原页核对。

需要人工核对双栏、图注、扫描页或表格版式时，再开启页面渲染：

```bash
python scripts/extract_sources.py paper.pdf --render-pages --output source-extraction
```

页面 PNG 是视觉 QA 辅助，不是新的证据来源；默认不生成，以免普通文献批处理产生过大的中间目录。

## 3. 来源锚点

所有提取内容必须能回到原始文件：

- PDF 使用 `source_id:page=N:item=...`；
- XML 使用 `source_id:section=...`、表格/图注/参考文献 ID；
- HTML/DOCX/XLSX 使用章节、表格、工作表或对象 ID；DOCX 的正文阅读顺序和可选嵌入图像会保留到结构 JSON/Markdown；
- 原始文件路径、SHA-256 和提取环境保存在 `source-extraction.json`；
- 环境报告包含 profile 状态、后端顺序和建议命令；文件 manifest 包含 `review_status`、内容信号和 `recommended_actions`，用于交接“可读/需复核/输入错误”；
- Markdown 是给 Agent 阅读的呈现层，结构 JSON 和 CSV 是机器检查层，原始文件仍是唯一来源。
- Docling PDF 额外保留 `reading_order`、`section_anchor` 和图像路径，使双栏正文、表格、图注不会在 Markdown 中被重新拼成无序文本。

提取文本中出现的数值、单位、样本量、误差、图表关系和协议只能先登记为候选内容。XLSX 公式不会被执行；公式单元格保留 `formula` 与 `cached_value`，缓存缺失时不能把公式结果当作观测值。Agent 仍需把事实绑定到 `source`、`evidence`、实体、条件和定位；表格/图像没有被成功提取时，不得用正文摘要补成图表事实。

## 4. 失败与继续规则

- 单个文件转换失败时保留 manifest、错误和环境信息；同批其他文件仍可继续处理。
- 只有当决策必须依赖该文件且没有可用替代证据时，提取失败才升级为 blocker。
- PDF fallback 只能降低布局/表格置信度，不能被写成等价于 Docling 的完整抽取；即使读到了文字，只要存在 PDF 级转换警告，manifest 也标为 `partial`。
- XML 解析失败不能回退到无锚点的自由文本并声称结构已保留。
- 转换工具不执行输入中的宏、JavaScript、外部实体或远程内容；不使用网络检索替代缺失的原始文件。

## 5. 交给 Agent 的最小上下文

按需加载：

1. `source-extraction.json` 的环境、策略和文件级摘要；
2. 目标文献的 `documents/IN-xxxx.md`；
3. 只在需要核对表格时加载对应 `tables/IN-xxxx-Txxx.csv` 或结构 JSON；
4. 需要查看图注/图片时加载 `figures/*.png` 或 `pages/*.png`；
5. 回查争议数值时打开原始文件并核对页码/章节/图表，而不是只看转换 Markdown。

不要把整个文献目录和所有领域 adapter 一次性装入上下文。提取工具负责结构和定位，Skill 负责条件、证据等级、可比性、误差和机制推理。
