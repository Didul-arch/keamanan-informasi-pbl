from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, datetime, time, timedelta
from backend.app.domains.item.entity import ItemEntity, ReportType
from database.models.item_model import ItemModel

class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_entity(self, item: ItemModel) -> ItemEntity:
        return ItemEntity(
            id=item.id,
            title=item.title,
            description=item.description,
            location=item.location,
            image=item.image,
            category=item.category,
            latitude=item.latitude,
            longitude=item.longitude,
            report_type=item.report_type,
            status=item.status,
            reporter_id=item.reporter_id,
            created_at=item.created_at,
        )

    # 1. Save new item
    async def save(self, item: ItemEntity) -> ItemEntity:
        db_item = ItemModel(
            title=item.title,
            description=item.description,
            location=item.location,
            category=item.category,
            image=item.image,
            latitude=item.latitude,
            longitude=item.longitude,
            report_type=item.report_type,
            status=item.status,
            reporter_id=item.reporter_id,
            created_at=item.created_at
        )
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        
        item.id = db_item.id
        return item

    # 2. Cari Semua Barang 
    async def get_all(self, limit: int = 20) -> list[ItemEntity]:
        query = select(ItemModel).order_by(ItemModel.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        db_items = result.scalars().all()
        
        # Balikin dalam bentuk list of Entities (Mapping massal)
        return [self._to_entity(item) for item in db_items]

    # 3. Cari Barang Berdasarkan ID 
    async def get_by_id(self, item_id: int) -> ItemEntity | None:
        result = await self.db.execute(select(ItemModel).where(ItemModel.id == item_id))
        item = result.scalars().first()
        
        if not item: return None
        
        return self._to_entity(item)

    # 4. Cari Barang dengan filter opsional
    async def get_filtered_items(
        self,
        report_type: ReportType | None = None,
        location: str | None = None,
        report_date: date | None = None,
    ) -> list[ItemEntity]:
        query = select(ItemModel)

        if report_type is not None:
            query = query.where(ItemModel.report_type == report_type)

        if location:
            query = query.where(ItemModel.location.ilike(f"%{location}%"))

        if report_date is not None:
            start_of_day = datetime.combine(report_date, time.min)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.where(
                (ItemModel.created_at >= start_of_day) & (ItemModel.created_at < end_of_day)
            )

        query = query.order_by(ItemModel.created_at.desc())
        result = await self.db.execute(query)
        db_items = result.scalars().all()
        return [self._to_entity(item) for item in db_items]