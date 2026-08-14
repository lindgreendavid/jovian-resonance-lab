# Jovian Resonance Lab

**Which minimum dynamical ingredients reproduce the JUP365 Laplace angle of Io, Europa, and
Ganymede—and does that result survive a new interval and a numerical-convergence gate?**

[Open the interactive lab](https://lindgreendavid.github.io/jovian-resonance-lab/) ·
[Read the v1 research report](docs/research-report-v1.0.md) ·
[Inspect the frozen v1 protocol](docs/protocol-v1.0.md) ·
[Audit the release](docs/v1-release-audit.md)

Jovian Resonance Lab is a bounded, reproducible planetary-science study of the Laplace angle

`phi_L = lambda_Io - 3 lambda_Europa + 2 lambda_Ganymede`.

The original v0.1 analysis compared four prespecified dynamical models against 10,957 daily
JUP365 samples from 2001–2030. Its expected model ordering passed, but the nominal 0.01-day trace
failed its numerical sensitivity check. Product v1.0.0 adds a protocol-frozen, non-overlapping
2031–2040 replication with 3,653 new daily samples, a common 0.0025-day model comparison, and a
prespecified convergence gate. All v1 gates passed.

## What this contributes

This project contributes a two-interval, protocol-frozen ablation of the minimum dynamical terms
needed to follow the JUP365 Laplace-angle trace, together with common-step comparisons and explicit
convergence and reference-adequacy gates. It preserves the failed v0.1 sensitivity check instead of
rewriting it. It does **not** infer resonance formation, long-term stability, tidal physics,
habitability, or observational truth from a fitted ephemeris.

## Research status

- Product version: `1.0.0`
- Historical study: [frozen v0.1 protocol](docs/protocol-v0.1.md), unchanged
- v1 validation: [frozen before new retrieval](docs/protocol-v1.0.md)
- Reference: NASA/JPL Horizons, response-reported `JUP365_MERGED`
- Combined public registry: 14,610 daily epochs across two non-overlapping intervals
- Primary endpoint: circular RMSE of the Laplace-angle trace relative to JUP365
- v1 outcome: ordering, convergence, and reference-adequacy gates all passed
- Critical boundary: v1 restarts from a JUP365 state in 2031; it is not a forty-year blind forecast
- Calendar boundary: 2031–2040 values are ephemeris predictions, not future observations

## v1 temporal replication

All four models used the same 0.0025-day internal step over 2031–2040.

| Model | Frozen ingredients | Circular RMSE | Maximum residual |
| --- | --- | ---: | ---: |
| K2 | independent Jupiter–moon pairs | 97.9578° | 179.9717° |
| G3 | Jupiter + inner three moons, mutual point masses | 25.1741° | 36.4787° |
| G4 | G3 + Callisto | 24.7109° | 35.8714° |
| G4J2 | G4 + Jupiter `J2` | **1.0434°** | **1.5298°** |

The prespecified ordering `G4J2 < G4, G3, K2` replicated.

## Frozen numerical gates

| Gate | Result | Threshold | Outcome |
| --- | ---: | ---: | --- |
| G4J2 0.0025 vs 0.00125 day | 0.5735° RMSE | ≤ 0.75° | pass |
| Estimated convergence order | 1.984 | 1.5–2.5 | pass |
| Fine G4J2 vs JUP365 | 0.4699° RMSE | ≤ 1.0° | pass |

The convergence behavior is compatible with the nominal second-order integrator. It does not prove
convergence to exact Solar System dynamics or turn JUP365 into an uncertainty-free truth source.

## Historical v0.1 result

The v0.1 common nominal step was 0.01 day over 2001–2030. Its G4J2 result (11.2678° RMSE) beat the
three frozen alternatives, while the prespecified 0.01-versus-0.005-day sensitivity difference was
8.1342°. Those historical endpoints remain published under their original v0.1 names and are not
overwritten by the v1 replication.

## Reproduce

Python 3.10–3.13 is supported. Network retrieval is deliberately separated from deterministic
analysis:

```bash
python scripts/fetch_reference.py
python scripts/fetch_sensitivities.py
python scripts/run_models.py
python scripts/fetch_validation.py
python scripts/run_validation.py
python scripts/build_site_data.py
python scripts/validate_registry.py
pytest
```

The committed registries allow every deterministic validation step after retrieval to run offline.
Provenance files preserve query maps, response sources, timestamps, row counts, and normalized
scientific-data hashes.

## Evidence boundaries

JUP365 is a fitted and propagated ephemeris, not raw astrometry or a probability distribution.
Agreement over these intervals cannot establish formation history, tidal parameters, internal
heating, subsurface oceans, habitability, or geological-timescale stability. The model omits solar
forcing, higher Jovian harmonics, relativity, tides, and pole precession. The animation uses real
ephemeris timing and projected directions but deliberately rescales distances and body sizes.

## License

Code and original documentation are MIT licensed. Third-party scientific data retain their source
terms and are documented in [the source audit](docs/source-audit.md).
