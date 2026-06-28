<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

---

# tools/moltbook

Operational glue for URML's verified agent presence on [Moltbook](https://moltbook.com), the social network for AI agents. Tracked by [RFC-0640](../../docs/rfcs/0640-moltbook.md) (Move #62) and the ledger [`outreach-move62.yaml`](../../examples/lighthouses/outreach-move62.yaml).

This lives under `tools/`, **not** `reference/`, on purpose: Moltbook is a cloud service, and [`CLAUDE.md`](../../CLAUDE.md) prohibits cloud dependencies in the reference runtimes. Nothing here is imported by the bridge, the validator, or any runtime.

## What is here

- [`posts/demo-intro.md`](posts/demo-intro.md): the draft post body (title + body), reviewable before anything goes live. AI-authored and disclosed (VIBE.md), the standing posture for URML outreach.
- [`post_to_moltbook.py`](post_to_moltbook.py): a standard-library-only client with `register` and `post` subcommands. Posting is **dry-run by default**; it never touches the network without `--post` and `MOLTBOOK_API_KEY`.

## The API, verified

Request shapes match Moltbook's official agent skill doc (`https://www.moltbook.com/skill.md`), verified 2026-06-28:

- Base: `https://www.moltbook.com/api/v1` (pinned in the client; the key is only ever sent there, per Moltbook's security rule).
- Register: `POST /agents/register {name, description}` returns `api_key` (`moltbook_...`), `claim_url`, and a verification code. **Self-serve, no waitlist.**
- Auth: `Authorization: Bearer <api_key>`.
- Post: `POST /posts {submolt_name, title (<=300), content (<=40000)}`. Rate limit: **1 post / 30 min**.

The "Apply for Early Access" developer program on `moltbook.com/developers` is a *different* thing (third-party app identity verification, the `moltdev_` / `X-Moltbook-App-Key` flow) and is **not** needed to register or post.

## The one real gate

There is no Meta-access blocker. The single gate is the **X claim tweet**: registration returns a `claim_url`, and a human (founder identity) must post the claim tweet to verify the agent. Until the agent is claimed and a post lands, the ledger row stays `response: none` with an empty `posted_url`. Do not massage state.

## Usage

1. Register the agent (prints the api_key and claim_url; save the key, it is shown once):

```bash
python tools/moltbook/post_to_moltbook.py register --name URML
```

2. Verify the agent: open the printed `claim_url` and post the X claim tweet under the founder identity.

3. Preview the post (no network, no key needed):

```bash
python tools/moltbook/post_to_moltbook.py post
```

4. Submit for real (needs the key, and only with `--post`):

```bash
export MOLTBOOK_API_KEY=moltbook_...
python tools/moltbook/post_to_moltbook.py post --post --submolt robotics
```

The key comes from the environment only; never commit it.

## After a post lands

Update [`outreach-move62.yaml`](../../examples/lighthouses/outreach-move62.yaml): set `sent_at` / `posted_url` / `last_touch`, add a posted `comment`, flip the `claude_directive` to `done`. Then refresh the dashboard mirror (`python tools/scripts/refresh_outreach_db.py`). Do not quote Moltbook counters (agent totals, upvotes) as engagement; they are vanity metrics by the repo's standing discipline.
