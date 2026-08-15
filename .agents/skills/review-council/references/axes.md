# Review axes

Always use `SPEC` and `CODE-STANDARDS`.

Add an axis when the diff crosses its trigger:

| Axis | Trigger examples |
| --- | --- |
| ARCHITECTURE | New boundary, dependency direction, shared abstraction, schema ownership |
| TESTING | Changed behavior without clear coverage, flake risk, weak seams |
| SECURITY | Authentication, authorization, secrets, parsing, filesystem, process, network, dependencies |
| PERFORMANCE | Hot path, algorithmic complexity, large data, concurrency, caching |
| OPERABILITY | Deployment, migration, feature flag, telemetry, alerting, rollback |

Axes are independent perspectives, not necessarily separate agents. Parallelize only when scope and available context make the passes genuinely independent.

Severity reflects user or system impact, not reviewer confidence. State confidence separately in the finding evidence when uncertain.
