from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from digital_signature.auth_router import get_current_user
from backend.app.api.v1.schemas.claim_schema import ReviewClaimRequest
from backend.app.domains.claim.entity import ClaimEntity, ClaimStatus
from backend.app.domains.claim.service import ClaimService
from backend.app.domains.user.entity import Role, UserEntity
from backend.app.infrastructure.config.settings import settings
from backend.app.infrastructure.repositories.claim_repository import ClaimRepository
from database.session import get_db

router = APIRouter()

def save_claim_proof_image(upload_file: UploadFile) -> str:
	storage_dir = Path(settings.CLAIM_UPLOAD_DIR)
	storage_dir.mkdir(parents=True, exist_ok=True)
	extension = Path(upload_file.filename or "proof").suffix or ".jpg"
	file_name = f"{uuid4().hex}{extension}"
	file_path = storage_dir / file_name
	content = upload_file.file.read()
	file_path.write_bytes(content)
	return f"/storage/claims/{file_name}"


# Updated helper to accept the authenticating user's ID
def build_claim(proof_text: str, proof_image: str, item_id: int, claimer_id: int) -> ClaimEntity:
	return ClaimEntity(
		id=None,
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


@router.post("/claims/")
async def create_claim(
	proof_text: str = Form(...),
	item_id: int = Form(...),
	proof_image: UploadFile = File(...),
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	repo = ClaimRepository(db)
	service = ClaimService(repo)

	try:
		# Pass current_user.id directly so they can't impersonate someone else
		image_path = save_claim_proof_image(proof_image)
		claim = await service.submit_claim(build_claim(proof_text, image_path, item_id, current_user.id))
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
# --- CHANGED: Added current_user dependency with Admin check ---
async def review_claim(
	claim_id: int,
	payload: ReviewClaimRequest,
	db: AsyncSession = Depends(get_db),
	current_user: UserEntity = Depends(get_current_user)
):
	# Role validation: block users who are not Admin
	if current_user.role != Role.ADMIN:
		raise HTTPException(status_code=403, detail="Hanya admin yang dapat mereview claim")

	repo = ClaimRepository(db)
	service = ClaimService(repo)

	try:
		reviewed_claim = await service.review_claim(
			claim_id=claim_id,
			new_status=payload.status,
			reviewer_id=current_user.id, # Securely inject admin ID from JWT
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))

	if not reviewed_claim:
		raise HTTPException(status_code=404, detail="Claim tidak ditemukan")

	return {"status": "success", "data": reviewed_claim}
