from operator import or_, and_

import bcrypt
from aiohttp import web
from asyncpg.exceptions import UniqueViolationError

from app.error_handlers import BadRequest, Unauthorized, Forbidden
from app.models import User, Advertisement
from app.validators import (
    validate,
    GetTokenValidate,
    CreateUserValidate,
    CreateAdvertisementModel,
    UpdateAdvertisementModel,
    CheckToken,
)


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


class AdvertisementsView(web.View):

    async def get(self):
        adv_id = self.request.match_info.get("adv_id")
        if adv_id is None:
            advertisements = await Advertisement.query.where(
                Advertisement.is_active == True
            ).gino.all()
            return web.json_response([advertisement.to_dict() for advertisement in advertisements])
        try:
            advertisement = await Advertisement.query.where(
                and_(
                    Advertisement.id == int(adv_id),
                    Advertisement.is_active == True
                )
            ).gino.first()
            return web.json_response(advertisement.to_dict())
        except AttributeError:
            raise BadRequest(error="incorrect advertisement id")

    async def post(self):
        unvalidated_data = await self.request.json()
        unvalidated_data['token'] = self.request.headers.get('Authorization')
        validated_data = validate(unvalidated_data, CreateAdvertisementModel)
        user_id = await User.get_id(validated_data.pop('token'))
        if user_id is None:
            raise BadRequest(error="incorrect token")
        new_adv = await Advertisement.create(owner_id=user_id, **validated_data)
        return web.json_response(new_adv.to_dict())

    async def patch(self):
        unvalidated_data = await self.request.json()
        unvalidated_data['token'] = self.request.headers.get('Authorization')
        validated_data = validate(unvalidated_data, UpdateAdvertisementModel)
        adv_id = int(self.request.match_info.get("adv_id"))
        advertisement_owner = await Advertisement.is_owner(
            validated_data.pop('token'), adv_id)
        if advertisement_owner is None:
            raise BadRequest(error="incorrect advertisement id")
        elif not advertisement_owner:
            raise Forbidden(error="permission denied")
        await advertisement_owner.update(**validated_data).apply()
        return web.json_response(advertisement_owner.to_dict())

    async def delete(self):
        token = self.request.headers.get('Authorization')
        validated_data = validate({'token': token}, CheckToken)
        adv_id = int(self.request.match_info.get("adv_id"))
        advertisement_owner = await Advertisement.is_owner(
            validated_data.pop('token'), adv_id)

        if advertisement_owner is None:
            raise BadRequest(error="incorrect advertisement id")
        elif not advertisement_owner:
            raise Forbidden(error="permission denied")
        await advertisement_owner.update(is_active=False).apply()
        return web.json_response(status=204)
