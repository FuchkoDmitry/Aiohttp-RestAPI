import re
from typing import Union, Optional, Any

import pydantic
from pydantic import BaseModel, root_validator, ValidationError

from error_handlers import BadRequest


email_regex = re.compile(
    r"([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)"
)

password_regex = re.compile(
    r"^(?=.*[a-z_])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!#%*?&_]{8,200}$"
)


class GetTokenValidate(BaseModel):

    username: str = None
    email: str = None
    password: str = None

    @root_validator(pre=True)
    def check_password(cls, values):
        if values.get('password') is None:
            raise ValueError("password is required field")
        return values

    @root_validator
    def check_fields(cls, values):
        if values.get('email') is None and values.get('username') is None:
            raise ValueError("username or e-mail must be defined")
        return values


class CreateUserValidate(BaseModel):

    username: str
    email: str
    password: str

    @pydantic.validator('email')
    def correct_email(cls, value: str):
        if not re.search(email_regex, value):
            raise ValueError("incorrect e-mail")
        return value

    @pydantic.validator('password')
    def strong_password(cls, value: str):
        if not re.search(password_regex, value):
            raise ValueError("password too easy")
        return value


class CheckUserId(BaseModel):
    user_id: Union[int, None]

    @pydantic.validator('user_id')
    def check_id(cls, value):
        if value is None:
            raise ValueError("incorrect token")
        return value


class CheckOwner(BaseModel):
    adv_owner: Any = None

    @pydantic.validator('adv_owner')
    def check_adv_owner(cls, value):
        if value is None:
            raise ValueError("incorrect advertisement id")
        elif not value:
            raise ValueError("permission denied")
        return value


class CheckToken(BaseModel):
    token: str = None

    @pydantic.validator('token')
    def check_token(cls, value: str):
        if value is None:
            raise ValueError("token is required")
        value = value.replace('Token ', '')
        if len(value) != 36:
            raise ValueError("incorrect token")
        return value.replace('Token ', '')


class CreateAdvertisementModel(CheckToken):
    title: str
    description: str


class UpdateAdvertisementModel(CreateAdvertisementModel):
    title: Optional[str] = None
    description: Optional[str] = None

    @root_validator
    def check_fields(cls, values):
        if values.get('title') is None and values.get('description') is None:
            raise ValueError("title or description must be defined")
        return values


def validate(unvalidated_data: dict, validation_model):
    try:
        return dict(validation_model(**unvalidated_data))
    except ValidationError as er:
        raise BadRequest(error=er.errors())
