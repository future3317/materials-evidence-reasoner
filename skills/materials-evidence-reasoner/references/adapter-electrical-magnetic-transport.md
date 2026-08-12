# Electrical, Magnetic, and Transport Adapter

适配器：`electrical-magnetic-transport`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: electrical-magnetic-transport -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `electrical-magnetic-transport` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `emt-electrical-run` / actual electrical or Hall transport run | `四探针电阻率`、`范德堡法`、`霍尔测量`、`量子霍尔效应`、`舒勃尼科夫-德哈斯振荡`、`磁阻`、`电流电压特性`、`four-probe resistivity`、`van der Pauw`、`Hall measurement`、`quantum Hall effect`、`Shubnikov-de-Haas oscillation`、`magnetoresistance`、`current-voltage characteristic`、`I-V`、`MR`、`QHE`、`SdH` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `emt-magnetic-run` / actual magnetic measurement | `SQUID 磁测量`、`振动样品磁强计`、`磁化率`、`磁滞回线`、`零场冷却`、`SQUID magnetometry`、`vibrating sample magnetometry`、`magnetic susceptibility`、`magnetization loop`、`zero-field-cooled`、`SQUID`、`VSM`、`ZFC`、`FC` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `emt-transport-result` / transport result and geometry | `电阻率温度曲线`、`载流子浓度`、`迁移率`、`热导率`、`塞贝克系数`、`resistivity versus temperature`、`carrier concentration`、`mobility`、`thermal conductivity`、`Seebeck coefficient` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `emt-generic` / generic transport vocabulary | `电阻`、`电导`、`磁性`、`输运`、`电流`、`resistance`、`conductivity`、`magnetic`、`transport`、`current` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `emt-apparatus` / electrical or magnetic apparatus component | `铜引线`、`超导磁体供场`、`电加热器`、`仅接触金属`、`copper lead wire`、`superconducting magnet supplies field`、`electrical heater`、`contact metal only` | 用于排除或消歧；有效语境：apparatus、sample-mounting、environment |

**歧义词消解**

- `conductivity`：候选含义为 electrical conductivity / ionic conductivity / thermal conductivity。判定规则：Resolve the transported quantity, geometry, frequency, and conditions.
- `magnetic`：候选含义为 target magnetic property / applied magnetic field / magnetic apparatus。判定规则：Require a measured target response for magnetic records.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound electrical, Hall, magnetic, dielectric, thermal, or thermoelectric transport run is reported
  - a transport property is derived with geometry and condition context
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`superconductivity`, `thermoelectric`, `quantum-materials`, `two-dimensional-materials`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: electrical-magnetic-transport -->

## 1. 范围

适用于 DC/AC 电阻率和电导、I-V、二/四探针、van der Pauw、Hall、磁阻、量子振荡、介电、Seebeck、热导/热扩散、磁化率、VSM、SQUID 和相关输运。超导判据由 `superconductivity` 适配器解释；本适配器只规范测量运行和通用输运结果。

## 2. 样品与接触

记录：

- 试样尺寸、厚度、形状、晶向、薄膜/体材和坐标系；
- 接触材料、制备、位置、数量、接触面积和接触电阻；
- 二探针、四探针、van der Pauw、Hall bar 或其他几何；
- 电流/电压源、量程、频率、锁相参数、前置放大和滤波；
- 温度计、磁场计、热流/温差传感器和校准；
- 温度、磁场矢量、电场、压力、栅压、应变和扫描历史；
- 激励幅值、极性反转、扫描速率、稳定等待和平均；
- 原始 V/I/相位/T/B/时间或热流/温差数据。

## 3. 分析记录

### `electrical-transport-analysis`

字段：`geometry`、`excitation`、`linear_region`、`contact_correction`、`geometric_factor`、`thickness`、`resistance_property_ids`、`resistivity_property_ids`、`conductivity_property_ids`、`iv_artifact_ids`、`heating_or_nonlinearity_risk`。

### `hall-and-magnetotransport-analysis`

字段：`field_orientation`、`current_orientation`、`symmetrization_or_antisymmetrization`、`field_range`、`fit_range`、`carrier_model`、`hall_property_ids`、`carrier_density_property_ids`、`mobility_property_ids`、`magnetoresistance_property_ids`、`multi_band_or_anomalous_contribution`。

### `oscillation-analysis`

字段：`oscillation_type`、`background_subtraction`、`field_window`、`frequency_analysis`、`frequency_property_ids`、`effective_mass_property_ids`、`dingle_or_scattering_property_ids`、`berry_phase_property_ids`、`indexing_convention`、`alternative_interpretations`。

### `magnetic-measurement-analysis`

字段：`instrument_mode`、`field_orientation`、`zfc_fc_protocol`、`demagnetization_correction`、`background_subtraction`、`mass_or_volume_basis`、`magnetization_property_ids`、`susceptibility_property_ids`、`coercivity_property_ids`、`remanence_property_ids`、`saturation_assessment`、`substrate_or_holder_contribution`。

### `thermal-or-thermoelectric-transport-analysis`

字段：`steady_or_transient`、`heat_flow_geometry`、`temperature_gradient`、`radiation_or_contact_correction`、`thermal_conductivity_property_ids`、`thermal_diffusivity_property_ids`、`seebeck_property_ids`、`direction`、`same_specimen_status`。

## 4. 硬审计

1. 电阻和电阻率不得混淆；保存几何换算和厚度。
2. Hall 单带模型结果标记模型依赖，多带/反常 Hall 保留替代项。
3. 场方向、温度扫描、冷却历史和极性处理不可省略。
4. 量子振荡背景、窗口和索引选择必须保存。
5. 磁矩、磁化强度和磁化率保存质量/体积/摩尔基准。
6. 基底、样品架、接触和自热贡献必须审计。

## 5. 规范依据

- NIST quantum transport measurements: https://www.nist.gov/programs-projects/quantum-transport-measurements
- BIPM SI Brochure: https://www.bipm.org/en/publications/si-brochure
- NeXus application definitions: https://manual.nexusformat.org/classes/applications/index.html
