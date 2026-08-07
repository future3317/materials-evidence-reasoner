# Diffraction and Scattering Adapter

适配器：`diffraction-scattering`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: diffraction-scattering -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `diffraction-scattering` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `dif-actual-measurement` / actual diffraction or scattering measurement | `粉末 X 射线衍射`、`单晶衍射`、`中子衍射`、`小角 X 射线散射`、`总散射`、`powder X-ray diffraction`、`single-crystal diffraction`、`neutron diffraction`、`small-angle X-ray scattering`、`total scattering`、`XRD`、`PXRD`、`SAXS`、`WAXS`、`PDF` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `dif-analysis` / diffraction/scattering analysis | `Rietveld 精修`、`Le Bail 精修`、`Pawley 精修`、`对分布函数`、`倒易空间图`、`Rietveld refinement`、`Le Bail refinement`、`Pawley refinement`、`pair distribution function`、`reciprocal-space map`、`RSM` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `dif-data-feature` / target-bound scattering data | `衍射峰`、`散射矢量`、`衍射图谱`、`结构因子`、`相分数`、`diffraction peak`、`scattering vector`、`diffractogram`、`structure factor`、`phase fraction`、`2theta`、`q` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `dif-generic` / generic diffraction vocabulary | `衍射`、`散射`、`XRD 证实`、`峰`、`diffraction`、`scattering`、`XRD confirmed`、`peak` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `dif-nonmaterial` / non-material diffraction use | `衍射光栅`、`衍射极限分辨率`、`XRD 样品架`、`引用的衍射图`、`diffraction grating`、`diffraction-limited resolution`、`XRD sample holder`、`cited diffraction pattern` | 用于排除或消歧；有效语境：apparatus、optics、cited-comparison |

**歧义词消解**

- `PDF`：候选含义为 pair distribution function / portable document format / probability density function。判定规则：Resolve from scattering context, q/r ranges, and structural analysis.
- `peak`：候选含义为 diffraction feature / spectral feature / thermal-analysis feature / generic maximum。判定规则：Require method and axis context.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound diffraction/scattering run or data artifact is reported
  - a structure, phase, size, correlation, or refinement result is derived from target-bound scattering data
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`ceramics-glass-cement`, `metallic-materials`, `two-dimensional-materials`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: diffraction-scattering -->

## 1. 范围

适用于粉末/单晶 XRD、中子衍射、总散射/PDF、SAXS/WAXS、GI-XRD/GI-SAXS 和相关散射测量。仅在背景中提到“XRD confirmed”且没有目标实体、图表、方法或结果证据时使用 `candidate`，不得生成完整测量运行。

本适配器主要约束 `measurement_run.technique_details`、数据产物和分析链；相鉴定、结构精修或尺寸模型的科学解释可进入 `domain_records[]`。

## 2. 采集字段

记录：

- `probe`：X ray、neutron 或 electron；
- `source_type`、`radiation_or_beamline`、`wavelength` 或 `energy`、单色化；
- `measurement_mode`、`geometry`、`incident_angle`、`sample_rotation`；
- `detector`、`detector_distance`、`slits_or_collimation`；
- `axis_type`：2theta、Q、d-spacing、TOF 等；
- `scan_range`、`step_size`、`count_or_dwell_time`、`scan_rate`；
- `sample_form`、`holder_or_capillary`、`packing`、`orientation`、`spinning`；
- `temperature`、`pressure`、`atmosphere`、`field` 和原位/操作条件；
- `calibration_standard`、`instrument_resolution`、`zero_or_geometry_correction`；
- 原始计数、掩膜、几何校正、归一化和背景产物。

不能从仪器型号自动推断波长、狭缝、探测器、扫描范围或默认处理。

## 3. 分析记录

### `phase-identification`

字段：`candidate_phases`、`reference_database`、`reference_entry_ids`、`matched_peak_or_region_evidence`、`unmatched_features`、`preferred_orientation_risk`、`overlap_risk`、`assessment`。

### `structure-refinement`

字段：

- `model_structure_ids`、`space_group`、`refined_parameters`、`fixed_parameters`；
- `profile_function`、`background_model`、`peak_shape_model`；
- `preferred_orientation_model`、`size_or_strain_model`；
- `constraints`、`restraints`、`excluded_regions`；
- `r_factors`、`goodness_of_fit`、`residual_artifact_ids`；
- `parameter_uncertainties`、`correlations`、`alternative_models`。

### `scattering-size-or-correlation-analysis`

字段：`q_range`、`model`、`contrast_or_scattering_length_density`、`background`、`instrument_smearing`、`size_or_correlation_property_ids`、`distribution_assumption`、`fit_diagnostics`、`model_nonuniqueness`。

### `pair-distribution-analysis`

字段：`qmin`、`qmax`、`r_range`、`correction_pipeline`、`model`、`scale_and_resolution_parameters`、`fit_diagnostics`、`local_or_average_structure_scope`。

## 4. 硬审计

1. 原始、校正、计算和差值曲线分别保存。
2. 峰匹配不自动证明相纯度、价态或含量。
3. Scherrer 尺寸必须保存峰、形状因子、仪器展宽和应变假设。
4. Rietveld 拟合优度不单独证明结构唯一或正确。
5. 非晶宽峰、纳米尺寸、缺陷和背景之间保留歧义。
6. 多相定量保存吸收、织构、微吸收和内标假设。

## 5. 规范依据

- IUCr crystallographic metadata catalogue: https://www.iucr.org/resources/data/dddwg/metadata-catalogue
- IUCr powder CIF dictionary: https://www.iucr.org/resources/cif/dictionaries/browse/cif_pd
- IUCr Rietveld reporting guidance: https://journals.iucr.org/services/cif/powder.html
- NeXus diffraction and scattering definitions: https://manual.nexusformat.org/classes/applications/index.html
