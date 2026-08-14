# Post-freeze corrections

## 2026-08-14 — report timestamp serialization

The first complete model execution reached all numerical endpoints but stopped before writing the
report. The serializer attempted to read `jd_tdb` from the derived list of reference angles rather
than from the unchanged reference-row registry. The one-line correction changes that input to the
reference-row registry.

This correction affects only serialization of the already frozen epoch axis. It does not alter a
query, state, force, integration step, model trace, endpoint, expectation, or interpretation.

## 2026-08-14 — daily mean-longitude alias disclosure

The frozen daily cadence undersamples Io's approximately 1.77-day orbit: its principal wrapped
increment is negative even though the physical orbit is prograde. The report therefore retains the
principal daily alias and adds a separately labelled prograde-resolved estimate by summing positive
modulo-360 daily increments. Both forms are descriptive. No primary model metric depends on this
clarification.

## 2026-08-14 — exploratory convergence extension

The prespecified 0.01-versus-0.005-day G4J2 comparison was not numerically close over thirty years.
Two smaller steps (0.0025 and 0.00125 day) were therefore added after confirmation solely to show
the convergence trend. They are marked exploratory and do not replace the frozen 0.01-day primary
endpoint or its confirmatory ordering.
