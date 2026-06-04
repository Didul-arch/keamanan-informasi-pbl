# Testing Plan - FoundIt Security Implementation (3A)

Dokumen ini berisi rencana pengujian (*Testing Plan*) yang difokuskan pada pengujian pilar keamanan **3A (Authentication, Authorization, Accounting)** beserta sistem enkripsi yang telah diimplementasikan pada aplikasi FoundIt.

## Tabel Skenario Pengujian 3A

| ID | Kategori | Skenario Pengujian | Langkah Pengujian | Hasil yang Diharapkan | Status |
|---|---|---|---|---|---|
| **AUTH-01** | *Authentication* | Login dengan kredensial valid | Masukkan email dan password yang benar pada halaman Login | Pengguna berhasil masuk dan menerima *JWT Token* | `[x]` |
| **AUTH-02** | *Authentication* | Login dengan password salah | Masukkan email yang benar dengan password yang salah | Muncul pesan error "Invalid credentials" dan tidak mendapatkan *Token* | `[x]` |
| **AUTH-03** | *Authentication* | Akses API terproteksi tanpa Token | Panggil endpoint `GET /history/me` tanpa Header `Authorization` | Mengembalikan respon `401 Unauthorized` | `[x]` |
| **AUTH-05** | *Confidentiality* | Enkripsi data identitas | Registrasi pengguna baru dan upload gambar dokumen identitas | Gambar tersimpan dalam bentuk *ciphertext* (Fernet) di media penyimpanan | `[x]` |
| **AUTH-07** | *Confidentiality* | Akses gambar KTP oleh pihak tak berwenang | User biasa mencoba memanggil API `GET /users/{id}/identity-document` milik orang lain | Mengembalikan respon `403 Forbidden` | `[x]` |
| **AUTH-08** | *Authorization* | Akses endpoint Audit Logs oleh Admin | Login sebagai Admin dan panggil API `GET /admin/audit-logs` | Data Audit Logs berhasil dikembalikan | `[x]` |
| **AUTH-10** | *Authorization* | Bypass Endpoint API Admin | User biasa memanggil API `GET /admin/audit-logs` dengan tokennya | Mengembalikan respon `403 Forbidden` | `[x]` |
| **AUTH-14** | *Authorization* | Eksekusi Endpoint Klaim Ilegal | *Finder* "menembak" endpoint `PATCH /claims/{id}/mark-collected` via Postman | Mengembalikan respon `403 Forbidden` atau `404 Not Found` | `[x]` |
| **ACC-01**  | *Accounting* | Perekaman IP saat Login Sukses | Lakukan proses Login hingga berhasil | Tabel `audit_logs` menyimpan aksi "POST /api/v1/auth/login" beserta `ip_address` user | `[x]` |
| **ACC-02**  | *Accounting* | Perekaman IP saat Login Gagal | Lakukan proses Login dengan *password* salah | Tabel `audit_logs` menyimpan log aksi dengan `status_code` 401 dan `ip_address` | `[x]` |
| **ACC-05**  | *Accounting* | Paginasi Audit Logs | Admin mengecek pembatasan jumlah data dari API `Audit Logs` | Sistem membatasi jumlah data yang tampil menjadi maksimal sesuai parameter limit | `[x]` |
