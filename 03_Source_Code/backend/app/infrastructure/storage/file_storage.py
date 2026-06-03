from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from botocore.config import Config
from PIL import Image, UnidentifiedImageError

from backend.app.infrastructure.config.settings import settings

try:
	import pillow_heif

	pillow_heif.register_heif_opener()
except Exception:
	pass


def _build_s3_client():
	import boto3

	addressing_style = "path" if settings.S3_FORCE_PATH_STYLE else "virtual"
	return boto3.client(
		"s3",
		region_name=settings.S3_REGION,
		endpoint_url=settings.S3_ENDPOINT_URL,
		aws_access_key_id=settings.S3_ACCESS_KEY_ID,
		aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
		config=Config(s3={"addressing_style": addressing_style}),
	)


def _build_file_name(upload_file: UploadFile, default_extension: str) -> str:
	extension = Path(upload_file.filename or "file").suffix or default_extension
	return f"{uuid4().hex}{extension}"


def _is_webp_convertible(upload_file: UploadFile) -> bool:
	content_type = (upload_file.content_type or "").lower()
	extension = Path(upload_file.filename or "").suffix.lower()
	return content_type.startswith("image/") or extension in {
		".jpg",
		".jpeg",
		".png",
		".webp",
		".gif",
		".bmp",
		".tif",
		".tiff",
		".heic",
		".heif",
		".avif",
	}


def _convert_image_to_webp_bytes(upload_file: UploadFile) -> bytes:
	try:
		upload_file.file.seek(0)
		with Image.open(upload_file.file) as image:
			image = image.convert("RGBA") if image.mode in {"P", "LA"} else image.convert("RGB")
			buffer = BytesIO()
			image.save(buffer, format="WEBP", quality=85, method=6)
			return buffer.getvalue()
	except UnidentifiedImageError as exc:
		raise HTTPException(status_code=400, detail="File gambar tidak valid atau formatnya tidak didukung") from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail="Gagal mengonversi gambar ke WebP") from exc


def _save_locally(upload_file: UploadFile, storage_dir: Path, file_name: str, subdir: str) -> str:
	storage_dir.mkdir(parents=True, exist_ok=True)
	if _is_webp_convertible(upload_file):
		(storage_dir / file_name).write_bytes(_convert_image_to_webp_bytes(upload_file))
	else:
		upload_file.file.seek(0)
		(storage_dir / file_name).write_bytes(upload_file.file.read())
	return f"/storage/{subdir}/{file_name}"


def _save_to_s3(upload_file: UploadFile, object_key: str) -> str:
	if not settings.S3_BUCKET_NAME:
		raise HTTPException(status_code=500, detail="S3_BUCKET_NAME belum diset")

	client = _build_s3_client()
	is_convertible = _is_webp_convertible(upload_file)
	body = BytesIO(_convert_image_to_webp_bytes(upload_file)) if is_convertible else upload_file.file
	if not is_convertible:
		upload_file.file.seek(0)
	client.upload_fileobj(
		body,
		settings.S3_BUCKET_NAME,
		object_key,
		ExtraArgs={
			"ContentType": "image/webp" if is_convertible else (upload_file.content_type or "application/octet-stream"),
		},
	)
	return _build_public_url(object_key)


def _extract_s3_object_key(stored_path: str) -> str:
	if stored_path.startswith("http://") or stored_path.startswith("https://"):
		parsed = urlparse(stored_path)
		path = parsed.path.lstrip("/")
		if settings.S3_BUCKET_NAME and path.startswith(f"{settings.S3_BUCKET_NAME}/"):
			return path[len(settings.S3_BUCKET_NAME) + 1 :]
		return path

	return stored_path.lstrip("/")


def get_storage_reference(stored_path: str | None) -> str | None:
	if not stored_path:
		return None

	if stored_path.startswith("http://") or stored_path.startswith("https://"):
		return _extract_s3_object_key(stored_path)

	return stored_path


def get_accessible_file_url(stored_path: str | None) -> str | None:
	if not stored_path:
		return None

	if settings.STORAGE_PROVIDER.lower() != "s3":
		return stored_path

	if stored_path.startswith("/storage/") or stored_path.startswith("storage/"):
		return stored_path

	if not settings.S3_BUCKET_NAME:
		return stored_path

	object_key = _extract_s3_object_key(stored_path)
	client = _build_s3_client()
	try:
		return client.generate_presigned_url(
			"get_object",
			Params={"Bucket": settings.S3_BUCKET_NAME, "Key": object_key},
			ExpiresIn=60 * 60,
		)
	except Exception:
		return stored_path


def _build_public_url(object_key: str) -> str:
	if settings.S3_PUBLIC_URL:
		return f"{settings.S3_PUBLIC_URL.rstrip('/')}/{object_key}"

	if not settings.S3_ENDPOINT_URL or not settings.S3_BUCKET_NAME:
		raise HTTPException(status_code=500, detail="S3_ENDPOINT_URL atau S3_BUCKET_NAME belum diset")

	endpoint = urlparse(settings.S3_ENDPOINT_URL)
	if not endpoint.scheme or not endpoint.netloc:
		raise HTTPException(status_code=500, detail="S3_ENDPOINT_URL tidak valid")

	if settings.S3_FORCE_PATH_STYLE:
		return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET_NAME}/{object_key}"

	return f"{endpoint.scheme}://{settings.S3_BUCKET_NAME}.{endpoint.netloc}/{object_key}"


def save_upload_file(upload_file: UploadFile, *, subdir: str, default_extension: str = ".bin") -> str:
	if upload_file is None:
		raise HTTPException(status_code=400, detail="File upload tidak ditemukan")

	file_name = _build_file_name(upload_file, default_extension)
	if _is_webp_convertible(upload_file):
		file_name = f"{Path(file_name).stem}.webp"
	object_key = f"{subdir}/{file_name}"

	if settings.STORAGE_PROVIDER.lower() == "s3":
		_save_to_s3(upload_file, object_key)
		return object_key

	storage_dir = Path("storage") / subdir
	return _save_locally(upload_file, storage_dir, file_name, subdir)