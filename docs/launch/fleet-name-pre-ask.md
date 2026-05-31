<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# Fleet-name pre-ask — outreach framing (DRAFT, not sent)

> **Status: draft for the maintainer's review. Nothing here has been sent.** Outreach is
> founder-gated. Before any message goes out, read the relevant outreach ledger
> (`examples/lighthouses/outreach*.yaml`) so a target the founder already contacted is not
> double-touched, and customize per target — a templated blast reads as spam and gets
> closed (see the OVOS / LibreTranslate / QGC closes).

## What the pre-ask is

The lightest rung on the engagement ladder: invite a robot or parts vendor to **claim their
robot's fleet name** by self-publishing a [minimal fleet-ready manifest](../../examples/fleet/CLAIMING.md).
No code, no integration — a name and a capability declaration they write and own. The point
is to seat named supply early so that, once demand exists, an integrator can point at a named
robot and pull the vendor into real engagement.

## Why it must be an invitation, not a presumption

Three rules, non-negotiable. Breaking any one turns a goodwill move into a trust loss:

1. **Opt-in, never unilateral.** We never name, list, or "register" a vendor's product
   ourselves. The claim is theirs to make and theirs to revoke. Naming someone's robot
   without them is a trademark problem and reads as implied endorsement.
2. **No overclaim.** A claimed name is `response: none` in the ledger and "listed, not
   endorsed" everywhere it appears. It is not a partnership, not a certification, not
   "engaged." The moment a name is displayed as adoption, we are inflating the story — the
   exact failure the project corrected once already.
3. **Honest about what we are.** The prose is AI-assisted and we say so, once, plainly
   (see `VIBE.md`). Not apologetic, not buried.

## Sequencing — do not run ahead of demand

The pull ("others ask them to engage") needs an *other*. With the repo's real audience near
zero, a mass pre-ask is claiming spots in an empty room and yields closes, not claims. Send
the pre-ask **after** there is at least a thin demand signal — a fleet demo that travels, an
integrator who actually wants a named robot, a published claim or two that others can see.
Start with the warmest 2–3 targets (vendors who already engaged on an earlier RFC), not a
broadcast.

## Draft invitation (customize per target)

> Subject: Claim your robot's fleet name in URML — no code, opt-in
>
> Hi [name],
>
> URML is an open Apache-2.0 spec for describing robot intent above the runtime (ROS 2, PX4,
> vendor SDKs). It recently added multi-robot fleets: one program can name several robots,
> address them individually, and synchronize them, with the validator catching cross-robot
> collisions before anything moves.
>
> Lightweight ask, opt-in and reversible: if you publish a small self-declared manifest for
> [robot], its `robot_id` becomes a **fleet name** any URML program can address. No code, no
> integration — a name plus a one-line capability declaration you write and own, de-listable
> any time. The template is here: [link to examples/fleet/CLAIMING.md].
>
> To be clear about what it is and isn't: a published manifest is a capability declaration,
> not an endorsement in either direction, and not a partnership or certification. It just
> makes [robot] nameable in a fleet, so an integrator assembling one can find it and come to
> you with a concrete request.
>
> Full disclosure: URML's prose and tooling are AI-assisted under the maintainer's direction
> (we document this openly in VIBE.md). A human reads and owns every word.
>
> No pressure and no follow-up unless you want one. If it's interesting, the claim path is one
> YAML file.
>
> — [name], greenvh@gmail.com

## Operational checklist before sending

- [ ] Read `examples/lighthouses/outreach*.yaml` — is this target already contacted? If so,
      this rides the existing thread, it does not open a new one.
- [ ] Customize the message to the specific robot and what it could do in a fleet. Delete the
      generic phrasing.
- [ ] Pick the right venue (an existing engaged thread, the vendor's preferred channel, not a
      cold GitHub issue if they've signalled otherwise).
- [ ] Do not name other engaged maintainers or orgs in a message to this one.
- [ ] After sending, record it in the ledger as `none` with `sent_at == last_touch`. A
      pre-ask is not engagement until they answer.
