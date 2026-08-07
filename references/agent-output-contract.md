# Agent output contract 1.0

本文件解决“README 让 Agent 生成什么”和“SKILL/Schema 实际要求什么”之间的交接问题。README 是用户入口，SKILL 是执行规则，`references/output-schema.json` 是唯一的 canonical 字段合同；三者不能各自发明一套字段。

## 交付链

| 阶段 | Agent/脚本产物 | 是否是最终科学结论 |
|---|---|---|
| 输入盘点 | `intake-packet.json`、`intake-checklist.md` | 否，保留原始值和缺口 |
| 文献处理 | `source-extraction.json`、`documents/*.md`、`tables/*.csv`、`source-dashboard.html` | 否，提取中间资产；必须回查原文 |
| 主动学习盘点 | `active-learning-profile.json`、`.md`、`.html` | 否，区分候选池、模型推荐、代码来源和可复现性 |
| Agent 证据建模 | `materials-result.json` | 是可审计的 canonical 证据记录，但结论强度受证据等级限制 |
| 交付呈现 | `materials-report.md`、`materials-dashboard.html`、机制图导出/审计 | 否，全部从已验证 canonical JSON 派生 |

## `materials-result.json` 的最低要求

输出必须遵循 `references/output-schema.json`，其 root `required` 列出的数组/对象都必须出现。没有证据时使用空数组、`missing_information` 和 `quality` 说明缺失，不得删除字段或编造占位事实。至少保证：

1. `input_assessment` 记录收到的文件、路径、解析限制和 blocker/analysis-limiting/optional 缺口；
2. `sources` 和 `evidence` 绑定到原始文件与页/章节/图表锚点；
3. `entities`、`process_runs`、`measurement_runs`、`property_records` 只写有来源的实体、条件和测量；
4. `comparability_assessments` 先判断可比性，再决定是否能写偏差；不可比时不要补算残差；
5. `hypotheses`、`information_gaps`、`verification_plan`、`experiment_sets` 明确证据等级、反证条件、停止规则和资源边界；
6. `mechanism_*`、`pspp_maps`、`experience_updates` 只有在证据、边界、falsifier、版本和治理字段齐全时才升级状态；
7. `artifact_manifest` 列出每个生成文件的相对路径和来源 JSON；`quality.json_valid` 只有通过 `validate_output.py` 后才可写成 `tool-validated`。

## 串联命令

```text
python scripts/prepare_intake.py <input> --output intake-output
python scripts/extract_sources.py <papers-or-supplements> --output source-extraction
python scripts/profile_active_learning.py <active-learning-folder> --output active-learning-profile

# Agent 根据上述中间资产写 materials-result.json
python scripts/validate_output.py materials-result.json
python scripts/render_report.py materials-result.json -o materials-report.md
python scripts/render_dashboard.py materials-result.json -o materials-dashboard.html
python scripts/mechanism_graph.py export materials-result.json -o mechanism-export
python scripts/audit_mechanism_graph.py materials-result.json -o mechanism-audit.json --report mechanism-audit.md
```

没有本地实验时，`materials-result.json` 仍然可以是 literature-first 结果，但必须明确没有本地基线/复现实验；主动学习推荐必须保持 `proposed`/`model-derived`/`待实验验证`，不能写入已验证 `property_records`。
