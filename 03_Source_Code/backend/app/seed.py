# ai generated heheh :p
import asyncio
from datetime import datetime, timezone
from backend.app.domains.item.entity import ItemStatus, ReportType
from backend.app.domains.user.entity import Role
from database.models.claim_model import ClaimModel
from database.models.item_model import ItemModel
from database.models.user_model import UserModel
from database.session import AsyncSessionLocal, Base, engine
from digital_signature.utils import get_password_hash

async def seed_data():
    async with engine.begin() as conn:
        print("[DB] Reset database schema...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("[SEED] Memulai seeding data...")

            user1 = UserModel(
                email="luqman@apps.ipb.ac.id",
                full_name="Luqman",
                is_active=True,
                password_hash=get_password_hash("luqman123"),
                role=Role.CIVITAS,
            )
            user2 = UserModel(
                email="naufal@apps.ipb.ac.id",
                full_name="Naufal",
                is_active=True,
                password_hash=get_password_hash("naufal123"),
                role=Role.CIVITAS,
            )
            user3 = UserModel(
                email="syafiq@apps.ipb.ac.id",
                full_name="Syafiq",
                is_active=True,
                password_hash=get_password_hash("syafiq123"),
                role=Role.ADMIN,
            )
            session.add_all([user1, user2, user3])

            await session.flush()

            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)

            item1 = ItemModel(
                title="Kunci Motor Honda",
                description="Gantungan kunci IPB warna merah, ilang deket GWW.",
                location="Parkiran GWW",
                image="/images/items/kunci-motor-honda.jpg",
                report_type=ReportType.LOST,
                status=ItemStatus.LOST,
                reporter_id=user1.id,
                created_at=now_naive,
            )

            item2 = ItemModel(
                title="Tumbler Tuku",
                description="Warna hitam polos, 500ml. Ketemu di meja perpus LSI.",
                location="Perpustakaan LSI",
                image="/images/items/tumbler-tuku.jpg",
                report_type=ReportType.FOUND,
                status=ItemStatus.FOUND,
                reporter_id=user2.id,
                created_at=now_naive,
            )

            session.add_all([item1, item2])

        print("[SUCCESS] Seeding selesai! Database sudah di-reset dan diisi ulang dari nol.")

if __name__ == "__main__":
    try:
        asyncio.run(seed_data())
    except Exception as e:
        print(f"[ERROR] Waduh gagal seed, Dul! Error: {e}")
