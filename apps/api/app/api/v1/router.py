from fastapi import APIRouter

from app.api.v1.endpoints import (
    account,
    admin,
    analytics,
    auth,
    calendar,
    class_groups,
    documents,
    health,
    imports,
    knowledge,
    personal_assets,
    questions,
    sharing,
    style_profile,
    tasks,
    teaching_reflections,
    teaching_units,
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
api_v1_router.include_router(questions.router)
api_v1_router.include_router(sharing.router)
api_v1_router.include_router(calendar.router)
api_v1_router.include_router(class_groups.router)
api_v1_router.include_router(teaching_units.router)
api_v1_router.include_router(teaching_reflections.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(analytics.router)
