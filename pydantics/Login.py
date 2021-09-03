from pydantic import BaseModel
from enum import Enum


class LoginMode(str, Enum):
    STUDENT = 'STUDENT'
    MANAGER = 'MANAGER'


class LoginForm(BaseModel):
    username: str
    password: str
    mode: LoginMode
