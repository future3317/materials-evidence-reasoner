# 主动学习混合输入请求示例

```text
请使用 materials-evidence-reasoner 审查这个“文献 + 主动学习代码 + 推荐结果”目录。

先运行 prepare_intake.py 和 profile_active_learning.py，再处理文献 PDF。请把
labeled.csv、候选池、recommended_*.csv、qbc_recommended.csv 和 Python 脚本分开解释：

- 确认 x/y 的物理变量、单位、范围和约束；
- 确认 z 是实测、可信模拟还是示例目标函数；
- 把 acquisition_value/QBC variance 保持为模型派生排序量；
- 检查脚本依赖、随机种子、硬编码路径和是否覆盖输入；
- 只有独立实验或可信模拟记录才能写入 property_records；
- 最终仍按 references/output-schema.json 生成 materials-result.json，运行
  validate_output.py，再生成报告、结果 dashboard 和机制图审计。

请先告诉我：哪些文件可以直接读，哪些需要人工回查，当前最小验证实验是什么。
```
