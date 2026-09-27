<!--
Thanks for submitting a robot to the URML registry.

This template is for registry entries only. For code or spec PRs, use the
default template. The full flow is in docs/registry/SUBMISSION.md, what an
entry means is in registry/README.md, and what a listing does and does not
grant is in TRADEMARK.md.
-->

## Entry

- **Entry id** (the file name in `registry/entries/`):
- **Robot**:
- **Runtime and version**:
- **Evidence** (tick what the entry carries):
  - [ ] `hardware_run`
  - [ ] `simulation_run`
  - [ ] validation records
  - [ ] a self-reported compatibility claim (conformance report from the runtime's own adapter)

## Checks

- [ ] `python -m urml_conformance.registry check` prints no problems.
- [ ] I ran `python -m urml_conformance.registry export` and committed the updated `registry/registry.json`.
- [ ] Every date in the entry is quoted, every source opens without an account, and the entry names people and projects, not email addresses.
- [ ] The summaries say only what the sources say.
- [ ] The `limits` state what the evidence does not show.
- [ ] If the entry claims compatibility: the report came from `urml conformance run --adapter <our adapter>` (or `python -m urml_conformance --adapter <our adapter> --report`), unedited, and it names only profiles whose fixtures ran and passed.
- [ ] Every commit is signed off (`git commit -s`).

## Trademark acknowledgement

- [ ] I have read [TRADEMARK.md](https://github.com/URML-MARS/URML/blob/main/TRADEMARK.md). A listing does not grant a license to the URML or URML-Certified marks beyond the factual descriptor use it describes. I will not describe the robot or the runtime as "URML-Certified", and I will not imply URML endorsement, sponsorship, or affiliation.

## Keeping it current

- [ ] When URML releases a new version, I will re-run the check and update the entry, or open a pull request that sets `status: withdrawn`.

## Anything else the reviewer should know

<!-- Optional. Most submissions need nothing here. -->
