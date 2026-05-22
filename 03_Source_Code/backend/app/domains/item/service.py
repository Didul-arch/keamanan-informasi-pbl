from backend.app.domains.item.entity import ItemEntity, ItemStatus, ReportType
from backend.app.infrastructure.repositories.item_repository import ItemRepository
from datetime import date

class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    async def report_lost_item(self, item: ItemEntity) -> ItemEntity:
        if len(item.title) < 5:
            raise ValueError("Judul laporan minimal 5 karakter.")

        item.status = ItemStatus.LOST
        return await self.item_repo.save(item)

    async def report_found_item(self, item: ItemEntity) -> ItemEntity:
        if len(item.title) < 5:
            raise ValueError("Judul laporan minimal 5 karakter.")

        item.status = ItemStatus.FOUND
        return await self.item_repo.save(item)

    async def get_all_items(self):
        return await self.item_repo.get_all()

    async def get_filtered_items(
        self,
        report_type: ReportType | None = None,
        location: str | None = None,
        report_date: date | None = None,
    ):
        return await self.item_repo.get_filtered_items(
            report_type=report_type,
            location=location,
            report_date=report_date,
        )