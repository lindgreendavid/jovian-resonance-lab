# Research report v0.1 — Jovian Laplace-angle model adequacy

## Abstract

This preregistered model-ablation study asks which minimum dynamical ingredients reproduce the
Io–Europa–Ganymede Laplace angle relative to NASA/JPL JUP365 from 2001-01-01 through 2030-12-31 TDB.
Four independently implemented models began from the same ephemeris state. The model including all
four Galilean moons and Jupiter's `J2` (G4J2) had lower circular RMSE than each prespecified
alternative: 11.27° versus 28.32° (G4), 28.21° (G3), and 103.59° (K2). All three confirmatory
comparisons passed. A prespecified step-size test exposed substantial long-horizon numerical error:
the 0.01- and 0.005-day G4J2 traces differed by 8.13° RMSE. Post-confirmatory halvings reduced the
successive discrepancies to 2.15° and 0.54°, consistent with second-order convergence. The study
supports the comparative importance of mutual satellite gravity plus Jovian oblateness within this
model family; it does not establish a precision ephemeris, formation history, or long-term
stability.

## Design and provenance

The protocol was frozen at commit `7d562ebaaf0be7073d3cfef206803472cbfce5e1` before full scored
extraction. A disclosed two-date pilot from 2000 is outside the scored interval. Horizons identified
every scored response as `JUP365_MERGED`. The aligned daily registry contains 10,957 epochs and has
normalized SHA-256 `4eda38e1899306a9cfff6d6474748a3c8270dd20d63c72a0df4d0422f427d1fb`.

JUP365 body-equator-of-date osculating elements define the reference angle. Initial geometric
Cartesian vectors are Jovicentric ICRF/J2000. The models use published JPL gravitational parameters,
Jupiter `J2 = 0.0146965735`, reference radius 71,492 km, and a fixed IAU J2000 pole. Velocity Verlet
uses a nominal 0.01-day internal step and exact daily output.

## Results

The JUP365 circular mean was 180.0036°. Every daily sample was within 2° of 180°, and the unwrapped
reference half peak-to-peak range was 0.4169°. These values describe this ephemeris and interval;
the ±2° band is neither a confidence interval nor a definition of resonance.

| Model | Circular RMSE | Maximum absolute residual |
| --- | ---: | ---: |
| K2 | 103.5936° | 179.9917° |
| G3 | 28.2122° | 45.8739° |
| G4 | 28.3195° | 46.4336° |
| G4J2 | 11.2678° | 16.8662° |

The frozen expectation `G4J2 < K2, G3, G4` passed in every comparison. Callisto alone did not improve
the primary metric relative to G3. This is a model- and endpoint-specific result, not evidence that
Callisto is dynamically irrelevant.

Point-mass energy drift was `−2.57 × 10^-7` for G3 and `−9.72 × 10^-9` for G4. Interacting-model
barycenter displacement remained below `6 × 10^-8` km. K2's fixed Jupiter construction does not
conserve the barycenter of the represented Jupiter-plus-moons collection and is not interpreted as
a comparable conservation diagnostic.

## Sensitivity and numerical adequacy

The prespecified G4J2 step-size difference was too large to call the nominal thirty-year trace
converged. Exploratory halvings showed the expected approximately fourfold reduction for a
second-order method:

| Trace comparison | Circular RMSE |
| --- | ---: |
| 0.01 vs 0.005 day | 8.1342° |
| 0.005 vs 0.0025 day | 2.1487° |
| 0.0025 vs 0.00125 day | 0.5417° |

Against JUP365 itself, the exploratory 0.005-, 0.0025-, and 0.00125-day G4J2 runs had circular RMSE
of 3.1519°, 1.0054°, and 0.4641°, respectively. This convergence is encouraging and makes numerical
phase error the likely explanation for much of the nominal 11.27° discrepancy. Because these
additional steps were chosen after observing the frozen sensitivity failure, they remain
exploratory and require a new frozen replication before becoming a confirmatory endpoint.

The 2011 frozen 12-hour reference segment ranged only 0.2273° and contained no circulation; its
largest adjacent increment was 0.0840°. Re-expressing that segment in the ICRF/J2000 element frame
changed the angle by 0.2019° RMS and at most 0.2037°. Frame choice is small relative to model RMSE
but not negligible relative to the reference libration range.

Daily sampling aliases Io's prograde mean-longitude increment to a negative principal value. The
machine-readable report therefore retains that alias and separately labels the prograde-resolved
modulo-360 estimate. This descriptive clarification does not affect the primary angle residual.

## Interpretation

Within this frozen comparison, mutual satellite gravity is necessary to preserve much of the
three-body phase relationship, and including Jupiter's oblateness materially improves it. The
result is consistent with Paita, Celletti, and Pucacco (2018), but it is not an independent
astrometric measurement: both the initial state and reference come from a fitted JPL ephemeris.

Lainey et al. (2009) inferred secular evolution in the Galilean system, while Lari, Saillenfest, and
Fenucci (2020) showed that uncertain tidal evolution can shape later resonant behavior involving
Callisto. Peale and Lee (2002) studied a possible primordial migration origin. Those works constrain
what this thirty-year experiment cannot claim: no result here determines resonance age, origin,
future survival, tidal dissipation, heating, ocean state, or habitability.

## Reproducibility record

The exact reference, initial states, query mappings, hashes, model traces, endpoint calculations,
and sensitivity traces are committed as JSON. Source code has no numerical-analysis dependency;
tests cover circular arithmetic, parser failure modes, element conversion, force modes,
barycentering, energy, integration output, and the command interface. Post-freeze corrections and
extensions are listed in `docs/post-freeze-corrections.md`.
