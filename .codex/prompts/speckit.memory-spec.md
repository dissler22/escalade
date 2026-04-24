---
description: Reconcile transverse memory and durable documentation after implementation, from the real repository delta.
handoffs:
  - label: Run Final Analysis
    agent: speckit.analyze
    prompt: Run a final consistency analysis after updating durable documentation
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Mandatory First Read

Before reconciling durable documentation, read `.specify/memory/project-memory.md` first.

Use it as the transverse map of the repository:
- what the product is
- which durable feature docs exist
- which feature boundaries already matter
- which cross-feature invariants are already documented

Then read only the relevant durable docs in `docs/features/*.md` for the areas touched by the implemented change.

## Execution

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only`.
2. Inspect the real repository delta.
3. Update the smallest durable documentation surface that restores truth.

## Rules

- Start from the real repository delta, not spec prose alone.
- Update feature docs first, then `project-memory.md` if needed.
- Do not paste spec or plan summaries into durable docs.
