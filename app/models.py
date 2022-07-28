import uuid

import bcrypt
from gino import Gino
from sqlalchemy import func
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

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "token": self.token,
            "pwd_need_to_del": self.password
        }


class Advertisement(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer,
                         db.ForeignKey('users.id', ondelete='cascade'),
                         nullable=False)
