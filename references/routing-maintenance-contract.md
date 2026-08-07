# Routing and Semantic-Match Maintenance Contract

本文件和 `adapter-routing-lexicon.json` 是领域路由的外部维护层。`SKILL.md` 只规定何时加载它们；不要把领域关键词、同义词和歧义词重新写回 SKILL 正文。

## 1. 权威文件与依赖

| 目的 | 权威文件 | 生成/消费方 |
|---|---|---|
| 领域范围、边界和字段解释 | `adapter-*.md` | LLM 按需读取 |
| 机器可读信号、同义词、排除词和歧义词 | `adapter-routing-lexicon.json` | `build_adapter_assets.py`、`validate_output.py` |
| 词典结构 | `adapter-routing-lexicon.schema.json` | JSON Schema 校验 |
| 适配器状态、组合和相对引用 | `adapter-registry.json` | 路由与验证器 |
| 记录字段与类型 | `adapter-field-contracts.json` | 记录生成与验证 |
| 用户输入字段别名 | `intake-field-aliases.json` | `prepare_intake.py` |

JSON 词典是可编辑的规范源。`scripts/build_adapter_assets.py` 只读取它并刷新 reference 中的 generated block，不再用 Python 内置词表覆盖 JSON。

## 2. LLM 语义匹配顺序

关键词、缩写和符号只负责高召回候选检索；它们不是事实，也不是 `load` 信号。对每个候选按以下顺序判断：

1. 解析来源身份、目标材料/样品/设备和文章中心性；
2. 根据 `concept` 判断出现内容是否表达该规范概念，而不要求表面字符串完全相同；
3. 记录原词、规范概念、来源章节/页码、句子极性、目标实体和 `evidence_id`；
4. 检查 `valid_contexts` 与 `invalid_contexts`，排除引言转述、参考文献、设备、基底、容器、否定和未来工作；
5. 处理 `ambiguous_terms`，没有足够上下文时保留 `candidate`，不要强行归一化；
6. 按 `independence_group` 去重，同一实验或同一曲线的多个术语不重复计数；
7. 只有满足适配器 `load_gate` 后才生成领域记录，不能因词命中创建空壳记录。

## 3. 如何维护词典

新增术语时：

- 先确认它对应已有 `concept`；若概念不同，新增 signal，不把无关同义词塞进旧 signal；
- 目标结果/方法术语放 `strong` 或 `supporting`，宽泛词放 `weak`；
- 设备、背景、同形异义和非目标角色优先放 `exclusion`，并写入对应 `valid_contexts`；
- 中英文、缩写、符号分开保存；保留原始大小写和连字符，不把规范化后的词替代原词；
- 常见歧义必须补进 `ambiguous_terms`，`resolution_rule` 要说明需要哪些实体、方法、单位或语境；
- 不因为一次误触发就删除已有术语；优先增加排除语境或调整信号强度，并保留回归案例；
- 不修改 `load_gate` 来补偿词典噪声，除非领域边界本身发生变化并同步更新 reference 和版本。

每次维护后运行：

```bash
python scripts/build_adapter_assets.py
python scripts/validate_knowledge_assets.py
python scripts/evaluate_routing.py --self-test
python scripts/validate_output.py --self-test
```

生成的 `adapter-*.md` 路由区块只能由构建脚本刷新；手工领域解释、字段合同和来源引用仍由人工维护。变更应增加至少一个正例、一个反例和一个歧义例；合成 benchmark 不是 gold 标注。

## 4. 路由状态边界

- `load`：目标实体、来源语境、极性和方法/结果级证据齐全，并满足适配器门控；
- `candidate`：概念可能匹配，但实体、语境、中心性、极性或来源可访问性仍未决；
- `skip`：完整可访问证据表明只有排除语境或领域明确不适用；信息不足时不要用 `skip` 伪装确定性。

所有与词典有关的推断仍必须回到 `source`、`evidence`、条件和实体。词典维护改变的是召回和边界，不是科学结论本身。
