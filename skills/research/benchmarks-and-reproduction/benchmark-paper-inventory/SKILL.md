---
name: benchmark-paper-inventory
description: 按指定 benchmark（如 TOFU/MUSE/WMDP）系统检索「在该基准上做实验的论文」并产出可维护清单：五路检索（框架反查/引用链/会议逐年扫/综述交叉/关键词直搜）→ 官方页 venue 核验分级（CCF-A/COLM/预印本）→ 与已有表格去重 → 缺失 PDF 三重校验下载 → Markdown 清单成文。触发词：列出用 X 基准的论文清单、某基准的 A 会论文有哪些、补充 SOTA 表论文覆盖、benchmark paper list、论文清单检索核验。
description_zh: 基准论文清单检索核验
description_en: Benchmark paper inventory builder
disable: false
agent_created: true
---

# benchmark-paper-inventory

## When to use
用户要求「列出在 benchmark X/Y/Z 上做实验的论文清单」（尤指机器遗忘/LLM 领域），需要方法简称、全称、链接、venue、代码、实验配置（模型/数据集），并要求 venue 可溯源、可与已有维护表去重时。

## Steps
1. **明确口径**：与用户确认 ①收录范围（严格 CCF-A / +COLM+高引预印本 / 全部）②是否含基准论文本身 ③输出位置（独立文件 or 并入主表）④是否顺带下载缺失 PDF。收录判据默认=「论文自身实验用了该基准」，仅引用/仅被第三方评测的不计入。
2. **P1 五路检索**（2-3 个并行子智能体，只做研究不写文件）：
   - 路A 框架反查：官方评估框架 GitHub（如 locuslab/open-unlearning 的 docs/links.md）+ 各基准项目页 leaderboard。
   - 路B 引用链：Semantic Scholar API `https://api.semanticscholar.org/graph/v1/paper/ARXIV:<id>/citations?fields=title,externalIds,venue,year&limit=100` 查基准原文被引。
   - 路C 会议逐年扫（防漏主防线）：proceedings.mlr.press / papers.neurips.cc / openreview.net / aclanthology.org / ojs.aaai.org，关键词 unlearn*/forget*/基准名。
   - 路D 综述交叉：最新 survey 的「benchmark × Used by」表。
   - 路E 关键词直搜补漏。
3. **P2 核验去重**（并行子智能体，每篇：开 arXiv 页核对 ID↔标题 → 找官方收录页 → 定级 ✅CCF-A/✅COLM/⚠️CCF-B或Findings/📄预印本）：
   - venue 只信官方页面（OpenReview/PMLR/proceedings/ACL Anthology/AAAI OJS/dblp 辅证）；仅 arXiv comments 自称 → 标「待复核」。
   - 与已有维护表逐篇去重（键：arXiv ID 主，标题次），标「已在主表」；顺带复核已有表的「venue 需复核」项。
4. **P3 PDF 下载**（仅 ⚠️剔除线以上且本地缺失者）：
   - 先 `find <pdf库> -name "*.pdf" | grep -iE "<关键词>"` fuzzy 匹配防重复下载。
   - arXiv 直链 `https://arxiv.org/pdf/<id>` 优先。NeurIPS 2025 proceedings 用 `/paper_files/paper/2025/file/<hash>-Paper-Conference.pdf`（`/hash/` 路径会 404）。AAAI OJS 需 `curl -sL --compressed`（否则得 gzip 乱码），galley 链接形如 `/index.php/AAAI/article/view/<id>/<galley_id>`，从页面 HTML 提取。
   - 三重校验：`head -c 5` = %PDF- ；>100KB；pypdf 抽首页文本比对标题关键词（注意 PDF 抽取会丢空格，如 "MODELSTATEHISTORY"，误判时肉眼复核前 120 字符）。
5. **P4 成文**：卷首统计+口径+标签定义；基准论文单独第〇节；正文按基准分节（跨基准论文主节全行+他节引用行）；末尾勘误记录（venue 升级项，反哺已有表）+ 待复核清单 + 数据缺口声明。

## Pitfalls
- arXiv ID 严禁凭记忆填写，必须逐条打开验证标题一致（用户有下错论文前科）。
- 2025-2026 论文 venue 误判高发：预印本常自称 "accepted at X"，无官方页一律 📄。
- 同名/同团队论文易混淆：如 WGA(ICLR 2025)≠SatImp(ICML 2025)；同一 arXiv 号可能对应与已有表不同的方法简称（如 2408.06621=LoKU=IHL+FILA）。
- 早于基准诞生的经典方法（ROME/SCRUB/SalUn 等）自身实验未用基准，不计入，但需在边界说明中交代。
- 子智能体并行限流（429）时，缩范围重发单一路线即可。
- curl 抓 OJS/部分站点必须 `--compressed`；OpenReview `/pdf?id=` 常被浏览器验证拦截，优先 proceedings/arXiv。

## Verification
- 清单每行 venue 有官方 URL；arXiv 列逐条已验证；留「—」字段=未核实非编造。
- 下载的 PDF 全部通过三重校验并记录到清单附录。
- 统计数（各级篇数）与各表实际行数一致。
