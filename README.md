# Citizen Property-Tax BACE Survey

A Bayesian Adaptive Choice Experiment (BACE) implementation designed to elicit
citizens' preferences over automated (satellite) vs. human property tax
assessment, and their willingness to bribe an assessor — including whether
that willingness changes when the bill is inflated by assessor error.

Built on top of the [BACE framework](<link to original repo>) developed by
Drake, Payró, Thakral & Tô (2025), *"Bayesian Adaptive Choice Experiments"*.
The underlying adaptive-design engine (Bayesian Optimization for menu
selection, Population Monte Carlo for posterior estimation, the Flask/Lambda
survey backend) is the authors' — this repo documents the survey design,
utility model, and identification work built on top of it for a specific
applied research question.

> **Note:** this implements an active/unpublished research survey. Design
> specifics beyond this summary, raw response data, and infrastructure
> details are intentionally not included here.

## What I designed and implemented

**Utility model.** Replaced the framework's example (pen preferences) with a
choice model over property assessments, where each option is defined by who
assesses the property (human inspector vs. satellite), a signed assessment
error (over- or under-assessment, as a % of liability), and an optional
informal payment ("bribe") that can reduce the recorded bill for a price.
Money enters as the utility numeraire so all preference parameters are
denominated in %-of-liability terms and comparable across respondents with
different tax liabilities.

**Moral-cost decomposition.** Split bribery aversion into two structural
parameters: `m0`, the moral cost of bribing a *correctly* assessed bill (pure
willingness to cheat), and `m1`, how much that cost erodes as over-assessment
increases (a "corrective bribery" motive). This separates "won't cheat a fair
system" from "will pay to correct an unfair one" as distinct, independently
estimable traits, rather than a single conflated bribery-aversion score.

**Identification diagnostics and fix.** Diagnosed, via single-respondent test
runs and a small pilot, that the framework's fully adaptive design under-
sampled the specific comparison needed to identify intrinsic taste for
automation (satellite vs. bribe-free human, at matched cost) — most adaptive
menus instead pitted a clean satellite against a *bribing* human, entangling
the automation-preference parameter with the moral-cost parameters. Designed
and verified (via direct likelihood simulation) a set of fixed "seed"
screens served before the adaptive phase, each constructed so that two of
the three structural terms in the choice utility cancel algebraically,
isolating one target parameter per screen.

**Design constraints.** Added domain constraints to prevent the optimizer
from wasting evaluations on structurally dominated or incoherent menus (e.g.
a bribe offered on an option where no assessor can be bribed).

**Respondent-facing display logic.** Implemented rounding of on-screen
rupee amounts to the nearest 100 for display, while keeping the underlying
continuous design values used for estimation untouched — with derived
totals (e.g. bribe + reduced bill) computed from the already-rounded
components so every number a respondent sees is internally consistent.

**Field validation.** Iteratively validated the design end-to-end: verified
the likelihood function reproduces the on-screen numbers exactly, confirmed
each seed screen's isolation property numerically, and used pilot data to
recalibrate priors before full fielding. Also diagnosed a parameter-
interpretation bug in a downstream analysis pipeline, where a moral-cost
*erosion* coefficient was being read as a stand-alone *level*, producing an
internally inconsistent conclusion about respondent behavior.

## Original framework

- Paper: Drake, Payró, Thakral & Tô (2025), *Bayesian Adaptive Choice Experiments*
- Original repository: `<link>`

## License

`<fill in based on the original repo's license>`
