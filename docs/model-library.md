# Model Library — mechanistic models for oral–systemic hypothesis generation

> The curated, cited catalog behind [`MODELS.md`](MODELS.md) and [`SOLUTION.md`](SOLUTION.md). Pruned to
> five tiers by decreasing commitment (an honest census — most of the field we explored is *not*
> load-bearing): **Core spine (built) → Flagged scaffolds (swept) → Staged substrate (next axes) →
> Reference-only (cited, not built) → Explored & rejected (with the reason).** A reader sees at a glance
> what runs, what's swept as a range, what's queued, and what was tried and killed — nothing is lost,
> nothing is over-claimed. **Non-diagnostic:** every model generates falsifiable hypotheses about
> population/parameter-level quantities, never a patient diagnosis or an imputed value.

## 1. The organizing principle — one source, one shared parameter, many axes

One defensible mechanistic chain from the mouth to the systemic axes, every stage an established model:

```
 periodontal source            systemic transducer                 downstream axis
 ─────────────────             ──────────────────                  ───────────────
 local cytokines/LPS   ──►  human acute-phase (Relouw) ──►  IL-6→hepatic CRP turnover ──┬─► CV: atherosclerosis ODE
 (Fujihara source)          (E2.3)                          (Pepys, t½≈19h,             │   (E2.6)
                                                             calibratable to NHANES)     └─► NEURO: neuroinflammation (E2.7)
                                                                                             → tau spread on the connectome (E2.8)
```

**One shared parameter — effective inflammatory gain (excess IL-6).** The same quantity drives the CV,
neuro, and (staged) metabolic/microbiome axes, so one ε/`gain` sweep propagates coherently and the agent
reports **ranges of falsifiable hypotheses**, never points. **Two epistemic-risk parameters** carry the
uncertainty and are swept, never asserted: **ε** (oral→systemic spillover efficiency) and **the
inflammation→α multiplier** on tau spread. Mendelian-randomization favors **IL-6/IL-1β as causal, CRP as
a marker** — the agent privileges IL-6 as the driver, CRP as the observable.

---

## 2. Core spine — built, load-bearing

**E2.3 Human LPS acute-phase kernel (Relouw 2024).** Human-scaled IL-6 dynamics (μ_IL6=ln2/2 h); the
source→IL-6 stage. Indirect-response `dX/dt=k_in·stim·inhib − k_out·X`. *Relouw et al. 2024, npj Syst
Biol Appl 10:146 (PMC11621538).*

**E2.4 Periodontitis host–microbe / bone-loss source (Fujihara 2023).** Bacteria→TLR→monocyte
recruitment drives the local cytokine source; implemented as structural bands feeding `ε·structural_load`.
*Fujihara et al. 2023, J Dent Res 102(13); biofilm Martin 2017, PLoS ONE 12:e0173153.*

**E2.5 IL-6→hepatic CRP turnover (Pepys) — the transducer & ε-calibration anchor.** CRP a near-linear
low-pass integrator of IL-6, t½≈19 h. `dCRP/dt=k_syn·IL6/(EC50+IL6)−k_deg·CRP`; spillover `IL6+=ε·load`.
Calibratable to **NHANES hs-CRP + ΔCRP-after-therapy**. The single most load-bearing edge. *Pepys &
Hirschfield 2003, JCI 111:1805.*

**E2.8 Prion-like tau spread — Fisher–KPP on the connectome (neuro math anchor).**
`∂c/∂t=∇·(D∇c)+α c(1−c)`; network `dc_i/dt=−κ Σ_j L_ij c_j+α c_i(1−c_i)`, L=connectome Laplacian.
Bayesian ADNI fit κ≈1.30 µm/yr; inflammation enters as α→α(1+β·gain). *(Subsumes the former "network tau
spread modulated by inflammation" label — same model.)* *Fornari et al. 2019, J R Soc Interface
16:20190356; Schäfer et al. 2021, Front Physiol 12:702975; Raj et al. 2021, Brain Connect 11(8):624.*

**E2.10 Cytokine/CRP PK-PD (TMDD) — the counterfactual lever.** IL-6R blockade (tocilizumab) TMDD + CRP
indirect response: regulatory-grade proof the transducer is turnover-kinetic; the "neutralize IL-6 →
predicted ΔCRP" lever. *tocilizumab PK-PD 2011, JPKPD 38:769.*

**E4.5 Gingipain-inhibition therapeutic test — the honesty anchor (negative result).** Atuzaginstat/GAIN
trial **failed both endpoints, hepatotoxicity, FDA hold, program abandoned** (Cortexyme→Quince). Wired
into `mech_neuro` flags — *why* the neuro edge stays a swept hypothesis, not a result. *review
PMC10275298; Alzforum.*

**E4.6 Epidemiological risk / NHANES perio↔cognition — the validated association.** Severe periodontitis
~2.9–6.9× dementia risk (meta-analytic). Implemented in `perio_cognition.py`: NHANES 2011-2012, 3/4
cognitive measures significant, confounder-adjusted — the neuro axis's empirical anchor. *Noble et al.
2009, JNNP (PMC3073380); meta-analysis 2025 (PMID 40335202).*

## 3. Flagged scaffolds — real biology, imposed math, swept as a range (never asserted)

**E2.6 Systemic inflammation → early atherosclerosis (CV).** oxLDL→monocyte→macrophage→foam-cell
positive feedback; implemented as `recruitment_multiplier = 1 + γ_cv·gain`. *MR: CRP marker, IL-6/IL-1
causal — frame accordingly.* *Ougrinovskaia et al. 2010, Bull Math Biol.*

**E2.7 Neuroinflammation–amyloid–tau cascade (Hao & Friedman 2016).** The neuro node the gain forks
into; implemented as a reduced saturating `N(gain)` gating tau-α. Full cascade weakly identifiable →
kept as the swept coupling, not a fit. *Hao & Friedman 2016, BMC Syst Biol 10:108.*

**E3.2 Diabetes↔periodontitis coupling.** `gain → insulin-sensitivity` set-point shift (the monotone
coupling, **not** the decorative loop-gain instability), anchorable to the ~0.3–0.4 pp HbA1c-drop-after-
therapy meta-analysis + in-cycle NHANES 2009-2010 HbA1c. *Graves et al. 2026, J Dent Res.*

**E4.2 Systemic inflammation → neuroinflammation (IL-6/TNF/IL-1β) — the central hypothesis.** The
best-supported oral→neuro bridge; **realized by E2.7 → E2.8**, not separate code. *Ide et al. 2016, PLoS
ONE 11:e0151081 (periodontitis→~6× faster ADAS-cog decline).*

## 4. Staged substrate — not built; the direct substrate for the next axes

**E3.1 Bergman glucose–insulin minimal model.** `dG/dt=−(p1+X)G+p1 G_b; dX/dt=−p2 X+p3(I−I_b)`;
S_I=p3/p2. **The substrate the C4 diabetes coupling (E3.2) is built on.** *Bergman et al. 1979, Am J
Physiol 236:E667.*

**E3.5 Disordered generalized Lotka–Volterra (oral microbiome).** `dN_i/dt=N_i[ρ(K_i−N_i)−Σα_ij N_j]+…`;
replicon eigenvalue R→0 = marginal stability. Public data: **NHANES 2009–2012 oral-rinse 16S.** **Staged
substrate for a future microbiome axis** (identifiability weak — flagged-exploratory). *Pasqualini et al.
2026, eLife 14:RP105948.*

**E3.6 Two-species biofilm (*P. gingivalis* vs *S. gordonii*).** Reaction–diffusion biomass+damage,
fitted in vitro. Substrate for the microbiome-source detail. *Martin et al. 2017, PLoS ONE 12:e0173153.*

**E3.7 Allee/quorum threshold for *P. gingivalis* persistence.** `dN/dt=rN(1−N/K)(N/A−1)`; keystone
dysbiosis-onset threshold. Substrate for the microbiome axis. *npj Syst Biol Appl 2026 s41540-026-00662-x;
Hajishengallis et al. 2012, Nat Rev Microbiol 10:717.*

## 5. Reference-only — cited, not built (superseded or no in-hand data path)

- **E1.4 Gingival crevicular fluid flow** (`J=dV/dt`) — the source boundary condition, subsumed by
  `ε·structural_load`; GCF values sparse. *Goodson 2003, Periodontol 2000 31:43.*
- **E1.5 Windkessel under inflammation** (`C dP/dt+P/R=Q`; PWV) — no PWV in NHANES; CV covered by E2.6.
  *Westerhof et al. 2009, Med Biol Eng Comput 47:131.*
- **E1.6 Bacteremia transport pocket→circulation** — an alternate source the ε-abstraction already
  swallows; useful only to bound ε. *Forner et al. 2006, JCP 33:401; Lockhart et al. 2008, Circulation.*
- **E2.1 Reynolds 4-ODE acute inflammation** — murine/dimensionless; the human pipeline uses E2.3.
  Conceptual reference for bistability. *Reynolds et al. 2006, J Theor Biol 242:220.*
- **E2.2 Kumar 8-ODE endotoxin** — its insight ("IL-6 integral, not TNF peak, drives damage") is *why*
  IL-6 is the shared scalar; the 42-param model itself is unidentifiable. *Kumar et al. 2004, JTB 230:145.*
- **E3.4 Inflammation-as-control-system / bistability** — falsifiable test needs GCF IL-10/TNF we don't
  have; overlaps E2.1/E3.5. Narrative reference for chronicity. *Kotas & Medzhitov 2015, Cell 160:816.*

## 6. Explored & rejected — the graveyard (kept as one line + the reason, so we don't re-explore)

- **E1.1 WSS/CFD → endothelium** — REJECTED: needs patient-specific vascular geometry/imaging we cannot
  get from NHANES; the "periodontitis shifts the low-WSS threshold" coupling has no data path.
- **E1.2 Glymphatic advection–diffusion (Aβ)** — REJECTED: needs PVS velocities/AQP4/brain-transport
  params we don't measure; two speculative hops to oral inflammation; unvalidatable on our data.
- **E1.3 Sleep-dependent glymphatic** — REJECTED: the periodontitis→sleep→clearance chain is decorative;
  no in-hand dataset to pin it.
- **E1.7 Bacteremia→BBB (Kedem–Katchalsky)** — REJECTED: quantitative model admittedly missing;
  gingipain-driven permeability unparameterizable; duplicates the implemented saturating BBB gate.
- **E2.9 Raj size-resolved Smoluchowski tau** — REJECTED: duplicates E2.8 with machinery we can't fit
  (no size-resolved tau-PET) + an unreviewed 2026 preprint for the joint-inflammation part.
- **E3.3 Guyton/baroreflex BP** — REJECTED: no baroreflex-sensitivity data in NHANES; inflammation→
  baroreflex coupling speculative; decorative.
- **E3.8 Alternative-stable-states / fold / chaos framing** — REJECTED: tipping/hysteresis is "hard to
  distinguish from cross-sectional data" and cross-sectional is all we have; duplicates E3.4/E3.5.
- **E4.1 P. gingivalis brain-invasion (SIR/logistic)** — REJECTED: no brain-Pg data, direction
  unresolved, and the one direct causal test (atuzaginstat) failed — keep the failure (E4.5), not the model.
- **E4.3 Oral–gut–brain axis** — REJECTED: weak quantitatively, no model, no data path; a longer
  speculative detour around the direct systemic bridge (E4.2).

*(E4.4 removed outright — it was a duplicate label for E2.8, folded above.)*

---

## 7. Bridging biomarkers & Gladstone alignment (for the neuro axis)

**Bridging biomarkers.** Oral: CAL/pocket depth/tooth count, subgingival 16S, anti–P. gingivalis IgG.
Systemic: IL-6, TNF-α, IL-1β, CRP, IL-10, LPS. Neuro: plasma p-tau181/217, Aβ42/40, NfL, GFAP;
tau/amyloid-PET; cognitive batteries. Public data: **NHANES** (oral+cognition+hs-CRP), **ADNI**
(tau/amyloid-PET + connectomes for E2.8), UK Biobank (tooth loss + cognition).

**Gladstone alignment.** Their neurodegeneration program centers on the nodes this library models: **tau**
(Mucke), **APOE4 + human iPSC** (Huang), **neuroinflammation & the blood–brain interface** (Akassoglou —
fibrinogen→BBB-leak→microglia→synapse loss, the same "peripheral insult→BBB→microglia→cognition" shape as
the periodontitis→brain hypothesis), **microglia/innate-immune senescence in tauopathy** (Gan). A
non-diagnostic agent that formalizes the inflammation→tau-spread coupling and proposes biomarker-
stratified oral→neuro experiments offers a **novel upstream perturbation** for those frameworks —
prioritized experiments, not clinical claims.

## 8. The centerpiece (wires the built spine end-to-end)

1. **Source** (E2.4): periodontal cytokine/LPS source, magnitude from BOP/pocket strata.
2. **Transducer** (E2.3 → E2.5): human acute-phase → IL-6→CRP turnover; **calibrate ε to the NHANES
   ΔCRP-after-therapy anchor** (what makes it a result, not a demo).
3. **Fork from the same IL-6/CRP state:** CV via E2.6; neuro via E2.7 → E2.8, validated against NHANES
   perio↔cognition (E4.6).
4. **Counterfactual lever** (E2.10): IL-6 neutralization → predicted ΔCRP.

Everything sweeps **ε** and the **inflammation→α multiplier** as ranges, privileges **IL-6/IL-1β causal,
CRP observable**, and stays strictly **non-diagnostic**. Next axes draw on §4 (staged substrate);
richer sub-models follow the technique + ensemble discipline of [`MODELS.md`](MODELS.md) §6.
