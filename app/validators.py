import re

import pydantic
from pydantic import BaseModel, root_validator, ValidationError

from app.error_handlers import Unauthorized, HttpError, BadRequest


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
            raise ValueError("username or e-mail is required fields")
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


def validate(unvalidated_data: dict, validation_model):
    try:
        return dict(validation_model(**unvalidated_data))
    except ValidationError as er:
        raise BadRequest(error=er.errors())
