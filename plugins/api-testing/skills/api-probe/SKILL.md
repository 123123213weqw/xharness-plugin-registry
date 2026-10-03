---
name: api-probe
description: "Send bounded HTTP GET/HEAD probes and separate HTTP failure, transport failure and incomplete bodies."
---

# Api Probe

Use the endpoint and account selected for the current task. Read [the probe guide](../api-contract/references/workflow.md). The bundled `api_tool.py probe URL` supports GET/HEAD with a finite timeout, bounded output, explicit truncation, and no automatic redirects. Credentials are passed through `--header-env Header=ENV_NAME`, never pasted into command arguments or reports. For mutating methods, reuse existing Host execution/approval and project clients; this helper does not implement them. A 200 response is not proof of the business contract. Do not retry a write after an unknown result without checking external state.
