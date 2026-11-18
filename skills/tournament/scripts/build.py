#!/usr/bin/env python3
"""Build a self-contained pairwise tournament page from a JSON spec.

Usage:
    python3 build.py spec.json [-o tournament.html] [--open]

The spec format is described in ../references/spec.md. The output is one HTML
file with no external dependencies: local images are embedded as data URIs,
candidate CSS and HTML are inlined. Standard library only.
"""

import argparse
import base64
import hashlib
import json
import mimetypes
import subprocess
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
CONTENT_KEYS = ("text", "html", "image", "code")
MAX_ELIMINATION = 64
MAX_ROUND_ROBIN = 10


def fail(msg):
    sys.exit(f"tournament: {msg}")


def embed_image(value, base):
    if value.startswith(("http://", "https://", "data:")):
        return value
    path = (base / value).expanduser()
    if not path.is_file():
        fail(f"image not found: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def validate(spec, base):
    if not isinstance(spec, dict):
        fail("spec must be a JSON object")
    if not spec.get("title"):
        fail("spec.title is required")
    items = spec.get("items")
    if not isinstance(items, list) or len(items) < 2:
        fail("spec.items must list at least 2 candidates")
    fmt = spec.get("format", "single-elimination")
    if fmt not in ("single-elimination", "round-robin"):
        fail("spec.format must be 'single-elimination' or 'round-robin'")
    limit = MAX_ROUND_ROBIN if fmt == "round-robin" else MAX_ELIMINATION
    if len(items) > limit:
        fail(
            f"{fmt} supports up to {limit} candidates, got {len(items)}; pre-filter or split into groups"
        )
    if spec.get("stage", "panel") not in ("panel", "dark", "light"):
        fail("spec.stage must be panel, dark or light")
    seen = set()
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            fail(f"items[{i}] must be an object")
        it.setdefault("id", f"V{i + 1}")
        it["id"] = str(it["id"])
        if it["id"] in seen:
            fail(f"duplicate id: {it['id']}")
        seen.add(it["id"])
        present = [k for k in CONTENT_KEYS if k in it]
        if len(present) != 1:
            fail(
                f"items[{i}] ({it['id']}) needs exactly one of {', '.join(CONTENT_KEYS)}"
            )
        if "image" in it:
            it["image"] = embed_image(it["image"], base)
        if it.get("stage") and it["stage"] not in ("panel", "dark", "light"):
            fail(f"items[{i}].stage must be panel, dark or light")
    return spec


def build(spec_path, out_path):
    spec_path = Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec = validate(spec, spec_path.parent)
    css = spec.pop("css", "")
    if isinstance(css, list):
        css = "\n".join(css)
    # stable key: same candidates -> resume where the owner stopped
    fingerprint = json.dumps(
        [spec["title"], spec.get("format"), [i["id"] for i in spec["items"]]],
        ensure_ascii=False,
    )
    spec["key"] = hashlib.sha1(fingerprint.encode()).hexdigest()[:12]
    data = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__CSS__*/", css.replace("</script", "<\\/script"), 1)
    html = html.replace("/*__SPEC__*/", data, 1)
    out = Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out, spec


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    ap.add_argument(
        "--open", action="store_true", help="open the page in the default browser"
    )
    args = ap.parse_args()
    out = args.out or str(Path(args.spec).with_suffix(".html"))
    path, spec = build(args.spec, out)
    n = len(spec["items"])
    fmt = spec.get("format", "single-elimination")
    duels = n * (n - 1) // 2 if fmt == "round-robin" else n - 1
    print(f"{path}\n{n} candidates, {fmt}, {duels} duels")
    if args.open:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            webbrowser.open(path.as_uri())


if __name__ == "__main__":
    main()
