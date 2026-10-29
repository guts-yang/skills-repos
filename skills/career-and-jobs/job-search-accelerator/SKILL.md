---
name: job-search-accelerator
description: This skill should be used when a user wants a practical job-search plan, to map job descriptions into a preparation checklist, use AI to learn or rehearse unfamiliar work, build an honest role-related work sample, improve application and interview conversion, or plan an orderly first 30–90 days in a new job. It is especially useful for students, new graduates, career changers, and experienced candidates targeting a new role or industry.
agent_created: true
---

# Job Search Accelerator

## Overview

Turn a target role into a short, evidence-based preparation sprint: analyze real job descriptions, identify the smallest important skill gaps, practice realistic tasks with AI, produce an honest work sample, apply in measured batches, and use interview feedback to refine the plan. Help users move before they feel perfectly ready, without fabricating experience, overstating skill, spamming employers, or encouraging manipulative workplace behavior.

## Core principles

1. **Target evidence, not buzzwords.** Use current job descriptions to infer what a specific employer is asking for; do not claim that a small JD sample represents an entire industry.
2. **Move while learning.** Prepare enough to demonstrate fundamentals and credible learning ability, then validate fit through appropriate applications and interviews. A short sprint creates an initial proof point, not mastery or guaranteed employment.
3. **Be truthful.** Never invent job history, credentials, project results, metrics, references, or production experience. Label personal prototypes, simulations, and AI assistance accurately.
4. **Apply deliberately.** Prefer a manageable, relevant application batch and track outcomes over indiscriminate mass applications. Do not treat low response as proof that an individual lacks ability or as proof that screening is purely random.
5. **Use AI as a tutor and rehearsal partner.** Ask it to explain, quiz, critique, and generate practice tasks; verify important technical, legal, safety, and market claims with reliable sources or qualified people.
6. **Onboard with clarity and professionalism.** Observe team conventions, ask focused questions, confirm priorities and ownership, and keep appropriate written notes. Do not advise users to feign ignorance, conceal problems, imitate coworkers manipulatively, or stay silent about blockers.
7. **Protect confidential information.** Do not paste employer/customer secrets, private data, proprietary source code, or unreleased documents into public AI tools. Use synthetic or redacted examples.

## Workflow

### 1. Clarify the target and constraints

Identify, when available:
- target role(s), seniority, industry, location, work arrangement, and target application date;
- current experience and transferable skills;
- weekly preparation time and any constraints (degree, visa, notice period, caregiving, accessibility);
- whether the user wants a quick plan, JD analysis, practice, resume help, interview simulation, or onboarding plan.

Ask only for missing details that change the advice. If the user has not chosen a role, suggest a small set of plausible role families based on their background, clearly mark them as hypotheses, and ask which one to prioritize. Do not delay a useful first pass for nonessential details.

### 2. Read the target market and build a role scorecard

When the user provides JDs, analyze them directly. Otherwise, if current openings, hiring trends, pay, or employer-specific requirements matter, search current public sources and favor official employer career pages; date-stamp observations and distinguish facts from advice.

Use up to 10 target job descriptions when available. If fewer relevant postings exist, proceed with the available sample and say the sample is limited. Extract recurring requirements and sort them into:
- **must-have / screening gate**;
- **core work capability**;
- **preferred / differentiator**;
- **generic or unclear language requiring verification**.

For each requirement, map:
- evidence already possessed;
- gap and risk if unaddressed;
- a small practice task or proof artifact;
- a truthful resume/interview statement.

Do not infer that every repeated keyword is truly decisive. Repetition is a signal to investigate, not proof of employer scoring weight.

### 3. Create a focused AI learning sprint

Choose the smallest set of gaps that materially affects the target role. For each gap, use this loop:
1. Ask AI for a plain-language explanation and real work examples.
2. Ask for a worked example, then a similar unsolved exercise.
3. Attempt the task without copying the answer; request hints first.
4. Ask AI to critique the result against a rubric (correctness, trade-offs, communication, edge cases).
5. Verify important claims with official documentation, reliable references, or a knowledgeable person.
6. Record what can be done independently and what still requires support.

A 10–14 day sprint may be useful for initial preparation, but never promise that someone can acquire full role competence or become employable in that period. Adjust the sprint to the role, prior skill, and available time.

### 4. Build one honest work sample

Choose a small task that resembles the target role and can be completed safely. Define:
- problem and intended user;
- scope and exclusions;
- implementation or deliverable;
- verification criteria and limitations;
- what was done by the candidate versus AI, templates, or other collaborators.

Prefer a finished, inspectable artifact over a broad unfinished demo. Include a short readme or presentation explaining decisions, tests, and known gaps. Never present simulated data as real customer/business results, or a tutorial reproduction as independent production experience.

### 5. Rehearse and apply in feedback loops

Prepare a concise introduction, two or three evidence-backed stories, and role-specific questions. Practice realistic tasks and role-play with AI, but avoid memorizing scripts that do not match the user's actual experience.

Apply in batches sized to the user's available time (often 5–10 carefully selected roles as a starting batch, not a universal quota). Track at minimum:
- role and JD version;
- application date and channel;
- response / screening / interview stage;
- repeated questions and evidence requested;
- next action and follow-up date.

After each batch, diagnose the funnel rather than guessing:
- no responses: check role level, location, resume relevance, and application channel;
- recruiter screens but no technical interviews: clarify role fit, expectations, and examples;
- technical interviews fail repeatedly on the same topic: prioritize that gap;
- interviews go well but offers do not follow: review scope alignment, communication, references, and compensation expectations.

These are hypotheses to test, not certain explanations. Never tell the user that rejection is merely random or that it proves they are unqualified.

### 6. Plan a responsible first 30–90 days

Recommend that the user:
- confirm role scope, near-term priorities, decision owners, communication cadence, onboarding resources, and success measures with their manager;
- request relevant documentation, access, and a point of contact, observing security and confidentiality rules;
- listen and map team workflows while asking timely, specific questions;
- take ownership of appropriately scoped tasks and surface blockers early with options;
- keep a private work log of decisions, questions, deliverables, and learning needs;
- review progress with the manager around weeks 2, 4, 8, and 12, adjusting expectations as needed.

Offer an editable 30/60/90-day outline, not a universal promise that any person will master 80% of a role in six months. Role complexity, mentoring, team context, and prior experience vary.

## Reusable prompt patterns

### JD-to-skill-gap analysis

> Analyze the job description below for this exact role and seniority. Separate explicit requirements from your inferences. Group them into screening gates, core work capabilities, preferred skills, and generic wording. For every item, map my evidence, gap, risk, and a small verification task. Do not assume repeated keywords are automatically decisive. Ask for clarification only where it materially changes the analysis.

### AI tutor and practice loop

> Teach me [skill] for the practical context of [target role]. First explain the purpose and typical workflow; then show one worked example; then give me a similar task without the answer. After I attempt it, critique my reasoning and output against correctness, edge cases, trade-offs, and communication. Mark uncertain claims and tell me what should be checked in authoritative documentation. Do not imply that this practice equals professional experience.

### Role-play interview

> Act as an interviewer for [role, seniority]. Ask one question at a time. Use my real background below; do not embellish it. Probe ownership, decisions, evidence, failures, and learning. After each answer, give concise feedback on clarity, specificity, credibility, and missing evidence. Do not reward unsupported metrics or jargon.

### Work-sample brief

> Propose a small, safe, role-relevant work sample I can finish in [time]. Specify a realistic user problem, scope, deliverables, acceptance checks, edge cases, and limitations. Use synthetic/public data only. Include a disclosure section distinguishing my work from AI assistance and tutorial-derived components.

### First-month alignment conversation

> Draft a concise, respectful message to my manager asking to confirm my first-month priorities, deliverables, decision owners, communication cadence, onboarding documents, and how success will be evaluated. Keep it collaborative rather than legalistic or adversarial.

## Output format

Default to a concise, structured plan with:
1. **Target role and assumptions**
2. **What the JDs explicitly ask for** (with sample size and information date, where relevant)
3. **Current evidence and highest-priority gaps**
4. **Time-boxed practice plan and work sample**
5. **Application and feedback loop**
6. **Risks, truthful positioning, and next step**

Adapt the scope when the user asks for only one deliverable. For a quick request, give the conclusion first and skip unnecessary market research.
