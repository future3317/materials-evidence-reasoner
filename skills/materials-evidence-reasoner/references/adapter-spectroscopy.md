# Spectroscopy Adapter

适配器：`spectroscopy`　层级：`measurement-technique`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: spectroscopy -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `spectroscopy` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `spec-actual-technique` / actual spectroscopy measurement | `拉曼光谱`、`红外光谱`、`X 射线光电子能谱`、`X 射线吸收谱`、`核磁共振`、`Raman spectroscopy`、`infrared spectroscopy`、`X-ray photoelectron spectroscopy`、`X-ray absorption spectroscopy`、`nuclear magnetic resonance`、`Raman`、`FTIR`、`XPS`、`XAS`、`NMR` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `spec-feature-analysis` / spectral feature analysis | `峰拟合`、`结合能校准`、`化学位移`、`吸收边`、`光致发光寿命`、`peak fitting`、`binding-energy calibration`、`chemical shift`、`absorption edge`、`photoluminescence lifetime` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `spec-data` / target-bound spectrum or assignment | `光谱`、`谱带归属`、`振动模式`、`氧化态归属`、`光学跃迁`、`spectrum`、`band assignment`、`vibrational mode`、`oxidation-state assignment`、`optical transition` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `spec-generic` / generic spectral vocabulary | `光谱学`、`谱学`、`谱带`、`峰`、`信号`、`spectroscopy`、`spectral`、`band`、`peak`、`signal` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `spec-apparatus` / spectroscopy apparatus or cited result | `光谱仪窗口`、`滤光片`、`激光器参数`、`文献光谱`、`spectrometer window`、`optical filter`、`laser specification`、`literature spectrum` | 用于排除或消歧；有效语境：apparatus、source-description、cited-comparison |

**歧义词消解**

- `band`：候选含义为 spectral band / electronic band / mechanical band / range。判定规则：Resolve from the measurement axis, technique, and analysis object.
- `NMR`：候选含义为 nuclear magnetic resonance / unrelated acronym。判定规则：Require a spectroscopy method, nucleus, field, or spectrum.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual target-bound spectrum or spectroscopy run is reported
  - a target chemical, vibrational, electronic, optical, or magnetic-state result derives from spectral data
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`composition-particle-surface`, `quantum-materials`, `two-dimensional-materials`, `materials-simulation`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: spectroscopy -->

## 1. 范围与子类型

适用于 Raman、FTIR、UV-Vis、吸收/反射、PL、XPS、UPS、AES、XAS、NMR、Mossbauer 和相关光谱。先记录 `spectroscopy_subtype`，再加载对应条件；不同光谱的峰不能共享一套默认解释。

## 2. 通用采集字段

- 激发/辐射源、波长/能量、功率或通量、线宽和偏振；
- 光斑、采样深度、入射/收集几何、角度和方向；
- 光栅/单色器、狭缝、分辨率、探测器和响应校准；
- 积分时间、累计次数、扫描范围、步长、采样模式；
- 样品制备、厚度、基底、容器、浓度和光程；
- 温度、压力、气氛、磁/电场和原位刺激；
- 能量/波数/强度校准、暗电流、空白、背景和参考；
- 原始谱、校正谱、归一化谱、拟合谱和残差。

## 3. 子类型条件

### Raman/PL

记录激光波长、样品处功率、光斑、物镜、偏振、光栅、光谱分辨率、积分、累积、宇宙射线处理、基线、峰模型、映射步长及激光损伤检查。

### FTIR/UV-Vis/吸收反射

记录透射/反射/ATR/漫反射模式、附件、背景、光程、浓度、基底、积分球、参考材料、谱带转换和 Kubelka-Munk/Tauc 等模型假设。

### XPS/UPS/AES

记录源、通能、步长、光斑、出射角、分析面积、真空、溅射条件、充电中和、结合能校正、背景、峰型、约束、灵敏度因子和深度剖析。污染碳校正、价态拟合和峰归属保留替代解释。

### XAS

记录边、束线、单色器、能量校准、透射/荧光模式、探测器、样品厚度/稀释、自吸收、扫描次数、归一化、k/r 区间、窗函数和路径模型。

### NMR/Mossbauer

记录核/同位素、场强、频率、脉冲序列、转速、弛豫延迟、温度、参考物；Mossbauer 保存源、速度校准、几何、温度、谱线模型和超精细参数。

## 4. 分析记录

### `spectral-feature-analysis`

字段：`feature_assignments`、`peak_position_property_ids`、`width_property_ids`、`area_or_intensity_property_ids`、`baseline_model`、`peak_model`、`constraints`、`fit_range`、`residual_artifact_ids`、`assignment_sources`、`alternative_assignments`。

### `chemical-state-assessment`

字段：`species_or_states`、`reference_energy`、`charge_correction`、`quantification_method`、`sensitivity_factors`、`state_fraction_property_ids`、`depth_scope`、`model_dependence`、`conflicting_evidence`。

### `optical-transition-assessment`

字段：`transition_type`、`measurement_mode`、`bandgap_or_transition_property_ids`、`model`、`fit_window`、`thickness_or_path_length`、`direct_or_indirect_assumption`、`excitonic_or_defect_alternatives`。

## 5. 硬审计

1. 峰位置、面积和价态依赖校准、背景、峰型与约束。
2. 不以数据库峰位匹配单独证明化学物种。
3. 不用归一化谱做绝对强度比较，除非归一化基准一致。
4. Tauc、Kubelka-Munk、峰分解和 EXAFS 拟合结果标记模型依赖。
5. 光束/激光损伤、充电、自吸收、荧光饱和和基底信号进入限制。

## 6. 规范依据

- ISO 16243 XPS reporting: https://www.iso.org/standard/30222.html
- ISO 19318 XPS charge control/correction: https://www.iso.org/standard/81448.html
- ISO 19830 XPS peak fitting: https://www.iso.org/standard/66294.html
- AnIML analytical data standard: https://new.animl.org/overview
- NeXus optical/photoemission definitions: https://manual.nexusformat.org/classes/applications/index.html
