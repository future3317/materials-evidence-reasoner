# 材料实验推理报告

## 一句话结论

The local result is lower under matched nominal conditions; surface re-oxidation is the leading testable explanation, but contamination remains plausible.

- 决策状态：`partially-answerable`
- 证据强度：`medium`
- 可比性/偏差状态：`material-process-deviation`

## 现在该做什么

1. **Run a paired, approved surface-recovery intervention with untreated and clean-handling controls, then repeat the same CE protocol.**
  - 优先级：`high`；理由：One paired intervention and two measurements address both leading chains while keeping Cond-A fixed.
  - 关闭信息缺口：IG1, IG2
  - 预期决策变化：Can upgrade one surface-state pathway, reject both, or stop material optimization and return to data-quality review.
  - 判定规则：Upgrade H1 only if the paired intervention restores the surface indicator and CE beyond repeat variability while the clean-handling control does not explain the change.
  - 停止规则：Stop mechanism escalation if measurement repeatability is inadequate or neither surface state nor resistance changes with the intervention.
  - 安全：Follow the existing laboratory SOP and SDS; no executable treatment parameters are supplied.

## 输入完整度与缺失信息

输入状态：`ready-with-caveats`；已规范化对象数：6。

### 必须补充

无。

### 会限制结论

- **surface_composition**：No direct surface chemistry measurement is available. 影响：Oxidation and contamination cannot yet be separated. 最小补充：Run a paired surface-sensitive measurement before and after the recovery treatment.

### 可选增强

无。

## 条件对照表

| 条件 | 说明 | 完整签名 | 缺失条件 |
|---|---|---|---|
| [Cond-A] | Matched high-rate CE condition | `{"current_density_mA_cm2": 5.0, "electrolyte": "matched", "normalization": "coulombic efficiency percent", "temperature_C": 25}` | 无 |

## 基准、可比性与偏差

- `literature-prior` / `reference-case`：coulombic_efficiency；适用范围：Cond-A only；统计/趋势：{"reference_value": 95.6, "unit": "%"}；限制：Single synthetic reference case; no population distribution.
- 可比性 `comparable`：未登记差异项
- 偏差 `material-process-deviation`；方法：Direct difference against a single matched reference case.；残差：-3.1 percentage points；工程意义：A notable negative difference that requires verification; statistical significance is not claimed.

## 误差预算

### EB1：variance-components

- 结论：Known repeatability and the synthetic uncertainty budget do not explain the full observed effect; between-batch uncertainty remains a limitation.
- 效应与不确定度：`uncertainty-smaller`；The synthetic 3.1 percentage-point effect is materially larger than the 0.40-point expanded uncertainty estimate.
- 主导来源：EC2, EC4

| 分量 | 类别 | 估计状态 | 贡献基础 | 贡献比例 | 限制 |
|---|---|---|---|---:|---|
| Within-run CE repeatability | `measurement-repeatability` | `quantified` | `variance` | 20.0% | 无 |
| Sample heterogeneity | `sample-within-batch` | `bounded` | `variance` | 30.0% | Not independently identified from n=3 repeats. |
| Handling/exposure variation | `process-control` | `qualitative` | `variance` | 20.0% | Synthetic allocation; no process-control log. |
| Unallocated between-run/batch contribution | `unallocated` | `qualitative` | `variance` | 30.0% | Only one synthetic batch is available. |
- 局限：Synthetic variance allocation; not a metrology-grade uncertainty statement.；Only one batch is represented.

## 异常传播链

### 1. Exposure-driven surface-state pathway

- 传播路径：The sample experienced air exposure before testing. [observed] → Surface oxide coverage increased. [hypothesized] → Interfacial resistance increased. [hypothesized] → Coulombic efficiency decreased under Cond-A. [observed]
- 状态：`leading`；排序理由：The path fits the reported exposure and observed CE change, but two mediator nodes are unmeasured.
- 未解决节点：C1N2, C1N3
- 证据缺口：Surface chemistry；Interfacial resistance
- C1N1 → C1N2：Air exposure can alter the surface state.（证据 `indirect`；falsifier：Surface-sensitive analysis shows no change relative to a fresh control.）
- C1N2 → C1N3：A changed surface layer may increase interfacial transport resistance.（证据 `none`；falsifier：Matched EIS shows no interfacial resistance change.）
- C1N3 → C1N4：Higher interfacial resistance can reduce plating/stripping efficiency.（证据 `inferred`；falsifier：CE remains low despite restored interfacial resistance.）

### 2. Handling-contamination pathway

- 传播路径：Sample handling may have introduced contamination. [hypothesized] → Contaminant coverage blocked active interface area. [hypothesized] → Coulombic efficiency decreased under Cond-A. [observed]
- 状态：`candidate`；排序理由：The chain is simple and testable but currently lacks direct supporting evidence.
- 未解决节点：C2N1, C2N2
- 证据缺口：Contamination identity and coverage
- C2N1 → C2N2：Handling contamination may cover active interface sites.（证据 `none`；falsifier：Surface assay and clean-handling control exclude contamination.）
- C2N2 → C2N3：Blocked interface area may lower plating/stripping efficiency.（证据 `inferred`；falsifier：Cleaning changes contamination marker without improving CE.）

## 证据约束机理图谱

### MG1：Synthetic Ion-Cu exposure and efficiency mechanism graph

- 材料体系：Ion-Cu sodium plating interface；版本：`1.0`；状态：`draft`
- 适用条件：COND-A；边界：Synthetic fixture only.；Ion-Cu under Cond-A.；Pre-test handling is part of the regime.
- 来源类型：combined, domain-inference；更新提案：MU1
- pre-test air exposure → altered surface coverage：Air exposure may alter the surface chemical state. （`hypothesis`；证据 E3；迁移 `same-regime`；falsifier：Surface-sensitive analysis shows no difference from a fresh control.）
- altered surface coverage → surface-layer transport impedance：A changed surface layer may create an interfacial transport barrier. （`hypothesis`；证据 E2, E3；迁移 `same-regime`；falsifier：Matched transport measurements show no change after exposure.）
- surface-layer transport impedance → interfacial resistance：The transport barrier may increase interfacial resistance. （`hypothesis`；证据 E2, E4；迁移 `same-regime`；falsifier：Matched EIS or equivalent analysis shows no resistance difference.）
- interfacial resistance → coulombic efficiency：Higher interfacial resistance may reduce plating/stripping efficiency. （`hypothesis`；证据 E1, E2, E4；迁移 `same-regime`；falsifier：CE remains low after resistance is restored or matched.）
- 局限：Surface chemistry and interfacial resistance are not directly measured.

## 机理假设排序

### 1. Surface re-oxidation increased interfacial resistance and reduced CE.

- 状态：`plausible`
- 传播链：CHAIN1
- 机理图谱匹配：`partial-condition-match`；边：ME1, ME2, ME3, ME4
- 迁移边界：{"known_mismatches": [], "level": "same-regime", "rationale": "Only the synthetic Ion-Cu regime under Cond-A is considered.", "required_matches": ["material system", "surface handling", "cell architecture", "measurement protocol"]}；检索说明：Matched by material system, handling state, and CE endpoint; two mediator nodes remain unmeasured.
- 支持证据：E3
- 反证：未提供
- 独有预测：A controlled surface-recovery intervention should restore both surface indicator and CE.
- 反证条件：CE remains low after validated surface recovery while contamination is excluded.
- 适用边界：Local Ion-Cu under Cond-A.

### 2. Contact contamination reduced CE independently of oxidation.

- 状态：`speculative`
- 传播链：CHAIN2
- 机理图谱匹配：`no-match`；边：无
- 迁移边界：{"known_mismatches": [], "level": "not-assessed", "rationale": "No reusable graph edge currently represents the contamination alternative.", "required_matches": []}；检索说明：No graph match; retain as a run-scoped competing hypothesis.
- 支持证据：无直接证据
- 反证：未提供
- 独有预测：Cleaning without changing oxidation state should improve CE.
- 反证条件：A clean-handling control remains low while oxidation recovery restores CE.
- 适用边界：Local sample handling.

## 信息缺口

| ID | 未知量 | 层级 | 影响 | 当前状态 | 最小测量 | 决策用途 | 处置 |
|---|---|---|---|---|---|---|---|
| IG1 | Surface chemical state and contaminant identity | `structure` | `high` | `unmeasured` | XPS or a validated equivalent available to the laboratory | A coupled surface-state and CE recovery supports H1; contamination change without oxide change supports H2. | `plan-measurement` |
| IG2 | Interfacial resistance under matched cell state | `properties` | `medium` | `unmeasured` | EIS or a validated equivalent | No resistance difference weakens the middle link in H1. | `plan-measurement` |

## 最小实验集与验证方案

### SET1：Resolve the minimum surface-state and resistance information needed to choose between H1 and H2.

- 选择理由：A single paired design covers two high-value unknowns and avoids unconstrained process optimization.
- 覆盖 gap：IG1, IG2；实验：V1
- 资源：One approved intervention workflow, paired surface analysis, matched EIS, and repeated CE.
- 停止规则：Stop if the paired design cannot preserve Cond-A.；Stop if expected decision value is lower than sample or external-service cost.

### V1：Run a paired, approved surface-recovery intervention with untreated and clean-handling controls, then repeat the same CE protocol.

- 区分假设：H1, H2；关闭 gap：IG1, IG2
- 最小变化：Change only surface recovery/handling while keeping Cond-A fixed.
- 对照：Untreated exposed sample；Fresh reference；Clean-handling control
- 重复数：3
- 预期：Oxidation hypothesis: surface indicator and CE recover together.；Contamination hypothesis: cleaning improves CE without oxidation change.
- 判定规则：Upgrade H1 only if the paired intervention restores the surface indicator and CE beyond repeat variability while the clean-handling control does not explain the change.
- 停止规则：Stop mechanism escalation if measurement repeatability is inadequate or neither surface state nor resistance changes with the intervention.
- 可执行性：`not-confirmed`；成本档：`medium`；样品消耗：Three paired groups with three repeats each.
- 风险：Requires approved handling and no unreviewed chemical procedure.；安全：Follow the existing laboratory SOP and SDS; no executable treatment parameters are supplied.

## PSPP 经验图与更新

### PSPP1：Synthetic exposure–surface state–interfacial property–CE map

- 状态：`draft`；覆盖：{"material_attributes": "present", "performance": "present", "processing": "present", "properties": "missing", "structure": "present"}
- processing → structure：Exposure history may change surface chemistry.（`hypothesis`；falsifier：Surface chemistry matches fresh reference.）
- structure → properties：A changed surface layer may increase interfacial resistance.（`hypothesis`；falsifier：Matched EIS shows no resistance change.）
- properties → performance：Higher interfacial resistance may reduce CE.（`hypothesis`；falsifier：CE remains low after resistance is restored.）
- 缺失层：properties；局限：Relationships are hypotheses pending V1.

- `proposed-not-written`：Air exposure is associated with lower CE under Cond-A in this synthetic fixture; the structure and interfacial-property mediators remain unmeasured.；PSPP：PSPP1；机理图谱更新：MU1；边界：Synthetic fixture only.；复核触发：Update after V1 is executed.
  - 图谱操作说明：Propose support-edge update after the paired intervention; do not apply before validation evidence exists.
- Synthetic demonstration fixture; not a real scientific result.

## 交付与审计

- 机器记录：`synthetic-closed-loop.json`
- Schema：`4.6`
- JSON 验证：`tool-validated`
- machine-json: `synthetic-closed-loop.json`（validated）
- dashboard-html: `synthetic-closed-loop-dashboard.html`（validated）
- mechanism-nodes-csv: `synthetic-mechanism-nodes.csv`（not-validated）
- mechanism-edges-csv: `synthetic-mechanism-edges.csv`（not-validated）
- mechanism-graph-dot: `synthetic-mechanism-graph.dot`（not-validated）
