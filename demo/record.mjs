// Record a demo run of a built tournament page into PNG frames (real time).
// Usage: node demo/record.mjs <page.html> <framesDir> [livePicks=4] [width=1100] [height=640]
// Then: ffmpeg -f concat -i <framesDir>/list.txt ... (see demo/README in the main README).
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [page, outDir, liveArg, wArg, hArg] = process.argv.slice(2);
const LIVE = Number(liveArg || 4), W = Number(wArg || 1100), H = Number(hArg || 640);
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9341;
mkdirSync(outDir, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${path.join(outDir, "..", "rec-profile")}`, `--window-size=${W},${H}`, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 50; i++) { try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); if (targets.find((t) => t.type === "page")) break; } catch {} await sleep(200); }
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pending = new Map();
ws.addEventListener("message", (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } });
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (e) => (await send("Runtime.evaluate", { expression: e, awaitPromise: true, returnByValue: true })).result?.result?.value;

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
await send("Page.navigate", { url: pathToFileURL(path.resolve(page)).href });
await sleep(1200);
await js("localStorage.clear(); location.reload(); 1");
await sleep(1200);

// background frame grabber
const frames = []; let grabbing = true, n = 0;
const grab = (async () => {
  while (grabbing) {
    const t = Date.now();
    const shot = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
    const f = `f${String(n++).padStart(4, "0")}.png`;
    writeFileSync(path.join(outDir, f), Buffer.from(shot.result.data, "base64"));
    frames.push({ f, t });
    await sleep(Math.max(0, 60 - (Date.now() - t)));
  }
})();

let mx = W / 2, my = H - 40;
async function moveTo(x, y, ms = 450) {
  const steps = Math.max(6, Math.round(ms / 30));
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: mx + (x - mx) * e, y: my + (y - my) * e });
    await sleep(ms / steps);
  }
  mx = x; my = y;
}
async function clickSide(i) {
  const r = await js(`(function(){var b=document.querySelectorAll('.side')[${i}].getBoundingClientRect();return [b.left+b.width/2,b.top+b.height*0.55]})()`);
  await moveTo(r[0] + (Math.random() - .5) * 60, r[1] + (Math.random() - .5) * 30);
  await sleep(350);
  for (const type of ["mousePressed", "mouseReleased"]) await send("Input.dispatchMouseEvent", { type, x: mx, y: my, button: "left", clickCount: 1 });
  await sleep(1100);
}

await sleep(1400);
for (let k = 0; k < LIVE; k++) await clickSide(Math.random() < .5 ? 0 : 1);
// finish the rest off-camera, then show the result
grabbing = false; await grab;
await js("(function(){var T=window.__tournament;var g=0;while(!T.state().done&&g<5000){T.pick(Math.random()<.5?0:1);g++}return 1})()");
await sleep(600);
await moveTo(W - 80, H - 40, 10);
grabbing = true;
const grab2 = (async () => {
  const end = Date.now() + 3600;
  while (Date.now() < end) {
    const t = Date.now();
    const shot = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
    const f = `f${String(n++).padStart(4, "0")}.png`;
    writeFileSync(path.join(outDir, f), Buffer.from(shot.result.data, "base64"));
    frames.push({ f, t });
    await sleep(Math.max(0, 120 - (Date.now() - t)));
  }
})();
await grab2;

// concat list with real durations; the cut to the result gets a fixed 0.15 s
const lines = [];
for (let i = 0; i < frames.length; i++) {
  const d = i + 1 < frames.length ? Math.min(0.5, (frames[i + 1].t - frames[i].t) / 1000) : 1.2;
  lines.push(`file '${frames[i].f}'`, `duration ${(d > 0.4 && i + 1 < frames.length ? 0.15 : d).toFixed(3)}`);
}
lines.push(`file '${frames[frames.length - 1].f}'`);
writeFileSync(path.join(outDir, "list.txt"), lines.join("\n"));
console.log(JSON.stringify({ frames: frames.length }));
ws.close(); chrome.kill();
