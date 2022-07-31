import uuid

import bcrypt
from gino import Gino
from sqlalchemy import func, and_
from sqlalchemy.orm import relationship

db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String, default=str(uuid.uuid4()), unique=True)
    advertisements = relationship('Advertisement')

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    @classmethod
    async def get_id(cls, token: str):
        return await cls.select('id').where(
            cls.token == token
        ).gino.scalar()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "token": self.token
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
