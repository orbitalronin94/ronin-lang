# CES-Saturated family — mathematical appendix (English companion)

This is an English companion summary of [the complete Spanish mathematical appendix](family.md).

The family combines a weighted CES power mean with a Hill saturation transform: Omega_sat = Omega^alpha_h / (K^alpha_h + Omega^alpha_h). Its parameters include CES curvature lambda, Hill scale K, Hill exponent alpha_h and aggregation weights. The appendix discusses limiting cases, the interpretation of sigma, the K–alpha degeneracy at low Omega/K, practical identifiability and recommended model families by domain.

The source document has an editorial inconsistency: the opening normative declaration gives the geometric-mean limit as lambda approaches zero for CES, while N.2.3 says CES at lambda=1e-7 should recover PUSFRE. These are not generally equivalent. The Python implementation follows the geometric-mean CES limit; the inconsistency is explicitly documented for a future normative decision.
