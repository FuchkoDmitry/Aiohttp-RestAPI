from operator import or_, and_

import bcrypt
from aiohttp import web
from asyncpg.exceptions import UniqueViolationError

from app.error_handlers import BadRequest, Unauthorized
from app.models import User
from app.validators import validate, GetTokenValidate, CreateUserValidate


class UsersView(web.View):

    async def get(self):
        unvalidated_data = await self.request.json()
        validated_data = validate(unvalidated_data, GetTokenValidate)
        user = await User.query.where(
            or_(
                User.username == validated_data.get('username'),
                User.email == validated_data.get('email')
            )
        ).gino.first()
        if user is None:
            raise Unauthorized(error="incorrect username/e-mail")
        elif not user.check_password(validated_data["password"]):
            raise Unauthorized(error="incorrect password")
        return web.json_response(user.to_dict())

    async def post(self):
        unvalidated_data = await self.request.json()
        validated_data = validate(unvalidated_data, CreateUserValidate)
        validated_data['password'] = bcrypt.hashpw(
            validated_data['password'].encode(),
            bcrypt.gensalt()).decode()
        try:
            new_user = await User.create(**validated_data)
            return web.json_response(new_user.to_dict())
        except UniqueViolationError:
            raise BadRequest(
                error="user with this username/e-mail already exists."
            )


