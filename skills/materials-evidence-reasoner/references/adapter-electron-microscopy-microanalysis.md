# Electron Microscopy and Microanalysis Adapter

适配器：`electron-microscopy-microanalysis`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: electron-microscopy-microanalysis -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `electron-microscopy-microanalysis` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `em-imaging` / actual electron microscopy imaging | `扫描电子显微镜`、`透射电子显微镜`、`扫描透射电子显微镜`、`高分辨透射电镜`、`scanning electron microscopy`、`transmission electron microscopy`、`scanning transmission electron microscopy`、`high-resolution TEM`、`SEM`、`TEM`、`STEM`、`HRTEM` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `em-microanalysis` / electron-beam microanalysis | `能量色散 X 射线谱`、`电子能量损失谱`、`电子背散射衍射`、`选区电子衍射`、`energy-dispersive X-ray spectroscopy`、`electron energy-loss spectroscopy`、`electron backscatter diffraction`、`selected-area electron diffraction`、`EDS`、`EDX`、`EELS`、`EBSD`、`SAED` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `em-quantification` / image or map quantification | `取向图`、`元素面分布`、`图像分割`、`粒径分布`、`晶粒图`、`orientation map`、`elemental map`、`segmentation`、`particle-size distribution`、`grain map` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `em-generic` / generic microscopy vocabulary | `显微图`、`电子图像`、`显微观察`、`面扫描`、`micrograph`、`electron image`、`microscopy`、`mapping` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `em-support` / microscopy support or apparatus | `TEM 载网`、`SEM 样品台`、`仅用于成像的喷碳`、`仅引用电子显微镜`、`TEM grid`、`SEM stub`、`carbon coating for imaging`、`electron microscope cited only` | 用于排除或消歧；有效语境：sample-mounting、apparatus、cited-method |

**歧义词消解**

- `mapping`：候选含义为 elemental/orientation map / generic spatial mapping / mathematical mapping。判定规则：Require an electron microscopy modality and target-bound artifact.
- `carbon coating`：候选含义为 target coating / conductive preparation layer。判定规则：Do not assign the preparation coating to target composition unless explicitly studied.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a target-bound electron image, spectrum, diffraction pattern, or map is available with an actual run
  - quantification or interpretation derives from target-bound electron microscopy data
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`composition-particle-surface`, `diffraction-scattering`, `metallic-materials`, `two-dimensional-materials`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: electron-microscopy-microanalysis -->

## 1. 范围

适用于 SEM、TEM、STEM、FIB、cryo-EM 材料表征、电子衍射、EDS/EDX、EELS 和 EBSD。光学显微或 AFM 可复用通用图像规则，但不应伪装成电子显微子类型。

必须区分一次显微镜 session、一次采集运行、一个视场/位置、一种信号和后续图像分析。拼图、映射和断层数据保留维度与坐标变换。

## 2. 制样与实体绑定

记录样品来源、取样位置、截面、方向、厚度、抛光、离子减薄、FIB lift-out、镀膜、染色/冷冻、支撑膜和保护层。束流损伤、污染、充电、漂移和制样伪影作为限制。

局部图像不能代表整批。每个图像、谱、图或地图绑定明确实体和空间位置；无法绑定时保持 `candidate`。

## 3. 采集字段

- `modality`、`imaging_mode`、`signal_type`；
- 仪器、电子/离子柱、探测器和控制软件；
- `accelerating_voltage`、`beam_current`、`probe_size`、`convergence_angle`；
- `working_distance`、`camera_length`、`magnification`、`pixel_size`；
- `dwell_time`、`frame_count`、`scan_rotation`、`dose_or_dose_rate`；
- `stage_position`、`tilt`、`azimuth`、`sample_orientation`；
- 真空、温度、气氛、偏压、原位载荷；
- 标尺/畸变/相机长度/能量校准；
- 数据维度、单位、原始文件和元数据提取来源。

## 4. 分析记录

### `image-quantification`

字段：`input_artifact_ids`、`region_of_interest`、`preprocessing_steps`、`segmentation_method`、`thresholds`、`manual_edits`、`excluded_objects`、`pixel_calibration`、`sampling_strategy`、`object_count`、`distribution_property_ids`、`uncertainty_or_sensitivity`。

### `eds-composition-analysis`

字段：`detector`、`takeoff_geometry`、`live_time`、`dead_time`、`energy_calibration`、`lines_used`、`background_model`、`overlap_handling`、`quantification_method`、`standards_or_standardless`、`absorption_or_thickness_correction`、`composition_property_ids`、`detection_limits`。

### `eels-analysis`

字段：`collection_angle`、`convergence_angle`、`dispersion`、`energy_resolution`、`zero_loss_alignment`、`background_model`、`plural_scattering_correction`、`edge_windows`、`cross_sections`、`thickness_property_ids`、`chemical_state_property_ids`。

### `ebsd-analysis`

字段：`step_size`、`pattern_resolution`、`indexing_library`、`phase_models`、`confidence_or_quality_thresholds`、`cleanup_steps`、`grain_reconstruction_rule`、`minimum_grain_size`、`reference_frame`、`grain_or_texture_property_ids`、`unindexed_fraction_property_ids`。

### `electron-diffraction-analysis`

字段：`diffraction_mode`、`camera_length_calibration`、`zone_axis`、`aperture_or_probe_size`、`indexing_method`、`candidate_structures`、`dynamical_scattering_limitations`、`orientation_or_lattice_property_ids`。

## 5. 硬审计

1. 不从文件名或倍率标签推断像素尺寸。
2. 不静默裁剪标尺、改变纵横比或覆盖原图。
3. 图像增强、去噪、反卷积和 AI 分割必须保留参数和输入。
4. EDS/EELS 局部定量不能自动代表总体成分。
5. EBSD 清理不能覆盖原始索引率和阈值敏感性。
6. 漂移、束损伤、充电、厚度和制样伪影必须进入限制。

## 6. 规范依据

- NeXus NXem: https://manual.nexusformat.org/classes/applications/em-structure.html
- NIST NexusLIMS: https://www.nist.gov/publications/nexuslims-laboratory-information-management-system-shared-use-electron-microscopy
- ISO 13067 EBSD grain size: https://www.iso.org/standard/74309.html
