# Real Skill Effect Evaluation

这是一次真实的双 Agent 对照，不是模拟输出：

- 模型：`gpt-5.6-luna`；
- 输入：`../error-budget-demo.csv`；
- 任务：判断 Coulombic efficiency 重复测量数据的主要变异来源、结论边界和最小验证实验；
- 唯一变量：一组 Agent 不读取本项目 Skill，另一组读取 `SKILL.md` 并使用配套脚本与合同；
- 评分：`scripts/evaluate_real_skill_effect.py`（实际命令见下）。

无 Skill 组只保留普通研究备忘录和自由格式 JSON；使用 Skill 组必须经过输入盘点、误差预算、canonical JSON 生成和 `validate_output.py` 校验。两组使用同一个原始 CSV，不读取额外文献。

重新计算评分与可视化：

```bash
python scripts/evaluate_real_skill_effect.py
```

评估结果在 `evaluation.json`，离线页面在 `evaluation.html`。结果只代表一个固定任务、每种模式一次运行；下一步应扩展到 source-backed 文献、多个材料领域、重复运行和独立人工金标准。
