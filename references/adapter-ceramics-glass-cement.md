# Ceramics, Glass, and Cement Adapter

适配器：`ceramics-glass-cement`　层级：`material-family`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: ceramics-glass-cement -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `ceramics-glass-cement` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `cer-inorganic-product` / target inorganic nonmetallic product | `先进陶瓷`、`玻璃陶瓷`、`耐火材料`、`水泥浆体`、`砂浆`、`混凝土`、`advanced ceramic`、`glass-ceramic`、`refractory`、`cement paste`、`mortar`、`concrete` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `cer-forming-firing-curing` / ceramic, glass, or cement process | `粉体压制`、`烧结`、`玻璃熔制`、`退火点`、`水泥水化`、`养护龄期`、`powder pressing`、`sintering`、`glass melting`、`annealing point`、`cement hydration`、`curing age` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `cer-state` / inorganic microstructure or state | `生坯`、`烧结体`、`玻璃相`、`熟料相`、`水灰比`、`green body`、`fired body`、`vitreous phase`、`clinker phase`、`water-cement ratio`、`w/c`、`w/b` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `cer-generic` / generic ceramic vocabulary | `陶瓷`、`玻璃`、`水泥`、`氧化物`、`碳化物`、`氮化物`、`陶瓷片`、`ceramic`、`glass`、`cement`、`oxide`、`carbide`、`nitride`、`pellet` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `cer-apparatus` / incidental inorganic component | `氧化铝坩埚`、`玻璃载片`、`陶瓷样品架`、`石英窗口`、`alumina crucible`、`glass slide`、`ceramic holder`、`quartz window` | 用于排除或消歧；有效语境：apparatus、container、substrate、sample-mounting |

**歧义词消解**

- `glass`：候选含义为 target amorphous material / glass substrate or window / glass fiber reinforcement。判定规则：Resolve product role and whether glass-specific composition, process, state, or property is studied.
- `cement`：候选含义为 hydraulic binder / dental cement / adhesive cement / verb。判定规则：Require a material entity and application-consistent evidence.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - target ceramic/glass/cement identity plus batch, forming, thermal history, curing, structure, or property evidence
  - a domain-specific state such as green body, glass network, clinker/hydrate, or refractory is a study object
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`materials-processing`, `thermal-analysis`, `mechanical-testing`, `diffraction-scattering`, `electron-microscopy-microanalysis`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: ceramics-glass-cement -->

## 1. 范围与子类型

适用于致密/多孔陶瓷、耐火材料、玻璃、玻璃陶瓷、水泥、砂浆、混凝土和无机胶凝材料。使用 `subdomain` 区分 `ceramic`、`glass`、`glass-ceramic`、`cementitious`、`refractory`，不要把它们的专属字段互设为全局必填。

- `load`：目标实体的无机组成、粉体、成型、烧结/熔制/养护、相与孔隙或性能是核心证据。
- `candidate`：仅出现“ceramic/glass/cement”类别词，具体角色或目标实体不明。
- `skip`：仅为坩埚、窗口、基底、研磨介质、绝缘件、建筑背景或被引材料。

## 2. 实体拆分

解析 `raw-batch`、`powder-lot`、`green-body`、`fired-body`、`glass-melt`、`annealed-glass`、`cement-paste`、`mortar`、`concrete`、`specimen`、`phase`、`pore-network`。

粉体批次、配料、成型、脱脂、烧结、熔制、退火、养护龄期、含水状态和试样几何变化时拆分实体或快照。

## 3. 通用记录

### `inorganic-batch-composition`

字段：`subdomain`、`component_entity_ids`、`composition_basis`、`raw_material_purity`、`impurity_property_ids`、`batching_method`、`loss_on_ignition_property_ids`、`volatile_components`。

### `powder-and-forming-state`

字段：

- `particle_size_property_ids`、`specific_surface_area_property_ids`、`agglomeration_state`；
- `binder`、`dispersant`、`plasticizer`、`solids_loading_property_ids`；
- `forming_method`、`forming_pressure_property_ids`、`green_density_property_ids`；
- `debinding_process_run_ids`、`sintering_process_run_ids`；
- `atmosphere`、`temperature_program`、`cooling_program`。

### `ceramic-microstructure-state`

字段：

- `phase_names`、`phase_fraction_property_ids`；
- `grain_size_property_ids`、`grain_morphology`、`texture`；
- `bulk_density_property_ids`、`true_density_property_ids`；
- `open_porosity_property_ids`、`closed_porosity_property_ids`、`pore_size_property_ids`；
- `defects`、`secondary_phases`、`interface_state`；
- `section_plane`、`sampling_scope`、`statistics_scope`。

## 4. 子领域记录

### `glass-state`

字段：

- `glass_family`、`network_formers`、`modifiers`、`intermediates`；
- `melt_process_run_ids`、`quench_rate`、`annealing_process_run_ids`；
- `amorphous_fraction_property_ids`、`crystalline_fraction_property_ids`；
- `tg_property_ids`、`softening_point_property_ids`、`annealing_point_property_ids`；
- `viscosity_temperature_property_ids`、`refractive_index_property_ids`；
- `transmission_property_ids`、`chemical_durability_property_ids`、`devitrification_state`。

### `cementitious-state`

字段：

- `binder_components`、`clinker_phases`、`supplementary_cementitious_materials`；
- `aggregate`、`admixtures`、`water_binder_ratio_property_ids`；
- `particle_size_property_ids`、`mixing_process_run_ids`、`casting_method`；
- `curing_temperature`、`curing_relative_humidity`、`curing_medium`、`age`；
- `hydration_degree_property_ids`、`heat_of_hydration_property_ids`；
- `workability_property_ids`、`setting_time_property_ids`；
- `shrinkage_property_ids`、`permeability_property_ids`、`durability_property_ids`。

龄期、养护和试样尺寸必须绑定强度及耐久性结果。

## 5. 脆性性能要求

- 强度：试样尺寸、制样、表面、缺陷总体、加载速率、环境、夹具和失效位置。
- 统计：试样数、分布、均值/标准差、Weibull 参数和置信区间。
- 断裂韧性：方法、裂纹/缺口制备、尺寸有效性、R 曲线或单值定义。
- 多孔陶瓷：孔隙率、孔结构、各向异性和承载截面。
- 热震：热循环、介质、温差、残余强度或失效判据。

## 6. 硬审计

1. 不混淆体密度、真密度和相对密度。
2. 不混淆开孔、闭孔和总孔隙率。
3. 不从单个强度值推断总体可靠性。
4. 不忽略制样引入的表面缺陷和尺寸效应。
5. 不把水泥不同龄期或养护条件的性能直接比较。
6. 不把宽散射峰自动判作完全非晶。

## 7. 规范依据

- NIST ceramic phase diagrams: https://www.nist.gov/srd/nist-standard-reference-database-31
- ASTM C1161 ceramic flexural strength: https://store.astm.org/c1161-02cr08e01.html
- ASTM C1499 biaxial strength: https://store.astm.org/c1499-19.html
- ASTM C1674 porous ceramics: https://store.astm.org/c1674-16.html
- ISO 679 cement strength: https://www.iso.org/standard/45568.html
