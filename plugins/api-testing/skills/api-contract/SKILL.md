---
name: api-contract
description: "Inspect OpenAPI routes and response contracts without sending requests."
---

# Api Contract

Read the project OpenAPI document and identify its exact version, method, path, path/query parameters, request body, authentication and response statuses. Use [the bounded helper](scripts/api_tool.py) with `python api_tool.py index SPEC.json` to list JSON OpenAPI 3.x operations. It is an indexer, not a full OpenAPI validator: YAML, referenced Path Items and schema semantics require the project's compatible validator. Do not invent an endpoint, credentials or schema. A server URL from a document is metadata, not permission to call every endpoint. Explain unsupported references before choosing another installed tool.
