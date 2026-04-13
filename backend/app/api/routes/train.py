from fastapi import APIRouter, Depends, Request

from app.core.rate_limiter import limiter
from app.core.security import get_current_user_email
from app.schemas.train import TrainModelRequest, TrainModelResponse
from app.services.model_service import ModelService

router = APIRouter(tags=["models"])


@router.post("/train-model", response_model=TrainModelResponse)
@limiter.limit("5/minute")
def train_model(
    request: Request,
    payload: TrainModelRequest,
    _email: str = Depends(get_current_user_email),
):
    result = ModelService().train(samples=payload.samples, epochs=payload.epochs)
    return TrainModelResponse(message="Model training completed", artifacts=result["artifacts"])
