# ARCHITECTURE.md - Sistem Klasifikasi Mutu Biji Kopi (Hybrid CNN-SVM)

## 1. Ikhtisar Sistem
Aplikasi web berbasis Streamlit untuk inferensi klasifikasi 4 kelas mutu biji kopi (*defect*, *longberry*, *peaberry*, *premium*) menggunakan arsitektur hybrid Transfer Learning CNN (ekstraktor fitur) + Support Vector Machine (klasifikator).

Dataset & acuan bobot: Skenario 60:20:20 dari notebook penelitian skripsi (`Klasifikasi_Kopi_TL_SVM_Skenario_60_20_20.ipynb`).
Sumber bobot lokal tersimpan di: `/Users/agusfarhan/Downloads/skenario_60-20-20/`
- Checkpoint CNN: `checkpoint/{Model}_60-20-20.pt`
- Model SVM: `svm/{Model}_60-20-20_svm.joblib`

Arsitektur model yang didukung:
1. `MobileNetV3-Small` (Feature dimension: 1024) + SVM (RBF, OvR)
2. `ShuffleNetV2` (Feature dimension: 1024) + SVM (RBF, OvR)
3. `EfficientNet-B0` (Feature dimension: 1280) + SVM (RBF, OvR)

---

## 2. Struktur Proyek Modular (Clean Architecture)
```
/Users/agusfarhan/proyek-web/
├── AGENTS.md                  # Panduan kerja tim agen
├── ARCHITECTURE.md            # Dokumen arsitektur teknis & kontrak data
├── requirements.txt           # Dependensi runtime Python
├── config.py                  # Konfigurasi aplikasi & path artefak (12-Factor App)
├── app.py                     # Entry point UI Streamlit
├── core/                      # Domain logic & entity
│   ├── __init__.py
│   ├── constants.py           # Daftar kelas, warna visualisasi, ukuran gambar
│   └── schemas.py             # Dataclass / Pydantic schema hasil prediksi & metrik
├── services/                  # Application services
│   ├── __init__.py
│   ├── model_loader.py        # Singleton & lazy caching loader bobot PyTorch & SVM
│   ├── feature_extractor.py   # Pipeline preprocessing & ekstraksi layer penultimate
│   └── predictor.py           # Pipeline inferensi SVM, probability calibration / softmax
├── ui/                        # Presentation layer (Streamlit components)
│   ├── __init__.py
│   ├── components.py          # Uploader, visualisasi probabilitas, preview gambar
│   └── layout.py              # Header, sidebar panduan, tabs evaluasi vs prediksi
├── models/                    # Symlink / direct target ke checkpoint & model SVM
│   ├── checkpoint/
│   └── svm/
└── tests/                     # Unit test & integration test
    ├── __init__.py
    ├── test_pipeline.py       # Uji inferensi end-to-end dengan dummy/sample image
    └── test_model_loader.py   # Uji keberadaan bobot & integritas layer
```

---

## 3. Kontrak Data & Domain Schema (`core/schemas.py`)

### 3.1 Input
- File: Citra RGB (JPG, JPEG, PNG, WEBP).
- Max size: 10 MB.
- Preprocessing: Resize 224x224, Normalisasi ImageNet (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).

### 3.2 Output Prediksi (`PredictionResult`)
```python
@dataclass(frozen=True)
class ClassProbability:
    label: str           # defect, longberry, peaberry, premium
    display_name: str    # Defect, Longberry, Peaberry, Premium
    score: float         # 0.0 - 1.0 (persentase keyakinan)

@dataclass(frozen=True)
class ModelInferenceOutput:
    model_name: str      # MobileNetV3-Small / ShuffleNetV2 / EfficientNet-B0
    predicted_class: str
    display_name: str
    confidence: float
    probabilities: list[ClassProbability]
    inference_time_ms: float
```

---

## 4. Pipeline Inferensi Teknis
1. **Penyiapan Backbone CNN:**
   - Bangun model dasar torchvision tanpa klasifikator akhir (`Identity()`).
   - Load state_dict dari checkpoint `.pt` dengan `map_location='cpu'`.
   - Set mode `.eval()` dan bungkus dalam konteks `torch.no_grad()`.
2. **Penyiapan SVM:**
   - Load pipeline scikit-learn via `joblib.load()`.
   - Pipeline mencakup `StandardScaler` + `OneVsRestClassifier(SVC(kernel='rbf'))`.
3. **Ekstraksi Fitur & Klasifikasi:**
   - Tensor input shape: `(1, 3, 224, 224)`.
   - Forward pass CNN menghasilkan tensor `(1, dim_fitur)`.
   - SVM decision function `decision_function(X)` dinormalisasi via Softmax numerik stabil:
     $$\sigma(z)_i = \frac{e^{z_i - \max(z)}}{\sum_j e^{z_j - \max(z)}}$$
   - Ambil argmax sebagai kelas prediksi akhir.

---

## 5. Security & Resource Constraints
- **Zero Disk Leak:** Gambar hasil upload diproses via `io.BytesIO` di memory, tidak disimpan permanen ke disk tanpa izin.
- **CPU Optimization:** Jalankan inferensi pada CPU mode (`torch.set_num_threads(2)` atau otomatis) untuk menghindari CPU contention di server/local.
- **Cache Persistence:** Gunakan `@st.cache_resource` pada fungsi pemuatan model agar tidak reload bobot pada setiap re-run script Streamlit.

---

## 6. Pembagian Tugas (Actionable Checklist)

### @padolo (Backend & Machine Learning Service)
- [ ] Buat `config.py` yang mendeteksi jalur model lokal `/Users/agusfarhan/Downloads/skenario_60-20-20/` secara otomatis.
- [ ] Buat `core/constants.py` dan `core/schemas.py`.
- [ ] Buat `services/model_loader.py`: loader singleton untuk 3 model CNN + 3 pipeline SVM dengan caching resource.
- [ ] Buat `services/feature_extractor.py`: transformasi gambar dan forward pass penultimate layer.
- [ ] Buat `services/predictor.py`: fungsi eksekusi prediksi tunggal dan multi-model perbandingan lengkap dengan timing (ms).

### @parewa (Frontend & Streamlit UI)
- [ ] Buat file `requirements.txt` (`streamlit`, `torch`, `torchvision`, `scikit-learn`, `joblib`, `pillow`, `pandas`, `altair`).
- [ ] Buat `ui/components.py`: widget drag-and-drop file uploader, kartu hasil prediksi, grafik batang probabilitas horizontal, perbandingan side-by-side 3 model.
- [ ] Buat `ui/layout.py`: header informasi mutu kopi, panel metrik teknis (latensi, arsitektur), deskripsi kelas mutu.
- [ ] Buat `app.py`: orkestrasi halaman utama, penanganan 4 status state (`Idle`, `Loading`, `Empty`, `Error`).

### @banggapupa (Security, Architecture & Code Review)
- [ ] Validasi keamanan upload file (ekstensi, ukuran payload, sanitasi memori).
- [ ] Audit zero memory leak pada caching PyTorch & joblib.
- [ ] Review kepatuhan Clean Architecture dan modularitas antar-layer.

### @dorowani (QA, Testing & Local Execution Verification)
- [ ] Buat `tests/test_pipeline.py` untuk menguji inferensi tanpa UI menggunakan sample citra asli.
- [ ] Uji eksekusi runtime lokal Streamlit (`streamlit run app.py`).
- [ ] Verifikasi output log dan pastikan exit code bersih tanpa warning fatal.

---

## 7. Spesifikasi Arsitektur Desain UI/UX (Compact, Elegan & Balanced)

### 7.1 Filosofi Desain & Multi-Source Inspiration
- **Linear & Raycast:** Kepadatan informasi optimal (compact density), border kontras halus (`1px solid #E2E8F0`), micro-radius (`10px`–`14px`), sub-pixel badge status, keyboard-first feel.
- **Stripe & Apple Human Interface:** Tipografi hierarkis tajam (`Plus Jakarta Sans` display + `JetBrains Mono` numerical), dynamic gradient warm amber coffee (`#92400E` to `#451A03`) dipadu slate neutral dark (`#0F172A`).
- **Vercel / Tailwind UI:** Glassmorphism header (`backdrop-filter: blur(16px)`), pill tabs navigasi, visual balance antara workspace uploader (kiri) dan telemetry inference panel (kanan).

### 7.2 Design Token & Color Palette
1. **Background Canvas:** `#F8FAFC` (Slate-50) dengan surface `#FFFFFF` (Pure White).
2. **Gradient Accents:**
   - Brand Coffee Roast: `linear-gradient(135deg, #78350F 0%, #451A03 100%)`
   - Hero Badge Gold: `linear-gradient(135deg, #F59E0B 0%, #D97706 100%)`
   - Model Card Active: `linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)`
   - Border Shimmer: `linear-gradient(90deg, #E2E8F0, #CBD5E1, #E2E8F0)`
3. **Status & Class Colors:**
   - Premium: Emerald `#059669` (Gold/Green glow)
   - Peaberry: Indigo `#2563EB` (Precision blue)
   - Longberry: Amber `#D97706` (Warm harvest)
   - Defect: Rose `#DC2626` (Muted red alert)

### 7.3 Proporsi & Tata Letak Compact
- **Density:** Padding kontainer dipangkas dari 24px ke 12px–16px; margin vertikal diperketat untuk mencegah scrolling berlebih (above-the-fold prioritised).
- **Iconography:** Pure SVG inline (Lucide spec, 14px–20px) menggantikan emoji/raster font demi ketajaman retina display.
- **Micro-Typography:**
   - Display Label: `11px`, `uppercase`, `letter-spacing: 0.06em`, `font-weight: 700`.
   - Primary Metrics: `18px–24px`, tabular numbers, mono precision.
   - Body & Descriptions: `13px–14px`, `line-height: 1.45`.

### 7.4 Actionable Checklist Redesain UI/UX
- [x] `@parewa`: Implementasi perombakan visual di `ui/layout.py`, `ui/components.py`, `app.py`, dan `.streamlit/config.toml` sesuai spesifikasi Section 7.
- [x] `@banggapupa`: Security & DOM validation (cegah XSS, sanitasi inline SVG/HTML, zero style bleed).
- [x] `@dorowani`: Verifikasi regression test suite, uji render visual browser, tangkap bukti screenshot, dan commit perubahan ke branch `main`.

---

## 8. Spesifikasi Revisi Detail Visual, Logo Hierarchy, Metadata Layout, & Seamless Model Card

### 8.1 Evaluasi & Solusi Detail Visual
1. **Hierarki & Penempatan 3 Logo Website:**
   - **Logo 1 (Hero Header):** Hindari double-container (kotak di dalam kotak). Lepas wrapper `div` bertumpuk dengan gradien serupa. Gunakan single SVG mark proporsional ($36\text{px} \times 36\text{px}$) berdampingan langsung dengan judul utama dan versi badge.
   - **Logo 2 (Footer & Sub-komponen):** Pastikan viewBox SVG `0 0 32 32` dapat diskalakan secara fluid (`width="100%" height="100%"` dalam kontainer $20\text{px} \times 20\text{px}$) tanpa cropping atau visual distortion.
   - **Logo 3 (Favicon & Browser Shell):** Sinkronkan icon di `setup_page_config()` agar menggunakan coffee bean vector konsisten tanpa ketergantungan link eksternal yang rentan putus.

2. **Penghapusan Kotak Pembungkus Nama Model:**
   - Hapus header div abu-abu kaku (`card_header` ber-border dan background terpisah) di `render_model_result_card()`.
   - Ubah representasi nama model (`model_name`) dan arsitektur backbone (`arch_pill`) menjadi elemen tipografis terintegrasi yang menyatu langsung dengan header kartu prediksi atau tipografi judul bersih di atas badge tanpa garis batas pemisah canggung.

3. **Reorganisasi Layout Inspeksi Citra (Isi Ruang Kosong Samping Kiri):**
   - Di `app.py` & `ui/components.py`: Pindahkan blok informasi metadata citra (dimensi piksel, kanal warna RGB 24-bit, tensor normalisasi $224 \times 224$, serta status validasi integritas) ke kolom kiri (`col_input`) di bawah widget file uploader.
   - Kolom kanan (`col_meta`) didedikasikan penuh untuk pratinjau citra resolusi tinggi dengan rounded frame halus dan shadow lembut.
   - Hasil: Mengeliminasi kekosongan pada sisi kiri bawah uploader, menciptakan keseimbangan proporsional 50:50 yang compact dan informatif.

4. **Enhancement Mikro: Shadow, Gradiasi & Interaktivitas CSS:**
   - Card Hover Effects: Tambahkan elevation lembut `translateY(-2px)` dan shadow bertingkat `0 6px 16px -4px rgba(15, 23, 42, 0.08)`.
   - Haluskan transisi antar state dengan `transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1)`.

### 8.2 Actionable Checklist Revisi
- [x] `@parewa`: Eksekusi restrukturisasi layout di `app.py`, `ui/components.py`, dan `ui/layout.py` sesuai spesifikasi Section 8.
- [ ] `@banggapupa`: Re-audit keamanan DOM, sanitasi `html.escape()`, dan validasi layout style bleed.
- [ ] `@dorowani`: Uji test suite, validasi browser runtime, ambil tangkapan layar verifikasi, dan lakukan git commit ke branch `main`.
