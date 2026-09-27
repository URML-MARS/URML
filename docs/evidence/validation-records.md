<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# Validation records

The URML validator decides whether a program may run on a robot. A validation record is the written trace of one of those decisions: the verdict, the program that was judged, a content digest of every input it was judged against (manifest, envelope, compliance policy, rulebooks), the error codes, and the validator version. Records are opt-in. When you turn them on, each entry point appends one record per verdict, accepted or refused, to a local file you name, one JSON object per line.

A refused program is the evidence that the gate held: what a person or a model asked the robot to do, and the declared limit that stopped it. An accepted program is the other half of the same ledger. Because the inputs are recorded as digests, anyone who holds the same manifest, envelope, policy and rulebooks can run the validator again on a recorded program and check that the verdict comes out the same.

## Turn it on

| Entry point | Setting | Records |
|---|---|---|
| `urml validate` | `--evidence-log PATH` | its verdict |
| `urml execute` | `--evidence-log PATH` | the verdict of its check before execution, and the runtime's refusal if the runtime's own check refuses |
| `urml translate` | `--evidence-log PATH` | the LLM bridge's final verdict, with the request and each attempt's error codes |
| `urml run` | `--evidence-log PATH` | the bridge's final verdict as for `translate`, and the runtime's refusal |
| Python runtime | `URMLRuntime(adapter, evidence_log=PATH)` | refusals at its re-validation |
| MCP server | `URML_MCP_EVIDENCE_LOG=PATH`, or `--evidence-log PATH` (the flag wins) | the verdict of every `urml_validate` and `urml_execute` call, and the runtime's refusals |
| ROS 2 action server | node parameter `evidence_log` (empty, the default, is off) | the bridge's verdict for a sentence goal, the validator's verdict for every goal, and the runtime's refusals |

For example, `ros2 run urml_ros2_runtime urml-ros2-action-server --ros-args -p evidence_log:=/var/log/urml/evidence.jsonl`.

The runtime records refusals only. Every program it runs was accepted first by the entry point that called it, and that entry point recorded the acceptance. The MCP server and the action server take the log from the operator when they start, and an agent calling a tool or sending a goal cannot change it.

Some outcomes write no record because there is no verdict to record. A provider error is one: the model's reply was not a JSON object, or the provider call failed. It ends the translation without a verdict, even when an earlier attempt in the same translation was refused. A clarifying question that ends the command (clarify mode, RFC-0700) is another, as are usage errors and goals the action server turns away before validation. Fleet programs are not recorded yet: a record holds one manifest digest, and a fleet has one manifest per member.

`urml` prints nothing about the log. Output and exit codes are the same with and without `--evidence-log`. A log that cannot be written stops the command with exit code 2 before the verdict is printed or acted on. The MCP server fails the call and the action server refuses the goal, so nothing runs in either case. The Python runtime still raises its refusal, with a note that the record was not written.

## An example

The red-mug example has a variant, [`red-mug.grasp-4n.urml.yaml`](../../examples/home/red-mug.grasp-4n.urml.yaml), that grasps the mug at 4 N. The gripper allows 5 N and the deployment envelope caps the grip at 3 N, so the envelope refuses it:

```bash
cd examples/home
urml validate red-mug.grasp-4n.urml.yaml -m red-mug.manifest.yaml \
  -e red-mug.envelope.yaml --profile home --no-policy --evidence-log evidence.jsonl
```

The command prints the refusal and exits 1, as it does without the flag, and appends this line to `evidence.jsonl`:

```json
{"as_of":null,"attempt_codes":null,"attempts":null,"codes":["envelope.force_exceeded"],"default_rulebooks":true,"envelope_digest":"sha256:660c42e847de58644fe3767120097571adadb112f404ff888672e716898f466b","format":"urml.validation-record/1","manifest_digest":"sha256:7227344fdec067d4a854f7f3ec87ebc631de132e33731b2f2b4568cf71117699","policy":"none","profiles":["home"],"program":{"behavior":{"on_error":"abort_and_report","steps":[{"detect":{"object":"mug","store_as":"target"}},{"grasp":{"force":4.0,"target":"$target"}}],"type":"sequence"},"profile":"home"},"program_digest":"sha256:1932ce0821d9f81fb8c9ded1e3d5c04dac2ac9ce316217da4ea2e5afc4be2ba2","record_id":"sha256:42f41076198799d42a633cf8320927ef5b10e998ec7cc3961cbcfc9387a9f083","recorded_at":"2026-09-27T06:43:54Z","request":null,"result":{"accepted":false,"errors":[{"code":"envelope.force_exceeded","detail":null,"field":"force","message":"grasp.force (4.0 N) exceeds the strictest declared force cap (3.0 N).","path":["behavior","steps","1"],"primitive":"grasp","severity":"error","suggestion":"Reduce the grasp force to at most 3.0 N."}],"warnings":[]},"robot_id":"turtlebot4_red_mug","rulebooks":[],"stage":"validation","surface":"validate","tool":{"name":"urml-validator","version":"0.4.0"},"verdict":"refused","warning_codes":[]}
```

To read a log by eye, `python -m json.tool --json-lines evidence.jsonl` prints each record indented.

## Fields

| Field | Meaning |
|---|---|
| `format` | Always `urml.validation-record/1`. A reader rejects any other value. |
| `record_id` | `sha256:` over the verdict, the input digests, the profiles, the error codes and the validator version. Two runs that judged the same inputs the same way share an id; `recorded_at` is not part of it. |
| `recorded_at` | UTC time of the verdict, to the second. |
| `tool` | The validator's name (`urml-validator`) and version. |
| `surface` | The entry point that made the verdict: `validate`, `execute`, `run`, `translate`, `runtime`, `mcp` or `action_server`, or `api` for a record your own code builds with `build_record`. |
| `stage` | `validation` for an entry point's own check, `revalidation` for the runtime's check before its first adapter call, `bridge` for the LLM bridge's final verdict. |
| `verdict` | `accepted` or `refused`. |
| `robot_id` | The manifest's `robot_id`. |
| `program` | The program as judged. For a bridge verdict it is the model's final emission as the bridge parsed it, before `urml translate` and `urml run` copy the request into its `description`. Null only for a bridge refusal from a `urml-llm-bridge` too old to attach the parsed program; such a record cannot be replayed. |
| `program_digest` | Content digest of `program`. |
| `manifest_digest` | Content digest of the manifest. |
| `envelope_digest` | Content digest of the envelope, or null when there was none. |
| `policy` | `none` (the compliance pass was off), `default` (the bundled US-federal policy), or the content digest of a policy file. |
| `rulebooks` | The operator's rulebooks in the order they applied, each as its `rulebook_id` and content digest. The bundled rulebooks are not listed. |
| `default_rulebooks` | Whether the bundled rulebooks applied. |
| `as_of` | The date rulebook effective dates were judged against, when the entry point fixed one (`execute`, `run`, the runtime, the MCP execute tool, the action server's own check). Null means the validator used the current UTC date, which is the date in `recorded_at`. |
| `profiles` | The profiles the program was judged under. |
| `codes` | The error codes, in the order the validator emitted them. Empty for an acceptance. |
| `warning_codes` | The warning codes, in order. |
| `result` | The full verdict as `urml validate --json` prints it, with each error's path, message and suggestion. |
| `request` | The natural-language request, for a bridge verdict. Null otherwise. |
| `attempts` | How many emissions the bridge validated. Bridge verdicts only. |
| `attempt_codes` | The sorted error codes of each bridge attempt, in order. The last entry belongs to the final verdict, and an accepted attempt has none. Bridge verdicts only. |

A content digest is `sha256:` over canonical JSON (sorted keys, no whitespace), so the same content hashes the same whether it came from a YAML file, a JSON file or memory, however the file is formatted.

## Privacy

The log is off unless the operator names a file. URML writes records to that path and sends nothing anywhere. There is no telemetry.

A record holds the command being judged: the program, and for a bridge verdict the natural-language request, because they are what the gate decided about. If a deployment's requests can hold something you do not want kept, leave the log off there, or treat the file like any other log that holds user input.

A record adds no user name, host name, network address or account. The manifest, envelope, policy and rulebooks appear only as digests, and `robot_id` is the identifier the manifest gives the robot. The `result` field is the validator's report exactly as printed, so it carries what the validator reports. One case names a local file: when a policy's HBOM content rule (RFC-0005) cannot find the HBOM file, the error's `detail.resolved` holds the absolute path it looked for.

## Read and replay

```python
import yaml
from urml_validator.evidence import read_records, reverify

def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)

record = read_records("evidence.jsonl")[0]
check = reverify(
    record,
    manifest=load("red-mug.manifest.yaml"),
    envelope=load("red-mug.envelope.yaml"),
    policy=None,
)
print(check.reproduced, check.problems)
```

`read_records` returns every record in the file, in order, and raises `ValueError` naming the first line that is not a record. `reverify` runs the validator again on the recorded program and compares the verdict and the error codes. The inputs you pass must hash to the digests in the record: `policy=None` for `none`, `"DEFAULT"` for `default`, the parsed policy file for a digest, and the operator's rulebooks in their original order. When an input differs, the record does not reproduce and `problems` names the input. A policy with HBOM content rules (RFC-0005) reads files next to the manifest, so pass `manifest_base_dir` for those.

## The registry

The URML registry (`registry/`) re-verifies committed records with `reverify`, to show that a listed robot's recorded verdicts still reproduce under the current validator. A record there shows what one version of the validator decided about one program under one set of declared inputs, and nothing about the robot beyond that.
