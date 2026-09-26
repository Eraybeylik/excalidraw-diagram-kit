// Screenshot the rendered <svg> of a page once it signals completion (document.title === "DONE").
// Usage: node capture.mjs <chrome> <url> <out.png> <width> <height> [timeoutMs]
// Uses the Chrome DevTools Protocol over Node's built-in WebSocket (Node >= 22), no npm deps.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [chrome, url, out, width, height, timeoutMs = "60000"] = process.argv.slice(2);
const profile = mkdtempSync(join(tmpdir(), "exdraw-chrome-"));
const proc = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
  "--remote-debugging-port=0", `--user-data-dir=${profile}`, `--window-size=${width},${height}`, "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

const fail = (msg) => { console.error(msg); cleanup(); process.exit(1); };
const cleanup = () => { proc.kill("SIGKILL"); try { rmSync(profile, { recursive: true, force: true }); } catch {} };
setTimeout(() => fail(`timeout after ${timeoutMs} ms`), Number(timeoutMs)).unref();

const port = await new Promise((resolve) => {
  let buf = "";
  proc.stderr.on("data", (d) => {
    buf += d;
    const m = buf.match(/DevTools listening on ws:\/\/[^:]+:(\d+)\//);
    if (m) resolve(m[1]);
  });
});
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));

let seq = 0;
const pending = new Map();
ws.addEventListener("message", (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
});
const send = (method, params = {}) => new Promise((resolve) => {
  const id = ++seq;
  pending.set(id, resolve);
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expr) => (await send("Runtime.evaluate", { expression: expr, returnByValue: true })).result?.result?.value;

await send("Page.navigate", { url });
for (;;) {
  const title = await evaluate("document.title");
  if (title === "DONE") break;
  if (title && title.startsWith("ERR")) fail(title);
  await new Promise((r) => setTimeout(r, 250));
}
const box = await evaluate(
  "(() => { const r = document.querySelector('svg').getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()",
);
const shot = await send("Page.captureScreenshot", {
  format: "png", captureBeyondViewport: true, clip: { ...box, scale: 1 },
});
writeFileSync(out, Buffer.from(shot.result.data, "base64"));
cleanup();
process.exit(0);
