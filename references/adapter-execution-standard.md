# Adapter Execution Standard

本文件是所有领域适配器的规范性执行合同。领域 reference 提供领域内容，`adapter-routing-lexicon.json` 提供机器可读信号，`adapter-field-contracts.json` 提供记录与字段合同；三者冲突时不得输出该领域记录，并在 `missing_information[]` 报告 `adapter-contract-conflict`。

## 1. 三层触发

1. **Skill 触发**：`SKILL.md` frontmatter 只决定是否加载整个材料证据 Skill。
2. **适配器路由**：领域信号只召回候选适配器；依次评估来源位置、极性、文章中心性和目标实体绑定，输出 `load`、`candidate` 或 `skip`。
3. **记录生成**：适配器为 `load` 后，仍须满足具体 `record_type` 的生成条件；不得因为适配器已加载而创建所有记录。

关键词命中不是领域事实。题名、摘要、结果、方法、图表及图注中的目标绑定信号通常比引言、参考文献、设备说明和未来工作更强，但来源位置不能替代实体绑定。

## 2. 信号合同

每个路由信号包含：

- `signal_id`：适配器内稳定 ID；
- `concept`：信号代表的规范概念，而不是某一个字符串；
- `terms_en`、`terms_zh`、`abbreviations`、`symbols`：用于候选召回的表面形式；
- `strength`：`strong`、`supporting`、`weak` 或 `exclusion`；
- `valid_contexts`：该概念可贡献路由证据的位置或语义角色；
- `invalid_contexts`：设备、背景、引文、否定、同形异义等误触发环境；
- `requires_entity_binding`：是否必须绑定目标实体；
- `independence_group`：同一组信号只算一个证据通道，防止同一曲线的多个派生词重复计数。

匹配时保存原词、规范概念、章节、句子极性、实体 ID、证据 ID 和独立通道。字符串或正则只用于召回，不得直接把 `matched=true` 当作 `load`。

## 3. 路由算法

```text
resolve source identity and article profile
resolve target and non-target entities
retrieve candidate adapters from lexical signals
for each adapter:
    classify each signal's polarity and source context
    bind each usable signal to an entity or mark unresolved
    apply adapter exclusions to the matched occurrence, not automatically to the whole paper
    evaluate article centrality and adapter-specific gates
    emit load, candidate, or skip with reason codes
```

### `load`

同时满足：

- 至少一个目标实体已解析；
- 至少一个方法级或结果级证据绑定该目标实体；
- 领域对象、过程、测量或性质是当前来源的实质内容，不是设备/耗材/背景/引文；
- 满足该适配器 `load_gate`；
- 排除信号未解释掉全部正向信号。

### `candidate`

存在领域可能性，但实体、极性、来源位置、文章中心性或最小证据门槛仍有一项未解析。`candidate` 只输出路由证据、歧义和待查信息，不输出该适配器的 `domain_records[]`。

### `skip`

可访问证据只属于设备、耗材、基底、容器、对照、引文、否定、未来工作或明确的异义词；或者来源已足够完整且目标明确不属于该领域。访问内容不足时优先 `candidate`，不要用 `skip` 伪装未知。

## 4. 多适配器组合

适配器按 `material-family`、`physical-form`、`process`、`application`、`measurement-technique`、`simulation-method` 和 `phenomenon` 分层，可同时加载。共享事实只写入核心实体、工艺、测量、数据产物、分析步骤和性质记录；领域记录只保存新增语义与审计判断。

同一字符串可触发多个候选。例如 `electrolyte` 可召回液体、电池和电化学测试；最终由目标角色和文章任务分别路由，不采用单选分类器。

## 5. 记录生成合同

每个 `record_type` 必须声明：

- `description`：该记录表达的一个明确事实单元；
- `create_when`：何时允许生成；
- `do_not_create_when`：常见误生成边界；
- `required_any_of`：至少出现一项的专属字段组；
- `required_context`：必须关联的实体、运行、数据产物、性质或证据；
- `allowed_fields` 与每个字段的类型和语义角色。

只因记录名称看起来适用，不得生成空壳记录。记录中的每个非枚举事实必须能追溯到证据，或者明确标为 `derived`/`inferred` 并保存依据。

## 6. 字段语义约定

后缀具有规范含义：

- `_entity_id` / `_entity_ids`：核心 `entities[]` 引用；
- `_property_id` / `_property_ids`：核心 `property_records[]` 引用；
- `_measurement_run_id` / `_measurement_run_ids`：核心 `measurement_runs[]` 引用；
- `_process_run_id` / `_process_run_ids`：核心 `process_runs[]` 引用；
- `_simulation_job_id` / `_simulation_job_ids`：核心 `simulation_jobs[]` 引用；
- `_artifact_id` / `_artifact_ids`：核心 `data_artifacts[]` 引用；
- `_evidence_id` / `_evidence_ids` 或以 `_evidence` 结尾：证据 ID 或带证据 ID 的结构化判断，不得存无来源结论；
- `_property_ids` 字段不得直接存数值；数值、单位、条件、判据和不确定度进入被引用的 `property_record`；
- `_raw` 保存原文，不静默规范化；`_canonical` 保存有依据的规范映射；
- `*_basis` 保存分母、参考态、归一化或分类依据；
- `*_status`、`*_state` 和 `*_class` 使用领域合同枚举；来源使用合同外术语时保留原词并标记映射状态。

无专属说明的普通字段默认是“来源报告的结构化描述”，不是允许 Agent 自行补全的常识槽位。

## 7. 字段状态与缺失

- `required_when_reported`：来源明确报告该概念时必须抽取；
- `required_for_claim`：要输出某项结论时必须存在，否则结论降级；
- `optional`：有证据时抽取；
- `not_applicable`：由实体或方法类型证明不适用；
- `not_reported`：已检查预期位置但来源未报告；
- `not_accessible`：补充信息、原始数据或正文不可访问；
- `ambiguous`：存在多个不能裁决的解释；
- `conflicting`：来源内部或来源之间明确冲突。

不得用 `null` 同时表示以上状态。决策关键缺失进入 `missing_information[]`，包含影响和解决方式。

## 8. 禁止推断

除非领域 reference 明确允许派生并给出公式，否则禁止：

- 从材料名称、牌号或家族填入组成、结构、工艺或性能；
- 从仪器型号填入实际采集参数；
- 从“标准方法”填入文中未报告的标准版本或参数；
- 从图中趋势填入精确数值；
- 从单一性质异常证明相、机制、失效模式或应用性能；
- 从软件默认值填入实际模拟输入；
- 把背景、对照、基底、容器、导线、集流体或被引材料的事实绑定给目标实体。

## 9. 适配器 Reference 必备结构

每个领域 reference 至少包含：

1. 范围、非范围和层级；
2. 自动生成的“执行路由合同”，与机器词典一致；
3. 实体与快照拆分；
4. 记录类型及字段；
5. 条件化性质或方法要求；
6. 跨字段硬审计；
7. `load`、`candidate`、`skip` 边界例；
8. 权威术语、标准或方法来源。

生成区块由 `scripts/build_adapter_assets.py` 维护，标记之间不得手工修改；领域解释和硬审计由人工维护。

## 10. 质量门槛

适配器晋级 `implemented` 前必须通过：

- 路由词典 Schema 和唯一 ID 检查；
- 每类至少两个正例、两个反例和两个歧义例；
- 记录类型、字段类型和引用目标验证；
- 拼写错误、枚举值混入字段名和无效引用的负向测试；
- 至少一个来源支持的真实正例和一个真实边界例；
- 人工裁决的目标实体与路由状态；
- 与可组合适配器的交叉测试；
- 主输出通过 `output-schema.json` 和 `validate_output.py`。
