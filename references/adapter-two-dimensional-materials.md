# Two-Dimensional Materials Adapter

适配器：`two-dimensional-materials`　层级：`material-family`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: two-dimensional-materials -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `two-dimensional-materials` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `twod-layer-count` / defined one-to-few-layer material | `单层`、`双层`、`少层`、`单层石墨烯`、`二维材料`、`monolayer`、`bilayer`、`few-layer`、`single-layer graphene`、`two-dimensional material`、`1LG`、`2LG`、`FLG`、`2D` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `twod-production-stack` / 2D production or stacking | `机械剥离`、`液相剥离`、`层转移`、`范德华异质结构`、`扭转角`、`mechanical exfoliation`、`liquid-phase exfoliation`、`layer transfer`、`van der Waals heterostructure`、`twist angle` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `twod-dimension-evidence` / thickness or layer-resolved evidence | `层数`、`片层厚度`、`拉曼层数判定`、`原子层`、`layer number`、`flake thickness`、`Raman layer identification`、`atomic layer` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `twod-generic` / generic dimensional vocabulary | `二维`、`层状`、`纳米片`、`薄片`、`超薄`、`2D`、`layered`、`nanosheet`、`flake`、`ultrathin` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `twod-false-sense` / non-material two-dimensional use | `二维图`、`二维图像`、`二维模拟`、`二维探测器`、`仅块体层状晶体`、`two-dimensional plot`、`2D image`、`two-dimensional simulation`、`2D detector`、`bulk layered crystal only` | 用于排除或消歧；有效语境：data-visualization、simulation-dimensionality、instrument、bulk-material |

**歧义词消解**

- `2D`：候选含义为 two-dimensional material / plot or image dimensionality / simulation dimensionality / detector geometry。判定规则：Require a physical sheet/flake/layer entity or explicit material definition.
- `graphene`：候选含义为 single-layer graphene / few-layer graphene / graphene oxide / graphitic additive。判定规则：Preserve the source term and layer evidence; do not normalize all graphene-related materials to graphene.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - a target physical sheet, flake, layer, heterostructure, or 2D device entity is resolved with layer/form evidence
  - production or layer-dependent properties are central results
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`quantum-materials`, `materials-processing`, `electron-microscopy-microanalysis`, `spectroscopy`, `electrical-magnetic-transport`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: two-dimensional-materials -->

## 1. 范围与路由

适用于石墨烯及相关二维材料、层状化合物的单层/少层片、二维异质结构和莫尔体系。仅因块体材料具有层状晶体结构，不自动认定为二维材料。

- `load`：目标实体明确为片层、二维薄片、单层/少层、二维异质结构，且制备或二维相关性质是中心证据。
- `candidate`：只出现“2D/layered/nanosheet”或层数不清、目标实体未绑定。
- `skip`：仅块体层状材料、二维图像、二维模拟网格、基底或被引背景。

## 2. 形态先行

首先分类 `sheet-on-substrate`、`free-standing-sheet`、`flake-powder`、`liquid-dispersion`、`assembled-film`、`heterostructure`、`device`。不同形态需要不同采样、制样和测量规则。

## 3. 记录类型

### `two-dimensional-identity`

字段：

- `material_name_raw`、`material_name_canonical`、`composition`、`polytype_or_allotrope`；
- `form`、`layer_class`、`layer_count_property_ids`、`thickness_property_ids`；
- `lateral_size_property_ids`、`coverage_property_ids`、`flake_shape`；
- `stacking_order`、`twist_angle_property_ids`、`interlayer_spacing_property_ids`；
- `substrate_entity_ids`、`encapsulation_entity_ids`、`heterostructure_sequence`；
- `orientation`、`alignment`、`reference_axis`。

单层、双层、少层和多层必须依据来源判据；厚度与层数的换算记录模型和材料假设。

### `two-dimensional-production`

字段：

- `production_route`：机械/液相/电化学剥离、CVD、MBE、外延、转化、溶液合成等；
- `precursor_entity_ids`、`growth_substrate_entity_ids`、`catalyst_entity_ids`；
- `growth_process_run_ids`、`exfoliation_process_run_ids`、`transfer_process_run_ids`；
- `transfer_support`、`cleaning`、`annealing`、`storage_conditions`；
- `yield_property_ids`、`size_selection`、`contamination_risk`。

### `two-dimensional-structure-quality`

字段：

- `defect_classes`、`defect_density_property_ids`、`disorder_property_ids`；
- `grain_size_property_ids`、`grain_boundary_state`、`edge_state`；
- `roughness_property_ids`、`wrinkle_or_fold_state`；
- `strain_property_ids`、`doping_property_ids`；
- `surface_chemistry_property_ids`、`oxidation_property_ids`、`functionalization`；
- `contamination`、`spatial_uniformity`、`sampling_map_artifact_ids`。

### `two-dimensional-device-context`

字段：`device_architecture`、`channel_geometry`、`contact_materials`、`gate_stack`、`dielectric`、`encapsulation`、`fabrication_process_run_ids`、`measurement_orientation`、`active_area`。

## 4. 条件化测量

- Raman：激发波长/功率、光斑、偏振、基底、峰拟合和空间采样；峰比不能脱离材料和缺陷区间机械换算。
- AFM：模式、探针、基底、台阶定义、吸附层和统计位置。
- TEM：转移/制样、束流剂量、衍射/成像条件和局部代表性。
- XPS/TGA/ICP-MS/FTIR：粉体或分散液制样、背景、定量模型和化学状态。
- 输运：器件几何、接触、栅压、温度、磁场、方向和历史。
- 分散液：溶剂、浓度、稳定性、采样位置和片层尺寸/厚度联合分布。

## 5. 硬审计

1. 不把“层状”自动等同于“二维”。
2. 不用单个位置的层数代表整片或整批。
3. 不忽略基底、封装、污染、应变和储存。
4. 不把厚度、层数和横向尺寸各自的边缘分布错误拼成联合分布。
5. 不把理论单层性质赋给实验多层、缺陷或基底支撑样品。
6. 不把器件性能直接归因于二维材料本体而忽略接触和界面。

## 6. 规范依据

- ISO/TS 9651 classification framework: https://www.iso.org/standard/84232.html
- ISO/TR 19733 property-method matrix: https://www.iso.org/standard/66188.html
- ISO/TS 23359 chemical characterization: https://www.iso.org/obp/ui#iso:std:iso:ts:23359:ed-1:v1:en
- NPL graphene structural characterization guide: https://eprintspublications.npl.co.uk/8654/1/mgpg145.pdf
