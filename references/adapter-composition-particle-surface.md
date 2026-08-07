# Composition, Particle, and Surface Measurements Adapter

适配器：`composition-particle-surface`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: composition-particle-surface -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `composition-particle-surface` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `cps-composition` / actual composition or separation analysis | `电感耦合等离子体质谱`、`X 射线荧光`、`元素分析`、`体积排阻色谱`、`气相色谱`、`inductively coupled plasma mass spectrometry`、`X-ray fluorescence`、`elemental analysis`、`size-exclusion chromatography`、`gas chromatography`、`ICP-MS`、`ICP-OES`、`XRF`、`SEC`、`GC`、`LC` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `cps-particle-surface` / actual particle or surface measurement | `动态光散射`、`激光衍射粒度`、`气体吸附`、`BET 比表面积`、`接触角`、`dynamic light scattering`、`laser diffraction particle size`、`gas adsorption`、`BET surface area`、`contact angle`、`DLS`、`BET` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `cps-quantification` / quantitative analysis context | `校准曲线`、`检出限`、`回收率`、`粒径分布`、`吸附等温线`、`calibration curve`、`detection limit`、`recovery`、`particle-size distribution`、`adsorption isotherm`、`LOD`、`LOQ` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `cps-generic` / generic composition or surface vocabulary | `组成`、`粒径`、`比表面积`、`孔隙`、`密度`、`润湿`、`composition`、`particle size`、`surface area`、`porosity`、`density`、`wetting` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `cps-nontarget` / calibration or environmental composition | `载气组成`、`仅仪器校准标准`、`仅供应商名义成分`、`非目标接触液`、`carrier gas composition`、`instrument calibration standard only`、`supplier nominal composition only`、`contact liquid not studied` | 用于排除或消歧；有效语境：apparatus、calibration-only、secondary-source、environment |

**歧义词消解**

- `BET`：候选含义为 Brunauer-Emmett-Teller surface-area analysis / unrelated acronym。判定规则：Require a gas adsorption isotherm, fit range, and target powder/porous entity.
- `composition`：候选含义为 target measured composition / nominal recipe / gas/environment composition。判定规则：Preserve measurement status and bind to the correct entity or environment.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound composition, chromatography, particle, adsorption, density, or wetting run is reported
  - a quantitative result derives from a named method with calibration/model context
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`liquid-materials`, `polymers`, `battery`, `electron-microscopy-microanalysis`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: composition-particle-surface -->

## 1. 范围

覆盖常见的体成分、痕量元素、分子量/色谱、粒径、比表面积、孔结构和润湿测量，包括 ICP-MS/OES、XRF、元素分析、GC/LC、SEC/GPC、激光粒度、DLS、BET/气体吸附、密度和接触角。XPS 等表面光谱仍由 `spectroscopy` 处理。

## 2. 通用定量字段

记录目标分析物/被测量、取样和代表性、样品质量/体积、制备、消解/萃取/稀释、空白、标准物质、校准曲线、内标、回收率、重复、检出限/定量限、仪器漂移、基质效应、原始信号和计算公式。

## 3. 方法记录

### `elemental-composition-analysis`

字段：`method`、`sample_preparation`、`digestion_or_fusion`、`dilution`、`analytes`、`isotopes_or_lines`、`standards`、`internal_standards`、`calibration_range`、`blank_correction`、`interference_correction`、`recovery_property_ids`、`composition_property_ids`、`detection_limits`。

### `chromatography-or-sec-analysis`

字段：`method`、`column`、`mobile_phase_or_eluent`、`flow`、`temperature`、`injection`、`detector`、`calibration_standards`、`retention_or_elution_artifact_ids`、`peak_integration`、`molecular_distribution_property_ids`、`response_factor_assumptions`。

### `particle-size-analysis`

字段：`method`、`dispersion_medium`、`concentration`、`dispersion_process`、`optical_properties`、`viscosity`、`measurement_angle`、`inversion_model`、`size_basis`、`distribution_property_ids`、`agglomeration_or_multiple_scattering_risk`。

强度、体积、数量和质量分布不可静默转换；DLS hydrodynamic size 与显微几何尺寸不得合并。

### `gas-adsorption-and-porosity-analysis`

字段：`adsorptive`、`degassing_program`、`sample_mass`、`temperature`、`relative_pressure_range`、`equilibration`、`isotherm_artifact_ids`、`bet_fit_range`、`bet_consistency_checks`、`surface_area_property_ids`、`pore_model`、`pore_size_property_ids`、`total_pore_volume_property_ids`。

### `contact-angle-and-wetting-analysis`

字段：`liquid`、`solid_surface_state`、`surface_preparation`、`roughness_property_ids`、`drop_volume`、`dispensing_rate`、`atmosphere`、`temperature`、`time_after_deposition`、`static_advancing_receding`、`fit_model`、`contact_angle_property_ids`、`surface_energy_model`。

### `density-measurement-analysis`

字段：`method`、`temperature`、`pressure`、`sample_state`、`fluid_or_displacement_medium`、`open_pore_access`、`drying_or_conditioning`、`bulk_true_apparent_definition`、`density_property_ids`。

## 4. 硬审计

1. 不以单次局部分析代表总体而不说明取样。
2. 组成保存质量、原子、摩尔或其他基准。
3. 低于检出限与零分开。
4. 粒径分布保存加权基准和反演模型。
5. BET 保存拟合区间和一致性检查，不只保存面积。
6. 接触角保存表面状态、时间和静态/前进/后退定义。
7. 体密度、真密度、骨架密度和表观密度不可混淆。

## 5. 规范依据

- AnIML overview: https://new.animl.org/overview
- NIST materials data curation: https://www.nist.gov/programs-projects/materials-data-curation-system
- ISO nanotechnology measurement catalogue: https://www.iso.org/sectors/engineering/nanotechnology
