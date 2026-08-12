# Mechanical Testing Adapter

适配器：`mechanical-testing`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: mechanical-testing -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `mechanical-testing` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `mech-actual-test` / actual mechanical test | `拉伸试验`、`压缩试验`、`弯曲试验`、`硬度试验`、`纳米压痕`、`tensile test`、`compression test`、`flexural test`、`hardness test`、`nanoindentation` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `mech-durability-test` / fatigue, creep, fracture, or wear test | `疲劳试验`、`蠕变断裂`、`断裂韧度`、`裂纹扩展试验`、`磨损试验`、`fatigue test`、`creep rupture`、`fracture toughness`、`crack-growth test`、`wear test` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `mech-curve-property` / mechanical curve or criterion | `应力应变曲线`、`屈服判据`、`S-N 曲线`、`载荷位移曲线`、`未失效截止`、`stress-strain curve`、`yield criterion`、`S-N curve`、`load-displacement curve`、`runout` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `mech-generic` / generic mechanical vocabulary | `强度`、`模量`、`硬度`、`载荷`、`应变`、`strength`、`modulus`、`hardness`、`load`、`strain` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `mech-nontest` / non-test mechanical context | `夹紧载荷`、`堆叠压力`、`仅计算弹性常数`、`机械支撑`、`混合剪切`、`clamping load`、`stack pressure`、`computed elastic constant only`、`mechanical support`、`mixing shear` | 用于排除或消歧；有效语境：apparatus、environment、simulation-only、processing |

**歧义词消解**

- `strength`：候选含义为 measured mechanical strength / signal intensity / qualitative performance adjective。判定规则：Require test mode, specimen, geometry, conditions, and a property result.
- `load`：候选含义为 mechanical test load / material loading fraction / electrical load / process charge。判定规则：Resolve units and method context.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound mechanical test and specimen are resolved
  - a target mechanical property or failure result derives from a defined test mode
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`metallic-materials`, `polymers`, `ceramics-glass-cement`, `materials-processing`, `electron-microscopy-microanalysis`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: mechanical-testing -->

## 1. 范围

适用于拉伸、压缩、弯曲、剪切、硬度、纳米压痕、断裂韧性、疲劳、蠕变、冲击、磨损和摩擦。材料领域适配器定义材料状态，本适配器定义试样、加载、曲线和有效性。

## 2. 试样和设备

记录：

- 标准/方法及版本、试样类型、几何、尺寸、标距、缺口/裂纹；
- 从母体材料的取样位置、方向、截面和加工方法；
- 表面粗糙度、抛光、边缘、预裂、调湿和储存；
- 试验机、夹具、载荷传感器、引伸计/应变测量和校准；
- 控制模式、速率、波形、频率、R 比、预载和终止条件；
- 温度、湿度、气氛、介质、辐照和原位环境；
- 完整载荷-位移、应力-应变、循环或时间曲线；
- 失效位置、失效模式、超量程、打滑和标准有效性。

工程应力/应变、真实应力/应变和名义截面必须区分；后颈缩数据不自动有效。

## 3. 分析记录

### `monotonic-mechanical-test`

字段：`test_mode`、`control_mode`、`rate`、`stress_strain_definition`、`modulus_fit_window`、`yield_criterion`、`strength_property_ids`、`modulus_property_ids`、`strain_property_ids`、`toughness_property_ids`、`failure_location`、`validity_status`。

### `hardness-or-indentation-test`

字段：`hardness_scale_or_method`、`indenter`、`load_or_depth_program`、`hold_time`、`spacing`、`surface_preparation`、`area_function`、`frame_compliance`、`thermal_drift`、`hardness_property_ids`、`modulus_property_ids`、`size_effect_or_substrate_risk`。

### `fatigue-test`

字段：`stress_or_strain_control`、`waveform`、`frequency`、`r_ratio`、`mean_and_amplitude`、`runout_definition`、`cycle_count_property_ids`、`sn_or_en_artifact_ids`、`crack_growth_property_ids`、`replicate_count`、`censoring`、`failure_mode`。

### `creep-test`

字段：`stress_or_load`、`temperature`、`environment`、`duration`、`strain_time_artifact_ids`、`primary_secondary_tertiary_definition`、`minimum_rate_property_ids`、`rupture_time_property_ids`、`interruption_history`、`failure_mode`。

### `fracture-test`

字段：`fracture_method`、`loading_mode`、`crack_or_notch_geometry`、`precracking`、`size_validity`、`crack_measurement`、`toughness_property_ids`、`r_curve_artifact_ids`、`fracture_energy_property_ids`、`validity_status`。

### `wear-and-friction-test`

字段：`contact_configuration`、`counterbody`、`normal_load`、`speed`、`distance_or_cycles`、`lubrication_or_medium`、`temperature`、`track_geometry`、`friction_property_ids`、`wear_property_ids`、`wear_basis`、`debris_or_transfer_layer`。

## 4. 统计和重复

保存试样数、批次数、均值/分布/离群规则、删失和失效模式。对脆性或寿命结果保存 Weibull、生存或其他分布模型及置信区间。单个“代表性曲线”不能替代重复统计。

## 5. 硬审计

1. 不省略试样几何、方向、速率和环境。
2. 不将横梁位移自动当试样应变。
3. 不把无效断裂/失效位置的数据静默保留或删除。
4. 不混淆硬度标尺、载荷和压痕尺寸效应。
5. 疲劳 runout 作为删失数据保留。
6. 不从单一曲线推断批次分布或可靠性。

## 6. 规范依据

- ASTM E8/E8M tensile testing: https://store.astm.org/e0008_e0008m-21.html
- ISO 6892-1 metallic tensile testing: https://www.iso.org/standard/78322.html
- ASTM E139 creep testing: https://store.astm.org/e0139-11.html
- ASTM C1161 ceramic flexural strength: https://store.astm.org/c1161-02cr08e01.html
