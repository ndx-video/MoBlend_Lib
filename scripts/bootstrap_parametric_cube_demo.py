#!/usr/bin/env python3
"""Generate the M4a bootstrap template (parametric-cube-demo).

Run under headless Blender from MoBlend_Studio engine root:

    blender --background --factory-startup --python ../MoBlend_Lib/scripts/bootstrap_parametric_cube_demo.py

Reuses the M1 synthetic template (m1_roundtrip.py), rebrands manifest metadata,
writes the three library artifacts, and renders a static WebP preview.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import bpy  # type: ignore[import-not-found]

_LIB_ROOT = Path(__file__).resolve().parent.parent
_STUDIO_ENGINE = _LIB_ROOT.parent / "MoBlend_Studio" / "engine"
_OUT_DIR = _LIB_ROOT / "templates" / "demo" / "parametric-cube-demo"
_TEMPLATE_ID = "parametric-cube-demo"

if str(_STUDIO_ENGINE) not in sys.path:
    sys.path.insert(0, str(_STUDIO_ENGINE))

from moblend.engine import load_template, render_frame  # noqa: E402
from moblend.manifest import minimal_validate  # noqa: E402

_M1_TEST = _STUDIO_ENGINE / "tests" / "m1_roundtrip.py"


def _library_manifest(source: dict[str, Any]) -> dict[str, Any]:
    manifest = json.loads(json.dumps(source))
    manifest["template_id"] = _TEMPLATE_ID
    manifest["metadata"] = {
        "name": "Parametric Cube Demo",
        "author": "MoBlend Library",
        "template_version": "1.0.0",
        "category": "demo",
        "description": "Parametric cube with full scalar types — Studio integration demo",
    }
    minimal_validate(manifest)
    return manifest


def _generate_fresh_m1_template() -> tuple[Path, dict[str, Any]]:
    """Return (path, manifest) from a clean M1 synthetic generator (no test mutations)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("m1_roundtrip", _M1_TEST)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {_M1_TEST}")
    m1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m1)
    return m1._create_minimal_test_template()  # type: ignore[attr-defined]


def main() -> int:
    _src_path, source_manifest = _generate_fresh_m1_template()
    manifest = _library_manifest(source_manifest)
    bpy.context.scene["moblend_manifest"] = json.dumps(manifest)

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    blend_path = _OUT_DIR / f"{_TEMPLATE_ID}.mo.blend"
    manifest_path = _OUT_DIR / f"{_TEMPLATE_ID}.manifest.json"
    webp_path = _OUT_DIR / f"{_TEMPLATE_ID}.webp"

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    load_template(str(blend_path))
    webp_bytes = render_frame(1, width=512, height=512, img_format="WEBP")
    webp_path.write_bytes(webp_bytes)

    print(f"[m4a-bootstrap] source: {_src_path}")
    print(f"[m4a-bootstrap] blend:  {blend_path} ({blend_path.stat().st_size} bytes)")
    print(f"[m4a-bootstrap] manifest: {manifest_path}")
    print(f"[m4a-bootstrap] preview:  {webp_path} ({webp_path.stat().st_size} bytes)")
    print("[m4a-bootstrap] PASS")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)