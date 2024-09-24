import sqlalchemy.exc

from ..db import Session
from ..models import TgBotUser

from sqlalchemy import select, Sequence

__all__ = ["get_users", "get_user", "add_user"]


def get_user(**find_by) -> TgBotUser | None:
    with Session() as session:
        return session.scalars(select(TgBotUser).filter_by(**find_by)).first()


def get_users(**find_by) -> Sequence[TgBotUser]:
    with Session() as session:
        return session.scalars(select(TgBotUser).filter_by(**find_by)).all()


def add_user(user: TgBotUser) -> bool:
    with Session() as session:
        session.add(user)
        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            raise

    return True
