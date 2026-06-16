#!/usr/bin/env python3
"""Build index.json from templates/** manifest sidecars.

M4a delivers full validation; this scaffold walks the tree and emits catalog entries.
Run from repo root: python scripts/build_index.py [--base-url URL]
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
SCHEMAS_DIR = REPO_ROOT / "schemas"
MANIFEST_SCHEMA_PATH = SCHEMAS_DIR / "manifest-v1.schema.json"
DEFAULT_BASE_URL = "https://raw.githubusercontent.com/ndx-video/MoBlend_Lib/main"

_TEMPLATE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ALLOWED_PARAM_TYPES = frozenset(
    {"string", "text", "int", "float", "bool", "color_rgba", "enum", "image", "video", "font"}
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel_url(base: str, rel: str) -> str:
    base = base.rstrip("/")
    rel = rel.replace("\\", "/").lstrip("/")
    return f"{base}/{rel}"


def _validate_manifest_structural(manifest: dict, manifest_path: Path) -> None:
    if manifest.get("version") != "1.0":
        raise SystemExit(f"{manifest_path}: manifest.version must be '1.0'")
    template_id = manifest.get("template_id")
    if not isinstance(template_id, str) or not _TEMPLATE_ID_RE.match(template_id):
        raise SystemExit(f"{manifest_path}: invalid template_id {template_id!r}")
    params = manifest.get("parameters")
    if not isinstance(params, list) or not params:
        raise SystemExit(f"{manifest_path}: parameters must be a non-empty array")
    for i, p in enumerate(params):
        if not isinstance(p, dict):
            raise SystemExit(f"{manifest_path}: parameters[{i}] must be an object")
        for key in ("id", "type", "node_target", "socket_identifier"):
            if not p.get(key):
                raise SystemExit(f"{manifest_path}: parameters[{i}] missing {key}")
        if p["type"] not in _ALLOWED_PARAM_TYPES:
            raise SystemExit(f"{manifest_path}: parameters[{i}] unknown type {p['type']!r}")
        if p["type"] == "enum" and not p.get("options"):
            raise SystemExit(f"{manifest_path}: parameters[{i}] enum requires options")


def _validate_manifest(manifest: dict, manifest_path: Path) -> None:
    if not MANIFEST_SCHEMA_PATH.is_file():
        raise SystemExit(f"manifest schema not found: {MANIFEST_SCHEMA_PATH}")
    try:
        import jsonschema
    except ImportError:
        _validate_manifest_structural(manifest, manifest_path)
        return
    with MANIFEST_SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as exc:
        raise SystemExit(f"{manifest_path}: manifest schema validation failed: {exc.message}") from exc


def _parameter_summary(manifest: dict) -> list[dict]:
    out: list[dict] = []
    for p in manifest.get("parameters") or []:
        if not isinstance(p, dict) or "id" not in p or "type" not in p:
            continue
        entry: dict = {"id": p["id"], "type": p["type"]}
        if p.get("label"):
            entry["label"] = p["label"]
        out.append(entry)
    return out


def build_catalog(base_url: str) -> dict:
    entries: list[dict] = []
    if not TEMPLATES_DIR.is_dir():
        raise SystemExit(f"templates/ not found: {TEMPLATES_DIR}")

    for manifest_path in sorted(TEMPLATES_DIR.rglob("*.manifest.json")):
        with manifest_path.open(encoding="utf-8") as f:
            manifest = json.load(f)

        _validate_manifest(manifest, manifest_path)

        template_id = manifest.get("template_id")
        if not template_id:
            raise SystemExit(f"manifest missing template_id: {manifest_path}")

        folder = manifest_path.parent
        stem = manifest_path.name[: -len(".manifest.json")]
        blend_name = f"{stem}.mo.blend"
        webp_name = f"{stem}.webp"
        blend_path = folder / blend_name
        webp_path = folder / webp_name

        if not blend_path.is_file():
            raise SystemExit(f"missing .mo.blend for {manifest_path}: {blend_path}")
        if not webp_path.is_file():
            raise SystemExit(f"missing .webp for {manifest_path}: {webp_path}")

        rel_dir = folder.relative_to(REPO_ROOT).as_posix()
        meta = manifest.get("metadata") or {}

        entries.append(
            {
                "template_id": template_id,
                "name": meta.get("name") or template_id,
                "category": meta.get("category") or "uncategorized",
                "description": meta.get("description") or "",
                "version": meta.get("template_version") or "1.0.0",
                "preview_url": _rel_url(base_url, f"{rel_dir}/{webp_name}"),
                "download_url": _rel_url(base_url, f"{rel_dir}/{blend_name}"),
                "manifest_url": _rel_url(base_url, f"{rel_dir}/{manifest_path.name}"),
                "parameters": _parameter_summary(manifest),
            }
        )

    return {
        "version": "1.0",
        "generated_at": _utc_now_iso(),
        "base_url": base_url,
        "templates": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MoBlend_Lib index.json")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="CDN root for absolute artifact URLs")
    parser.add_argument("-o", "--output", type=Path, default=REPO_ROOT / "index.json")
    args = parser.parse_args()

    catalog = build_catalog(args.base_url.rstrip("/"))
    args.output.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(catalog['templates'])} entries to {args.output}")


if __name__ == "__main__":
    main()