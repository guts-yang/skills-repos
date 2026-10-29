---
name: research-baseline-comparison
description: This skill should be used when selecting research baselines, building SOTA comparison tables, checking whether published or reproduced results are comparable, or documenting baseline inclusion and exclusion. It enforces traceable values, explicit setting alignment, and fair comparison boundaries.
agent_created: true
---

# R4｜基线筛选与可比证据表

## 职责边界

把 R3 的已定义挑战转为透明、可追溯的候选基线集和结果比较口径。负责纳入规则、文献值/本地值分层与可比性判断；不运行完整复现实验（R5），不凭榜单单一最高数值替用户确定科学结论。

## 输入

- 必需：研究问题/挑战、目标任务与评估维度。
- 优先输入：R3 challenge dossier、目标数据/模型/系统及资源上限。
- 独立触发时：先明确任务版本、比较目的、指标方向、评测设置与检索时间点；未明确时标为“比较协议待定”。

## 操作步骤

1. **固定比较协议。** 列明任务、数据集与切分、模型/基座及版本、预处理、训练与推理设置、指标定义/方向、评估脚本、预算边界、纳入截止日。
2. **预注册候选纳入规则。** 依据直接竞品、社区常用基线、强基线、挑战覆盖度、代码/数据可获取性和资源约束选择；记录搜索范围、排除理由和不可复现限制。避免只选择容易超过或容易引用的方法；候选数按课题调整，不固定 3–5 篇。
3. **逐项核验来源。** 对论文版本、正式发表信息、代码仓库/分支或提交、数据版本、表格/图号进行定位。论文公布值标 `paper_reported`，本地运行值标 `local_reproduced`；不混为同一种证据。
4. **按行拆开实验结果。** 每行代表一个方法 × 数据集 × 模型/设置结果。记录方法/版本、论文/代码出处、模型或系统、数据/拆分、指标定义及方向、关键超参/训练预算/种子、分数、数值类型、可比性类别和备注。
5. **分级判断可比性。**
   - `A_exact`：关键任务、模型/数据、指标和评估设置一致，可在同表直接比较。
   - `B_normalized`：存在可验证且不改变含义的转换；写清转换公式、假设和原值，并单独标明归一化值。
   - `C_context_only`：关键设置不同或缺失，只作背景参考，不得混入同一排名/平均值。
   不确定时降级到更保守类别，不靠文字备注掩盖不可比。
6. **执行填数铁律。** 设置对齐时引用原论文值并附精确出处；设置不一致而比较决定核心结论时安排 R5 统一复现；源文未报告留空/“—”，不从截图猜数、不外推、不补造。把相反方向、不同量纲的指标拆开解释。
7. **标记 SOTA 边界。** “SOTA”只限定在指定任务、数据、模型/基座、指标、评估协议及检索截止时间内。只有关键条件匹配才标为可直接领先；否则标“不同设置，不可判定”。不把 venue 名头替代方法质量或社区共识证据。
8. **排序复现优先级。** 综合挑战覆盖、强度、开源可用性、运行成本和结果不确定性，给出 R5 排序及理由，不把“代码能下载”误认为可复现。

## 交付物

产出《基线比较表 + 纳入/排除规则 + 可比性说明》。核心列：`method/version`、`paper/source locator`、`code/revision`、`model/base`、`dataset/split`、`metric/direction`、`protocol`、`budget/seeds`、`score`、`value_type`、`comparability`、`caveat`、`R5_priority`。

提供一段比较口径说明：本表内哪些行可直接比较、哪些仅为背景、需要复现的缺口是什么。

## 质量门与状态

- **PASS：**候选覆盖直接竞品及必要强基线；数值可追溯；核心比较口径一致，或不同设置被清楚隔离；缺失值未臆造；R5 可执行优先级已说明。
- **PASS_WITH_CAVEATS：**表格结构和出处齐全，但个别设置尚待核验；把受影响结论与补核行动明确列出。
- **BLOCKED：**研究问题/评估协议不明确，或关键基线的来源/数据不可获取；输出缺口清单，不伪造完整排名。
- **FAIL：**将不可比结果混排、选择性排除强对手、误标 SOTA，或将论文报告值说成本地复现值。

## 回退与交接

- 候选覆盖不了挑战或挑战边界模糊 → 回 R3。
- 领域/基线检索不全 → 回 R1 或 R2。
- 代码/数据可得性不明、比较依赖一致设置 → 对该候选只交 R5 做一次可行性预检；预检失败后回 R4 必须换候选或停止，不能把同一候选、同一阻塞原因再次送回 R5。
- 通过后 → 交 R5，附候选基线、冻结评估协议、优先级及不可比风险。
- 每次回退记录 `attempt_key` 与输入变化；没有新证据、资源或协议变更时，不重复同一阶段。

交接包统一包含：`project/question/scope`、`protocol`、`candidate_baselines`、`source_evidence`、`artifacts`、`gate_status`、`caveats`、`next_skill`、`backtrack_reason`。