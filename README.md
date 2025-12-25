# Action-Sink

A minimal, production-grade downstream agent for Axis.
Designed to receive `axis_output` and perform append-only auditing with strict idempotency.

## Production Invariants

See [INVARIANTS.md](./INVARIANTS.md) for the "hard rules" regarding PHI, failure modes, and idempotency.

## Setup

No external dependencies (Postgres/Redis) required. Uses async SQLite for the "no new services" constraint.

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API

See [API.md](./API.md) for the strict contract definition.
