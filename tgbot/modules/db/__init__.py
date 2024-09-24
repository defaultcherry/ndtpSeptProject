from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declared_attr
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("sqlite:///storage/tgbot.db", echo=True)
Session = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"


from modules.models import *

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

from .get_owner import get_owner
from .add_owner import add_owner
from .users import *
