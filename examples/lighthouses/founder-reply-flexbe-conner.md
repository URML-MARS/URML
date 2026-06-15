# Founder action: email reply to David Conner (FlexBE / CHRISLab)

**Do not auto-send.** This is a human reply for the founder to send on the
existing Gmail thread, under `greenvh@gmail.com`.

- **To:** david.conner@cnu.edu
- **Cc:** robotics@cnu.edu
- **Subject:** Re: URML + FlexBE: following up from your note (overview attached)

Human-voiced, no LLM-posting. The engagement is academic and warm; keep it
short and technical. Send after the RFC-0474 branch / PR is up so the links
resolve.

---

Hi David,

Thank you, this is exactly the right nudge. I read both papers. The
capability framing in the synthesis work maps onto URML almost one to one:
your "capability" with its pre/post-conditions is a URML primitive plus the
manifest and safety envelope that gate it, and your realizability check is the
same idea as URML refusing a program before it actuates.

I took your suggestion and built the worked example. URML now exposes itself as
a ROS 2 action, `ExecuteURML`, so a FlexBE state can hand it a goal and get back
a result. The goal is either a validated URML program or a plain English
sentence; the server validates against the robot's capability manifest and
safety envelope first, refuses with the reason if it does not hold, and only
then executes against the substrate. There is a `ExecuteUrmlState` and a small
`URML Turtle Patrol` behavior that gates the run behind an operator approval,
the way Fig. 5 in your paper does.

It is all under `examples/flexbe/` in the repo, with a README that walks through
cloning FlexBE and `flexbe_turtlesim_demo`, building the workspace, and running
it against turtlesim. You can also exercise the URML side with no ROS 2 at all:

    urml execute examples/flexbe/turtle-patrol.urml.yaml \
      -m examples/flexbe/turtle.manifest.yaml --profile home --adapter mock

I would love to point a CHRISLab robot at it. If a student project or a short
co-authored workshop note on the URML-as-a-capability seam is of interest, I am
glad to support it. To keep things clean on my side: anything that lands stays
Apache 2.0 under DCO sign-off, co-authorship rather than co-invention, and the
URML name and the URML-Certified mark stay reserved. Nothing there should get in
the way of you using or evaluating it.

Happy to jump on a call whenever suits you.

Best,
Ido

---

## Notes for the founder

- Swap in the actual branch / PR URL once it is pushed (the README path above is
  stable regardless).
- A Gmail draft was **not** auto-created this round; say the word and I will
  prepare one on the existing thread.
- Per the confidentiality rule, this names no other engaged maintainer or org.
