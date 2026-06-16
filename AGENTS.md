# Agent Guide — MoBlend_Lib

Official Mo.Blend template library (v1). GitOps source for `lib.moblend.dev` during beta.

## Relationship

| Repo | Role |
|------|------|
| **MoBlend_Lib** (this repo) | Template artifacts + generated `index.json` |
| **MoBlend_Studio** (sibling `../MoBlend_Studio`) | Engine, broker, desktop — **client integration only** |

Specs and slice prompts live in `MoBlend_Studio/specs/`:
- [M4 — Registry Integration](../MoBlend_Studio/specs/M4%20-%20Registry%20Integration.md)
- [M4a — Library Repository Bootstrap](../MoBlend_Studio/specs/M4a%20-%20Library%20Repository%20Bootstrap.md)

## Layout (PRD 7)

```
templates/{category}/{template-id}/
  {id}.mo.blend
  {id}.manifest.json
  {id}.webp
index.json          # generated — run scripts/build_index.py
schemas/            # manifest + catalog JSON Schema
```

## Rules

1. **Manifest contract** — copy `manifest-v1.schema.json` from `MoBlend_Studio/specs/manifest.schema.json`; do not fork field semantics.
2. **Catalog contract** — `catalog-v1.schema.json` matches `MoBlend_Studio/specs/catalog.schema.json`.
3. **Security** — `use_scripts_auto_execute` disabled; no embedded Python drivers in `.mo.blend`.
4. **Sizes** — `.mo.blend` ≤ 50MB; `.webp` ≤ 2MB (PRD 7).
5. **Regenerate** — always run `python scripts/build_index.py` before committing `index.json` changes.

## Milestone

**M4a** bootstraps this repo. Progress files append to `MoBlend_Studio/.progress/` as `M004a.*.md`.

## Skill

From MoBlend_Studio: `/implement-m4a-library-bootstrap`