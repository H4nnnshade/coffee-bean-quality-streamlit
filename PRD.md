# PRD.md — Coffee Bean Quality Lab (Streamlit)

Versi: 1.2 · Otoritas: @dara · Status: S1/S2/S7 boleh jalan paralel sekarang. S3 tunggu S1+S2+S7 merged.

Dokumen ini adalah kontrak produk untuk fase berikutnya. Semua slice implementasi wajib merujuk §9. Perubahan scope hanya lewat revisi dokumen ini.

Riwayat revisi:
- 1.0 — PRD awal, keputusan D1–D5.
- 1.1 — Koreksi pasca-audit @banggapupa (T1–T5). Nama exception & path manifest dikunci. Kontrak `ComparisonResult` diubah agar kartu gagal tetap berposisi. Semantik 4-state UI ditetapkan (D6).
- 1.2 — D9: drop gate timeout, `TIMEOUT` dibuang dari `error_code`. D10: `ArtifactContainmentError → ARTIFACT_INTEGRITY → error` (bukan empty). Enum `error_code` final dikunci. Koreksi S2 (chunked hash + BytesIO, verifikasi di @cache_resource). Koreksi S7 (raise di resolver bukan import). Koreksi T4.4 (`with catch_warnings()`, bukan global). Kontrak UI dikunci: `render_empty_state(split, on_retry_split)`, `ui/state.py:resolve_result_state`, `MODEL_DISPLAY_NAMES` di S3. `display_name` dibuang dari `PerModelResult`.

---

## 1. Masalah yang Terverifikasi (bukan asumsi)

Bukti dari inspeksi repo `main` @ `b57ecb9`, ditambah pengukuran ulang @banggapupa di `.venv` (torch 2.8.0, pillow 11.3.0, sklearn 1.6.1).

| # | Temuan | Bukti | Dampak |
|---|---|---|---|
| P1 | `predict_all_models` sekuensial tanpa isolasi kegagalan | `services/predictor.py:87-99` | 1 artefak rusak → seluruh perbandingan 3 model gagal |
| P2 | Cold path masuk ke spinner pertama | `model_loader.py` load saat prediksi pertama; belum ada warmup | Persepsi "hang" di unggahan pertama |
| P3 | `joblib.load` (pickle) tanpa integritas artefak | `model_loader.py:151` | **RCE terbukti** (T1): payload pickle tereksekusi; 333 MB artefak `.joblib` di `models/svm/` tanpa verifikasi apa pun |
| P4 | `torch.load` tanpa `weights_only=True` eksplisit | `model_loader.py:104` | RCE via pickle bila versi torch dipin turun; sekarang aman hanya karena default library |
| P5 | 2 dari 4 state UI tidak terpakai | `render_empty_state`/`render_loading_state` hanya dipanggil dari `tests/`; `app.py` pakai spinner inline | Kontrak 4-state AGENTS.md §2 belum terpenuhi |
| P6 | Absolute path mesin dev di source | `config.py:12` `/Users/agusfarhan/Downloads/...` | Pelanggaran 12-Factor; bocor struktur host |
| P7 | Tanpa batch, riwayat, ekspor | `app.py` single upload | Tidak ada artefak hasil untuk laporan skripsi |
| P8 | Confidence = softmax atas margin SVM | `predictor.py:_stable_softmax` | Angka tinggi bisa menyesatkan pada sampel ambigu |
| P9 | Path artefak disusun naif | `config.py:32-39` | Traversal terbukti (`../../../../etc/passwd` → escape base); sekarang tertahan hanya oleh whitelist di loader |
| P10 | Gate ukuran upload bergantung atribut objek | `ui/components.py:246` `getattr(uploaded_file, "size", 0)` | Bila `size` absen/nol, gate 10 MB terlewati tanpa cadangan |
| P11 | `Image.MAX_IMAGE_PIXELS` dimutasi global saat import | `ui/components.py:45` | Efek samping lintas modul; 25 MP hanya `DecompressionBombWarning` (ambang raise = 2× limit) |
| P12 | `warnings.filterwarnings("ignore", ".*Trying to unpickle estimator.*")` | `model_loader.py:12` | Meredam sinyal justru saat artefak asing di-unpickle |

---

## 2. Pengguna & Tujuan

- **P1 — Peneliti/mahasiswa (utama):** membandingkan 3 backbone CNN-SVM pada 3 skenario split, butuh bukti angka yang bisa dilampirkan.
- **P2 — Dosen/penguji:** membaca hasil tanpa perlu tahu PyTorch; butuh label mutu yang jujur soal ketidakpastian.

**Tujuan metrik:** p90 latensi hangat < 400 ms; 100% kegagalan artefak terdeteksi **sebelum** unpickle; hasil dapat diekspor.

---

## 3. Scope

**Fase 1 (dokumen ini, dikerjakan sekarang):** hardening service layer, warmup lazy per split, integritas artefak fail-closed, isolasi kegagalan per-model, 4-state UI dipakai nyata, ekspor hasil, manifest checksum ter-commit, benchmark terdokumentasi.

**Fase 2 (deferred, tidak dikerjakan):** HTTP API publik, batch upload, riwayat persisten (DB), multi-user auth, kalibrasi probabilitas (Platt/isotonic), manifest sidecar `.sig` (detached signature).

**Non-scope:** perubahan arsitektur model, retraining, perubahan skema split.

---

## 4. Kontrak Domain

Reuse `core/schemas.py` tanpa breaking change pada tipe yang sudah dipakai. Tambahan aditif (D5a — revisi 1.1, menggantikan bentuk `results`+`failures` terpisah):

```python
REVIEW_THRESHOLD: float = 0.55     # core/constants.py — batas tunggal, bukan literal di UI

MODEL_DISPLAY_NAMES: Dict[str, str] = {   # core/constants.py — satu-satunya sumber label kartu
    "MobileNetV3-Small": "MobileNetV3-Small",
    "ShuffleNetV2":       "ShuffleNetV2",
    "EfficientNet-B0":    "EfficientNet-B0",
}
# Re-export via core/__init__.py __all__ — wajib, karena core/__init__ bukan wildcard

# error_code enum final (D9: TIMEOUT dibuang, D10: containment → ARTIFACT_INTEGRITY):
# ARTIFACT_MISSING   — ModelArtifactNotFoundError       → state: empty (recoverable)
# ARTIFACT_INTEGRITY — ChecksumMismatchError            → state: error
#                    — ArtifactContainmentError          → state: error (bukan empty; ini serangan)
# INVALID_REQUEST    — ValueError whitelist             → state: error
# INFERENCE_ERROR    — semua kecualikan lain            → state: error

@dataclass(frozen=True)
class PerModelResult:
    model_key: str                     # persis string MODEL_KEYS, bukan slug kedua
    # display_name DIHAPUS — pakai MODEL_DISPLAY_NAMES[model_key] di UI; satu sumber kebenaran
    status: str                        # "ok" | "failed"
    predicted_class: Optional[str]     # None saat failed
    confidence: Optional[float]        # softmax atas margin, BUKAN probabilitas terkalibrasi
    probabilities: Optional[Dict[str, float]]
    error_code: Optional[str]          # lihat enum di atas; TIMEOUT tidak ada (D9)
    latency_ms: Optional[float]

    @property
    def needs_review(self) -> bool:
        return self.status == "ok" and self.confidence < REVIEW_THRESHOLD
        # 0.5499 → True, 0.55 → False (< bukan <=)

@dataclass(frozen=True)
class ComparisonResult:
    split_ratio: str
    models: List[PerModelResult]       # panjang == len(MODEL_KEYS), urutan == MODEL_KEYS
    degraded: bool                     # 1..N-1 gagal
    failed_count: int
    total_time_ms: float
```

Aturan kontrak:
- **Invarian panjang:** `len(models) == len(MODEL_KEYS)` di semua jalur, termasuk saat semua gagal. Model gagal = entri berstatus `failed`, **bukan absen**. Ini yang membuat gate ordering @dorowani bisa dibuktikan di UI, bukan hanya di service.
- Urutan `models` selalu `MODEL_KEYS`; tidak ada sorting ulang.
- `model_key` memakai string kanonis `MODEL_KEYS` (`"MobileNetV3-Small"`, `"ShuffleNetV2"`, `"EfficientNet-B0"`). Tidak ada peta slug kedua — satu sumber kebenaran, satu tabel lebih sedikit untuk salah.
- `needs_review` adalah **properti terhitung**, bukan field tersimpan: tidak bisa desinkron dari `confidence`. Batas ketat `< 0.55` (0.55 tepat = tidak ditandai). Diuji inline `0.5499 → True`, `0.55 → False`.
- `predict_all_models` → `ComparisonResult`. Signature publik berubah; `app.py` + `tests/test_pipeline.py` diperbarui dalam diff yang sama.
- `render_comparison_section` menerima `ComparisonResult`, bukan `List`.

**Nama exception dikunci (D8), di `core/exceptions.py`:**

```python
class ModelArtifactNotFoundError(Exception): ...      # sudah ada, dipakai ulang
class ChecksumMismatchError(Exception): ...           # mismatch hash ATAU file yatim/di luar manifest
class ArtifactContainmentError(Exception): ...        # path resolve() keluar MODEL_BASE_DIR
```

`ChecksumMismatchError` adalah nama yang dipakai tripwire @dorowani dan audit @banggapupa. `ModelFailure.reason` = `ARTIFACT_INTEGRITY` untuk kedua kelas kegagalan integritas; UI tidak pernah merender teks exception.

**D1 — Keputusan: tidak ada HTTP API di Fase 1.** Kontrak API usulan @padolo (FastAPI, 413/415/422, rate limit) diparkir sebagai Fase 2. Alasan: satu konsumen (Streamlit, in-process), menambah attack surface upload yang harus diaudit + 6 gate QA tanpa nilai pengguna. Boundary tetap ditegakkan di `services/input_gate.py` supaya adapter HTTP nanti tipis.

---

## 5. Pipeline & Performa

1. **Warmup lazy per split (D6a).** Tidak ada eager load 3 split saat startup. Warmup hanya untuk split default di thread background; split lain dimuat saat pertama dipilih, dengan copy "Menyiapkan model untuk skenario ini (pertama kali ±2.0–2.5 s)". Flag `READY` via `threading.Event`. Alasan: eager 3 split = 628 MB RSS dan ~2.8 s yang dibayar semua pengguna untuk split yang mungkin tidak dipakai.
2. **Paralelisasi = conditional, default OFF** (D2). `ENABLE_PARALLEL` env, `ThreadPoolExecutor(max_workers=3)`. Hanya jadi default bila bench 3-model **≥20% lebih cepat** dari sekuensial di mesin target. Jika tidak menang (contention intra-op torch), slice dibatalkan dan dicatat di README.
3. **Integritas artefak = fail-closed (D7).** Detail di §6.
4. **Target:** p90 hangat < 400 ms, total 3 model hangat < 250 ms bila paralel menang; **cold ≤ 4.5 s per split yang dipakai** termasuk inferensi pertama (D6b). Verifikasi manifest 325 ms/18 file sudah masuk budget; tidak ada alasan naikkan gate.

---

## 6. Validasi & Keamanan

### 6.1 Integritas artefak (T1 — blocker)

Manifest: **`models/MANIFEST.sha256`**, path dikunci, **di-commit** (bukan digenerate runtime). Format: baris `sha256<dua spasi>path-relatif-terhadap-repo`, tepat **18 entri** (9 `.pt` + 9 `.joblib`).

Syarat yang tidak bisa dinegosiasikan:
1. Hash diverifikasi **sebelum** `torch.load` / `joblib.load`, hard-fail `ChecksumMismatchError`. Bukan warning.
2. **Fail-closed dua arah:** (a) manifest hilang → tolak load; (b) file artefak ada di `models/` tapi tidak tercatat di manifest → tolak juga. Tanpa (b), drop 1 artefak baru = bypass penuh.
3. Assert manifest berisi tepat 18 entri, path relatif, tanpa duplikat; himpunan path di disk == himpunan di manifest. Gate alternatif bebas I/O: `set(manifest) == set(git ls-files models/) - {"models/MANIFEST.sha256"}`.
4. **Manifest tidak memuat dirinya sendiri** (`models/MANIFEST.sha256`); self-referential = hash berubah tiap regenerate.
5. `torch.load(..., weights_only=True)` **eksplisit** (T3). Semua 9 checkpoint load bersih dengan param ini → nol risiko regresi.
6. Hapus `warnings.filterwarnings("ignore", message=".*Trying to unpickle estimator.*")` (`model_loader.py:12`) — itu meredam sinyal saat artefak asing di-unpickle.
7. Generator: `scripts/gen_manifest.py`, dipakai manual oleh maintainer, output di-review di diff. Bukan dijalankan saat runtime.
8. **Pola I/O wajib (T8):** chunked SHA-256 (1 MB chunk) → `BytesIO` → `load(buf)`. Jangan `read()` utuh lalu `load(path)` — itu 2× I/O dan 2× RSS untuk file 55 MB. Kedua loader (torch, joblib) menerima buffer; tripwire @dorowani tetap bisa membedakan "hash dulu" vs "load dulu" tanpa mengubah jalur sah.
9. Verifikasi di dalam `@cache_resource` (`load_feature_extractor`/`load_svm_classifier`), bukan saat startup bebas-cache — maksimal 1× per artefak per proses. **Jangan** tambah cache skip berbasis `(path, size, mtime)`; 325 ms/18 file hanya dibayar sekali, itu harga fail-safe.

**Residual risk (masuk §11):** checksum melindungi dari korupsi/tamper file dan artefak tak terdaftar, **bukan** dari artefak jahat yang hash-nya ikut diubah di repo. `.joblib` dari sumber tak dipercaya = RCE, titik. Artefak hanya dari build pipeline, tidak pernah dari upload pengguna. Signature sidecar = Fase 2.

### 6.2 Containment path (T2)

Setelah whitelist, tetap `p.resolve()` lalu `p.is_relative_to(MODEL_BASE_DIR)`; False → `ArtifactContainmentError`. Whitelist primer, containment sekunder — dua lapis, karena S1 memindahkan whitelist ke `input_gate.py` dan urutan panggil bisa salah.

### 6.3 Input gate terpusat (T4)

`services/input_gate.py` jadi satu-satunya pintu validasi upload, dipakai `ui/components.py`:

1. **Ukur panjang buffer nyata**, jangan percaya `uploaded_file.size` (P10). `size` hilang/nol bukan izin lolos.
2. **Ekstensi divalidasi server-side** (`Path(name).suffix` vs `ALLOWED_EXTENSIONS`); `type=` di `st.file_uploader` hanya hint UI.
3. **Re-encode wajib:** decode → `convert("RGB")` → `save(BytesIO, "PNG")` → buka ulang. Itu satu-satunya cara menjamin tidak ada trailing bytes/EXIF aneh yang ikut downstream, dan invariannya bisa diuji: `assert b"PK\x03\x04" not in reencoded` untuk polyglot JPEG+ZIP, `Image.open(reencoded).format == "PNG"`.
4. `Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS` **dipindah** dari import-time `ui/components.py:45` ke `input_gate.py`. Band warning dinaikkan jadi error via `with warnings.catch_warnings(): warnings.simplefilter("error", Image.DecompressionBombWarning)` **hanya di dalam jalur buka citra**, bukan di import-level — itu juga mutasi global (sama seperti `Image.MAX_IMAGE_PIXELS` yang mau dihapus). Alasan butuh error bukan warning (P11): default PIL 89.5 MP dan 25 MP hanya menghasilkan `DecompressionBombWarning`, tidak raise.
5. Whitelist split/model diterapkan di gate, dipakai uploader dan service — bukan hanya di loader.

### 6.4 Lain-lain

- `config.py`: hapus default absolute path; `MODEL_DIR` env-only, fallback `BASE_DIR/models`. **`import config` tanpa `MODEL_DIR` lulus** (tidak raise di import-level — itu membunuh test suite dan Streamlit Cloud). Raise terjadi di `get_checkpoint_path`/`get_svm_path` saat resolve, setelah containment check.
- Pesan error ke UI: tanpa stack trace, tanpa path absolut (CWE-209).
- **D3:** `needs_review` (confidence < 0.55) → badge amber "Perlu Review Manual" di kartu, hasil tetap tampil. Disclaimer tetap: skor = softmax atas margin SVM, belum terkalibrasi; bukan probabilitas statistik.

---

## 7. QA Gates (wajib, bukan lampiran)

**Urutan gate: Integrity → semua gate lain.** Tidak ada uji fungsional yang ditandatangani sebelum fail-closed lulus. Kalau integrity belum ada, QA tidak jalan — bukan "jalan sambil menunggu".

| Gate | Kriteria | Pemilik |
|---|---|---|
| Integrity | Prasyarat semua gate. **Event-order test**: monkeypatch `joblib.load`/`torch.load` jadi tripwire `fail("unpickle dipanggil")`; kirim `.joblib` tamper → test lulus dengan tripwire **tak pernah tersentuh**. `assertRaises` saja tidak cukup: ia bisa lolos walau hash dicek setelah unpickle | @dorowani |
| Integrity coverage | Manifest hilang → tolak; artefak yatim (ada di disk, tak di manifest) → tolak; tepat 18 entri, tanpa duplikat, path relatif; himpunan disk == himpunan manifest | @dorowani |
| Weights-only | `torch.load` dipanggil dengan `weights_only=True` eksplisit — assert pada call args, bukan pada default library | @dorowani |
| Cold start | **≤ 4.5 s per split yang dipakai** termasuk inferensi pertama. Proses fresh per pengukuran, N=5, laporkan **max** + median. Tidak ada eager 3-split | @dorowani |
| Warm latency | 100 iterasi, lapor p50/p90/p99; p90 < 400 ms | @dorowani |
| Fan-out | bench 1 vs 3 vs 8 worker; default ON hanya bila ≥20% menang | @dorowani |
| Memory | RSS pasca-load 3 split **≤ 650 MB**; lalu 50 request/split berurutan: RSS akhir − pasca-warm **≤ 5 MB** | @dorowani |
| Ordering | `len(models) == len(MODEL_KEYS)` dan urutan == `MODEL_KEYS` di semua split, **termasuk saat 1 dan saat 2 model gagal** | @dorowani |
| Degraded path | Rusak 1 artefak → render ≤ cold budget, 2 kartu `ok` + 1 kartu `failed` terlihat, banner amber, urutan utuh | @dorowani |
| Empty vs error (D6c/D10) | `ARTIFACT_MISSING` → empty state; `ARTIFACT_INTEGRITY`/`INVALID_REQUEST`/`INFERENCE_ERROR` → error state + retry. `ArtifactContainmentError` → `ARTIFACT_INTEGRITY` → error (bukan empty). Tidak ada 200 palsu | @dorowani |
| Empty-state button | AppTest: klik tombol empty-state **benar-benar mengubah split** (assert state setelah klik, bukan hanya assert tombol ada). Callback via `on_click=setter` — tidak ada `StreamlitAPIException` | @dorowani |
| Checksum | Tamper 1 byte `.pt`/`.joblib` → `ChecksumMismatchError` → `ARTIFACT_INTEGRITY`, tidak crash | @dorowani |
| Negative upload | >10 MB, 10 MB+1 B, `size` absen, ekstensi di luar whitelist, `.jpg` isi PDF, polyglot JPEG+ZIP, 16 MP pass / 16 MP+1 fail, EXIF bomb, `../` di split/model | @dorowani |
| Re-encode invarian | `zip_marker not in reencoded`, `format == "PNG"`, tanpa trailing bytes | @dorowani |
| Warning→error | 25 MP harus **raise**, bukan `Warning` (regresi diam-diam paling mudah lolos review) | @dorowani |
| Error hygiene | Body/UI tanpa `Traceback`, `File "`, `/Users/` — assert regex, **termasuk di jalur degraded** | @dorowani |
| Visual | 4 state nyata (idle/loading/empty/error) di 1440px + 390px, `window.onerror` bersih | @dorowani |
| Suite | `PYTHONPATH=. .venv/bin/python -m unittest discover -s tests` hijau, + test baru | @dorowani |

---

## 8. Keputusan Arsitek

- **D1** HTTP API ditunda ke Fase 2. Boundary dipindah ke `services/input_gate.py`.
- **D2** Paralelisasi conditional, default OFF, mati bila bench tidak menang.
- **D3** Ambang review manual 0.55 = badge amber non-blocking, plus disclaimer kalibrasi. Batas tunggal `REVIEW_THRESHOLD` di `core/constants.py`.
- **D4** Partial failure: degraded success — kartu berhasil + kartu gagal + banner. Total gagal tidak pernah jadi sukses diam-diam.
- **D5** `ModelFailure.reason` / `PerModelResult.error_code` = string stabil; UI tidak pernah merender exception mentah.
- **D5a** Kontrak `ComparisonResult` memakai **satu list berposisi** (`models`), bukan `results`+`failures` terpisah. Gagal = entri `failed`, bukan absen. Alasan: gate ordering dan gate degraded path harus bisa dibuktikan dari UI; list terpisah membuat model gagal "hilang" dan invarian panjang tidak teruji.
- **D6** Semantik 4-state UI:
  - **idle** = belum ada citra di session → `render_idle_state()`.
  - **loading** = inferensi berjalan → `render_loading_state()` menggantikan `st.spinner` inline di `app.py`.
  - **empty** = citra valid, **semua** model gagal `ARTIFACT_MISSING` → `render_empty_state(split, on_retry_split)`. `on_retry_split` = `next(s for s in ALLOWED_SPLITS if s != failed_split)`, dihitung di `app.py`, diteruskan sebagai argumen — bukan dihitung di dalam callback (closure tidak dievaluasi ulang tiap rerun). Tombol via `on_click=_set_split_from_button, args=(on_retry_split,)` (D6/T6 — tulis langsung ke session_state setelah widget instantiated = `StreamlitAPIException`).
  - **error** = semua gagal `ARTIFACT_INTEGRITY`/`INVALID_REQUEST`/`INFERENCE_ERROR`, atau exception tak terduga → `render_error_state()` + retry.
  - Empat state eksklusif; masing-masing punya test.
  - **D6a** warmup lazy per split, bukan eager 3 split.
  - **D6b** gate cold ≤ 4.5 s per split dipakai (menggantikan 3.5 s).
  - **D6c** pemetaan gagal → state: lihat tabel §7 dan D10.
- **D7** Manifest `models/MANIFEST.sha256` di-commit, verifikasi sebelum unpickle, fail-closed dua arah termasuk artefak yatim.
- **D8** Nama dikunci: `ChecksumMismatchError`, `ArtifactContainmentError`, `models/MANIFEST.sha256`.
- **D9** Gate timeout dihapus; `TIMEOUT` tidak ada di `error_code`. Single-process torch tidak bisa benar-benar membatalkan inferensi yang hang tanpa `ProcessPoolExecutor` (628 MB/proses). Dicatat §11 butir 6.
- **D10** `ArtifactContainmentError` → `ARTIFACT_INTEGRITY` → state **error**, bukan empty. Ini serangan, bukan ketersediaan artefak. Tidak ada tombol "pilih split lain" di state ini.
- **D11** `ui/state.py: resolve_result_state(models: List[PerModelResult]) -> Literal["ok","partial","empty","error"]` — tidak boleh `import streamlit`, tidak boleh `import ui.components`. Murni petakan `error_code` → state; bisa diuji tanpa mock Streamlit. Owner: @parewa (S5).
- **D12** `render_empty_state` signature: `(split: str, on_retry_split: str) -> None`. Body lama ("Belum ada citra") salah secara semantik; wording baru: "Skenario `{split}` belum punya artefak model" + aksi "Pilih {on_retry_split}".
- **D13** `MODEL_DISPLAY_NAMES` di `core/constants.py`, re-export via `core/__init__.py __all__` — dikunci di S3, bukan S5. Tanpa ini S5 `ImportError` saat kompile. `display_name` dihapus dari `PerModelResult`.

---

## 9. Slice Implementasi

| # | Slice | File | Owner | Skill wajib | Depends |
|---|---|---|---|---|---|
| S1 | Input gate + whitelist terpusat | `services/input_gate.py`, `ui/components.py`, `tests/test_input_gate.py` | @padolo | `hybrid-ml-inference` | — |
| S2 | Integritas artefak fail-closed + `weights_only` + manifest | `services/model_loader.py`, `scripts/gen_manifest.py`, `models/MANIFEST.sha256`, `core/exceptions.py`, `tests/test_integrity.py` | @padolo | `hybrid-ml-inference` | — |
| S3 | `ComparisonResult` berposisi + isolasi kegagalan + containment + warmup lazy + `MODEL_DISPLAY_NAMES` | `core/schemas.py`, `core/constants.py`, `core/exceptions.py`, `core/__init__.py`, `services/predictor.py`, `services/model_loader.py`, `tests/test_pipeline.py` | @padolo | `hybrid-ml-inference` | S1, S2, S7 |
| S4 | Benchmark fan-out (blocking decision D2) | `tests/test_perf.py` (+ hasil di README) | @dorowani | `visual-web-qa` | S3 |
| S5 | UI: 4-state nyata (D6/D11/D12), banner degraded, badge review manual, `ui/state.py`, konsumsi `ComparisonResult` | `app.py`, `ui/components.py`, `ui/state.py`, `tests/test_ui_components.py` | @parewa | `impeccable`, `frontend-design` | S3 |
| S6 | Ekspor hasil (CSV + JSON) | `services/export.py`, `ui/components.py`, `tests/test_export.py` | @parewa | `frontend-design` | S3 |
| S7 | `config.py` 12-Factor (hapus absolute path, gagal jelas) | `config.py`, `tests/test_negative.py` | @padolo | `hybrid-ml-inference` | — |
| S8 | Audit keamanan S1/S2/S3/S7 | diff review | @banggapupa | `web-guidelines-review` | S1,S2,S3,S7 |
| S9 | QA penuh §7 | eksekusi | @dorowani | `visual-web-qa`, `browser-qa` | S8 APPROVED |

S6 ekspor: CSV satu baris per (split, model) dengan kolom wajib `model_key, status, predicted_class, confidence, needs_review, error_code, split_ratio`; model gagal **tetap punya baris** dengan `status=failed` — tanpa itu baris gagal terbaca sebagai hasil valid di lampiran skripsi. Plus JSON penuh `ComparisonResult`. Tanpa PII, tanpa path host.

S2 dan S3 sama-sama menyentuh `services/model_loader.py`; S3 milik urutan setelah S2 merge. S7 (config) juga menyentuh loader, sehingga S7 mendarat sebelum S3 untuk menghindari konflik `config.py`.

---

## 10. Definition of Done

1. Semua slice S1–S7 merged, test suite hijau dengan test baru.
2. §8 keputusan tercermin di kode (assertable di test).
3. @banggapupa APPROVED tanpa temuan High/Critical.
4. @dorowani melampirkan log §7 (integrity tripwire, latensi, RSS, visual).
5. `ARCHITECTURE.md` §4/§5 disinkronkan dengan dokumen ini.

---

## 11. Batasan yang Diakui (known limitations)

1. **Confidence tidak terkalibrasi.** `_stable_softmax` atas margin SVM = skor ordinal, bukan probabilitas statistik. Badge review manual hanya mitigasi tampilan. Kalibrasi Platt/isotonic = Fase 2.
2. **Integritas bukan provenance.** Checksum menahan korupsi/tamper file dan artefak tak terdaftar, tapi tidak menahan artefak jahat yang hash-nya ikut diubah. `.joblib`/`.pt` dari sumber tak dipercaya = RCE. Artefak hanya dari build pipeline; tidak pernah dari upload. Detached signature (`.sig`) = Fase 2.
3. **Single-process, single-user.** Tidak ada isolasi antar-sesi, tidak ada rate limit HTTP (tidak ada HTTP). Sandbox eksekusi model di luar scope.
4. **Warmup lazy** berarti split non-default tetap membayar cold ≤4.5 s pada pemakaian pertama; itu diterima sebagai trade-off memori (628 MB baseline 3-split).
5. **Baseline angka v1.0 yang direvisi:** cold 3.5 s → 4.5 s per split; "RSS stabil" → ≤650 MB pasca-load 3 split + drift ≤5 MB/50 request. Angka 45 test, cold 3356.7 ms, dan RSS 9.8→507.5→628.2 MB adalah pengukuran @banggapupa dan dicatat sebagai klaim terverifikasi-pihak-ketiga sampai @dorowani menjalankan ulang setelah S2 mendarat.
6. **Timeout inferensi tidak bisa ditegakkan (D9).** `ThreadPoolExecutor.result(timeout=N)` meninggalkan thread worker tetap jalan — RSS naik tanpa batas; bertabrakan dengan gate memory. `ProcessPoolExecutor` yang benar-benar membunuh kerja butuh 628 MB/proses. Gate timeout dihapus; backbone yang hang membuat kartu menunggu hingga forward selesai. Perbaikan nyata = Fase 2.

---

## 12. Sistem Desain (DESIGN.md — Arabica Aurora)

D13 mengunci token visual sebagai kontrak, bukan preferensi. Sumber tunggal: `DESIGN.md`
(frontmatter YAML = nilai normatif) + turunan mesin `theme.css` (Tailwind v4 `@theme`) dan
`tokens.json` (W3C DTCG). Ketiganya di-commit; tidak ada warna hex baru yang boleh masuk
`ui/` tanpa lebih dulu masuk `DESIGN.md`.

**Kenapa dua palet:** `ARCHITECTURE.md` §19 mengunci palet terang "vibrant crypto"
(`#F8FAFC`) dengan lantai kontras 4.8:1. `DESIGN.md` mendefinisikan pasangan gelapnya
(`#0A0A0C`) untuk konsol inspeksi. Aturan §19 tidak dicabut: token gelap tetap tunduk pada
ambang AA yang sama, dan stop gradien KPI `115deg` yang grandfathered di §19.2 dipakai
identik di kedua palet.

| Peran | Token | Nilai | Kontras |
|---|---|---|---|
| Field | `colors.neutral` | `#0A0A0C` | — |
| Kartu | `colors.surface` | `#141416` | — |
| Inset | `colors.surface-sunken` | `#101012` | — |
| Aksi terisi | `colors.action` | `#C2410C` | 5.18:1 vs putih |
| Aksen interaksi | `colors.primary` | `#FF6B4A` | 7.02:1 di neutral |
| Teks utama / sekunder / muted | `text-primary/secondary/muted` | `#FFFFFF` / `#A8A8B3` / `#8A8A93` | 20.4 / 8.40 / 5.79:1 |
| Positif / bahaya | `positive` / `danger` | `#4ADE80` / `#FF5C5C` | 11.35 / 6.53:1 |

**Larangan keras:**
1. Teks putih di atas `#FF6B4A` (2.82:1, FAIL) — tombol terisi wajib `#C2410C`.
2. `hairline #5A5A63` sebagai warna teks (2.90:1). Hanya untuk divider 1px, gridline, dan
   stroke ikon non-aktif; stroke ikon terendah yang sah `#6B6B73` (≥3:1, SC 1.4.11).
3. Kartu di dalam kartu. Region inset memakai `surface-sunken`, bukan kartu kedua.
4. Elevasi keempat. Tiga level saja: flat (border hairline), raised (tooltip/popover/
   nav aktif), glow (CTA primer + stroke chart).
5. Angka non-monospace. Setiap nilai yang bisa berubah antar-render (confidence, latensi,
   dimensi, persen probabilitas, rasio split) wajib `JetBrains Mono` + `tabular-nums`.

**Verifikasi:** `npx -y @google/design.md lint DESIGN.md` → 0 error, 8 warning
`orphaned-tokens` (token struktural yang sengaja tidak dipakai komponen: `neutral`,
`border-subtle`, `border-medium`, `text-secondary`, `hairline`, tiga stop aurora). Warning
ini diterima; menambahkan komponen dummy untuk membungkamnya akan mengotori spec.

**Status Figma:** file `Arabica Aurora — Coffee Bean Quality Dashboard`
(`fucnagV9oPMSG5eADRqRgK`) berisi frame 1440×900 dengan 178 node editable — rail sidebar,
header, 4 kartu KPI gradien, kartu chart keyakinan, panel hasil klasifikasi kanan, deck kamus
mutu. Variable collection 24 token + 10 text style dibuat dari `DESIGN.md`; tidak ada teks
ter-flatten, tidak ada screenshot yang ditempel sebagai pengganti layer.

---

## 13. Deployment (Streamlit Community Cloud)

**Target:** situs publik, bukan `localhost`. `streamlit run` lokal hanya untuk smoke test.

| Item | Nilai |
|---|---|
| Repo | `github.com/H4nnnshade/coffee-bean-quality-streamlit` (PUBLIC) |
| Branch deploy | `fix/vibrant-crypto-harmonization` sampai PR ke `main` di-merge |
| Entry point | `app.py` |
| Python | 3.11 (bukan 3.9 — `torch 2.8` wheel macOS-only tidak tersedia untuk Cloud) |
| Secrets | tidak ada. Aplikasi tidak membaca kredensial apa pun. |
| Upload map | `maxUploadSize = 10` MB dari `.streamlit/config.toml` |

**Blocker yang diakui:**
1. **Artefak 413 MB ter-track di Git** (9 `.pt` + 9 `.joblib`). Clone Cloud akan lambat dan
   berisiko kena batas build. Mitigasi Fase 2: pindah ke Git LFS atau unduh artefak saat
   runtime dari release asset, dengan `MANIFEST.sha256` tetap jadi gerbang integritas.
   Sampai itu dilakukan, deploy tetap mungkin tetapi first-build tidak cepat.
2. **Sign-in Cloud butuh OAuth GitHub milik @H4nnnshade.** Tidak ada yang bisa mengerjakannya
   dari pihak agent tanpa sesi peramban pemilik akun. Langkah manusia: buka
   `share.streamlit.io` → Continue to sign-in → authorize GitHub → New app → pilih repo,
   branch, `app.py`.
3. **`MANIFEST.sha256` fail-closed.** Bila artefak tidak ikut ter-clone, aplikasi menolak
   inferensi dan menampilkan empty state — bukan hasil palsu. Ini perilaku benar, bukan bug.

**Definisi "live":** URL `*.streamlit.app` merespons 200, judul halaman memuat
`Arabica Vision AI`, dan unggahan citra mengembalikan kartu hasil (bukan banner artefak
hilang). Sampai ketiganya terpenuhi, status dilaporkan **belum live**.
