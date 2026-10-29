---
name: research-baseline-reproduction
description: This skill should be used when implementing or rerunning a selected research baseline, diagnosing a gap between reproduced and reported results, deciding whether a baseline is sufficiently aligned for innovation work, or creating an auditable experiment record.
agent_created: true
---

# R5｜基线复现与实验验收

## 职责边界

在冻结的 R4 比较协议下，验证所选基线能否运行、结果与参考值是否在预先声明的容差/不确定性范围内，并留下可复跑记录。负责复现诊断与 go/no-go 建议；不通过改变评测口径追求“对齐”，不把调参后的新结果冒称严格复现，也不设计 R6 创新替代复现。

## 输入

- 必需：唯一基线标识（方法、代码/版本）、目标结果、数据和评估协议。
- 优先输入：R4 比较表中冻结的候选、设置、预算、优先级及可比性备注。
- 缺少可执行代码/数据时，区分“无法独立复现”与“方法无效”，给出阻塞原因和替代验证路径。

## 复现前冻结清单

在运行前建立实验卡，不得事后根据结果修改容差：

- 论文及代码来源、commit/tag、补丁差异；
- 模型/检查点标识与哈希（可得时）、数据版本/切分/预处理及数据许可；
- 依赖锁定、运行环境、硬件、驱动/框架版本；
- 完整配置、超参搜索范围、随机种子策略、停止条件；
- 指标实现/脚本版本、方向、聚合方式；
- 计算/时间/数据预算；
- 参考数字与精确来源；
- 允许偏差/统计判据、由何种依据设定、触发复核/换基线条件。

将“按作者代码与设定重跑”与“独立实现/复现”分开标注；两者的偏差来源和结论强度不同。

## 操作步骤

1. **可行性预检。** 核对许可证、数据权限、硬件/显存、依赖和下载可用性；估算最低成本。若无法满足，先报告 BLOCKED，不擅自改变任务定义。
2. **最小冒烟测试。** 运行导入/数据读取/单 batch/单评估路径，保存完整命令、日志与错误；确认端到端产物而非仅进程退出码。
3. **按冻结设置运行。** 不同时改算法、数据、超参和评估脚本。每个变更单独编号，并区分原始复现与修复性偏差。
4. **计算对齐差异。** 对同定义数值报告 `Δ = local − reference`；只有量纲/尺度允许时才提供相对差异。注明指标方向、聚合、种子、区间/方差及可比性限制。单个最优 seed 不代替稳定性信息。
5. **按顺序诊断偏差。** 检查数据版本/切分 → 模型/检查点 → 预处理 → 实现与论文细节 → 超参/预算 → 指标脚本/聚合 → 随机性与硬件非确定性。逐项记录证据，不盲目重写实现。
6. **决定继续或止损。** 在冻结的门槛内则认定对齐；未达标先判断差异是否可解释、是否影响研究结论、继续排查成本是否合理。只有经用户认可的充分理由才允许带 caveat 进入创新阶段。
7. **拆出模块图。** 标示输入输出、核心算子、训练/推理路径、评估接口和潜在替换点；注明每个方框来自原论文、代码还是本地改动。
8. **留下复现包。** 保存配置、依赖、命令、日志、指标原始结果、检查点引用、代码修订和已知偏差，使他人能按记录重复运行。

## 交付物与实验记录

产出《基线复现报告》，至少包含：`run_id`、method/revision、data/model identity、environment、config、seed、budget、metric implementation、reference locator/value、local result、delta/uncertainty、deviations、failure diagnosis、module diagram、reproduction status、next decision。

差异阈值按任务噪声、指标语义、资源和社区惯例预先设定。原会议的约 10% 只可作为待讨论起点，不可默认作为通用验收线。

## 质量门与状态

- **PASS：**冻结设置已执行；关键产物和来源齐全；结果符合预声明门槛/统计判据；他人可按记录重跑；创新对比协议可沿用。
- **PASS_WITH_CAVEATS：**偏差未完全消除但有证据解释，且不改变后续比较有效性；列明残余风险，需用户明确同意再进 R6。
- **BLOCKED：**许可、数据、代码、资源或环境问题阻止有效运行；如实报告已完成的检查与最小解阻路径。
- **FAIL：**结果偏差大且原因未明、设置无法核实、评估口径变更，或无法稳定重跑；不得声称 baseline aligned。

## 回退与交接

- 代码/数据/预算不可行或基线不能公平复现 → 回 R4 更换候选或调整比较计划；handoff 写明候选 ID、已尝试的预检和未解决阻塞。每个候选只做一次相同条件预检。
- 复现暴露 challenge 定义、场景或指标本身有误 → 回 R3。
- 仅是检索/实现细节不清 → 由 R1/R4 补证，再续跑本 Skill；必须指出新增证据/输入变化，不得原样重跑。
- 没有替代候选或新增资源时 → 停止并标 `BLOCKED`，请求用户决定，不在 R4↔R5 间循环。
- 通过后 → 交 `research-innovation-validation`，携带冻结 baseline、模块图、评估协议和复现报告。

交接包统一包含：`project/question/scope`、`baseline_identity`、`frozen_protocol`、`run_records`、`artifacts`、`gate_status`、`caveats`、`next_skill`、`backtrack_reason`。不得把“跑通代码”单独等同于“复现成功”。