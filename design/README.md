# Arabica Aurora — Design Deliverables

Dark inspection console for the coffee bean quality classifier. Derived entirely from the
reference stock-portfolio dashboard (aurora field, gradient KPI rail, area chart with glow,
donut allocation, right-hand asset panel).

## Files

| File | What it is |
|---|---|
| `aurora-dashboard.html` | Single-file interactive prototype. Open in any browser — no build, no server. |
| `screens/dashboard.png` | 1440×900 capture of the main console. |
| `screens/batch.png` | Batch & arsip table view. |
| `screens/model.png` | Model performance comparison view. |
| `screens/riwayat.png` | Inference history timeline view. |
| `screens/pengaturan.png` | Inference settings form view. |
| `../DESIGN.md` | Normative token spec (28 colors / 11 type scales / 13 components). |
| `../theme.css` | Tailwind v4 `@theme` export. |
| `../tokens.json` | W3C DTCG export. |

## Prototype behaviour

- **Rail nav routes** between 5 real views: Dashboard, Batch, Model, Riwayat, Pengaturan
  (hash-based, deep-linkable: `#Model`).
- **Chart** has working 1D / 1W / 1M / 1Y / MAX ranges, hand-rolled SVG smoothing,
  gradient glow stroke, area fill, hover crosshair + tooltip, 55% review threshold line.
- **Jalankan Klasifikasi** runs a simulated 1.4 s inference: re-randomises confidence,
  re-animates donut and probability bar.
- Batch table filters by class chip; Riwayat filters needs-review items.
- Toast feedback on every action; `Esc`-free, keyboard focus rings on all controls.

## Layout contract

1440×900 single viewport, no scroll. 90px rail · 58px top bar · 4 KPI cards (149px) ·
chart 902px + side panel 360px · Kamus Mutu deck 902px. Verified programmatically:
`docH == 900`, zero overflowing elements across all five views.

## Figma

File: `Arabica Aurora — Coffee Bean Quality Dashboard` — `fileKey=fucnagV9oPMSG5eADRqRgK`.
Contains the 1440×900 dashboard frame, 24 variables and 10 text styles built from `DESIGN.md`.
Further canvas edits are blocked by the Figma MCP Starter-plan call quota; the HTML
prototype is the live continuation of the same design.
