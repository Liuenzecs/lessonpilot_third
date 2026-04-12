from fastapi import APIRouter

from app.api.v1.endpoints import account, admin, analytics, auth, billing, documents, health, tasks

api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(tasks.router)
api_v1_router.include_router(documents.router)
api_v1_router.include_router(account.router)
api_v1_router.include_router(billing.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(admin.router)
