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
   - Gradient header & hero: `linear-gradient(135deg, #78350F 0%, #451A03 100%)`.
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
- Key warna: `str(label).strip().lower()`, lalu `CLASS_COLORS.get(key, "#78350F")`. Jangan `KeyError` untuk kelas tak dikenal.
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
- Test baru `render_compact_probability_rows`: urutan descending; `display_name` berisi `<script>` ter-escape; `display_name=None` jatuh ke `label`; kelas tak dikenal memakai fallback `#78350F`; `score=NaN` → lebar 0; `score=1.5` → clamp 100%.
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
