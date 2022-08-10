
import bcrypt
from gino import Gino
from sqlalchemy import func, and_, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(UUID, server_default=text("gen_random_uuid()"))
    advertisements = relationship('Advertisement')

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    @classmethod
    async def get_id(cls, token: str):
        user_id = await cls.select('id').where(
            cls.token == token
        ).gino.scalar()
        return user_id

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "token": str(self.token)
        }


class Advertisement(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('users.id', ondelete='cascade'),
                         nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "owner_id": self.owner_id
        }

    @classmethod
    async def is_owner(cls, user_id: int, adv_id: int):
        advertisement = await Advertisement.query.where(
            and_(
                Advertisement.id == adv_id,
                Advertisement.is_active == True
            )
        ).gino.first()
        if advertisement is None:
            return None
        elif advertisement.owner_id != user_id:
            return False
        return advertisement
