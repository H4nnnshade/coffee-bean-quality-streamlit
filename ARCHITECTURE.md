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

## 12. Spesifikasi Redesign Visual Menyeluruh (2026-11-21)

### Tujuan dan batas cakupan
Redesign seluruh komponen antarmuka aplikasi klasifikasi agar lebih terstruktur, ringkas, konsisten, responsif, dan mudah dibaca. Cakupan: shell halaman, header, navigasi/tab, ringkasan metrik, upload dan preview sampel, metadata/preprocessing, hasil klasifikasi tunggal dan perbandingan model, grafik probabilitas, status/loading/empty/error, tombol, input, card, tipografi, warna, border, shadow, gradient, dan jarak. Perubahan visual tidak boleh mengubah model, preprocessing, kontrak data, label/semantik hasil, atau alur inferensi.

### Sistem visual
- Gunakan palet kopi hangat sebagai aksen dengan permukaan netral terang; gunakan permukaan gelap secara selektif untuk hero/pengetahuan utama, bukan seluruh dashboard.
- Tetapkan token terpusat untuk warna, tipografi, spacing, radius, border, elevation, dan breakpoint; hindari nilai visual ad hoc yang berulang.
- Terapkan hierarki tipografi konsisten: sans-serif untuk UI dan judul, monospace tabular hanya untuk metrik teknis dan angka. Jangan menambah font eksternal wajib atau membuat layout bergantung pada jaringan eksternal.
- Gunakan ikon SVG konsisten, bukan emoji. Pertahankan kontras teks yang terbaca dan fokus keyboard terlihat.
- Komponen memakai spacing padat dan grid responsif mobile-first. Hindari kartu bersarang tanpa alasan, duplikasi logo, teks terpotong, overflow horizontal, dan informasi operasional yang tidak didukung data.
- Gunakan shadow/gradient secara hemat untuk membedakan hierarki, bukan sebagai ornamen pada setiap elemen. Animasi hanya mikro-interaksi singkat dan tidak boleh mengganggu pembacaan, pengunggahan, atau hasil klasifikasi; hormati `prefers-reduced-motion` dengan menonaktifkan gerakan non-esensial.
- Semua komponen interaktif mempertahankan state idle, loading, empty, dan error; error memberi pesan aman dan tindakan pemulihan yang jelas.
- Perubahan dinamis yang dirender sebagai HTML harus tetap di-escape; kelas warna hanya dari pemetaan tepercaya. Jangan menambah ketergantungan runtime eksternal.

### Alur dan prioritas informasi
1. Brand/header dan konteks tugas yang ringkas.
2. Ringkasan status/indikator yang tersedia dan benar.
3. Alur inspeksi sampel: unggah, preview, metadata, preprocessing, tindakan klasifikasi.
4. Hasil klasifikasi dan distribusi probabilitas; perbandingan model tetap ringkas, detail grafik mendapat lebar cukup.
5. Penjelasan kelas mutu/standar sebagai informasi pendukung.

### Kriteria responsif dan aksesibilitas
- Uji viewport minimum 390 px dan desktop 1440 px; tanpa scroll horizontal yang tidak disengaja, clipping, atau tabrakan antar-komponen.
- Uji keyboard/focus, kontras, dan semantic labels pada kontrol utama.
- Pertahankan label probabilitas analisis tunggal di kanan batang: nama kelas dan persentase satu desimal, tetap terlihat pada ukuran sempit.

### Iterasi berikutnya — Coffee Quality Lab

#### Arah yang disetujui
- Ganti polish CSS incremental dengan perubahan komposisi yang nyata: header ringkas → workspace unggah/pratinjau dua kolom → panel hasil mutu utama → probabilitas dan perbandingan model → kamus mutu sebagai pendukung.
- Dunia visual: latar krem hangat, panel espresso gelap sebagai fokus hasil, aksen tembaga, tipografi editorial dengan hierarki jelas. Layout desktop dan mobile mengikuti mockup konsep yang ditinjau sebelum implementasi.
- Mockup referensi kerja (scratch, bukan aset produksi): `/Users/agusfarhan/.hermes/profiles/parewa/cache/scratch/coffee-quality-lab-mockup.html`; screenshot: `concept-desktop.png`, `concept-mobile.png` di direktori scratch yang sama.

#### Syarat wajib sebelum/selama implementasi
- Ukur kontras WCAG 2.1 AA untuk teks kecil, label, dan tombol; perbaiki pasangan warna yang gagal sebelum ship. Hasil implementasi aktual: putih pada `#8E4A25` = 6.65:1 (minimum 6.56:1), teks `#6A5D51` pada `#F3ECDF` = 5.42:1 (minimum 5.34:1). Hover tombol `#733B1D` = 8.85:1; detail hasil pada espresso 11.15:1; disabled `#6A5D51` pada `#E8D9C7` = 4.53:1. Focus punya outline terlihat; perlu QA browser aktual.
- Semua label kelas utama berasal dari `ModelInferenceOutput.display_name`; seluruh model harus sepakat pada `predicted_class` sebelum satu label ditampilkan. Jika berbeda, tampilkan “Hasil berbeda antar model”, bukan label pemenang rekaan. Rincian kelas/probabilitas tetap dari setiap hasil aktual.
- Pertahankan upload, validasi, preprocessing, kontrak data, klasifikasi, dan pipeline inferensi apa adanya; lakukan perubahan UI-only.
- Sebelum merge/commit: uji state yang tersedia, keyboard/focus, reduced motion, viewport 390 px/1440 px, tanpa overflow, serta audit/QA sesuai DoD proyek.

### DoD redesign
- [x] @dara merilis spesifikasi ini sebelum implementasi visual dimulai.
- [x] @parewa inventaris komponen aktual, susun token/sistem visual, lalu implementasikan UI-only pada shell, navigasi, uploader/preview, metadata, hasil prediksi, grafik, dan kamus visual. File implementasi: `app.py` (urutan/komposisi UI saja), `ui/layout.py`, `ui/components.py`, dan `tests/test_ui_components.py`; alur validasi dan pemanggilan inferensi tidak diubah.
- [ ] @padolo cek tidak ada perubahan kontrak/backend/inference pipeline.
- [ ] @banggapupa audit keamanan, aksesibilitas dasar, konsistensi dan scope diff; berikan APPROVED atau temuan spesifik.
- [ ] @dorowani jalankan test suite, syntax/diff checks, dan browser QA pada 390 px serta desktop; verifikasi semua state dan log konsol bila dapat direproduksi.
- [ ] Catat batasan build/linter jika alat tidak tersedia; jangan klaim gate tidak dijalankan sebagai lulus.
- [ ] Commit/push hanya setelah audit dan QA final menyetujui; verifikasi hash remote dan worktree bersih.
