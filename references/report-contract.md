# Report and Visualization Contract 4.6

## 1. 默认呈现原则

- 聊天正文优先服务实验人员决策，不展开完整 JSON。
- 一句话结论后立即给“现在该做什么”。
- 条件重复时使用 `[Cond-A]` 等别名；完整条件保留在 `condition_registry`。
- 专业术语第一次出现时附一句通俗解释。
- 关键事实均使用 `[S#:E#]`，派生值引用源证据和转换。
- 人类报告、JSON、CSV 和仪表盘必须由同一数据对象生成；任何呈现不得升级底层结论。
- 误差预算、异常传播链、Mechanism Graph 和 PSPP 图必须区分“直接观测、派生、假设、缺失”，不得用视觉样式掩盖证据等级。

## 2. 人类报告结构

1. 一句话结论；
2. 下一步行动，最多 3 项，并说明关闭哪个信息缺口；
3. 输入完整度、blocker 与缺失项；
4. 条件注册表；
5. 文献先验、本地基线、规格限值；
6. 数据质量、可比性、偏差和误差预算；
7. 异常传播链、未测节点和替代路径；
8. 证据约束机理图谱：匹配边、状态、适用条件、迁移边界、冲突和更新；
9. 机理排序及反证；
10. 信息缺口与最小实验集，包括 coverage matrix 和 stop rule；
11. PSPP 经验图、图谱更新提案、风险和局限。

没有内容的章节可以省略，但不得用空章节暗示已经完成审计。

## 3. 条件别名

`condition_registry[]` 的 `id` 使用 `COND-A`、`COND-B` 等稳定 ID，`alias` 使用 `Cond-A`、`Cond-B`。同一运行内：

- 相同条件签名复用同一别名；
- 任一关键条件不同必须使用不同别名；
- 条件未知时不得把两个运行合并为同一别名；
- 报告中出现别名时必须能在表中找到；
- 条件注册表变化后重新校验所有引用。

## 4. 误差预算呈现

- 先说明误差分析方法和重复结构，再显示主导来源。
- 只有在共同统计基础上才显示贡献百分比；否则显示 `quantified/bounded/qualitative/unavailable`。
- 同时展示观察效应、综合不确定度和二者关系：`uncertainty-smaller/comparable/uncertainty-dominates/unknown`。
- `unallocated` 必须可见；不能用已知分量填满 100% 来制造完整感。
- 仪表盘不得把标准差、置信区间、仪器精度和规格容差画在同一比例条上，除非底层 JSON 明确统一了统计含义。

## 5. 异常传播链与 PSPP 呈现

- 链条节点按阶段显示，但不强迫补齐不存在的节点。
- `observed/derived/hypothesized/missing` 使用文字标签和不同线型/边框，不只依赖颜色。
- 每条边可展开查看支持证据、反证、假设、falsifier 和边界。
- PSPP 固定为 Processing → Structure → Properties → Performance；`material-attributes` 作为可选上游节点。
- 未测节点显示为缺口，不能渲染成已确认结构或性质。
- `locally-validated` 只在底层关系对象明确为该状态时显示。


## 6. Mechanism Graph 呈现

- 图谱与运行内异常链分区展示；必须说明图谱是跨实验知识层。
- 节点按 material-attribute、processing、structure、mechanism、property、performance、measurement、context 分组。
- 边同时显示关系、`validation_status`、来源类型、条件、falsifier 与 transferability；状态不能只靠颜色。
- `hypothesis` 使用虚线或空心样式；`reported/supported/locally-validated` 使用不同文字标签；`contradicted/deprecated` 保留但默认弱化，不隐藏。
- 点击节点或边时展示证据 ID、冲突证据、验证证据、边界和版本。
- 跨材料 `cross-material-proposed` 必须显示“类比，不是已验证迁移”。
- 图谱更新以 proposed/reviewed/approved/applied 区分；查看器不得直接修改原始 JSON。
- 图布局只是导航，不代表因果强度、概率、贡献大小或时间尺度。

## 7. 信息缺口与最小实验集

- 每个建议先写“缺少什么”和“为什么影响决策”，再写测量方法。
- 显示 `impact`、影响的假设、最小测量、判定用途和 disposition。
- 实验优先级使用 `priority_tier` 与文字理由；没有效用/成本概率模型时不得显示伪精确分数。
- coverage matrix 应清楚表明实验覆盖哪些 gap 和假设。
- stop rule 与“不建议继续”必须与实验建议同等可见。

## 8. 文件交付

建议的 `artifact_manifest[]`：

- `human-report`: Markdown；
- `machine-json`: 完整 JSON；
- `evidence-csv`、`records-csv`、`deviations-csv`、`error-budget-csv`、`information-gaps-csv`；
- `dashboard-html`: 离线单文件；
- `mechanism-graph-json`、`mechanism-nodes-csv`、`mechanism-edges-csv`、`mechanism-graph-dot`、`mechanism-audit-report`；
- `plot` 或其他按需图表。

每项记录路径、生成状态、验证状态、内容说明和依赖的 JSON 版本。

## 9. 仪表盘规则

通用查看器必须：

- 离线读取本地 JSON/CSV，不调用网络；
- 默认显示结论、行动、缺失项、条件、偏差、误差预算、传播链、Mechanism Graph、机理、信息缺口、验证和 PSPP；
- 可展开来源、证据和原始记录；
- 对不可信字符串使用 `textContent` 或等价安全转义；
- 不执行输入中的 HTML、JavaScript、公式或宏；
- 对缺失字段显示“未提供/不适用”，不伪造 0；
- 显示 Schema 版本和验证状态；
- 当 `not-comparable` 时不绘制误导性的残差或材料异常链；
- 当结论为假设时不得用“已证实”视觉标签；
- 以 JSON 为审计源，仪表盘不允许写回或覆盖原始数据。
- 视觉采用清晰层级、充足留白、语义色、细分隔和克制材质；不得复制 Apple 商标、图标或品牌资产。
- 支持浅色/深色、键盘导航、可见焦点、200% 缩放、`prefers-reduced-motion`；透明材质必须有降低透明度/高对比回退。
- 动效只用于状态连续性，不得用弹跳、视差或持续运动装饰科学结论。

## 10. 术语速查

- `blocker`：不补就无法可靠继续的关键信息；
- `error_budget`：把已知误差来源、统计基础、未识别部分和总不确定度放在同一审计对象中；
- `anomaly_propagation_chain`：异常从数据/材料属性经工艺、结构、性质到性能的候选传播路径；
- `information_gap`：当前决策缺少的变量或判据；
- `experiment_set`：用最少实验覆盖关键未知和竞争假设的组合；
- `PSPP`：Processing–Structure–Properties–Performance；
- `mechanism_graph`：跨实验保存的证据、条件、反证和版本受控机制关系网络；
- `transferability`：某条机制边能否迁移到当前材料/工艺/尺度/测试条件的边界评估；
- `falsifier`：出现后会削弱或推翻某个解释的观测；
- `locally-validated`：只在当前材料、工艺和测试边界内被干预验证；
- `protocol-shift`：结果变化主要来自测试或处理协议变化；
- `literature_prior`：文献在特定条件下提供的先验参照。
