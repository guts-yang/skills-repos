---
name: research-innovation-validation
description: This skill should be used when proposing or evaluating a research method on top of an aligned baseline, designing a minimal experiment to test a mechanism, checking train/test information consistency, or preparing an evidence-backed research narrative. It uses idea-evaluator to adversarially assess a formulated candidate idea before committing to implementation.
agent_created: true
---

# R6｜创新设计与验证

## 职责

把已验证的具体挑战和对齐基线转成最小、可证伪的机制改动及实验计划。负责方法方案、预测、验证与研究叙事；不把未经实验的方案称为已验证创新，不代替 R3 证明挑战、不代替 R5 对齐基线。

## 输入

R3 challenge dossier、R4 比较协议、R5 复现报告与模块图、数据/资源约束。缺少任一影响结论的上游产物时，先回报缺口并决定是否能以可见 caveat 继续。

## idea-evaluator 调用规则

- 当已有一条或多条可描述的候选创新、需要判断值不值得投入、检查致命缺陷/新颖性/可行性或比较候选方案时，先加载并调用 `idea-evaluator`。它用于审稿人式挑战，不用于从零发散 brainstorming；尚无候选想法时，先按 R6 的问题—机制—预测写出候选，再评估。
- 传入候选想法、R3 dossier、R4/R5 的已核结果、真实可用资源/周期及深度调研已核文献。明确区分实测证据与机制推理；要求 idea-evaluator 将 novelty 未能检索核实之处标为未核，不因“没搜到”断言首创。
- 保存评估结论、fatal-flaw、各维度依据、资源匹配、需要修改的假设和建议验证实验，作为 R6 的 `idea_evaluation` artifact。评估分数和 verdict 是决策辅助，不是实验证据，不能覆盖 R3/R4/R5 的质量门。
- `Reject and Pivot` 或发现 CRITICAL fatal flaw：暂停该方案，不继续包装成候选创新；按根因回 R3/R4 或请求用户决定是否换题。
- `Accept with Revisions`：将修改项写回挑战映射/实验计划，重新检查 R3 假设与 R4/R5 依赖后再推进。
- `Strong Accept`：只表示值得进入验证，不表示创新已成立；仍须执行下述最小实验、反证/消融和端到端检查。

## 步骤

1. 将创新目标写成单条因果链：具体痛点 → 设计机制/算子 → 预期改变的中间量 → 可观测结果。
2. 优先提出最小改动；每个组件标注其挑战 ID、必要性、备选解释和预期副作用。设计能先单独验证的组件，不一开始叠加多个未知因素。
3. 确保实验可证伪：给出正向预测、失败阈值、反例条件和停止规则；安排消融、负对照、边界/敏感性及成本评估。
4. 核对端到端可用性：训练与测试时可见信息、标签、数据访问和计算预算是否一致；排除未来信息、隐藏 oracle 或只在评测集可得的信号。
5. 先做最低成本原型；比较时冻结 R4 协议和 R5 baseline，记录所有偏差。实验不能证明机制时，限制结论范围，不用涨点代替因果证据。
6. 复用 `idea-evaluator` 已核验的近邻工作和新颖性判断；只有覆盖缺口或新出现的直接竞品才做定向补检。形成“挑战 → 方法 → 证据”的主线，明确哪些结果是真实、哪些待测。

## 交付

方案图/模块改动表、方法假设、预测和失败判据、实验矩阵（问题/对照/变量/指标/预算/解释）、风险清单、主张—证据映射、`idea_evaluation`（verdict/fatal flaws/维度依据/修改动作/新颖性核验状态）及下一步。

## 质量门与衔接

- `PASS`：挑战有证据；基线可信；设计机制必要且实现可行；实验能区分机制与调参/工程变化；测试阶段可用信息自洽；若已形成候选想法，`idea-evaluator` 无未解决的 CRITICAL 缺陷，且关键修改已落实。
- `PASS_WITH_CAVEATS`：方案逻辑成立但关键预测尚待原型验证；idea-evaluator 的可修订项已写入行动计划且无未解决的 CRITICAL 缺陷；只允许称“候选方案/假设”，不得称结果已成立。
- `BLOCKED`：上游基线、数据、评估协议或资源缺失，或完成 idea-evaluator 所需的想法/资源信息不足。
- `FAIL`：痛点泛化、组件无明确作用、依赖不可得信息、实验不能证伪、方案被直接相关工作覆盖，或 idea-evaluator 给出 `Reject and Pivot`/未解决的 CRITICAL fatal flaw。

挑战/新颖性失焦 → R3；基线设置不可信 → R4/R5；机制依赖的领域关系未清楚 → R2。通过验证后进入论文写作/投稿流程；该 Skill 本身不自动提交论文。交接字段：`challenge_id`、`baseline_identity`、`hypothesis`、`experiment_plan`、`idea_evaluation`、`artifacts`、`gate_status`、`caveats`、`next_action`。