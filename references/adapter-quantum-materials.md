# Quantum Materials Adapter

适配器：`quantum-materials`　层级：`phenomenon`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: quantum-materials -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `quantum-materials` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `qmat-emergent-phase` / emergent quantum phase | `量子自旋液体`、`重费米子`、`莫特绝缘体`、`量子临界点`、`近藤晶格`、`quantum spin liquid`、`heavy fermion`、`Mott insulator`、`quantum critical point`、`Kondo lattice`、`QSL`、`QCP` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `qmat-topological` / topological electronic phase | `拓扑绝缘体`、`外尔半金属`、`狄拉克半金属`、`量子反常霍尔`、`量子自旋霍尔`、`topological insulator`、`Weyl semimetal`、`Dirac semimetal`、`quantum anomalous Hall`、`quantum spin Hall`、`QAHE`、`QAH`、`QSH` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `qmat-quantized-transport` / quantized electronic transport state | `量子霍尔效应`、`舒勃尼科夫-德哈斯振荡`、`朗道能级量子化`、`分数量子霍尔`、`quantum Hall effect`、`Shubnikov-de-Haas oscillation`、`Landau level quantization`、`fractional quantum Hall`、`QHE`、`SdH`、`FQHE` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `qmat-signature` / quantum-state signature | `拓扑不变量`、`贝里相位`、`边缘态`、`表面态`、`非费米液体`、`莫尔关联态`、`topological invariant`、`Berry phase`、`edge state`、`surface state`、`non-Fermi liquid`、`moiré correlated state` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `qmat-generic` / generic quantum vocabulary | `量子`、`自旋`、`能带反转`、`低温异常`、`关联`、`quantum`、`spin`、`band inversion`、`low-temperature anomaly`、`correlated` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `qmat-other-quantum` / non-material quantum use | `量子化学方法`、`量子效率`、`量子产率`、`量子计算机`、`仪器量子极限`、`quantum chemistry method`、`quantum efficiency`、`quantum yield`、`quantum computer`、`instrument quantum limit` | 用于排除或消歧；有效语境：method-name、device-metric、photochemistry、instrument |

**歧义词消解**

- `quantum`：候选含义为 emergent material state / calculation method / optical efficiency/yield / instrument principle。判定规则：The word alone is weak; require a named phase/signature and target-bound evidence.
- `topological`：候选含义为 electronic topology / geometric morphology / network topology。判定规则：Require an electronic/magnetic invariant, state, or corresponding probe.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a named quantum phase or topological class is a target-bound result with measurement or calculation evidence
  - multiple probes or a probe-plus-model constrain an ordered state, excitation, topology, coherence, or phase diagram
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`superconductivity`, `two-dimensional-materials`, `electrical-magnetic-transport`, `spectroscopy`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: quantum-materials -->

## 1. 范围与路由

适用于强关联电子、拓扑相、量子磁性、自旋液体、重费米子、低维量子态、莫尔量子体系、量子临界、多铁和相关涌现现象。量子计算软件、量子化学方法或泛称“quantum effect”不自动触发材料适配器。

- `load`：文章以目标实体的量子相、序参量、激发、输运、拓扑、相干或相图为中心，并有结果级测量或明确计算证据。
- `candidate`：仅有理论可能性、背景词、单一模糊异常、实体未绑定或访问内容不足。
- `skip`：量子仅指计算方法、仪器原理、普通能级描述、被引材料或非目标器件。

超导由独立 `superconductivity` 适配器处理；量子材料适配器可以与其并行加载，但不能重复生成超导数值。

## 2. 目标实体与控制变量

解析 `bulk-crystal`、`thin-film`、`heterostructure`、`device`、`domain`、`defect-center`、`surface-state`、`edge-state`、`magnetic-phase`、`electronic-phase`。

必须保存：化学计量、缺陷/掺杂、同位素、晶体对称性、维度、畴、样品质量、取向和器件几何。温度、磁场矢量、压力、应变、电场/栅压、电流、频率、冷却/扫描历史属于状态定义，不是可选附注。

## 3. 记录类型

### `quantum-material-state`

字段：

- `phenomenon_classes`、`dimensionality`、`crystal_symmetry`、`relevant_symmetries`；
- `stoichiometry_property_ids`、`doping_property_ids`、`defect_property_ids`、`isotope_state`；
- `domain_state`、`sample_quality_property_ids`、`orientation`；
- `control_parameter_signature`、`phase_labels`、`phase_boundary_property_ids`。

### `ordered-state-assessment`

字段：

- `order_type`、`order_parameter`、`broken_or_preserved_symmetries`；
- `transition_property_ids`、`hysteresis_property_ids`；
- `correlation_length_property_ids`、`domain_property_ids`；
- `supporting_measurement_run_ids`、`competing_order_ids`；
- `evidence_convergence`、`alternative_explanations`。

### `excitation-and-quasiparticle`

字段：

- `excitation_type`、`dispersion_artifact_ids`；
- `gap_property_ids`、`linewidth_property_ids`、`lifetime_property_ids`；
- `effective_mass_property_ids`、`mobility_property_ids`；
- `momentum_or_real_space`、`selection_rules`、`model_dependence`；
- `measurement_run_ids`、`simulation_job_ids`。

### `topological-assessment`

字段：

- `topological_class_claimed`、`topological_invariant`、`invariant_method`；
- `symmetry_assumptions`、`band_inversion_evidence`；
- `surface_or_edge_state_evidence`、`spin_texture_evidence`；
- `berry_phase_property_ids`、`berry_curvature_property_ids`；
- `transport_signatures`、`spectroscopic_signatures`；
- `theory_experiment_alignment`、`trivial_alternatives`、`assessment_level`。

`assessment_level` 使用 `predicted`、`candidate`、`supported`、`multi-probe-supported`、`disputed`；不得由单一异常自动升级。

### `quantum-coherence-dynamics`

字段：`coherence_type`、`coherence_time_property_ids`、`relaxation_time_property_ids`、`dephasing_channels`、`drive_protocol`、`non_equilibrium_state`、`time_resolution`、`control_fidelity_property_ids`。

### `quantum-phase-diagram`

字段：`control_axes`、`phase_regions`、`boundary_property_ids`、`critical_point_property_ids`、`scaling_exponents_property_ids`、`interpolation_or_fit`、`measured_or_inferred_regions`、`missing_regions`。

## 4. 多探针证据

常见互补证据包括输运、磁化、热容、ARPES、STM/STS、光谱、X 射线/中子散射、NMR、muSR、Mossbauer 以及第一性原理或多体计算。记录每个探针真正约束的对象，避免把结构、磁序、体输运和表面态证据混为一个结论。

## 5. 硬审计

1. 不把理论预测写成实验发现。
2. 不把低温异常自动命名为量子相变。
3. 不省略场方向、取向、冷却与扫描历史。
4. 不把表面态、边缘态和体态证据互相替代。
5. 不以单一拟合指数证明量子临界性。
6. 不以材料家族声誉证明拓扑、强关联或自旋液体状态。
7. 保留竞争解释、阴性观测和探针之间冲突。

## 6. 规范依据

- DOE Basic Research Needs for Quantum Materials: https://science.osti.gov/-/media/bes/pdf/reports/2016/BRN_Quantum_Materials_for-Energy_Relevant_Technology.pdf
- NIST quantum transport measurements: https://www.nist.gov/programs-projects/quantum-transport-measurements
- ORNL quantum materials and neutron probes: https://www.ornl.gov/content/quantum-materials
