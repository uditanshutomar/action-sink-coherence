# Action-Sink API Contract

> **Service Version:** 1.0.0
> **Schema Version:** v1

This service acts as the reliable "write-ahead log" for Axis decisions. It accepts `axis_output` and guarantees an append-only audit trail. It is designed to be **fail-closed**: if we cannot write to disk, we reject the request.

---

## POST /v1/action/dispatch

Accepts Axis routing decisions and logs them for audit purposes.

### Request

```json
{
  "tenant_id": "acme_corp",
  "message_id": "msg_550e8400-e29b-41d4-a716-446655440000",
  "schema_version": "v1",
  "timestamp": "2024-12-25T10:30:00.000Z",
  "payload_ref": "s3://audit-bucket/events/2024/12/25/evt_123456.json",
  "axis_output": {
    "decision": "axis",
    "coherence_score": 0.92,
    "reason_codes": ["HIGH_CONFIDENCE", "PATTERN_MATCH"],
    "explanation": "Matched known pattern with high confidence",
    "processing_ms": 45
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `tenant_id` | string | 1-128 chars, alphanumeric + underscore |
| `message_id` | string | Idempotency key (1-256 chars) |
| `schema_version` | string | Must be `"v1"` |
| `timestamp` | string | ISO 8601 format |
| `payload_ref` | string | Pointer to stored event, not raw data |
| `axis_output.decision` | enum | `axis`, `m`, `both`, or `dlq` |
| `axis_output.coherence_score` | number | Between 0.0 and 1.0 |
| `axis_output.reason_codes` | string[] | Up to 10 codes, 64 chars each |
| `axis_output.explanation` | string | Max 1024 chars |
| `axis_output.processing_ms` | integer | Axis processing time in ms |

### Response

```json
{
  "message_id": "msg_550e8400-e29b-41d4-a716-446655440000",
  "accepted": true,
  "idempotent_replay": false,
  "action_taken": "logged",
  "processing_ms": 12
}
```

| Field | Description |
|-------|-------------|
| `message_id` | Echoes back the request ID |
| `accepted` | Always `true` if successful |
| `idempotent_replay` | `true` if this was a duplicate |
| `action_taken` | What we did: `logged`, `webhook_stub`, or `noop` |
| `processing_ms` | How long we took |

### Handling Duplicates

If you send the same `message_id` twice, we return `200 OK` with `idempotent_replay: true` and `action_taken: "noop"`. We chose this over `409 Conflict` to make retry logic simpler on your end.

---

## GET /v1/action/health

Returns `{"status": "ok"}` when the service is healthy.

---

## GET /v1/action/version

```json
{
  "service": "action-sink",
  "version": "1.0.0",
  "schema_version": "v1"
}
```

---

## Errors

| Status | When | Retry? |
|--------|------|--------|
| 400 | Malformed JSON or missing fields | No |
| 422 | Invalid values (e.g., score > 1.0) | No |
| 503 | Database unavailable | Yes |
| 500 | Something unexpected broke | Yes |

Example error response:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "coherence_score must be between 0.0 and 1.0"
  }
}
```
