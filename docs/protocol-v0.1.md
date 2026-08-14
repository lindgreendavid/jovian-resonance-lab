# Frozen protocol v0.1 — Jovian Laplace-angle model adequacy

**Protocol state:** frozen before confirmatory data extraction and model evaluation  
**Freeze date:** 2026-08-14  
**Product status at freeze:** 0.1.0a0  

## 1. Question

Over a prespecified thirty-year interval, which of four increasingly complete dynamical models
best reproduces the JPL JUP365 Laplace angle

`phi_L = lambda_Io - 3 lambda_Europa + 2 lambda_Ganymede`,

where each mean longitude is `lambda = Omega + omega + M` and angular differences are evaluated
circularly?

The experiment evaluates model adequacy relative to a reference ephemeris. It does not estimate
the age, origin, or long-term survival probability of the resonance.

## 2. Prior inspection and separation from confirmation

Before this protocol was frozen, a feasibility pilot queried JPL Horizons for geometric,
Jovicentric, body-equator-of-date osculating elements on 2000-01-01 and 2000-01-02 TDB. The derived
Laplace angles were approximately 180.108 and 180.229 degrees. Those dates established only that
the source and coordinate definitions were operational. They are excluded from the scored interval
and were not used to tune model parameters or numerical tolerances.

The published Paita, Celletti, and Pucacco (2018) result—mutual Galilean-satellite interactions plus
Jupiter's `J2` approximate the Laplace argument over a century—is known before analysis and is the
target of a shorter, independently implemented model-ablation study. This is not a blind discovery
study.

## 3. Reference source and interval

- Source system: NASA/JPL Horizons API.
- Satellite ephemeris reported by the response: JUP365.
- Targets: Io 501, Europa 502, Ganymede 503, Callisto 504.
- Center: Jupiter body center 599.
- Timescale: TDB.
- Reference plane for elements: Jupiter body equator and node of date.
- Scored interval: 2001-01-01 00:00 through 2030-12-31 00:00 TDB, inclusive.
- Scored cadence: one day.
- Initial Cartesian states: 2001-01-01 00:00 TDB, geometric vectors in ICRF/J2000,
  centered on Jupiter, in km and km/day.

The extraction script must record the complete normalized query specification, response-reported
source, retrieval timestamp, row count, and SHA-256 of normalized numeric rows. Raw response headers
that vary between calls are not part of the scientific identity.

## 4. Fixed dynamical models

All models begin from the same JUP365 state epoch. Jupiter and included moons are shifted into their
common barycentric frame before integration. Published JPL gravitational parameters are used as
`GM`; `G` and masses are never separately estimated.

- **K2:** each of Io, Europa, and Ganymede follows an independent two-body orbit about a fixed
  Jupiter. No moon–moon forces and no oblateness.
- **G3:** Jupiter, Io, Europa, and Ganymede interact as point masses.
- **G4:** G3 plus Callisto as a fully interacting point mass.
- **G4J2:** G4 plus Jupiter's axisymmetric `J2` acceleration using the documented equatorial radius.

No solar perturbation, higher Jovian gravity harmonic, relativistic correction, tidal dissipation,
or pole-precession model will be added after results are seen. Their omission is a declared model
boundary, not evidence that they are physically irrelevant.

## 5. Numerical method

- Integrator: independently implemented velocity Verlet/leapfrog in double precision.
- Nominal internal step: 0.01 day.
- Output cadence: one day, aligned exactly with reference epochs.
- Coordinates: barycentric Cartesian ICRF/J2000 for integration.
- Osculating elements: derived relative to the instantaneous Jupiter state with the corresponding
  Jupiter-plus-moon two-body `GM`.
- Angular residual: wrapped to `[-180, 180)` degrees.

The implementation must test two-body closure, barycenter conservation, time reversibility over a
short interval, circular-angle wrapping, element reconstruction, and the sign and symmetry of the
`J2` acceleration.

## 6. Endpoints and expectations

### Primary endpoint

For each model, circular root-mean-square error of daily `phi_L` relative to JUP365 over the scored
interval, in degrees.

### Confirmatory ordering

The prespecified expectation is:

`RMSE(G4J2) < RMSE(G4)`, `RMSE(G4J2) < RMSE(G3)`, and `RMSE(G4J2) < RMSE(K2)`.

Every comparison is reported even if the ordering fails. No universal solver or dynamical-model
ranking follows from this one system and interval.

### Secondary descriptive endpoints

- circular mean of the JUP365 Laplace angle;
- unwrapped minimum, maximum, and half peak-to-peak range;
- fraction of daily reference samples within 2 degrees of 180 degrees;
- maximum absolute angular residual per model;
- initial and final total-energy drift for point-mass models;
- initial and final barycenter displacement and velocity drift;
- pairwise mean-motion combinations estimated from unwrapped mean longitudes.

The 2-degree band is a broad descriptive containment check, not an uncertainty interval or a formal
definition of resonance.

## 7. Frozen sensitivity analyses

1. Repeat G4J2 with a 0.005-day internal step and compare its daily Laplace-angle trace with the
   nominal run.
2. Query a fixed 30-day segment beginning 2011-01-01 at 12-hour cadence and confirm that daily
   sampling does not conceal a circulation event in that segment.
3. Recalculate the reference angle in the ICRF/J2000 element frame for the same 30-day segment and
   describe frame sensitivity; it is not substituted into the primary endpoint.
4. Report results both including and excluding the final calendar day to expose endpoint handling.

## 8. Missingness and failure rules

- Any missing or duplicate reference epoch stops the confirmatory run.
- Any source label other than JUP365 is reported and requires a new dated protocol amendment before
  analysis continues.
- Non-finite state, failed element conversion, or barycenter drift above the implementation's tested
  numerical envelope stops that model; it is not silently dropped.
- A post-freeze code correction must be documented with its effect on results and must not change an
  expectation simply because it failed.

## 9. Interpretation boundary

JUP365 is a fitted and propagated ephemeris, not raw astrometry and not a probability distribution.
The experiment cannot establish causal formation, geological heating, ocean habitability, tidal
quality factors, or stability outside 2001–2030. An animation may exaggerate radii and rescale
orbital distances only when the active scale is visibly labelled. It must never show a synthetic
model as measured reality.

## 10. Required release artifacts

- normalized reference registry and provenance manifest;
- machine-readable model report;
- deterministic comparison script;
- methods and research report;
- source and release audits;
- interactive site with reference/model distinction, reduced-motion support, keyboard controls,
  and a non-animated data table;
- CI, CodeQL, dependency/security checks, responsive tests, and accessibility tests.

