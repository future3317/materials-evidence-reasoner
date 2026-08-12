# Error Attribution, Anomaly Chain, Information Gap and PSPP Contract 4.6

本契约定义材料实验偏差诊断中四类容易被模型“说得像、但没有真正做”的能力：误差归因、异常传播链、信息缺口驱动实验，以及 PSPP 经验沉淀。它是跨领域通用合同；领域 adapter 只能补充变量和方法，不能降低证据、可比性或安全要求。

## 1. 术语边界

本项目中的 **PSPP** 固定指：

`Processing（加工/工艺） → Structure（结构/状态） → Properties（材料性质） → Performance（器件/系统/应用表现）`

前驱体纯度、粒度、比表面积、含水率等记为上游 `material-attributes`，不能与 `properties` 混为一类。某些研发任务只有材料性质而没有明确器件表现；此时 `performance` 可标为 `not-applicable`，但不得把同一观测同时复制成 properties 和 performance 来伪造完整链条。

## 2. Stage 3.5：误差结构与归因

### 2.1 何时执行

以下任一条件满足时执行：

- 有重复测量、重复样、批次、设备或操作者层级；
- 用户要求判断差异是否真实；
- 偏差大小接近报告误差或历史波动；
- 使用拟合、校正、图像分割、等效电路、反演或代理模型；
- 结果将用于规格判定、机理升级或工艺变更。

数据不足时仍创建 `error_budget`，但方法标为 `insufficient-data` 或 `expert-ordinal`，明确不能量化总不确定度。

### 2.2 误差结构树

至少检查：

1. `measurement-repeatability`：同一对象重复测量、采样噪声、短期仪器波动；
2. `measurement-calibration`：标准样、零点、漂移、校准模型与有效期；
3. `data-processing`：基线、窗口、拟合、分割、删点、人工选择与公式；
4. `sample-within-batch`：同批次位置、试样、视场或电芯差异；
5. `batch-between`：原料、制备批次、日期、设备或操作者差异；
6. `process-control`：温度、压力、时间、速率、流量、气氛等实际控制波动；
7. `environment`：湿度、环境暴露、存储、老化与测试环境；
8. `model-fit` / `model-extrapolation`：参数不确定度、模型失配、外推和域外预测；
9. `covariance`：误差源相关性；不能默认所有输入独立；
10. `unallocated`：设计无法识别的剩余变异。

### 2.3 量化规则

- 有明确函数关系时，可使用灵敏度系数和不确定度传播；必须记录公式、输入记录、协方差假设和单位。
- 有层级重复设计时，可使用方差分量、Gauge R&R、bootstrap 或稳健分层统计；必须记录重复结构和适用条件。
- 只有不同量纲或不同统计基础的误差源时，不得给“贡献百分比”。改用 `qualitative` 或区间等级。
- 只有在所有分量共享同一贡献基础时，才允许 `fraction_of_total`；完整分解总和应接近 1，并保留 `unallocated`。
- 不得把标准差、标准误、置信区间、仪器精度、容差和 expanded uncertainty 互换。
- 不得把模型交叉验证误差当成实验测量不确定度。

### 2.4 对偏差分类的约束

比较的是“效应”与“综合不确定度/过程变异”，不是简单比较两个百分数：

- 若误差区间覆盖观察效应，或不确定度与效应同量级，优先使用 `inconclusive`、`expected-variation`、`data-quality-suspect` 或 `protocol-shift`；
- 若综合不确定度明显小于效应，可继续材料/工艺机理分析，但仍需检查批次和协议；
- 若坚持在不确定度占主导时判为 `material-process-deviation` 或 `promising-outlier`，必须给 `override_justification`，说明独立证据为什么足以越过误差闸门。

“某误差来源占总方差 50%”只说明它在共同方差基础上主导，不能直接等价为“解释了性能差异的 50%”。

## 3. Stage 5.5：异常传播链追溯

### 3.1 触发条件

偏差分类为 `material-process-deviation`、`promising-outlier` 或 `unexplained-residual` 时执行。若结果属于数据质量、定义或协议问题，可建立以 `measurement-data` 为起点的纠错链，但不得包装成材料机理。

`aligned`、`expected-variation` 和 `not-comparable` 不建立材料异常传播链。

### 3.2 链条结构

可使用以下节点，不要求每条链都机械包含全部节点：

`measurement/data → material-attributes → processing → structure → properties → performance`

每个节点记录：

- 它是 `observed`、`derived`、`hypothesized` 还是 `missing`；
- 绑定的实体、工艺、测量或性质记录；
- 支持证据与限制。

每条边记录：

- 传播机制；
- 证据强度 `direct/indirect/inferred/none`；
- 支持和反证；
- 必要假设；
- falsifier；
- 适用边界。

### 3.3 排序原则

排序同时考虑：

1. 证据覆盖和直接性；
2. 与对象、条件和时间顺序的匹配；
3. 能否被当前实验区分；
4. 是否解释全部关键观测和反证；
5. 路径简洁性。

“路径最短”不能单独获胜；跳过必要中间节点只是把未知藏起来。必须在 `unresolved_node_ids` 和 `chain_evidence_gaps` 中显式登记缺口。

`locally-validated` 要求受控干预支持链上关键关系、主要替代链被排除，并且关键节点不再处于 unresolved 状态。

## 4. Stage 7.1：信息缺口驱动的最小实验集

### 4.1 先列未知，再列仪器

每个 `information_gap` 必须回答：

- 当前决策缺少哪个变量或判据；
- 它位于 measurement/data、material-attributes、processing、structure、properties、performance 或 context 哪一层；
- 它影响哪些偏差事件和假设；
- 当前状态是未测、歧义、冲突、分辨率不足、不可访问还是已解决；
- 最低成本、最直接的测量或补充输入是什么；
- 哪种结果会改变决策。

不得从“常见表征清单”直接生成实验。正确顺序是：

`决策问题 → 竞争假设 → 区分变量 → 最小测量 → 对照与判定规则`

### 4.2 优先级

优先顺序：

1. blocker 和测量系统问题；
2. 能同时区分多个假设或关闭关键传播链节点的实验；
3. 当前设备可做、耗时短、样品消耗低、可逆且安全的实验；
4. 只对参数优化有帮助但不能解释原因的实验。

默认使用 `priority_tier` 和文字理由，不输出伪精确的“信息增益×成本倒数”小数。只有用户提供效用、成本和概率模型时，才可另外计算定量决策价值，并记录假设。

### 4.3 最小实验集

`experiment_set` 用 coverage matrix 说明每个实验覆盖哪些信息缺口和假设。一个合格最小集应：

- 覆盖所有选择继续解决的 blocker/high gap；
- 尽量复用同一配对、随机化或对照设计；
- 明确重复、批次和检测/分辨率要求；
- 预先定义 stop rule；
- 当成本高于决策价值、关键条件无法匹配或安全/权限不满足时，允许结论为“不建议继续”。

## 5. Stage 8：PSPP 经验沉淀

### 5.1 可复用经验的最低结构

每个 `add/revise/supersede` 的 `experience_update` 必须引用 `pspp_map_ids`；确实不适用时，填写 `pspp_exception_reason`。可复用 PSPP map 至少覆盖 canonical PSPP 四层中的三层：

- Processing：有顺序的加工、处理和历史；
- Structure：相、晶粒、孔隙、缺陷、界面、形貌、分布或状态；
- Properties：力学、电学、热学、电化学、光学等材料响应；
- Performance：器件、组件、寿命、稳定性、良率或应用指标。

可选增加 `material-attributes`，表示前驱体或初始材料状态。

### 5.2 关系强度

关系状态：

- `observation`：同一受控条件下直接观察到共同变化，但不声称因果；
- `derived`：由明确公式或数据处理得到；
- `hypothesis`：机理解释，必须有 falsifier；
- `locally-validated`：在明确材料、工艺、设备和测试边界内被干预支持；
- `refuted/conflicting`：被反证或存在不可消解冲突。

不得把“相关”自动升级为“加工决定结构”或“结构导致性能”。每条边单独绑定证据、反证、修饰因素和边界。

### 5.3 版本与持久化

- 单次异常先 quarantine，不进入稳定 baseline；
- 经验追加、不静默覆盖；
- 设备、原料、配方、工艺或测量协议改变时创建新 `regime_id`；
- 只在运行环境支持、用户授权且写入成功时标记 `written-confirmed`；
- 人类报告和仪表盘可展示 PSPP map，但不能把未知节点画成已确认关系。

## 6. 人类报告最低呈现

当相关对象存在时，报告应依次展示：

1. 偏差及误差预算结论；
2. 主要误差来源和未识别部分；
3. 首选异常传播链与链上缺口；
4. 信息缺口清单；
5. 最小实验集、覆盖关系和 stop rule；
6. PSPP 经验图及各关系证据等级。

以自然语言和条件别名为主；完整对象保留在 JSON。仪表盘应允许查看链条和 PSPP 节点，但 JSON 始终是事实源。
