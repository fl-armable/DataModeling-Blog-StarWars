from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Date, Time, DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from eralchemy2 import render_er
from sqlalchemy.exc import SQLAlchemyError


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
#    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#    username: Mapped[str] = mapped_column(
#        String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    member_since: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
#            "firstname": self.firstname,
#            "lastname": self.lastname,
            "email": self.email,
#            "username": self.username,
            "member_since": self.member_since.isoformat()
        }

    @staticmethod
    def add_user(data: dict):
        try:
            new_user = User(
#                firstname=data["firstname"],
#                lastname=data["lastname"],
                email=data["email"],
#                username=data["username"],
                password=data["password"],
                member_since=data["member_since"]
            )
            db.session.add(new_user)
            db.session.commit()
            return True, new_user.serialize()
        except (KeyError, SQLAlchemyError)as e:
            db.session.rollback()
            return False, {"error": str(e)}
        
    @staticmethod
    def get_users():
        try:
            users = db.session.query(User).all()
            return [user.serialize() for user in users]
        except SQLAlchemyError:
            db.session.rollback()
            return []

    @staticmethod
    def delete_user(id: int):
        try:
            user = db.session.get(User, id)
            if user is None:
                return False
            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False


class Favorites(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), nullable=False)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('item.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_id": self.item_id,
        }
    
    @staticmethod
    def add_favorites(user_id: int, item_id: int):
        try:
            # Contar cuántos favoritos tiene este usuario
            count = db.session.query(Favorites).filter_by(user_id=user_id).count()
            if count >= 5:
                return False, None
            # Verificar si ya existe este favorito para evitar duplicados
            exists = db.session.query(Favorites).filter_by(user_id=user_id, item_id=item_id).first()
            if exists:
                return False, None
            favorite = Favorites(
                user_id=user_id,
                item_id=item_id
            )
            db.session.add(favorite)
            db.session.commit()
            return True, favorite.serialize()
        except SQLAlchemyError:
            db.session.rollback()
            return False, None
            
    @staticmethod
    def get_favorites(user_id: int):
        try:
            favorites = db.session.query(Favorites).filter_by(user_id=user_id).all()
            return [fav.serialize() for fav in favorites]
        except SQLAlchemyError:
            db.session.rollback()
            return []

    @staticmethod
    def delete_favorites(item_id: int):
        try:
            favorite = db.session.get(Favorites, item_id)
            if favorite is None:
                return False
            db.session.delete(favorite)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

# type_item define el tipo de elemento, que puede ser "People" o "Planets"
class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_item: Mapped[str] = mapped_column(String(50), nullable=False)
    prop_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    uid: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[int] = mapped_column("version", Integer, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "type_item": self.type_item,
            "prop_id": self.prop_id,
            "description": self.description,
            "uid": self.uid,
            "version": self.version
        }
    
    @staticmethod
    def add_item(data: dict):
        try:
            item = Item(
                type_item=data["type_item"],
                prop_id=data["prop_id"],
                description=data["description"],
                uid=data["uid"],
                version=data["version"]
            )
            db.session.add(item)
            db.session.commit()
            return True, item.serialize()
        except (KeyError, SQLAlchemyError)as e:
            db.session.rollback()
            return False, {"error": str(e)}
        
    @staticmethod
    def get_item(type_item, uid):
        try:
            item = db.session.query(Item).filter_by(type_item=type_item, uid=uid).first()
            if item:
                return True, item.serialize()
            else:
                return False, None
        except SQLAlchemyError:
            db.session.rollback()
            return False, None

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
    
    @staticmethod
    def add_propertie(data: dict):
        try:
            propertie = Properties(
                propertie_id=data["propertie_id"],
                created=data["created"],
                edited=data["edited"],
                propertie_1=data["propertie_1"],
                propertie_2=data["propertie_2"],
                propertie_3=data["propertie_3"],
                propertie_4=data["propertie_4"],
                propertie_5=data["propertie_5"],
                propertie_6=data["propertie_6"],
                propertie_7=data["propertie_7"],
                propertie_8=data["propertie_8"],
                propertie_9=data["propertie_9"],
                url=data["url"]
            )
            db.session.add(propertie)
            db.session.commit()
            return True, propertie.serialize()
        except (KeyError, SQLAlchemyError):
            db.session.rollback()
            return False, None

    @staticmethod
    def get_propertie(propertie_id: str):
        try:
            propertie = db.session.query(Properties).filter_by(propertie_id=propertie_id).first()
            if propertie:
                return True, propertie.serialize()
            else:
                return False, None
        except SQLAlchemyError:
            db.session.rollback()
            return False, None

try:
    render_er(Base, 'diagram.png')
    print("✅ Diagrama generado correctamente como diagram.png")
except Exception as e:
    print("❌ Error generando el diagrama:", e)
