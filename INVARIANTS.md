# Production Invariants

These are the guarantees Action-Sink makes. They're non-negotiable.

---

## 1. No Silent Success

If we can't write to the audit log, we fail the request. Period.

- Database write failure returns `503`
- You won't get a `200 OK` unless we've durably recorded your dispatch
- We commit the write before sending the response

---

## 2. Idempotent Dispatch

Send the same `message_id` twice, get the same result.

- The `message_id` is your idempotency key
- We detect duplicates atomically
- Replays return `idempotent_replay: true` with `action_taken: "noop"`

---

## 3. Append-Only Audit

Once a record is written, it's never modified or deleted.

- No `UPDATE` or `DELETE` in our code
- No `updated_at` column—records are immutable
- Corrections? Write a new record

---

## 4. No Raw Payloads

We never store your actual signal data.

- We only store `payload_ref` (a pointer)
- The `explanation` field is length-bounded
- Unknown fields are rejected

---

## 5. Schema Versioning

We don't break things without warning.

- Every request must include `schema_version`
- Unsupported versions get `400`
- Breaking changes bump the version (v1 → v2)
- New optional fields are fine within a version
