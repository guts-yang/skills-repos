---
name: paper-math-note
description: Extract text/math from academic PDFs (especially Chinese-titled ML/unlearning papers), locate precise formulas via grep, and produce a clean Markdown note using Unicode math + code blocks that renders correctly in ANY plain Markdown viewer (no LaTeX/MathJax dependency). Use when a user asks to "精读/梳理/解读某篇论文的数学推导、公式、实现原理" or to connect a paper's method to machine-unlearning / LLM fine-tuning innovation. Designed for the /Users/chenyliao/MuRAG/Papers workspace.
description_zh: 论文数学笔记
description_en: Paper Math Note
disable: false
agent_created: true
---

# paper-math-note

## When to use
- User asks to 精读 / 梳理 / 解读 a paper's 数学推导 / 公式 / 实现原理 / 底层逻辑.
- User wants to relate a paper (LoRA, ReLearn, Safe Mutations, SimNPO, ES-at-Scale, etc.) to 机器遗忘 / LLM 微调 / 新方法创新.
- The PDF may have a Chinese filename (e.g. `【ReLearn】...pdf`) and live in a nested subdir like `论文原文v3/实验复现/`.

## Steps

### 1. Locate the PDF locally first (avoid blind web-search)
```bash
cd /Users/chenyliao/MuRAG/Papers
find "论文原文" "论文原文v3" -type f -iname "*<keyword>*" 2>/dev/null
# keyword tips: use English short token AND Chinese 【】prefix; also scan nested dirs (实验复现, GA x SGD, 2026)
# e.g. for ReLearn: find . -iname "*relearn*"  # often MISSING because file is 【ReLearn】..., so also grep for 实验复现 subdir
```
If not found locally, fall back to WebSearch for arxiv id + key method terms.

### 2. Extract full text with an ISOLATED pymupdf venv (never pollute global env)
```bash
P=/Users/chenyliao/.workbuddy/binaries/python/versions/3.13.12/bin/python3
VENV=/Users/chenyliao/.workbuddy/binaries/python/envs/pdfread
[ -d "$VENV" ] || "$P" -m venv "$VENV"
"$VENV/bin/pip" install --quiet pymupdf
"$VENV/bin/python" - <<'PY'
import pymupdf
pdf = pymupdf.open("/abs/path/to/paper.pdf")
out=[]
for i,page in enumerate(pdf):
    out.append(f"\n===== PAGE {i+1} =====\n"+page.get_text())
open("/Users/chenyliao/MuRAG/Papers/.workbuddy/memory/<paper>_text.txt","w").write("".join(out))
print("pages",pdf.page_count,"chars",len("".join(out)))
PY
```
NOTE: extracted `.txt` often contains NUL bytes; always read it via a Python script (open bytes, `.replace(b"\x00",b"")`, decode utf-8), NOT via the Read tool directly (Read treats NUL as binary).

### 3. Locate precise formulas / method via targeted grep (in Python, not shell grep)
```python
text = open("/Users/chenyliao/MuRAG/Papers/.workbuddy/memory/<paper>_text.txt","rb").read().replace(b"\x00",b"").decode("utf-8","ignore")
for kw in ["Algorithm","Equation","∇","loss","L_","reparameter","update rule","where","z-score","σ","α","rank","freeze","target module"]:
    idx=text.find(kw)
    if idx>=0: print(f"\n--- {kw} @ {idx} ---\n", text[idx-150:idx+350])
```
Search for method/algorithm/appendix sections specifically; for math derivations, the paper usually states the final formula but NOT the derivation — you may need to derive yourself (e.g. ES gradient = score-function/REINFORCE derivation).

### 4. Write the note — CRITICAL formatting rule
- **Use Unicode math + fenced code blocks ONLY. NO LaTeX `$...$`, NO `\command`, NO `$$`.** The user's viewer does NOT render MathJax/KaTeX; LaTeX shows as raw source garbage.
- Symbol conventions to avoid font issues: write `~D` for D̃ (tilde set), `L` for ℒ (loss), `E[·]` for expectation, `≠ ∪ ‖ ∑ ∨ ∧ θ → ≪` are fine as Unicode.
- Structure that worked well across this workspace:
  1. 一句话定位 2. 数学推导（带完整、逐步推导，标出 ★核心公式）3. 算法/实现解读（逐 trick 列表）4. 复杂度/对比 5. 与 RL/相关方法的关系 6. 复用伪代码 7. 新方法 trick（编号列出，每个讲"为什么是新 trick"）8. 可行性（评分+风险清单）9. 一句话记忆.
- Save to `/Users/chenyliao/MuRAG/Papers/实验与SOTA/<Paper>_数学底层与...笔记.md`.

### 5. Update workspace memory
Append a one-line note to `/Users/chenyliao/MuRAG/Papers/.workbuddy/memory/YYYY-MM-DD.md` (create if absent). Record: paper -> note path, core formula, and any 新颖性核查 (whether the idea is already occupied by another paper — important to avoid claiming novelty that's taken).

## Pitfalls
- Read tool on the NUL-containing extracted `.txt` fails → always parse via Python.
- Chinese `【】`-prefixed filenames + nested subdirs → plain `find *unlearn*` misses them; scan `实验复现/`, `GA x SGD/`, `2026/` explicitly.
- LaTeX math breaks in user's viewer → must use Unicode + code blocks (this was a corrected mistake in-session).
- Don't over-claim novelty: before proposing "X × Y 创新", search whether the core idea already exists (e.g. Safe Mutations sensitivity idea was independently rediscovered in unlearning as GRI/WAGLE/Zuo; EvoMU already occupies "evolutionary loss search"). State this honestly.
- Keep method claims grounded in the actual PDF, not prior knowledge.

## Verification
- Re-open the written `.md` with Read to confirm no stray `$` / `\frac` / `\mathcal` remain.
- Confirm the file path exists and present it via present_files.
- If the note connects to another paper already summarized, add a cross-reference (e.g. "见 SimNPO 笔记第7节") instead of repeating.
