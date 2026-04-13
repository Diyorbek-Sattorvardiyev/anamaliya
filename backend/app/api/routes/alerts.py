from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.core.security import get_current_user_email
from app.db.session import get_db
from app.schemas.alert import AlertRead
from app.services.alert_service import AlertService

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[AlertRead])
@limiter.limit("60/minute")
def list_alerts(
    request: Request,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_user_email),
):
    return AlertService(db).list_alerts(limit=limit)
