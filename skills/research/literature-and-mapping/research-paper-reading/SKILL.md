---
name: research-paper-reading
description: This skill should be used when reading, explaining, comparing, or taking notes on one or a few research papers, especially when the user needs the paper's actual contribution, method mechanism, equations, assumptions, or limitations rather than a generic abstract summary.
agent_created: true
---

# R0｜单篇论文精读与科研笔记

## 职责

把原始论文转成可复述、可追溯、能进入后续领域调研的精炼笔记。AI 摘要只用于建立阅读路线；原文、附录、代码和正式补充材料才是证据来源。

## 输入

论文 PDF/链接/题目/作者版本，以及用户的研究问题或阅读目标。若只有引用信息而没有可读原文，说明当前证据范围。

## 步骤

1. 获取并确认版本、题目、作者、发表/预印本信息；不要将版本信息猜测为已核实事实。
2. 快速浏览摘要、引言、方法图、实验与结论，列出要回原文核查的疑问。
3. 精读问题定义、关键方法段、公式推导、实验设置及局限；需要时追踪引用或代码实现。
4. 用自己的话写下“问题—机制—相对改进”，区分作者主张与本文实际证据。
5. 对公式逐项解释变量、假设、优化对象/作用路径和实现位置；不理解处明确标“待核”，不抄一段 AI 解释代替推导。
6. 对照摘要检查笔记是否准确，补充反例、前提和适用边界。

## 交付

一篇论文一张卡：书目信息及版本；研究问题；一句话核心贡献；基线/已有方法；方法流程/关键算子；关键公式与符号；证据位置（页码/图表/章节/代码路径）；实验设置；实际结果（注明来源）；局限/未解决点；个人质疑；待核清单。

## 质量门与衔接

- `PASS`：不看摘要能讲清问题、机制、改进对象；主要主张有原文定位；个人推断有标记。
- `PASS_WITH_CAVEATS`：核心方法已懂，但公式、结果或版本仍待核；如实列出。
- `BLOCKED`：原文不可访问或缺页，不能作全面概括。
- `FAIL`：笔记只有摘要搬运、引文或公式堆砌，无法解释其因果机制。

完成多篇后交 `research-literature-scout`（R1），传递笔记卡、核心来源和待核问题；若用户只问单篇，则直接回答，不强制进入 R1。最小交接字段：`question/scope`、`paper_version`、`claim_evidence`、`notes_artifact`、`gate_status`、`caveats`、`next_skill`。