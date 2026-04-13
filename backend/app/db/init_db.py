from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models import User
from app.db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        admin = db.query(User).filter(User.email == "admin@netsentinel.local").first()
        if not admin:
            db.add(
                User(
                    email="admin@netsentinel.local",
                    full_name="System Admin",
                    hashed_password=get_password_hash("Admin12345"),
                    role="admin",
                )
            )
            db.commit()


if __name__ == "__main__":
    init_db()
