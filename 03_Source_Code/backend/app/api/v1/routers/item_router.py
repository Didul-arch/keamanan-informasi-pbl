from datetime import datetime
from datetime import date

from digital_signature.auth_router import get_current_user
from backend.app.domains.user.entity import UserEntity
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.schemas.item_schema import ItemResponse
from backend.app.domains.item.entity import ItemEntity, ItemStatus, ReportType
from backend.app.domains.item.service import ItemService
from database.session import get_db
from backend.app.infrastructure.repositories.activity_history_repository import ActivityHistoryRepository
from backend.app.infrastructure.repositories.item_repository import ItemRepository
from backend.app.infrastructure.storage.file_storage import save_upload_file

router = APIRouter()


def save_item_image(upload_file: UploadFile) -> str:
	return save_upload_file(upload_file, subdir="items", default_extension=".jpg")


def build_item(
	title: str,
	description: str,
	location: str,
	category: str | None,
	image: str,
	status: ItemStatus,
	report_type: ReportType,
	reporter_id: int,
) -> ItemEntity:
	return ItemEntity(
		id=None,
		title=title,
		description=description,
		location=location,
		category=category,
		image=image,
		latitude=None,
		longitude=None,
		report_type=report_type,
		status=status,
		reporter_id=reporter_id,
		created_at=datetime.now(),
	)


@router.post("/items/report-lost")
async def report_lost_item(
	title: str = Form(...),
	description: str = Form(...),
	location: str = Form(...),
	category: str | None = Form(None),
	image: UploadFile | None = File(None),
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	repo = ItemRepository(db)
	service = ItemService(repo)

	reporter_id = current_user.id

	try:
		image_path = save_item_image(image) if image else None
		result = await service.report_lost_item(
			build_item(title, description, location, category, image_path, ItemStatus.NOT_RETURNED, ReportType.LOST, reporter_id)
		)
		history_repo = ActivityHistoryRepository(db)
		await history_repo.create_report_entry(reporter_id, result)
		return {"status": "success", "data": result}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/items/report-found")
async def report_found_item(
	title: str = Form(...),
	description: str = Form(...),
	location: str = Form(...),
	category: str | None = Form(None),
	image: UploadFile | None = File(None),
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	repo = ItemRepository(db)
	service = ItemService(repo)

	reporter_id = current_user.id

	try:
		image_path = save_item_image(image) if image else None
		result = await service.report_found_item(
			build_item(title, description, location, category, image_path, ItemStatus.NOT_RETURNED, ReportType.FOUND, reporter_id)
		)
		history_repo = ActivityHistoryRepository(db)
		await history_repo.create_report_entry(reporter_id, result)
		return {"status": "success", "data": result}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/items/")
async def list_items(db: AsyncSession = Depends(get_db)):
	repo = ItemRepository(db)
	items = await repo.get_all()
	return {"data": items}


@router.get("/items/{item_id}")
async def get_item_detail(item_id: int, db: AsyncSession = Depends(get_db)):
	repo = ItemRepository(db)
	item = await repo.get_by_id(item_id)
	if not item:
		raise HTTPException(status_code=404, detail="Item tidak ditemukan")
	return {"data": item}


@router.get("/items/search")
async def search_item_by_title(
	report_type: ReportType | None = None,
	location: str | None = None,
	report_date: date | None = None,
	db: AsyncSession = Depends(get_db),
):
	repo = ItemRepository(db)
	service = ItemService(repo)
	items = await service.get_filtered_items(
		report_type=report_type,
		location=location,
		report_date=report_date,
	)
	return {"data": items}
