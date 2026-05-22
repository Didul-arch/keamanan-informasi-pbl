# Backend SIPESAT - Lost and Found IPB

Backend ini sekarang hanya berisi API, domain, service, repository, dan Alembic. Concern database ada di [../database](../database) dan autentikasi/JWT ada di [../digital_signature](../digital_signature).

## Tech Stack

- Framework: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy 2.0 (Async)
- Driver DB: asyncpg

## Menjalankan Backend

1. Instal dependensi:

```bash
cd ..
pip install -r backend/requirements.txt
```

2. Jalankan server:

```bash
uvicorn backend.app.main:app --reload
```

3. (Opsional) Jalankan seeding data awal:

```bash
python -m backend.app.seed
```

## Endpoint Aktif Saat Ini

- `GET /` - health check.
- `POST /users/` - membuat user.
- `POST /items/report` - melaporkan barang hilang.
- `GET /items/` - menampilkan daftar item.

## Checklist Feature Progress

### A. Core Lost and Found
- [x] Lapor barang hilang.
- [ ] Lapor barang ditemukan.
- [x] Lihat daftar barang.
- [ ] Lihat detail barang.
- [ ] Proses claim barang.
- [ ] Alur perubahan status item (`lost/found/claimed`) konsisten via API.

### B. Authentication dan Verifikasi Identitas
- [ ] Login mahasiswa IPB (`@apps.ipb.ac.id`).
- [ ] Token authentication (JWT).
- [ ] Guest mode dengan pembatasan hak akses.
- [ ] Upload dokumen identitas (KTM/KTP).
- [ ] Verifikasi identitas oleh admin/petugas.

### C. RBAC
- [ ] Definisi role (`guest`, `student`, `verified_student`, `admin`, `super_admin`).
- [ ] Matriks permission per role.
- [ ] Proteksi endpoint berbasis role.
- [ ] Riwayat perubahan role.

### D. Admin AAA

Authentication:
- [ ] Login admin aman.
- [ ] Password hashing dan kebijakan password.
- [ ] Opsi MFA.

Authorization:
- [ ] Permission matrix admin.
- [ ] Penerapan least privilege.
- [ ] Persetujuan aksi kritikal.

Accounting:
- [ ] Audit log aktivitas admin.
- [ ] Pencatatan aktor, aksi, target, waktu, IP, user agent.
- [ ] Pencarian/filter log.
- [ ] Ekspor log untuk audit internal.
