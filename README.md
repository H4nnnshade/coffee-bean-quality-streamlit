# Coffee Bean Quality Classification Web App ☕

Aplikasi web interaktif berbasis **Streamlit**, **PyTorch**, dan **Scikit-Learn** untuk klasifikasi mutu biji kopi 4 kelas (*Defect*, *Longberry*, *Peaberry*, *Premium*) menggunakan arsitektur hybrid **CNN Penultimate Layer Feature Extraction + Support Vector Machine (SVM RBF)** skenario 60:20:20.

---

## 🔬 Arsitektur & Model

Aplikasi mendukung inferensi tunggal maupun perbandingan multi-model (*side-by-side*) dari 3 arsitektur CNN Backbone:
1. **MobileNetV3-Small** (1024-dim penultimate feature vector)
2. **ShuffleNetV2** (1024-dim penultimate feature vector)
3. **EfficientNet-B0** (1280-dim penultimate feature vector)

Klasifikasi akhir diproses melalui **SVM One-vs-Rest (RBF kernel)** dengan normalisasi margin Softmax numerik stabil.

---

## 🚀 Fitur Utama

- **Drag-and-Drop Image Uploader**: Validasi format citra (JPG, PNG, WEBP), pembatas ukuran file (<= 10 MB), dan perlindungan Decompression Bomb DoS (maksimal 16 Megapiksel).
- **Multi-Model Side-by-Side Comparison**: Perbandingan metrik prediksi mutu utama, tingkat keyakinan (*confidence*), dan latensi inferensi (ms) secara instan.
- **Horizontal Probability Chart**: Visualisasi distribusi probabilitas 4 kelas mutu kopi menggunakan Altair chart interaktif.
- **Defensive UI State Management**: Penanganan komprehensif 4 status state (*Idle*, *Loading*, *Empty*, *Error*) tanpa eksposur stack trace internal.

---

## 🛠️ Instalasi & Menjalankan Aplikasi

### 1. Prasyarat
- Python 3.10+
- Bobot model berada di `models/` dalam repo (default `MODEL_DIR`). Override lewat env `MODEL_DIR=/path/ke/models` — jangan menaruh path absolut host di source.

### 2. Setup Virtual Environment & Dependensi
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Menjalankan Server Streamlit
```bash
streamlit run app.py
```
Akses aplikasi melalui peramban web di `http://localhost:8501`.

### 4. Menjalankan Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### 5. Benchmark Fan-out (S4)
```bash
python scripts/bench_fanout.py --mode latency  --out bench/fanout_bench_60-20-20.json
python scripts/bench_fanout.py --mode rss3     --out bench/rss3_seq_run1.json
python scripts/bench_fanout.py --mode rss3 --parallel --out bench/rss3_par_run1.json
python scripts/bench_fanout.py --mode drift --split 80-10-10 --drift-iters 50 --out bench/drift_seq_80-10-10.json
```
Setiap mode berjalan di interpreter baru; angka di bawah dari host 8 core,
arm64, `TORCH_NUM_THREADS=2`, split `60-20-20`, 20 iterasi, satu citra sampel.

| Metrik | Sequential | Parallel (3 worker) | Gate PRD | Status |
|---|---|---|---|---|
| Latency p50 | 228.92 ms | 175.11 ms | ≥20% lebih cepat | **+23.51% PASS** |
| Latency p90 | 240.19 ms | 195.22 ms | info | — |
| Parity probabilitas | — | max Δ 0.0 | identik | PASS |
| Urutan `MODEL_KEYS` | terjaga | terjaga | invarian | PASS |
| Worker sweep p50 | 1: 242.7 / 3: 178.49 / 8: 248.41 ms | efektif 3 | 3 worker terbaik | PASS |
| RSS puncak cold-load 3 split | 846.1–974.6 MB | 770.6–951.4 MB | ≤650 MB | **FAIL (dua jalur)** |
| RSS puncak runtime Streamlit | 957.1–1022.6 MB | 1007.6–1068.0 MB | ≤650 MB | **FAIL (dua jalur)** |
| Drift 50 req/split | −71.1 … −105.3 MB | −284.5 … −322.1 MB | ≤+5 MB | tidak ada pertumbuhan |

Catatan gate memori: jalur **sekuensial** juga menembus 650 MB pada host ini
(3 run: 974.6 / 846.1 / 880.7 MB) dan juga menembus gate di bawah runtime
Streamlit (957.1–1022.6 MB), jadi pelanggaran bukan disebabkan fan-out.
`ENABLE_PARALLEL` tetap default `OFF` (keputusan D2) sampai gate memori
diselesaikan sebagai pekerjaan terpisah. Angka drift negatif berarti RSS akhir
lebih rendah dari baseline pasca-warm (arena/reclaim), bukan kebocoran.

---

## 📂 Struktur Direktori Proyek

```text
proyek-web/
├── app.py                     # Entry point & orkestrator Streamlit
├── config.py                  # Konfigurasi path model & runtime
├── requirements.txt           # Daftar pustaka & dependensi
├── ARCHITECTURE.md            # Dokumentasi arsitektur sistem
├── core/
│   ├── constants.py           # Pemetaan kelas, palet warna, & batas dimensi
│   └── schemas.py             # Domain dataclass inferensi
├── services/
│   ├── model_loader.py        # Singleton model loader ter-cache (@st.cache_resource)
│   ├── feature_extractor.py   # Ekstraktor representasi penultimate layer PyTorch
│   └── predictor.py           # Pipeline inferensi CNN-SVM & Softmax numerik
├── ui/
│   ├── components.py          # Komponen UI: uploader, badge, chart, card
│   └── layout.py              # Header, sidebar mode selector, kamus visual
└── tests/
    ├── test_model_loader.py   # Verifikasi integritas bobot & layer
    ├── test_pipeline.py       # Integration test inferensi end-to-end
    ├── test_ui_components.py  # Unit test rendering komponen Streamlit
    └── test_negative.py       # Negative testing & boundary value analysis
```
