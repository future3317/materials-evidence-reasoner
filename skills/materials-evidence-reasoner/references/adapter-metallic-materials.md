# Metallic Materials Adapter

适配器：`metallic-materials`　层级：`material-family`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: metallic-materials -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `metallic-materials` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `met-alloy-identity` / metal or alloy identity | `金属材料`、`金属试样`、`打印金属`、`合金牌号`、`钢号`、`高温合金`、`金属间化合物`、`金属玻璃`、`metallic material`、`metal specimen`、`printed metal`、`alloy grade`、`steel grade`、`superalloy`、`intermetallic`、`metallic glass`、`UNS` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `met-metallurgical-state` / metallurgical state or microstructure | `状态代号`、`奥氏体`、`马氏体`、`沉淀强化`、`再结晶`、`temper condition`、`austenite`、`martensite`、`precipitation hardened`、`recrystallized` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `met-heat-or-melt` / heat, melt, or product lineage | `炉号`、`熔炼批次`、`铸锭`、`轧板`、`锻棒`、`heat number`、`melt number`、`cast billet`、`wrought plate`、`forged bar` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `met-generic-metal` / generic metallic vocabulary | `金属`、`合金`、`箔`、`丝`、`钢`、`metal`、`alloy`、`foil`、`wire`、`steel` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `met-apparatus` / incidental metallic component | `样品架`、`铜导线`、`不锈钢夹具`、`集流体`、`金属基底`、`sample holder`、`copper wire`、`stainless-steel fixture`、`current collector`、`metal substrate` | 用于排除或消歧；有效语境：apparatus、sample-mounting、device-component |

**歧义词消解**

- `steel`：候选含义为 target engineering alloy / apparatus or structural support / figurative adjective。判定规则：Load only when the steel entity itself has composition, process, structure, or property evidence.
- `foil`：候选含义为 target metallic product / current collector / substrate or electrode component。判定规则：Resolve the foil role in the entity hierarchy.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - target metal/alloy identity plus a target-bound composition, process, microstructure, or property result
  - a target-bound metallurgical state is a study variable or conclusion
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`materials-processing`, `mechanical-testing`, `electron-microscopy-microanalysis`, `diffraction-scattering`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: metallic-materials -->

## 1. 范围与路由

适用于纯金属、工程合金、金属间化合物、高熵/多主元合金、金属玻璃及金属基复合材料。金属只是基底、集流体、电极支架、仪器部件或被引对照时不加载。

- `load`：目标实体的金属成分、制造/热机械历史、组织或金属性能是方法、结果或结论的重要对象。
- `candidate`：只出现牌号/元素名，目标实体不清，或全文不足以确认材料角色。
- `skip`：仅为设备、基底、容器、连接件、背景材料或他人工作。

不得从牌号或名义化学式自动填入实测成分、热处理状态、组织或性能。相同牌号但炉次、热处理、变形、取向或取样位置不同者拆分实体。

## 2. 目标实体

优先解析：`material`、`heat-or-melt`、`batch`、`feedstock`、`coupon`、`specimen`、`coating`、`weld-zone`、`phase`、`inclusion`。

以下变化通常生成新实体或快照：熔炼批次、粉末复用、铸态/锻态/轧态、固溶、时效、淬火、焊接区、增材构建方向、表面处理、辐照、腐蚀和测试后状态。

## 3. 记录类型

### `metallic-identity`

字段：

- `metallic_class`：`pure-metal`、`alloy`、`intermetallic`、`multi-principal-element-alloy`、`metallic-glass`、`metal-matrix-composite`、`unknown`；
- `grade_raw`、`grade_canonical`、`designation_system`；
- `nominal_composition_basis`、`measured_composition_available`；
- `heat_id`、`melt_id`、`batch_id_raw`；
- `matrix_phase`、`intended_phase_constitution`；
- `product_form`：板、棒、线、箔、粉、铸锭、锻件、焊件、涂层、增材件等；
- `supplier_state` 与 `certification_status`。

元素含量、杂质和偏析数值进入 `property_records[]`，保留原始计量基准，例如 wt%、at%、ppm、面积分数或局部探针结果。

### `metal-feedstock-state`

字段：

- `feedstock_form`、`supplier`、`lot_id`、`reuse_count`；
- `particle_morphology`、`size_distribution_property_ids`；
- `surface_condition`、`oxide_condition`、`moisture_or_oxygen_property_ids`；
- `flowability_property_ids`、`apparent_density_property_ids`；
- `sampling_method`、`storage_history`、`conditioning_history`。

### `metallic-microstructure-state`

字段：

- `phase_names`、`phase_fraction_property_ids`；
- `grain_morphology`、`grain_size_property_ids`、`grain_size_method`；
- `texture_description`、`texture_property_ids`、`reference_direction`；
- `precipitate_classes`、`precipitate_property_ids`；
- `inclusion_classes`、`inclusion_property_ids`；
- `porosity_property_ids`、`defect_classes`、`dislocation_density_property_ids`；
- `residual_stress_property_ids`、`surface_state`；
- `sampling_location`、`section_plane`、`orientation`、`statistics_scope`。

晶粒尺寸必须绑定测量方法、截面和分布；ASTM grain size number、平均截距和等效圆直径不能直接互换。相分数、孔隙率和夹杂率必须保存面积/体积/质量等基准。

### `metallurgical-state-assessment`

字段：

- `process_run_ids`；
- `temper_or_condition_raw`、`temper_or_condition_canonical`；
- `recrystallization_state`、`solution_state`、`aging_state`；
- `work_hardening_state`、`segregation_state`、`homogenization_state`；
- `state_assignment_basis`、`conflicting_state_evidence`。

### `calphad-assessment`

字段：

- `software`、`software_version`、`thermodynamic_database`、`database_version`；
- `mobility_database`、`components`、`allowed_phases`、`suppressed_phases`；
- `reference_states`、`calculation_type`、`conditions`；
- `assessed_or_extrapolated`、`fit_sources`、`uncertainty_or_confidence`；
- `simulation_job_ids`、`property_record_ids`。

不同数据库版本、组元集合、相抑制或参考态的结果不可静默合并。

## 4. 条件化性能要求

- 拉伸/压缩：试样标准、几何、标距、取向、取样位置、应变测量、速率、温度和环境。
- 疲劳：应力/应变控制、波形、R 比、频率、表面和终止定义。
- 蠕变：应力、温度、气氛、时间、稳态判据和断裂定义。
- 断裂：裂纹几何、预裂、尺寸有效性、加载模式和标准有效性。
- 硬度：标尺、压头、载荷、保持时间、位置和表面制备。
- 腐蚀/磨损：介质、温度、流动、面积、暴露时间、载荷/速度和计算基准。

数值仍进入核心 `property_records[]`；本适配器只补充金属学语义和跨字段审计。

## 5. 硬审计

1. 不把名义成分当实测成分。
2. 不把材料牌号当作唯一实体标识。
3. 不忽略取样方向、位置、几何和热机械历史。
4. 不以单张显微图代表整批统计分布。
5. 不把相关组织特征直接升级为强化、脆化或腐蚀机理。
6. 不把计算相稳定性写成实验相存在。

## 6. 规范依据

- NIST AM-Bench: https://www.nist.gov/ambench
- ASTM E8/E8M metallic tensile testing: https://store.astm.org/e0008_e0008m-21.html
- ASTM E112 grain size: https://store.astm.org/standards/e112
- ASTM E139 creep testing: https://store.astm.org/e0139-11.html
- NIST CALPHAD overview: https://www.nist.gov/publications/calphad-method-and-its-role-material-and-process-development
