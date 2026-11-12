# AGENTS.md - Standar & Konvensi Rekayasa Web

Dokumen ini adalah acuan operasional wajib untuk seluruh bot pengembang (`dara`, `parewa`, `padolo`, `banggapupa`, `dorowani`) saat bekerja di direktori ini.

---

## 1. Arsitektur & Teknologi
- **Prinsip Utama:** Modular, Type-Safe, Clean Architecture, Low Coupling.
- **Kerahasiaan:** Dilarang keras menaruh credentials, API tokens, atau database connection string langsung di dalam source code. Seluruh variabel sensitif wajib dibaca via environment variables (`.env`).
- **Skema & Kontrak:** Tidak ada implementasi kode sebelum struktur endpoint atau skema data didefinisikan secara tertulis oleh `@dara`.

---

## 2. Standar Frontend (`@parewa`)
- **UI/UX Polished:** Desain responsif (Mobile-first & Desktop-first), hierarki tipografi jelas, spacing konsisten.
- **State Handling Lengkap:** Komponen UI wajib menangani 4 status:
  1. `Idle` (keadaan normal)
  2. `Loading / Skeleton` (saat fetching data)
  3. `Empty State` (saat data kosong)
  4. `Error State` (pesan kegagalan ramah pengguna dengan tombol retry)
- **Validasi Sisi Klien:** Validasi ketat seluruh input form sebelum payload dikirim ke API.

---

## 3. Standar Backend (`@padolo`)
- **Zero-Trust Input:** Semua parameter request (body, query, params) wajib divalidasi dan disanitasi di sisi server.
- **Standar API HTTP:** 
  - Gunakan HTTP method yang sesuai (GET, POST, PUT, PATCH, DELETE).
  - Status code standar RFC (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `500 Internal Error`).
  - Struktur JSON response seragam:
    ```json
    {
      "success": true,
      "data": { ... },
      "message": "Operasi berhasil"
    }
    ```
- **Keamanan Bawaan:** Lindungi dari SQL Injection (gunakan parameterized query/ORM), hindari N+1 queries, pasang rate limiter pada rute sensitif.

---

## 4. Standar Review & Audit (`@banggapupa`)
- **Checklist Audit Keamanan:**
  - [ ] Bebas dari SQLi, XSS, CSRF, IDOR, dan SSRF.
  - [ ] Tidak ada hardcoded credentials atau credential leak di git log.
  - [ ] Error handler tidak membocorkan stack trace teknis atau internal server info ke client.
  - [ ] Algoritma efisien, tidak ada unbounded loops atau memory leak risks.
- **Hak Veto:** Berikan penolakan (BLOCK) jika ditemukan celah keamanan berstatus High/Critical atau pelanggaran arsitektur fatal.

---

## 5. Standar QA & Uji Mutu (`@dorowani`)
- **Prinsip Pengujian:** Bukti eksekusi nyata lebih tinggi dari asumsi verbal.
- **Kriteria Keberhasilan:**
  1. Build project bebas error (`exit code 0`).
  2. Test suite berjalan sukses tanpa fail.
  3. Linter dan format checker lulus.
  4. Bila ada UI aktif, verifikasi responsivitas DOM dan log konsol via browser tools.

---

## 6. Definition of Done (DoD)
Sebuah fitur atau modul hanya dianggap **SELESAI (DONE)** bila memenuhi rantai verifikasi:
1. Spesifikasi telah dirancang oleh `@dara` di `ARCHITECTURE.md`.
2. Frontend & Backend telah selesai diimplementasikan dengan penanganan error lengkap.
3. Telah diaudit dan disetujui (APPROVED) oleh `@banggapupa`.
4. Telah lolos uji build dan testing nyata oleh `@dorowani` dengan lampiran log sukses.
