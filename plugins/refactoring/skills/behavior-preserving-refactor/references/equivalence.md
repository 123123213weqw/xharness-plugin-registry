# Refactor equivalence boundaries

Characterize return values, exception type/message/cause where contractual, observable mutation/aliasing, lazy iterator consumption, IO ordering/count, resource release and concurrency/cancellation before transformation. Monetary rounding, text encoding and nondeterministic ordering can change without obvious happy-path failures.

Use unchanged tests, independent caller cases and finite representative properties/inputs before and after. Where safe, execute old/new implementations in separate disposable processes with identical data and compare structured results/effects. Preserve test/source hashes and explicit environment; do not import candidate code into a trusted oracle parent. Differential tests establish the sampled domain, not arbitrary equivalence.

Metrics and static tools help identify hotspots but are not behavioral proof. Avoid universal source example20-line/80%-coverage quotas. Evaluate meaningful abstraction and SOLID boundaries pragmatically: patterns solve actual variation/coupling, not a required checklist. Treat API/error/data-format changes as migrations with explicit approval, adapters, deprecation and rollback, not undocumented cleanup.
