from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.rate_limiter import limiter
from app.core.security import get_current_user_email
from app.db.session import get_db
from app.schemas.traffic import IngestRequest, IngestResponse, TrafficLiveResponse
from app.services.analytics_service import AnalyticsService
from app.services.traffic_service import TrafficService
from app.workers.tasks import process_ingest_payload

router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.post("/ingest", response_model=IngestResponse)
@limiter.limit("30/minute")
def ingest_traffic(
    request: Request,
    payload: IngestRequest,
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_user_email),
):
    packets = [p.model_dump() for p in payload.packets]
    if payload.simulate_count:
        packets.extend(TrafficService.simulate_packets(payload.simulate_count))

    if not packets:
        raise HTTPException(status_code=400, detail="Provide packets or simulate_count")

    if payload.async_mode:
        task = process_ingest_payload.delay(packets)
        return IngestResponse(message="Ingestion task queued", processed=0, task_id=task.id)

    processed = TrafficService(db).process_packets(packets)
    return IngestResponse(message="Traffic processed", processed=processed)


@router.get("/live", response_model=TrafficLiveResponse)
@limiter.limit("60/minute")
def live_traffic(
    request: Request,
    db: Session = Depends(get_db),
    _email: str = Depends(get_current_user_email),
):
    return AnalyticsService(db).live_snapshot()
