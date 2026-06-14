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

# Move #56 post bodies: the service-robotics wave

Five targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(Apache stated; python-miio is GPL so cross-citation only; temi has no license
file, so the post states that and asks nothing). AI-assisted-authoring
disclosure up front. Titles carry no em-dash. The clean open service-robot
surface is cleaning robots (most service vendors are proprietary or excluded),
plus one hospitality SDK and one fleet-management framework. Framing: URML is
the typed validated intent checked against a per-model capability manifest and
dispatched over the project's own control plane. Bodies are varied per target.

---

## RFC-0600: Valetudo (anchor)

**Post to (Issue):** https://github.com/Hypfer/Valetudo/issues/new
**Title:** URML (open robot intent language): a validated cleaning intent over Valetudo's local API (request for comment)

```
Hi Valetudo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Valetudo is a great match in spirit: it puts a local, cloud-free control plane on a whole family of cleaning robots and exposes a documented REST and MQTT API. A cleaning task is a goal plus constraints, which is exactly what URML declares and checks.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML would map a clean-these-zones / go-to-this-room / spot-clean intent onto Valetudo's REST capabilities, validated against a per-model capability manifest (which suction modes, segment cleaning, zones, mop present) before any command is sent. You already expose what a given model supports as capabilities, and that maps directly onto a URML capability manifest, so an intent a particular robot cannot honor (a zone clean on a model without zone support) is refused before dispatch rather than failing on the device. URML adds the typed pre-dispatch check and a natural-language front door; Valetudo stays the firmware and the local control plane, and the same approach extends across the RE fork and the firmware builders without per-model special-casing.

Two real questions: (1) is a typed, validated cleaning-intent layer (checked against a per-model capability manifest, then dispatched over the local REST/MQTT API) useful above Valetudo? (2) Does your per-model capability exposure map cleanly onto such a manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0600-valetudo-outreach.md

Thanks for Valetudo; a cloud-free local control plane with a real API across many models is exactly where a validated-intent layer is both useful and easy to keep honest.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0601: python-miio

**Post to (Issue):** https://github.com/rytilahti/python-miio/issues/new
**Title:** URML (open robot intent language): a validated intent layer above python-miio for robot vacuums (request for comment)

```
Hi python-miio maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the device's declared capabilities and a safety envelope, then dispatched. python-miio is the canonical library for the Xiaomi miIO/MIoT protocol, and for the robot-vacuum subset it is a concrete substrate a validated cleaning intent could dispatch to. This is a request for comment (cross-citation only, since python-miio is GPL-3.0).

Nothing here asks the project to adopt, host, or maintain anything.

The mapping, scoped to vacuums: URML validates a cleaning intent (clean these zones, fan speed, go to dock) against the robot's declared features and a safety envelope, then dispatches; python-miio is one path that turns the validated intent into device commands. A miIO/MIoT vacuum advertises the features it supports, and that advertisement maps toward a URML capability manifest, so an unsupported intent is caught before it reaches the device. URML adds the typed pre-dispatch check and an optional natural-language front door; python-miio stays the protocol library, and given the GPL-3.0 license this proposes no shared code, only a dispatch relationship.

Two real questions: (1) for the robot-vacuum subset, is a typed validated intent layer above python-miio useful? (2) Do miIO/MIoT vacuum feature flags map cleanly toward a capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0601-python-miio-outreach.md

Thanks for python-miio; a well-maintained protocol library is exactly the kind of substrate a validated intent layer wants to dispatch through rather than reimplement.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0602: temi robot SDK

**Post to (Issue):** https://github.com/robotemi/sdk/issues/new
**Title:** URML (open robot intent language): a validated movement-intent layer for a temi robot (request for comment)

```
Hi temi SDK maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. temi is a service and hospitality robot, and the physical-action side of it (go to a saved location, follow, patrol a route, return to base) is exactly the goal-plus-constraints intent URML declares and validates.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a temi skill orchestrates an interaction; its movement actions are the part URML speaks to. URML would declare the movement intent, validate it against temi's saved locations and movement capabilities, then dispatch through the SDK. The interaction and the app stay with temi; URML adds the typed, checkable movement layer and an optional natural-language path ("go to the lobby, then patrol the east wing"). temi's saved locations and movement capabilities map onto a URML capability manifest and declared locations, so an instruction is checked against what the robot actually knows before it runs.

Two real questions: (1) is a typed, validated movement-intent layer (a go-to / patrol intent checked against temi's saved locations and capabilities, then dispatched through the SDK) useful? (2) Do temi's saved locations and movement capabilities map onto a capability manifest and declared locations?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0602-robotemi-sdk-outreach.md

Thanks for the temi SDK; a hospitality robot with a clean movement API is a natural place for a typed, English-friendly intent layer to sit above the interaction logic.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0603: Transitive

**Post to (Issue):** https://github.com/transitiverobotics/transitive/issues/new
**Title:** URML (open robot intent language): the validated intent a fleet mission-control app dispatches (request for comment)

```
Hi Transitive maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Transitive gives developers the full-stack plumbing to build web-based robot management and mission-control apps across a fleet, which is exactly the layer URML's multi-robot roster speaks to. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: Transitive provides the web-and-cloud framework and the connectivity; URML's candidate role is the typed, validated intent that a Transitive-built app dispatches. Declare the mission per robot, validate it against each robot's declared capabilities and a safety envelope, address the fleet through a roster with cross-robot constraints, then send it over Transitive's transport. A managed fleet maps onto URML's roster directly, which is what makes a multi-robot mission validatable before it leaves the dashboard. Transitive keeps the app framework and the plumbing; URML is the checkable intent that travels over it.

Two real questions: (1) is a typed, validated intent layer (a per-robot mission checked against each robot's capabilities, addressed via a fleet roster) a useful thing for a Transitive-built mission-control app to dispatch? (2) Does URML's multi-robot roster map onto how Transitive models a managed fleet?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0603-transitive-outreach.md

Thanks for Transitive; an open framework for building fleet mission-control is exactly where a validated multi-robot intent earns its place as the thing that travels over the wire.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0604: Congatudo

**Post to (Issue):** https://github.com/congatudo/Congatudo/issues/new
**Title:** URML (open robot intent language): a validated cleaning intent for the Conga family (request for comment)

```
Hi Congatudo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Congatudo puts a cloud-free local control plane on Cecotec Conga cleaning robots, in the spirit of Valetudo for a different vendor family, and the seam is the same: a cleaning intent, checked against a per-model capability picture, dispatched over your local control.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML would map a clean-these-zones / go-to-this-room / spot-clean intent onto Congatudo's local control, validated against a per-model capability manifest (suction modes, zones, mop) before dispatch. URML adds the typed pre-dispatch check and a natural-language front door; Congatudo stays the Conga control plane. There is a broader question your project helps answer: between Congatudo and the Valetudo ecosystem, the same validated-intent layer could sit above more than one cloud-free cleaning-robot control plane, and the interesting part is whether a single capability-manifest shape spans the vendor families cleanly.

Two real questions: (1) is a typed, validated cleaning-intent layer (checked against a per-model capability manifest, then dispatched over Congatudo's local control) useful for the Conga family? (2) Does Congatudo's per-model capability picture map cleanly onto such a manifest, and would it share a shape with the Valetudo side?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0604-congatudo-outreach.md

Thanks for Congatudo; a second cloud-free cleaning-robot control plane is exactly what makes the "one intent layer, many vendor families" question concrete rather than hypothetical.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
