# Investigation choices

Use reproducible local debugging for deterministic state failures, correlated production logs/traces for remote failures, record/replay for complex temporal state where available, and controlled differential reduction for intermittent subsets. Test a hypothesis by varying one input/state/timing factor and predicting a contrasting outcome; rerunning a failing command alone does not distinguish alternatives.

Keep an evidence table: symptom/expected/observed, source revision/runtime, hypothesis, supporting/counter evidence, discriminating experiment, result and next decision. A ranking may change as observations arrive. Preserve unresolved alternatives rather than label an attractive explanation proven.

Instrumentation belongs at entry/decision/mutation/dependency/error/cleanup boundaries. Use bounded/sanitized logging and restore temporary changes. Profiling and remote telemetry need real tools and permission. Production debug endpoints, flagging, canary traffic or chaos are separate operational actions, not implicit authority from a troubleshooting request.

Validate a repair with the original reproduction, neighboring errors/boundaries, repeated isolation where relevant and comparable performance measurements. Separate primary and cleanup failure, maintain rollback/recovery and proposed prevention. Updated runbooks/alerts/notifications require actual acknowledged writes; suggestions are not completion receipts.
