from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _format_validation_error(exc: ValidationError) -> str:
    messages = []
    for error in exc.errors():
        field = ".".join(str(part) for part in error.get("loc", []) if part != "body")
        text = error.get("msg", "Noto'g'ri qiymat")
        if field:
            messages.append(f"{field}: {text}")
        else:
            messages.append(text)
    return "; ".join(messages) or "Kiritilgan ma'lumot noto'g'ri"


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            raw_payload = await request.json()
        else:
            form = await request.form()
            raw_payload = {
                "email": form.get("email") or form.get("username"),
                "password": form.get("password"),
            }

        payload = LoginRequest.model_validate(raw_payload)
        token = AuthService(db).login(payload.email, payload.password)
        return TokenResponse(access_token=token)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_format_validation_error(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/register", response_model=TokenResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    try:
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            raw_payload = await request.json()
        else:
            form = await request.form()
            raw_payload = {
                "full_name": form.get("full_name") or form.get("fullname") or form.get("name"),
                "email": form.get("email"),
                "password": form.get("password"),
            }

        payload = RegisterRequest.model_validate(raw_payload)
        token = AuthService(db).register(payload.full_name, payload.email, payload.password)
        return TokenResponse(access_token=token)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_format_validation_error(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
