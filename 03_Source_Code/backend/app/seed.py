import asyncio
from datetime import datetime, timezone

from database.session import AsyncSessionLocal, engine, Base
from database.models.user_model import UserModel
from database.models.item_model import ItemModel
from database.models.claim_model import ClaimModel

from database.models.activity_history_model import ActivityHistoryModel
from database.models.activity_history_model import ActivityHistoryKind
from backend.app.domains.item.entity import ItemStatus, ReportType
from backend.app.domains.user.entity import Role
from backend.app.domains.claim.entity import RequestType, ClaimStatus

from digital_signature.utils import get_password_hash

async def seed_data():
    async with engine.begin() as conn:
        print("[DB] Reset database schema...")
        # WARNING: Ini akan mereset semua tabel termasuk tabel alembic_version
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("[SEED] Memulai seeding data...")
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

            # ==========================================
            # 1. SEED USERS
            # ==========================================
            user1 = UserModel(
                email="syafiq@apps.ipb.ac.id",
                full_name="Syafiq Syadidul Azmi",
                phone_number="081234567890",
                identity_number=None,
                identity_document=None,
                is_active=True,
                password_hash=get_password_hash("syafiq123"),
                role=Role.ADMIN,
            )
            user2 = UserModel(
                email="naufal@apps.ipb.ac.id",
                full_name="Naufal Raya Pragata",
                phone_number="081234567891",
                identity_number=None,
                identity_document=None,
                is_active=True,
                password_hash=get_password_hash("naufal123"),
                role=Role.ADMIN,
            )
            user3 = UserModel(
                email="budi@apps.ipb.ac.id",
                full_name="Budi Santoso",
                phone_number="081234567892",
                identity_number="B2023001",
                identity_document="budi-ktm.jpg",
                is_active=True,
                password_hash=get_password_hash("budi123"),
                role=Role.CIVITAS,
            )
            session.add_all([user1, user2, user3])
            await session.flush() # Flush agar id user ter-generate

            # ==========================================
            # 2. SEED ITEMS
            # ==========================================
            item1 = ItemModel(
                title="Kunci Motor Honda",
                description="Gantungan kunci IPB warna merah, ilang deket GWW.",
                location="Parkiran GWW",
                image="/images/items/kunci-motor-honda.jpg",
                latitude=-6.5593,
                longitude=106.7262,
                report_type=ReportType.LOST,
                status=ItemStatus.NOT_RETURNED,
                reporter_id=user1.id,
                category="Accessories",
                created_at=now_naive,
            )

            item2 = ItemModel(
                title="Tumbler Tuku",
                description="Warna hitam polos, 500ml. Ketemu di meja perpus LSI.",
                location="Perpustakaan LSI",
                image="/images/items/tumbler-tuku.jpg",
                latitude=-6.5580,
                longitude=106.7280,
                report_type=ReportType.FOUND,
                status=ItemStatus.NOT_RETURNED,
                reporter_id=user2.id,
                category="Tumbler",
                created_at=now_naive,
            )
            session.add_all([item1, item2])
            await session.flush() # Flush agar id item ter-generate

            # ==========================================
            # 3. SEED CLAIMS
            # ==========================================
            # Budi (user3) mencoba mengklaim Kunci Motor (item1) yang dilaporkan Syafiq
            claim1 = ClaimModel(
                proof_text="Ini kunci saya, saya lampirkan foto kunci cadangannya.",
                proof_image="/images/claims/proof-kunci.jpg",
                status=ClaimStatus.PENDING, # Misal enum PENDING
                claimer_id=user3.id,
                item_id=item1.id,
                reviewer_id=None,
                request_type=RequestType.CLAIM,
                created_at=now_naive,
                updated_at=now_naive,
            )
            session.add(claim1)
            await session.flush() # Flush agar id claim ter-generate

            # ==========================================
            # 4. SEED ACTIVITY HISTORY
            # ==========================================
            # History 1: Pencatatan awal saat item1 dilaporkan
            history1 = ActivityHistoryModel(
                user_id=item1.reporter_id,
                item_id=item1.id,
                claim_id=None,
                history_type=ActivityHistoryKind.REPORT,
                request_type=None,
                item_status=item1.status.value,
                request_status=None,
                report_type=item1.report_type.value,
                title=item1.title,
                description=item1.description,
                location=item1.location,
                category=item1.category,
                image=item1.image,
                created_at=item1.created_at,
            )

            # History 2: Pencatatan saat Budi (user3) mengajukan klaim atas item1
            history2 = ActivityHistoryModel(
                user_id=claim1.claimer_id,
                item_id=item1.id,
                claim_id=claim1.id,
                history_type=ActivityHistoryKind.REQUEST,
                request_type=claim1.request_type,
                item_status=item1.status.value,
                request_status=claim1.status.value,
                report_type=item1.report_type.value,
                title=item1.title,
                description=item1.description,
                location=item1.location,
                category=item1.category,
                image=item1.image,
                created_at=claim1.created_at,
            )
            
            session.add_all([history1, history2])
            
        print("[SUCCESS] Seeding selesai! Database sudah di-reset dan diisi ulang dari nol.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_data())
    except Exception as e:
        print(f"[ERROR] Waduh gagal seed, Dul! Error: {e}")