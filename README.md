# Jovian Resonance Lab

**Which minimum dynamical ingredients reproduce the JUP365 Laplace angle of Io, Europa, and
Ganymede?**

[Open the interactive lab](https://lindgreendavid.github.io/jovian-resonance-lab/) ·
[Read the research report](docs/research-report-v0.1.md) ·
[Inspect the frozen protocol](docs/protocol-v0.1.md)

This bounded, reproducible planetary-science project compares four prespecified dynamical models
against 10,957 daily samples from NASA/JPL's JUP365 satellite ephemeris. The protocol was committed
before the full scored interval was extracted or any confirmatory model was run.

## Research status

- Product version: `0.1.0`
- Protocol: [docs/protocol-v0.1.md](docs/protocol-v0.1.md)
- Source audit: [docs/source-audit.md](docs/source-audit.md)
- Scored interval: 2001-01-01 through 2030-12-31 TDB
- Reference: JPL Horizons/JUP365 geometric osculating elements
- Primary endpoint: circular RMSE of `phi_L = lambda_Io - 3 lambda_Europa + 2 lambda_Ganymede`
- Confirmatory result: G4J2 had lower RMSE than K2, G3, and G4
- Important limitation: the nominal 0.01-day thirty-year trace is not numerically converged

## Frozen models and results

| Model | Frozen ingredients | Circular RMSE |
| --- | --- | ---: |
| K2 | independent Jupiter–moon pairs | 103.59° |
| G3 | Jupiter + inner three moons, mutual point masses | 28.21° |
| G4 | G3 + Callisto | 28.32° |
| G4J2 | G4 + Jupiter `J2` | **11.27°** |

The prespecified ordering passed. However, the 0.01-versus-0.005-day G4J2 traces differ by 8.13°
RMSE. Exploratory step halvings reduce successive differences to 2.15° and 0.54°, as expected for
the second-order integrator. The ordering is supported; the nominal model is not a precision
ephemeris. The finest exploratory 0.00125-day run reached 0.464° RMSE against JUP365, a promising
post-confirmatory result that requires a future frozen replication before it can replace the
nominal endpoint.

## Reproduce

Python 3.10–3.13 is supported. Install the development environment, then run:

```bash
python scripts/fetch_reference.py
python scripts/fetch_sensitivities.py
python scripts/run_models.py
python scripts/build_site_data.py
pytest
```

Network retrieval is separated from deterministic model and site generation. Every normalized
reference row, query mapping, source label, retrieval time, and scientific-data hash is preserved
under `data/`.

## Evidence boundaries

The reference ephemeris is a fitted numerical product, not raw observation or error-free truth.
Agreement over thirty years cannot establish formation history, billion-year stability, tidal
parameters, internal heating, subsurface oceans, or habitability. The animation uses real ephemeris
timing and projected directions but intentionally rescales distances and body sizes.

## License

Code and original documentation are MIT licensed. Third-party scientific data retain their source
terms and are documented separately.
