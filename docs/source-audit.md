# Source audit

## Reference ephemeris

JPL's planetary-satellite ephemeris table identifies JUP365 as the current ephemeris for Io,
Europa, Ganymede, and Callisto. It covers 1600-01-10 through 2200-01-10 and is served through
Horizons. The full binary kernel is about 1.1 GB, so this project will preserve normalized,
query-specific extracts and their hashes rather than copy the full kernel into Git.

- JPL satellite ephemerides: https://ssd.jpl.nasa.gov/sats/ephem/
- Horizons API: https://ssd-api.jpl.nasa.gov/doc/horizons.html
- Horizons manual: https://ssd.jpl.nasa.gov/horizons/manual.html

## Dynamical claim being tested

Paita, Celletti, and Pucacco modelled the Laplace argument over 100 years. Their Cartesian result
states that mutual interactions among Jupiter and the Galilean moons, including Callisto, plus
Jupiter's `J2` provide a sufficient approximation on that interval. Our implementation is an
independent, shorter model-ablation study with a different release pipeline.

- Paita, F., Celletti, A., & Pucacco, G. (2018), A&A 617, A35.
  https://doi.org/10.1051/0004-6361/201832856

## Competing and limiting evidence

The resonance is not an immutable exact integer clock. Lainey et al. inferred secular accelerations
from astrometry and reported evolution away from the exact Laplace resonance. Long-term simulations
also depend on uncertain tidal evolution and possible future resonance with Callisto. These results
prevent any thirty-year fit from being presented as proof of eternal stability.

- Lainey, V. et al. (2009), Nature 459, 957–959.
  https://doi.org/10.1038/nature08108
- Lari, G., Saillenfest, M., & Fenucci, M. (2020), A&A 639, A40.
  https://doi.org/10.1051/0004-6361/202037445

Peale and Lee showed that primordial differential migration can generate the Laplace relation and
contrasted it with later tidal-torque capture. The present project cannot adjudicate between origin
scenarios.

- Peale, S. J., & Lee, M. H. (2002), Science 298, 593–597.
  https://doi.org/10.1126/science.1076557

## Constants

Gravitational parameters are taken from JPL's maintained Horizons PCK and recorded verbatim in the
data manifest used for the scored run. Jupiter's reference radius is 71,492 km. The `J2` coefficient
and reference radius used by the model will be pinned to a named, peer-reviewed Juno gravity product
before the scored integration begins.

- JPL Horizons GM kernel: https://ssd.jpl.nasa.gov/ftp/xfr/gm_Horizons.pck
- Juno derived gravity archive: https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=JNO-J-RSS-5-JUGR-V1.0
- JPL planetary physical parameters: https://ssd.jpl.nasa.gov/planets/phys_par.html

