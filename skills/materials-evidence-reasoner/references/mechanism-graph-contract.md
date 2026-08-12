# Evidence-grounded Mechanism Graph Contract 4.6

本契约定义跨实验、跨文献复用的 **Mechanism Knowledge Graph（MKG）**。它不是百科知识图谱，也不是把模型常识写入数据库的通道；它只保存具有来源、条件、反证和版本的材料机制关系。

## 1. 与现有对象的边界

- `anomaly_propagation_chain`：一次偏差事件中的诊断路径，属于当前运行；允许存在未测节点和竞争链。
- `hypothesis`：针对当前实验的待检验解释；可检索并链接已有机制边，但链接不等于验证。
- `pspp_map`：某项经验的 Processing–Structure–Properties–Performance 快照，用于说明 know-how 的完整关系。
- `mechanism_graph`：跨运行保存的可复用机制层；边必须有证据、条件、falsifier、迁移边界和版本。
- `experience_update`：经验持久化提案；通过 `mechanism_update_ids` 提议图谱操作，不直接修改历史。

不得把运行内异常链直接复制为机制事实。只有完成实体、条件、证据和边界审查后，才可创建或更新 MKG。

## 2. 图谱对象

### 2.1 `mechanism_graphs[]`

图谱容器至少记录：

- `id`、`namespace`、`material_system`、`version`；
- `node_ids`、`edge_ids`；
- `condition_ids` 和自然语言 `boundary_conditions`；
- 来源类型、支持证据、关联 PSPP/异常链；
- `update_ids`、历史版本与限制。

图谱状态：

- `draft`：存在可复用结构，但关键边仍是假设；
- `evidence-backed`：边均有可追溯证据，但不一定被本地干预验证；
- `locally-validated`：至少一条关键边在明确 regime 内被干预支持；
- `conflicting`：存在未消解的正反证据；
- `deprecated`：不再用于新推理，但保留历史。

### 2.2 `mechanism_nodes[]`

节点类型：

`material-attribute | processing | structure | mechanism | property | performance | measurement | context`

`mechanism` 节点表示中间物理/化学过程，例如扩散受限、位错钉扎、界面副反应；不能用它代替所有结构或性质节点。

节点状态：

`observed | reported | derived | hypothesized | supported | locally-validated | contradicted | deprecated | conflicting`

### 2.3 `mechanism_edges[]`

每条边必须包含：

- 起点、终点与关系类型；
- `mechanism_description`；
- `support_evidence_ids`，至少一条；
- 冲突证据与本地验证证据；
- 适用条件、边界、falsifier；
- 来源类别和 `validation_status`；
- `transferability`；
- 版本、被替代边和局限。

状态含义：

- `reported`：原始来源明确报告该关系，但本 Skill 不替来源证明因果；
- `hypothesis`：当前证据支持候选关系，仍需验证；
- `supported`：多个匹配证据支持，但缺少足够本地干预；
- `locally-validated`：在明确材料、工艺、设备和测试边界内被干预支持；
- `contradicted/conflicting`：反证存在；
- `deprecated`：历史边不再用于默认检索。

`domain-inference` 来源的边必须保持 `hypothesis`。通用知识不能直接升级为 `reported`、`supported` 或 `locally-validated`。

## 3. 条件化检索与迁移

Stage 6 生成假设前，先检索 MKG，并按以下顺序使用：

1. 相同材料实体或同一 `regime_id`、关键条件匹配的本地验证边；
2. 同材料体系、条件部分匹配的文献或本地支持边；
3. 同材料族的类比；
4. 跨材料体系的领域推断。

假设必须记录：

- `linked_mechanism_edge_ids`；
- `mechanism_match_status`；
- `mechanism_transferability`；
- `boundary_conditions`；
- `graph_retrieval_notes`。

迁移等级：

- `same-regime`；
- `same-material-family`；
- `cross-material-proposed`；
- `not-assessed`；
- `not-transferable`。

跨材料类比只能用于提出假设；必须列出需要匹配的物理量、结构尺度、主导机制和已知不匹配条件。

## 4. 图谱更新治理

`mechanism_updates[]` 允许：

- `append-node`、`append-edge`；
- `support-edge`、`add-conflict`；
- `revise-boundary`；
- `supersede-edge`、`deprecate-edge`；
- `split-graph`、`merge-proposal`；
- `no-change`。

规则：

1. 新实验不静默覆盖旧边；边界改变时创建新版本或 supersede。
2. 否定结果标记冲突或废弃，保留原证据和历史。
3. `split-graph` 与 `merge-proposal` 必须人工审查，配套脚本不自动应用。
4. 只有 `approved` 更新可由脚本写入新 artifact；写入后标记 `applied + artifact-written`。
5. 外部企业知识库只有在运行时确认写入后，才标记 `external-written-confirmed`。
6. 机制边的“证据数量”不是置信概率；重复发表、同一数据派生和非独立证据不得重复计权。

## 5. 与异常链、PSPP 和实验计划的连接

- 异常传播边可以通过 `linked_mechanism_edge_ids` 指向 MKG；未命中时保持运行内边。
- PSPP 关系可以链接 MKG，但 PSPP 的 observation 不因链接而自动升级为因果。
- `hypothesis` 的独有预测和 falsifier 应与链接机制边一致；冲突必须披露。
- 信息缺口应优先指向机制图中的未测节点、边界条件或竞争边。
- 最小实验集应说明它将支持、限制、冲突还是废弃哪条机制边。

## 6. 硬审计

发布前检查：

- 图、节点、边双向引用完整；
- 每条边有支持证据、边界和 falsifier；
- `locally-validated` 有本地验证证据；
- `contradicted/conflicting/deprecated` 有反证或 supersession；
- 跨材料迁移没有被伪装成已支持机制；
- 图谱匹配与当前实验的材料、工艺、尺度、测试条件一致；
- 图谱更新经过批准且写入状态真实；
- 仪表盘与报告不把假设边渲染成验证边；
- 输入文本不会作为 HTML/脚本执行。

配套命令：

```bash
python scripts/mechanism_graph.py summary materials-result.json
python scripts/mechanism_graph.py query materials-result.json --text "surface resistance"
python scripts/mechanism_graph.py export materials-result.json -o mechanism-export
python scripts/mechanism_graph.py index materials-result.json -o mechanism-index.json
python scripts/mechanism_graph.py diff old.json new.json -o mechanism-diff.json
python scripts/audit_mechanism_graph.py materials-result.json -o mechanism-audit.json --report mechanism-audit.md
```

只有明确批准的更新可写入新 artifact：

```bash
python scripts/mechanism_graph.py apply materials-result.json \
  --update-id MU-001 -o materials-result-updated.json
```
