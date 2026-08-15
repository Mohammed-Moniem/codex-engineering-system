# Prototype branches

| Branch | Smallest useful evidence |
| --- | --- |
| UI | Clickable mock or isolated component with target states |
| STATE | Transition model covering success, failure, retry, and cancellation |
| ALGORITHM | Executable sample with correctness cases and complexity measurement |
| API | Minimal contract, request/response examples, and compatibility probe |
| DATA-MODEL | Representative schema and query/migration checks |
| INTEGRATION | Sandbox or fake-backed handshake proving boundary assumptions |
| AI-LLM | Versioned prompt/model fixture with a scored representative set |
| PERFORMANCE | Repeatable benchmark with baseline, budget, and variance |
| MIGRATION | Dry-run slice with rollback and data-integrity checks |

Use production-like inputs only when they are synthetic or safely redacted. Record exact versions and commands. A prototype should answer one question; split independent hypotheses rather than accumulating a miniature product.
