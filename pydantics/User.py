from pydantic import BaseModel, EmailStr, ValidationError, validator
from datetime import datetime, date
import config
from models.User import User
from typing import Optional
from utils.peewee_util import PeeweeGetterDict


class UserBase(BaseModel):
    fullname: str
    date_of_birth: date
    student_id: str
    email: Optional[EmailStr] = None
    phone: str
    note: Optional[str] = None
    username: str


class UserOut(UserBase):
    ID: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    phone_verify: bool
    email_verify: bool
    block: bool
    avatar_image: Optional[str] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class UserIn(UserBase):
    password: Optional[str] = None

    @validator("fullname")
    def validate_fullname(cls, value: str):
        value = value.strip()
        if len(value) > 255 or any(c.isdigit() for c in value) or any(c in config.SPECIAL_CHAR for c in value):
            raise ValueError("Họ và tên chỉ có thể chứa chữ cái và dấu cách")
        return " ".join(value.split())

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value: date):
        if value >= datetime.now().date():
            raise ValueError("Ngày sinh không hợp lệ")
        return value

    @validator("student_id")
    def validate_student_id(cls, value: str):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("Mã sinh viên chỉ có thể chứa chữ số")
        if User.get_or_none(student_id=value) is not None:
            raise ValueError("Mã sinh viên đã được đăng ký")
        return value

    @validator("phone")
    def validate_phone(cls, value: str):
        value = value.strip()
        if not value.isdigit() or not (5 <= len(value) <= 12):
            raise ValueError("Số điện thoại không hợp lệ")
        if User.get_or_none(phone=value) is not None:
            raise ValueError("Số điện thoại đã được đăng ký")
        return value

    @validator("username")
    def validate_username(cls, value: str):
        value = value.strip()
        if not value.isalnum() or not (5 <= len(value) <= 50):
            raise ValueError("Tên tài khoản chỏ có thể bao gồm chữ cái và số, độ dài từ 5 đến 50")
        if User.get_or_none(username=value) is not None:
            raise ValueError("Tên đã khoản đã được sử dụng")
        return value

    @validator("password")
    def validate_password(cls, value: str):
        if not (5 <= len(value) <= 50):
            raise ValueError("Mật khẩu phải có độ dài từ 5 đến 50")
        return value


class UserUpdate(BaseModel):
    fullname: Optional[str]
    date_of_birth:  Optional[date]
    email: Optional[EmailStr]
    student_id: Optional[str]
    phone:  Optional[str]
    block:  Optional[bool]
    note: Optional[str]
    username:  Optional[str]

    @validator("fullname")
    def validate_fullname(cls, value: str):
        value = value.strip()
        if len(value) > 255 or any(c.isdigit() for c in value) or any(c in config.SPECIAL_CHAR for c in value):
            ValueError("Họ và tên chỉ có thể chứa chữ cái và dấu cách")
        return " ".join(value.split())

    @validator("date_of_birth")
    def validate_date_of_birth(cls, value: date):
        if value >= datetime.now().date():
            raise ValueError("Ngày sinh không hợp lệ")
        return value

    @validator("student_id")
    def validate_student_id(cls, value: str, values: dict):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("Mã sinh viên chỉ có thể chứa chữ số")
        return value

    @validator("phone")
    def validate_phone(cls, value: str, values: dict):
        value = value.strip()
        if not value.isdigit() or not (5 <= len(value) <= 12):
            raise ValueError("Số điện thoại không hợp lệ")
        return value

    @validator("username")
    def validate_username(cls, value: str, values: dict):
        value = value.strip()
        if not value.isalnum() or not (5 <= len(value) <= 50):
            raise ValueError("Tên tài khoản chỏ có thể bao gồm chữ cái và số, độ dài từ 5 đến 50")
        return value







