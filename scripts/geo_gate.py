"""Gate geometri rilis (ARCHITECTURE.md 20.13).

Mengukur `dropzone.top - lastCardBottom` di sembilan lebar lewat CDP mentah
ke Chrome headless. Nol dependency pihak ketiga: hanya stdlib HTTP + WebSocket
RFC6455 minimal, jadi `requirements.txt` tidak berubah.

Pemakaian:
    .venv/bin/python scripts/geo_gate.py --url http://127.0.0.1:8767

Exit 0 = sembilan lebar lulus enam belas slot. Exit 1 = ada pelanggaran.
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
  // 20.13 amandemen §20.11.6: jangkar dropzone = IDENTITAS, bukan atribut
  // first-match. `querySelector` bisa disuapi decoy yang menyalin data-testid;
  // decoy setinggi posisi asli membuat gapToDz tetap 62.7 sementara dropzone
  // asli bergeser +34px. Identitas = elemen yang memuat input[type=file] DAN
  // aria-label kontrak §20.9. aria-label dipakai karena `input` gampang
  // diduplikasi; aria-label itu isi kontrak, sekelas judul di rantai header.
  // 20.11.7: jangkar = elemen FUNGSIONAL, bukan atribut. `data-testid` dan
  // `aria-label` bisa dipindah ke decoy tanpa mengubah UI (terukur: dzTop
  // dilaporkan 801.9 sementara dropzone asli di 903.9, selisih 164.6 vs
  // ambang 62.7). Yang tidak bisa diduplikasi tanpa mengubah perilaku:
  // `input[type=file]`. Satu input -> closest() resolusi dropzone-nya.
  const DZ_ARIA = 'Unggah Citra Biji Kopi';
  const FIN = [...document.querySelectorAll('input[type=file]')];
  const dz = (FIN.length === 1)
    ? FIN[0].closest('[data-testid="stFileUploaderDropzone"]') : null;
  const dzAria = dz ? (dz.getAttribute('aria-label') || '') : '';
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
  // 20.13 amandemen 20.11.8: identitas kartu = empat teks label KPI kontrak
  // 20.9, bukan selektor gradien. `div[style*="linear-gradient(115deg"]` cuma
  // string atribut: ia bertahan walau kartu asli di-repaint jadi `none`
  // (terukur: cards 4, h 104x4, gapToDz 62.7 identik baseline, sementara
  // backgroundImage kartu ke-4 = none -> teks putih di latar #F8FAFC 1.046:1).
  // Rantai: span label -> closest(card) -> should land on 4 DISTINCT cards.
  const KPI = ['Engine Pipeline', 'Skenario Riset', 'Kelas Mutu', 'Protokol Uji'];
  const spans = [...document.querySelectorAll('span')];
  const rows = [...document.querySelectorAll('[data-testid="stHorizontalBlock"]')];
  const kpiN = [], kpiIdx = [], kpiInRow = [], kpiRowIdx = [];
  for (const t of KPI) {
    const hits = spans.filter(s => (s.textContent || '').trim() === t);
    const el = hits.length === 1 ? hits[0] : null;
    const cardEl = el ? el.closest('div[style*="linear-gradient(115deg"]') : null;
    const rowEl = el ? el.closest('[data-testid="stHorizontalBlock"]') : null;
    kpiN.push(hits.length);
    kpiIdx.push(cardEl ? cards.indexOf(cardEl) : -1);
    kpiInRow.push(!!rowEl);
    kpiRowIdx.push(rowEl ? rows.indexOf(rowEl) : -1);
  }
  // 20.11.9 / 6f: muka kartu. Hitungan tidak membuktikan apa pun soal paint.
  const paint = cards.map(c => getComputedStyle(c).backgroundImage || 'none');
  const boxes = cards.map(rect);
  // 20.11.10 / 6g: 6f memverifikasi PENULISAN gradien, bukan WARNA-nya.
  // `linear-gradient(#FFFFFF, #FFFFFF)` lolos substring 6f dengan geometri
  // byte-identik. Bukti warna hanya bisa dari piksel: rect mentah + warna
  // teks anak terjauh (label 0.68rem = teks terkecil = kasus terlemah).
  const rects = boxes.map(b => [+b.left.toFixed(1), +b.top.toFixed(1),
                               +b.width.toFixed(1), +b.height.toFixed(1)]);
  const textCol = cards.map(c => {
    const leaves = [...c.querySelectorAll('*')]
      .filter(e => !e.children.length && (e.textContent || '').trim());
    return leaves.length ? getComputedStyle(leaves[0]).color : null;
  });
  // 20.11.11 / 6h: 6g membaca `leaves[0]` SAJA -- label 0.68rem. Daun nilai
  // (teks besar) bisa diwarnai apa pun tanpa terlihat: saat `DoD Strict` dipaksa
  // rgb(78,54,226), teks kontras 1.000, geometri byte-identik, gate tetap hijau.
  // Koridor: pojok token sah + pita putih 44px di belakang teks -> (True, []).
  // Bukti kontras wajib per-DAUN, bukan per-kartu.
  const leafRects = cards.map(c => {
    const ls = [...c.querySelectorAll('*')]
      .filter(e => !e.children.length && (e.textContent || '').trim());
    return ls.map(e => {
      const b = rect(e);
      return [getComputedStyle(e).color,
              +b.left.toFixed(1), +b.top.toFixed(1),
              +b.width.toFixed(1), +b.height.toFixed(1)];
    });
  });
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
    rects: rects,
    textCol: textCol,
    leaves: leafRects,
    gaps: gaps,
    lastBot: lb === null ? null : +lb.toFixed(1),
    dzTop: dt === null ? null : +dt.toFixed(1),
    gapToDz: (lb === null || dt === null) ? null : +(dt - lb).toFixed(1),
    hdrH: hdr ? +rect(hdr).height.toFixed(1) : null,
    hdrTop: hdr ? +rect(hdr).top.toFixed(1) : null,
    hdrBot: hdr ? +rect(hdr).bottom.toFixed(1) : null,
    kpiN: kpiN,
    kpiIdx: kpiIdx,
    kpiInRow: kpiInRow,
    kpiRowIdx: kpiRowIdx,
    paint: paint,
    nFileInputs: FIN.length,
    nDz: FIN.length ? FIN[0].closest('[data-testid="stFileUploaderDropzone"]') ? 1 : 0 : 0,
    dzAria: dzAria,
    dzAnchored: !!dz && dzAria === DZ_ARIA,
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


# 20.11.10 / 6g: endpoint token 18 sebagai RGB. Dua ujung gradien 115deg
# dibandingkan sebagai PASANGAN TAK BERURUTAN -- urutan arah tidak dipakai
# sebagai bukti, yang dipakai adalah "dua warna ini ada di dua ujung".
KPI_STOPS = [
    ((0x00, 0x85, 0x72), (0x00, 0x71, 0xEF)),
    ((0x70, 0x47, 0xEB), (0xE5, 0x0B, 0x6A)),
    ((0xBC, 0x5A, 0x00), (0xEC, 0x00, 0x2B)),
    ((0x4E, 0x36, 0xE2), (0x7B, 0x55, 0xFF)),
]
STOP_TOL = 8          # toleransi per kanal terhadap endpoint kontrak
FACE_INSET = 10       # jarak titik sampel dari pojok, di luar border-radius 12
CONTRAST_MIN = 4.5    # WCAG SC 1.4.3; lantai token 4.8 (19.3) adalah ambang LAIN

# Dekode PNG dilakukan di dalam halaman (Image + canvas), bukan di Python:
# satu tangkapan per lebar, nol decoder pihak ketiga, requirements.txt tetap.
FACE_JS = r"""(() => {
  const img = new Image();
  const ready = new Promise((res, rej) => { img.onload = res; img.onerror = rej; });
  img.src = %s;
  return ready.then(() => {
    const cv = document.createElement('canvas');
    cv.width = img.naturalWidth; cv.height = img.naturalHeight;
    const ctx = cv.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0);
    const med = (x, y) => {
      const px = [];
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
        const d = ctx.getImageData(Math.round(x) + dx, Math.round(y) + dy, 1, 1).data;
        px.push([d[0], d[1], d[2]]);
      }
      const mid = k => px.map(p => p[k]).sort((a, b) => a - b)[4];
      return [mid(0), mid(1), mid(2)];
    };
    return JSON.stringify(%s.map(([x, y, w, h]) => {
      const i = %d;
      return [med(x + i, y + i), med(x + w - i, y + h - i)];
    }));
  });
})()"""


# 20.11.11 / 6h: sampel LATAR untuk tiap daun teks. Satu tangkapan yang sama
# (nol capture tambahan), median 3x3, titik di LUAR kotak glyph (kiri/kanan,
# `LEAF_GAP` px) -- bukan di dalamnya. Daun 0.68rem hanya setinggi huruf, jadi
# sampel di dalam rect membaca tinta glyph sebagai latar dan memerahkan tree
# sah. Titik dijepit ke dalam rect kartu supaya tak melempar getImageData
# keluar batas gambar.
LEAF_GAP = 6
FACE_LEAF_JS = r"""(() => {
  const img = new Image();
  const ready = new Promise((res, rej) => { img.onload = res; img.onerror = rej; });
  img.src = %s;
  return ready.then(() => {
    const cv = document.createElement('canvas');
    cv.width = img.naturalWidth; cv.height = img.naturalHeight;
    const ctx = cv.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0);
    const med = (x, y) => {
      const px = [];
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
        try {
          const d = ctx.getImageData(Math.round(x) + dx, Math.round(y) + dy, 1, 1).data;
          px.push([d[0], d[1], d[2]]);
        } catch (e) {}
      }
      if (!px.length) return null;
      const mid = k => px.map(p => p[k]).sort((a, b) => a - b)[Math.floor(px.length / 2)];
      return [mid(0), mid(1), mid(2)];
    };
    const rects = %s, leaves = %s, gap = %d;
    return JSON.stringify(rects.map(([cx, cy, cw, ch], i) => {
      const clamp = (px, py) => [
        Math.min(Math.max(px, cx + 1), cx + cw - 2),
        Math.min(Math.max(py, cy + 1), cy + ch - 2),
      ];
      // Titik sampel DI LUAR kotak glyph, bukan di dalamnya. Kotak teks 0.68rem
      // hanya setinggi huruf: sampel "inset 2px di dalam rect" mendarat di tinta
      // glyph itu sendiri dan membaca putih teks sebagai latar -> kontras 1.000
      // pada tree SAH. Latar diukur di kiri/kanan kotak pada dua tinggi.
      return (leaves[i] || []).map(([col, x, y, w, h]) => {
        const pts = [[x - gap, y + h / 3], [x - gap, y + 2 * h / 3],
                     [x + w + gap, y + h / 3], [x + w + gap, y + 2 * h / 3]]
          .map(([px, py]) => clamp(px, py));
        return [col, pts.map(([px, py]) => med(px, py))];
      });
    }));
  });
})()"""


def sample_faces(cdp: CDP, m: dict) -> tuple[list, list, float]:
    """Tangkap viewport sekali: pojok kartu (6g) + latar tiap daun (6h)."""
    rects = m.get("rects") or []
    leaves = m.get("leaves") or []
    if len(rects) != 4:
        return [], [], 0.0
    t0 = time.time()
    shot = cdp.call("Page.captureScreenshot", format="png")
    url = "data:image/png;base64," + shot["data"]
    raw = cdp.evaluate(FACE_JS % (json.dumps(url), json.dumps(rects), FACE_INSET))
    faces = json.loads(raw) if raw else []
    raw2 = cdp.evaluate(FACE_LEAF_JS % (json.dumps(url), json.dumps(rects),
                                        json.dumps(leaves), LEAF_GAP))
    leaf = json.loads(raw2) if raw2 else []
    return faces, leaf, (time.time() - t0) * 1000


_RGB_RE = re.compile(
    r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)"
    r"(?:\s*[,/]\s*([\d.]+)(%?))?\s*\)\s*$")


def parse_rgb(s: str | None):
    """Tiga kanal sah ATAU None. Alpha < 1 = None, sintaks lain = None.

    20.11.11: `rgba(255,255,255,0)` dulu terbaca (255,255,255) -- teks yang
    TAK TERLIHAT mendapat kontras 4.603:1 yang sama dengan putih opaque, jadi
    ghost text lolos. Warna yang tidak bisa dibuktikan terlihat bukan warna.
    """
    if not s:
        return None
    mt = _RGB_RE.match(s.strip())
    if not mt:
        return None
    a, pct = mt.group(4), mt.group(5)
    if a is not None:
        alpha = float(a) / 100.0 if pct else float(a)
        if alpha < 1.0:
            return None
    return tuple(float(x) for x in mt.groups()[:3])


def _lum(rgb) -> float:
    def f(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def stop_delta(i: int, pair: list) -> float:
    """Selisih kanal terburuk antara dua sampel dan dua endpoint kontrak."""
    a, b = pair
    ca, cb = KPI_STOPS[i]
    fwd = max(max(abs(a[k] - ca[k]), abs(b[k] - cb[k])) for k in range(3))
    rev = max(max(abs(a[k] - cb[k]), abs(b[k] - ca[k])) for k in range(3))
    return float(min(fwd, rev))


def verdict(w: int, m: dict) -> tuple[bool, list[str]]:
    """Enam belas slot sah ARCHITECTURE.md 20.13. Kembalikan (ok, alasan gagal)."""
    limit = THRESHOLDS[w]
    fails = []
    gap = m.get("gapToDz")
    # Syarat 1 dua sisi (20.11.5): plafon satu sisi sudah tiga kali memberi hijau
    # palsu -- header keluar alur / jangkar dz disuapi membuat gap MENGE CIL,
    # jadi makin rusak makin hijau. Lantai 16 wajib, bukan opsional.
    if gap is None or not (16 <= gap <= limit):
        fails.append(f"gapToDz {gap} di luar 16..{limit}")
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
    # 6c (20.11.5): relasi geometris, bukan cuma properti elemen. `position:absolute`
    # pada LELUHUR keluar dari alur tanpa menyentuh kelas/judul/style header:
    # hdrPos tetap `static`, hdrH tetap 38.7, tapi header menimpa dropzone.
    hdr_top, hdr_bot = m.get("hdrTop"), m.get("hdrBot")
    lb, dt = m.get("lastBot"), m.get("dzTop")
    if hdr_top is None or hdr_bot is None or lb is None or dt is None:
        fails.append(f"relasi geometri tidak terukur "
                     f"top={hdr_top} bot={hdr_bot} lastBot={lb} dzTop={dt}")
    else:
        if hdr_top < lb - 1:
            fails.append(f"header di atas baris KPI: hdrTop {hdr_top} < lastBot {lb}")
        if hdr_bot > dt + 1:
            fails.append(f"header menimpa dropzone: hdrBot {hdr_bot} > dzTop {dt}")
    # 6d (20.11.6): jangkar dropzone = identitas, bukan atribut first-match.
    # Decoy yang menyalin data-testid di posisi baseline membuat gapToDz tetap
    # 62.7 sementara dropzone asli bergeser +34px. `dzTop <= 0` FAIL eksplisit:
    # -739.3 (testid dipindah ke <style>) lolos di gate tanpa sisi bawah.
    # `nDz` turun jadi diagnostik: dulu syarat, padahal cuma menghitung
    # pembawa atribut `data-testid`. Penyerang yang memindahkan atribut justru
    # MENURUNKAN hitungan ke angka yang dianggap sah. Penentu = nFileInputs.
    if m.get("nFileInputs") != 1 or not m.get("dzAnchored"):
        fails.append(f"anchor dropzone nFileInputs={m.get('nFileInputs')} "
                     f"aria={m.get('dzAria')!r} anchored={m.get('dzAnchored')}")
    if dt is not None and dt <= 0:
        fails.append(f"dzTop {dt} <= 0")
    # 6e (20.11.8): identitas kartu = empat teks label KPI kontrak 20.9, bukan
    # selektor gradien. `div[style*="linear-gradient(115deg"]` cuma string
    # atribut: ia bertahan walau kartu asli di-repaint jadi `none`. Rantai:
    # span label -> closest(card) harus mendarat di 4 KARTU BERBEDA, dan label
    # harus di dalam stHorizontalBlock. Hitungan saja gugur oleh duplikasi.
    kn, ki, kr = m.get("kpiN"), m.get("kpiIdx"), m.get("kpiInRow")
    if not kn or not kr or any(n != 1 for n in kn) or not all(kr):
        fails.append(f"anchor kartu label kpiN={kn} kpiInRow={kr}")
    if not ki or len(set(ki)) != 4 or any(i < 0 for i in ki):
        fails.append(f"anchor kartu label -> kartu {ki} bukan 4 kartu berbeda")
    # 6e sisi kedua: `kpiInRow` cuma membuktikan tiap label punya LELUHUR
    # stHorizontalBlock, bukan bahwa keempatnya di BARIS YANG SAMA. Empat label
    # di empat baris berbeda (mis. uploader dipindah di antara kartu) lolos
    # `all(kr)` dan geometri kartu tetap terbaca seragam. Identitas baris =
    # satu indeks, bukan empat.
    kri = m.get("kpiRowIdx")
    if not kri or len(set(kri)) != 1 or any(i < 0 for i in kri):
        fails.append(f"anchor kartu label beda baris kpiRowIdx={kri}")
    # 6f (20.11.9): muka kartu. `cards == 4` + `h` seragam + `gapToDz` 62.7
    # semuanya tetap hijau saat backgroundImage kartu ke-4 jadi `none` ->
    # teks putih di latar efektif #F8FAFC = 1.046:1. Hitungan tidak
    # membuktikan paint; `getComputedStyle` yang membuktikan.
    paint = m.get("paint") or []
    if len(paint) != 4 or any("linear-gradient" not in (v or "") for v in paint):
        fails.append(f"paint kartu bukan linear-gradient {paint}")
    # 6g (20.11.10): 6f cuma substring. `linear-gradient(#FFFFFF, #FFFFFF)` dan
    # `linear-gradient(#000000, #000000)` dua-duanya lolos 6f -- yang kedua
    # bahkan kontras 21:1, jadi kriteria kontras SENDIRIAN tidak menutup
    # pelanggaran token 18. Tiga langkah, semuanya wajib:
    #   (1) dua pojok kartu disampel dari PIKEL hasil render, bukan string CSS
    #   (2) kontras warna teks terlemah vs KEDUA ujung >= 4.5 (WCAG, bukan 4.8)
    #   (3) kedua ujung wajib cocok endpoint token 18 untuk indeks kartu itu
    faces = m.get("faces") or []
    tcol = m.get("textCol") or []
    if len(faces) != 4:
        fails.append(f"muka kartu tidak tersampel {len(faces)}")
    else:
        for i, pair in enumerate(faces):
            if len(pair) != 2:
                fails.append(f"muka kartu {i} titik sampel {len(pair)}")
                continue
            # Coersi null DILARANG: probe yang gagal baca `textCol` dulu jatuh ke
            # putih, jadi muka gelap dapat 7.119:1 dan PASS. Pengukuran yang
            # hilang bukan pengukuran yang menguntungkan -- ia FAIL terpisah.
            raw_txt = tcol[i] if i < len(tcol) else None
            txt = parse_rgb(raw_txt)
            if txt is None:
                fails.append(f"teks kartu {i} tidak terbaca {raw_txt!r} "
                             f"(kontras tidak terukur)")
            else:
                worst = min(contrast_ratio(txt, tuple(pair[0])),
                            contrast_ratio(txt, tuple(pair[1])))
                if worst < CONTRAST_MIN:
                    fails.append(f"kontras kartu {i} {worst:.3f} < {CONTRAST_MIN} "
                                 f"muka={pair} teks={raw_txt}")
            d = stop_delta(i, pair)
            if d > STOP_TOL:
                fails.append(f"muka kartu {i} bukan token 18: delta {d:.1f} > "
                             f"{STOP_TOL} muka={pair} kontrak={KPI_STOPS[i]}")
    # 6h (20.11.11): 6g membaca `textCol` = `leaves[0]` saja (label 0.68rem).
    # Daun nilai (teks besar) bisa diwarnai apa pun tanpa terlihat, dan pojok
    # kartu tetap token -> hijau palsu. Tiga langkah, semuanya wajib:
    #   (1) tiap daun: latar di dalam rect daunnya sendiri, median 3x3, dari
    #       tangkapan yang SAMA (nol capture tambahan)
    #   (2) kontras = min lintas daun per kartu -- daun terlemah yang menembak
    #   (3) `parse_rgb` -> None untuk alpha < 1 dan sintaks non-rgb; verdict
    #       FAIL eksplisit, nol konstanta default
    leaf = m.get("leafFaces") or []
    if len(leaf) != 4:
        fails.append(f"latar daun tidak tersampel {len(leaf)}")
    else:
        for i, group in enumerate(leaf):
            if not group:
                fails.append(f"kartu {i} nol daun teks")
                continue
            worst_leaf = None
            worst_at = None
            for j, (col, pts) in enumerate(group):
                txt = parse_rgb(col)
                if txt is None:
                    fails.append(f"daun kartu {i}#{j} warna tidak terbaca {col!r}")
                    continue
                for p in pts:
                    if p is None:
                        fails.append(f"daun kartu {i}#{j} titik latar di luar kanvas")
                        continue
                    cr = contrast_ratio(txt, tuple(p))
                    if worst_leaf is None or cr < worst_leaf:
                        worst_leaf, worst_at = cr, (j, col, tuple(p))
            if worst_leaf is not None and worst_leaf < CONTRAST_MIN:
                j, col, p = worst_at
                fails.append(f"daun terlemah kartu {i} {worst_leaf:.3f} < "
                             f"{CONTRAST_MIN} daun#{j} teks={col} latar={p}")
    # Penjepit untuk daun di LUAR rect kartu (mis. teks terlempar keluar):
    # sampel latar akan jatuh ke piksel halaman, bukan muka kartu.
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
                m["faces"], m["leafFaces"], m["faceMs"] = sample_faces(cdp, m)
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
    worst = min((m.get("faceMs") or 0.0) for _w, m, _ok, _why in rows) if rows else 0.0
    print(f"\n6g+6h sampling: 1 tangkapan/lebar, tercepat {worst:.0f} ms")
    print("\nGATE PASS: sembilan lebar lulus enam belas slot 20.13 (6a-6h).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
