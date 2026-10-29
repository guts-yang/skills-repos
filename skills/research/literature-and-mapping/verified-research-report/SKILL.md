---
name: verified-research-report
description: >-
  Orchestrates a multi-agent deep-research report pipeline whose citations survive scrutiny: parallel
  scouting agents write drafts to disk, each chapter passes a review-revise loop, then all citations are
  verified by opening the primary source page, globally renumbered with a two-pass placeholder method,
  and gated by mechanical checks (dollar-delimiter balance, citation-set bidirectional diff, banned-name
  scan, URL-vs-paper match). Use when producing a literature survey, benchmark comparison, industry
  research report, or any long document whose references must be individually traceable — especially
  when the user has complained before about fabricated references, wrong venues, or mismatched arXiv IDs.
description_zh: 带引用核验的深度研究报告流水线
description_en: Verified-citation research report pipeline
disable: false
agent_created: true
---

# verified-research-report

## When to use

- The user asks for a 深度研究 / 文献综述 / 行业研究 / 竞品分析 / benchmark comparison report **and** cares about traceability.
- Any report where every reference must be individually checkable (arXiv ID, venue, year, author).
- The user has previously flagged fabricated citations, wrong venues, or string-numbered IDs as unacceptable.
- You are orchestrating sub-agents (TeamCreate / Agent) on a writing task and need the citation layer to not degrade.

Do **not** use for one-off literature lookups or short answers that stay in the conversation.

## Core principle

**An LLM writing ~100 citations will introduce errors.** Do not try to prevent this by writing more
carefully — prevent it with *mechanical gates* that fail loudly, plus *primary-source verification* by a
different agent than the one who wrote the claim.

## Steps

### 0. Freeze the brief into a file (context economy)
Write a single **parameter card** to disk, e.g. `报告/<topic>_Phase1_来源池与研究参数卡.md`, containing:
research questions (RQ1..RQn), output language, time window, citation format, formatting rules, and the
source pool. Every downstream agent **reads this file** instead of receiving the pool inline. This keeps
the orchestrator's context small across many sub-agent spawns.

### 1. Scout in parallel perspectives, one agent each
3–5 perspectives chosen to be adversarial to each other, e.g. mainstream methods / benchmarks &
evaluation reliability / failure & attack evidence / formalization & adjacent fields.
Each agent **writes its output to a file** and returns only a ≤200-word summary + file path + new-source list.

### 2. Plan the outline (separate agent), confirm with the user
5 chapters max. Force a **differentiation constraint**: if a competing survey exists, name it explicitly and
forbid re-treading its organizing axis.

### 3. Per chapter: research → review → revise loop (max 3 rounds)
- Chapter agent writes `drafts/<ch>.md`.
- Review agent reads the file and returns `PASS` or `REVISE` with line-level must-fix items.
- Reviser agent applies fixes, **writing back to the same file**.
- Round 3 must return PASS except for **citation-integrity** problems, which are never deferred.

### 4. Frame sections + dedupe + build a mapping table
One agent writes 目录 / 引言 / 结论 / a de-duplicated master reference list, **plus a complete
`章内编号 → 全局编号` mapping table** covering every chapter-local number. The mapping table converts
renumbering from guesswork into table lookup.

### 5. Assemble with two-pass placeholder renumbering
Never renumber in place — `[1]→[14]` then `[14]→[3]` cascades. Instead:
pass 1: replace every `[n]` in a chapter with `{{CH<k>-REF-n}}`; pass 2: substitute placeholders with global numbers.

### 6. Run the mechanical gates (see Verification) and fix failures
### 7. Have the citation verifier open every source page
Any claim's source is verified by an agent that did **not** write it. Unconfirmable ⇒ delete the citation
and re-examine every judgment that depended on it.

## Pitfalls

- **Venue over-claiming is the single most frequent error.** Preprints get written up as top-conference papers.
  Corollary: *absence of a venue in the arXiv abs-page Comments field is NOT evidence of doubt.* To settle a
  venue, check the conference's official proceedings, the `nips.cc/virtual/...` / `openreview.net` page, ACM DL,
  or DBLP — not the abs page alone.
- **An abbreviation is not a title.** Real examples encountered: `BYE` = method name *"Believe Your Eyes"* inside
  the paper *"Backdoor Cleaning without External Guidance in MLLM Fine-tuning"*; `PRISM` = method name inside
  *"Dual-Space Smoothness for Robust and Balanced LLM Unlearning"*; `CTRAP` = self-named mechanism. **Searching
  by abbreviation always fails** — always resolve the abbreviation to its owning paper's real title first.
- **A well-formed URL does not mean it points at the right paper.** A real case: an ACL Anthology URL cited for
  "NGDiff" actually opened a spatial-transcriptomics paper. Always open the URL and compare the title.
- **Placeholder-shaped IDs.** `openreview.net/forum?id=ControllableUnlearningI2I` looked plausible but OpenReview
  IDs are random strings (the real one was `9OJflnNu6C`). Semantic-looking IDs are a red flag.
- **Never send parallel Edit calls to the same file** — write-write races (last-write-wins) silently drop edits.
  Serialize them and re-verify after each.
- **absence claims need evidence.** "No work has done X" is only writable together with the search keywords and
  the databases/time window actually searched. Otherwise mark `[unconfirmed]`.
- **State the LaTeX scope explicitly.** If the user says "render formulas in LaTeX", write into the card:
  *all formulas, variable definitions, AND quantitative expressions; escape `%` as `\%`; verify `$` delimiter
  balance.* Otherwise every chapter interprets the scope differently and all of them get rejected.
- **Unbalanced `$` breaks the entire document's rendering.** Treat it as a top-severity incident, not cosmetics.
- **Don't let the orchestrator carry the report body.** Chapter text lives in files; agents return paths and summaries.
- **Wide comparison tables need the link on the work's name, not in a new column.** Tables of 9+ columns
  (method / year / venue / route / intervention site / granularity / mechanism / boundary / cost) become
  unreadable if you append a "paper link" column. Instead rewrite the first cell:
  `| [MMUnlearner](https://arxiv.org/abs/2502.11051) [2] | …`. This is purely additive — **never add or
  remove a `[n]` while doing it**, so the citation-set bidirectional diff stays untouched. Verify with:
  `diff <(grep -oE '\[[0-9]+\]' bak.md | sort -u) <(grep -oE '\[[0-9]+\]' new.md | sort -u)` → must be empty.
- **Tables whose rows are named works may have no `[n]` at all** (e.g. a benchmark table that cites numbers
  only in a "reliability warning" column). You then have to build a `name → reference number` map by hand and
  confirm each against the reference list before linking — do not guess from the row's other cells.
- **Back up before a bulk in-place edit** (`cp report.md report.md.bak`), then confirm afterwards that
  *only* table data rows changed: `diff a.md b.md | grep '^<' | grep -cvE '^\|'` must be `0`.

## Verification

**Run the bundled script first** — it performs all five mechanical gates at once:

```bash
bash ~/.workbuddy/skills/verified-research-report/scripts/verify_report.sh <报告文件.md>
```

Exit code 0 = all gates passed. It checks: `$`/`$$` delimiter balance, reference numbering continuity
1..N, citation-set bidirectional diff (dangling refs + orphan entries), banned-name scan, and
suspicious-link scan (placeholder-shaped OpenReview IDs, bare repo links, aggregator sites).

The underlying commands, if you need them individually:

```bash
# 1. $ delimiter balance — total must be even, and zero lines with an odd count
for f in *.md; do
  tot=$(grep -o '\$' "$f" | wc -l)
  odd=$(awk '{n=gsub(/\$/,"$"); if(n%2==1) c++} END{print c+0}' "$f")
  echo "$f total=$tot odd_lines=$odd"
done

# 2. Reference list is continuous 1..N with no gaps or duplicates
ids=$(grep -oE '^\[[0-9]+\]' report.md | grep -oE '[0-9]+' | sort -n)
[ "$(echo "$ids"|tr '\n' ' ')" = "$(seq 1 $(echo "$ids"|wc -l)|tr '\n' ' ')" ] && echo OK || echo GAP

# 3. Citation-set bidirectional diff: in-text set == reference-list set
grep -oE '\[[0-9]+\]' report.md | sort -u > intext
grep -oE '^\[[0-9]+\]' report.md | sort -u > reflist
comm -3 intext reflist   # must be empty (dangling refs AND orphan entries)

# 4. Banned / unverifiable names must appear only inside erratum notices
grep -n -iE 'MMUnlearnBench|SIUO' report.md

# 5. Collect cross-report set difference to expose coverage gaps
#    (compare this report's ID set against any previous report on the same topic)
```

- [ ] Every reference opened at least once at its primary source by a non-author agent.
- [ ] Every venue stated as a formal publication has a traceable official record.
- [ ] Coverage gap check done against prior reports on the same topic — and if a whole sub-direction is
      missing, run a **targeted re-scout** and record it as an appendix rather than silently dropping it.
- [ ] Unresolved items collected into a "待完善事项" section — never silently fixed or silently hidden.
