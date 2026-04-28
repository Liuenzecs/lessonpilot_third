from fastapi import APIRouter

from app.api.v1.endpoints import (
    account,
    auth,
    documents,
    health,
    imports,
    knowledge,
    personal_assets,
    style_profile,
    tasks,
    templates,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(tasks.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(account.router)
api_v1_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_v1_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_v1_router.include_router(imports.router)
api_v1_router.include_router(personal_assets.router)
api_v1_router.include_router(style_profile.router)
