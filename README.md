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

Penjelasan detail struktur source code ada di [03_Source_Code/README.md](03_Source_Code/README.md).

## Cara Menjalankan Backend

### Dengan Docker Compose

Ini cara yang paling praktis karena sekaligus menyalakan backend dan database PostgreSQL.

```bash
cd 03_Source_Code
docker compose -f backend/docker-compose.yml up --build
```

Setelah service aktif, backend bisa diakses di `http://localhost:8000`.

### Lokal

```bash
cd 03_Source_Code
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

## Migrasi Database

Setelah backend dan database siap, migrasi Alembic bisa dijalankan dari folder `03_Source_Code`:

```bash
cd 03_Source_Code
alembic -c backend/alembic.ini upgrade head
```

## Catatan

- Backend dijalankan dari folder `03_Source_Code` supaya paket `backend`, `database`, dan `digital_signature` bisa dipakai bersama.
- Folder `database/` dipisah untuk session dan model ORM.
- Folder `digital_signature/` dipakai untuk autentikasi/JWT dan utilitas keamanan.
- Jika ingin melihat detail implementasi source code, buka [03_Source_Code/README.md](03_Source_Code/README.md).