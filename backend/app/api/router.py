from fastapi import APIRouter

from app.api.routes import auth, meta, photos, places, visits

api_router = APIRouter(prefix="/api")
api_router.include_router(meta.router)
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(places.router)
api_router.include_router(visits.router)
api_router.include_router(photos.router)
