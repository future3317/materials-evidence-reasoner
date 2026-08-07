# Offline Materials Viewer 4.6.11 / Schema 4.6

`index.html` 是无网络依赖的通用查看器。

用法：

1. 双击打开 `index.html`；
2. 选择或拖入通过 4.6 Schema 校验的 `materials-result.json`；

viewer 也能以“兼容阅读”方式打开旧结果字段（例如 `title`、`supporting_evidence`、`experiment_id`），但顶部会明确标记旧格式，且不会把它显示成已通过 4.6 canonical 校验。正式交付仍需运行 `python scripts/validate_output.py result.json`。
3. 按概览页四步引导阅读：条件与可比性 → 结果/参照 → 偏差/误差与异常链 → 信息缺口/最小实验集。
4. 查看结果比较图、误差效应对照图、异常链逐边审计、实验 coverage matrix、证据约束机理图谱、机理假设、PSPP 多节点关系图、证据和缺失项。

机理图谱页支持图谱选择、状态筛选、文本检索、缩放以及节点/边证据审计；它只显示 JSON 中已经存在的关系，不自动补边、升级状态或跨材料迁移。

PSPP 页显示 material-attributes（如有）、Processing、Structure、Properties、Performance 的全部已登记节点；未知节点使用虚线边框，关系可以展开查看证据、反证、Falsifier 和边界。结构化记录页会显示 JSON 的全部顶层对象，便于核对呈现层是否漏掉数据。

也可以加载普通 CSV/TSV。查看器只显示原始表格，不执行材料语义判断或自动升级结论。

如果选择 JSON 后提示“文件可能被截断或字符串/数组未闭合”，请按提示的行号和列号检查原始文件；也可以先运行 `python -m json.tool materials-result.json`。查看器不会自动补全缺失的科研数据。读取器兼容 UTF-8 BOM 与 UTF-16LE/BE 文件。

生成已嵌入 JSON 的单文件仪表盘：

```bash
python ../scripts/render_dashboard.py materials-result.json -o materials-dashboard.html
```

安全边界：查看器不联网、不执行输入中的 HTML/JavaScript、不写回原始 JSON。误差预算的占比只在相同贡献基准下显示；`not-comparable` 结果不显示数值残差；任何结论都应回查底层证据记录。
