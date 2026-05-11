"""Schema definitions for URML.

Sub-modules:
  common      Shared types: Pose, Frame reference, Location, VarRef, Duration.
  manifest    Layer-1 capability manifest schema.
  primitives  Layer-2 intent primitive arg schemas (one model per primitive).
  composition Layer-3 behavior-composition schema (Sequence, Branch, Parallel,
              Retry, on-error handling, variable bindings).
  envelope    Safety-envelope schema.
  program     Top-level URMLProgram model that ties everything together.

The schemas are versioned per Layer; see the per-layer spec docs under
`/spec/`. This module currently tracks v0.1 of every layer.
"""
