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

# Adoption-campaign drafts (founder-action)

## 1. slowrunner: first registry/directory entry (founder-voiced, founder-posted)

Channel: email or a comment on Discussion #497, founder's choice. He prefers
human replies; keep it personal, no footer. Why this matters strategically:
the runtime registry's third-party section is empty, and the standing public
commitment to a Tier-1 OEM advances "in the same wave that admits the first
third-party runtime." His entry is that wave, and it is also simply true:
he earned it. Do not name the OEM to him or anyone; the invite stands on its
own merits.

> Hey, an invitation rather than an ask.
>
> URML is opening its adopter and runtime registry, and I want the first entry to be real rather than corporate: you and Lyrical-Dave. You were the first person outside the project to run a validated URML program on hardware, you caught the FLU-to-RFD frame bug on a real robot and fixed it upstream, and your Ollama HOWTO literally changed the CLI (native `--provider ollama` is on main now, no dummy key; your context-length guidance still applies word for word).
>
> Concretely, if you are up for it: a short self-reported row in `docs/compatible-runtimes.md` for the GoPiGo3 runtime you validated (RFC-0014 self-reported tier, you credited as its hardware validator and field maintainer), and, if you like, an adopter entry on urml.dev with Dave's picture. It is one PR against a template (`docs/registry/SUBMISSION.md`); I can prepare the whole thing for your review, or you drive it, whichever is more fun.
>
> No deadline, no obligation, and if you would rather stay an uncredited legend, that is fine too.

On acceptance: help him land the PR (or prepare it for his review), then the
registry's first third-party entry exists; the OEM listing wave (Kawasaki row
on the commitments page) advances in that same wave, per the written promise.

## 2. Kawasaki listing back-post (queued behind entry #1)

Only after the first third-party registry entry is merged. One short comment
on Kawasaki-Robotics/khi_ros2#9 (closed resolved, warm): the listing condition
recorded in RFC-0029 and the commitments page has been met, the
`KawasakiAdapter` row is now live in `docs/compatible-runtimes.md` at the
self-reported tier, link to the row. No ask. Then the Mitsubishi follow-up on
melfa_ros2_driver discussion #25: the conformance-listing wave hunterzhongME
deferred on is now real, his Q4 answer welcome whenever.

## 3. Zivid report-back (after RFC-0682 merges)

**Public, on zivid/zivid-ros#163** (posted under idoco2003, VIBE line, no ask):

> Closing the loop on the schema questions from May: RFC-0682 (https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0682-3d-camera-declaration.md) is on main. It follows the guidance from the email exchange rather than inventing shapes: a 3D camera declares its primary product as a color point cloud with per-point attributes (xyz, rgba, snr, normals), accuracy is never a scalar (the manifest points at the per-model datasheet instead), acquisition modes stay the camera's business, and `pick_from` gained no vision-source field. The one open item that was ours to decide, hand-eye calibration, is a `mount` declaration (eye-in-hand or eye-to-hand against a declared frame, with an opaque reference to the calibration artifact). The Zivid Two cell manifest in the repo demonstrates every field. No ask; corrections welcome.
>
> AI-assisted prose, maintainer-reviewed before posting (see VIBE.md). Human-only correspondence available on request.

**Email to Espen Holmbakken** (founder-voiced, founder-sent from greenvh@gmail.com; he chose email as the substantive channel):

> Subject: URML follow-up: the 3D-camera schema, built the way you suggested
>
> Hi Espen,
>
> A short report-back on the exchange from May. You steered us away from recommending schema shapes and toward Zivid's authoritative documentation, and that turned out to be the right instruction. RFC-0682 is now on URML's main branch: a camera declares its primary product as a color point cloud with per-point attributes (xyz, rgba, snr, normals), accuracy is deliberately not a scalar (the manifest carries a pointer to the per-model datasheet, exactly the trueness/precision/working-distance point you made), acquisition modes stay the camera's business, and we dropped the pick_from vision-source idea as you suggested.
>
> The one question you left with us, hand-eye calibration, became a small `mount` declaration: eye-in-hand or eye-to-hand against a declared frame, with an opaque reference to the calibration artifact and the geometry riding the frame transforms we already had. No calibration file format invented.
>
> The Zivid Two cell manifest in the repo demonstrates every field: https://github.com/URML-MARS/URML/blob/main/reference/validator/tests/fixtures/manifests/zivid_two_cell.yaml
>
> Nothing to ask. If any of it misrepresents how Zivid thinks about these fields, I would rather fix it than leave it wrong.
>
> Thanks again,
> Ido

