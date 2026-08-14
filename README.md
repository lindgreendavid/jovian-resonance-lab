# Jovian Resonance Lab

Which dynamical ingredients are needed to reproduce the observed Laplace angle of Io, Europa,
and Ganymede?

This repository is being built as a bounded, reproducible planetary-science research product.
The confirmatory protocol was frozen before the scored JPL interval was downloaded or the model
comparison was run. A two-date feasibility pilot inspected on 2026-08-14 is disclosed in the
protocol and excluded from confirmatory threshold selection.

## Research status

- Product version: `0.1.0a0` (protocol-frozen development build)
- Protocol: [docs/protocol-v0.1.md](docs/protocol-v0.1.md)
- Source audit: [docs/source-audit.md](docs/source-audit.md)
- Scored interval: 2001-01-01 through 2030-12-31 TDB
- Reference: JPL Horizons/JUP365 geometric osculating elements
- Primary endpoint: circular RMSE of the Laplace angle against JUP365

No confirmatory result exists at this commit. The project will report failed expectations and
numerical limitations as directly as successful ones.

## Planned models

1. Independent Jupiter–moon Keplerian pairs.
2. Jupiter plus Io, Europa, and Ganymede with mutual point-mass gravity.
3. Jupiter plus all four Galilean moons with mutual point-mass gravity.
4. The four-moon model plus Jupiter's `J2` oblateness term.

The reference ephemeris is a fitted numerical product, not raw observation or error-free truth.
Agreement over thirty years cannot establish formation history or billion-year stability.

## License

Code and original documentation are MIT licensed. Third-party scientific data retain their source
terms and are documented separately.

