from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from utils.peewee_util import PeeweeGetterDict


class CheckinNoUserNoEvent(BaseModel):
    ID: int
    uploaded_at: datetime
    accept: Optional[bool] = None
    accepted_at: Optional[datetime] = None
    score: Optional[float] = None

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


class BriefEvent(BaseModel):
    ID: int
    title: str
    place: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CheckInNoEvent(CheckinNoUserNoEvent):
    user: BriefUser

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CheckInNoUser(CheckinNoUserNoEvent):
    event: BriefEvent

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class CheckIn(CheckinNoUserNoEvent):
    user: BriefUser
    event: BriefEvent

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


