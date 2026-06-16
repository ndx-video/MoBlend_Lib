# MoBlend_Lib

Official Mo.Blend template library (beta). Powers [lib.moblend.dev](https://lib.moblend.dev) via static/Git CDN delivery.

**Client integration** lives in the sibling monorepo [MoBlend_Studio](../MoBlend_Studio).

## Quick start (authors)

1. Add a template under `templates/{category}/{template-id}/` with three artifacts:
   - `{id}.mo.blend`
   - `{id}.manifest.json` (extracted manifest per [manifest schema](../MoBlend_Studio/specs/manifest.schema.json))
   - `{id}.webp` (preview; animated preferred)
2. Regenerate the catalog:
   ```bash
   python scripts/build_index.py
   ```
3. Commit `index.json` and template files.

## Quick start (Mo.Blend Studio dev)

Point Studio broker config at this repo's raw Git URL:

```json
{
  "registryBaseUrl": "https://raw.githubusercontent.com/ndx-video/MoBlend_Lib/main"
}
```

Or use a local fixture path in `config.json` (`catalogFixturePath`) during offline dev — see [M4b spec](../MoBlend_Studio/specs/M4b%20-%20Broker%20Catalog%20Cache.md).

## Structure

```
MoBlend_Lib/
├── index.json              # auto-generated catalog
├── schemas/
├── scripts/
│   ├── build_index.py
│   └── bootstrap_parametric_cube_demo.py
└── templates/
    └── demo/
        └── parametric-cube-demo/   # M4a bootstrap template
```

## Bootstrap template

`parametric-cube-demo` is generated from the M1 synthetic template (`MoBlend_Studio/engine/tests/m1_roundtrip.py`). Regenerate artifacts with headless Blender:

```bash
blender --background --factory-startup --python scripts/bootstrap_parametric_cube_demo.py
python scripts/build_index.py
```

Preview images: static WebP is acceptable for bootstrap; production templates should ship animated WebP loops (PRD 7).

## Status

**M4a** (library bootstrap) — complete. One publishable template + generated `index.json`. See [ROADMAP M4a](../MoBlend_Studio/ROADMAP.md#m4a--library-repository-bootstrap).