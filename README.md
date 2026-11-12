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
- Bobot model tersimpan di lokasi direktori yang dikonfigurasi pada `config.py` (default: `/Users/agusfarhan/Downloads/skenario_60-20-20/`).

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
