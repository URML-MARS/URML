# URML — Universal Robot Language

A small, opinionated, human-readable language for describing robot **intent**.

URML sits above existing robot operating systems (ROS 2, PX4, OPC UA Robotics, vendor SDKs) and lets humans, large language models, and robots share one vocabulary for *what should happen* — independent of which motors, joints, or frames carry it out. URML programs are statically verified against a robot's declared capabilities and active safety envelope before a single actuator moves.

URML is a **specification** and a set of **reference implementations**, not a robot operating system. The specification is Apache 2.0. The Core Commitment ([`CORE_COMMITMENT.md`](CORE_COMMITMENT.md)) names what will always remain so.

**Regulatory alignment.** URML's default validator policy aligns with United States federal robotics and uncrewed-systems regulation — NDAA Section 889 / FY26, the FCC Covered List, Executive Order 14307, and the American Security Robotics Act once enacted. Deployments outside the US may override the default via `urml validate --policy <file.yaml>`. See [RFC-0003](docs/rfcs/0003-us-alignment.md) for the rationale and RFC-0004 (forthcoming) for the mechanism.

## Status

**Phase 0 — pre-public draft.** Solo author working in public. The repository is being scaffolded; substantive specification work begins in Phase 1.

## Start Here

| Document | What it is |
|---|---|
| [`MANIFESTO.md`](MANIFESTO.md) | The project's constitution: vision, scope, design principles, architecture, roadmap. Read this first. |
| [`CLAUDE.md`](CLAUDE.md) | Strategic posture and working conventions for the repository. Loaded by AI-assisted tooling. |
| [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) | What stays Apache 2.0 forever. Non-negotiable. |
| [`GOVERNANCE.md`](GOVERNANCE.md) | How decisions are made today and how that scales. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to engage during Phase 0; how to contribute from Phase 1 on. |

## Engagement

For the duration of Phase 0, the artifact under review is the manifesto itself. The author welcomes critique of the primitive vocabulary, the layer boundaries, pointers to prior art, and use cases that strain the current architecture. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to reach the author.

Direct code contributions open in Phase 1.

## License

Apache License 2.0. See [`LICENSE`](LICENSE). Contributions require a Developer Certificate of Origin sign-off — see [`DCO`](DCO) and [`CONTRIBUTING.md`](CONTRIBUTING.md).
