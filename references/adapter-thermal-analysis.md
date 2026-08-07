# Thermal Analysis Adapter

适配器：`thermal-analysis`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: thermal-analysis -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `thermal-analysis` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `ta-actual-technique` / actual thermal-analysis run | `差示扫描量热`、`热重分析`、`热机械分析`、`动态力学分析`、`膨胀法`、`differential scanning calorimetry`、`thermogravimetric analysis`、`thermomechanical analysis`、`dynamic mechanical analysis`、`dilatometry`、`DSC`、`TGA`、`TG`、`TMA`、`DMA` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `ta-transition` / thermal-analysis transition or mass-loss result | `玻璃化转变起始`、`熔融焓`、`结晶峰`、`失重台阶`、`残余质量分数`、`glass-transition onset`、`melting enthalpy`、`crystallization peak`、`mass-loss step`、`residue fraction` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `ta-protocol` / thermal-analysis program | `升温速率`、`降温循环`、`吹扫气体`、`基线校正`、`等转化率分析`、`heating rate`、`cooling cycle`、`purge gas`、`baseline correction`、`isoconversional analysis` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `ta-generic` / generic thermal vocabulary | `热分析`、`玻璃化温度`、`分解温度`、`热稳定性`、`thermal analysis`、`decomposition temperature`、`thermal stability`、`Tg` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `ta-process-heating` / non-thermal-analysis heating or thermal property | `炉内热处理`、`合成升温程序`、`反应器控温`、`热电偶校准`、`仅热导率测量`、`仅服役温度`、`furnace heat treatment`、`synthesis heating schedule`、`reactor temperature control`、`thermocouple calibration`、`thermal conductivity measurement only`、`service temperature only` | 用于排除或消歧；有效语境：materials-processing、synthesis、apparatus、transport-property |

**歧义词消解**

- `Tg`：候选含义为 glass-transition temperature by DSC / glass-transition temperature by DMA / unresolved literature value。判定规则：Preserve method and criterion; DMA and DSC values are not interchangeable.
- `thermal stability`：候选含义为 TGA mass-loss resistance / service-temperature claim / generic adjective。判定规则：Require a defined measurand, method, and temperature/time criterion.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound DSC/TG/TMA/DMA/dilatometry run is reported
  - a thermal transition, mass-loss, thermomechanical, dynamic-mechanical, or kinetic result derives from that run
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`polymers`, `ceramics-glass-cement`, `materials-processing`, `thermoelectric`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: thermal-analysis -->

## 1. 范围

适用于 DSC、TGA/TG、DTA、TMA、dilatometry 和 DMA。热导、热扩散和量热器可复用通用测量契约，但只有方法匹配时使用相应子类型字段。

## 2. 采集字段

- `thermal_method`、仪器、传感器和控制软件；
- 样品质量、形态、尺寸、取样位置和预处理；
- 坩埚/盘、盖、密封/打孔、参比和坩埚材料；
- 气氛、纯度、流量、压力和切换程序；
- 温度范围、升降温速率、等温段、循环、调制程序；
- 温度、热流、质量和尺寸校准；
- 空白、浮力、基线、漂移和仪器响应修正；
- 原始信号、导数、基线、积分和拟合产物。

## 3. 分析记录

### `thermal-transition-analysis`

字段：`transition_type`、`onset_property_ids`、`midpoint_property_ids`、`peak_property_ids`、`end_property_ids`、`enthalpy_property_ids`、`baseline_definition`、`integration_bounds`、`heating_or_cooling`、`cycle_index`、`reversing_or_nonreversing`。

### `mass-loss-analysis`

字段：`mass_loss_steps`、`onset_property_ids`、`peak_rate_property_ids`、`mass_fraction_property_ids`、`residue_property_ids`、`temperature_or_time_bounds`、`atmosphere_segments`、`dtg_method`、`species_assignment`、`assignment_basis`。

### `thermomechanical-analysis`

字段：`mode`、`probe_or_fixture`、`load_or_stress`、`specimen_geometry`、`direction`、`expansion_property_ids`、`softening_property_ids`、`shrinkage_or_creep_property_ids`、`contact_correction`。

### `dynamic-mechanical-analysis`

字段：`fixture`、`geometry`、`strain_or_stress_amplitude`、`linear_region_check`、`frequency`、`temperature_program`、`storage_modulus_property_ids`、`loss_modulus_property_ids`、`tan_delta_property_ids`、`tg_criterion`、`time_temperature_superposition`。

### `thermal-kinetics-analysis`

字段：`reaction_or_process`、`kinetic_method`、`heating_rates`、`conversion_definition`、`mechanism_assumption`、`fit_range`、`activation_energy_property_ids`、`preexponential_property_ids`、`fit_diagnostics`、`applicability_limit`。

## 4. 硬审计

1. onset、midpoint、peak 和 extrapolated 值不能合并。
2. 不同升温速率、循环、气氛和样品质量的结果不自动可比。
3. DSC 热焓保存质量基准、基线和积分边界。
4. TGA 失重物种归属不是由温区单独证明。
5. 动力学参数必须保存模型、升温速率、转化定义和机制假设。
6. DMA Tg 与 DSC Tg 保持方法和判据区分。

## 5. 规范依据

- ISO 11357-1 DSC principles: https://www.iso.org/standard/83904.html
- ISO 11357-3 melting/crystallization: https://www.iso.org/standard/11357-3
- ISO 11358-1 thermogravimetry: https://www.iso.org/standard/79999.html
- ISO 11358-2 activation energy: https://www.iso.org/standard/80001.html
