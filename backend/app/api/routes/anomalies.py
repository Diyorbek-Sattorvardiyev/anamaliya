from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.core.security import get_current_user_email
from app.db.session import get_db
from app.schemas.anomaly import AnomalyRead
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["anomalies"])


@router.get("/anomalies", response_model=list[AnomalyRead])
@limiter.limit("60/minute")
def list_anomalies(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_user_email),
):
    return AnalyticsService(db).anomalies(limit=limit)
