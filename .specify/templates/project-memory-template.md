# [PROJECT_NAME] Project Memory

## Role

This file is the transverse map of the repository. It explains what the product is, which features exist, where their durable documentation lives, and how they interact.

This file is not:
- a spec
- a changelog
- a task log
- a full code dump

## Product Snapshot

- Product: [what the system actually does]
- Main flow: [main user or runtime flow]
- Main surfaces: [backend, frontend, jobs, CLI, etc.]

## How To Read The Repo

- Start here for the global map.
- Then read the relevant feature docs in `docs/features/*.md`.
- Then open code and tests.
- If a change spans multiple features, read all linked feature docs named in `## Feature Interactions`.

## Active Documentation

- `.specify/memory/project-memory.md`: transverse map of the repository
- `docs/features/*.md`: durable current state by feature
- `docs/operations/server.md`: deployment and server operations, if the project has a server

## Quick Verification

- Main verification command: [main verification command]
- Scope: [what this verifies globally]

## Repository Topology

- Runtime code: [main code roots]
- Runtime data: [main storages, metadata, runtime paths]
- Public surfaces: [API routes, UI routes, jobs, CLI commands]

## Feature Map

### [Feature Name 1]
- Doc: `docs/features/[feature_doc_1].md`
- Role: [what this feature owns]

### [Feature Name 2]
- Doc: `docs/features/[feature_doc_2].md`
- Role: [what this feature owns]

### [Feature Name 3]
- Doc: `docs/features/[feature_doc_3].md`
- Role: [what this feature owns]

## Feature Interactions

- [Feature 1] depends on [Feature 2] for [contract / shared data / API]
- [Feature 3] consumes outputs from [Feature 1]
- [Feature 2] and [Feature 4] share [reference / metadata / runtime boundary]

## Cross-Feature Invariants

- [Invariant 1]
- [Invariant 2]
- [Invariant 3]

## Source Of Truth

In case of conflict, use this order:

1. current code and current tests
2. relevant `docs/features/*.md`
3. this file for transverse structure and feature interactions
4. operational docs when relevant
5. legacy documents

## Active Structural Drift

- [Current mismatch, unresolved migration, or known documentation/code gap]
