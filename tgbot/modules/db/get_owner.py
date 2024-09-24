from . import Session
from . import TgBotUser

from sqlalchemy import select


def get_owner() -> TgBotUser | None:
    with Session() as session:
        return session.scalars(select(TgBotUser).filter_by(is_owner=True)).first()
