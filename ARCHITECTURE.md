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
