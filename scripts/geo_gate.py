"""Gate geometri rilis (ARCHITECTURE.md 20.13).

Mengukur `dropzone.top - lastCardBottom` di sembilan lebar lewat CDP mentah
ke Chrome headless. Nol dependency pihak ketiga: hanya stdlib HTTP + WebSocket
RFC6455 minimal, jadi `requirements.txt` tidak berubah.

Pemakaian:
    .venv/bin/python scripts/geo_gate.py --url http://127.0.0.1:8767

Exit 0 = sembilan lebar lulus delapan syarat. Exit 1 = ada pelanggaran.
Batas: probe ini mengukur geometri akhir, bukan penyebabnya.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

WIDTHS = [320, 360, 390, 414, 768, 820, 1024, 1280, 1440]
THRESHOLDS = {320: 80, 360: 80, 390: 72, 414: 72, 768: 64, 820: 64,
              1024: 56, 1280: 56, 1440: 56}

# Dipasang sebelum dokumen mana pun dimuat, jadi error saat render ikut tertangkap.
INIT_JS = r"""(() => {
  window.__errs = [];
  window.addEventListener('error', e => window.__errs.push(String(e.message || e.error)));
  window.addEventListener('unhandledrejection', e => window.__errs.push('rejection: ' + String(e.reason)));
})()"""

PROBE_JS = r"""(() => {
  const rect = e => e ? e.getBoundingClientRect() : null;
  const cards = [...document.querySelectorAll('div[style*="linear-gradient(115deg"]')];
  const last = cards[cards.length - 1];
  const dz = document.querySelector('[data-testid="stFileUploaderDropzone"]');
  // 20.13 amandemen §20.11.4: jangkar = IDENTITAS elemen (judul + kelas di
  // rantai yang sama), bukan `querySelector` first-match. `querySelector`
  // bisa disuapi decoy polos (h=20, static) di depan header asli, dan
  // class-swap memindahkan kelas tanpa mengubah hitungan -> dua-duanya bikin
  // gate hijau pada elemen yang salah. Judul = isi kontrak 20.9, tidak bisa
  // dipindah tanpa mengubah UI.
  const TITLE = 'Studio Unggah';
  const hdrs = [...document.querySelectorAll('.upload-studio-header')];
  const titled = [...document.querySelectorAll('h3')]
    .filter(h => (h.textContent || '').includes(TITLE));
  const hdr = (titled.length === 1 && hdrs.length === 1)
    ? titled[0].closest('.upload-studio-header') : null;
  const row = cards.length ? cards[0].closest('[data-testid="stHorizontalBlock"]') : null;
  const boxes = cards.map(rect);
  const tops = boxes.map(b => +b.top.toFixed(1));
  const gaps = [];
  for (let i = 1; i < boxes.length; i++) {
    const g = boxes[i].top - boxes[i - 1].bottom;
    if (Math.abs(g) > 200) continue;  // kartu di baris berbeda
    gaps.push(+g.toFixed(1));
  }
  const hs = boxes.map(b => +b.height.toFixed(1));
  const lb = last ? rect(last).bottom : null;
  const dt = dz ? rect(dz).top : null;
  const hs2 = hdr ? getComputedStyle(hdr) : null;
  return JSON.stringify({
    cards: cards.length,
    h: hs,
    tops: tops,
    gaps: gaps,
    lastBot: lb === null ? null : +lb.toFixed(1),
    dzTop: dt === null ? null : +dt.toFixed(1),
    gapToDz: (lb === null || dt === null) ? null : +(dt - lb).toFixed(1),
    hdrH: hdr ? +rect(hdr).height.toFixed(1) : null,
    hdrDisp: hs2 ? hs2.display : null,
    hdrPos: hs2 ? hs2.position : null,
    nHeaders: hdrs.length,
    nTitles: titled.length,
    hdrAnchored: !!hdr,
    rowGap: row ? getComputedStyle(row).rowGap : null,
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
    errs: window.__errs || [],
  });
})()"""


# ---------------------------------------------------------------- websocket
class WS:
    def __init__(self, url: str) -> None:
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        if not m:
            raise ValueError(f"unsupported ws url: {url}")
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.sock = socket.create_connection((host, port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
               "Upgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        if b"101" not in buf.split(b"\r\n")[0]:
            raise RuntimeError(f"handshake failed: {buf[:120]!r}")
        self._buf = b""

    def send(self, text: str) -> None:
        payload = text.encode()
        header = bytearray([0x81])
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 1 << 16:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _read(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("socket closed")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def recv(self) -> str:
        data = b""
        while True:
            b0, b1 = self._read(2)
            fin, _opcode = b0 & 0x80, b0 & 0x0F
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            if b1 & 0x80:
                mask = self._read(4)
                raw = self._read(n)
                data += bytes(b ^ mask[i % 4] for i, b in enumerate(raw))
            else:
                data += self._read(n)
            if fin:
                break
        return data.decode()

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


class CDP:
    def __init__(self, ws_url: str) -> None:
        self.ws = WS(ws_url)
        self._id = 0

    def call(self, method: str, **params):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def evaluate(self, expression: str):
        res = self.call("Runtime.evaluate", expression=expression,
                        returnByValue=True, awaitPromise=True)
        return res.get("result", {}).get("value")

    def close(self) -> None:
        self.ws.close()


# ---------------------------------------------------------------- chrome
def find_chrome() -> str:
    cands = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chrome/Chromium tidak ditemukan")


def http_json(url: str):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read().decode())


def launch(port: int):
    profile = tempfile.mkdtemp(prefix="geo-gate-")
    proc = subprocess.Popen(
        [find_chrome(), "--headless=new", f"--remote-debugging-port={port}",
         f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
         "--disable-gpu", "--hide-scrollbars", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            ver = http_json(base + "/json/version")
            return proc, ver["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.5)
    proc.kill()
    raise SystemExit("Chrome devtools tidak siap dalam 30s")


def new_page(browser_ws: str) -> str:
    b = CDP(browser_ws)
    try:
        target = b.call("Target.createTarget", url="about:blank")["targetId"]
    finally:
        b.close()
    host = re.match(r"ws://([^/]+)", browser_ws).group(1)
    for _ in range(40):
        for t in http_json(f"http://{host}/json/list"):
            if t.get("id") == target and t.get("webSocketDebuggerUrl"):
                return t["webSocketDebuggerUrl"]
        time.sleep(0.25)
    raise SystemExit("target page ws url tidak muncul")


def measure(cdp: CDP, url: str, width: int, wait: float) -> dict:
    cdp.call("Emulation.setDeviceMetricsOverride", width=width, height=900,
             deviceScaleFactor=1, mobile=width < 600)
    time.sleep(0.4)
    cdp.call("Page.navigate", url=url)
    deadline = time.time() + 40
    last = None
    while time.time() < deadline:
        try:
            raw = cdp.evaluate(PROBE_JS)
            last = json.loads(raw) if raw else None
            if last and last.get("cards") == 4:
                break
        except Exception:
            pass
        time.sleep(0.5)
    time.sleep(wait)
    raw = cdp.evaluate(PROBE_JS)
    return json.loads(raw) if raw else (last or {})


def verdict(w: int, m: dict) -> tuple[bool, list[str]]:
    """Delapan syarat sah ARCHITECTURE.md 20.13. Kembalikan (ok, alasan gagal)."""
    limit = THRESHOLDS[w]
    fails = []
    gap = m.get("gapToDz")
    if gap is None or gap > limit:
        fails.append(f"gapToDz {gap} > {limit}")
    if m.get("cards") != 4:
        fails.append(f"cards {m.get('cards')} != 4")
    if m.get("sw") != m.get("cw"):
        fails.append(f"overflow sw/cw {m.get('sw')}/{m.get('cw')}")
    hs = m.get("h") or []
    if len(hs) != 4 or max(hs) - min(hs) > 1:
        fails.append(f"tinggi kartu tidak seragam {hs}")
    if m.get("rowGap") != "16px":
        fails.append(f"rowGap {m.get('rowGap')} != 16px")
    hdr_h = m.get("hdrH")
    # 20.11.4: satu elemen berkelas, satu judul kontrak, dan keduanya di rantai
    # yang sama. Hitungan saja gugur oleh class-swap (kelas dipindah, hitungan
    # tetap 1), `querySelector` saja gugur oleh decoy-first.
    if m.get("nHeaders") != 1 or m.get("nTitles") != 1 or not m.get("hdrAnchored"):
        fails.append(f"anchor header nHeaders={m.get('nHeaders')} "
                     f"nTitles={m.get('nTitles')} anchored={m.get('hdrAnchored')}")
    if m.get("hdrDisp") in (None, "none"):
        fails.append(f"header display {m.get('hdrDisp')}")
    if m.get("hdrPos") != "static":
        fails.append(f"header position {m.get('hdrPos')} != static")
    if hdr_h is None or not (18 <= hdr_h <= 44):
        fails.append(f"hdrH {hdr_h} di luar 18..44")
    tops = m.get("tops") or []
    rows = len({round(t) for t in tops})
    if w >= 768:
        if rows != 1:
            fails.append(f"baris kartu {rows} != 1")
    else:
        gaps = m.get("gaps") or []
        if len(gaps) != 3 or any(abs(g - 16) > 1 for g in gaps):
            fails.append(f"gap antar kartu {gaps} != 16")
    if m.get("errs"):
        fails.append(f"page errors {m['errs'][:2]}")
    return (not fails), fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8767")
    ap.add_argument("--port", type=int, default=9333)
    ap.add_argument("--settle", type=float, default=1.0)
    args = ap.parse_args()

    url = args.url + ("&" if "?" in args.url else "?") + "geo=1"
    proc, browser_ws = launch(args.port)
    rows, failures = [], []
    try:
        cdp = CDP(new_page(browser_ws))
        try:
            cdp.call("Page.enable")
            cdp.call("Runtime.enable")
            cdp.call("Page.addScriptToEvaluateOnNewDocument", source=INIT_JS)
            for w in WIDTHS:
                m = measure(cdp, url, w, args.settle)
                ok, why = verdict(w, m)
                rows.append((w, m, ok, why))
                if not ok:
                    failures.append((w, m.get("gapToDz"), THRESHOLDS[w], why))
        finally:
            cdp.close()
    finally:
        proc.kill()

    print(f"{'w':>5} {'hdrH':>6} {'gapToDz':>8} {'limit':>6} {'cards':>6} "
          f"{'rowGap':>7} {'heights':>22} {'sw/cw':>11}  verdict")
    for w, m, ok, _why in rows:
        heights = ",".join(str(x) for x in m.get("h", []))
        print(f"{w:>5} {str(m.get('hdrH')):>6} {str(m.get('gapToDz')):>8} "
              f"{THRESHOLDS[w]:>6} {str(m.get('cards')):>6} "
              f"{str(m.get('rowGap')):>7} {heights:>22} "
              f"{str(m.get('sw'))+'/'+str(m.get('cw')):>11}  {'PASS' if ok else 'FAIL'}")

    if failures:
        print("\nBREACH:")
        for w, gap, limit, why in failures:
            print(f"  {w}px: gapToDz={gap} limit={limit}")
            for reason in why:
                print(f"      - {reason}")
        return 1
    print("\nGATE PASS: sembilan lebar lulus delapan syarat 20.13.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
