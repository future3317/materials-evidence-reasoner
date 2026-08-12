# 单篇文献用户工作流

这份说明面向“用户把一篇论文交给 Agent”这一最常见入口。Agent 负责执行，用户不需要先理解 JSON Schema。

## 用户只需要提供什么

优先提供：

- 论文 PDF；
- 补充信息、数据表、代码仓库或项目页（如果有）；
- 一句话说明想从文献中得到什么，例如“找出影响循环寿命的关键条件，并规划验证实验”。

如果只有 PDF，也可以开始。不要让 Agent 把没有提供的实验数据、图中未读出的数值或补充信息补成“典型值”。

## 建议直接复制的请求

```text
请使用 materials-evidence-reasoner 处理我上传的文献。

这是 literature-first 任务，目前没有本地实验数据。请：
1. 先检查文件身份、页数、可访问范围和 PDF/XML 提取环境；
2. 提取方法、样品/材料、工艺、测量条件、图表和明确报告的数值，并为每条证据保留页码/图表/表格定位；
3. 区分 source-reported、derived、hypothesis 和 missing，不把引言或常识写成本文已证明；
4. 建立条件化文献先验、证据台账、PSPP/机制候选关系；
5. 给出信息缺口、可证伪的候选假设和最小验证实验；
6. 生成可阅读的中文报告、source-extraction dashboard、materials-result.json 和 materials-dashboard.html；
7. 按 references/output-schema.json 生成 canonical JSON，并运行 scripts/validate_output.py；
8. 最后用“先看什么、哪些结论可以相信、下一步可以补什么”的方式交接结果。

如果 PDF 是扫描件、表格或图像提取质量不足，请明确标记并保留需要人工回查的页码，不要静默猜测。
```

## Agent 应交付什么

至少给出以下四类东西，并在最终消息中逐一说明用途：

| 产物 | 用户怎么用 |
|---|---|
| `source-extraction/source-dashboard.html` | 先检查 PDF/XML 是否读对、哪些页/表/图需要人工回查 |
| `materials-report.md` | 先读这个，了解研究问题、条件、证据强度、限制和下一步 |
| `materials-dashboard.html` | 交互查看条件、证据、偏差、假设和验证计划 |
| `materials-result.json` | 机器可读事实源，后续交给 Agent 继续比较或更新；不要手工改字段名 |

只有文献时，报告应明确说明“没有本地基线/复现实验”，因此不能直接下“已复现”或“复现失败”结论。此时的 `information_gaps` 和 `verification_plan` 是后续研究入口，不是已经完成的实验。

## 用户阅读顺序

1. 先打开 source dashboard，确认标题、页数、文件身份、抽取状态和警告。
2. 再读 `materials-report.md` 的结论、证据限制和“现在该做什么”。
3. 在 `materials-dashboard.html` 中打开条件、证据和假设详情；优先检查证据定位和适用边界。
4. 只有需要程序复用时才查看 JSON。继续研究时，把 JSON 和新文献/实验一起交给 Agent。

## 三种常见后续请求

```text
基于这份 materials-result.json，再加入我上传的第二篇文献。只合并条件匹配的证据，标出冲突，不要覆盖原记录。
```

```text
基于这份文献结果和我上传的本地实验表，检查是否可比，再判断偏差来自测量、工艺、结构还是材料本征属性。
```

```text
我准备验证 H-2。请从 verification_plan 中选出当前设备能执行的最小实验，并列出对照、重复、判定规则和停止条件。
```

## 什么时候需要人工回查

- PDF 是扫描件、双栏顺序混乱、公式/单位丢失；
- 数值来自图像读数而不是正文或表格；
- 补充信息未提供但论文结论依赖它；
- 同一指标在不同条件、样品或归一化方式下被混用；
- Agent 报告中出现“未提供”“无法确认”“仅类比”时。

这些不是系统失败，而是科研证据边界。人工回查后，把补充文件或明确定位再次交给 Agent。
