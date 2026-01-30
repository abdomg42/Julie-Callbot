from fastapi import APIRouter
from .interactions import router as interactions_router
from .views import router as views_router

api_router = APIRouter()
api_router.include_router(interactions_router)
api_router.include_router(views_router)
