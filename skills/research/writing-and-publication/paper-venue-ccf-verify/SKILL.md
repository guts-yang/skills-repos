---
name: paper-venue-ccf-verify
description: 核验学术论文（尤指机器遗忘/LLM unlearning 文献对比表）每篇论文的真实发表出处、区分正式发表 vs arXiv 预印本、按 CCF-A/B/C 分级打标（⚠️建议剔除 / 📄预印本）、并把正式论文的 arXiv 链接批量替换为会议官方页面链接。触发词：核实论文出处、CCF 分级、是否顶会、建议剔除、换成会议官方链接、venue verification、CCF-A。
description_zh: 论文出处核验与CCF分级
description_en: Paper venue & CCF verification
disable: false
agent_created: true
---

# paper-venue-ccf-verify

## When to use
- 用户给出一份论文列表 / 文献对比表（如 SOTA 对比表、related work、对比实验基线），要求逐一核实发表出处。
- 需要区分「正式发表（会议/期刊）」vs「仅 arXiv 预印本」。
- 需要按 CCF 分级（A/B/C/workshop）判断，给低级别 venue 打「⚠️建议剔除」、预印本打「📄预印本」。
- 需要把正式发表论文的 arXiv 链接替换为对应会议的官方论文页面链接。
- 本项目特指 `实验与SOTA/机器遗忘_SOTA对比动态维护表_2026-08-03.md`（廖晨扬方向A），但流程通用。

## 前置事实（本项目已核验，勿重复联网）
- CCF-A（AI）：NeurIPS、ICML、ICLR、AAAI、ACL、CVPR、ICCV、IJCAI。
- CCF-B（AI）：EMNLP、NAACL、COLING、ECCV、AISTATS 等。
- COLM（Conference on Language Modeling）：2024 新会、同行评审、未入 CCF 但公认高质量——按「保留」处理，标签 `✅COLM(新会公认)`，**不要**打建议剔除（TOFU/NPO 主口径论文在此）。
- ACL Findings：主会外轨道，认可度低于主会——按用户规则打 `⚠️建议剔除(Findings)`。
- 官方链接模式：ACL/NAACL/EMNLP/COLING→`aclanthology.org/<年份>.<会议>-<类型>.<号>/`；ICLR/COLM→`openreview.net/forum?id=<id>`；ICML→`proceedings.mlr.press/v<卷>/<id>.html`；NeurIPS→`papers.neurips.cc/paper_files/paper/<年>/hash/<hash>-Abstract-Conference.html`；AAAI→`ojs.aaai.org/index.php/AAAI/article/view/<号>`。

## Steps
1. **梳理清单**：读目标表，列出全部不重复论文及其当前「年份/出处（链接）」单元格。区分：基线行（Original/Retrain/Target/Zephyr原始）与评估框架（OpenUnlearning）不需核；方法级论文需核。
2. **并行子代理核官方链接**：按「渠道家族」分 3 个 general-purpose 子代理（各自 web 搜索+打开核对标题），要求每篇返回 `方法 | 会议+年份 | 正式发表/仅预印本 | 官方链接`：
   - ACL Anthology 家族：ACL/NAACL/EMNLP/COLING/ACL Findings 论文。
   - OpenReview/COLM 家族：ICLR/COLM 论文。
   - NeurIPS/PMLR/AAAI 家族：NeurIPS/ICML/AAAI 论文。
   预印本特征明显的（近 1-2 年 arXiv、无会议信息）不必派子代理，直接判 📄预印本。
3. **判定分级打标**：正式发表→✅CCF-A / ✅COLM / ⚠️建议剔除(CCF-B 或 Findings)；仅 arXiv→📄预印本。
4. **批量替换链接**：写 Python 脚本，按 arXiv ID 正则 `\[([^\]]*)\]\(https://arxiv\.org/abs/<ID>\)` 把正式论文链接替换为 `[会议 年份](官方链接) 标签`、预印本替换为 `[arXiv:ID](url) 📄预印本`；随后清理标签后冗余的 `（preprint）`/`（**preprint**）`/`（会议名）` 字样（见 Pitfalls）。用 managed python 跑，打印每篇替换处数核对。
5. **手动补非 arXiv 行**：表内无 arXiv 链接的（如已用 ACL Anthology 链接、纯文字「EMNLP 2024」「本地PDF」等）用 Edit 单独补官方链接+标签。
6. **汇总总表**：在卷首加「出处核验与 CCF 分级总表」（A=CCF-A / B=COLM / C=CCF-B+Findings / D=预印本 四档 + 勘误清单）。
7. **校验**：跑管道符完整性脚本（每个表格块各行 `|` 数与表头一致）；grep 统计四类标签数。
8. **提交推送 + 同步副本**：`git -C <repo> add/commit/push`（勿用 cd、勿 --no-verify）；本项目须 `cp` 同步到 `方向A_可解释遗忘损失GP/精读笔记/` 同名副本并 `cmp` 校验一致。

## Pitfalls
- **arXiv ID 会错**：表里可能存在错误 arXiv 号（本项目曾发现 SCRUB 2305.14936→2302.09880、SalUn 2310.11883→2310.12508）。子代理核出的正确 ID 以官方页面为准；脚本里把错误 ID 也映射到正确官方链接即可顺带修正。
- **出处会标错**：ICUL 实为 ICML 2024 非 ICLR 2024；AlphaEdit 实为 ICLR 2025 杰出论文非 preprint；FLAT 实为 ICLR 2025 非 preprint。不要轻信表内旧标注，以官方页面为准。
- **替换后冗余**：脚本替换 arXiv 链接后，单元格里原有的 `（COLM 2024）`、`（**NeurIPS 2025，已确认**）`、`**AAAI 2024（已确认）**` 等旧括注会残留成冗余，须逐个清理（grep 标签后紧跟 `（会议…）` 的行）。
- **同一论文多行**：同一方法在多个子表重复出现，其 arXiv 链接显示文本可能不同（`arXiv:X` vs `会议, arXiv:X`），但 URL 相同——按 URL 正则替换可一次全改。
- **「同上」行**：MUSE 等基准内部基线（GA_GDR/GA_KLR/NPO_GDR 等）出处列写「同上」指**数据来源**（MUSE 论文），不是方法原始 venue，不要改动；方法原始 venue 在全景表核。但注意「同上」也可能出现在**代码列**（指代码仓库，如 GA+KL/NPO+RT），替换「同上」时务必用脚本按行内容（如含 `muse_bench`）精准定位到**出处列**，勿误改代码列。
- **基线行无链接属正常**：Original/Retrain/Target/Zephyr原始/FT(通用基线)/RT(各基准自带) 等是基线操作而非论文，出处列标「通用基线/各基准自带」即可，**不要**强行加链接。用户说"尽可能所有都有链接"指方法级论文，不含这些。
- **汇总表链接别用截断文本**：写汇总/总表时，链接列**不要**用 `papers.neurips.cc/.../hash…` 这种截断显示文本（看着像链接其实不可点），必须用完整可点 markdown 链接 `[会议 年份](完整url)`。本项目阶段〇总表曾因此返工。
- **不要凭记忆填链接**：所有官方链接必须联网打开核对标题后再用。

## Verification
- 四类标签计数符合预期（✅CCF-A / ✅COLM / ⚠️建议剔除 / 📄预印本）。
- 残留 arXiv 链接只剩预印本（带📄）与模型引用（如 Zephyr 2310.16944）。
- 表格列数完整性脚本无异常；`cmp` 源与副本一致；git push 成功且 `status -sb` 显示与 origin 同步。
