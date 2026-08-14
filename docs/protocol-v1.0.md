# Frozen protocol v1.0 — temporal replication and numerical convergence

**Protocol state:** frozen before retrieval of the 2031–2040 reference extract and before any
v1 model execution  
**Freeze date:** 2026-08-14  
**Prior evidence:** the disclosed v0.1 study and its post-confirmatory convergence extension  
**Product target:** 1.0.0

## 1. Question

Does the v0.1 conclusion—that mutual Galilean-satellite gravity plus Jupiter's `J2` best preserves
the Io–Europa–Ganymede Laplace angle within the tested model family—replicate on a non-overlapping
JUP365 interval when every model is evaluated at a common, finer step and the preferred model must
also pass a prespecified numerical-convergence gate?

This is a temporal replication of model adequacy relative to a fitted ephemeris. It is not a test
of the origin, geological consequences, or long-term survival of the resonance.

## 2. Separation from prior analysis

The v0.1 scored interval (2001-01-01 through 2030-12-31 TDB), model results, and exploratory step
halvings are known. They informed the thresholds below and remain unchanged. No 2031–2040 element
or vector response may be retrieved, inspected, or used by the v1 pipeline until this document is
committed.

The new integration is initialized from JUP365 at 2031-01-01. It therefore tests transport across
the subsequent ten-year interval, conditional on a new ephemeris initial state; it is not an
uninterrupted forty-year forecast from the 2001 state.

## 3. Reference and interval

- Source system: NASA/JPL Horizons API.
- Required response-reported satellite ephemeris: JUP365.
- Targets: Io 501, Europa 502, Ganymede 503, Callisto 504.
- Center: Jupiter body center 599.
- Timescale: TDB.
- Element frame: Jupiter body equator and node of date.
- Validation interval: 2031-01-01 00:00 through 2040-12-31 00:00 TDB, inclusive.
- Cadence: one day; expected sample count: 3,653.
- Initial vectors: 2031-01-01 00:00 TDB, geometric ICRF/J2000, Jupiter-centered, km and km/day.

The retrieval must retain the normalized query maps, retrieval time, response source, row count,
and SHA-256 of the numeric registry. Missing, duplicate, non-daily, or misaligned epochs stop the
analysis.

## 4. Models and numerical method

The K2, G3, G4, and G4J2 force definitions, constants, coordinate conversions, circular residual,
and velocity-Verlet implementation are unchanged from the frozen v0.1 protocol.

All four models are run at a common internal step of `0.0025` day. G4J2 is additionally run at
`0.005` and `0.00125` day. Daily outputs are aligned exactly with the reference epochs. No force,
constant, initial-state adjustment, phase correction, interpolation, or tolerance is fitted to the
validation interval.

## 5. Confirmatory endpoints and gates

### 5.1 Temporal replication

At the common `0.0025`-day step, circular RMSE relative to JUP365 must satisfy all three comparisons:

`G4J2 < G4`, `G4J2 < G3`, and `G4J2 < K2`.

The exact RMSE and maximum absolute circular residual are reported for every model regardless of
outcome. The comparison is restricted to this model family, endpoint, source, and interval.

### 5.2 Numerical convergence

Let `D(h1, h2)` be circular RMSE between the two daily G4J2 traces. The convergence gate passes only
if both conditions hold:

1. `D(0.0025, 0.00125) <= 0.75°`.
2. `1.5 <= log2[D(0.005, 0.0025) / D(0.0025, 0.00125)] <= 2.5`.

The first threshold is a practical trace-agreement bound selected before validation; the second
requires behavior compatible with the nominal second-order method without treating the estimated
order as an exact theorem for this nonlinear observable.

### 5.3 Reference adequacy

The `0.00125`-day G4J2 trace passes the prespecified reference-adequacy gate if its circular RMSE
against JUP365 is at most `1.0°`. This threshold is informed by the disclosed v0.1 exploratory
result (`0.4641°`) and is therefore a replication criterion, not a discovery threshold or an
ephemeris-uncertainty statement.

The v1 research conclusion is called *replicated and numerically adequate under this protocol*
only if the ordering, convergence, and reference-adequacy gates all pass. Partial failures are
published without changing the thresholds.

## 6. Descriptive diagnostics

- JUP365 circular mean, unwrapped range, and fraction within 2° of 180°;
- maximum residual for each common-step model;
- coarse/medium/fine G4J2 trace differences and estimated convergence order;
- model RMSE with the final epoch excluded;
- point-mass energy drift and barycenter drift where physically applicable;
- annual circular RMSE for the finest G4J2 trace to expose temporal concentration of error.

Annual values are descriptive and do not create additional pass/fail tests. No confidence interval
is attached to deterministic ephemeris samples as though they were independent random draws.

## 7. Failure and amendment rules

- A source other than JUP365, a changed scientific-data identity, or an incomplete registry stops
  the run and requires a dated amendment before analysis.
- A non-finite state, element-conversion failure, or inconsistent output length stops that model.
- The implementation and artifact schemas may be corrected after freeze only with a public note
  that states whether any endpoint changed.
- Failed gates remain visible. They may not be replaced by a more favorable interval, step, metric,
  frame, or threshold.

## 8. Interpretation boundary

JUP365 is a fitted numerical ephemeris rather than raw astrometry or error-free truth. A ten-year
replication initialized from JUP365 cannot establish causal formation, tidal parameters, internal
heating, subsurface oceans, habitability, or stability on geological timescales. Agreement also
does not show that omitted solar forcing, higher gravity harmonics, relativity, tides, or pole
precession are generally negligible.

## 9. Required v1 artifacts

- immutable v0.1 protocol, registries, reports, and terminology;
- normalized v1 reference and initial-state registries with provenance;
- deterministic v1 model and validation report;
- v1 research report and release audit with exact commit identity;
- interactive convergence and holdout views with accessible non-canvas summaries;
- synchronized README, citation, changelog, package metadata, website, and release notes;
- green lint, formatting, typing, coverage, build, registry, accessibility, responsive, security,
  CI, CodeQL, and live-link checks.
