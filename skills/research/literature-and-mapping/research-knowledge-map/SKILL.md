---
name: research-knowledge-map
description: This skill should be used when organizing a literature corpus into a research-field map, taxonomy, survey outline, or method landscape that relates scenarios, concrete challenges, mechanisms, and evaluation evidence.
agent_created: true
---

# R2｜知识地图与方法分类

## 职责

把 R1 的文献矩阵从“逐篇列表”提升为可解释的领域结构：对象/场景、挑战、方法机制、评估证据及其关系。负责定义分类规则与知识缺口；不凭分类本身推断方法有效或挑战成立。

## 输入

文献矩阵、研究边界、代表性论文、领域术语表。直接触发时可接收零散材料，但需标注材料覆盖不完整。

## 步骤

1. 建立统一术语和实体层：研究对象、应用场景、挑战、干预对象/算子、数据/证明、评估指标。
2. 构造“场景/对象 → 挑战 → 方法机制 → 评估/证据”关系图；一个论文可连接多个节点但需标明连接理由。
3. 按可观测机制/干预对象分类，不按论文标题、模型名或“新/旧”叙事分类。对梯度、数据、参数/架构、Loss 等领域类别仅作示例，按当前领域改造。
4. 为每个类别写定义、纳入/排除规则、代表来源、假设与边界；检查分类是否同一抽象层级、覆盖目标范围、有无重复或空泛类别。
5. 对天然重叠使用显式多标签或主类+副标签，不强制伪造互斥；对“穷尽”范围声明检索边界。
6. 标出争议、依赖关系、无证据连接、没有强评估的路线，形成 R3 需要核实的候选挑战。

## 交付

知识地图（图或结构化表）、分类规则、分类—代表工作表、跨路线关系/争议、挑战候选与证据空白。每个节点可回链到文献矩阵和原文定位。

## 质量门与衔接

- `PASS`：分类定义一致且有判定规则；场景、挑战、机制、指标未混层；关系可追溯；交叉类别有明确处理。
- `PASS_WITH_CAVEATS`：覆盖范围有明示缺口，且不影响当前挑战候选。
- `BLOCKED`：文献覆盖不足以支持稳定分类。
- `FAIL`：分类只是论文/标题列表或同层级混杂，无法定位方法机制。

挑战候选初步可用后交 `research-challenge-definition`（R3）；发现文献不足回 R1。最小交接字段：`scope/taxonomy`、`map_artifact`、`category_rules`、`challenge_candidates`、`evidence_gaps`、`gate_status`、`next_skill`。