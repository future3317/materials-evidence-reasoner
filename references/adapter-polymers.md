# Polymers Adapter

适配器：`polymers`　层级：`material-family`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: polymers -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `polymers` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `pol-polymer-identity` / polymer identity or architecture | `聚合物复合材料`、`高分子纳米复合材料`、`聚合物薄膜`、`聚合物基体`、`均聚物`、`共聚物`、`热塑性塑料`、`热固性树脂`、`弹性体`、`聚合物网络`、`polymer composite`、`polymeric nanocomposite`、`polymer film`、`polymer matrix`、`homopolymer`、`copolymer`、`thermoplastic`、`thermoset`、`elastomer`、`polymer network` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `pol-polymerization` / polymerization or curing | `聚合`、`交联`、`固化反应`、`转化率`、`polymerization`、`crosslinking`、`curing reaction`、`degree of conversion` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `pol-molar-distribution` / molar-mass distribution | `数均摩尔质量`、`重均摩尔质量`、`摩尔质量分散度`、`凝胶渗透色谱`、`number-average molar mass`、`weight-average molar mass`、`molar-mass dispersity`、`gel permeation chromatography`、`Mn`、`Mw`、`SEC`、`GPC` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `pol-generic` / generic polymer vocabulary | `高分子`、`树脂`、`塑料`、`粘结剂`、`薄膜`、`凝胶`、`polymer`、`resin`、`plastic`、`binder`、`film`、`gel` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `pol-consumable` / incidental polymer component | `塑料瓶`、`胶带`、`手套`、`仅作封装`、`非目标粘结剂`、`polymer vial`、`adhesive tape`、`glove`、`encapsulant only`、`incidental binder` | 用于排除或消歧；有效语境：apparatus、sample-mounting、consumable、secondary-component |

**歧义词消解**

- `resin`：候选含义为 target thermoset precursor / generic trade-name material / mounting resin。判定规则：Require target role and formulation, cure, structure, or property evidence.
- `film`：候选含义为 polymer specimen / thin-film form of another material / protective consumable。判定规则：Resolve composition and target role before loading.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - target polymer identity plus formulation, polymerization, cure, morphology, or property evidence
  - molar-mass or polymer-state evidence is bound to the target polymer
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`materials-processing`, `thermal-analysis`, `mechanical-testing`, `spectroscopy`, `composition-particle-surface`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: polymers -->

## 1. 范围与路由

适用于热塑性塑料、热固性树脂、弹性体、共聚物、聚合物共混物、凝胶、纤维和聚合物基复合材料。聚合物仅作为粘结剂、封装或背景组件且不是目标实体时，可保持 `secondary` 或 `skip`。

- `load`：聚合物结构、聚合、分子量、加工、形态、界面、固化或性能属于目标结果。
- `candidate`：只出现商品名、缩写或“resin/polymer”而身份和角色未解析。
- `skip`：仅为非目标耗材、容器、胶带、手套、安装介质或被引背景。

不得从商品名、缩写或单体名称推断完整重复单元、分子量、立构规整性、添加剂或固化状态。

## 2. 目标实体与拆分

优先解析：`polymer-material`、`resin-batch`、`monomer-mixture`、`blend`、`composite`、`film`、`fiber`、`gel`、`cured-specimen`、`aged-specimen`、`interface`。

配方比例、分子量批次、固化程度、含水、加工温度/剪切、退火、取向、调湿、老化和测试历史变化时，通常拆分实体或快照。

## 3. 记录类型

### `polymer-identity`

字段：

- `polymer_class`：`thermoplastic`、`thermoset`、`elastomer`、`gel`、`polymer-composite`、`unknown`；
- `name_raw`、`name_canonical`、`trade_name`、`grade`；
- `constitutional_repeat_unit`、`constitutional_unit_source`；
- `architecture`：线型、支化、星型、梳型、网络、超支化等；
- `copolymer_type`：随机、交替、嵌段、接枝、梯度等；
- `sequence_description`、`tacticity`、`end_groups`；
- `charge_state`、`functionalization`、`bio_or_synthetic_origin`。

### `polymerization-record`

字段：

- `monomer_entity_ids`、`initiator`、`catalyst`、`chain_transfer_agent`、`crosslinker`；
- `polymerization_mechanism`、`polymerization_mode`；
- `solvent`、`concentrations`、`temperature_program`、`pressure`、`atmosphere`、`time`；
- `conversion_property_ids`、`yield_property_ids`；
- `quench_and_purification`、`residual_monomer_property_ids`；
- `process_run_ids`、`evidence_ids`。

### `molecular-distribution-state`

字段：

- `mn_property_ids`、`mw_property_ids`、`mz_property_ids`、`dispersity_property_ids`；
- `degree_of_polymerization_property_ids`；
- `measurement_method`、`calibration_standard`、`absolute_or_relative`；
- `solvent`、`temperature`、`column_or_detector`；
- `branching_or_architecture_assumption`、`distribution_artifact_ids`。

不同 SEC/GPC 标准、绝对法和相对校准结果不可直接合并。

### `polymer-formulation`

字段：

- `component_entity_ids`、`component_roles`；
- `fraction_basis`、`composition_property_ids`；
- `filler`、`fiber`、`plasticizer`、`stabilizer`、`flame_retardant`、`solvent`；
- `dispersion_state`、`interface_treatment`、`coupling_agent`；
- `mixing_order`、`mixing_process_run_ids`。

### `polymer-state`

字段：

- `physical_state`、`crystallinity_property_ids`、`phase_morphology`；
- `tg_property_ids`、`tm_property_ids`、`tc_property_ids`；
- `crosslink_density_property_ids`、`degree_of_cure_property_ids`；
- `orientation`、`residual_stress`、`free_volume`；
- `moisture_property_ids`、`conditioning_history`、`aging_history`；
- `specimen_geometry`、`sampling_location`。

## 4. 条件化性能要求

- 流变/DMA：应变幅、线性区验证、频率、温度程序、夹具、时间温度叠加及移位因子。
- 拉伸/冲击/蠕变：调湿、几何、取向、应变率、温度和测试标准。
- 阻隔/渗透：膜厚、有效面积、温湿度、压差、气体/蒸气、稳态判据。
- 溶胀/溶解：溶剂、浓度、温度、时间、干燥基准和网络状态。
- 热稳定/燃烧：样品质量和几何、气氛、升温程序、点火与终点定义。
- 降解：介质、光谱/剂量、温度、机械载荷、时间和质量/分子量基准。

## 5. 硬审计

1. 不把单体性质转移给聚合物。
2. 不把商品名当成唯一化学身份。
3. 不省略分子量测法和校准基准。
4. 不把未固化、部分固化和完全固化试样合并。
5. 不忽略含水、调湿、取向和热剪切历史。
6. 不将 DSC/DMA 的不同 Tg 判据合并成一个值。

## 6. 规范依据

- NIMS PoLyInfo scope: https://polymer.nims.go.jp/PoLyInfo/guide/en/what_is_polyinfo.html
- NIMS PoLyInfo property catalog: https://polymer.nims.go.jp/PoLyInfo/guide/en/property.html
- IUPAC Polymer Compendium: https://iupac.org/wp-content/uploads/2016/01/Compendium-of-Polymer-Terminology-and-Nomenclature-IUPAC-Recommendations-2008.pdf
- ISO 11357 DSC: https://www.iso.org/standard/83904.html
- ISO 11358 thermogravimetry: https://www.iso.org/standard/79999.html
