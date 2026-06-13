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

# Move #47 post bodies: the perception / SLAM / mapping wave

Eleven targets (nerfstudio + gsplat folded into one org post), all GitHub
Issues. Post under idoco2003. No license-ask anywhere (MOLA core is GPL-3.0;
state, never ask). AI-assisted-authoring disclosure up front. Titles carry no
em-dash.

Shared posture: URML CONSUMES a map or state estimate as input to its
capability manifest and safety envelope; it does not produce one. These
projects build the poses, reconstructions, point clouds, occupancy, and VIO
estimates that a URML deployment resolves its frames and validates its
geofence / occupancy constraints against.

---

## RFC-0518: Nerfstudio (anchor; folds gsplat)

**Post to (Issue):** https://github.com/nerfstudio-project/nerfstudio/issues/new
**Title:** URML (open robot intent language): a reconstruction as the declared map a robot validates intent against (request for comment)

```
Hi Nerfstudio community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes a map, it does not build one -- and a nerfstudio / gsplat reconstruction is exactly the kind of map a robot could navigate and be geofenced against. (One note for the org, covering both repos.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a reconstruction of an environment is the spatial model a URML deployment declares as its world -- named locations and frames, and geofence / occupancy constraints in the safety envelope, reference geometry that came from the reconstruction. URML does not build the scene; it consumes it as the declared world a validated intent is checked against.

Two real questions: (1) is "a nerfstudio / gsplat reconstruction is the declared map a URML deployment validates intent against" a sensible consumer relationship? (2) Is there a clean export (poses, scene bounds, a mesh / occupancy proxy) a robot deployment would want to feed a capability manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0518-nerfstudio-outreach.md

Thanks for Nerfstudio and gsplat; high-quality reconstruction is exactly the input a declared-world layer wants to consume.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0519: COLMAP

**Post to (Issue):** https://github.com/colmap/colmap/issues/new
**Title:** URML (open robot intent language): a COLMAP reconstruction as declared geometry for a robot (request for comment)

```
Hi COLMAP community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes geometry, it does not compute structure -- and a COLMAP reconstruction (poses + 3D model) is exactly the geometry a robot's capabilities and envelope are defined against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: a COLMAP reconstruction gives camera poses and a 3D model. A URML deployment declares its frames and its geofence / occupancy constraints against geometry that can come from exactly such a reconstruction. URML consumes the reconstruction as the world an intent is validated in; it does not run the SfM/MVS.

Two real questions: (1) is "a COLMAP reconstruction is the declared geometry a URML deployment validates intent against" a sensible consumer relationship? (2) Is there a clean output (poses, model bounds) a robot deployment would feed a capability manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0519-colmap-outreach.md

Thanks for COLMAP; it is the reconstruction so much downstream robotics is built on, which is why the consumer relationship is worth naming.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0520: Open3D

**Post to (Issue):** https://github.com/isl-org/Open3D/issues/new
**Title:** URML (open robot intent language): Open3D geometry as the declared world a robot validates intent against (request for comment)

```
Hi Open3D community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes 3D geometry, it does not process point clouds -- and Open3D's point clouds, meshes, and reconstructions are exactly the geometry a robot's intent is validated against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Open3D's products (point clouds / meshes / reconstructions) are the geometry a URML deployment declares its occupancy and geofence constraints against, and its frames against. URML consumes that geometry as input; it does not do the processing.

Two real questions: (1) is "Open3D produces the 3D geometry, URML declares intent / constraints against it" a sensible consumer relationship? (2) Is there a clean product (an occupancy grid, a mesh, scene bounds) a robot deployment would feed a URML manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0520-open3d-outreach.md

Thanks for Open3D; it is the 3D-processing layer a declared-world robot intent sits on top of.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0521: Point Cloud Library (PCL)

**Post to (Issue):** https://github.com/PointCloudLibrary/pcl/issues/new
**Title:** URML (open robot intent language): processed point clouds as the declared world a robot validates intent against (request for comment)

```
Hi PCL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes processed geometry, it does not do the point-cloud math -- and PCL's segmented, registered point clouds are exactly the geometry a robot's intent is validated against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: PCL turns raw sensor returns into segmented, registered geometry. A URML deployment declares its occupancy / geofence constraints and its frames against that geometry. URML consumes the processed result as input; the heavy point-cloud math stays in PCL.

Two real questions: (1) is "PCL processes the point cloud, URML declares intent / constraints against the result" a sensible consumer relationship? (2) Is there a clean product (segmented obstacles, an occupancy proxy) a robot deployment would feed a URML manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0521-pcl-outreach.md

Thanks for PCL; it is the canonical point-cloud layer beneath the declared world a robot reasons about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0522: PDAL

**Post to (Issue):** https://github.com/PDAL/PDAL/issues/new
**Title:** URML (open robot intent language): ingested site point data as a robot's declared prior map (request for comment)

```
Hi PDAL community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. For a robot working over a large prior map -- a surveyed site, a building scan -- PDAL is how that point data is ingested and tiled, and URML consumes the resulting spatial model as the declared world it validates intent against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: PDAL ingests, filters, and tiles large point datasets. A URML deployment over such a site declares its named locations / frames and its geofence / occupancy constraints against geometry that came through a PDAL pipeline. URML consumes it; PDAL does the ingest.

Two real questions: (1) is "PDAL ingests the site point data, URML declares intent / constraints against it" a sensible consumer relationship for robotics over prior maps? (2) Is there a clean product (tiled occupancy, site bounds) a robot deployment would feed a URML manifest / envelope -- and is robotics-over-a-prior-map the right framing for PDAL's audience?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0522-pdal-outreach.md

Thanks for PDAL; for site-scale robotics the prior map starts as point data your pipelines ingest.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0523: OpenVDB

**Post to (Issue):** https://github.com/AcademySoftwareFoundation/openvdb/issues/new
**Title:** URML (open robot intent language): an OpenVDB grid as a robot's declared occupancy (request for comment)

```
Hi OpenVDB community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. On the robotics side, an OpenVDB grid is a memory-efficient occupancy / distance-field map -- and URML consumes an occupancy representation as the world its safety envelope is checked against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML's safety envelope declares occupancy and geofence constraints; an OpenVDB grid is exactly the kind of map those constraints can be checked against. URML consumes the volume as the declared world; OpenVDB is the volumetric data structure.

Two real questions: (1) is "an OpenVDB grid is the declared occupancy a URML deployment validates intent against" a sensible consumer relationship for the robotics use of OpenVDB? (2) Is there a clean way a robot deployment would reference a VDB occupancy / distance field from a URML safety envelope -- and is robotics-occupancy the right framing for OpenVDB's audience (vs VFX)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0523-openvdb-outreach.md

Thanks for OpenVDB; the sparse-volume structure is increasingly the occupancy map robots reason about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0524: MOLA

**Post to (Issue):** https://github.com/MOLAorg/mola/issues/new
**Title:** URML (open robot intent language): a MOLA estimate as the localized world a robot validates intent against (request for comment)

```
Hi MOLA community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML's posture toward SLAM is fixed: it consumes the estimate, it does not compute it -- and a MOLA pose estimate + map is exactly the localized world a URML deployment resolves its frames and constraints against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: MOLA produces the robot's pose in a map. URML resolves its frames and validates its geofence / occupancy constraints against that estimate and map. URML consumes the SLAM output; it does not run the optimization. (MOLA's core is GPL-3.0; this proposes no code reuse, only a consumer relationship.)

Two real questions: (1) is "MOLA produces the pose estimate + map, URML resolves frames and validates constraints against it" a sensible consumer relationship? (2) Is there a clean output (pose, map frame, occupancy) a robot deployment would feed a URML manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0524-mola-outreach.md

Thanks for MOLA; a modular LiDAR-inertial SLAM is exactly the estimate a declared-world intent layer wants to consume.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0525: MRPT

**Post to (Issue):** https://github.com/MRPT/mrpt/issues/new
**Title:** URML (open robot intent language): MRPT localization + maps as the world a robot validates intent against (request for comment)

```
Hi MRPT community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes the localization and maps a toolkit like MRPT produces, as the world a deployment validates intent against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: MRPT yields a pose estimate and occupancy / metric maps. URML resolves its frames and validates its geofence / occupancy constraints against that. URML consumes the estimate; MRPT does the localization and mapping.

Two real questions: (1) is "MRPT localizes and maps, URML resolves frames and validates constraints against it" a sensible consumer relationship? (2) Is there a clean output (pose, occupancy grid, map frame) a robot deployment would feed a URML manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0525-mrpt-outreach.md

Thanks for MRPT; a long-standing mapping/localization toolkit is exactly the estimate a declared-world intent layer consumes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0526: SymForce

**Post to (Issue):** https://github.com/symforce-org/symforce/issues/new
**Title:** URML (open robot intent language): consuming the estimate a SymForce-powered estimator produces (request for comment)

```
Hi SymForce community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. SymForce is the factor-graph / optimization engine behind state estimators and SLAM back-ends, and URML consumes the estimate such an engine produces -- it does not estimate.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The layering: SymForce optimizes the factor graph that yields a robot's state estimate. URML resolves its frames and validates intent against the active safety envelope using that estimate. URML is the declarative intent + envelope layer above the estimator; SymForce is the optimization that produces the estimate.

Two real questions: (1) is "a SymForce-powered estimator produces the state estimate, URML consumes it" a sensible layering? (2) Is an optimization library the right altitude to engage, or is the seam better at a SLAM / estimator that wraps SymForce?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0526-symforce-outreach.md

Thanks for SymForce; the codegen-plus-optimization approach is the engine under a lot of the estimates a declared-world intent layer consumes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0527: Patchwork++

**Post to (Issue):** https://github.com/url-kaist/patchwork-plusplus/issues/new
**Title:** URML (open robot intent language): ground segmentation feeding the occupancy a robot validates against (request for comment)

```
Hi Patchwork++ community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Patchwork++ is a perception pre-processing step -- separating ground from obstacles -- and that feeds the occupancy a robot reasons about, which URML consumes as the world its constraints are checked against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Patchwork++ turns a raw LiDAR scan into ground vs non-ground, which downstream becomes the obstacle / occupancy model. URML's geofence / occupancy constraints are validated against that model. URML consumes the result; Patchwork++ does the segmentation.

Two real questions: (1) is "Patchwork++ segments the scan, URML validates intent against the resulting occupancy" a sensible (if indirect) consumer relationship? (2) Is a segmentation step the right altitude to engage, or is the seam better at a mapping layer that consumes Patchwork++?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0527-patchwork-plusplus-outreach.md

Thanks for Patchwork++; fast, robust ground segmentation is where the occupancy a robot reasons about begins.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0528: OKVIS2

**Post to (Issue):** https://github.com/ethz-mrl/okvis2/issues/new
**Title:** URML (open robot intent language): an OKVIS2 VIO pose as the localized world a robot validates intent against (request for comment)

```
Hi OKVIS2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: an intent becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. URML consumes a state estimate, it does not compute one -- and an OKVIS2 visual-inertial pose is exactly the localized state a URML deployment's frames and constraints resolve against.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: OKVIS2 yields a real-time visual-inertial pose estimate. URML resolves its frames and validates intent against the active safety envelope using that pose. URML consumes the estimate; OKVIS2 is the VIO that produces it.

Two real questions: (1) is "OKVIS2 produces the VIO pose estimate, URML consumes it to resolve frames and validate intent" a sensible consumer relationship? (2) Is there a clean output (pose, covariance, frame) a robot deployment would feed a URML manifest / envelope -- and which is the cleaner first seam?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0528-okvis2-outreach.md

Thanks for OKVIS2; a real-time VIO estimate is exactly the localized state a declared-world intent layer consumes.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
