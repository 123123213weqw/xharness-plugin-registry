---
name: api-regression
description: "Build reproducible positive, boundary and failure API tests using the project actual client and contract."
---

# Api Regression

Read [the regression guide](../api-contract/references/workflow.md), existing tests and the real OpenAPI specification. Use the project's installed test runner or client; assert status, typed body, expected side effects and error behavior, rather than only HTTP 200. Exercise a valid request, missing/invalid inputs, auth failure where a dedicated fixture exists, and a bounded timeout. Keep all writes and cleanup in an authorized disposable fixture. Execute the tests and preserve the real command, exit code and output; a generated test file or mocked response is not a live API pass.
