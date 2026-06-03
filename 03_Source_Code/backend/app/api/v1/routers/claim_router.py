from datetime import date, datetime

from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.schemas.claim_schema import ReviewClaimRequest
from backend.app.domains.claim.entity import ClaimEntity, ClaimStatus, RequestType
from backend.app.domains.item.entity import ItemStatus
from backend.app.domains.item.service import ItemService
from backend.app.domains.claim.service import ClaimService
from database.session import get_db
from backend.app.infrastructure.repositories.activity_history_repository import ActivityHistoryRepository
from backend.app.infrastructure.repositories.claim_repository import ClaimRepository
from backend.app.infrastructure.repositories.item_repository import ItemRepository
from database.models.claim_model import ClaimModel
from database.models.item_model import ItemModel
from backend.app.infrastructure.storage.file_storage import save_upload_file
from backend.app.infrastructure.storage.file_storage import get_accessible_file_url

from digital_signature.auth_router import get_current_user
from backend.app.domains.user.entity import UserEntity, Role
from backend.app.domains.notification.service import NotificationService
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository

router = APIRouter()

def save_claim_proof_image(upload_file: UploadFile) -> str:
	return save_upload_file(upload_file, subdir="claims", default_extension=".jpg")


# Updated helper to accept the authenticating user's ID
def build_claim(
    request_type: RequestType,
    proof_text: str,
    proof_image: str,
    item_id: int,
    claimer_id: int,
) -> ClaimEntity:
	return ClaimEntity(
		id=None,
		request_type=request_type,
		proof_text=proof_text,
		proof_image=proof_image,
		status=ClaimStatus.PENDING,
		claimer_id=claimer_id,        
		item_id=item_id,
		reviewer_id=None,
		reviewed_at=None,
		created_at=datetime.now(),
		updated_at=None,
	)


def build_history_item_entry(item: ItemModel) -> dict:
	return {
		"id": item.id,
		"kind": "report",
		"request_type": None,
		"request_status": None,
		"item_id": item.id,
		"title": item.title,
		"description": item.description,
		"location": item.location,
		"category": item.category,
		"image": get_accessible_file_url(item.image),
		"created_at": item.created_at.isoformat() if item.created_at else None,
		"item_status": item.status.value if hasattr(item.status, "value") else str(item.status),
		"request_status": None,
		"can_mark_returned": False,
	}


def build_history_request_entry(claim: ClaimModel, item: ItemModel) -> dict:
	request_status = claim.status.value if hasattr(claim.status, "value") else str(claim.status)
	item_status = item.status.value if hasattr(item.status, "value") else str(item.status)
	return {
		"id": claim.id,
		"kind": "request",
		"request_type": claim.request_type.value if hasattr(claim.request_type, "value") else str(claim.request_type),
		"request_status": request_status,
		"item_id": item.id,
		"title": item.title,
		"description": item.description,
		"location": item.location,
		"category": item.category,
		"image": get_accessible_file_url(item.image),
		"created_at": claim.created_at.isoformat() if claim.created_at else None,
		"item_status": item_status,
		"request_status": request_status,
		"can_mark_returned": request_status == ClaimStatus.APPROVED.value and item_status == ItemStatus.NOT_RETURNED.value,
	}


@router.post("/claims/")
async def create_claim(
	request_type: RequestType = Form(RequestType.CLAIM),
	proof_text: str = Form(...),
	item_id: int = Form(...),
	proof_image: UploadFile = File(...),
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	item_repo = ItemRepository(db)
	item = await item_repo.get_by_id(item_id)
	if not item:
		raise HTTPException(status_code=404, detail="Item tidak ditemukan")

	repo = ClaimRepository(db)
	service = ClaimService(repo)

	try:
		# Pass current_user.id directly so they can't impersonate someone else
		image_path = save_claim_proof_image(proof_image)
		claim = await service.submit_claim(build_claim(request_type, proof_text, image_path, item_id, current_user.id))
		history_repo = ActivityHistoryRepository(db)
		await history_repo.create_request_entry(current_user.id, claim, item)
		notification_service = NotificationService(NotificationRepository(db))
		await notification_service.create_for_claim_submission(claim, item.reporter_id, item.title)
		return {"status": "success", "data": claim}
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/claims/")
async def list_claims(
	claim_date: date | None = None,
	reviewer_id: int | None = None,
	claimer_id: int | None = None,
	status: ClaimStatus | None = None,
	limit: int = 20,
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	repo = ClaimRepository(db)
	service = ClaimService(repo)

	# regular users can only see their own claims:
	if current_user.role != Role.ADMIN:
		claimer_id = current_user.id

	claims = await service.get_all(
		claim_date=claim_date,
		reviewer_id=reviewer_id,
		claimer_id=claimer_id,
		status=status,
		limit=limit,
	)
	return {"data": claims}


@router.get("/claims/{claim_id}")
# --- CHANGED: Added current_user dependency ---
async def get_claim_detail(
	claim_id: int, 
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	repo = ClaimRepository(db)
	service = ClaimService(repo)
	claim = await service.get_by_id(claim_id)

	if not claim:
		raise HTTPException(status_code=404, detail="Claim tidak ditemukan")

	return {"data": claim}


@router.patch("/claims/{claim_id}/review")
async def review_claim(
	claim_id: int,
	payload: ReviewClaimRequest,
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	if current_user.role != Role.ADMIN:
		raise HTTPException(status_code=403, detail="Hanya admin yang dapat mereview claim")

	repo = ClaimRepository(db)
	service = ClaimService(repo)

	try:
		reviewed_claim = await service.review_claim(
			claim_id=claim_id,
			new_status=payload.status,
			reviewer_id=current_user.id, 
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))

	if not reviewed_claim:
		raise HTTPException(status_code=404, detail="Claim tidak ditemukan")

	history_repo = ActivityHistoryRepository(db)
	await history_repo.update_request_status_by_claim_id(claim_id, reviewed_claim.status.value)

	notification_service = NotificationService(NotificationRepository(db))
	await notification_service.create_for_claim_review(reviewed_claim)

	return {"status": "success", "data": reviewed_claim}


@router.get("/history/me")
async def get_my_history(
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user),
):
	if current_user.id is None:
		raise HTTPException(status_code=500, detail="User id missing")

	history_repo = ActivityHistoryRepository(db)
	history = await history_repo.get_for_user(current_user.id)

	return {"data": history}


@router.patch("/history/items/{item_id}/returned")
async def mark_item_returned_from_history(
	item_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user),
):
	if current_user.id is None:
		raise HTTPException(status_code=500, detail="User id missing")

	approved_claim_result = await db.execute(
		select(ClaimModel)
		.where(ClaimModel.item_id == item_id)
		.where(ClaimModel.claimer_id == current_user.id)
		.where(ClaimModel.status == ClaimStatus.APPROVED)
	)
	approved_claim = approved_claim_result.scalars().first()
	if not approved_claim:
		raise HTTPException(status_code=403, detail="Tidak ada request approved untuk item ini")

	item_result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
	item = item_result.scalars().first()
	if not item:
		raise HTTPException(status_code=404, detail="Item tidak ditemukan")

	if item.status != ItemStatus.RETURNED:
		item.status = ItemStatus.RETURNED
		await db.commit()
		await db.refresh(item)

	history_repo = ActivityHistoryRepository(db)
	updated_history = await history_repo.mark_user_item_returned(current_user.id, item_id)

	return {"status": "success", "data": updated_history}


@router.patch("/claims/{claim_id}/mark-collected")
async def mark_claim_collected(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    # Verify claim exists
    claim_service = ClaimService(ClaimRepository(db))
    claim = await claim_service.get_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim tidak ditemukan")

    # Only the claimer can mark collected
    if current_user.id != claim.claimer_id:
        raise HTTPException(status_code=403, detail="Hanya claimer yang dapat menandai item sebagai dikumpulkan")

    # Claim must be approved
    if claim.status != ClaimStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Claim belum disetujui")

    # Update item status lewat service — tidak langsung ke DB
    item_service = ItemService(ItemRepository(db))
    try:
        await item_service.update_status(claim.item_id, ItemStatus.RETURNED)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    # Update activity history
    history_repo = ActivityHistoryRepository(db)
    updated_history = await history_repo.mark_user_item_returned(current_user.id, claim.item_id)

    # Notify — tidak block kalau gagal
    try:
        notification_service = NotificationService(NotificationRepository(db))
        await notification_service.create_for_claim_review(claim)
    except Exception:
        pass

    return {"status": "success", "data": updated_history}