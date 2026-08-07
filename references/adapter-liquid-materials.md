# Liquid Materials Adapter

适配器：`liquid-materials`　层级：`physical-form`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: liquid-materials -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `liquid-materials` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `liq-composition` / target liquid composition | `离子液体`、`熔盐`、`液态金属`、`混合溶剂`、`电解液配方`、`ionic liquid`、`molten salt`、`liquid metal`、`mixed solvent`、`electrolyte formulation` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `liq-state-property` / liquid state or transport property | `液液平衡`、`黏度`、`流变`、`表面张力`、`蒸气压`、`liquid-liquid equilibrium`、`viscosity`、`rheology`、`surface tension`、`vapor pressure` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `liq-dispersion` / dispersion or slurry state | `分散稳定性`、`浆料`、`沉降`、`Zeta 电位`、`dispersion stability`、`slurry`、`sedimentation`、`zeta potential` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `liq-generic` / generic liquid vocabulary | `溶液`、`溶剂`、`液体`、`电解液`、`熔体`、`solution`、`solvent`、`liquid`、`electrolyte`、`melt` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `liq-incidental-fluid` / incidental fluid | `清洗溶剂`、`水浴`、`传压介质`、`载液`、`浸油`、`仅作测试环境而未研究的电解液`、`cleaning solvent`、`water bath`、`pressure medium`、`carrier liquid`、`immersion oil`、`electrochemical test electrolyte not studied` | 用于排除或消歧；有效语境：cleaning、apparatus、environment、sample-preparation-only |

**歧义词消解**

- `solution`：候选含义为 target formulated liquid / temporary preparation medium / mathematical solution。判定规则：Require a liquid entity with composition, state, process, or property evidence.
- `electrolyte`：候选含义为 target liquid material / battery component / electrochemical environment / solid electrolyte。判定规则：Route liquid form here and co-load application/measurement adapters as appropriate; solid electrolytes do not load this adapter.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - target liquid formulation or phase state is explicitly resolved
  - a target-bound liquid thermophysical, transport, interfacial, or stability result is reported
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`battery`, `electrochemical-testing`, `composition-particle-surface`, `thermal-analysis`, `polymers`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: liquid-materials -->

## 1. 范围与路由

适用于纯液体、溶液、混合溶剂、电解液、离子液体、熔盐、液态金属、液晶、浆料和稳定/不稳定分散液。液体只是清洗剂、传压介质、浴液或非目标环境时不自动加载。

- `load`：液体组成、制备、状态、界面或热物性/输运性质属于目标结果。
- `candidate`：液体仅以简称、商品名或未解析“solution/electrolyte/melt”出现。
- `skip`：仅为设备介质、清洗/安装耗材、背景或被引体系。

“液体”是物态层，可与聚合物、电池、电化学、能源或金属适配器同时加载。

## 2. 目标实体与快照

解析 `pure-liquid`、`mixture`、`solution`、`electrolyte`、`dispersion`、`slurry`、`molten-salt`、`liquid-metal`、`liquid-crystal`、`interface`。

组分比例、水/氧、温压、相态、干燥、脱气、搅拌、储存、老化、沉降和污染变化时生成新配方实体或快照。

## 3. 记录类型

### `liquid-composition-state`

字段：

- `liquid_subtype`、`component_entity_ids`、`component_roles`；
- `composition_basis`、`composition_property_ids`；
- `purity_property_ids`、`water_property_ids`、`oxygen_property_ids`、`impurity_property_ids`；
- `preparation_process_run_ids`、`drying_history`、`degassing_history`；
- `homogeneity_state`、`equilibration_time`、`storage_history`。

摩尔分数、质量分数、体积分数、质量摩尔浓度和物质的量浓度不可静默互换。

### `liquid-phase-state`

字段：

- `phase_identity`、`phase_count`、`phase_boundary_property_ids`；
- `temperature`、`pressure`、`atmosphere`；
- `supercooling_or_superheating`、`metastability`；
- `container_or_crucible`、`container_compatibility`；
- `visual_state`、`precipitation`、`gas_evolution`、`aging_time`。

### `dispersion-state`

字段：

- `dispersed_phase_entity_ids`、`continuous_phase_entity_ids`；
- `concentration_property_ids`、`particle_size_property_ids`、`zeta_potential_property_ids`；
- `surfactant_or_stabilizer`、`mixing_or_sonication_process_run_ids`；
- `sedimentation_property_ids`、`stability_window`、`sampling_position`。

### `liquid-crystal-state`

字段：`mesophase`、`transition_temperature_property_ids`、`alignment_method`、`field_conditions`、`texture`、`birefringence_property_ids`、`dielectric_anisotropy_property_ids`。

### `liquid-metal-state`

字段：`alloy_composition_property_ids`、`oxygen_activity_property_ids`、`oxidation_state`、`crucible_material`、`wetting_property_ids`、`superheat`、`solidification_history`。

## 4. 性能及条件

- 密度、黏度、流变、扩散、电导、热导、热容、表面/界面张力、蒸气压、介电、折射和溶解度数值进入核心性能记录。
- 每个值绑定组成、温度、压力、相态、测量方法和不确定度。
- 流变记录剪切历史、剪切速率/应力、频率、应变、几何和稳态判据。
- 电解液输运区分总电导、离子电导、扩散系数和迁移数及其模型。
- 接触角/润湿记录固体表面、粗糙度、清洁、液滴体积、气氛、时间和拟合模型。

## 5. 硬审计

1. 不以名称相同认定配方相同。
2. 不省略水、氧、纯度和制备历史对敏感液体的影响。
3. 不把外观均一写成热力学单相。
4. 不把不同组成基准和参考态的性质直接合并。
5. 不忽略容器、气氛、蒸发和时间依赖。
6. 不把拟合得到的输运参数写成直接观测。

## 6. 规范依据

- NIST ThermoML: https://www.nist.gov/mml/acmd/trc/thermoml
- IUPAC ThermoML: https://iupac.org/what-we-do/digital-standards/thermoml/
- NIST ILThermo: https://www.nist.gov/mml/acmd/trc/ionic-liquids-database
