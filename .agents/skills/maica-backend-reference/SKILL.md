---
name: maica-backend-reference
description: Verify MAICA ChatSubmod work against the current MAICA backend and API contract. Use when a task involves backend endpoints, request or response fields, authentication, errors, streaming or WebSocket behavior, protocol compatibility, or any claim about how the MAICA server currently works.
---

# MAICA Backend Reference

Treat these upstream sources as authoritative for this project:

- Backend repository: https://github.com/Mon1-innovation/MAICA
- API documentation: https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Documents.md

## Verification Workflow

1. Inspect the relevant local code first to identify the exact endpoint, field, or behavior in question.
2. When the task depends on the current backend contract, check the API documentation at the URL above. Do not rely on memory or assumptions about MAICA.
3. Inspect the corresponding backend implementation when the documentation is ambiguous, incomplete, potentially stale, or contradicted by local behavior.
4. Treat the API documentation as the declared contract and the backend source as the observed implementation. Explicitly report any discrepancy instead of silently choosing one.
5. Base code changes on verified behavior. Keep compatibility handling narrowly scoped and preserve existing local conventions.
6. In the final response, mention what upstream source was checked when that verification materially informed the result. Prefer a stable commit permalink when citing implementation details.

If the upstream sources cannot be accessed, state that verification was not possible and clearly distinguish verified local facts from assumptions.
