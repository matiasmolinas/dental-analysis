# The Approach — Inferred-Lens Observer & Session Working-Consciousness

> **Domain-general description of the method.** The *what* and *why* of the architecture,
> independent of the dental instance.
>
> **Status: the loop is validated as software; its lens-driven contribution is inconclusive.**
> When we tested whether reading the inferred lens improves outcomes *over blind convergence*,
> the result was `lens_inconclusive` — see [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md) §0. Read
> this doc as the method's design, not as a demonstrated win. The one clean win (missing-data
> flagging 0→1.0) is the **deterministic harness**, not the lens.

---

## 1. One paragraph

We run an agent system where a **second model instance — the Lens Observer — reads
the *inferred Jacobian lens* of the primary model** (the workspace self-report the
primary emits while it processes a prompt, and everything inside that prompt: the
skill, the knowledge-base context, the sub-agent definition, the injected variables),
diagnoses where that processing is deficient (a required variable missing or wrong, a
reasoning step skipped, a bridging concept never represented, the problem
under-specified), and uses the diagnosis to **evolve the system** — its prompts,
skills, knowledge base, sub-agent definitions, injected variables, and **harness
code** — while curating a cumulative **Session Working-Consciousness** it steers the
session from. The lens signal is *inferred* (self-report), not measured; the whole
loop is built to the interface of a real lens, so if one were exposed the same
architecture would consume a measured signal unchanged.

---

## 2. Why a lens, and why a *second* instance

A model that solves a relational problem must, internally, **represent the linking
concepts** — not just echo the inputs. Anthropic's July-2026 global-workspace result
found that a model's verbal self-report is causally read out of that internal
workspace: what it says it is thinking tracks what it is actually representing. That
makes a self-report **readout channel** a usable — if uninstrumented — window on
whether an input actually made the needed concepts representable.

Two design choices follow:

1. **Read the lens, don't just read the answer.** The final answer tells you *whether*
   the system was right; the lens tells you *why* — which variable never entered the
   workspace, which step was skipped, which bridging concept stayed absent. That is
   the signal you can act on to fix the *input*, not just grade the output.
2. **A separate instance reads it.** The Observer never does the task. This (a) gives
   a genuinely independent perspective, (b) stops the executor from grading its own
   homework, and (c) mirrors the paper's separation between the *model* and the
   external *lens* reading it. The Observer analyzes the **primary's** lens — the lens
   of the model actually processing the prompts — not its own.

---

## 3. The three roles

| Role | Instance | Does | Never does |
|---|---|---|---|
| **Executor** (primary) | Model A — the task agent(s), run with the inferred-lens readout active | The work; emits output **plus** its workspace readout | Decide its own evolution |
| **Lens Observer** (secondary) | Model B — a *separate*, capable instance | Reads the primary's readout, diagnoses deficiencies, curates the Session Working-Consciousness, proposes + applies bounded evolution | Produce the task output |
| **Gate / Guardrail** | A protected verifier | Enforce invariants at every gate | Ever be evolved |

The Executor↔Observer split is the load-bearing structure. Everything else is how the
Observer turns a readout into an improvement.

---

## 4. What the Observer reads out of the lens

Given the primary's readout (`schemas/lens_readout_schema.json`) and a **spec** of
what the prompt *should* have surfaced, the Observer extracts:

- **Concept coverage** — did the required bridging concepts surface, early and salient,
  or faint / late / absent? Absence is the signal.
- **Variable presence & correctness** — did each required input variable actually
  register, with a sane value?
- **Procedure / chain-of-thought coverage** — did the internal reasoning pass through
  the steps the task needs, or skip/shallow them?
- **Problem framing** — was the problem articulated with the variables needed to solve
  it, or under-specified?

Each gap becomes a typed **deficiency** (`schemas/deficiency_map_schema.json`):
`missing_mediator`, `missing_variable`, `wrong_value`, `uncovered_cot_step`,
`underspecified_problem`.

---

## 5. Five evolution surfaces

The Observer routes each deficiency to the **cheapest surface that fixes it**:

| Surface | Fix |
|---|---|
| **Work prompt** | reorder, add a problem-formulation constraint |
| **Skill** | make a reasoning step explicit; tighten a rule |
| **KB context** | add/modify a bridging knowledge snippet |
| **Sub-agent def + injected variables** | add a required parameter and how to derive it |
| **Harness code** | new/updated parser or deterministic analyzer whose output is injected |

The prompt-vs-code boundary is explicit: **deterministic + reproducible → code;
representational + semantic → prompt.** A value the model keeps approximating, or a
field the input handling keeps dropping, is moved into code (a parser or a
deterministic analyzer), tested, and its output injected back as a variable the lens
then re-checks. This is how the same signal that evolves prompts also evolves the
tooling.

---

## 6. Session Working-Consciousness — the closed loop

The primary has an **ephemeral per-call workspace** (its inferred lens). The Observer
maintains a **persistent cross-call working consciousness**: a curated, evolving
ledger it reads as its own context every turn and consolidates after every turn. It
holds the task model, a turn log of deficiencies→edits→outcomes, **consolidated
beliefs** promoted from repeated evidence, pending hypotheses, and the currently
active ephemeral injections. From it the Observer **injects or modifies the next
prompt** on its own criterion. It is a *curated optimization state*, not a transcript —
the difference between a system that merely has history and one that has a working
consciousness of the session it is steering.

---

## 7. Evolution tiers & gating

| Tier | Scope | Lifetime | Gate |
|---|---|---|---|
| **T0 ephemeral** | prompt/variable/KB adaptation, injections | in-session; auto-reverts at session end; logged | bounded + guardrail-safe + readout-grounded rationale |
| **T1 promoted** | committed edits to skills / sub-agent defs / harness code | persistent | strict held-out improvement **and** no drop in guardrail pass-rate **and** tests pass **and** human approval |

Two invariants make online self-modification safe:

- **Anti-Goodhart:** every edit must cite the readout evidence that justifies it. No
  evidence → not an edit. The final authority is task accuracy + the guardrail, never
  the readout score itself.
- **Protected guardrail:** the safety/compliance invariant is never evolved and is part
  of every gate. An accuracy gain that lowers guardrail pass-rate is rejected.

---

## 8. Epistemic honesty, corroboration, and the API feature we're proposing

**This project runs entirely on Claude.** We explore the Jacobian-lens paper
*indirectly* — through the self-report **skill**, not through any instrumented lens and
not on any open-weights proxy. The live signal is **inferred**: self-report exercised
as a readout channel, **not a measurement and not evidence about the world.** We say so
everywhere it appears, and the authorities remain task accuracy on Claude + the
protected guardrail — never the readout score.

Because the readout is self-report, the Observer **corroborates load-bearing claims
with an API-observable behavioral test** rather than trusting the readout alone:
**counterfactual sensitivity** — flip one input factor (e.g. a mediator present ↔
MISSING) and check that the dependent conclusion moves in the mechanistically-correct
direction while unrelated conclusions stay put. A conclusion *insensitive* to flipping
a factor it should depend on is the same "the model isn't really using it" signal the
lens gives, measured at the output. This keeps the loop grounded on Claude alone, with
no external instrument. Accordingly, `relational_recall` (a mediator counts only when
used inside a traced mechanism) and counterfactual sensitivity are the **primary honest
metrics**; plain substring `mechanism_recall` is secondary — the live Sonnet-5 v2 runs
showed unadorned recall is largely name-echo, not factor-grounded reasoning (see
`AB_PROTOCOL.md`).

> **The feature we're proposing to Anthropic.** The whole loop is built to the
> interface of a lens readout. On the evidence we gathered, the *inferred* signal is
> non-redundant with the output but did **not** improve outcomes over blind convergence
> (`lens_inconclusive`; [`RESEARCH_SUMMARY.md`](RESEARCH_SUMMARY.md) §0) — the access we
> have is the weak link, not the concept. That motivates a concrete, honest API ask:
> **expose the real Jacobian lens on Claude through the Anthropic API.** If it existed,
> the Observer would swap the inferred signal for a **measured** one with **no
> architectural change** — turning a directional, uncorroborated hint into causal ground
> truth and enabling representation swaps. Only the signal source would change. We raise
> it as a **forward claim to test, not a demonstrated result** — full case in
> [`API_FEATURE_REQUEST.md`](API_FEATURE_REQUEST.md).

---

## 9. Instantiating it on a new problem (domain-general recipe)

1. **Name the bridging concepts / required variables / procedure steps** the task
   needs represented — the *spec* the Observer scores against.
2. **Turn on the inferred-lens readout** on the executor for that task.
3. **Stand up the Observer** as a separate instance with the deficiency-analysis and
   session-working-consciousness instruments and the deficiency→surface routing.
4. **Define the five surfaces** for your system and which are T0 vs T1.
5. **Protect your invariant** (safety, compliance, correctness contract) as an
   un-evolvable gate.
6. **Add a harness seam** so deterministic values can be computed in code and injected.
7. **Corroborate on the model itself** with counterfactual-sensitivity flips (§8) —
   no external instrument, Claude only.

Nothing here is dental-specific. The dental oral-systemic agent is the first instance;
the method is the product.

---

## 10. Relationship to prior art

- **Global workspace / Jacobian lens** (Anthropic, 2026): the reason a self-report
  readout is a meaningful signal, and the measured instrument we would use directly if
  it were exposed on Claude via the API (§8) — the paper we are exploring *indirectly*
  through the skill.
- **SkillOpt** (Microsoft Research): skills as trainable state with bounded edits and a
  held-out gate — the discipline behind the T1 promotion tier, here generalized from
  skills to five surfaces.
- **`j-space-lens`** (skirano-skills, referenced not vendored): the community
  self-report skill that inspired the inferred-lens readout.

The novel composition is putting a **second instance in charge of the first's lens**,
giving it a **persistent session working-consciousness**, and letting it evolve **code
as well as prompts** — behind a protected gate.
