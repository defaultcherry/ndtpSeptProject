from sqlalchemy import select

from . import Session, TgBotUser


def add_owner(user_id: int) -> bool:
    with Session() as session:
        user = session.scalars(select(TgBotUser).filter_by(telegram_id=user_id)).first()
        if user is None:
            session.add(TgBotUser(telegram_id=user_id, is_owner=True))
        else:
            user.is_owner = True
        session.commit()
    return True
