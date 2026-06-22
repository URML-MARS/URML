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

# Move #52 founder actions: GoPiGo3 / Dexter Industries forum

The GoPiGo3 thread (`gopigo3`, RFC-0572) is the highest-momentum education engagement to date. It started on GitHub (`DexterInd/GoPiGo3#375` + URML discussion `#448`) and expanded to the Dexter Industries community forum, which is **not GitHub-routable**: posting there needs a forum account under the founder's own identity. The body below is drafted for the founder to post; ledger it in `outreach-move52.yaml` only once it actually goes out.

The skeptical-but-fair user feedback (slowrunner / `cyclicalobsessive`) has already been answered candidly on GitHub discussion `#448` ([discussioncomment-17356116](https://github.com/URML-MARS/URML/discussions/448#discussioncomment-17356116)): the platform's limits were conceded and the value reframed as the pedagogical validate-and-explain teaching loop. The maintainer (CleoQc) thread and the meeting remain the priority.

Two standing constraints apply:

- **No support promise.** URML is early and solo-maintained. Do not commit a response SLA or a "we will support your classroom" guarantee (CLAUDE.md, public-commitments rule). Offer interest and material, not a service level.
- **No cross-thread name-dropping.** Do not cite engaged maintainers or orgs from other threads as social proof. The forum participants themselves (`@cyclicalobsessive`, `@cleoqc`) are part of this conversation and fine to address directly.

---

## Dexter Industries forum: "Discuss a standardized robot language for GoPiGo3"

**Who.** GoPiGo3 community + maintainer. CleoQc (GoPiGo maintainer, built Bloxter in 2017) wants the natural-language-for-kids angle; slowrunner / jharris1993 are community regulars who pressure-tested the fit.

**Channel.** Forum topic 10858: <https://forum.dexterindustries.com/t/discuss-a-standardized-robot-language-for-gopigo3/10858>. Needs a forum account (founder identity; fill name/email with `greenvh@gmail.com` if registering).

**Ready-to-post body.**

> Hi all, and thanks to @cyclicalobsessive for starting this topic and to @cleoqc for the nudge to bring it here.
>
> Quick intro, since most of you have not seen URML. It is a small, open (Apache-2.0) language for describing what a robot should do. You write an instruction in plain words, it becomes a typed, explicit plan, and that plan is checked against the robot's declared capabilities and a safety envelope before anything moves. If you ask for something the robot can't do, or that isn't safe, it stops and tells you why in plain language, instead of failing silently. urml.dev has the details.
>
> I want to be honest about the GoPiGo3 specifically, because @cyclicalobsessive has pressure-tested it well. He's right that it's a simple platform: dead-reckoning, no fixed frame, and chasing any kind of compliance mark would be non-useful complexity for it. I'm not proposing any of that.
>
> The part I think is interesting for this audience is the teaching loop, and it's additive to Bloxter and Python, not a replacement. A kid types "drive to the desk and come back," sees it turn into a plan, and watches the robot explain itself when the request doesn't fit. That "the robot tells you why it said no" moment is exactly the classroom-safe behavior @cleoqc described when she talked about bringing robotics to more kids who aren't ready to type code yet.
>
> I'd genuinely like to hear where this is useful and where it isn't, from people who run these robots every day. No pitch attached. If the surface area isn't worth it for the GoPiGo3 user, that's a fair conclusion, and the conversation is still worth having.
>
> Thanks,
> Ido (urml.dev)

**After posting.** Record the post URL in `outreach-move52.yaml` (`gopigo3`) as a 2026 touch, refresh `outreach.db`.

---

## Standing personal founder-actions (not postable by the assistant)

- **Reply to CleoQc's email** (she emailed `greenvh@gmail.com`) and schedule the call. First outreach target to reach the let's-meet stage on the education / natural-language angle.
