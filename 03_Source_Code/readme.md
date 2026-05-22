# Source Code

Folder ini berisi implementasi teknis proyek keamanan informasi. Struktur aktif saat ini dipisah menjadi dua bagian utama: `backend` dan `database`.

## Struktur Folder

```text
03_Source_Code/
├── backend/           # Implementasi aplikasi utama: API, domain, infrastruktur, migrasi, dan storage
├── database/          # Session database dan model ORM
└── digital_signature/ # Autentikasi, JWT, hashing, dan non-repudiation
```

## Backend

Folder `backend/` memuat seluruh implementasi layanan utama, termasuk:

```text
backend/
├── app/
│   ├── api/v1/
│   │   ├── routers/
│   │   └── schemas/
│   ├── domains/
│   └── infrastructure/
├── alembic/
├── storage/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

database/
├── session.py
└── models/

digital_signature/
├── auth_router.py
├── auth_schema.py
└── utils.py
```

### Isi Utama Backend

- `backend/app/api/v1/routers/` untuk endpoint API.
- `backend/app/api/v1/schemas/` untuk schema request/response.
- `backend/app/domains/` untuk entity dan service per domain.
- `backend/app/infrastructure/` untuk konfigurasi dan repository aplikasi.
- `database/` untuk session database dan model ORM.
- `digital_signature/` untuk autentikasi, hashing, dan JWT.
- `alembic/` untuk migrasi database.
- `storage/` untuk file atau data pendukung aplikasi.

## Database

Folder `database/` sekarang dipakai untuk session dan model ORM.

## Catatan

- Struktur ini sudah memisahkan concern autentikasi ke `digital_signature/`.
- Jika nanti ada kebutuhan tambahan, struktur folder bisa diperluas tanpa mengubah pemisahan utama antara backend, database, dan digital_signature.
