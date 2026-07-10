# Model Library — mechanistic models for oral–systemic hypothesis generation

> Curated by the Harness-0 deep-research pass (4 tracks, search-verified citations) — see
> [`SOLUTION.md`](SOLUTION.md). Each entry: domain edge → mechanism
> → math formalism → parameters/data → key papers → confidence → caveats.
> **Non-diagnostic:** every model generates falsifiable research hypotheses about population- or
> in-silico-level parameters, **never** a patient diagnosis or an imputed value. Status: **complete
> (2026-07-09)**.

## 1. The organizing principle — one source, one shared parameter, many axes

Two findings from the deep research make the library cohere into a single agent rather than a bag of
models:

**(a) The clean, calibratable pipeline (Track 2).** There is one defensible mechanistic chain from
the mouth to both systemic axes, and every stage has an established model:

```
 periodontal source            systemic transducer                 downstream axis
 ─────────────────             ──────────────────                  ───────────────
 local cytokines/LPS   ──►  human acute-phase (Relouw) ──►  IL-6→hepatic CRP turnover ──┬─► CV: atherosclerosis ODE / WSS / Windkessel
 (Fujihara bone-loss,       (TNF, IL-6, IL-10, cortisol)    (Pepys kinetics, t½≈19h,    │
  two-species biofilm)                                       calibratable to NHANES      └─► NEURO: neuroinflammation cascade (Hao–Friedman)
                                                             hs-CRP + ΔCRP after              ──► tau spread on the connectome (Fisher–KPP)
                                                             periodontal therapy)                  + glymphatic Aβ clearance (fluid track)
```

**(b) One shared parameter — effective inflammatory gain (Track 3).** The *same* quantity (a) degrades
insulin sensitivity S_I in the diabetes↔periodontitis loop, (b) is the control gain whose loss
produces a chronic-inflammation stable state, and (c) is the control parameter μ that pushes the oral
microbiome across its dysbiosis tipping point. A single sympy/scipy pipeline can vary that one
parameter and propagate it across the metabolic, cardiovascular, ecological, **and** neuro equilibria
— generating coherent, falsifiable, cross-axis hypotheses. That is the intended use of HISTORA.

**The two epistemic-risk parameters** carry almost all the uncertainty and must be treated as *swept
unknowns producing ranges of falsifiable predictions*, never point claims:
- **ε** — oral→systemic spillover/translocation efficiency (Track 2, Entry 5).
- **the inflammation → α/β multiplier** on tau-spread growth/transmissibility (Track 2, Entries 8–9).

Mendelian-randomization evidence favors **IL-6/IL-1β as causal nodes and CRP as a marker**, so the
agent should privilege IL-6/IL-1β as mechanistic drivers and use CRP as the observable.

## 2. Confidence map — what to build on vs. what to flag

| Tier | Models | Use |
|---|---|---|
| **Anchors (strong, fitted, simulation-ready)** | WSS→endothelium (Malek 1999); glymphatic advection–diffusion (Iliff 2012, Mestre 2018); sleep→clearance (Xie 2013); Bergman minimal model (1979); acute-inflammation ODEs (Reynolds 2006, Kumar 2004, **Relouw 2024 human**); IL-6→CRP turnover (Pepys 2003) + IL-6R-blockade PK-PD; Fisher–KPP tau spread on connectome (Fornari 2019, Schäfer 2021, Raj 2021); oral biofilm gLV/Allee (Pasqualini 2026, Martin 2017) | Build the hackathon model here |
| **Coupling scaffolds (biology real, math imposed by us)** | periodontal→systemic ε spillover; diabetes↔periodontitis loop-gain instability; Windkessel-under-inflammation; bacteremia→wall deposition; bacteremia→BBB (Kedem–Katchalsky); inflammation→α on tau spread | Present as hypotheses, sweep the parameter, report ranges |
| **Speculative (attractive analogy, weak evidence)** | oral–gut–brain axis; chaos/tipping-point framings; joint tau–neuroinflammation (2026 preprint) | Label hypothesis, never result |

---

## 3. Track — Compartmental ODE / systems-immunology (the spine)

**E2.1 Reduced acute inflammatory response (Reynolds/Vodovotz, 4 ODE).** Pathogen→phagocytes→damage
with slow anti-inflammatory feedback; reproduces resolution vs. runaway vs. persistent as distinct
stable states/bistability. `dP/dt=k_pg P(1−P/p∞)−k_pn f(N*)P; dN*/dt=s_nr R/(μ_nr+R)−μ_n N*; dD/dt=…;
dC_A/dt=…`, `f(V)=V/(1+(C_A/c∞)²)`. Params: BioModels **BIOMD0000000714**. **Strong.** Caveat:
dimensionless, murine-illustrative. *Reynolds et al. 2006, J Theor Biol 242:220.*

**E2.2 Endotoxin cytokine model (Kumar/Chow/Clermont, 8 ODE).** Explicit TNF-α/IL-6/IL-10/NO; global
sensitivity found **IL-6 exposure-integral, not peak TNF, controls cumulative damage**. **Strong.**
Caveat: 42 params → identifiability. *Kumar et al. 2004, J Theor Biol 230:145; sensitivity PMC4125477.*

**E2.3 Human LPS response (Relouw 2024) — the human-scaled kernel.** In-vitro + human endotoxemia; TNF,
IL-6, IL-8, IL-10, cortisol (HPA brake); bolus **and prolonged** LPS → lets the agent test *chronic
low-dose periodontal endotoxemia*. Indirect-response form `dX/dt=k_in·stim·inhib − k_out·X`. **Strong,
human, open (PMC11621538).** Caveat: built for experimental endotoxemia; chronic extrapolation is an
assumption. *Relouw et al. 2024, npj Syst Biol Appl 10:146.*

**E2.4 Periodontitis host–microbe/bone-loss (Fujihara 2023) — the source compartment.** Omics-fitted
ODE; bacteria→TLR→monocyte recruitment is the principal driver of alveolar bone loss; two-species
*P. gingivalis*/commensal biofilm gives the dysbiosis onset. **Medium** (murine, local-only).
*Fujihara et al. 2023, J Dent Res 102(13); biofilm Martin 2017, PLoS ONE 12:e0173153.*

**E2.5 IL-6→hepatic CRP turnover (Pepys) — the transducer & the calibratable edge.** CRP is a
near-linear low-pass integrator of IL-6 (t½≈19 h constant). `dCRP/dt=k_syn·IL6/(EC50+IL6)−k_deg·CRP`,
`k_deg=ln2/19h≈0.0365/h`; spillover edge `IL6_sys += ε·(periodontal load)`. **Calibratable to NHANES
hs-CRP + ΔCRP-after-periodontal-therapy meta-analyses** → invert to bound ε. **Strong kernel / medium
ε.** *Pepys & Hirschfield 2003, JCI 111:1805; therapy dynamics 2025, Front Immunol.*

**E2.6 Systemic inflammation → early atherosclerosis ODE (CV edge).** oxLDL→monocyte→macrophage→foam-
cell positive-feedback loop; chronic IL-6/CRP raises recruitment/oxidation → bistable healthy vs.
plaque. **Medium.** Caveat: MR says **CRP is a marker, IL-6/IL-1 causal** — frame accordingly.
*Ougrinovskaia et al. 2010, Bull Math Biol; review arXiv:1510.01888.*

**E2.7 Neuroinflammation–amyloid–tau cascade (Hao & Friedman 2016) — the neuro node.** Aβ pools, tau,
M1/M2 microglia, astrocytes, TNF, neuron density; explicit inflammatory positive feedback. **Inject
systemic TNF/IL-6 (from E2.3/E2.5) as forcing on M1.** **Medium** (weak identifiability; BBB transfer
simplified). *Hao & Friedman 2016, BMC Syst Biol 10:108.*

**E2.8 Prion-like tau spread — Fisher–KPP on the connectome (the neuro math anchor).**
`∂c/∂t=∇·(D∇c)+α c(1−c)`; network form `dc_i/dt=−κ Σ_j L_ij c_j+α c_i(1−c_i)`, L=connectome
Laplacian. Bayesian ADNI fit: κ≈1.30±0.69 µm/yr, α amyloid-status-dependent (**amyloid gates tau**).
Inflammation enters as α→α(1+β·TNF). **Strong math / speculative inflammation coupling.**
*Fornari et al. 2019, J R Soc Interface 16:20190356; Schäfer et al. 2021, Front Physiol 12:702975.*

**E2.9 Aggregation + network diffusion (Raj AND model) + joint neuroinflammation.** Smoluchowski
size-resolved aggregation coupled to graph-Laplacian transport; recapitulates regional tau-PET. A 2026
preprint jointly couples tau spread with a neuroinflammation field (inflammation↑→spread↑). **Strong
base / speculative joint (unreviewed).** *Raj et al. 2021, Brain Connect 11(8):624.*

**E2.10 Cytokine/CRP PK-PD (TMDD) — the counterfactual lever.** IL-6R blockade (tocilizumab) TMDD +
CRP indirect response: regulatory-grade proof that IL-6→CRP is turnover-kinetic. Lets the agent ask
"if periodontal IL-6 were neutralized, predicted ΔCRP=…". **Strong.** *tocilizumab PK-PD 2011, JPKPD
38:769.*

## 4. Track — Fluid mechanics & transport (the CV and glymphatic axes)

**E1.1 Wall shear stress / CFD → endothelial dysfunction & plaque localization (PILLAR).**
Navier–Stokes; `τ_w=μ(∂u/∂n)|_wall`, `TAWSS`, `OSI=½(1−|∫τ_w|/∫|τ_w|)`, RRT. Atheroprotective
>1.5 Pa, atherogenic <0.4 Pa. Periodontitis enters as an inflammatory shift of the endothelial low-WSS
threshold. Geometry: SimVascular / Vascular Model Repository; validate vs. carotid IMT cohorts.
**Strong.** *Malek/Alper/Izumo 1999, JAMA 282:2035; OSI Ku et al. 1985.*

**E1.2 Glymphatic advection–diffusion clearance of Aβ (PILLAR).** `∂c/∂t+∇·(vc)=∇·(D_eff∇c)−k c`,
`D_eff=D_free/λ²`, Péclet `Pe=vL/D`; aggregating-protein variant uses Smoluchowski kernel. PVS velocity
~15–20 µm/s; α≈0.2, λ≈1.6; AQP4-KO cuts large-solute clearance ~70%. **Strong pathway / medium
advection-vs-diffusion balance (contested).** *Iliff et al. 2012, Sci Transl Med 4:147ra111; Mestre et
al. 2018, Nat Commun 9:4878.*

**E1.3 Sleep-dependent glymphatic modulation.** NREM expands interstitial space ~60% → ~2× faster Aβ
clearance; chronic sleep fragmentation (inflammation-linked) suppresses it. Periodically-forced
clearance ODE. **Strong effect / speculative periodontitis→sleep coupling.** *Xie et al. 2013, Science
342:373.*

**E1.4 Gingival crevicular fluid flow — the periodontal source boundary condition.** `J=dV/dt`;
well-mixed washout `dc/dt=S(t)−(J/V_pocket)c−k_adh c`, turnover τ=V_pocket/J; Starling filtration for
the source. Supplies the bacteremia/mediator flux to E1.6/E2. **Medium** (flow values sparse,
site-variable). *Goodson 2003, Periodontol 2000 31:43; crevice-on-chip Makkar et al. 2023.*

**E1.5 Windkessel arterial mechanics under inflammation.** 2-/3-element: `C dP/dt+P/R=Q(t)`; PWV
(Moens–Korteweg) `√(Eh/2ρr)`; inflammation raises stiffness E → PWV/central pulse pressure. cfPWV
~6–10 m/s. **Medium.** *Westerhof et al. 2009, Med Biol Eng Comput 47:131; NCT01556373.*

**E1.6 Bacteremia transport pocket→circulation.** `dN_blood/dt=Φ_in(t)−k_clear N_blood`, `Φ_in=f·load·
GCF-flux`; transient decay `N(t)=N₀e^(−k_clear t)`. Measured bacteremia 1–300 CFU/mL, <10 min,
~25–38% incidence with brushing/chewing/scaling, higher in periodontitis (tracks BOP, not pocket
depth). **Medium.** *Forner et al. 2006, JCP 33:401; Lockhart et al. 2008, Circulation 117:3118.*

**E1.7 Bacteremia → BBB permeabilization → cerebral entry (oral→neural bridge).** Kedem–Katchalsky
`J_s=P_d ΔC+(1−σ)J_v C̄`, P_d rising with gingipain degradation; feeds the E1.2 clearance PDE as a
source. **Speculative-medium** (biology documented, quantitative model missing). *Dominy et al. 2019,
Sci Adv 5:eaau3333; Zheng et al. 2023, PMC9834243.*

## 5. Track — Control theory & ecological dynamics (metabolic + microbiome)

**E3.1 Bergman glucose–insulin minimal model.** `dG/dt=−(p1+X)G+p1 G_b; dX/dt=−p2 X+p3(I−I_b)`;
S_I=p3/p2, S_G=p1. FSIVGTT/MINMOD; HbA1c the slow integrator to couple periodontitis. **Strong** (the
link to periodontitis is the speculative part). *Bergman et al. 1979, Am J Physiol 236:E667.*

**E3.2 Diabetes↔periodontitis feedback loop (control framing).** Two slow coupled vars P (periodontal)
and H (glycemia) with `S_I(I_sys)=S_I0/(1+β I_sys)`, `I_sys=a·P`; **loop gain L=∂Ṗ/∂H·∂Ḣ/∂P**, L→1 =
saddle-node/tipping. Anchor: periodontal therapy lowers HbA1c ~0.3–0.4 pp → bounds a·β. **Speculative**
(vicious cycle more likely shifts a set-point than makes true instability). *Graves et al. 2026, J Dent
Res; Kotas & Medzhitov 2015, Cell 160:816.*

**E3.3 Blood-pressure regulation (Guyton/baroreflex).** Nested negative feedback: fast baroreflex +
slow renal pressure-natriuresis set-point; inflammation lowers baroreflex sensitivity. **Strong model /
speculative periodontal coupling.** *Guyton et al. 1972; Beard et al. 2013, PMC3886803.*

**E3.4 Inflammation as a control system (acute ODE + alternative-stable-state).** Same Reynolds-class
4-var model read through set-point/gain: weak anti-inflammatory gain or strong damage feedback →
saddle-node into a persistent-inflammation stable state (bistability/hysteresis). Falsifiable: GCF
IL-10/TNF-α below threshold → bistable non-resolving regime. **Medium.** *Kotas & Medzhitov 2015, Cell;
skin bistability PMC10796066.*

**E3.5 Disordered generalized Lotka–Volterra (oral microbiome dysbiosis).** `dN_i/dt=N_i[ρ(K_i−N_i)−
Σ_j α_ij N_j]+N_i η_i+λ`, α_ij random (mean μ/S, var σ²/S); **replicon eigenvalue R→0 = marginal
stability**. Diseased communities sit near R≈0. **Public: NHANES 2009–2012 oral-rinse 16S.** **Medium**
(oral parameterization early; gLV identifiability limited). *Pasqualini et al. 2026, eLife 14:RP105948.*

**E3.6 Two-species biofilm ODE (*P. gingivalis* vs *S. gordonii*).** Reaction–diffusion biomass+damage;
*S. gordonii* toxin raises P. gingivalis damage (inhibitory). Fitted in vitro. **Strong (fitted) /
medium relevance.** *Martin et al. 2017, PLoS ONE 12:e0173153.*

**E3.7 Allee/quorum threshold for *P. gingivalis* persistence (keystone).** `dN/dt=rN(1−N/K)(N/A−1)`;
A=quorum threshold, facilitation by early colonizers lowers A. Fixed points 0/A/K (A unstable = tip).
**Medium-strong.** *npj Syst Biol Appl 2026 s41540-026-00662-x; Hajishengallis et al. 2012, Nat Rev
Microbiol 10:717.*

**E3.8 Alternative-stable-states / tipping framework.** Fold normal form `dx/dt=μ−x²` with μ=
inflammatory/nutrient drive; hysteresis + early-warning signals (rising variance/autocorrelation).
**Medium** (hard to distinguish from cross-sectional data). *Gonze et al. 2017, ISME J 11:2159.*

## 6. Track — Periodontitis ↔ Alzheimer's + Gladstone alignment

**Honest domain verdict:** a biologically plausible, mechanistically well-populated **association** that
has **not** crossed to established causation — and the one direct causal test (gingipain inhibitor
**atuzaginstat/COR388**, GAIN trial) **failed both co-primary endpoints, caused dose-dependent
hepatotoxicity, hit an FDA hold, and the program was abandoned** (Cortexyme→Quince, 2022). Ideal terrain
for a non-diagnostic hypothesis-generating agent.

**E4.1 Oral pathogen brain invasion (*P. gingivalis*/gingipains).** Proposed SIR/logistic load coupled
to pathology `dB/dt=rB(1−B/K)−(δ+u·I)B; d[tau_p]/dt=k_g G(B)−c·tau_p`. **Low–moderate for causation**
(detection replicated; direction unresolved; Dominy COI). *Dominy et al. 2019, Sci Adv 5:eaau3333;
Haditsch et al. 2020, JAD 75:1361.*

**E4.2 Systemic inflammation → neuroinflammation (IL-6/TNF/IL-1β) — the best-supported bridge.** IL-6
disrupts hippocampal BBB; TNF/IL-1β drive microglia→Aβ/tau. Formalizes via E2.7 + E2.8. **Moderate.**
*Ide et al. 2016, PLoS ONE 11:e0151081 (periodontitis→~6× faster ADAS-cog decline).*

**E4.3 Oral–gut–brain axis.** Swallowed pathogens→gut dysbiosis→leaky gut→LPS/metabolite
translocation→neuroinflammation. **Low / speculative** (rich for hypotheses, weak quantitatively).
*Front Aging 2021, 10.3389/fragi.2021.781582.*

**E4.4 Network tau spread modulated by inflammation — the formal anchor (= E2.8/E2.9).** Inflammation
field modulates connectome spread rate; validated tau-spread math, speculative periodontal→α coupling.

**E4.5 Gingipain-inhibition therapeutic test — the negative causal probe (include honestly).**
Atuzaginstat GAIN trial failed; a *P. gingivalis*-positive subgroup showed a company-reported dose-
response (~57% slowing — **press-reported, not peer-reviewed**). Motivates biomarker-stratified
re-analysis, not a causal claim. **High-confidence negative.** *review PMC10275298; Alzforum.*

**E4.6 Epidemiological risk — the data bridge.** Severe periodontitis ~2.9–6.9× dementia/cognitive-
impairment risk (meta-analytic, wide dispersion). **NHANES-III and 2011–2014 carry BOTH periodontal
exams and validated cognitive batteries (CERAD-WL, AFT, DSST)** — the single best open oral↔neuro
linkage. **Moderate association / low causation.** *Noble et al. 2009, JNNP (PMC3073380); meta-analysis
2025 (PMID 40335202).*

**Bridging biomarkers.** Oral: CAL/pocket depth/tooth count, subgingival 16S, anti–P. gingivalis IgG.
Systemic: IL-6, TNF-α, IL-1β, CRP, IL-10, LPS, zonulin. Neuro: plasma p-tau181/217, Aβ42/40, NfL,
GFAP; tau/amyloid-PET; cognitive batteries. Public data: **NHANES** (oral+cognition+hs-CRP), **ADNI**
(tau/amyloid-PET + connectomes for E2.8), UK Biobank (tooth loss + cognition).

**Gladstone alignment (verified).** Their neurodegeneration program centers on exactly the nodes this
library models: **tau** (Mucke — tau downstream of apoE4, network dysfunction independent of plaques),
**APOE4 + human iPSC** (Huang), **neuroinflammation & the blood–brain interface** (Akassoglou —
fibrinogen→BBB-leak→microglia→synapse loss, *the same "peripheral insult→BBB→microglia→cognition"
shape as the periodontitis→brain hypothesis*), and **microglia/innate-immune senescence in tauopathy**
(Gan). A non-diagnostic agent that formalizes the inflammation→tau-spread coupling and proposes
biomarker-stratified oral→neuro experiments offers Gladstone-adjacent labs a **novel upstream
perturbation** to plug into existing tau/microglia/BBB frameworks — generating prioritized experiments,
not clinical claims.

---

## 7. Recommended hackathon centerpiece (wires the pipeline end-to-end)

**One model, two systemic axes, deep-research-grounded, guardrail-safe:**

1. **Source** (E2.4): a periodontal cytokine/LPS source term, magnitude bounded by BOP/pocket strata.
2. **Transducer** (E2.3 → E2.5): human acute-phase → IL-6→CRP turnover; **calibrate ε against NHANES
   hs-CRP + ΔCRP-after-therapy meta-analyses** (this is what makes it a *result*, not a demo).
3. **Fork to both axes from the same IL-6/CRP state:** CV via E2.6/E1.1; **neuro via E2.7 → E2.8**
   (inflammation raises tau-spread α), with **NHANES periodontal+cognitive** data on the neuro side.
4. **Counterfactual lever** (E2.10): simulate IL-6 neutralization → predicted ΔCRP/Δrisk.

Everything sweeps **ε** and the **inflammation→α multiplier** as unknowns, reports **ranges** of
falsifiable predictions, privileges **IL-6/IL-1β as causal / CRP as observable**, and stays strictly
**non-diagnostic**.
