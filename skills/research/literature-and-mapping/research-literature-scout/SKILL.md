---
name: research-literature-scout
description: This skill should be used when surveying a research field, expanding a paper list, selecting representative literature, mapping debates and evidence gaps, or deciding whether literature coverage is sufficient for a research question. For broad or contested field surveys, it coordinates the deep-research skill and turns its verified corpus into the R1 literature matrix.
agent_created: true
---

# R1｜领域扫读与文献证据盘点

## 职责

围绕研究问题建立透明、可更新的文献集合和领域判断。负责检索策略、纳入/排除、覆盖度和证据缺口；不替 R2 定最终分类，不替 R3 宣称挑战已证明。

## 输入

研究问题、主题/时间范围、可访问的文献来源、R0 笔记（如有）、领域/venue 约束。对检索截止日、语言、论文类型等作显式约定。

## deep-research 调用规则

- 对跨多个子方向、需要系统梳理/观点对照、R3 发现关键文献缺口，或创新方向存在明显争议的任务，先加载并调用 `deep-research`。
- 调用前冻结 brief：主题、2–3 个可回答研究问题、检索角度/读者、边界与截止日。若研究问题仍过宽，先澄清，不用宽泛主题直接启动大规模检索。
- 让 `deep-research` 执行多视角搜集、反方证据检索、引文核验和主题综合；遵循其 citation protocol 和 coverage gates。没有可用检索能力时将阶段标为 `BLOCKED`，不得凭记忆生成综述。
- 将其输出作为 R1 的**候选已核验文献池**，逐条导入矩阵：来源版本、核验状态、主张/证据定位、方法/设置、反方或限制、纳入/排除理由。复用既有 R0 文献并去重；不能把报告正文或搜索摘要直接当成已核实事实。
- 若只需查一两篇论文或窄范围候选清单，直接采用 R1 定向检索，避免启动完整 survey；若只是补 R3 的一个缺口，向 `deep-research` 提交定向补充 brief，增量合并而不重启全部检索。
- R1 仍负责筛选记录、文献矩阵、范围覆盖和向 R2 交接；`deep-research` 的 MECE taxonomy/综合报告是辅助产物，不替代 R2 根据本项目问题重新定义分类。

## 步骤

1. 将研究问题拆成检索概念、同义词、技术术语和关键先行工作；写明检索源与截止日期，并按上节决定是否调用 `deep-research`。
2. 设纳入/排除标准：相关性、对象/场景、方法、证据类型、版本重复、语言/年份限制；记录每项排除理由。
3. 分层筛选：标题摘要初筛、全文核查关键候选、引文追踪补漏；标记预印本与正式版本关系，去重但保留版本轨迹。
4. 对代表论文提取对象、假设、机制、算子/框架、数据/证明、评价指标、限制和出处。把主框架与局部增量分开。
5. 对不同路线/观点找直接支持与反证，识别未解决的问题、已知失败条件和证据空白。
6. 按主题饱和度决定是否扩检：新增工作是否仍改变分类、边界、挑战或候选基线？篇数只是过程指标，不是通过标准。

## 交付

文献矩阵（论文/年份/正式发表状态/对象/问题/机制/证据/数据或证明/限制/来源定位）；检索与纳入排除日志；领域主线与争议；待补文献/证据缺口。若调用 `deep-research`，另附 brief、检索视角、报告路径、逐条引用核验状态和增量补检记录。所有书目信息、会议等级、引用和数值可查则附出处，不可查标待核。

## 质量门与衔接

- `PASS`：检索范围有界、筛选规则可复述、主要路线及反证均有代表性证据、主题趋于饱和。
- `PASS_WITH_CAVEATS`：有不可访问文献、语种/年份缺口或版本未确认，并说明可能影响。
- `BLOCKED`：研究问题过宽或缺少有效检索条件。
- `FAIL`：只堆引用、按标题归类、没有纳入规则，或仅选支持预设结论的论文。

通过后交 `research-knowledge-map`（R2），携带文献矩阵、主题边界和未决矛盾。若单独完成文献梳理，可直接交付，不必触发后续阶段。交接字段：`question/scope`、`search_protocol`、`literature_matrix`、`coverage_gaps`、可选 `deep_research_brief/report`、`citation_verification`、`gate_status`、`caveats`、`next_skill`。