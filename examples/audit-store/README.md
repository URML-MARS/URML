# URML validated-intent audit records as a robotics time series

Every time URML validates an intent before dispatch, it produces a verdict worth
keeping: the intent, the primitives it used, whether it dispatched or was
refused, and (if refused) the failing validation pass and the exact error codes.
Collected over time, those verdicts are a robotics time series. A refused intent
is as valuable to record as a dispatched one: it is the audit trail of what the
robot was asked to do and what the safety layer allowed.

This example comes from the
[ReductStore engagement](https://github.com/reductstore/reductstore/issues/1434),
where the maintainer confirmed ReductStore can store URML's audit messages.
[ReductStore](https://www.reduct.store/) is a time-series database for
unstructured robotics data, which is a clean fit: each URML audit record is a
small labeled entry on a per-robot time series.

```
intent ──URML validate──▶ verdict (dispatched / refused + reason) ──▶ audit record ──▶ ReductStore time series
                          (per dispatch, before actuation)              (one entry)      (bucket / entry / labels)
```

## What the example shows

[`emit_audit_records.py`](emit_audit_records.py) runs a short stream of intents
([`intents.yaml`](intents.yaml)) through the validator against
[`delivery.manifest.yaml`](delivery.manifest.yaml) +
[`safety-envelope.yaml`](safety-envelope.yaml), and turns each verdict into one
audit record:

| Intent | Audit record |
|---|---|
| go_to_shelf | DISPATCHED |
| fetch_the_mug | DISPATCHED |
| grab_too_hard | REFUSED — `envelope.force_exceeded` |
| into_the_crowd | REFUSED — `envelope.occupancy_zone_intrusion` |
| go_to_garage | REFUSED — `capability.missing_location` |

Each record carries a timestamp, the robot id, the intent, the primitives, the
verdict, the failing pass, and the codes. The script also prints the ReductStore
write plan: a `urml_audit` bucket, one entry per robot, each record written at its
timestamp with labels (`verdict`, `intent`) so the series is queryable by
outcome.

## The ReductStore write (integration pattern)

The hermetic script above stops at the write plan. A live node persists each
record with [reduct-py](https://github.com/reductstore/reduct-py):

```python
import json
from reduct import Client

async with Client("http://localhost:8383", api_token="...") as client:
    bucket = await client.create_bucket("urml_audit", exist_ok=True)
    for r in records:                       # the records this script builds
        await bucket.write(
            r["robot_id"],                  # entry = one per robot
            json.dumps(r).encode(),         # body  = the audit record
            timestamp=r["ts"],              # Unix microseconds
            labels={"verdict": r["verdict"], "intent": r["intent"]},
        )
```

Labels let you later query the series by outcome, for example "every refused
intent in the last hour" or "all `envelope.*` rejections for this robot", which
is exactly the audit question a time-series store answers well.

The ReductStore founder confirmed this layout on the
[engagement thread](https://github.com/reductstore/reductstore/issues/1434):
one bucket with entry paths for logical grouping (a separate bucket only earns
its keep when you need separate access, replication, or lifecycle policies), and
when the dispatch rate is high, batch the records before writing rather than
writing one at a time:

```python
# High event rate: batch records per entry before writing.
# https://www.reduct.store/docs/next/guides/data-ingestion#batching-data
from collections import defaultdict

by_robot = defaultdict(list)
for r in records:
    by_robot[r["robot_id"]].append(r)

for robot_id, batch in by_robot.items():
    async with bucket.batch(robot_id) as writer:
        for r in batch:
            writer.add(
                timestamp=r["ts"],
                data=json.dumps(r).encode(),
                labels={"verdict": r["verdict"], "intent": r["intent"]},
            )
```

## Run it

```bash
python examples/audit-store/emit_audit_records.py
```

Validator-only, no server, no robot, and deterministic (synthetic timestamps).
The committed [`audit-records.txt`](audit-records.txt) is byte-asserted by
`reference/validator/tests/test_audit_store.py`, so the example cannot drift from
the validator.
