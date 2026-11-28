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

## 6. Spesifikasi Perubahan Header Dashboard (2026-11-16)

### Masalah teridentifikasi
- Header menggandakan logo kiri dan kanan; identitas merek berulang tanpa fungsi.
- Judul memakai `transform: translateY(12.5px)` dan `padding-top`, sehingga alignment bergantung pada offset manual.
- Header memuat badge dan rincian teknis terlalu padat; hierarki informasi dashboard tidak jelas.

### Keputusan UI
- Pakai satu logo saja, di sisi kiri; hapus logo kanan.
- Gunakan badge netral untuk jumlah arsitektur; jangan pakai hijau atau indikator online tanpa health check operasional yang nyata.
- Susun header sebagai baris identitas: logo, nama produk dan deskripsi ringkas; status operasional jadi badge di sisi kanan pada layar lebar, turun ke baris berikutnya di layar sempit.
- Hapus transform/offset manual pada judul. Gunakan flex alignment konsisten, ukuran responsif, dan wrap tanpa overflow.
- Pindahkan rincian model/dataset dan metode teknis keluar dari hero header ke strip ringkasan/metrik di bawah header; jangan mengubah pipeline atau klaim status model yang belum diverifikasi.
- Pertahankan palet kopi dan kompatibilitas Streamlit; hindari selector DOM rapuh jika struktur komponen native cukup.

### Kriteria penerimaan
- Header hanya menampilkan satu logo.
- Judul, subtitle, dan status sejajar tanpa offset manual pada desktop; tetap terbaca dan tidak overflow pada viewport sempit.
- Header punya hirarki dashboard yang jelas dan tidak mengulang rincian teknis.
- Uji terkait UI lulus, `py_compile` dan `git diff --check` lulus.

### Checklist implementasi
- [ ] Revisi `ui/layout.py` sesuai keputusan UI di atas.
- [ ] Perbarui uji header untuk memastikan satu logo dan tidak ada offset judul.
- [ ] Jalankan uji UI dan pemeriksaan sintaks/diff.

## 8. Pembagian Tugas (Actionable Checklist)

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
   - ~~Brand Coffee Roast: `linear-gradient(135deg, #78350F 0%, #451A03 100%)`~~ — **usang, diganti §19.5** (header accent bar multi-hue).
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
- [x] `@banggapupa`: Re-audit keamanan DOM, sanitasi `html.escape()`, dan validasi layout style bleed.
- [x] `@dorowani`: Uji test suite, validasi browser runtime, ambil tangkapan layar verifikasi, dan lakukan git commit ke branch `main`.

---

## 9. Spesifikasi Perbaikan Visual Altair Chart, Jarak Bar Probabilitas, & Kerapian Estetika Komprehensif

### 9.1 Root Cause & Solusi Komponen Probabilitas (Altair)
1. **Label Kelas Terpotong/Hilang:**
   - *Penyebab:* Axis Y Altair/Vega-Lite default menerapkan clipping atau `labelLimit` sempit ketika dirender di Streamlit canvas dinamis, sehingga label teks kelas mutu ("Premium", "Peaberry", "Longberry", "Defect / Rusak") tersembunyi atau terpotong.
   - *Solusi:* Konfigurasi eksplisit `alt.Axis(labelLimit=250, labelPadding=12, labelColor="#0F172A", labelFontWeight=600, labelFontSize=12, domain=False, ticks=False, grid=False)`.
2. **Batang Grafik Menyatu Tanpa Celah (Zero Gap/Spacing):**
   - *Penyebab:* Band scale kategori Y tidak memiliki padding pemisah antarbundel bar, atau tinggi statis chart memadatkan bar height.
   - *Solusi:* Terapkan discrete band padding `scale=alt.Scale(paddingInner=0.35, paddingOuter=0.2)` pada axis Y atau atur `bandPaddingInner=0.35`. Tetapkan `height=alt.Step(32)` atau total `height=150` dengan bar height diskrit (16–18px) dan corner radius `cornerRadiusTopRight=5, cornerRadiusBottomRight=5`. Berikan celah bernapas yang terstruktur dan terukur.
3. **Penyajian Data & Tipografi Skor:**
   - Teks persentase probabilitas sejajar horizontal di kanan bar dengan font tabular `JetBrains Mono`, kontras tajam `#1E293B`, dan offset rapi (`dx=8`).

### 9.2 Standardisasi Kotak Pembungkus (Card & Container Wrappers)
1. **Bentuk & Radius:** Sudut kurva seragam `border-radius: 12px` untuk card utama, `8px` untuk badge dan chips.
2. **Border & Garis Tepi:** 1px solid border `#E2E8F0` dengan border-left accent khusus pada status card.
3. **Elevasi & Shadow:** 
   - Base state: `0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 2px 8px -1px rgba(15, 23, 42, 0.03)`.
   - Hover state: `0 4px 14px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)` dengan `transform: translateY(-2px)`.
4. **Gradien & Palet Kopi:**
   - ~~Gradient header & hero: `linear-gradient(135deg, #78350F 0%, #451A03 100%)`~~ — **usang, diganti §19.5**: `linear-gradient(90deg, #00D2B4, #7047EB, #FF3D60, #FFA048)`.
   - Soft card background: `linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)`.
   - Badge mutu terstandarisasi: Premium (Emerald `#059669`), Peaberry (Indigo `#2563EB`), Longberry (Amber `#D97706`), Defect (Rose `#DC2626`).

### 9.3 Actionable Checklist Tim
- [x] `@parewa`: Terapkan perbaikan visual Altair chart di `ui/components.py` (label terlihat jelas, celah/spacing bar proporsional), rapikan kotak container/cards di `ui/components.py`, `ui/layout.py`, dan `app.py`.
- [ ] `@banggapupa`: Audit keamanan DOM injection, XSS sanitization, dan zero style bleed.
- [ ] `@dorowani`: Jalankan unit & negative tests, verifikasi visual runtime browser di port 8501, simpan screenshot, lalu eksekusi git commit dan push ke `origin main`.
- [ ] `@padolo`: Standby untuk validasi sinkronisasi git dan kestabilan inference pipeline.

## 10. Spesifikasi Revisi Header & Hierarki Workspace (2026-11-16)

### Tujuan
Perbaiki baseline header dashboard tanpa mengubah inferensi atau klaim operasional. Judul “Arabica Vision AI” turun sedikit agar center vertikal terhadap logo. Identitas “Studio Unggah Inspeksi” ikut memakai baseline visual yang konsisten. Header saat ini terasa kosong karena hanya memuat logo, judul/subjudul, versi, dan hitungan model; tambahkan konteks produk dan navigasi/metadata yang sudah benar-benar tersedia, tanpa badge palsu atau data rekaan.

### Keputusan & batasan desain
- Ubah hanya header/layout terkait dan tesnya; pertahankan palet kopi, logo tunggal, responsive wrapping, dan konsistensi Streamlit.
- Kelompok logo dan blok judul dengan `align-items:center`; koreksi judul memakai alignment/flex, bukan offset `transform` yang rapuh.
- Tambahkan baris konteks header yang menghubungkan brand dengan ruang kerja “Studio Unggah Inspeksi”; sertakan deskripsi singkat alur upload → inspeksi → evaluasi, serta model sebagai metadata netral. Jangan menyiratkan model online/siap pakai tanpa health check.
- Cegah duplikasi bila nama studio sudah muncul pada konten utama; periksa `app.py` dan semua pemanggil header sebelum menetapkan teks.
- Pastikan elemen membungkus pada lebar kecil, kontras dan fokus semantik tetap terbaca, tidak overflow, tidak menambah ketergantungan eksternal, dan tidak menyisipkan HTML dinamis tanpa sanitasi.

### DoD / checklist
- [ ] Audit pemanggilan header dan judul studio di `app.py`, `ui/layout.py`, serta tes yang relevan.
- [ ] Implementasikan spesifikasi di atas; header tidak kosong, judul rata dengan center logo, studio inspeksi tertata konsisten.
- [ ] Tambah/perbarui tes struktural header untuk satu logo, teks studio, alignment tanpa transform manual, dan isi informasi yang tidak menyesatkan.
- [ ] Jalankan suite UI di environment proyek, `py_compile`, dan `git diff --check`; catat batasan runtime/visual bila ada.
- [ ] Review diff, baru commit/push `main` setelah semua pemeriksaan relevan lulus.

### Tugas tim
- `@parewa`: implementasi header dan regression test sesuai spesifikasi.
- `@padolo`: cek tidak ada perubahan pada kontrak/pipeline backend.
- `@banggapupa`: review klaim UI, sanitasi, responsive semantics.
- `@dorowani`: jalankan regression dan verifikasi render bila environment tersedia.

## 11. Spesifikasi Label Nilai Diagram Analisis Model Tunggal (2026-11-21)

### Keputusan tampilan
- Pada diagram probabilitas analisis model tunggal, tampilkan nilai setiap kelas sebagai label di sebelah kanan ujung batang masing-masing.
- Format nilai: persentase dengan tepat satu angka desimal (contoh: `42.7%`).
- Label berada di luar ujung batang namun tetap di dalam batas area plot/pembungkus diagram. Skala horizontal harus menyediakan ruang kanan yang cukup untuk nilai maksimum 100% beserta labelnya; jangan mengandalkan clipping atau menyembunyikan label.
- Pertahankan sumbu, judul, tick, grid, urutan kelas, dan warna diagram yang sudah ditetapkan. Uji spesifikasi chart wajib mencakup format persen, domain/ruang label, serta encoding axis.
- Pada lebar sempit, label tetap terbaca, tidak bertumpuk, dan tidak memicu overflow horizontal. Sesuaikan ruang diagram atau tata letak secara responsif tanpa menghilangkan nilai.

### DoD / checklist
- [ ] Implementasi label nilai di ujung kanan setiap batang dan tes regresi spesifikasi chart.
- [ ] Verifikasi visual diagram pada viewport lebar dan sempit; simpan bukti render.
- [ ] Jalankan suite test, cek runtime chart, `py_compile`, dan `git diff --check`.
- [ ] `@banggapupa` audit diff dan keamanan; `@dorowani` jalankan QA setelah approval.
- [ ] Commit/push hanya setelah audit dan QA menyetujui.

---

## 12. Spesifikasi Integrasi Multi-Split Data (60:20:20, 70:15:15, 80:10:10)

### 12.1 Latar Belakang & Tujuan
Menambahkan kapabilitas bagi pengguna untuk memilih salah satu dari 3 skenario rasio split dataset riset USK-Coffee:
1. `60:20:20` (60% Train, 20% Val, 20% Test) — Default
2. `70:15:15` (70% Train, 15% Val, 15% Test)
3. `80:10:10` (80% Train, 10% Val, 10% Test)

Setiap skenario memiliki bobot transfer learning CNN (`.pt`) dan pipeline SVM (`.joblib`) tersendiri yang telah dilatih secara independen.

### 12.2 Standar Penamaan & Struktur Berkas Artefak
Seluruh berkas model wajib mengikuti konvensi penamaan seragam:
```
models/
├── checkpoint/
│   ├── MobileNetV3-Small_60-20-20.pt
│   ├── ShuffleNetV2_60-20-20.pt
│   ├── EfficientNet-B0_60-20-20.pt
│   ├── MobileNetV3-Small_70-15-15.pt
│   ├── ShuffleNetV2_70-15-15.pt
│   ├── EfficientNet-B0_70-15-15.pt
│   ├── MobileNetV3-Small_80-10-10.pt
│   ├── ShuffleNetV2_80-10-10.pt
│   └── EfficientNet-B0_80-10-10.pt
└── svm/
    ├── MobileNetV3-Small_60-20-20_svm.joblib
    ├── ShuffleNetV2_60-20-20_svm.joblib
    ├── EfficientNet-B0_60-20-20_svm.joblib
    ├── MobileNetV3-Small_70-15-15_svm.joblib
    ├── ShuffleNetV2_70-15-15_svm.joblib
    ├── EfficientNet-B0_70-15-15_svm.joblib
    ├── MobileNetV3-Small_80-10-10_svm.joblib
    ├── ShuffleNetV2_80-10-10_svm.joblib
    └── EfficientNet-B0_80-10-10_svm.joblib
```
Sumber berkas: `/Users/agusfarhan/Downloads/hasil_eksperimen/`. Seluruh berkas berukuran $\le 53\text{ MB}$ (aman di bawah batas 100 MB per file GitHub).

### 12.3 Kontrak Data & Domain (`core/constants.py`, `core/schemas.py`)
1. **Whitelist Tuple:**
   ```python
   ALLOWED_SPLITS = ("60-20-20", "70-15-15", "80-10-10")
   DEFAULT_SPLIT = "60-20-20"
   SPLIT_DISPLAY_NAMES = {
       "60-20-20": "60:20:20 (Standar Skripsi)",
       "70-15-15": "70:15:15 (Eksperimen 2)",
       "80-10-10": "80:10:10 (Eksperimen 3)",
   }
   ```
2. **Path Traversal Guard (CWE-22):**
   Fungsi pembacaan model wajib memvalidasi input split terhadap `ALLOWED_SPLITS`. Nilai di luar whitelist ditolak seketika (raise `ValueError`). Dilarang memformat langsung user input ke path tanpa sanitasi.
3. **Domain Exception:**
   ```python
   class ModelArtifactNotFoundError(FileNotFoundError):
       """Dilempar saat checkpoint atau SVM joblib tidak ditemukan di disk."""
   ```

### 12.4 Spesifikasi Backend Service (`services/`)
1. **`services/model_loader.py`:**
   - Signature: `load_cnn_backbone(model_name: str, split: str = DEFAULT_SPLIT)`
   - Signature: `load_svm_pipeline(model_name: str, split: str = DEFAULT_SPLIT)`
   - Caching: `@st.cache_resource` memanfaatkan kombinasi `(model_name, split)` sebagai cache key otomatis.
   - Pengecekan file via `os.path.isfile()`. Jika berkas belum tersedia, lempar `ModelArtifactNotFoundError`.
2. **`services/predictor.py`:**
   - Signature: `predict_single_model(image: Image.Image, model_name: str, split: str = DEFAULT_SPLIT)`
   - Signature: `predict_all_models(image: Image.Image, split: str = DEFAULT_SPLIT)`
   - Hasil inferensi menyertakan metadata `split_ratio` pada `ModelInferenceOutput`.

### 12.5 Spesifikasi Antarmuka UI/UX (`ui/`, `app.py`)
1. **Widget Pemilihan Split:**
   - Ditempatkan di Sidebar (atau bagian atas Workspace Studio) secara elegan menggunakan `st.selectbox` atau `st.radio`.
   - Label: `"Pilih Skenario Split Data:"`
   - Pilihan: `"60:20:20"`, `"70:15:15"`, `"80:10:10"`.
2. **Responsivitas Komponen:**
   - KPI metrics bar memperbarui card "Skenario Riset" secara dinamis sesuai split yang aktif.
   - Tab "Spesifikasi Riset & Arsitektur" menampilkan deskripsi skenario yang sedang aktif.
   - State Handling: Jika split yang dipilih belum memiliki berkas model, tampilkan pesan ramah (Empty State / Error State) tanpa membocorkan path teknis server (CWE-209).

### 12.6 Actionable Checklist & Pembagian Tugas
- [ ] `@padolo`:
  1. Salin berkas model dari `/Users/agusfarhan/Downloads/hasil_eksperimen/` ke `models/checkpoint/` dan `models/svm/`.
  2. Implementasi whitelist `ALLOWED_SPLITS` di `core/constants.py`.
  3. Update `services/model_loader.py` & `services/predictor.py` untuk mendukung parameter `split`.
- [ ] `@parewa`:
  1. Tambahkan selector skenario split di UI (`app.py` / `ui/layout.py` / `ui/components.py`).
  2. Sinkronkan tampilan KPI metrics bar agar dinamis membaca split terpilih.
- [ ] `@banggapupa`:
  1. Audit keamanan path traversal (CWE-22) dan pencegahan credential/path leak (CWE-209).
  2. Verifikasi serialisasi aman dan validasi memory footprint 3 model x 3 split.
- [ ] `@dorowani`:
  1. Tambahkan unit test di `tests/test_model_loader.py` dan `tests/test_pipeline.py` untuk assert keberadaan dan fungsionalitas seluruh split.
  2. Jalankan `pytest`, `compileall`, verifikasi browser runtime, dan laporkan bukti QA.


---

## 13. Spesifikasi Komponen Distribusi Probabilitas Kompak (Kartu Perbandingan Multi-Model) — 2026-11-26

### 13.1 Masalah teridentifikasi
- `ui/components.py:508` memaksa `properties(height=150)` dan `render_model_result_card` (`:619-620`) memakainya di dalam `render_comparison_section` (`:696-699`) yang membagi layar ke 3 kolom. Tiap chart hanya mendapat ~1/3 lebar.
- `ui/components.py:409` + `:480-491` menggabung nama kelas dan persentase menjadi satu string `"Kelas · 98.2%"` (`LabelDiagram`) dengan `dx=8` dan `chart_scale` domain `[0, 122]`. Runway label hanya ~22% lebar plot, sehingga "Specialty Grade" / "Defect" + persen bertabrakan atau terpotong.
- Kesimpulan: endpoint-text Altair tidak layak dipakai pada konteks side-by-side 3 kolom.

### 13.2 Keputusan arsitektur
- **Komponen terpisah, bukan varian parameter.** Fungsi baru `render_compact_probability_rows(probabilities: list) -> None` di `ui/components.py`, diletakkan tepat setelah `render_probability_chart`.
- `render_probability_chart` **tidak disentuh**. Jalur Analisis Model Tunggal (lebar penuh) tetap memakai Altair + `LabelDiagram` + `chart_scale [0, 122]` sesuai Spesifikasi §11. Alasan: memisahkan jalur menghilangkan risiko regresi pada jalur full-width, dan tidak ada kebutuhan berbagi kode yang sepadan.
- Batas modul: UI presentasi saja. Tidak ada perubahan kontrak data di `core/` maupun `services/`; payload `probabilities` yang ada (`label`, `display_name`, `score`) sudah cukup.

### 13.3 Kontrak fungsi
- Signature: `render_compact_probability_rows(probabilities: list) -> None`
- Input: list berisi `dict` **atau** objek dengan atribut `label`, `display_name`, `score` (dua bentuk diterima, sama seperti `render_probability_chart`).
- Resolusi nama: `disp = item.get("display_name") or item.get("label") or ""` (dua bentuk akses), lalu `str()`. Nilai `None` pada key yang ada **tidak boleh** menghasilkan string `"None"`.
- Urutan: descending berdasarkan `score`.
- Key warna: `str(label).strip().lower()`, lalu `CLASS_COLORS.get(key, "#4E36E2")`. Jangan `KeyError` untuk kelas tak dikenal. (Fallback diselaraskan ke brand violet §19.5 per `ui/components.py:513`; nilai `#78350F` usang dan dilarang kembali.)
- Tampilan: HTML CSS grid satu baris per kelas, `grid-template-columns: minmax(0, 1fr) 5.5rem 3.4rem`; tinggi bar 16px; kolom persen `text-align: right; font-variant-numeric: tabular-nums`. Tidak ada `height=150` hardcode, tidak ada `st.altair_chart`.

### 13.4 Keamanan wajib (CWE-79 / CSS injection)
- `display_name` **wajib** lewat `html.escape()` sebelum masuk markup.
- `label_key` **dilarang** masuk markup dalam bentuk apa pun (tidak sebagai atribut, tidak sebagai nama class, tidak sebagai `data-*`). Nilai itu hanya boleh dipakai sebagai argumen `CLASS_COLORS.get()`.
- `score` diperlakukan sebagai untrusted karena masuk ke nilai CSS: `w = 0.0 if not math.isfinite(score) else min(max(score, 0.0), 1.0)`; `width` memakai `w`, bukan `score` mentah. `NaN` dan `score > 1` tidak boleh merusak layout.
- Markup harus berupa **satu string satu baris** sebelum `_clean_html`, karena `_clean_html` (`ui/components.py:86-88`) menggabung baris tanpa separator. f-string multi-baris dengan atribut terpotong akan merusak tag.

### 13.5 Call site & kompatibilitas
- `render_model_result_card` baris 620: `render_probability_chart(probs)` diganti `render_compact_probability_rows(probs)`. Tidak ada perubahan lain di fungsi itu.
- Bentuk `st.columns(len(results))` di `render_comparison_section` **dipertahankan** (int, bukan list) agar mock test `tests/test_ui_components.py:161-163` tidak pecah.
- **Mobile: tidak ada percabangan stacking kustom.** Kartu mengandalkan perilaku stack native Streamlit. Renderer wajib tetap aman pada lebar sempit (nama `min-width: 0` + `overflow-wrap: anywhere`, kolom persen lebar tetap) tanpa mengubah struktur kolom.

### 13.6 Kontrak test (wajib ikut dalam diff yang sama)
- `tests/test_ui_components.py:143-156` (`test_render_model_result_card`): target patch diubah ke `ui.components.render_compact_probability_rows`.
- Test baru `render_compact_probability_rows`: urutan descending; `display_name` berisi `<script>` ter-escape; `display_name=None` jatuh ke `label`; kelas tak dikenal memakai fallback `#4E36E2`; `score=NaN` → lebar 0; `score=1.5` → clamp 100%.
- `test_render_probability_chart` (`:104-141`) **tidak boleh berubah**.

### 13.7 Kriteria penerimaan (DoD)
- [ ] Komponen baru ada sesuai §13.3, `render_probability_chart` nol perubahan baris.
- [ ] Tidak ada overlap label vs kolom persen pada viewport 1280 dan 1024 (`labelRect.right <= percentRect.left + 1`).
- [ ] Tidak ada truncation (`scrollWidth <= clientWidth`) pada sel nama kelas.
- [ ] `font-variant-numeric: tabular-nums` benar-benar aktif (`getComputedStyle`).
- [ ] Tidak ada error konsol baru setelah render 3 kartu + pergantian model berulang.
- [ ] Jalur Analisis Model Tunggal identik dengan baseline commit `8052ddc` (diff screenshot).
- [ ] `pytest`, `compileall`, `git diff --check` lulus; `@banggapupa` APPROVED; `@dorowani` lampirkan bukti.
- [ ] Commit/push hanya setelah audit dan QA menyetujui.

### 13.8 Pembagian tugas
- `@parewa`: implementasi `render_compact_probability_rows`, tukar call site, tulis test §13.6. Skill: `impeccable`, `frontend-design`. Dilarang menyentuh `render_probability_chart`.
- `@padolo`: konfirmasi payload `probabilities` ketiga model membawa `display_name` (sudah terverifikasi `core/schemas.py:11`, `services/predictor.py:70`); tidak ada pekerjaan kode.
- `@banggapupa`: audit escaping, larangan `label_key` di markup, clamp skor, dan konsistensi kontrak test.
- `@dorowani`: eksekusi 5 gate QA + gate #6 baseline `8052ddc`, lampirkan log dan screenshot.


---

## 15. Spesifikasi Penyelarasan Warna Kartu KPI dengan Ikon/Logo — 2026-11-26

> **SUPERSEDED oleh §19.** Palet kartu KPI aktif = §19.2 (gradien `115deg`). Section ini disimpan sebagai riwayat keputusan.

### 15.1 Latar Belakang & Kebutuhan
- Pengguna meminta agar masing-masing dari keempat card metrik pada bar KPI atas disesuaikan warnanya dengan warna ikon/logo masing-masing.
- Desain sebelumnya menggunakan latar putih/abu-abu seragam. Pembaruan ini menerapkan skema warna tematik berbasis gradien elegan, border beraksen, serta tipografi kontras tinggi yang memenuhi standar aksesibilitas WCAG AAA (rasio kontras ≥ 7.0:1 untuk seluruh ukuran teks).

### 15.2 Design Token & Kontras (WCAG AAA)
1. **Card 1 — Engine Pipeline (Emerald / `cpu`):**
   - Background: `linear-gradient(180deg, #F0FDF4 0%, #ECFDF5 100%)`
   - Border: `1px solid #A7F3D0`
   - Badge Ikon: Background `#D1FAE5`, color `#047857`
   - Label & Subtitle: `#065F46` (Rasio kontras 7.6:1 terhadap `#F0FDF4`, lolos WCAG AAA)
   - Value Text: `#064E3B` (Rasio kontras 11.4:1 terhadap `#F0FDF4`, lolos WCAG AAA)

2. **Card 2 — Skenario Riset (Amber / `database`):**
   - Background: `linear-gradient(180deg, #FFFDF5 0%, #FFFBEB 100%)`
   - Border: `1px solid #FDE68A`
   - Badge Ikon: Background `#FEF3C7`, color `#B45309`
   - Label & Subtitle: `#78350F` (Rasio kontras 10.2:1 terhadap `#FFFDF5`, lolos WCAG AAA)
   - Value Text: `#78350F` (Rasio kontras 10.2:1 terhadap `#FFFDF5`, lolos WCAG AAA)

3. **Card 3 — Kelas Mutu (Blue / `target`):**
   - Background: `linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%)`
   - Border: `1px solid #BFDBFE`
   - Badge Ikon: Background `#DBEAFE`, color `#1D4ED8`
   - Label & Subtitle: `#1E40AF` (Rasio kontras 8.6:1 terhadap `#EFF6FF`, lolos WCAG AAA)
   - Value Text: `#1E3A8A` (Rasio kontras 12.8:1 terhadap `#EFF6FF`, lolos WCAG AAA)

4. **Card 4 — Protokol Uji (Purple / `zap`):**
   - Background: `linear-gradient(180deg, #FAF5FF 0%, #F5F3FF 100%)`
   - Border: `1px solid #DDD6FE`
   - Badge Ikon: Background `#F3E8FF`, color `#7E22CE`
   - Label & Subtitle: `#6B21A8` (Rasio kontras 8.4:1 terhadap `#F5F3FF`, lolos WCAG AAA)
   - Value Text: `#581C87` (Rasio kontras 12.5:1 terhadap `#F5F3FF`, lolos WCAG AAA)

### 15.3 Panduan Implementasi & Keamanan (`ui/components.py`)
- Modifikasi fungsi `render_kpi_metrics_bar`.
- Tetap gunakan `safe_split_label = html.escape(str(current_split).replace("-", ":"))` untuk pencegahan XSS (CWE-79).
- Pertahankan struktur kelas `.kpi-split-card` dan positioning popover split agar fungsionalitas interaktif tetap utuh.
- Teks konten utama (seperti `"Engine Pipeline"`, `"Skenario Riset"`, `"Kelas Mutu"`, `"Protokol Uji"`) wajib dipertahankan presisi agar kontrak pengujian `test_render_kpi_metrics_bar_dynamic_split` tetap hijau.

### 15.4 Kriteria Penerimaan (DoD)
- [ ] Keempat card memiliki warna latar, border, dan teks selaras dengan warna logonya sesuai token §15.2.
- [ ] Seluruh warna teks lolos pengujian rasio kontras WCAG AAA (≥ 7.0:1).
- [ ] Popover dan seleksi split skenario tetap berfungsi sempurna.
- [ ] `py_compile`, `compileall`, dan `git diff --check` lulus tanpa error.
- [ ] Seluruh unit test (44 passed) lulus 100%.
- [ ] Disetujui (APPROVED) oleh `@banggapupa` dan lolos pengujian QA `@dorowani`.

### 15.5 Pembagian Tugas
- `@parewa`: Implementasi styling warna di `render_kpi_metrics_bar`.
- `@banggapupa`: Audit kepatuhan token WCAG AAA, sanitasi XSS, dan kompatibilitas sintaksis Python 3.9.
- `@dorowani`: Uji visual, ukur rasio kontras DOM melalui CDP, verifikasi popover, dan jalankan seluruh suite pengujian.
- `@padolo`: Standby.


### 15.6 Known Limitation — Popover Split tanpa `aria-expanded`/`aria-haspopup` (WCAG 4.1.2 ditangguhkan)

- **Status:** Diketahui, tidak diperbaiki pada rilis ini. Bukan cacat implementasi §15.
- **Temuan:** Tombol `st.popover` pada card "Skenario Riset" tidak mengekspos `aria-expanded` maupun `aria-haspopup`, sehingga status buka/tutup tidak diumumkan ke screen reader (WCAG 4.1.2 Name, Role, Value).
- **Akar masalah (terverifikasi, bukan asumsi):** Streamlit `1.50.0`, bundel `static/js/index.6xX1278W.js`. Node `data-testid="stPopoverButton"` dirender lewat `BaseButton` dengan props `kind`, `size`, `disabled`, `containerWidth`, `onClick`, `children` — tidak ada `aria-expanded`/`aria-haspopup` pada segmen tersebut. Atribut itu hanya muncul pada komponen lain (tooltip, selectbox `aria-haspopup="listbox"`). Jadi keterbatasan framework, bukan kode aplikasi.
- **Keputusan arsitektur:** **Tidak** menambal via DOM mutation / selector rapuh. Alasan: kebijakan §7 melarang selector DOM rapuh bila komponen native cukup, dan patch DOM pada komponen internal Streamlit akan pecah pada upgrade minor. Nama aksesibel tombol sudah benar lewat `visually-hidden` label (`ui/layout.py:286`, commit `8052ddc`), sehingga pengguna screen reader tetap dapat mengoperasikan kontrol; yang hilang hanya state announcement.
- **Rencana penutupan:** Bila aksesibilitas penuh dibutuhkan, ganti `st.popover` dengan kontrol native yang mengekspos state (`st.radio` / `st.selectbox` inline di card), atau tunggu Streamlit menambahkan atribut tersebut. Perubahan itu wajib lewat card terpisah dengan spec sendiri, bukan disisipkan ke §15.


## 16. Spesifikasi Desain Warna Tegas (Solid Rich) Kartu KPI — 2026-11-27

> **SUPERSEDED oleh §19.** Kartu KPI saat ini memakai gradien `115deg` §19.2, bukan solid rich.

### 16.1 Latar Belakang & Masalah
- Pengguna meminta agar 4 kartu KPI atas tidak memakai warna transparan/pucat ("jangan gunakan warna transparant, buatkan agar warna tegas dan sesuai, sisanya sesuaikan").
- Latar gradien pastel lama tampak pudar dan menyerupai transparansi overlay di layar cerah.
- Solusi: Latar solid berbobot (deep saturated jewel tone) 100% tanpa alpha/transparansi, teks putih murni kontras tinggi, border tegas, lolos WCAG AAA.

### 16.2 Design Token Warna Tegas & Kontras WCAG AAA
1. **Card 1 — Engine Pipeline (Emerald):**
   - Background: `#065F46` (Solid Emerald-800, tanpa gradien/alpha)
   - Border: `1px solid #047857`
   - Badge Ikon: Background `#047857`, ikon `#A7F3D0`
   - Label: `#A7F3D0` (font-weight 700, kontras 8.5:1, WCAG AAA)
   - Value: `#FFFFFF` (font-weight 800, kontras 9.2:1, WCAG AAA)
   - Subtitle: `#D1FAE5` (kontras 10.4:1, WCAG AAA)

2. **Card 2 — Skenario Riset (Warm Amber):**
   - Background: `#92400E` (Solid Amber-800, tanpa gradien/alpha)
   - Border: `1px solid #B45309`
   - Badge Ikon: Background `#B45309`, ikon `#FDE68A`
   - Label: `#FDE68A` (font-weight 700, kontras 7.8:1, WCAG AAA)
   - Value: `#FFFFFF` (font-weight 800, kontras 8.2:1, WCAG AAA)
   - Subtitle: `#FEF3C7` (kontras 10.5:1, WCAG AAA)

3. **Card 3 — Kelas Mutu (Sapphire Blue):**
   - Background: `#1E40AF` (Solid Blue-800, tanpa gradien/alpha)
   - Border: `1px solid #2563EB`
   - Badge Ikon: Background `#1D4ED8`, ikon `#BFDBFE`
   - Label: `#BFDBFE` (font-weight 700, kontras 8.1:1, WCAG AAA)
   - Value: `#FFFFFF` (font-weight 800, kontras 8.8:1, WCAG AAA)
   - Subtitle: `#DBEAFE` (kontras 10.9:1, WCAG AAA)

4. **Card 4 — Protokol Uji (Royal Purple):**
   - Background: `#6B21A8` (Solid Purple-800, tanpa gradien/alpha)
   - Border: `1px solid #7E22CE`
   - Badge Ikon: Background `#7E22CE`, ikon `#DDD6FE`
   - Label: `#DDD6FE` (font-weight 700, kontras 8.0:1, WCAG AAA)
   - Value: `#FFFFFF` (font-weight 800, kontras 8.6:1, WCAG AAA)
   - Subtitle: `#F3E8FF` (kontras 10.6:1, WCAG AAA)

### 16.3 Kriteria Penerimaan (DoD)
- [ ] 4 kartu memakai background solid hex (tanpa `rgba()`, `transparent`, atau gradien pudar).
- [ ] Rasio kontras teks/value terhadap background lolos WCAG AAA (≥ 7.0:1).
- [ ] Semua fungsionalitas popover `kpi_split_selector` tetap utuh.
- [ ] Suite pengujian 45 test tetap hijau (`tests/test_ui_components.py`).
- [ ] Lolos audit `@banggapupa` dan QA visual `@dorowani`.

### 16.4 Pembagian Tugas
- `@parewa`: Update styling `render_kpi_metrics_bar` di `ui/components.py` sesuai token §16.2.
- `@banggapupa`: Audit kepatuhan token WCAG AAA dan sanitasi XSS.
- `@dorowani`: Verifikasi rendering DOM, rasio kontras, dan suite test.


## 17. Spesifikasi Desain Vibrant Fintech/Crypto Gradient Kartu KPI — 2026-11-27

> **SUPERSEDED oleh §19.** Token §17 (#047857/#B91C1C/#075985/#4338CA) tidak lagi dipakai.

### 17.1 Latar Belakang & Inspirasi Desain
- Pengguna menyediakan gambar referensi antarmuka dashboard kartu crypto dengan gradien tegas dan berdaya pendar elegan (Coral Flame, Teal Mint, Royal Indigo, Ocean Sky).
- Pengguna meminta agar model warna ini diterapkan dan arsitek menentukan paduan terbaik.
- Gradien tegas bukan gradien pucat/transparan: menggunakan stop warna bersaturasi tinggi, dengan kontras teks putih `#FFFFFF` ≥ 4.5:1 (WCAG AA) pada seluruh titik spektrum gradien.

### 17.2 Design Token & Kontras (Vibrant Fintech Gradient)
1. **Card 1 — Engine Pipeline (Vivid Teal Mint):**
   - Background: `linear-gradient(135deg, #047857 0%, #0F766E 100%)`
   - Border: `1px solid rgba(255, 255, 255, 0.20)`
   - Badge Ikon: Background `rgba(255, 255, 255, 0.20)`, color `#FFFFFF`
   - Label: `rgba(255, 255, 255, 0.88)` (uppercase, font-weight 700)
   - Value: `#FFFFFF` (font-weight 800, kontras: start 5.48:1, end 5.47:1 — WCAG AA)
   - Subtitle: `rgba(255, 255, 255, 0.90)`
   - Shadow: `0 4px 16px -2px rgba(4, 120, 87, 0.25)`

2. **Card 2 — Skenario Riset (Warm Coral Roast):**
   - Background: `linear-gradient(135deg, #B91C1C 0%, #C22D16 100%)`
   - Border: `1px solid rgba(255, 255, 255, 0.20)`
   - Badge Ikon: Background `rgba(255, 255, 255, 0.20)`, color `#FFFFFF`
   - Label: `rgba(255, 255, 255, 0.88)` (uppercase, font-weight 700, kontras: 4.72:1 — WCAG AA)
   - Value: `#FFFFFF` (font-weight 800, kontras: start 6.47:1, end 5.71:1 — WCAG AA)
   - Subtitle: `rgba(255, 255, 255, 0.90)` (kontras: 4.88:1 — WCAG AA)
   - Shadow: `0 4px 16px -2px rgba(185, 28, 28, 0.25)`

3. **Card 3 — Kelas Mutu (Ocean Sky Blue):**
   - Background: `linear-gradient(135deg, #075985 0%, #1D4ED8 100%)`
   - Border: `1px solid rgba(255, 255, 255, 0.20)`
   - Badge Ikon: Background `rgba(255, 255, 255, 0.20)`, color `#FFFFFF`
   - Label: `rgba(255, 255, 255, 0.88)` (uppercase, font-weight 700, kontras: 5.56:1 — WCAG AA)
   - Value: `#FFFFFF` (font-weight 800, kontras: start 7.56:1, end 6.70:1 — WCAG AA)
   - Subtitle: `rgba(255, 255, 255, 0.90)` (kontras: 5.74:1 — WCAG AA)
   - Shadow: `0 4px 16px -2px rgba(29, 78, 216, 0.25)`

4. **Card 4 — Protokol Uji (Royal Indigo Violet):**
   - Background: `linear-gradient(135deg, #4338CA 0%, #7C3AED 100%)`
   - Border: `1px solid rgba(255, 255, 255, 0.20)`
   - Badge Ikon: Background `rgba(255, 255, 255, 0.20)`, color `#FFFFFF`
   - Label: `rgba(255, 255, 255, 0.88)` (uppercase, font-weight 700)
   - Value: `#FFFFFF` (font-weight 800, kontras: start 7.90:1, end 5.70:1 — WCAG AA)
   - Subtitle: `rgba(255, 255, 255, 0.90)`
   - Shadow: `0 4px 16px -2px rgba(99, 102, 241, 0.25)`

### 17.3 Kriteria Penerimaan (DoD)
- [ ] 4 kartu memakai gradien tegas 135deg sesuai §17.2, bukan gradien pucat.
- [ ] Rasio kontras teks/value `#FFFFFF` terhadap seluruh titik stop gradien ≥ 4.5:1 (WCAG AA).
- [ ] Popover split di Card 2 tetap berfungsi normal.
- [ ] Unit tests 52 test tetap hijau.
- [ ] Lolos audit `@banggapupa` dan QA visual `@dorowani`.

### 17.4 Pembagian Tugas
- `@parewa`: Terapkan token gradien §17.2 di `render_kpi_metrics_bar` (`ui/components.py`) dan perbarui test UI.
- `@banggapupa`: Audit titik luminansi terlemah & sanitasi.
- `@dorowani`: Verifikasi DOM live dan ukur kontras visual.

---

## 18. Spesifikasi Penyelarasan Palet Gradien Referensi Kripto — 2026-11-27

### 18.1 Latar Belakang
- Pengguna menolak §17 karena hue tidak sesuai citra referensi dashboard kripto (BTC/ETH/LTC/XRP).
- Tujuan: selaraskan **hue** tiap kartu dengan referensi, bukan sekadar gelapkan seluruh gradien.
- Status: **SUPERSEDED oleh §19.** Token §18 gagal WCAG AA pada beberapa stop (mis. `#0E7490` Label 4.52:1 lolos, namun pass berikutnya tidak stabil) dan vibransi terlalu kusam. §18 dipertahankan sebagai catatan riwayat keputusan.

### 18.2 Token §18 (Riwayat, Jangan Dipakai untuk Implementasi Baru)
| Kartu | Gradient 135deg | Glow |
|---|---|---|
| Card 1 — Engine Pipeline (BTC) | `#0E7490` → `#1D4ED8` | `rgba(14, 116, 144, 0.30)` |
| Card 2 — Skenario Riset (ETH) | `#6D28D9` → `#BE185D` | `rgba(109, 40, 217, 0.30)` |
| Card 3 — Kelas Mutu (LTC) | `#B43403` → `#BE123C` | `rgba(180, 52, 3, 0.30)` |
| Card 4 — Protokol Uji (XRP) | `#3730A3` → `#6D28D9` | `rgba(55, 48, 163, 0.30)` |

Alasan ditolak: stop dikunci terlalu gelap demi angka kontras, sehingga *luminance delta* antar-stop menyusut dan gradien kehilangan vibransi referensi.

---

## 19. Spesifikasi Harmonisasi Vibrant Crypto (High Dynamic Range, WCAG-Safe) — 2026-11-27

### 19.1 Prinsip
1. **Hue referensi dipertahankan.** Penyesuaian hanya pada *lightness* sampai teks putih lolos ambang, bukan menyeragamkan kartu jadi gelap/kusam.
2. **Dynamic range dijaga.** Setiap kartu tetap punya arah terang → saturated, dengan sudut `115deg` agar pendar mengalir diagonal seperti referensi.
3. **`text-shadow` BUKAN remedi WCAG SC 1.4.3.** Rasio kontras dihitung murni warna teks vs warna latar; bayangan diabaikan oleh auditor. `text-shadow` hanya *enhancement* visual, tidak boleh dipakai untuk mengklaim PASS.
4. **Solid text.** Label/subtitle kartu wajib `#FFFFFF` solid — dilarang `rgba(255, 255, 255, 0.88)` / `0.90` karena menurunkan rasio efektif.

### 19.2 Token Final 4 Kartu KPI (commit `b125c0e`)
| Kartu | Gradient 115deg | Glow Shadow | Kontras Stop 1 | Kontras Stop 2 |
|---|---|---|---|---|
| Card 1 — Engine Pipeline (BTC) | `#008572` → `#0071EF` | `0 8px 24px -4px rgba(0, 133, 114, 0.40)` | 4.57:1 PASS AA | 4.56:1 PASS AA |
| Card 2 — Skenario Riset (ETH) | `#7047EB` → `#E50B6A` | `0 8px 24px -4px rgba(112, 71, 235, 0.40)` | 5.54:1 PASS AA | 4.58:1 PASS AA |
| Card 3 — Kelas Mutu (LTC) | `#BC5A00` → `#EC002B` | `0 8px 24px -4px rgba(188, 90, 0, 0.40)` | 4.56:1 PASS AA | 4.56:1 PASS AA |
| Card 4 — Protokol Uji (XRP) | `#4E36E2` → `#7B55FF` | `0 8px 24px -4px rgba(78, 54, 226, 0.40)` | 7.12:1 PASS AA | 4.58:1 PASS AA |

Hue terverifikasi: 171°, 212°, 255°, 334°, 29°, 349°, 248°, 253°.

**Tipografi kartu (wajib):**
- Value: `#FFFFFF`, `font-weight: 800`, `letter-spacing: -0.02em`.
- Label & Subtitle: `#FFFFFF` solid, `font-weight: 700`, `text-shadow: 0 1px 3px rgba(0, 0, 0, 0.45)` (enhancement saja).
- Icon box: `background: rgba(255, 255, 255, 0.22)`, `color: #FFFFFF`.
- Border: `1px solid rgba(255, 255, 255, 0.20)`.

### 19.3 Lantai Review Kontras & Aturan Container
- Titik terlemah §19 = **4.56:1**, hanya 0.06 di atas ambang 4.5:1.
- **Stop baru wajib ≥ 4.8:1** agar satu tweak hue di masa depan tidak langsung menjatuhkan build ke FAIL.
- **Grandfathered (tercatat, jangan diubah tanpa spec baru):** 4 stop kartu KPI `4.56:1`; chip `peaberry #2563EB` `4.75:1`. Keduanya PASS AA, di bawah lantai 4.8:1, dan menaikkannya menggeser hue referensi.
- **Larangan `#64748B` (slate-500) di atas container `#F1F5F9`.** Terukur `4.34:1` → FAIL SC 1.4.3 (2 situs: pill `arch_pill` & pill arsitektur kartu komparasi). Bukan "worst-case teoretis" — bg dibaca langsung dari elemen yang sama. Di atas `#FFFFFF` `4.76:1`, `#F8FAFC` `4.55:1` PASS tapi margin rapuh. **Setiap container tint baru wajib diuji terhadap `#64748B` sebelum dipakai**; bila tint lebih gelap dari `#F8FAFC`, ganti teks ke `#475569` (`6.92:1` di `#F1F5F9`).
- **Ambang per jenis objek:** teks normal `≥ 4.5:1` (SC 1.4.3); glyph ikon SVG, dot status, border aksen `≥ 3:1` (SC 1.4.11). Glyph `3.60:1` **bukan** blocker teks. Jangan mengunci ambang 4.5:1 pada objek grafis.
- **Di luar cakupan WCAG teks:** `#CBD5E1` separator `•` (`1.35:1`) dan `#94A3B8` footer/app caption (`2.33:1`) — hairline dekoratif, tidak membawa informasi.

### 19.4 Token Chip Kelas Prediksi (Blocker 1 `@banggapupa`)
`CLASS_COLORS` vs `CLASS_LIGHT_BG` wajib lolos ≥ 4.5:1:

| Kelas | Teks (lama → baru) | BG | Rasio |
|---|---|---|---|
| defect | `#E11D48` → `#BE123C` | `#FFF1F2` | 4.28 → **5.72:1** |
| longberry | `#D97706` → `#B45309` | `#FFFBEB` | 3.07 → **4.84:1** |
| premium | `#059669` → `#047857` | `#ECFDF5` | 3.58 → **5.21:1** |
| peaberry | `#2563EB` (tetap) | `#EFF6FF` | 4.75:1 PASS |

Hue amber Longberry **dipertahankan** (semantik kelas, bukan chrome UI) — argumen "biarkan karena semantik" tidak berlaku selama rasio < 4.5:1.

**Cakupan token ini bukan hanya dict `CLASS_COLORS`.** Semua `color:` hardcoded di template HTML wajib memakai token §19.4 yang sama:
- `render_visual_dictionary_deck` — badge "Valid RGB", badge "Grade 1 Utama", banner status, body kartu kelas.
- `render_comparison_card` — body kartu gagal, badge "Tolak Ekspor", pill `arch_pill`.
- Stepper upload — label & icon "Langkah 1/2/3".
- Nilai lama dilarang sebagai warna teks: `#E11D48`, `#059669`, `#DC2626`, `#D97706` → ganti `#BE123C` / `#047857` / `#B45309`.
- **Non-text KEEP** (ambang 3:1 SC 1.4.11, sudah PASS): dot status, `border-left`, `border-top`, `background` tint, atribut SVG `fill`/`stroke`. Tripwire wajib men-strip deklarasi non-text sebelum assert — `assertNotIn` polos salah.

### 19.5 Harmonisasi Elemen Non-Kartu (Hapus Palet Cokelat Usang)
1. Header accent bar — `linear-gradient(90deg, #00D2B4 0%, #7047EB 33%, #FF3D60 66%, #FFA048 100%)`. Dekoratif hairline 3px: **di luar cakupan SC 1.4.11**, dilarang membawa informasi status.
2. Version badge header — `background: rgba(112, 71, 235, 0.08)`, `color: #5B32D9` (6.45:1), `border: 1px solid rgba(112, 71, 235, 0.25)`.
3. Subteks header — `color: #475569`, icon coffee `#7047EB`.
4. Sidebar logo icon box — `linear-gradient(135deg, #4E36E2 0%, #7047EB 100%)`, drop-shadow `rgba(112, 71, 235, 0.25)`.
5. Stepper "Langkah 1", icon upload, model header icon, fallback class color — `#4E36E2`.
6. Model header icon kartu komparasi — Model 1 `#0078FF`, Model 2 `#7047EB`, Model 3 `#FF3D60`.
7. Chevron popover SVG `%23D97706` → `%23E50B6A`; uploader hover/focus ring `rgba(146, 64, 14, …)` → `rgba(112, 71, 235, …)`.
8. Tabel status banner & gallery icon `app.py` — violet.

**Dikecualikan:** `CLASS_LIGHT_BG["longberry"] = #FFFBEB` — tint latar chip semantik kelas, bukan chrome. Kontras teksnya dikunci via §19.4.

### 19.6 Kriteria Penerimaan (DoD)
- [ ] 4 kartu memakai token §19.2 tepat (`115deg`, pasangan hex & glow identik).
- [ ] Seluruh label/subtitle `#FFFFFF` solid — nol `rgba(255, 255, 255, 0.88|0.90)`.
- [ ] 8 stop kontras ≥ 4.5:1; target lantai ≥ 4.8:1 untuk stop baru.
- [ ] `CLASS_COLORS` chip lolos WCAG AA (§19.4).
- [ ] Test mengunci: assertNotIn `rgba(255, 255, 255, 0.88)` / `0.90`, assert token chip `#BE123C` / `#B45309` / `#047857`.
- [ ] Zero residu hex cokelat lama di `ui/` + `app.py` (`#78350F`, `#451A03`, `#92400E`, `#B45309` sebagai chrome).
- [ ] `__pycache__` tidak ter-track git.
- [ ] Lolos audit `@banggapupa` dan live DOM QA `@dorowani` (desktop 1440px, mobile 390px).

### 19.7 Pembagian Tugas
- `@parewa`: Terapkan §19.2 + §19.4 + §19.5 di `ui/components.py`, `ui/layout.py`, `app.py`; kunci regresi di `tests/test_ui_components.py`.
- `@banggapupa`: Audit titik kontras, klaim zero-brown, dan kekuatan assert test.
- `@dorowani`: Live DOM inspector port 8767 setelah APPROVED — jangan ukur build dengan chip < 4.5:1.

### 19.8 Token Teks Netral
- Caption `#64748B`: PASS di atas `#FFFFFF` (4.76:1), `#F8FAFC` (4.55:1), `#FFFCF7` (4.65:1). **FAIL di atas `#F1F5F9` (4.34:1).**
- Caption di atas container `#F1F5F9` wajib `#475569` — 6.92:1 di `#F1F5F9`, 7.58:1 di `#FFFFFF`, 7.24:1 di `#F8FAFC` (satu nilai aman semua container).
- **Cakupan berkas:** `ui/components.py` (pill `arch_pill` `:632`, pill kartu komparasi `:675`), `ui/layout.py` (tabbar `stTab` `:133`), dan `app.py` (pill header `:70`).
- Test wajib mengunci lintas berkas (`ui/components.py`, `ui/layout.py`, `app.py`): `#64748B` tidak boleh muncul sebagai `color:` di elemen yang punya `background: #F1F5F9` / tablist `#F1F5F9`.
- **Status sidebar (`ui/layout.py:366,395,401`):** `render_sidebar()` adalah dead code (nol pemanggil di `app.py`). Bila suatu saat dihubungkan kembali, elemen di dalamnya wajib diaudit kontrasnya sebelum dirilis ke runtime.

### 19.9 Tata Kelola Warna Teks Non-CSS (Altair / Chart)

**Keputusan: Altair MASUK cakupan §19.4, tapi tidak lewat tripwire source-grep CSS.**

- `ui/components.py:428` memakai `labelColor="#64748B"` — kwarg Altair, bukan deklarasi CSS `color:`. Tripwire `color:` (Blocker 5) dan tripwire pill `#F1F5F9` (Blocker 6) **tidak menjangkaunya**. Rasa aman dari grep CSS tidak berlaku untuk chart; ini dicatat eksplisit agar tidak diklaim tertutup.
- Nilai sekarang **PASS**: label sumbu dirender di atas bidang plot putih, `#64748B` vs `#FFFFFF` = 4.76:1 (SC 1.4.3 terpenuhi). Tidak dipatch, tidak dianggap blocker.
- **Aturan:** setiap `labelColor=` / `titleColor=` / `axis label color` Altair wajib dihitung terhadap **background plot chart**, bukan background kartu pembungkus. Bila bidang plot berubah jadi tint lebih gelap dari `#F8FAFC` (`#F1F5F9` dst.), warna label wajib naik ke `#475569`.
- **Enforcement:** test baru berbasis pola `labelColor=` harus mengekstrak nilai hex dan mengukur rasio terhadap bg plot yang dideklarasikan, bukan sekadar assert string. Tripwire source-grep CSS dinyatakan **tidak berwenang** atas kategori ini.

### 19.10 Status Gate Siklus Ini (pasca-merge)

**Status: SELESAI & DI-MERGE.** Blocker 1–8 tertutup.

- Blocker 1–6 ditutup di `7f29a71`; Blocker 7–8 (pill header `app.py:70`, tabbar `ui/layout.py:133`, tripwire multi-berkas) ditutup di `20437aa`.
- Spec final `c537e35`. APPROVED akhir oleh `@banggapupa` atas `20437aa` + `c537e35`; live DOM PASS `@dorowani` pada `df17a63` (kode identik `20437aa`).
- Merge ke `main`: `7e2b241` (merge commit, dari `fix/vibrant-crypto-harmonization`).
- Sync spec stale: `c50762b` (fallback `#4E36E2`, §15/§16/§17 ditandai SUPERSEDED).
- `main` = `origin/main` = commit terakhir pada rantai di atas; palet §18 (`e25560d`) sudah tidak aktif.

**Grandfathered** (tidak boleh disentuh tanpa spec baru): 4 stop kartu KPI `4.56:1`; chip `peaberry #2563EB` `4.75:1`.

**Utang terbuka, bukan blocker:**
1. Enforcement test Altair `labelColor=` (§19.9) belum ada — wajib dibuat sebelum `labelColor=` pertama kali diubah.
2. `#64748B` di `#F8FAFC` (4.55:1) pada `ui/components.py:878,900,922,944` dan stepper `:1034,1042,1050` — margin rapuh.
3. `render_sidebar` dead code (`ui/layout.py:366,395,401`) belum terukur; bila disambungkan ke `app.py`, kontras wajib diaudit sebagai gate baru.
- `ui/layout.py:66 --brand-emerald: #059669` — nol referensi `var(--brand-emerald)`, dihapus bersama pembersihan token berikutnya.

---

## 20. Kontrak Jarak & Tata Letak Baris KPI (Spacing Gate) — 2026-11-27

### 20.1 Masalah Terukur (bukan asumsi)
Dilaporkan user: 4 kartu KPI tidak sejajar jaraknya pada mode mobile. Akar masalah ditemukan lewat computed style DOM, bukan pembacaan source:

```
kartu div            h=102.86  margin-bottom=0
stMarkdownContainer  h=102.86  margin-bottom=-16px   <-- biang
stElementContainer   h=86.86                         <-- terpotong 16px
stColumn             h=86.86
```

`stMarkdownContainer` membawa `margin-bottom: -16px` bawaan Streamlit. Kartu meluber 16px keluar kolom. Saat kolom turun baris (mobile), jarak visual = row-gap 16px − luberan 16px = **0**. Karena hanya kartu 2 punya tinggi berbeda, pola jarak jadi **0 / 16 / 0** — persis yang user lihat.

Penyebab tinggi kartu 2 berbeda 1.8px: headline `1.08rem` ("60:20:20 Split") vs `1.15rem` kartu lain (`ui/components.py:143`).

### 20.2 Kontrak Wajib
1. **Row gap efektif baris KPI = 16px ± 1px di semua breakpoint** (360–1440). Bukan 0, bukan 32.
2. **Tinggi kartu KPI seragam di dalam satu baris.** Selisih antar kartu ≤ 1px pada lebar ≥ 1024; pada 768/820 kartu boleh lebih tinggi bila headline wrap, tetapi **seluruh kartu dalam baris yang sama wajib sama tinggi** (`align-items: stretch`).
3. **`margin-bottom: -16px` efektif dilarang** pada baris KPI. Dinetralkan ke `0` secara ter-scope.
4. **`box-sizing: border-box` + `height: 100%` + `min-height: 104px`** pada kartu KPI agar kartu mengisi tinggi kolom, bukan meluber keluar.
5. **Jarak kartu KPI terakhir → dropzone uploader ≤ 72px** pada 390px.
   - **Anchor metrik = `dropzone.top`**, bukan `header card top`. Baseline 116.8px diukur ke `uploader.top 867.5` yang identik dengan dropzone, jadi tafsir "ke kartu header = 16px lulus" **batal**.
   - Kondisi `6af3bde` = **128.8px → GAGAL**, dan **naik 12px** dari baseline. Poin 1–4 diperbaiki dengan mengorbankan poin 5.
   - Penyelesaian struktural ada di §20.9; target 72px **tidak diturunkan**.
6. **Jarak kartu KPI terakhir → judul inline uploader = 16px ±1px** pada semua breakpoint. Ini metrik terpisah dari poin 5, bukan pengganti.

### 20.3 Aturan Wrap Tipografi (768 / 820px)
- Kartu 2 **boleh wrap dua baris** pada 768/820px (kolom 165–178px tidak cukup untuk "60:20:20 Split" satu baris).
- **Dilarang `white-space: nowrap`** pada headline kartu — pada 320px akan overflow horizontal.
- Kompensasi: `min-height: 104px` + `align-items: stretch` menjaga seragam. Font tidak di-clamp per breakpoint pada siklus ini (menambah kompleksitas tanpa kebutuhan terukur).

### 20.4 Cakupan Selektor (wajib ketat)
```css
div[data-testid="stHorizontalBlock"]:has(div[style*="linear-gradient(115deg"])
  div[data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; }

div[style*="linear-gradient(115deg"] {
  box-sizing: border-box !important;
  height: 100% !important;
  min-height: 104px !important;
}
```
- **Wajib** ter-scope ke baris yang memuat kartu bergradien `115deg`. Dilarang menyentuh `stHorizontalBlock` milik uploader, tab, kartu komparasi, atau footer.
- Browser tanpa dukungan `:has()`: aturan baris pertama tidak berlaku (progressive enhancement). Tidak boleh ada fallback global yang lebih luas — risiko regresi lintas baris lebih besar daripada manfaatnya.
- Penempatan: blok CSS `setup_page_config` di `ui/layout.py`. **Markup kartu di `ui/components.py` tidak diubah** kecuali pemisah uploader (§20.2 poin 5).

### 20.5 Bukti Validasi Sebelum Patch
Kandidat fix diukur lebih dulu lewat injeksi live DOM pada 8 lebar:

| lebar | gap sesudah | tinggi sesudah | overflowX | window.errors |
|---|---|---|---|---|
| 1440 / 1280 / 1024 | satu baris | 104 × 4 | false | 0 |
| 820 / 768 | — | 104 / 119.5 / 104 / 104 | false | 0 |
| 414 / 390 / 360 | **16 / 16 / 16** | 104 × 4 | false | 0 |

Baseline 390px = `0 / 16 / 0`. Sesudah = `16 / 16 / 16`. Itu kriteria lulusnya.

### 20.6 Kriteria Penerimaan (DoD)
- [ ] Gap baris KPI = 16 ± 1px pada 360, 390, 414, 768, 820, 1024, 1280, 1440 — diukur dari computed style DOM, bukan screenshot mata.
- [ ] Tinggi seluruh kartu dalam satu baris sama (toleransi 1px); `min-height: 104px` aktif.
- [ ] `scrollWidth == clientWidth` di semua lebar (tanpa overflow horizontal).
- [ ] Gap kartu 4 → **dropzone** ≤ 72px pada 390/414px, ≤ 80px pada 360/320px (toleransi wrap). Ukur dari `dropzone.top`, bukan header card.
- [ ] Gap kartu 4 → judul inline uploader = 16px ±1px.
- [ ] `window.onerror` / `pageerror` = 0.
- [ ] Suite unit test tetap hijau; `compileall` exit 0.
- [ ] Audit `@banggapupa`: selektor `:has()` tidak bocor ke baris lain.
- [ ] Live DOM `@dorowani` pada commit pasca-patch.

### 20.7 Di Luar Cakupan (jangan dijadikan blocker)
- Glyph `✨` `scrollWidth 22` vs `clientWidth 20` — clip 2px, kosmetik.
- `"Pilih skenario split"` `sw=122 / cw=1` — sr-only by design untuk aksesibilitas popover.
- Suite 84/84 PASS tidak menangkap cacat ini karena **tidak ada satu pun test yang mengukur geometri DOM**. Dicatat sebagai batas wewenang unit test, bukan alasan menambah test geometri pada siklus ini.

### 20.8 Pembagian Tugas
- `@parewa`: patch CSS §20.4 di `ui/layout.py` (sudah mendarat `6af3bde`, jangan disentuh lagi) + patch **§20.9** pada `app.py:49-76` (demote kartu header → inline header, class hook `upload-studio-header`); verifikasi 360/390/414 + 768/820/1024/1440; laporkan commit hash.
- `@banggapupa`: audit cakupan selektor `:has()` dan pastikan nol bocor ke baris non-KPI.
- `@dorowani`: live DOM ulang pasca-patch, acuan commit baru (bukan `42a757f`).

### 20.9 Keputusan Struktural Poin 5 — Demosi Kartu Header Uploader

**Keputusan: opsi 2 (demote).** Kartu header `app.py:49-76` (tinggi 70.8px, `padding: 14px 18px`, `margin-bottom: 14px`) diubah menjadi **baris judul inline tanpa chrome** — tanpa `background`, `border`, `border-radius`, `box-shadow`. Konten (ikon + `h3` + badge) tetap, wadah kartunya dihapus.

Alasan memilih opsi ini, bukan yang lain:
- Opsi 1 (kompakkan padding saja) memotong ±28px dari 128.8px → ±100px. Masih **gagal** target 72px.
- Opsi 3 (turunkan target) menutupi cacat, bukan menutupnya — ditolak.
- Opsi 2 satu-satunya yang lulus tanpa menambal tiga tempat terpisah.

**Kontrak markup (wajib):**
1. Wadah: `<div class="upload-studio-header" style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin:0 0 8px 0; padding:0; flex-wrap:wrap;">`.
2. **Dilarang** `background`, `border`, `border-radius`, `box-shadow` pada `.upload-studio-header` — itu yang menambah 28.8px tinggi visual + 14px margin.
3. `h3` tetap `0.95rem` / `font-weight: 800` / `#0F172A`; ikon `#4E36E2` 18×18 tetap.
4. Badge `0.64rem` mono `#475569` di atas `#F1F5F9` = **6.92:1** (jangan diubah ke `#64748B`). `0.64rem` adalah nilai efektif terukur — spec lama menulis `0.68rem`, itu stale.
5. **Dilarang** `position: absolute` / `fixed` untuk header — harus flow normal agar `dropzone.top` stabil terukur.
6. `white-space: nowrap` tetap dilarang (§20.3).
7. Baris `st.columns([1, 1], gap="medium")` di `app.py:77` **tidak diubah**. Header duduk di luar kolom, tepat sebelum `st.columns`.

**Anggaran jarak (aritmetika yang harus ditutup):**
```
16  row gap baris KPI
30  header inline (ceil 390/414px)
 8  margin-bottom header
18  padding internal dropzone
= 72px  -> tepat di target
```
Konsekuensi mengikat: **tinggi header inline ≤ 30px pada ≥ 768px, ≤ 44px pada 320–414px**. Badge `Max 10 MB • Auto-Normalized 224px` tidak muat satu baris di kolom 342px, jadi `flex-wrap` mengizinkan dua baris dan tinggi efektif terukur **38.7px** — sah selama ≤ 44px. Batas gap 360/320 dilonggarkan ke ≤ 80px (§20.6). **Dilarang** memaksa `nowrap` demi 30px; itu yang dilarang §20.3.

**Ambang per lebar (acuan lulus):**

| lebar | tinggi header | gap kartu 4 → dropzone |
|---|---|---|
| 1024–1440 | ≤ 30px | ≤ 56px |
| 768 / 820 | ≤ 30px | ≤ 64px |
| 414 | ≤ 44px | **≤ 72px** |
| 390 | ≤ 44px | **≤ 72px** |
| 360 | ≤ 44px | ≤ 80px |
| 320 | ≤ 44px | ≤ 80px |

Kolom "tinggi header" mengizinkan dua baris pada 320–414 (badge wrap). Angka terukur pasca-patch: **18.4px** desktop, **38.7px** mobile.

**Yang tidak boleh berubah:** poin 1–4 sudah PASS di `6af3bde` (`16/16/16`, `min-height: 104px`, `mbNeg 0`). Patch §20.9 **tidak boleh** menyentuh blok CSS `ui/layout.py:317-355`; popover split (`stLayoutWrapper h=0`) sudah terbukti hidup — jangan diregresikan.

### 20.10 Status Gate §20 — SELESAI & DITUTUP
Status: **CLOSED.** Poin 1–5 §20.2 tertutup dan terukur live DOM di sembilan lebar (320–1440).

**Rantai penutupan (terverifikasi):**
- Kode patch: `9d3c39e` (chrome header uploader dihapus, `app.py:49–79`), `748607e` (`label_visibility="collapsed"` pada `st.file_uploader`, `ui/components.py:242`), `72f4c70` (koreksi komentar a11y, bukan kode).
- APPROVED `@banggapupa` atas `72f4c70` — ukur ulang independen, bukan salin tabel @parewa.
- PASS `@dorowani` atas `72f4c70` — ukur ulang independen, sembilan lebar, popover split + AX tree diuji.
- `main` = `origin/main` = `72f4c70` saat gate ditutup. `Ran 84 tests ... OK`, `compileall` 0, `diffcheck` 0, `__pycache__` tracked 0, tree clean.

**Angka penutupan (identik tiga pengukur):**

| w | tinggi kartu | gap kartu | hdrH | gap→dropzone |
|---|---|---|---|---|
| 1440 / 1280 / 1024 | 104×4 | satu baris | 18.4 | 42.4 |
| 820 / 768 | 119.5×4 | satu baris | 18.4 | 42.4 |
| 414 / 390 / 360 / 320 | 104×4 | **16/16/16** | 38.7 | 62.6 |

Baseline `0/16/0` → `16/16/16`; `128.8px` → `62.6px`.

**Nol regresi terverifikasi:** `git diff 6af3bde..HEAD -- ui/layout.py` kosong (poin 1–4 utuh); popover split hidup (`stLayoutWrapper h=0`, panel terbuka, 3 opsi radio); AX tree uploader tetap bernama (`dzAria = "Unggah Citra Biji Kopi"`, label `aria-hidden`, `display:none`); badge `#475569`/`#F1F5F9` 6.92:1 utuh.

**Dua kontradiksi dokumen yang diselesaikan di commit ini:**
1. Tabel ambang §20.9 dulu menulis `≤30px` untuk 414/390, bertentangan dengan prosa wrap `≤44px` di section yang sama. Yang menang = prosa: `≤30px` pada ≥768 (header satu baris), `≤44px` pada 320–414 (badge wrap dua baris, terukur 38.7px).
2. Badge tertulis `0.68rem` di spec, efektif `0.64rem` di kode. Spec diselaraskan ke `0.64rem` sebagai nilai efektif — kontras identik 6.92:1 di kedua ukuran.

**Utang terbuka, jangan diklaim beres:**
1. **Tripwire anti-chrome `.upload-studio-header` sudah ditulis (`d464dcb`), terkanonikalisasi (`060526d`), tapi BELUM FINAL — lima pintu berturut-turut terbukti.** Kronologi cacat, semuanya terukur di browser dan semuanya hijau di suite lama: (a) `"position:"` sebagai substring gugur (mem-ban `position: static`), (b) tripwire inline saja buta pada stylesheet `ui/layout.py` (`62.7 → 96.7` @390), (c) case-insensitivity — `BACKGROUND`, `PADDING !IMPORTANT`, (d) komentar + whitespace — `position/**/:/**/absolute`, `! important`, (e) **escape heksadesimal — `pos\69 tion:absolute`**, lapis yang masih terbuka di `060526d` (§20.11.2). Kelas cacatnya satu dan berulang: tripwire memeriksa **bentuk penulisan**, browser memeriksa **semantik CSS**. Karena itu aturan maju yang mengikat: normalisasi dulu lewat satu `_canon` bersama, dan **normalisasi source-level tidak pernah bisa lengkap** — escape dalam string, `url()`, `@import` jarak jauh, custom property `var()` tidak bisa didekode tanpa tokenizer penuh. Tiga lapis wajib ada bersama: §20.11 (inline attr `app.py`), §20.12 (style-block-scoped tiga berkas), §20.13 (gate geometri CDP — satu-satunya yang menangkap pintu keempat dan kelima). Yang menanggung klaim keamanan adalah §20.13, bukan regex. Chrome kembali = +28.8px tinggi +14px margin, poin 5 merah lagi, sementara suite tetap hijau — inilah satu-satunya utang dengan jalur regresi senyap. Masuk siklus berikutnya bersama pembersihan token `--brand-emerald`.
2. **Header brand ter-clip di ≤360px** — `sw 284 / cw 281` @360, `sw 297 / cw 270` @320. Brand header, pra-ada, di luar cakupan §20.
3. **`ui/layout.py:66 --brand-emerald: #059669`** — nol referensi `var(--brand-emerald)`, tidak dirender.
4. **`render_sidebar` dead code** (`layout.py:366,395,401`) — belum terukur; jadi gate baru bila disambung.
5. **Grandfathered kontras:** 4 stop kartu KPI `4.56:1`, `peaberry` `4.75:1` (§19.3). Utang §19.9 test Altair `labelColor=` (§19.10 versi §19).

**Di luar cakupan, jangan dibuka sebagai temuan §20:** `Limit 10MB per file • JPG, JPEG, PNG, WEBP` (`sw 282 / cw 248` @1024) milik widget Streamlit dengan `text-overflow: ellipsis`, by design. `"Pilih skenario split"` `sw 122 / cw 1` sr-only. Tab label panjang di tabstrip — scroll horizontal internal Streamlit, `docW == vw` di semua lebar.

**Catatan repo:** commit `42a757f` (local Figma builder plugin) sudah ada di `main` sebelum siklus §20, tidak di audit, tidak disentuh, tetap di luar cakupan.

### 20.11 Bentuk Final Tripwire Anti-Chrome `.upload-studio-header` (dikunci; masuk `d464dcb` = BELUM FINAL, lihat 20.11.1)

**Status:** spec terkunci. Test sudah ditulis di `d464dcb` (`tests/test_ui_components.py:TestUploaderHeaderNoChrome`). Tiga lapis normalisasi mendarat di `060526d` (§20.11.1). **Lapis keempat — escape heksadesimal — masih bocor**, lihat §20.11.2. Utang #1 §20.10 belum tertutup.

Dua bentuk sebelumnya gugur karena terbukti merah di tree bersih atau mem-ban lebih dari yang dilarang spec:

| bentuk | hasil pada `4d10255` bersih | alasan gugur |
|---|---|---|
| slice region `index("upload-studio-header") → index("st.columns")` | **3 false positive** (`background` rel=1144, `border:` rel=1165, `border-radius` rel=1210) | slice menelan `<span>` badge yang justru **diwajibkan** poin 4 |
| `"position:"` sebagai substring | lolos hari ini, tapi mem-ban `position: static` | poin 5 justru **mewajibkan** `static` agar anchor `dropzone.top` stabil |

**Bentuk yang dikunci** — scope ke atribut `style` milik `<div class="upload-studio-header">` saja:

```python
def test_uploader_header_has_no_chrome(self):
    src = pathlib.Path("app.py").read_text()
    anchor = src.index('class="upload-studio-header"')
    start = src.index('style="', anchor)
    block = src[start:src.index('">', start)]
    self.assertLess(len(block), 400, "slice style header terpotong")
    self.assertNotIn("<div", block, "slice menelan markup anak")
    self.assertIn("display: flex", block, "blok style header tidak terambil")
    for prop in ("background", "border", "border-radius", "box-shadow",
                 "position: absolute", "position: fixed"):
        self.assertNotIn(prop, block, f".upload-studio-header dilarang {prop} (§20.9 poin 2)")
```

Tiga guard wajib, bukan opsional:
1. `assertLess(len(block), 400)` — slice berhenti di `">` pertama; data-URI `background-image: url("data:...>")` akan memotong blok dan melahirkan hijau-palsu.
2. `assertNotIn("<div", block)` — memastikan slice tidak menelan markup anak.
3. `assertIn("display: flex", block)` — kalau markup berubah dan slice jadi kosong, semua `assertNotIn` lolos tanpa memeriksa apa pun. Kelas celah sama dengan guard `checked >= N` di tripwire §19.

**Bukti bergigi (reproduksi independen @parewa dan @dorowani, dijalankan pada salinan, working tree tidak disentuh):**

| injeksi ke `style` header | naive region | scoped final |
|---|---|---|
| bersih (HEAD `4d10255`) | **3 FP → merah** | `[]` → hijau benar |
| `background: #FFFFFF` | catch | catch |
| `border: 1px solid …` | catch | catch |
| `border-radius: 12px` | catch | catch |
| `box-shadow: …` | catch | catch |
| `position: absolute` (dan `fixed`) | catch | catch |

Terukur: region `len 1452`, scoped `len 221`.

**Batas wewenang — jangan dilebarkan:**
- Test ini **tidak** mengukur geometri. `dropzone.top − lastCardBottom` tetap **gate manual QA** milik `@dorowani`, tidak boleh dipalsukan jadi unit test yang hijau tanpa DOM.
- Test ini **tidak** menyentuh badge (`#475569` di `#F1F5F9` 6.92:1) — badge justru wajib punya `background`, `border`, `border-radius`.
- `position: static` sah dan tidak boleh ikut ditolak.

### 20.11.1 Klausa Kanonikalisasi CSS — Komentar + Whitespace + Case (mendarat `060526d`)

**Status:** tiga lapis mendarat di `060526d` (`_canon` dipakai bersama dua tripwire). Lapis keempat — escape heksadesimal — masih bocor, lihat §20.11.2.

Nama properti CSS, kata kunci `!important`, whitespace, dan komentar **tidak bermakna** bagi browser. Bentuk `d464dcb` memakai `assertNotIn(prop, block)` dan `re.search(rf"\b{prop}...")` tanpa flag — case-sensitive, literal-spasi, literal-komentar. Jadi tripwire dan browser tidak sepakat soal apa yang "ada".

Logika shipped dijalankan apa adanya pada `app.py` / `ui/layout.py` nyata:

```
§20.11  BACKGROUND: #FFFFFF;              shipped_hits=[]
        BORDER: 1px solid #E2E8F0;        shipped_hits=[]
        BORDER-RADIUS: 12px;              shipped_hits=[]
        BOX-SHADOW: 0 1px 3px ...;        shipped_hits=[]
        POSITION: ABSOLUTE;               shipped_hits=[]
        Position: Fixed;                  shipped_hits=[]
§20.12  .upload-studio-header { PADDING: 14px !IMPORTANT; }   shipped=[]
        .upload-studio-header { POSITION: FIXED !IMPORTANT; } shipped=[]
```

Huruf kecil tetap tertangkap, jadi test-nya memang hidup — bukan mati. Yang bolong hanya varian kapital.

Dan rule itu **berlaku di browser**, bukan cuma lolos regex. Live DOM @390, `d464dcb`, tree tidak disentuh:

| keadaan | gap→dropzone | hdrH | bg | pad | mb |
|---|---|---|---|---|---|
| base | **62.7** | 38.7 | `rgba(0,0,0,0)` | `0px` | `8px` |
| rule `PADDING/MARGIN !IMPORTANT` | **96.7** | 66.7 | `rgb(255,255,255)` | `14px 18px` | `14px` |
| restore | 62.7 | 38.7 | transparan | `0px` | `8px` |

`naiveBannedHit: false` selama injeksi hidup — kedua tripwire hijau, suite hijau, geometri jebol lewat ambang `≤72`.

**Fix terukur (dua baris):**

1. §20.11 — oper `block.lower()` sebelum loop `BANNED`. Hasil: `BACKGROUND` / `BORDER` / `BORDER-RADIUS` / `BOX-SHADOW` / `POSITION: ABSOLUTE` / `Position: Fixed` semua CAUGHT; `POSITION: STATIC` tetap lolos (sah, §20.9 poin 5).
2. §20.12 — `re.search(..., body, re.I)` untuk `GEOM_PROPS` dan `POS`. Hasil: `PADDING !IMPORTANT` / `Padding !Important` / `BACKGROUND: #FFFFFF !IMPORTANT` / `POSITION: FIXED !IMPORTANT` CAUGHT; `background` tanpa `!important`, `padding: 0`, dan `position: static !important` tetap lolos.

False positif baseline nol di tiga berkas (`0 / 1 blok 0 rule / 0`) sebelum dan sesudah tambalan.

**Kelas cacat:** sama dengan `"position:"` substring (§20.11) dan `checked >= N` (§19) — tripwire yang memeriksa **bentuk penulisan**, bukan **semantik CSS**. Setiap kali menambah ban-list, tanya: apakah penulisan lain yang sah bagi browser bisa melewatinya? Kalau ya, tambal normalisasi sebelum menambah nama properti.

### 20.11.2 Klausa Escape Heksadesimal — Lapis Keempat, dan Batas Akhir Normalisasi

**Status:** cacat terukur pada `060526d` (`_canon` mendarat, tapi tidak mendekode escape). Wajib ditambal sebelum pasangan §20.11+§20.12 boleh disebut tertutup.

`pos\69 tion:absolute` adalah deklarasi **sah**: `\69` = `i`, jadi nama propertinya tetap `position`. `_canon` membuang komentar dan merapatkan whitespace, tapi tidak mendekode escape CSS. Tripwire hijau, browser tetap mengeksekusi.

Bukti gigi — logika shipped `060526d`, dijalankan atas `app.py` / `ui/layout.py` nyata:

```
§20.11  pos\69 tion:absolute                 -> EVADED (hits=[])
        POS\69 TION:ABSOLUTE                 -> EVADED
§20.12  padd\69 ng:14px !important           -> EVADED
        padding:14px !impor\74 ant           -> EVADED
        pos\69 tion:fixed !\69 mportant      -> EVADED
```

Guard tidak menyelamatkan: `len 221 < 400` True, `"<div"` False, `display: flex` True.

Dan varian itu **berlaku di browser**, live DOM @390, tree tidak disentuh:

| keadaan | `hdrPos` terhitung | hdrH | gap→dropzone | verdict `PROBE_JS` |
|---|---|---|---|---|
| base | `static` | 38.7 | 62.7 | PASS |
| inline `pos\69 tion:absolute` | **`absolute`** | 38.7 | **32.0** | **FAIL `["hdr"]`** |
| stylesheet `padd\69 ng:14px 18px !important` | — | 66.7 | **96.7** | **FAIL `["gap","hdrH"]`** |
| stylesheet `… !impor\74 ant` | — | 66.7 | **96.7** | **FAIL `["gap","hdrH"]`** |
| restore | `static` | 38.7 | 62.7 | PASS |

**Fix terukur — satu baris di dalam `_canon`, bukan regex baru:**

```python
def _canon(css: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    s = re.sub(r"\\([0-9a-fA-F]{1,6})\s?", lambda m: chr(int(m.group(1), 16)), s)
    return re.sub(r"\s+", " ", s).lower()
```

Hasil pada berkas nyata: `pos\69 tion:absolute`, `POS\69 TION:ABSOLUTE`, `padd\69 ng:14px !important`, `padding:14px !impor\74 ant`, `margin-botto\6d :14px !IMPORTANT`, `pos\69 tion:fixed !\69 mportant` semuanya CAUGHT; `position: static`, `pos\69 tion:static`, `display: flex`, `background:#FFF`, `padding: 0px` tetap lolos. Baseline FP nol: `app.py len=221 canon=153 backslashes=0 hits=[]`, `ui/layout.py blocks=1 rules=0 hits=[]`.

**Batas akhir — normalisasi source-level tidak pernah bisa lengkap.** Escape CSS punya bentuk lain yang tidak bisa didekode tanpa tokenizer penuh (escape dalam string, escape di dalam `url()`, `@import` jarak jauh, custom property `--x` yang di-`var()`). Karena itu:

- Klausa ini **wajib** masuk, tapi **dilarang** diklaim sebagai penutup.
- Yang menanggung klaim keamanan tetap §20.13 — `hdrPos != "static"` dan `gapToDz > ambang` menangkap keempat lapis bypass ini **tanpa** perlu tahu bentuk penulisannya.
- Kalimat wajib yang berlaku untuk seluruh §20.11–§20.12: **perlu, tidak cukup; §20.13 yang otoritatif.**

### 20.12 Tripwire Anti-Chrome — Assertion Kedua (bypass stylesheet `!important`)

**Status:** spec terkunci. Test masuk `d464dcb`; kanonikalisasi mendarat `060526d` (§20.11.1), guard per-berkas lulus audit (§20.12.1). **Escape heksadesimal masih bocor** (§20.11.2). Utang #1 §20.10 belum tertutup.

`§20.11` hanya membaca `app.py` (atribut `style` inline). Itu **tidak cukup** — chrome bisa dipulihkan lewat stylesheet tanpa pernah dilihat tripwire. Dua temuan memperluas cakupannya:

**Temuan 1 — stylesheet bukan satu berkas.** `unsafe_allow_html=True` terpasang di tiga berkas: `app.py` (3), `ui/components.py` (19), `ui/layout.py` (5). Chrome `padding: 14px 18px !important` di `ui/components.py` mengembalikan penyakit poin 5 persis dan **nol** tripwire membacanya. Cakupan wajib: `app.py`, `ui/layout.py`, `ui/components.py`.

**Temuan 2 — regex rule atas source Python mentah menghasilkan rule palsu.** `RULE = re.compile(r"([^{}]*)\{([^{}]*)\}")` dijalankan pada `app.py` utuh mencocokkan brace Python:

```
SEL : """Main application entry point...""" | | import
BODY: selected_split
```

Itu dict/f-string/docstring, bukan CSS. Karena itu ekstraksi `<style>` wajib lebih dulu, baru `RULE` dijalankan di dalam isinya. Baseline terukur pada `eea855d`:

```
app.py             style_blocks=0  header_rules=0  hits=[]
ui/layout.py       style_blocks=1  header_rules=0  hits=[]
ui/components.py   style_blocks=0  header_rules=0  hits=[]
```

Dibuktikan @banggapupa lewat injeksi rule `.upload-studio-header` ke `layout.py` dan mengukur geometri @390:

| keadaan | hdrH | bg | pad | mb | dzTop | gap→dropzone |
|---|---|---|---|---|---|---|
| BASE `94048de` | 38.7 | `rgba(0,0,0,0)` | `0px` | `8px` | 801.9 | **62.7** |
| rule tanpa `!important` | 38.7 | `rgb(255,255,255)` | `0px` | `8px` | 801.9 | 62.7 |
| rule **dengan** `!important` | 66.7 | `rgb(255,255,255)` | `14px 18px` | `14px` | 835.9 | **96.7 FAIL** |
| restore | 38.7 | transparan | `0px` | `8px` | 801.9 | 62.7 |

Dua tingkat kebocoran:
1. **`background` pulang tanpa `!important`** — inline style header tidak menetapkan `background`, jadi rule stylesheet menang tanpa perlawanan. Geometri selamat, chrome visual kembali, `§20.11` hijau.
2. **`!important` membunuh geometri** — `padding: 14px 18px !important` + `margin-bottom: 14px !important` mengembalikan penyakit asli: `62.7 → 96.7`, lewat ambang `≤72` @390. `lastCardBottom 739.3` identik di keempat keadaan, jadi **tidak ada sinyal lain** yang menangkapnya.

**Assertion kedua (wajib, style-block-scoped atas tiga berkas `app.py`, `ui/layout.py`, `ui/components.py`):**

```python
GEOM_PROPS = ("padding", "margin", "background", "border", "border-radius", "box-shadow")
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
RULE = re.compile(r"([^{}]*upload-studio-header[^{}]*)\{([^{}]*)\}")

def test_no_important_chrome_override_for_uploader_header(self):
    total_blocks = 0
    for path in ("app.py", "ui/layout.py", "ui/components.py"):
        src = pathlib.Path(path).read_text()
        blocks = STYLE_BLOCK.findall(src)
        total_blocks += len(blocks)
        for block in blocks:
            for m in RULE.finditer(block):
                body = m.group(2)
                selector = m.group(1).strip()
                for prop in GEOM_PROPS:
                    if re.search(rf"\b{prop}[^;]*!important", body):
                        self.fail(f"{path}: {selector} dilarang me-force {prop} !important (§20.9 poin 2)")
                if re.search(r"\bposition\s*:\s*(absolute|fixed)\b[^;]*!important", body):
                    self.fail(f"{path}: {selector} dilarang me-force position:absolute|fixed !important (§20.9 poin 5)")
    self.assertGreaterEqual(total_blocks, 1, "ekstraksi <style> rusak — nol blok terbaca, semua assertNotIn lolos buta")
    print(f"[§20.12] blok <style> diperiksa: {total_blocks}")
```

**Koreksi wajib atas draf pertama:** `"position"` sebagai anggota ban-list **salah** — `position: static !important` ikut ditolak padahal §20.9 poin 5 justru **mewajibkan** `static` supaya anchor `dropzone.top` stabil. Ini cacat kelas yang identik dengan `"position:"` substring yang sudah digugurkan di §20.11. `position` karena itu dikeluarkan dari `GEOM_PROPS` dan ditangani lewat regex eksplisit `absolute|fixed`.

Guard wajib **per-berkas**, bukan dijumlah lintas berkas:

```python
assertEqual(blocks["ui/layout.py"], 1)   # satu-satunya blok wajib ada
assertIn(blocks["app.py"], (0,))         # sah nol hari ini
assertIn(blocks["ui/components.py"], (0,))
```

Alasan terukur: `total_blocks >= 1` dijumlah lintas berkas. Hari ini `app.py 0 / ui/layout.py 1 / ui/components.py 0`, jadi yang memenuhi guard adalah `layout.py`. Kalau ekstraksi `<style>` di `layout.py` rusak sementara `components.py` suatu hari menambah satu blok, guard tetap ≥1 → semua pemeriksaan lolos buta pada berkas yang justru paling penting. Guard agregat = hijau-palsu yang sama kelas dengan `checked >= N` §19.

Cetak `blocks / rules / hits` **per berkas** (bukan total) supaya pembaca bisa melihat berkas mana yang benar-benar diperiksa. Nol rule hari ini **sah** (hanya `app.py:55` punya literal kelas), jadi test tidak boleh menuntut rule > 0; ia hanya wajib membuktikan blok benar-benar terbaca.

Kelas hijau-palsu yang ditutup: sama dengan guard `checked >= N` di tripwire §19 dan tiga guard di §20.11.

Regex aman terhadap gaya `layout.py`: setiap selektor turunan ditulis satu baris (catatan `_clean_html` di blok §20.4), jadi tidak ada `{`/`}` literal di dalam selektor. Data-URI SVG memakai brace ter-encode (`%7B`/`%7D`), bukan literal.

**Batas cakupan — jangan dilebarkan:**
- **Hanya `!important` yang dilarang** di stylesheet. Larangan `background` biasa di stylesheet ditolak: nol efek geometri (terukur 62.7 tetap) dan akan mem-ban selector sah untuk state lain (`:hover`, print, dsb).
- Test ini **tidak** mengukur geometri. `dropzone.top − lastCardBottom` adalah **gate rilis wajib** (§20.13) milik `@dorowani`, bukan pelengkap opsional. Bukti tabel di atas justru menunjukkan kenapa unit test tidak bisa menggantikannya — dua keadaan berbeda (chrome visual kembali vs geometri jebol) sama-sama lolos atau sama-sama mustahil ditangkap tanpa DOM.
- `§20.11` dan `§20.12` **wajib ditulis bersama**. Satu tanpa yang lain = tripwire dengan pintu belakang yang kita sudah tahu.
- **`§20.11` + `§20.12` bersifat perlu, tidak cukup.** Keduanya source-level. Selector CSS tidak wajib menyebut nama kelas atau memakai `!important` per-nama; lihat pintu keempat di §20.13. Dilarang menulis di dokumen mana pun bahwa pasangan ini "menutup celah".

### 20.12.1 Klausa Guard Per-Berkas — Wajib `layout.py == 1`

**Status:** cacat terukur pada implementasi `d464dcb`. Wajib ditambal sebelum pasangan §20.11+§20.12 boleh disebut tertutup.

`TestNoImportantChromeOverride.test_no_important_chrome_override_for_uploader_header` di `d464dcb` memakai guard `self.assertGreaterEqual(total_blocks, 1)`. Itu **dijumlah lintas tiga berkas**.

Baseline hari ini: `app.py 0 / ui/layout.py 1 / ui/components.py 0`. Blok tunggal itu milik `layout.py`.

Jika ekstraksi `<style>` di `layout.py` rusak sementara `components.py` suatu hari menambah satu blok `<style>`, `total_blocks` tetap = 1 → guard `total_blocks >= 1` PASS → semua `assertNotIn` di `layout.py` **lolos buta** pada berkas yang justru menjadi satu-satunya sumber stylesheet hari ini.

**Fix terukur:**

```python
# Guard per-berkas, bukan agregat
self.assertEqual(blocks["ui/layout.py"], 1, "ekstraksi <style> ui/layout.py rusak")
self.assertIn(blocks["app.py"], (0,))
self.assertIn(blocks["ui/components.py"], (0,))
```

Cetak log `blocks / rules / hits` **per berkas** ke stdout.

### 20.13 Gate Geometri Rilis — Probe CDP Headless (menggantikan regex `BARE`)

**Status:** spec dikunci, skrip **belum masuk repo**. Skrip sudah berjalan nyata di `eea855d` (scratch @parewa), angka tereproduksi independen oleh @dorowani. Commit `scripts/geo_gate.py` menunggu section ini — §6.1: implementasi tidak mendahului spec.

**Kenapa gate ini ada: pintu keempat.** §20.11 membaca atribut `style` inline di `app.py`. §20.12 membaca rule yang **menyebut literal `upload-studio-header`** di blok `<style>`. Selector CSS tidak wajib menyebut nama atau kelas apa pun. Dibuktikan @banggapupa, direproduksi @dorowani sampai dua desimal — @390, tree clean `eea855d`:

| keadaan | hdrH | bg | pad | mb | dzTop | gap→dropzone |
|---|---|---|---|---|---|---|
| BASE `eea855d` | 38.67 | `rgba(0,0,0,0)` | `0px` | `8px` | 801.92 | **62.67** |
| selector struktural `body > :nth-child(...)` + `!important` | 66.67 | `rgb(255,255,255)` | `14px 18px` | `14px` | 835.92 | **96.67 FAIL** |
| restore | 38.67 | transparan | `0px` | `8px` | 801.92 | 62.67 |

Selama injeksi itu hidup: regex §20.12 `hits=[]`, §20.11 `([], 221)` — **kedua tripwire hijau**. `selHasClassLiteral: false`, `matchCount: 1`, `selectsHeader: true`. `lastCardBottom 739.25` identik di ketiga keadaan, jadi tidak ada sinyal lain yang menangkapnya. `ui/layout.py` sudah memuat **129** deklarasi `!important`, jadi larangan per-nama tidak mengurangi kemampuan menimpa inline style.

**Pernyataan tegas yang wajib dibaca sebelum mengandalkan tripwire:** §20.11 + §20.12 bersifat **perlu, tidak cukup**. Tidak ada bentuk regex yang bisa membuktikan "tidak ada rule mana pun yang mengenai elemen header". Permukaan selector CSS tak terbatas (`*`, `[data-testid]`, `:has()`, rantai `:nth-child`, `body div div div`). Dilarang menulis di dokumen mana pun bahwa pasangan itu "menutup celah".

**Heuristik `BARE` digugurkan — angka tidak stabil, 21 FP di tree bersih.** Bentuk yang diusulkan:

```python
BARE = re.compile(r"^\s*(?:[^{},>+~]*[>+~]\s*){3,}|:nth-(?:child|of-type)\(")
```

Klaim awalnya `bare_structural=2`, nol FP. Diukur ulang independen di checkout nyata, `ui/layout.py`:

```
RAW               rules=45  bare_structural=22
COMMENT-STRIPPED  rules=45  bare_structural=21
selector-level breakdown: legit .brand-copy 1, legit popover §19 18, other 2, attack-class 0
```

Hitungnya bergeser `2 → 11 → 21 → 22` hanya karena cara selector-list dipotong — charclass `[^{},>+~]` mengecualikan `,`, jadi rule ber-selector-list runtuh. Yang tertangkap aturan sah yang sudah dikunci (§19 popover `:nth-child(2)`, `.brand-copy > p:nth-of-type(2)`), bukan serangan. Heuristik yang angkanya bergeser 2→22 adalah undian; kalau dikunci, merah di tree bersih → orang pertama melonggarkan regex → mati sebelum lahir. **Gugur, jangan ditulis ke suite.**

**Gate yang dipakai: `dropzone.top − lastCardBottom` diukur headless via CDP.**

```bash
.venv/bin/python scripts/geo_gate.py --url http://127.0.0.1:8767
```

Ambang per lebar (milik @dorowani, angka terukur `eea855d`):

| w | `gapToDz` terukur | ambang | tinggi kartu |
|---|---|---|---|
| 1440 / 1280 / 1024 | 42.4 | ≤ 56 | 104 × 4 |
| 820 / 768 | 42.4 | ≤ 64 | 119.5 × 4 |
| 414 / 390 | 62.6 | ≤ 72 | 104 × 4 |
| 360 / 320 | 62.6 | ≤ 80 | 104 × 4 |

**Syarat sah — delapan, bukan satu.** `ok` per lebar wajib memuat semuanya:

1. `gapToDz <= ambang[w]`
2. `cards == 4`
3. `sw == cw` (tanpa overflow horizontal)
4. `max(h) - min(h) <= 1` (poin 2 §20.2: tinggi seragam dalam satu baris)
5. `rowGap == "16px"` — computed style baris KPI, **bukan** geometri turunan
6. header utuh: elemen `.upload-studio-header` ada, `hdrDisp != "none"`, `hdrPos == "static"`, `18 <= hdrH <= 44` (`hdrH is None` = FAIL, bukan lolos)
7. `w >= 768` → `len(set(round(top))) == 1` (satu baris); `w < 768` → setiap gap `|g - 16| <= 1` (poin 1 §20.2)
8. `errs == []` (`window.onerror` / `pageerror`)

Bentuk `ok` yang dikunci:

```python
ok = (gap is not None and gap <= limit
      and m["cards"] == 4
      and m["sw"] == m["cw"]
      and max(m["h"]) - min(m["h"]) <= 1
      and m["rowGap"] == "16px"
      and m["hdrDisp"] != "none" and m["hdrPos"] == "static"
      and 18 <= (m["hdrH"] or 0) <= 44
      and (rows == 1 if w >= 768 else all(abs(g - 16) <= 1 for g in m["gaps"]))
      and not m["errs"])
```

`PROBE_JS` wajib mengembalikan `tops`, `gaps`, `h`, `errs`, `rowGap`, `hdrH`, `hdrDisp`, `hdrPos` — bukan hanya `cards,h,gaps,lastBot,dzTop,gapToDz,hdrH,sw,cw`.

**Syarat 5 — `rowGap` ter-scope ke baris KPI.** Ambil dari `cards[0].closest('[data-testid="stHorizontalBlock"]')`, **bukan** `stVerticalBlock` (yang juga `16px`) dan bukan `body`. Injeksi `gap:0` pada simpul lain tidak boleh lolos lewat pembacaan simpul yang salah.

**Syarat 6 — `hdrH` wajib ada.** `(m["hdrH"] or 0)` membuat `None` runtuh ke `0` lalu gagal `18 <= 0` — header yang hilang dari DOM tidak boleh lolos karena field-nya kosong.

**Kenapa syarat 5 & 6 ada — dua lubang terukur pada bentuk enam-syarat.** Keduanya PASS di baseline dan PASS setelah dirusak, jadi tidak ada sinyal lain yang menangkapnya.

Lubang 5 — syarat 7 tidak pernah dieksekusi saat kartu satu baris (`gaps` kosong), dan `gap <= limit` satu arah: mengecil selalu hijau.

```
INJ row-gap:0 @768    gapToDz 42.4 -> 10.4   PASS  (salah)
INJ row-gap:0 @1440   gapToDz 42.4 -> 10.4   PASS  (salah)
```

Penambalnya computed style, bukan geometri turunan — stabil sembilan lebar, nol false positive:

```
computed rowGap baris KPI (cards[0].closest('[data-testid="stHorizontalBlock"]')):
  320/360/390/414/768/820/1024/1280/1440 base -> "16px"   (rowH 390: 464)
  setelah injeksi gap:0                        -> "0px"    (rowH 390: 416)
  restore                                      -> "16px"
```

Lubang 6 — header dihapus atau keluar alur tetap PASS, karena `hdrH` cuma dicetak dan nol masuk `ok`:

```
390  base              gapToDz 62.7  hdrH 38.7  disp flex  pos static   -> PASS
390  hide_header       gapToDz 32.0  hdrH  0.0  disp none  pos static   -> PASS  (salah)
390  header_absolute   gapToDz 32.0  hdrH 38.7  disp flex  pos absolute -> PASS  (salah)
1440 pola identik (42.4 -> 32.0)                                        -> PASS  (salah)
```

Gate tidak bisa membedakan "header collapse sah §20.9" (`38.7px`, batas `<=44`) dari "header dihapus / `position:absolute`". Ambang `18 <= hdrH <= 44` berasal dari angka terukur: `18.4` desktop, `38.7` mobile.

**Kenapa empat syarat tambahan itu bukan hiasan — terukur.** Versi pertama (hanya `gap <= limit and sw == cw`) tetap `PASS` saat `row-gap` diinjak ke `0`:

```
BASE          gaps [16,16,16]  lastBot 739.3  dzTop 801.9  gapToDz 62.7  -> PASS
INJ row-gap:0 gaps [ 0,  0,  0]  lastBot 659.3  dzTop 689.9  gapToDz 30.7  -> PASS  (salah)
```

Jarak kartu `16 → 0` adalah penyakit asli §20.2 poin 1 yang memicu seluruh siklus, dan probe buta terhadapnya: kolom mengempis, `gapToDz` **mengecil**, makin rusak layout makin hijau gate. `row-gap:0` juga lolos `overflowX` dan `sw == cw`. `cards` di versi pertama hanya dipakai di loop tunggu `measure()`, jadi kartu tinggal 2 tetap bisa `PASS`. `h` / `gaps` / `spread` dikumpulkan tapi nol masuk `ok`. `errs` tidak diambil sama sekali.

**Tata kelola gate:**
- Gate ini **syarat rilis**, bukan pelengkap opsional. Dijalankan headless pada commit yang akan merge; tabel hasilnya dilampirkan ke DoD.
- Tidak dijalankan → status `CHANGES_REQUESTED`, bukan "dianggap aman".
- `exit 0` = semua lebar lulus; `exit 1` = ada lebar gagal, cetak `w, gap, limit, sw, cw` per lebar.
- Pemilik eksekusi: `@dorowani`. Port headless ke CI: `@parewa` bila CI ditambahkan (repo saat ini `NO-CI-CONFIG` — nol `.github/`, `.gitlab-ci`, `Jenkinsfile`, `.circleci`).

**Batas jujur probe — jangan diklaim lebih:**
- Probe mengukur **geometri akhir**, bukan sebabnya. Ia menangkap pintu keempat (`62.7 → 96.7`) tapi tidak memberi tahu CSS mana pelakunya. Pembagian kerja yang benar: regresi ditangkap gate, penyebab dicari manusia.
- Anchor kartu = `div[style*="linear-gradient(115deg"]`. Selector yang sama yang jadi jebakan bila nanti ada komponen lain memakai `115deg`. Bila markup kartu KPI berubah, probe **wajib** ikut diubah; `cards == 4` dibuat hard-fail supaya perubahan markup gagal keras, bukan lolos diam-diam.
- Probe tidak menambah dependency aplikasi: nol `playwright`/`selenium`/`websocket-client` di `requirements.txt`. Pakai `json`, `socket`, `struct`, `subprocess`, `urllib` + Chrome headless sendiri.
- Probe **tidak** menggantikan §20.11/§20.12. Ketiganya lapis berbeda: dua source-level murah, satu geometri otoritatif.

**DoD §20.13:**
- [ ] `scripts/geo_gate.py` di repo, nol dependency baru.
- [ ] `ok` memuat **delapan** syarat di atas, bukan `gap <= limit` saja.
- [ ] Bukti bergigi, tiga injeksi terpisah: (a) `row-gap: 0` pada baris KPI -> FAIL syarat 5 & 7; (b) kartu 2 dipaksa tinggi 170 -> FAIL syarat 4; (c) `.upload-studio-header` dihapus atau `position: absolute` -> FAIL syarat 6. Restore -> PASS.
- [ ] Tabel sembilan lebar dilampirkan pada commit merge oleh `@dorowani`.
- [ ] `BARE` tidak ada di suite mana pun.
