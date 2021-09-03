from pydantic import BaseModel, validator


class Password(BaseModel):
    old_password: str
    new_password: str

    @validator("new_password")
    def validate_password(cls, value: str):
        if not (5 <= len(value) <= 50):
            raise ValueError("Mật khẩu phải có độ dài từ 5 đến 50")
        return value


class SinglePassword(BaseModel):
    new_password: str

    @validator("new_password")
    def validate_password(cls, value: str):
        if not (5 <= len(value) <= 50):
            raise ValueError("Mật khẩu phải có độ dài từ 5 đến 50")
        return value

