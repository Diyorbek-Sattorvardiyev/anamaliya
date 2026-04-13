from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.anomalies import router as anomalies_router
from app.api.routes.auth import router as auth_router
from app.api.routes.train import router as train_router
from app.api.routes.traffic import router as traffic_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(traffic_router)
api_router.include_router(anomalies_router)
api_router.include_router(train_router)
api_router.include_router(alerts_router)
