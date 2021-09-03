from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import config
from typing import Optional
from utils.peewee_util import PeeweeGetterDict
from models.Manager import Manager


class ManagerBase(BaseModel):
    fullname: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None


class ManagerIn(ManagerBase):
    password: str

    @validator("fullname")
    def validate_fullname(cls, value: str):
        value = value.strip()
        if len(value) > 255 or any(c.isdigit() for c in value) or any(c in config.SPECIAL_CHAR for c in value):
            raise ValueError("Họ và tên chỉ có thể chứa chữ cái và dấu cách")
        return " ".join(value.split())

    @validator("phone")
    def validate_phone(cls, value: str):
        value = value.strip()
        if not value.isdigit() or not (5 <= len(value) <= 12):
            raise ValueError("Số điện thoại không hợp lệ")
        if Manager.get_or_none(phone=value) is not None:
            raise ValueError("Số điện thoại đã được đăng ký")
        return value

    @validator("username")
    def validate_username(cls, value: str):
        value = value.strip()
        if not value.isalnum() or not (5 <= len(value) <= 50):
            raise ValueError("Tên tài khoản chỏ có thể bao gồm chữ cái và số, độ dài từ 5 đến 50")
        if Manager.get_or_none(username=value) is not None:
            raise ValueError("Tên đã khoản đã được sử dụng")
        return value

    @validator("password")
    def validate_password(cls, value: str):
        if not (5 <= len(value) <= 50):
            raise ValueError("Mật khẩu phải có độ dài từ 5 đến 50")
        return value


class ManageOut(ManagerBase):
    ID: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_admin: bool
    avatar_image: str = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class ManagerUpdate(BaseModel):
    fullname: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    username: Optional[str]
    is_admin: Optional[bool]

    @validator("fullname")
    def validate_fullname(cls, value: str):
        value = value.strip()
        if len(value) > 255 or any(c.isdigit() for c in value) or any(c in config.SPECIAL_CHAR for c in value):
            raise ValueError("Họ và tên chỉ có thể chứa chữ cái và dấu cách")
        return " ".join(value.split())

    @validator("phone")
    def validate_phone(cls, value: str):
        value = value.strip()
        if not value.isdigit() or not (5 <= len(value) <= 12):
            raise ValueError("Số điện thoại không hợp lệ")
        return value

    @validator("username")
    def validate_username(cls, value: str):
        value = value.strip()
        if not value.isalnum() or not (5 <= len(value) <= 50):
            raise ValueError("Tên tài khoản chỏ có thể bao gồm chữ cái và số, độ dài từ 5 đến 50")
        return value

