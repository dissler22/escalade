---
description: Update durable documentation from a real repository delta outside the normal post-spec workflow.
handoffs:
  - label: Run Final Analysis
    agent: speckit.analyze
    prompt: Run a final consistency analysis after updating durable documentation from repository delta
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Mandatory First Read

Before analyzing the delta, read `.specify/memory/project-memory.md` first.

Use it as the transverse map of the repository:
- what the product is
- which durable feature docs exist
- which feature boundaries already matter
- which cross-feature invariants are already documented

Then read only the relevant durable docs in `docs/features/*.md` for the areas touched by the delta.

## Purpose

This command updates durable documentation when the trigger is not "a completed spec".

Typical cases:
- the user asks to document the latest commit
- the user asks to reconcile docs after a merge
- the user asks to refresh docs from the current branch delta
- the user asks to document a change without using `specs/`

The target outputs are:
- `.specify/memory/project-memory.md` when the transverse state changed
- `docs/features/feature_*.md` when real feature state changed
- `docs/operations/server.md` only if a real recurring operational surface changed and the project uses that document

## Rules

- Start from the real delta, not from assumptions.
- Keep durable docs minimal and non-redundant.
- Do not turn durable docs into a changelog.
