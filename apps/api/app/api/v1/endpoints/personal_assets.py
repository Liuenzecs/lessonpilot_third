from __future__ import annotations

from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import get_current_user
from app.models import User
from app.schemas.personal_asset import PersonalAssetConfirmPayload, PersonalAssetPreview, PersonalAssetRead
from app.services import personal_asset_service

router = APIRouter(prefix="/personal-assets", tags=["personal-assets"])


@router.post("/preview", response_model=PersonalAssetPreview)
async def preview_personal_asset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> PersonalAssetPreview:
    _ = current_user
    return personal_asset_service.preview_personal_asset(await file.read(), file.filename or "asset.docx")


@router.post("/confirm", response_model=PersonalAssetRead, status_code=status.HTTP_201_CREATED)
def confirm_personal_asset(
    payload: PersonalAssetConfirmPayload,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PersonalAssetRead:
    return personal_asset_service.create_personal_asset(session, current_user.id, payload)


@router.get("/", response_model=list[PersonalAssetRead])
def read_personal_assets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[PersonalAssetRead]:
    return personal_asset_service.list_personal_assets(session, current_user.id)


@router.get("/{asset_id}", response_model=PersonalAssetRead)
def read_personal_asset(
    asset_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PersonalAssetRead:
    return personal_asset_service.get_personal_asset(session, asset_id, current_user.id)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_personal_asset(
    asset_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Response:
    personal_asset_service.delete_personal_asset(session, asset_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
