# RONIN 1.1 normative annex — English summary

See the complete Spanish source transcription in [`normative-annex.md`](normative-annex.md).

The annex defines an evaluation order: parse; validate types, ranges, agent count and normalized frequencies; validate model/parameter coherence; apply Hill saturation and CES combination; allocate resources; calculate coexistence and debt; diagnose Ω range and degeneracy; then return a solution with warnings. A zero total fitness must fail safely.

It specifies seven normative tests covering 1.0 compatibility, explicit PUSFRE, near-zero CES lambda, model coherence, active/inactive degeneracy, and Neural Scaling diagnostics. Conformance requires identifiable errors, numerical tolerances, allocation conservation, seeded simulation, coherent degeneracy reporting, and no unverified benchmark claims.

The source explicitly distinguishes specification from implementation and marks Rust, WASM, C, and Office extensions as specified or proposed rather than fully delivered. It also contains a CES-limit compatibility statement that must be read alongside the mathematical appendix and the repository’s documented discrepancy.
