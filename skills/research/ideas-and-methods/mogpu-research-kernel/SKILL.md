---
name: mogpu-research-kernel
description: Build or extend the MOGP-U research kernel for budget-controlled, multi-objective LLM unlearning loss discovery. Use when implementing typed AST loss expressions, safety gates, GP/NSGA-II search, protocol isolation, or reproducibility controls under /Users/chenyliao/MuRAG/DirectionA-MOGP-U.
description_zh: MOGP-U 研究内核
description_en: MOGP-U Research Kernel
disable: false
agent_created: true
---

# MOGP-U Research Kernel

## When to use

Use this skill when modifying the direction-A MOGP-U prototype at `/Users/chenyliao/MuRAG/DirectionA-MOGP-U`, especially for:

- typed AST grammar, canonicalization, complexity, and static safety;
- GP initialization, semantic-channel crossover/mutation, or NSGA-II selection;
- fixed-budget TOFU / MUSE experiment protocol and Search/Validation/Sealed-Test isolation;
- run ledger, candidate freezing, baseline fairness, or audit orchestration.

## Steps

1. Read `docs/benchmark_protocol.md`, `configs/protocol/frozen_protocol.json`, and `docs/implementation_status.md` before changing experimental code.
2. Keep the search gene restricted to the AST. Do not make steps, LoRA rank, data order, early stopping, attack settings, or model choice searchable.
3. Define a semantic-observable manifest before extending the DSL: every terminal must declare its operational definition, model quantity, unit/sign convention, intervention direction, expected failure mode, and permitted benchmark scope. Prefer non-negative semantic atoms such as residual forget memory, retain drift, and forget-margin deficit over unconstrained raw log-probability arithmetic.
4. Restrict final candidate losses to the frozen interpretable normal form: exactly `E+R` or `E+R+S`, where `E=EraseResidual`, `R=RetainDrift`, and `S=SelectiveMargin`. Use non-negative normalized coefficients on a fixed discrete simplex and explicitly declared bounded transforms. Do not let GP freely mix raw `z_f`, `z_r`, reference values, and deltas into opaque algebra. The AST renderer must be able to emit a term-by-term natural-language mechanism card.
5. Extend the DSL only with typed, serializable, backend-agnostic nodes. Apply grammar validation, canonicalization, deterministic hash, numerical probes, monotonicity checks, and path checks before a candidate reaches GPU training.
6. Freeze the raw-variable sign convention in the manifest before applying monotonicity gates. Under the currently declared log-probability convention, the forget-residual channel must satisfy `dL/dz_f >= 0`. A symmetric retain-drift channel must instead satisfy the restorative condition `Δ_r * dL/dΔ_r >= 0`, so gradient descent pulls drift toward zero; only a one-sided retain-anchor channel should require `dL/dz_r <= 0` while active. If the backend exposes NLL or another quantity, derive and document the corresponding signs rather than reusing these inequalities blindly.
7. Ensure GP operations exchange only compatible semantic channels. Record parent hashes, operator, generation, configuration hash, gate status, failure reason, and a semantic explanation card for every candidate.
8. In NSGA-II, treat static-gate failures and FQ-ineligible candidates as infeasible. All actual objectives use the maximize convention, with complexity and instability negated.
9. Freeze candidates after Search. On Validation, apply the pre-registered FQ and retain-noninferiority gates, then the knee-point rule. Do not inspect Sealed Test before the AST is frozen.
10. Add tests for every new rule, then run:
   ```bash
   PYTHONPATH="/Users/chenyliao/MuRAG/DirectionA-MOGP-U" /Users/chenyliao/.workbuddy/binaries/python/versions/3.13.12/bin/python3 -m unittest discover -s "/Users/chenyliao/MuRAG/DirectionA-MOGP-U/tests" -v
   ```

## Pitfalls

- Do not call the work “first GP/NSGA-II loss search”; EvoMU is direct prior work. The defensible contribution is constraint/auditability, fixed-budget isolation, explicit Pareto selection, and sealed evidence.
- Never compare Llama-3.2-1B proxy outcomes with LLaMA-2-7B-chat SOTA outcomes in one ranking table.
- `FQ >= 0.05` for every final seed is a feasibility gate, not an objective to average away. Compare MU only among FQ-eligible methods.
- Random AST versus GP, scalar GP versus NSGA-II, fixed versus variable budget, and removal of safety/complexity/stability/relearning terms are mandatory ablations.
- This prototype is not a training system until TOFU, PEFT/LoRA, reference caches, official metric bridges, and sealed attacks are actually integrated.

## Verification

- All unit tests pass.
- JSON protocol and run-ledger schema parse successfully.
- Canonically equivalent ASTs share one hash and cache key.
- Unsafe formulas (positive retain gradient, variable denominator, non-whitelisted constants, non-finite output) are rejected before model execution.
- Any result report identifies model, benchmark, split tier, seed, budget, AST hash, configuration hash, and whether it is sealed.
