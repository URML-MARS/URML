<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# tools/moltbook

Operational glue for URML's verified agent presence on [Moltbook](https://moltbook.com), the social network for AI agents. Tracked by [RFC-0640](../../docs/rfcs/0640-moltbook.md) (Move #62) and the ledger [`outreach-move62.yaml`](../../examples/lighthouses/outreach-move62.yaml).

This lives under `tools/`, **not** `reference/`, on purpose: Moltbook is a cloud service, and [`CLAUDE.md`](../../CLAUDE.md) prohibits cloud dependencies in the reference runtimes. Nothing here is imported by the bridge, the validator, or any runtime.

## What is here

- [`posts/demo-intro.md`](posts/demo-intro.md): the draft post body (title + body), reviewable before anything goes live. AI-authored and disclosed (VIBE.md), the standing posture for URML outreach.
- [`post_to_moltbook.py`](post_to_moltbook.py): a standard-library-only client. **Dry-run by default**; it never touches the network without `--post` and the credentials below.

## Status: gated, not live

Going live is founder-gated on two things, the same public-identity split used across URML's outreach:

1. **Moltbook developer-API access** (early-access, Meta-owned).
2. **The agent claim tweet** verifying the URML agent under the maintainer's X identity.

Until both are in place the ledger row stays `response: none` with an empty `posted_url`. Do not massage state.

The HTTP request shape in `post_to_moltbook.py::_submit()` is a **placeholder** to confirm against Moltbook's developer-API docs once access is granted; it is isolated so it is the only thing that needs updating.

## Usage

Preview the post (no network, no credentials needed):

```bash
python tools/moltbook/post_to_moltbook.py
```

Submit for real (requires the environment variables, and only with `--post`):

```bash
export MOLTBOOK_API_TOKEN=...     # developer-API token for the verified agent
export MOLTBOOK_AGENT_ID=...      # the claimed agent's id
export MOLTBOOK_API_BASE=https://...   # developer-API base URL

python tools/moltbook/post_to_moltbook.py --post --submolt robotics
```

Credentials come from the environment only; never commit them.

## After a post lands

Update [`outreach-move62.yaml`](../../examples/lighthouses/outreach-move62.yaml): set `sent_at` / `posted_url` / `last_touch`, add a posted `comment`, flip the `claude_directive` to `done`. Then refresh the dashboard mirror (`python tools/scripts/refresh_outreach_db.py`). Do not quote Moltbook counters (agent totals, upvotes) as engagement; they are vanity metrics by the repo's standing discipline.
