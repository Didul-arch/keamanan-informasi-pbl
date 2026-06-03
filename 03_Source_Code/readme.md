# Source Code

Folder ini berisi implementasi teknis proyek keamanan informasi. Struktur aktif saat ini dipisah menjadi tiga bagian utama: `backend`, `database`, dan `digital_signature`.

## 🚀 Cara Menjalankan Aplikasi (Lokal dengan Docker)

Aplikasi ini sudah dikonfigurasi agar bisa berjalan 100% secara lokal (termasuk Database PostgreSQL dan Penyimpanan File) menggunakan Docker Compose. Tidak perlu layanan cloud eksternal!

1. Buka terminal dan arahkan ke direktori `03_Source_Code`.
2. Jalankan perintah berikut:
   ```bash
   docker compose -f backend/docker-compose.yml up --build -d
   ```
3. Backend API akan menyala dan bisa diakses di: `http://localhost:8000`
4. Untuk melihat dokumentasi API (Swagger UI), buka: `http://localhost:8000/docs`
5. Semua file media (foto barang, dokumen identitas, bukti klaim) akan tersimpan secara otomatis di folder `03_Source_Code/storage/`.

---

## 📂 Struktur Folder

```text
03_Source_Code/
├── backend/           # Implementasi aplikasi utama: API, domain, infrastruktur, migrasi, dan konfigurasi
├── database/          # Session database dan model ORM
└── digital_signature/ # Autentikasi, JWT, hashing, dan keamanan
```

### Detail Struktur

```text
backend/
├── app/
│   ├── api/v1/          # Endpoint API (routers) dan schema (Pydantic)
│   ├── domains/         # Logika bisnis inti (Entity dan Service) per domain
│   └── infrastructure/  # Konfigurasi (.env parser), Repositori, dan Utils Storage
├── alembic/             # Konteks migrasi database
├── alembic.ini          # Config utama Alembic
├── Dockerfile           # Konfigurasi container backend
├── docker-compose.yml   # Orkestrasi Docker (Database + Backend)
├── requirements.txt     # Dependencies aplikasi
└── .env                 # Variabel konfigurasi khusus untuk lingkungan lokal docker

database/
├── session.py           # Konfigurasi AsyncSession, Engine SQLAlchemy, get_db dependency
└── models/              # Definisi tabel PostgreSQL (user, item, claim, dll.)

digital_signature/
├── auth_router.py       # Route untuk proses otentikasi (login, register)
├── auth_schema.py       # Validasi I/O untuk autentikasi
└── utils.py             # Verifikasi password, hashing (Argon2), pembuatan token JWT
```

## 📝 Catatan Tambahan

- **Pemisahan Concern**: Struktur ini memastikan fitur keamanan (autentikasi dan non-repudiation) tidak bercampur dengan _business logic_ biasa.
- **Konvensi Import**: Proyek ini menggunakan arsitektur _absolute import_ yang merujuk pada tiga root folder. Oleh karena itu, jika Anda tidak menggunakan Docker dan ingin me-run program secara manual via uvicorn/alembic, perintah CLI **harus dijalankan dari level direktori `03_Source_Code`**.
