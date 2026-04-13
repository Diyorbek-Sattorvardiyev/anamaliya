from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def login(self, email: str, password: str) -> str:
        normalized_email = email.strip().lower()
        user = self.users.get_by_email(normalized_email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Email yoki parol noto'g'ri")
        return create_access_token(subject=user.email)

    def register(self, full_name: str, email: str, password: str) -> str:
        normalized_email = email.strip().lower()
        existing_user = self.users.get_by_email(normalized_email)
        if existing_user:
            raise ValueError("Bu email bilan foydalanuvchi allaqachon mavjud")

        user = self.users.create(
            email=normalized_email,
            full_name=full_name.strip(),
            hashed_password=get_password_hash(password),
        )
        return create_access_token(subject=user.email)
