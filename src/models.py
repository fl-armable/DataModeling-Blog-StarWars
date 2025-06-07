from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Date, Time, DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from eralchemy2 import render_er
from enum import Enum as PyEnum  # <-- Importa Enum de Python
from sqlalchemy import Enum as SQLEnum  # <-- Importa Enum de SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    member_since: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "username": self.username,
            "member_since": self.member_since.isoformat()
        }


class Favorites(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), nullable=False)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('item.id'), nullable=False)
    favorites_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_id": self.item_id,
            "favorites_count": self.favorites_count
        }


class ItemTypeEnum(PyEnum):  # <-- Usa el Enum de Python
    PEOPLE = "People"
    PLANETS = "Planets"


# type_item define el tipo de elemento, que puede ser "People" o "Planets"
class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_item: Mapped[ItemTypeEnum] = mapped_column(
        SQLEnum(ItemTypeEnum), nullable=False)  # <-- Usa el Enum de SQLAlchemy
    prop_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    uid: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    version: Mapped[int] = mapped_column(
        "version", Integer, nullable=False)  # __v

    def serialize(self):
        return {
            "id": self.id,
            "type_item": self.type_item.value,
            "prop_id": self.prop_id,
            "description": self.description,
            "uid": self.uid,
            "version": self.version
        }

# Properties almacena las propiedades de cada elemento, independientemente de su tipo.
class Properties(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    propertie_id: Mapped[str] = mapped_column(
        String(50), ForeignKey('item.prop_id'), unique=True, nullable=False)
    created: Mapped[str] = mapped_column(String(50), nullable=False)
    edited: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_1: Mapped[str] = mapped_column(String(100), nullable=False)
    propertie_2: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_3: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_4: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_5: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_6: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_7: Mapped[str] = mapped_column(String(50), nullable=False)
    propertie_8: Mapped[str] = mapped_column(String(255), nullable=False)
    propertie_9: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "propertie_id": self.propertie_id,
            "created": self.created,
            "edited": self.edited,
            "propertie_1": self.propertie_1,
            "propertie_2": self.propertie_2,
            "propertie_3": self.propertie_3,
            "propertie_4": self.propertie_4,
            "propertie_5": self.propertie_5,
            "propertie_6": self.propertie_6,
            "propertie_7": self.propertie_7,
            "propertie_8": self.propertie_8,
            "propertie_9": self.propertie_9,
            "url": self.url
        }


try:
    render_er(Base, 'diagram.png')
    print("✅ Diagrama generado correctamente como diagram.png")
except Exception as e:
    print("❌ Error generando el diagrama:", e)
