---
name: research-seven-round-orchestrator
description: This skill should be used when starting, planning, resuming, or coordinating an end-to-end research investigation across literature review, challenge definition, baseline comparison, reproduction, and innovation validation. It selects the right independent stage skill, checks stage gates, and carries explicit handoffs and backtracking decisions.
agent_created: true
---

# 科研七轮 Skill 编排器

## 职责

负责识别当前研究阶段、选择独立子 Skill、核对前置产物/质量门、生成交接包和回退路由。不代替阶段 Skill 完成专业分析，不宣称未运行的实验或未核验的文献已通过。

## 阶段 Skill

|阶段|独立子 Skill|职责摘要|成功后的默认去向|
|---|---|---|---|
|R0|`research-paper-reading`|单篇论文原文精读、结构化笔记|R1|
|R1|`research-literature-scout`|检索范围、文献筛选与领域扫读|R2|
|R2|`research-knowledge-map`|知识地图、方法分类和依赖关系|R3|
|R3|`research-challenge-definition`|可检验挑战、证据链、方法映射|R4|
|R4|`research-baseline-comparison`|基线选择、可比性分级、SOTA 证据表|R5|
|R5|`research-baseline-reproduction`|冻结协议下复现与偏差诊断|R6|
|R6|`research-innovation-validation`|创新假设、最小验证、端到端自洽|写作/投稿准备或回退|
|横向|`research-weekly-review`|进度、质量门与下一步复盘|当前未通过门对应阶段|

## 对应辅助 Skill

- **R1 文献收集：**跨多个子方向、需系统综述/观点对照或 R3/R4 有实质性文献缺口时，调用 `deep-research` 完成 brief、多视角检索与引用核验，再由 `research-literature-scout` 合并到 R1 文献矩阵。窄范围的一两篇查证不启动完整 deep-research。
- **R6 创新评估：**已有可描述的候选机制且要判断是否值得投入、检查 fatal flaws/新颖性/可行性时，调用 `idea-evaluator`。先把评估意见转成修订动作；Reject/Pivot 或 CRITICAL flaw 按根因回退，Strong Accept 也不能替代实验验证。没有具体候选时先形成候选，不让 idea-evaluator 从零 brainstorming。
- 两者是对应阶段的辅助能力，不改变 R1/R6 的 gate，也不能覆盖原文证据或实测结果。

## 编排流程

1. **判断用户要解决的范围。** 完整调研从 R0 开始；单篇论文阅读直接选 R0；已有方向定义直接选 R3；要核对 SOTA 表直接选 R4；已有代码要求复现直接选 R5；已对齐基线并提出机制时选 R6。不要强迫用户跑完整流程。
2. **读取已有产物。** 获取研究问题、对象/场景、时间与资源限制、当前阶段、证据、已有产物路径/版本及其 Gate 状态。已有产物若来源/设置缺失，先让对应 Skill 复核，不仅凭文件名视作通过。
3. **检查前置质量门。** 只有 `PASS` 才默认进入下游；`PASS_WITH_CAVEATS` 仅在 caveat 不影响下游判断并已明示时继续；`BLOCKED` 先处理阻塞；`FAIL` 回退或重做。
4. **交接给一个阶段 Skill。** 传递最小必要上下文，不把全量聊天历史重复塞入；阶段完成后收集产物、Gate、风险、下一 Skill。
5. **处理回退。** R3 的分类缺口回 R2，文献缺口回 R1；R4 的问题/设置错配回 R3，检索不足回 R1/R2；R5 的基线不可用回 R4，问题/指标错位回 R3；R6 的挑战不成立回 R3、基线不可靠回 R4/R5。
6. **防止回退死循环。** 每次回退记录 `attempt_key`（阶段 + 候选/协议 + 阻塞原因）及发生变化的输入。只有新增证据、改变协议/资源或换候选时，才允许重跑相同阶段；同一候选、同一阻塞原因且无输入变化时停止重试，报告 `BLOCKED` 并请求用户决策。每个基线候选最多做一次 R5 可行性预检；预检失败后必须换候选或停止。
7. **保持诚实的手动衔接。** 如果运行环境不能自动调用另一 Skill，只输出下一 Skill 的准确名称、理由和交接包；不得声称已完成下游 Skill。
8. **允许裁剪。** 纯理论、纯综述、无实验条件等项目可跳过不适用阶段，但必须注明替代证据门及裁剪理由；不可把“没有数据”当作结果。

## 标准 Gate 状态

- `PASS`：验收标准均满足。
- `PASS_WITH_CAVEATS`：可以继续，但需带上不影响有效性的已知限制。
- `BLOCKED`：缺少资料、权限、工具、资源或用户决策。
- `FAIL`：核心假设/证据/设置不合格；回退或停止。

每次输出一行当前状态：`active_stage`、`gate_status`、`evidence_summary`、`blocking_items`、`next_skill`、`backtrack_reason`。统一交接格式见套件 `contracts/handoff-contract.md`；各子 Skill 自含最小字段定义，可脱离套件独立使用。

## 对用户的汇报

先说明当前在哪一轮、什么已通过、什么未通过，再给下一步和 Skill 名称。将事实、推断、待核分开；不把“建议下一步”说成“已执行”。