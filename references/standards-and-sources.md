# 标准、术语与来源依据

本文件说明本 Skill 的通用合同和领域适配器参考了什么，以及这些来源**没有**授权 Skill 做什么。它是设计依据映射，不复制付费标准正文，不把标准名称当作已执行协议，也不把综述或本体条目当作材料事实。

## 1. 采用原则

1. 优先标准组织、政府实验室、领域本体/数据格式的官方文档和原始论文。
2. 用标准统一概念边界、元数据和报告条件；用原始论文校准真实表达、共载和排除场景。
3. 标准中“应报告”的字段不等于某篇来源“已经报告”；未见证据仍为缺失。
4. 本 Skill 的路由阈值、信号分组和 JSON 封装是内部可执行规范，不宣称获得 ISO、ASTM、IEC、IUPAC、IUCr、NIST 或其他机构认证。
5. 付费或受版权保护的标准只保存标准号、标题、范围与官方链接；执行实验时由用户核对其持有的有效版本。

## 2. 通用表征与数据谱系

### CHADA、CHAMEO 与 EMMO

- EMMC CHADA: https://emmc.eu/moda-chada/chada/
- CHAMEO FAQ: https://emmo-repo.github.io/domain-characterisation-methodology/pages/faq.html

用于形成 `sample/entity -> environment/instrument -> procedure/technique -> raw data -> processing -> property -> data quality` 链，支持测量运行、数据产物、分析步骤和属性记录分离。它不替代具体仪器标准，也不证明来源数据质量合格。

### NeXus application definitions

- Application definitions: https://manual.nexusformat.org/classes/applications/index.html
- Electron microscopy structure: https://manual.nexusformat.org/classes/applications/em-structure.html
- Optical spectroscopy structure: https://manual.nexusformat.org/classes/applications/optical-spectroscopy-structure.html
- Raman application definition: https://manual.nexusformat.org/classes/applications/NXraman.html

用于把“某技术要保存哪些最小上下文”设计成合同，并区分仪器树、原始数据、处理结果和应用定义。Skill 不假装输出文件已经符合 NeXus；只有真正按相应定义验证的文件才能这样声明。

### PMD core ontology 与 NIST MDCS

- PMD core ontology: https://materialdigital.github.io/core-ontology/docs/intro/
- NIST Materials Data Curation System: https://www.nist.gov/programs-projects/materials-data-curation-system

用于材料、制造、表征、数据转换、过程输入/输出及数据策展边界。Skill 采用稳定 ID 和谱系思想，但不声称 JSON 等价于这些系统的原生模型。

## 3. 模拟与计算

- EMMC MODA: https://emmc.eu/moda-chada/moda/
- OPTIMADE specification: https://www.optimade.org/specification/latest/

MODA 支撑模型、求解器、处理器、工作流和输入/输出分层；OPTIMADE 支撑结构数据互操作和实现版本意识。`materials-simulation` 因而要求实际输入、代码/模型、执行、收敛、输出和实验映射，不把“软件可做什么”当成“本文做过什么”。

## 4. 材料家族与物态

### 金属与合金

- ASTM E7 terminology: https://store.astm.org/standards/e7
- ASTM E112 grain size: https://store.astm.org/standards/e112
- ASTM E527 UNS: https://store.astm.org/Standards/E527.htm
- NIST structural materials schema project: https://www.nist.gov/publications/structural-materials-data-demonstration-project-resource-thermal-process-modeling

用于牌号/状态/炉批、晶粒度方法、取样方向、热机械历史及名义成分与实测成分分离。具体性能仍需对应试验方法和有效版本。

### 高分子

- IUPAC Purple Book: https://iupac.org/what-we-do/books/purplebook/
- IUPAC polymer brief guides: https://iupac.org/what-we-do/nomenclature/brief-guides/

用于聚合物名称、组成、架构、摩尔质量与分散度语义。商品名不自动展开为配方，聚合物家族名不自动产生分子量、结晶度或固化状态。

### 陶瓷、玻璃与胶凝材料

- ISO 20507:2022 fine ceramics vocabulary: https://www.iso.org/standard/74705.html
- ASTM C1239 ceramic strength statistics: https://store.astm.org/standards/c1239

用于陶瓷术语、脆性材料强度离散与 Weibull 语境；玻璃和水泥的具体试验仍需对应产品与方法标准。

### 二维材料

- ISO/TS 80004-13:2024 nanotechnologies vocabulary: https://www.iso.org/standard/82855.html

用于区分单层、双层、少层、纳米片、石墨/石墨烯相关材料及二维几何的非材料义。层数必须保留原始定义和测量依据。

### 液体与热物性

- NIST ThermoML: https://www.nist.gov/mml/acmd/trc/thermoml

用于组成、相态、温压、方法、不确定度和热物性条件化表达。溶剂作为清洗剂、浴液或测试环境时不等于目标液体材料。

## 5. 能源与电化学应用

### 电池

- BattINFO: https://www.battinfo.org/
- Battery Data Toolkit schema guide: https://rovi-org.github.io/battery-data-toolkit/user-guide/schemas/source-metadata.html
- Battery Data Format: https://github.com/battery-data-alliance/battery-data-format
- RSC battery experimental reporting: https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/experimental-reporting
- ACS battery reporting checklist: https://pubs.acs.org/doi/10.1021/acsenergylett.1c00870

用于 `active material -> electrode -> cell -> module/pack` 层级、电极配方、面载量、N/P、E/C、化成、循环协议、参考循环、容量/能量基准和退化证据。半电池材料结果不得自动升级为全电池或系统结果。

### 光伏

- IEC 60904-9 solar simulator classification: https://webstore.iec.ch/en/publication/28973
- NREL photovoltaic device performance publications: https://www.nrel.gov/pv/pvdpc/publications

用于器件堆栈、有效/孔径/总面积、光谱与辐照度、参考器件、扫描方向、稳态输出和校准。扫描峰值 PCE 不自动等于稳定功率输出。

### 电化学能源转换

- IUPAC electrochemical terminology recommendations: https://iupac.org/wp-content/uploads/2019/07/PAC-REC-18-01-09R2_PR190703MC.pdf

用于参比电极、电位标度、过电位、电流归一化、iR 校正、Faradaic efficiency 和反应/反应器边界。电池循环、腐蚀、电镀和电化学清洗不自动加载能源转换适配器。

### 储氢

- DOE materials-based hydrogen storage: https://www.energy.gov/cmei/fuels/materials-based-hydrogen-storage
- DOE/NIST best practices: https://www1.eere.energy.gov/hydrogenandfuelcells/pdfs/bestpractices_h2_storage_materials.pdf
- NIST PCT tutorial: https://www.ctcms.nist.gov/hydrogen_storage/tutorials_PCT.html

用于材料/系统基准、总容量/可用容量、吸附/解吸、PCT/PCI、平衡判据、温压、体积校准和活化历史。储氢不等于析氢催化或氢脆。

### 热电

- NIST thermoelectric measurements: https://www.nist.gov/programs-projects/thermoelectric-measurements
- NIST thermoelectric measurement review: https://www.nist.gov/publications/thermoelectric-measurements

用于 Seebeck、电阻率/电导率、热导率、功率因子与 `zT` 的同试样/同方向/同温度追溯，以及接触几何、辐射/热损失和不确定度。

## 6. 常见表征与试验

### 衍射与散射

- IUCr powder CIF dictionary: https://www.iucr.org/resources/cif/dictionaries/cif_pd
- IUCr powder-data CIF guidance: https://journals.iucr.org/services/cif/powder.html

用于辐射源、波长、几何、扫描范围、步长、校准、数据产物、峰处理、结构模型、精修和拟合诊断。计算图谱与实验图谱不得混为同一测量运行。

### 电子显微、光谱、热分析、力学与输运

这些适配器以 CHAMEO/NeXus 的通用表征链为骨架，再保留各技术最小条件：样品制备与位置、仪器/探测器、激励和采集条件、校准、原始数据、处理步骤、模型/判据、统计范围与不确定度。具体执行标准由来源声称的标准号和有效版本决定；Skill 不从技术名称自动补齐电压、激光波长、升温速率、应变速率、场强或软件参数。

## 7. 量子与超导

- DOE Quantum Materials report: https://science.osti.gov/-/media/bes/pdf/reports/2016/BRN_Quantum_Materials_for-Energy_Relevant_Technology.pdf
- NIST quantum transport measurements: https://www.nist.gov/programs-projects/quantum-transport-measurements
- Review of superconductivity: https://harvest.aps.org/v2/journals/articles/10.1103/RevModPhys.71.S313/fulltext

用于命名量子相、量子化输运、拓扑/关联态和超导证据通道的边界。`quantum`、`Tc`、`Hc`、`Jc`、`gap` 等词必须消歧；理论预测、输运零电阻、抗磁响应和热力学异常保留为不同证据通道。

## 8. 版本与复核

来源链接和标准版本会变化。新增或升级 adapter 时应：

1. 记录访问日期、标准/规范版本和变更范围；
2. 更新路由词典、字段合同、合成边界用例和来源支持用例；
3. 运行 `build_adapter_assets.py`、`build_field_contracts.py`、`build_adapter_benchmarks.py`、`build_source_backed_cases.py`；
4. 运行 `validate_output.py --self-test` 与 `evaluate_routing.py --self-test`；
5. 只有独立人工裁决后才把相关案例或 adapter 提升为 `human-adjudicated`。
