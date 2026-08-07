# 单篇文献示例请求

把论文 PDF 和补充信息一起上传给 Agent，然后复制下面的请求：

```text
请使用 materials-evidence-reasoner 做一个 literature-first 审查。

我目前只提供文献，没有本地实验数据。请先完成文件和提取质量检查，再提取材料、样品、工艺、测量条件、图表数值和证据定位。请严格区分：
- 文献直接报告的事实；
- 从文献数值计算得到的 derived 结果；
- 机制候选或 hypothesis；
- 未提供或无法确认的信息。

请输出：
1. 中文行动优先报告；
2. source-extraction/source-dashboard.html；
3. materials-result.json；
4. materials-dashboard.html；
5. 信息缺口、可证伪假设和最小验证实验。

请按照 references/output-schema.json 生成结果，运行 scripts/validate_output.py，并在最后告诉我：我应该先打开哪个文件、哪些结论仍需人工回查、下一步如何把本地实验接入。
```
