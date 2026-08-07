# Electrochemical Testing Adapter

适配器：`electrochemical-testing`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: electrochemical-testing -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `electrochemical-testing` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `echem-sweep-step` / actual voltammetric or chrono method | `循环伏安`、`线性扫描伏安`、`计时电流`、`计时电位`、`旋转圆盘电极`、`cyclic voltammetry`、`linear sweep voltammetry`、`chronoamperometry`、`chronopotentiometry`、`rotating disk electrode`、`CV`、`LSV`、`CA`、`CP`、`RDE`、`RRDE` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `echem-impedance-pulse` / actual impedance or intermittent-titration method | `电化学阻抗谱`、`恒流间歇滴定`、`恒电位间歇滴定`、`腐蚀极化`、`electrochemical impedance spectroscopy`、`galvanostatic intermittent titration`、`potentiostatic intermittent titration`、`corrosion polarization`、`EIS`、`GITT`、`PITT` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `echem-cell-context` / electrochemical cell and potential context | `工作电极`、`参比电极`、`对电极`、`电位标尺`、`iR 补偿`、`working electrode`、`reference electrode`、`counter electrode`、`potential scale`、`iR compensation` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `echem-generic` / generic electrochemical vocabulary | `电化学`、`阻抗`、`极化`、`电极`、`电位`、`electrochemical`、`impedance`、`polarization`、`electrode`、`potential` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `echem-not-test` / non-test electrochemical use | `电化学清洗`、`电解抛光制样`、`未来使用电化学工作站`、`引用的 EIS 结果`、`electrochemical cleaning`、`electropolishing preparation`、`potentiostat listed for future work`、`cited EIS result` | 用于排除或消歧；有效语境：sample-preparation、future-work、cited-comparison |

**歧义词消解**

- `CV`：候选含义为 cyclic voltammetry / coefficient of variation / curriculum vitae。判定规则：Require an electrochemical potential-current scan and cell context.
- `EIS`：候选含义为 electrochemical impedance spectroscopy / unrelated acronym。判定规则：Require frequency-dependent complex impedance or an explicit electrochemical method.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound electrochemical run with cell/electrode context is reported
  - a property or fit derives from target-bound electrochemical data
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`battery`, `electrochemical-energy`, `liquid-materials`, `composition-particle-surface`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: electrochemical-testing -->

## 1. 范围

适用于 CV、LSV、chronoamperometry/chronopotentiometry、恒流充放电、EIS、GITT/PITT、RDE/RRDE、腐蚀极化和一般电化学测量。电池组件和寿命语义由 `battery` 处理；催化器件语义由 `electrochemical-energy` 处理。

## 2. 电池/电解池上下文

记录：

- 两/三/多电极配置、池体类型、几何和有效面积；
- 工作、对、参比电极身份、面积、载量、制备和预处理；
- 参比电极内部溶液、温度、校准和电位标度换算；
- 电解液成分、浓度、体积、pH、水/氧和气体饱和；
- 膜/隔膜、距离、搅拌/旋转、流量、压力、温度和气氛；
- 仪器、通道、量程、采样率、滤波和线缆/屏蔽；
- OCV 稳定、预循环、清洗和测试顺序；
- 原始时间、电位、电流、电荷和频域数据。

## 3. 方法记录

### `voltammetry-analysis`

字段：`method`、`start_vertex_end_potential`、`potential_scale`、`scan_rate`、`cycle_count`、`rotation_rate`、`ir_compensation`、`background_subtraction`、`peak_property_ids`、`onset_property_ids`、`current_property_ids`、`normalization_basis`。

### `galvanostatic-or-potentiostatic-analysis`

字段：`control_mode`、`current_or_potential_steps`、`cutoffs`、`rest_steps`、`sampling`、`capacity_or_charge_property_ids`、`energy_property_ids`、`efficiency_property_ids`、`cycle_index`、`normalization_basis`。

### `eis-analysis`

字段：

- `dc_bias`、`ac_amplitude`、`frequency_range`、`points_per_decade`；
- `equilibration`、`linearity_or_stationarity_check`、`kk_or_consistency_check`；
- `raw_impedance_artifact_ids`、`representation`；
- `equivalent_circuit_or_model`、`initial_values`、`bounds`、`weighting`；
- `fit_parameter_property_ids`、`fit_diagnostics`、`residual_artifact_ids`；
- `model_nonuniqueness`、`physical_assignment_basis`。

### `gitt-or-pitt-analysis`

字段：`pulse_mode`、`pulse_amplitude`、`pulse_duration`、`rest_duration`、`equilibrium_criterion`、`geometry_model`、`active_length_scale`、`diffusion_property_ids`、`voltage_regions_excluded`、`assumptions`。

### `corrosion-polarization-analysis`

字段：`exposure_history`、`potential_range`、`scan_rate`、`ocp_stabilization`、`tafel_fit_regions`、`ir_correction`、`corrosion_potential_property_ids`、`corrosion_current_property_ids`、`corrosion_rate_property_ids`、`equivalent_weight_or_density_basis`。

## 4. 硬审计

1. 所有电位保存原始参比和换算标度。
2. 电流/容量保存面积、质量、体积、ECSA 或器件基准。
3. iR 修正保存方法、比例和原始未修正数据。
4. EIS 等效电路不是唯一机理；保存残差和模型非唯一性。
5. GITT/PITT 扩散系数保存几何、长度尺度和平衡假设。
6. 不静默丢弃首圈、异常圈、负结果或未稳定数据。

## 5. 规范依据

- BattINFO electrochemistry ontology: https://www.big-map.eu/da/dissemination/battinfo
- NREL Battery Data Hub metadata examples: https://batterydata.nrel.gov/
- AnIML analytical data architecture: https://new.animl.org/overview
