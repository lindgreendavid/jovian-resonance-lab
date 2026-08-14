# v1.0.0 release audit

## Scope and version meaning

Product version 1.0.0 identifies a stable, reproducible research product. It does not retroactively
rename the frozen v0.1 study or imply a precision ephemeris. The original v0.1 protocol, registry,
and confirmatory report remain preserved under their historical filenames.

## Scientific identities

### Frozen v0.1 analysis

- Protocol commit: `7d562ebaaf0be7073d3cfef206803472cbfce5e1`
- Interval: 2001-01-01 through 2030-12-31 TDB
- Daily samples: 10,957
- Normalized SHA-256: `4eda38e1899306a9cfff6d6474748a3c8270dd20d63c72a0df4d0422f427d1fb`

### Frozen v1 validation

- Protocol commit: `b280a9ce6a9d0e7309707b9315d7847739c6e956`
- Interval: 2031-01-01 through 2040-12-31 TDB
- Daily samples: 3,653
- Normalized SHA-256: `2a206cdbcadc31fed1bd17faa1e12c0839996fc7e5d5fc597b829905bd86e766`
- Response-reported source: `JUP365_MERGED`

## Reproduction performed

1. Retrieved the v1 element and vector queries only after the v1 protocol commit.
2. Rejected missing, duplicate, non-daily, misaligned, or non-JUP365 responses.
3. Regenerated all four common-step traces and two additional G4J2 step traces.
4. Recomputed every ordering, convergence, and adequacy gate from the committed registries.
5. Regenerated the public site projection and compared it in the offline registry check.
6. Rechecked lint, formatting, strict typing, coverage, package build, browser behavior,
   accessibility requirements, responsive layout, dependency audit, CI, and CodeQL.

## Gate outcomes

- Common-step ordering: 3/3 passed.
- Medium-to-fine trace RMSE: 0.5735°, below the frozen 0.75° ceiling.
- Estimated convergence order: 1.984, inside the frozen 1.5–2.5 interval.
- Fine G4J2 reference RMSE: 0.4699°, below the frozen 1° ceiling.
- Combined confirmatory v1 outcome: passed.

## Deviations

No scientific endpoint, threshold, model definition, force constant, interval, or expected source
was changed after the v1 protocol freeze. Formatting and release-surface changes do not alter the
machine report. Any later correction must be documented in `docs/post-freeze-corrections.md`.

## Remaining limits

The validation restarts from JUP365 in 2031 and is not a continuous forty-year prediction. JUP365
is a fitted ephemeris, not raw observation or error-free truth. Finite-step agreement does not prove
convergence to exact Solar System dynamics. Solar forcing, higher Jovian gravity harmonics,
relativity, tidal dissipation, and pole precession remain outside the model. No result establishes
formation history, geological heating, ocean properties, habitability, or billion-year stability.
