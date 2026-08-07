# Energy Application Adapters

本文件定义多个应用层适配器。先完成材料、实体和测量解析，再选择真正相关的应用模块。`energy materials` 不是单一适配器。

## 1. Battery

适配器：`battery`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: battery -->
### 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `battery` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `bat-cell-hierarchy` / battery cell or component hierarchy | `电池单体`、`电池电极`、`锂离子电池`、`金属离子电池`、`半电池`、`全电池`、`扣式电池`、`软包电池`、`正极`、`负极`、`隔膜`、`battery cell`、`battery electrode`、`lithium-ion battery`、`metal-ion battery`、`half-cell`、`full cell`、`coin cell`、`pouch cell`、`positive electrode`、`negative electrode`、`separator`、`LIB` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `bat-cycling` / battery cycling protocol and result | `恒流充放电`、`循环寿命`、`容量保持率`、`倍率`、`荷电状态`、`健康状态`、`galvanostatic charge-discharge`、`cycle life`、`capacity retention`、`C-rate`、`state of charge`、`state of health`、`GCD`、`SOC`、`SOH` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `bat-practical-context` / battery balancing or inactive-material context | `负正极容量比`、`电解液容量比`、`面载量`、`化成循环`、`日历老化`、`N/P ratio`、`electrolyte-to-capacity ratio`、`areal loading`、`formation cycle`、`calendar ageing`、`E/C` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `bat-generic` / generic battery-component vocabulary | `正极`、`负极`、`电解液`、`电极`、`容量`、`cathode`、`anode`、`electrolyte`、`electrode`、`capacity` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `bat-other-use` / non-target battery mention | `电池供电`、`一系列测试`、`引用的电池电极`、`备用电池`、`battery powered`、`battery of tests`、`cited battery electrode`、`backup battery` | 用于排除或消歧；有效语境：apparatus、figurative-language、cited-comparison |

**歧义词消解**

- `capacity`：候选含义为 battery charge capacity / adsorption capacity / heat capacity / production capacity。判定规则：Require charge/discharge context, units, electrode/cell basis, and cycle index.
- `anode/cathode`：候选含义为 battery electrode / electrochemical cell electrode / vacuum-tube/electronic component。判定规则：Require a rechargeable/primary cell hierarchy or battery objective.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a target battery cell/component hierarchy and a cycling, assembly, performance, ageing, or safety result are bound
  - cell configuration plus battery-specific protocol is central to the source
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`electrochemical-testing`, `liquid-materials`, `polymers`, `materials-processing`, `thermal-analysis`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: battery -->

### 路由与层级

`load` 要求目标对象属于电极、电芯、模组或电池系统，且组成、制造、协议、性能或退化是中心结果。仅使用电池作为供电设备、背景应用或被引案例时 `skip`。

严格区分：`active-material -> electrode -> half-cell/full-cell -> module -> pack`。材料级比容量不能写成电芯级能量密度；半电池结果不能自动代表全电池。

### 记录类型

`battery-component-hierarchy` 字段：`level`、`parent_entity_ids`、`child_entity_ids`、`cell_format`、`manufacturer`、`batch_or_lot`、`nominal_capacity_property_ids`、`dimensions`、`mass_property_ids`。

`electrode-formulation` 字段：`active_material_entity_ids`、`conductive_additive_entity_ids`、`binder_entity_ids`、`fraction_basis`、`fraction_property_ids`、`loading_property_ids`、`areal_capacity_property_ids`、`thickness_property_ids`、`density_property_ids`、`porosity_property_ids`、`current_collector`、`coating_and_drying_process_run_ids`、`calendering_process_run_ids`。

`cell-assembly` 字段：`positive_electrode_id`、`negative_electrode_id`、`np_ratio_property_ids`、`separator_entity_ids`、`electrolyte_entity_ids`、`electrolyte_volume_property_ids`、`electrolyte_to_capacity_property_ids`、`assembly_atmosphere`、`stack_pressure_property_ids`、`formation_process_run_ids`。

`battery-test-protocol` 字段：`measurement_run_ids`、`protocol_steps`、`current_or_c_rate_basis`、`voltage_limits`、`soc_limits`、`cv_cutoff`、`rest_rules`、`temperature`、`pressure`、`cycle_index_definition`、`reference_performance_definition`、`excluded_cycles`。

`battery-performance-assessment` 字段：`capacity_property_ids`、`coulombic_efficiency_property_ids`、`energy_property_ids`、`power_property_ids`、`retention_property_ids`、`resistance_property_ids`、`impedance_property_ids`、`rate_capability_property_ids`、`cycle_life_property_ids`、`calendar_life_property_ids`、`soc_or_soh_property_ids`、`gas_or_swelling_property_ids`、`safety_property_ids`。

`battery-degradation-assessment` 字段：`degradation_modes`、`interphase_evidence`、`lithium_inventory_evidence`、`active_material_loss_evidence`、`transport_limitation_evidence`、`postmortem_entity_ids`、`supporting_measurement_run_ids`、`alternative_explanations`。

### 硬审计

- 容量、能量和保持率必须保存质量/面积/体积/电芯等基准和参考循环。
- C-rate 必须绑定额定或实测容量定义。
- EIS 拟合参数保留等效电路、频率范围、扰动和拟合诊断。
- 不用单一循环寿命数字替代完整协议。
- 安全失效和热失控值必须绑定 SOC、尺寸、触发方式和判据。

依据：NREL Battery Data Hub https://batterydata.nrel.gov/ ；BattINFO https://www.big-map.eu/da/dissemination/battinfo

## 2. Photovoltaic Device

适配器：`photovoltaic-device`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: photovoltaic-device -->
### 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `photovoltaic-device` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `pv-device` / photovoltaic cell or module | `太阳电池`、`光伏器件`、`单结电池`、`叠层太阳电池`、`光伏组件`、`solar cell`、`photovoltaic device`、`single-junction cell`、`tandem solar cell`、`PV module`、`PV` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `pv-jv-performance` / illuminated photovoltaic performance | `光照电流电压`、`光电转换效率`、`开路电压`、`短路电流密度`、`填充因子`、`current-voltage under illumination`、`power conversion efficiency`、`open-circuit voltage`、`short-circuit current density`、`fill factor`、`PCE`、`Voc`、`Jsc`、`FF` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `pv-calibration-stability` / PV calibration or stability protocol | `太阳模拟器等级`、`稳定功率输出`、`外量子效率`、`最大功率点跟踪`、`AM1.5G`、`solar simulator class`、`stabilized power output`、`external quantum efficiency`、`maximum power point tracking`、`EQE`、`MPPT` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `pv-generic` / generic photovoltaic vocabulary | `光伏`、`太阳能吸收层`、`光活性层`、`太阳能`、`photovoltaic`、`solar absorber`、`photoactive layer`、`solar energy` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `pv-other-photo` / non-PV optical or power context | `光催化`、`光电化学燃料制备`、`用于水氧化的光阳极`、`光探测器`、`量子产率`、`太阳能板供电`、`未来光伏应用`、`photocatalysis`、`photoelectrochemical fuel production`、`photoanode for water oxidation`、`photodetector`、`quantum yield`、`solar panel powers the experiment`、`future PV application` | 用于排除或消歧；有效语境：other-application、apparatus、future-work |

**歧义词消解**

- `efficiency`：候选含义为 PV power conversion efficiency / quantum efficiency / energy efficiency of another device。判定规则：Require PV device stack, illumination, area basis, and the named metric.
- `solar`：候选含义为 photovoltaic device / solar-thermal use / photocatalysis / illumination source。判定规则：Require electrical power generation by a resolved device.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a resolved PV device stack and illuminated electrical performance are reported
  - PV calibration, stabilized output, or device stability is a central target result
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`spectroscopy`, `electrical-magnetic-transport`, `materials-processing`, `two-dimensional-materials`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: photovoltaic-device -->

### 记录类型

`pv-device-stack` 字段：`architecture`、`substrate`、`layer_sequence`、`layer_entity_ids`、`layer_thickness_property_ids`、`contact_materials`、`active_area_property_ids`、`aperture_or_mask_area_property_ids`、`encapsulation`、`fabrication_process_run_ids`。

`pv-measurement-protocol` 字段：`measurement_run_ids`、`illumination_source`、`spectrum`、`intensity_property_ids`、`calibration_reference`、`temperature`、`preconditioning`、`scan_direction`、`scan_rate_property_ids`、`delay_or_settling`、`steady_state_method`。

`pv-performance-assessment` 字段：`voc_property_ids`、`jsc_property_ids`、`fill_factor_property_ids`、`efficiency_property_ids`、`eqe_property_ids`、`hysteresis_property_ids`、`stabilized_output_property_ids`、`stability_property_ids`、`degradation_modes`。

硬审计：不混淆 active、aperture 和 total area；不把扫描 PCE 当稳定输出；保存光谱、强度、校准、温度、扫描和预处理。

依据：NREL PV Device Performance https://www.nrel.gov/pv/device-performance

## 3. Electrochemical Energy

适配器：`electrochemical-energy`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: electrochemical-energy -->
### 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `electrochemical-energy` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `ece-reaction` / energy-conversion electrochemical reaction | `析氢反应`、`析氧反应`、`氧还原反应`、`二氧化碳还原`、`氮还原反应`、`hydrogen evolution reaction`、`oxygen evolution reaction`、`oxygen reduction reaction`、`carbon dioxide reduction`、`nitrogen reduction reaction`、`HER`、`OER`、`ORR`、`CO2RR`、`NRR` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `ece-reactor` / electrolyzer or fuel-cell reactor | `水电解槽`、`燃料电池`、`膜电极组件`、`流动电解池`、`气体扩散电极`、`water electrolyzer`、`fuel cell`、`membrane electrode assembly`、`flow cell`、`gas diffusion electrode`、`MEA`、`GDE` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `ece-performance` / electrocatalytic performance | `过电位`、`塔菲尔斜率`、`法拉第效率`、`转换频率`、`质量活性`、`overpotential`、`Tafel slope`、`Faradaic efficiency`、`turnover frequency`、`mass activity`、`FE`、`TOF` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `ece-generic` / generic electrocatalysis vocabulary | `电催化剂`、`电化学能源`、`催化电极`、`活性`、`electrocatalyst`、`electrochemical energy`、`catalytic electrode`、`activity` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `ece-other-electrochem` / non-energy-conversion electrochemical use | `仅电池循环`、`仅储氢`、`电镀`、`腐蚀测试`、`电化学清洗`、`电化学传感器`、`battery cycling only`、`hydrogen storage only`、`electroplating`、`corrosion test`、`electrochemical cleaning`、`electrochemical sensor` | 用于排除或消歧；有效语境：other-application、sample-preparation |

**歧义词消解**

- `activity`：候选含义为 electrocatalytic rate metric / chemical activity / generic performance adjective。判定规则：Require a named reaction, normalization basis, potential scale, and target electrode.
- `fuel cell`：候选含义为 target energy device / commercial power source used as apparatus。判定规则：Require reactor/component/performance evidence for the studied device.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a named energy-conversion reaction and target catalyst/electrode performance are bound
  - a fuel-cell or electrolyzer reactor and its operating result are central
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`electrochemical-testing`, `composition-particle-surface`, `liquid-materials`, `materials-processing`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: electrochemical-energy -->

适用于电催化、燃料电池、电解槽和其他非电池电化学能源转换。电池循环由 `battery` 处理；通用 CV/EIS/GITT 方法由 `electrochemical-testing` 处理。

`electrocatalyst-electrode` 字段：`catalyst_entity_ids`、`support_entity_ids`、`loading_property_ids`、`ink_composition`、`ionomer_fraction_property_ids`、`electrode_area_property_ids`、`ecsa_property_ids`、`pretreatment_process_run_ids`。

`electrochemical-reactor` 字段：`reactor_type`、`working_counter_reference`、`membrane_or_separator`、`electrolyte_or_feed`、`flow_property_ids`、`humidity_property_ids`、`pressure_property_ids`、`temperature`、`geometry`、`product_collection`。

`electrochemical-performance` 字段：`current_property_ids`、`voltage_or_overpotential_property_ids`、`activity_basis`、`tafel_property_ids`、`selectivity_property_ids`、`faradaic_efficiency_property_ids`、`mass_balance_property_ids`、`durability_property_ids`、`degradation_modes`、`ir_correction`。

硬审计：明确参比电极和换算标度；区分几何面积、质量和 ECSA 活性；Faradaic efficiency 必须有产物定量和电荷基准；不以初始活性代替耐久性。

## 4. Hydrogen Storage

适配器：`hydrogen-storage`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: hydrogen-storage -->
### 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `hydrogen-storage` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `h2s-storage-material` / materials-based hydrogen storage | `储氢材料`、`储氢容量`、`金属氢化物`、`复杂氢化物`、`化学储氢`、`储氢吸附剂`、`hydrogen storage material`、`hydrogen storage capacity`、`metal hydride`、`complex hydride`、`chemical hydrogen storage`、`hydrogen sorbent` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `h2s-sorption` / hydrogen sorption measurement | `压力组成温度等温线`、`吸氢`、`放氢`、`可逆储氢容量`、`范特霍夫分析`、`pressure-composition-temperature isotherm`、`hydrogen absorption`、`hydrogen desorption`、`reversible hydrogen capacity`、`van't Hoff analysis`、`PCT`、`PCI` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `h2s-performance` / storage performance context | `质量储氢容量`、`体积储氢容量`、`吸放氢动力学`、`平衡压力`、`循环稳定性`、`gravimetric capacity`、`volumetric capacity`、`sorption kinetics`、`equilibrium pressure`、`cycle stability` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `h2s-generic` / generic hydrogen vocabulary | `氢`、`氢化物`、`吸附`、`脱附`、`吸收量`、`hydrogen`、`hydride`、`adsorption`、`desorption`、`uptake` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `h2s-other-hydrogen` / non-storage hydrogen use | `氢载气`、`析氢催化剂`、`氢脆`、`氢气氛`、`仅储罐合金`、`hydrogen carrier gas`、`hydrogen evolution catalyst`、`hydrogen embrittlement`、`hydrogen atmosphere`、`storage tank alloy only` | 用于排除或消歧；有效语境：environment、other-application、degradation、apparatus |

**歧义词消解**

- `uptake`：候选含义为 hydrogen storage capacity / generic gas adsorption / biological uptake。判定规则：Require hydrogen identity, pressure/temperature, capacity basis, and target material.
- `hydride`：候选含义为 storage phase / intermediate reaction product / hydrogen embrittlement feature。判定规则：Require storage objective or sorption/thermodynamic evidence.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a target storage material and hydrogen sorption/capacity result are bound
  - storage thermodynamics, kinetics, reversibility, or cycling is a central result
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`composition-particle-surface`, `thermal-analysis`, `diffraction-scattering`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: hydrogen-storage -->

`hydrogen-storage-material` 字段：`storage_class`、`composition`、`structure`、`activation_process_run_ids`、`sample_mass_property_ids`、`packing_density_property_ids`。

`hydrogen-sorption-assessment` 字段：`pct_or_isotherm_artifact_ids`、`temperature`、`pressure_range`、`equilibrium_criterion`、`gravimetric_capacity_property_ids`、`volumetric_capacity_property_ids`、`usable_capacity_property_ids`、`kinetics_property_ids`、`enthalpy_property_ids`、`entropy_property_ids`、`cycle_property_ids`、`impurity_tolerance_property_ids`。

硬审计：区分材料和系统基准、总容量和可用容量、吸附和解吸、动力学和热力学；保存活化、温压和平衡判据。

依据：DOE materials-based hydrogen storage https://www.energy.gov/cmei/fuels/materials-based-hydrogen-storage

## 5. Thermoelectric

适配器：`thermoelectric`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: thermoelectric -->
### 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `thermoelectric` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `te-zt` / thermoelectric figure of merit | `热电优值`、`无量纲热电优值`、`thermoelectric figure of merit`、`dimensionless figure of merit`、`zT` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `te-coupled-transport` / coupled thermoelectric transport | `塞贝克系数与电导率`、`功率因子`、`热导率与塞贝克系数`、`Seebeck coefficient and electrical conductivity`、`power factor`、`thermal conductivity and Seebeck`、`S`、`sigma`、`kappa` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `te-device` / thermoelectric device performance | `热电模块`、`热电臂`、`温差发电`、`制冷性能系数`、`thermoelectric module`、`thermoelectric leg`、`temperature difference power generation`、`cooling coefficient of performance`、`TEG`、`TEC`、`COP` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `te-generic` / generic thermoelectric vocabulary | `热电`、`塞贝克`、`热输运`、`电输运`、`thermoelectric`、`Seebeck`、`thermal transport`、`electrical transport` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `te-instrument-or-other` / non-target thermoelectric use | `热电偶温度传感器`、`帕尔贴制冷器作为设备`、`仅自旋塞贝克`、`单独热导率结果`、`thermocouple temperature sensor`、`Peltier cooler used as apparatus`、`spin Seebeck only`、`single thermal conductivity result` | 用于排除或消歧；有效语境：apparatus、other-phenomenon、single-property |

**歧义词消解**

- `Seebeck`：候选含义为 thermoelectric material property / thermocouple principle / spin Seebeck phenomenon。判定规则：A single mention is supporting only; load when thermoelectric performance or a target thermoelectric state is central.
- `ZT`：候选含义为 thermoelectric figure of merit / unrelated acronym。判定规则：Require the defining transport quantities or an explicit thermoelectric definition.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - zT or power factor is reported with target and temperature context
  - at least two coupled transport quantities or a thermoelectric device result are central
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`electrical-magnetic-transport`, `thermal-analysis`, `materials-processing`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: thermoelectric -->

`thermoelectric-state` 字段：`composition`、`doping_property_ids`、`density_property_ids`、`orientation`、`microstructure_record_ids`、`contact_state`、`stability_state`。

`thermoelectric-performance` 字段：`seebeck_property_ids`、`electrical_conductivity_property_ids`、`thermal_conductivity_property_ids`、`power_factor_property_ids`、`zt_property_ids`、`temperature_range`、`same_specimen_status`、`derivation_inputs`、`contact_correction`、`radiation_correction`。

硬审计：ZT 的 S、sigma、kappa 和温度必须可追溯；记录是否同一试样、同一方向和可比状态；区分总热导、电子和晶格分量及模型假设。
