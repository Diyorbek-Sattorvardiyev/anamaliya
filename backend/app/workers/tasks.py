from app.db.session import SessionLocal
from app.services.traffic_service import TrafficService
from app.utils.notifications import send_email_alert
from app.workers.celery_app import celery_app


@celery_app.task(name="process_ingest_payload")
def process_ingest_payload(payload: list[dict]) -> dict:
    db = SessionLocal()
    try:
        service = TrafficService(db)
        processed = service.process_packets(payload)
        return {"processed": processed}
    finally:
        db.close()


@celery_app.task(name="send_email_notification")
def send_email_notification(to_email: str, subject: str, message: str) -> dict:
    send_email_alert(to_email=to_email, subject=subject, message=message)
    return {"sent": True, "to": to_email}
