from pydantic import BaseModel, Field


class TrainModelRequest(BaseModel):
    samples: int = Field(default=5000, ge=1000, le=50000)
    epochs: int = Field(default=20, ge=5, le=200)


class TrainModelResponse(BaseModel):
    message: str
    artifacts: list[str]
