# Research report v1.0 — temporal replication and numerical convergence

## Abstract

The v0.1 model-ablation study found that a model containing the four Galilean moons and Jupiter's
`J2` (G4J2) best reproduced the Io–Europa–Ganymede Laplace angle within a prespecified four-model
family, but its nominal thirty-year trajectory was not numerically converged. We therefore froze a
second protocol before retrieving a non-overlapping JUP365 interval. Across 3,653 daily samples from
2031-01-01 through 2040-12-31 TDB, all four models were run at a common 0.0025-day step. G4J2 again
had the lowest circular RMSE: 1.0434°, compared with 24.7109° for G4, 25.1741° for G3, and 97.9578°
for K2. Additional G4J2 runs at 0.005 and 0.00125 day passed both frozen convergence gates: the
medium-to-fine trace difference was 0.5735° and the estimated order was 1.984. The finest trace had
0.4699° RMSE relative to JUP365, passing the prespecified 1° adequacy gate. The model ordering and
numerical behavior therefore replicated under this protocol. The result is conditional on the
tested model family and a new JUP365 initial state at the validation boundary; it is not an
uninterrupted forty-year prediction or a claim that omitted physics is generally negligible.

## Design and provenance

The v1 protocol was frozen at commit `b280a9ce6a9d0e7309707b9315d7847739c6e956` before any
2031–2040 retrieval or v1 model execution. The validation registry contains 3,653 aligned daily
epochs and has normalized SHA-256
`2a206cdbcadc31fed1bd17faa1e12c0839996fc7e5d5fc597b829905bd86e766`. Every Horizons response
identified the source as `JUP365_MERGED`.

The model is initialized from geometric, Jovicentric ICRF/J2000 JUP365 vectors at 2031-01-01 TDB.
Reference Laplace angles are derived from JUP365 body-equator-of-date osculating elements. Force
definitions, constants, coordinate conversion, and the velocity-Verlet implementation are
unchanged from v0.1. This design tests a new ten-year propagation from a new reference initial
state. It does not test error accumulated continuously from 2001. Because the interval extends
beyond the 2026 release date, its reference values are JUP365 predictions, not future observations.

## Confirmatory results

At the common 0.0025-day internal step, the frozen model-ordering gate passed in all three
comparisons.

| Model | Circular RMSE | Maximum absolute residual |
| --- | ---: | ---: |
| K2 | 97.9578° | 179.9717° |
| G3 | 25.1741° | 36.4787° |
| G4 | 24.7109° | 35.8714° |
| G4J2 | **1.0434°** | **1.5298°** |

The comparison supports the importance of mutual satellite gravity plus Jovian oblateness for
preserving this phase relation within the tested family. G4's small advantage over G3 in this
interval was not a prespecified contrast and does not establish a general ranking of Callisto's
importance.

## Numerical convergence and reference adequacy

| Comparison or endpoint | Result | Frozen gate | Outcome |
| --- | ---: | ---: | --- |
| G4J2 0.005 vs 0.0025 day | 2.2687° RMSE | descriptive | — |
| G4J2 0.0025 vs 0.00125 day | 0.5735° RMSE | ≤ 0.75° | pass |
| Estimated convergence order | 1.984 | 1.5–2.5 | pass |
| Fine G4J2 vs JUP365 | 0.4699° RMSE | ≤ 1.0° | pass |

The finest trace's maximum absolute JUP365 residual was 0.6812°. Its annual circular RMSE ranged
from approximately 0.213° to 0.620°. These annual summaries are deterministic diagnostics, not
independent statistical samples or confidence intervals.

The observed factor-of-four reduction in successive trace differences is compatible with the
nominal second-order integrator. Passing a finite-step convergence test does not prove convergence
to the exact dynamics, and agreement with JUP365 does not provide an uncertainty estimate for that
ephemeris.

## Reference behavior and diagnostics

The validation JUP365 Laplace angle had circular mean 179.9884°, half peak-to-peak range 0.3879°,
and remained within 2° of 180° at every daily epoch. Point-mass relative energy drift was
`−5.10 × 10⁻8` for G3 and `−4.25 × 10⁻8` for G4. Interacting-model barycenter displacement stayed
below `5 × 10⁻8` km. K2's fixed-Jupiter construction is not expected to conserve the barycenter of
the represented Jupiter-plus-moons collection and is not interpreted as a comparable diagnostic.

## Relation to published evidence

Paita, Celletti, and Pucacco (2018) reported that mutual Galilean-moon interactions plus Jupiter's
`J2` approximate the Laplace argument over their tested century. The replicated model ordering is
consistent with that result, but it is not an independent astrometric measurement because the
initial state and comparison trajectory both derive from JUP365.

Lainey et al. (2009) inferred secular accelerations and evolution away from exact Laplace resonance,
while Lari, Saillenfest, and Fenucci (2020) showed that uncertain tidal evolution can influence
future resonant behavior involving Callisto. Those studies address dynamics absent here. This
project cannot determine resonance origin, age, geological heating, ocean state, habitability, or
geological-timescale survival.

## Reproducibility

The historical v0.1 protocol, registry, and report remain byte-distinct and unchanged in meaning.
The v1 reference registry, initial states, provenance, complete daily traces, gate outcomes, annual
diagnostics, and site projection are committed as machine-readable JSON. Network retrieval is
separated from deterministic integration and validation. The offline registry check verifies
sample identities, source labels, hashes, protocol identity, step gates, ordering gates, and the
generated public projection.

## Primary sources

- NASA/JPL, Planetary Satellite Ephemerides: https://ssd.jpl.nasa.gov/sats/ephem/
- NASA/JPL, Horizons API documentation: https://ssd-api.jpl.nasa.gov/doc/horizons.html
- Paita, F., Celletti, A., & Pucacco, G. (2018), *A&A* 617, A35:
  https://doi.org/10.1051/0004-6361/201832856
- Lainey, V. et al. (2009), *Nature* 459, 957–959:
  https://doi.org/10.1038/nature08108
- Lari, G., Saillenfest, M., & Fenucci, M. (2020), *A&A* 639, A40:
  https://doi.org/10.1051/0004-6361/202037445
