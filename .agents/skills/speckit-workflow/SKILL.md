---
name: speckit-workflow
description: Run the repo-local Specify/Speckit workflows from `.codex/prompts` when the user asks for Speckit, Specify, spec-driven development, or commands such as `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`, `/speckit.constitution`, `/speckit.memory-spec`, `/speckit.memory-commit`, or `/speckit.taskstoissues`.
---

# Speckit Workflow

Use this skill as the supported replacement for custom slash prompts in
`.codex/prompts/*.md`. The prompt files remain the source of truth; this skill
routes user intent to the right prompt and then follows that prompt exactly.

## Routing

Normalize a user request by stripping a leading `/` and mapping the command to a
file in `.codex/prompts/`:

- `speckit.specify` or `specify`: read `.codex/prompts/speckit.specify.md`.
- `speckit.plan` or `plan`: read `.codex/prompts/speckit.plan.md`.
- `speckit.tasks` or `tasks`: read `.codex/prompts/speckit.tasks.md`.
- `speckit.implement` or `implement`: read `.codex/prompts/speckit.implement.md`.
- `speckit.clarify` or `clarify`: read `.codex/prompts/speckit.clarify.md`.
- `speckit.analyze` or `analyze`: read `.codex/prompts/speckit.analyze.md`.
- `speckit.checklist` or `checklist`: read `.codex/prompts/speckit.checklist.md`.
- `speckit.constitution` or `constitution`: read `.codex/prompts/speckit.constitution.md`.
- `speckit.memory-spec`: read `.codex/prompts/speckit.memory-spec.md`.
- `speckit.memory-commit`: read `.codex/prompts/speckit.memory-commit.md`.
- `speckit.taskstoissues`: read `.codex/prompts/speckit.taskstoissues.md`.

If the user asks generally for a new feature spec, route to `speckit.specify`.
If they ask for planning a spec, route to `speckit.plan`. If they ask for
generating implementation work items, route to `speckit.tasks`. If they ask to
build the planned work, route to `speckit.implement`.

## Execution

1. Read `AGENTS.md`.
2. Read `.specify/memory/project-memory.md` and `.specify/memory/constitution.md`
   unless the selected prompt says otherwise.
3. Read exactly the selected `.codex/prompts/speckit.*.md` file.
4. Treat the user's remaining text after the command name as `$ARGUMENTS`.
5. Execute the selected prompt's workflow from the repository root.
6. Preserve the repo's normal safety rules: inspect current Git status before
   edits, do not overwrite unrelated user changes, and run relevant verification
   before committing or pushing when changes are made.

## Missing Or Ambiguous Command

If the requested workflow is ambiguous, ask one concise clarification. If a
prompt file is missing, stop and report the missing path instead of inventing the
workflow.
