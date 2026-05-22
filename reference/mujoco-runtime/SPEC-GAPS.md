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

# SPEC-GAPS — urml-mujoco-runtime

Per the spec-gap protocol (RFC-0014): each runtime is built strictly
against the frozen substrate Protocol; anything a substrate needs that
URML cannot express is recorded here and, if genuinely inexpressible,
promoted to a numbered RFC Draft for maintainer decision — never a
silent primitive/schema change.

## Gaps

**None.** A physics simulator is the purest case for the
substrate-neutrality acid test: it faithfully implements the existing
primitives (`move_to`/`hover`/`wait`/`measure`/`wait_for`/`report`,
`scan` as the documented stub) with zero ROS and no new vocabulary.
Capabilities a *bare* model lacks (`grasp`/`release`, `dock`,
`detect`, `capture`, `speak`, `listen`) are returned as honest
unsuccessful `SubstrateResult`s, not gaps in URML — a task-specific
model + controller companion supplies them under the unchanged
program, manifest, and validator. The drone trio is
`not_applicable_sim`.

No primitive, manifest field, or behavior-semantic change is needed or
proposed by this runtime.
