# Personal Skills Repository

个人 skills 分类集成仓库。以单个 `SKILL.md` 为技能入口，完整保留技能目录中的脚本、参考资料、资源与元数据。

## 快照范围

- **33 个用户级个人 skills**：复制自 `~/.workbuddy/skills/`，截至 **2026-10-29**。
- **1 个仓库原有 skill**：`github-python-repo`，保留其脚本与文档。
- 仓库共 **34 个技能包**。各包原始内容独立存放，不把所有技能内容拼成一个大文件。
- 内置、marketplace、插件及 Connector 随附技能不在此仓库内重复 vendoring；这些技能由各自上游管理。

`skills-manifest.json` 是机器可读目录，记录技能名称、分类、包目录和来源。用户级个人技能的原始目录名也记录在 `source_directory` 中；如 `self-improving-agent__skillhub` 这种来源名与技能元数据 `name` 不同的情形，保留两者映射。

## 分类结构

| 分类 | 数量 | 内容 |
|---|---:|---|
| `research/literature-and-mapping` | 6 | 深度调研、论文阅读、文献侦察与知识地图 |
| `research/ideas-and-methods` | 4 | idea 评估、挑战定义、创新验证、MOGP-U 研究内核 |
| `research/benchmarks-and-reproduction` | 5 | benchmark 清单、SOTA 表、baseline 比较与复现 |
| `research/writing-and-publication` | 8 | 论文写作、模板、数学笔记、投稿前审查与 venue 核验 |
| `research/workflows` | 3 | 多轮研究编排、vibe research、周度复盘 |
| `career-and-jobs` | 1 | 求职准备与 AI 辅助练习 |
| `ai-information` | 1 | AI HOT 动态检索与简报 |
| `documents-and-conversion` | 1 | Markdown / CSV 离线转 PDF |
| `visualization` | 2 | Draw.io 重建与科研图设计 |
| `developer-tools` | 2 | GitHub Python 仓库 / PR 工作流与技能仓库移植 |
| `agent-meta` | 1 | 自我改进与经验记录 |

完整包路径见 `skills/`；每个包都保留自己的 `SKILL.md`，有附属资源时也保留原 `scripts/`、`references/`、`assets/` 等目录。

## 后续维护

1. 新增用户级 skill 时，将完整技能目录复制到最匹配的分类下。
2. 更新 `skills-manifest.json`，补充源目录、技能元数据名称、包目录和分类。
3. 如果对仓库副本作了修改，注意同步回 `~/.workbuddy/skills/`，或明确将仓库标为该技能的新 source of truth；避免两边悄悄分叉。
4. 推送前检查所有新增文件与 skill 内容，确认未包含密钥、个人数据、公司机密或不应公开的资料。此仓库本次只在本地重构，未提交、未推送。
