# Materials Simulation Adapter

适配器：`materials-simulation`　层级：`simulation-method`　规则版本：`2.0.0`

<!-- BEGIN GENERATED ROUTING CONTRACT: materials-simulation -->
## 机器可执行路由合同

本节由 `scripts/build_adapter_assets.py` 生成，与 `adapter-routing-lexicon.json` 中 `materials-simulation` / `2.0.0` 同步。关键词命中只负责召回；最终判定必须完成语境、极性、目标实体和文章中心性检查。

| 等级 | signal_id / 概念 | 术语与符号 | 有效证据要求 |
|---|---|---|---|
| 强 | `sim-electronic-atomistic` / executed electronic or atomistic simulation | `密度泛函理论计算`、`第一性原理分子动力学`、`经典分子动力学`、`蒙特卡洛模拟`、`density functional theory calculation`、`ab initio molecular dynamics`、`classical molecular dynamics`、`Monte Carlo simulation`、`DFT`、`AIMD`、`MD`、`MC` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 强 | `sim-meso-continuum` / executed thermodynamic, mesoscale, or continuum simulation | `CALPHAD 计算`、`相场模拟`、`有限元模拟`、`有限体积模拟`、`离散元模拟`、`CALPHAD calculation`、`phase-field simulation`、`finite-element simulation`、`finite-volume simulation`、`discrete-element simulation`、`FEM`、`FVM`、`DEM` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 辅助 | `sim-provenance` / simulation execution provenance | `输入文件`、`代码版本`、`收敛判据`、`边界条件`、`训练集划分`、`随机种子`、`input file`、`code version`、`convergence criterion`、`boundary condition`、`training split`、`random seed` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 弱/召回 | `sim-generic` / generic calculation vocabulary | `计算得到`、`模拟`、`建模`、`预测`、`机器学习`、`calculated`、`simulated`、`modeled`、`predicted`、`machine learning`、`ML` | 必须绑定目标实体；有效语境：title、abstract、methods、results、figure-or-table、conclusion |
| 排除 | `sim-not-executed` / non-executed or non-simulation model | `未来模拟`、`软件功能`、`引用的计算`、`仅解析拟合`、`示意模型`、`future simulation`、`software capability`、`cited calculation`、`analytic fit only`、`schematic model` | 用于排除或消歧；有效语境：future-work、software-description、cited-comparison、analysis-only |

**歧义词消解**

- `model`：候选含义为 executed numerical simulation / analytical fit / conceptual mechanism / machine-learning model。判定规则：Classify the model role and require actual inputs, execution, and outputs for simulation records.
- `calculated`：候选含义为 current-source simulation output / derived arithmetic value / cited result。判定规则：Require method, target, and execution provenance; arithmetic derivation belongs to property derivation, not simulation.

**状态门控**

- `load`：来源与目标实体已解析；至少一个方法级或结果级信号绑定目标；排除语境不能解释全部阳性证据；并满足下列任一领域条件：
  - an actual simulation job has target-bound inputs, method details, and outputs
  - a materials-ML model has a defined dataset, split, task, validation, and target property
- `candidate`：只有弱/辅助词、实体绑定不清、全文不可得、极性未决，或强术语仍有未消除的异义；只保留路由证据，不生成领域记录。
- `skip`：完整来源足以判定该领域不是目标，或全部命中均属于仪器、耗材、基底、容器、引文、否定及未来工作语境。
- 推荐组合加载：`metallic-materials`, `quantum-materials`, `materials-processing`, `diffraction-scattering`。每个适配器仍须独立满足门控。

**记录生成门**：只有 `load` 才能按本文件的记录类型创建 `domain_records[]`；字段必须符合 `adapter-field-contracts.json`，引用已有核心实体/工艺/测量/产物/属性 ID，并提供字段级证据。未报告值保持缺失，不用典型值补齐。
<!-- END GENERATED ROUTING CONTRACT: materials-simulation -->

## 1. 范围与路由

适用于 DFT/第一性原理、分子动力学、蒙特卡洛、CALPHAD、相场、有限元、多物理场和材料机器学习计算。软件只在方法或背景中被提及、未实际执行或结果属于被引工作时不加载。

- `load`：当前来源报告目标实体的实际计算输入、执行或输出。
- `candidate`：只说“calculated/simulated/predicted”而方法、实体或实际执行不清。
- `skip`：仅讨论软件能力、未来计划、引用结果或无关计算。

## 2. 通用运行记录

每个 `simulation_job` 至少记录：

- `simulation_class`、`code`、`code_version`、`build_or_commit`；
- `workflow_id`、父任务、输入任务和输出任务；
- 输入结构/模型实体、来源、坐标、晶胞、边界和约束；
- 方法、参数、参考态、初始条件和随机种子；
- 求解器、收敛阈值、停止条件、重启和失败状态；
- 硬件、并行配置、运行时间和资源限制，在来源支持时记录；
- 输入/输出文件、哈希、日志、警告和软件环境；
- 结果属性、派生链、适用域、验证和限制。

解析成功不等于计算收敛；计算收敛不等于物理模型有效；模型有效不等于实验已验证。

## 3. 记录类型

### `simulation-provenance`

字段：`simulation_job_ids`、`workflow_graph`、`software_environment`、`input_artifact_ids`、`output_artifact_ids`、`log_artifact_ids`、`run_status`、`warnings`、`reproducibility_status`、`missing_dependencies`。

### `electronic-structure-method`

字段：

- `theory_level`、`exchange_correlation`、`dispersion_correction`；
- `basis_or_cutoff`、`pseudopotential_or_paw`、`hubbard_u`；
- `spin_treatment`、`soc`、`magnetic_initialization`；
- `k_point_mesh`、`smearing`、`occupancy`；
- `relaxation_protocol`、`force_tolerance`、`stress_tolerance`、`energy_tolerance`；
- `charge_state`、`defect_correction`、`reference_energy_scheme`。

能带、DOS、能隙、形成能、凸包、声子、弹性和表面能必须保存对应方法、参考态和收敛验证。

### `molecular-simulation-method`

字段：

- `model_or_potential_id`、`model_version`、`parameter_source`、`training_domain`；
- `system_size`、`boundary_conditions`、`ensemble`；
- `integrator`、`time_step`、`duration`、`equilibration`、`production_window`；
- `thermostat`、`barostat`、`temperature_program`、`pressure_program`；
- `long_range_method`、`cutoffs`、`constraints`、`random_seed`；
- `sampling_independence`、`replicate_count`、`finite_size_checks`。

### `continuum-and-mesoscale-method`

字段：

- `method_class`：`phase-field`、`finite-element`、`finite-volume`、`discrete-element`、`other`；
- `governing_equations`、`constitutive_models`、`material_parameters`；
- `geometry`、`mesh`、`mesh_convergence`；
- `initial_conditions`、`boundary_conditions`、`loads`；
- `solver`、`time_integration`、`tolerances`、`stabilization`；
- `parameter_calibration`、`validation_cases`、`scale_linkage`。

### `materials-ml-model`

字段：

- `task`、`target_definition`、`dataset_ids`、`data_split`、`leakage_controls`；
- `features_or_representation`、`model_family`、`hyperparameters`；
- `training_software`、`random_seeds`、`cross_validation`；
- `metrics`、`uncertainty_method`、`calibration`；
- `applicability_domain`、`out_of_distribution_checks`、`external_validation`；
- `model_artifact_ids`、`code_artifact_ids`、`prediction_property_ids`。

### `simulation-experiment-comparison`

字段：`simulation_property_ids`、`experimental_property_ids`、`mapping_assumptions`、`condition_match`、`scale_match`、`agreement_metric`、`discrepancies`、`calibration_or_validation_role`、`assessment`。

## 4. 硬审计

1. 不补写软件默认参数。
2. 不混合不同理论级别、势函数、参考态或修正体系的能量。
3. 不把外推区域预测写成已验证结果。
4. 不以单一随机种子或单次轨迹证明统计稳定。
5. 不忽略尺寸、时间尺度、边界和网格收敛。
6. 不把拟合训练数据称为独立验证。
7. 不把计算趋势直接升级为实验机理。

## 5. 规范依据

- NOMAD MetaInfo: https://nomad-lab.eu/prod/v1/docs/examples/computational_data/metainfo.html
- NOMAD workflows: https://nomad-lab.eu/prod/v1/docs/explanation/workflows.html
- Materials Project calculation details: https://docs.materialsproject.org/methodology/materials-methodology/calculation-details
- OPTIMADE specification: https://www.optimade.org/specification/latest/
