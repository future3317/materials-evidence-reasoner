# Materials Processing Adapter

适配器：`materials-processing`　层级：`process`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: materials-processing -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `materials-processing` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `proc-parameterized-step` / parameterized transformation step | `热处理制度`、`固溶处理`、`淬火`、`热轧`、`冷加工`、`烧结制度`、`放电等离子烧结`、`浆料混合`、`电极涂布`、`辊压`、`heat treatment schedule`、`solution treatment`、`quenching`、`hot rolling`、`cold working`、`sintering cycle`、`spark plasma sintering`、`slurry mixing`、`electrode coating`、`calendering`、`SPS` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `proc-additive-or-joining` / additive manufacturing or joining process | `增材制造`、`微尺度增材制造`、`三维打印`、`粉末床熔融`、`定向能量沉积`、`材料挤出`、`焊接`、`钎焊`、`扩散连接`、`additive manufacturing`、`micro-scale additive manufacturing`、`3D printing`、`powder bed fusion`、`directed energy deposition`、`material extrusion`、`welding`、`brazing`、`diffusion bonding`、`PBF-LB`、`DED`、`AM` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `proc-lineage` / input-output process lineage | `工艺路线`、`工艺链`、`原料到试样`、`后处理`、`构建方向`、`process route`、`process chain`、`feedstock to specimen`、`post-processing`、`build orientation` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `proc-generic` / generic preparation vocabulary | `制备`、`制造`、`处理`、`加工`、`合成`、`prepared`、`fabricated`、`treated`、`processed`、`synthesized` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `proc-not-executed` / non-executed or inaccessible process | `原样使用`、`方法见其他文献`、`未来加工`、`厂家保密工艺`、`as received`、`procedure reported elsewhere`、`future processing`、`manufacturer proprietary process` | 用于排除或消歧；有效语境：methods、cited-procedure、future-work、supplier-description |

**歧义词消解**

- `annealing`：候选含义为 material transformation process / instrument thermal equilibration / data-algorithm annealing。判定规则：Require a physical material input/output and actual temperature-time history.
- `fabricated`：候选含义为 actual documented process / unsupported summary verb。判定规则：Without steps, parameters, or an accessible referenced procedure, remain candidate.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an ordered target-material process with at least one reported parameter and input/output entity is present
  - a process variable or lineage is required to interpret a target result
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`metallic-materials`, `polymers`, `ceramics-glass-cement`, `two-dimensional-materials`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: materials-processing -->

## 1. 范围与路由

适用于改变材料身份、组成、形态、结构、界面或残余状态的有序工艺，包括合成、混合、熔炼、铸造、凝固、变形、热处理、烧结、固化、焊接/连接、沉积、涂覆、刻蚀、增材制造和后处理。

- `load`：工艺参数、轨迹、设备、环境或步骤顺序是实验变量、复现条件、比较依据或机理链的一部分。
- `candidate`：只出现“prepared/fabricated/treated”而完整过程指向外部文献或补充信息不可访问。
- `skip`：仅有供应商原样材料且来源没有可提取加工事实。

材料加工是跨材料适配器，不与金属、高分子、陶瓷、电池或二维材料竞争。

## 2. 工艺谱系

每个 `process_run` 明确：

- 输入实体、输出实体和副产物实体；
- 步骤顺序、并行/循环/保持/反馈控制关系；
- 设备、夹具、容器、模具、基底和关键接触材料；
- 设定参数、实测参数、容差、采样频率和控制模式；
- 温度、压力、气氛、流量、应力/应变、场和时间轨迹；
- 空间信息：位置、方向、扫描路径、层、区域和梯度；
- 过程内测量、异常、中断、返工、偏离和状态；
- 来源、证据、原始日志或数据产物。

只给出终点参数时，不生成完整轨迹；把缺失的升降温、保持、冷却、顺序和实测值分别列入 `missing_information[]`。

## 3. 记录类型

### `process-lineage-assessment`

字段：`process_run_ids`、`lineage_complete`、`unresolved_inputs`、`unresolved_outputs`、`external_method_dependencies`、`order_preserved`、`state_transitions`、`lineage_conflicts`。

### `thermal-history`

字段：`heating_segments`、`hold_segments`、`cooling_segments`、`temperature_measurement_location`、`setpoint_or_measured`、`maximum_temperature_property_ids`、`heating_rate_property_ids`、`cooling_rate_property_ids`、`quench_medium`、`thermal_cycle_count`。

### `mechanical-history`

字段：`deformation_mode`、`strain_path`、`strain_property_ids`、`strain_rate_property_ids`、`load_or_pressure_property_ids`、`pass_schedule`、`interpass_time`、`working_temperature`、`reference_direction`。

### `atmosphere-and-chemical-environment`

字段：`gas_or_liquid_components`、`purity`、`pressure`、`flow_property_ids`、`humidity_property_ids`、`oxygen_property_ids`、`dew_point_property_ids`、`vacuum_property_ids`、`container_compatibility`、`contamination_controls`。

### `additive-manufacturing-process`

字段：

- `am_process_class`、`machine`、`build_id`、`feedstock_entity_ids`；
- `layer_thickness_property_ids`、`power_property_ids`、`speed_property_ids`、`hatch_property_ids`；
- `scan_strategy`、`spot_or_beam_property_ids`、`preheat_property_ids`；
- `build_atmosphere`、`build_orientation`、`support_strategy`；
- `in_situ_measurement_run_ids`、`thermal_history_artifact_ids`；
- `post_process_run_ids`、`coupon_location`。

综合能量密度只能作为派生指标；必须保留功率、速度、道间距、层厚和公式，不得用它替代原始参数。

### `joining-and-interface-process`

字段：`joining_method`、`parent_entity_ids`、`filler_or_interlayer_entity_ids`、`surface_preparation`、`joint_geometry`、`heat_input_property_ids`、`pressure_or_force_property_ids`、`atmosphere`、`post_join_treatment`、`interface_entity_ids`、`zone_entity_ids`。

## 4. 工艺可比性

比较工艺时，至少核对输入状态、设备尺度、几何、设定/实测参数、时间轨迹、气氛、空间位置和后处理。参数名相同但传感器位置、控制方式、设备标定或尺度不同，不视为自动可比。

## 5. 硬审计

1. 不把无顺序参数列表称为完整工艺。
2. 不把设定值当实测值。
3. 不从目标温度猜测升温、保持或冷却程序。
4. 不忽略设备、容器、基底和尺度效应。
5. 不把方法引用中的通用流程自动赋给当前样品，除非引用明确采用且边界可解析。
6. 不把过程相关性直接升级为机理。

## 6. 规范依据

- NIST AM-Bench: https://www.nist.gov/ambench
- NIST types of AM benchmarks: https://www.nist.gov/ambench/types-am-benchmarks
- ISO heat treatment vocabulary: https://www.iso.org/standard/87711.html
