from backend.app.domains.item.entity import ItemEntity, ItemStatus, ReportType
from backend.app.infrastructure.repositories.item_repository import ItemRepository
from datetime import date

class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self.item_repo = item_repo

    # createReport() di class diagram — dipecah dua biar lebih eksplisit
    async def report_lost_item(self, item: ItemEntity) -> ItemEntity:
        if len(item.title) < 5:
            raise ValueError("Judul laporan minimal 5 karakter.")
        item.status = ItemStatus.NOT_RETURNED
        item.report_type = ReportType.LOST
        return await self.item_repo.save(item)

    async def report_found_item(self, item: ItemEntity) -> ItemEntity:
        if len(item.title) < 2:
            raise ValueError("Judul laporan minimal 2 karakter.")
        item.status = ItemStatus.NOT_RETURNED
        item.report_type = ReportType.FOUND
        return await self.item_repo.save(item)

    # getDetails() di class diagram
    async def get_item_by_id(self, item_id: int) -> ItemEntity:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item tidak ditemukan.")
        return item

    # updateStatus() di class diagram
    async def update_status(self, item_id: int, new_status: ItemStatus) -> ItemEntity:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item tidak ditemukan.")
        item.update_status(new_status)
        return await self.item_repo.update(item)

    # searchAndFilter() di class diagram
    async def search_and_filter(
        self,
        report_type: ReportType | None = None,
        location: str | None = None,
        report_date: date | None = None,
    ) -> list[ItemEntity]:
        return await self.item_repo.get_filtered_items(
            report_type=report_type,
            location=location,
            report_date=report_date,
        )

    # get_all_items tetap ada — dipakai di router
    async def get_all_items(self) -> list[ItemEntity]:
        return await self.item_repo.get_all()

    # get_filtered_items tetap ada sebagai alias — supaya router tidak rusak
    async def get_filtered_items(
        self,
        report_type: ReportType | None = None,
        location: str | None = None,
        report_date: date | None = None,
    ) -> list[ItemEntity]:
        return await self.search_and_filter(
            report_type=report_type,
            location=location,
            report_date=report_date,
        )