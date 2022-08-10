from operator import or_, and_

import bcrypt
from aiohttp import web
from asyncpg.exceptions import UniqueViolationError

from error_handlers import BadRequest, Unauthorized
from models import User, Advertisement
from validators import (
    validate,
    GetTokenValidate,
    CreateUserValidate,
    CreateAdvertisementModel,
    UpdateAdvertisementModel,
    CheckToken, CheckUserId, CheckOwner,
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
        validate({"user_id": user_id}, CheckUserId)
        new_adv = await Advertisement.create(owner_id=user_id, **validated_data)
        return web.json_response(new_adv.to_dict())

    async def patch(self):
        unvalidated_data = await self.request.json()
        unvalidated_data['token'] = self.request.headers.get('Authorization')
        validated_data = validate(unvalidated_data, UpdateAdvertisementModel)
        user_id = await User.get_id(validated_data.pop('token'))
        validate({"user_id": user_id}, CheckUserId)
        adv_id = int(self.request.match_info.get("adv_id"))
        advertisement_owner = await Advertisement.is_owner(user_id, adv_id)
        validate({'adv_owner': advertisement_owner}, CheckOwner)
        await advertisement_owner.update(**validated_data).apply()
        return web.json_response(advertisement_owner.to_dict())

    async def delete(self):
        token = self.request.headers.get('Authorization')
        validated_data = validate({'token': token}, CheckToken)
        user_id = await User.get_id(validated_data.pop('token'))
        validate({"user_id": user_id}, CheckUserId)
        adv_id = int(self.request.match_info.get("adv_id"))
        advertisement_owner = await Advertisement.is_owner(user_id, adv_id)
        validate({'adv_owner': advertisement_owner}, CheckOwner)
        await advertisement_owner.update(is_active=False).apply()
        return web.json_response(status=204)
