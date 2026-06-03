# Keamanan Informasi

Repositori ini berisi seluruh artefak proyek keamanan informasi, mulai dari proposal dan analisis, dokumen desain, source code, sampai laporan akhir dan paper.

Secara teknis, proyek ini mengarah ke aplikasi lost and found berbasis FastAPI dengan pemisahan layer yang lebih jelas:

- `backend` untuk API, domain, service, dan alur aplikasi utama.
- `database` untuk session dan model ORM.
- `digital_signature` untuk autentikasi, JWT, hashing, dan utilitas keamanan.

Tujuan utama struktur ini adalah membuat kode lebih rapi, mudah dikembangkan, dan lebih mudah dipresentasikan sebagai luaran pertemuan.

## Struktur Folder

```text
01_Proposal_&_Analisis/   # Proposal dan analisis kebutuhan
02_Design_Documents/      # Dokumen desain dan arsitektur
03_Source_Code/           # Source code utama proyek
04_Reports_&_Paper/       # Laporan akhir dan paper
```

## Source Code

Implementasi aplikasi ada di [03_Source_Code](03_Source_Code). Di dalamnya:

```text
03_Source_Code/
├── backend/           # API FastAPI, router, domain, service, seed, dan Alembic
├── database/          # Session database dan model ORM
└── digital_signature/ # Auth, JWT, hashing, dan utilitas non-repudiation
```

Penjelasan detail struktur source code ada di [03_Source_Code/readme.md](03_Source_Code/readme.md).

## Cara Menjalankan Backend

Ini adalah cara yang paling praktis karena akan menjalankan backend, database PostgreSQL lokal, serta melakukan migrasi database (Alembic) secara otomatis dalam satu perintah.

```bash
cd 03_Source_Code
docker compose -f backend/docker-compose.yml up --build -d
```

Setelah service aktif, backend bisa diakses di:
- **API URL**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`


## Catatan

- Backend wajib dijalankan **dari dalam folder `03_Source_Code`** supaya *absolute import* ke paket `backend`, `database`, dan `digital_signature` bisa dikenali oleh Python.
- Fitur Autentikasi dan Non-Repudiation dikemas khusus di dalam `digital_signature/` agar tidak bercampur dengan business logic utama.
- Folder `database/` khusus menangani session dan ORM, dipanggil oleh service yang membutuhkan query data.
- Jika ingin melihat detail implementasi source code, buka [03_Source_Code/readme.md](03_Source_Code/readme.md).