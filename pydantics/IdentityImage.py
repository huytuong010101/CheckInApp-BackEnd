from pydantic import BaseModel
from datetime import datetime
from utils.peewee_util import PeeweeGetterDict


class IdentityImageNoUser(BaseModel):
    ID: int
    uploaded_at: datetime
    approve: bool

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class BriefUser(BaseModel):
    ID: int
    fullname: str
    student_id: str
    phone: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class IdentityImage(IdentityImageNoUser):
    user: BriefUser

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

