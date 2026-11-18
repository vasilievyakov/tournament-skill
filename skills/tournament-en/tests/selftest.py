#!/usr/bin/env python3
"""End-to-end check: build specs, play the whole tournament in headless Chrome, check the result.

Usage: python3 tests/selftest.py [spec.json ...]
Without arguments it uses the two demo specs from the repository (demo/*.json)
or a generated spec when the demo folder is absent. Needs Google Chrome or
Chromium; set CHROME=/path/to/chrome if it is not found automatically.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "scripts"))
import build  # noqa: E402

CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]

# plays the tournament by random clicks, then checks undo and the exported result
PLAYER = """<script>window.__errs=[];window.addEventListener('error',function(e){__errs.push(e.message)});
setTimeout(function(){var T=window.__tournament,log={};try{
 var guard=0;while(!T.state().done&&guard<5000){T.pick(Math.random()<.5?0:1);guard++;
   var s=T.state(); if(s.format==='el'){/* render is deferred; state advances on next current() */} }
 // pick() renders with a delay; force pending renders
}catch(e){__errs.push(String(e))}
setTimeout(function(){try{
  var r=T.result();log.result=r;T.undo();log.afterUndoDone=T.state().done;
}catch(e){__errs.push(String(e))}
 log.errs=__errs;var p=document.createElement('pre');p.id='SELFTEST';p.textContent=JSON.stringify(log);document.body.appendChild(p);},400);
},300);</script></body>"""


def chrome():
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def play(html_path, binary):
    src = Path(html_path).read_text(encoding="utf-8")
    page = src[: src.rfind("</body>")] + PLAYER + src[src.rfind("</body>") + 7 :]
    tmp = Path(tempfile.mkdtemp()) / "play.html"
    tmp.write_text(page, encoding="utf-8")
    out = subprocess.run(
        [
            binary,
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=20000",
            "--dump-dom",
            tmp.as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    ).stdout
    m = re.search(r'<pre id="SELFTEST">(.*?)</pre>', out, re.S)
    if not m:
        raise AssertionError("page did not report back (JS error before start?)")
    return json.loads(unescape(m.group(1)))


def check(spec_path, binary):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    n = len(spec["items"])
    rr = spec.get("format") == "round-robin"
    out = Path(tempfile.mkdtemp()) / "t.html"
    build.build(spec_path, out)
    log = play(out, binary)
    assert not log["errs"], f"JS errors: {log['errs']}"
    r = log["result"]
    want = n * (n - 1) // 2 if rr else n - 1
    assert len(r["matches"]) == want, (
        f"expected {want} matches, got {len(r['matches'])}"
    )
    placed = sum(len(x["items"]) for x in r["ranking"])
    assert placed == n, f"ranking covers {placed} of {n}"
    assert r["champion"]["id"] == r["ranking"][0]["items"][0]["id"]
    if not rr:
        assert r["runner_up"]["id"] != r["champion"]["id"]
    assert log["afterUndoDone"] is False, "undo did not reopen the last match"
    return f"{Path(spec_path).name}: {n} candidates, {len(r['matches'])} matches, champion {r['champion']['label']}"


def main():
    binary = chrome()
    if not binary:
        print("SKIP: Chrome/Chromium not found (set CHROME=...)")
        return 0
    specs = sys.argv[1:]
    if not specs:
        demo = SKILL.parent.parent / "demo"
        specs = sorted(str(p) for p in demo.glob("*.json")) if demo.is_dir() else []
    if not specs:
        tmp = Path(tempfile.mkdtemp()) / "gen.json"
        tmp.write_text(
            json.dumps(
                {
                    "title": "selftest",
                    "items": [{"text": f"option {i}"} for i in range(1, 8)],
                }
            ),
            encoding="utf-8",
        )
        specs = [str(tmp)]
    ok = True
    for s in specs:
        try:
            print("PASS", check(s, binary))
        except AssertionError as e:
            ok = False
            print("FAIL", Path(s).name, e)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
