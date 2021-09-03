from pydantic import BaseModel, validator
from utils.peewee_util import PeeweeGetterDict
from typing import Optional


class LocationIn(BaseModel):
    # Info
    name: str
    longitude: float
    latitude: float
    radius: float

    @validator("longitude")
    def validate_longitude(cls, value):
        if value < 0:
            raise ValueError("Kinh độ phải là số không âm")
        return value

    @validator("latitude")
    def validate_latitude(cls, value):
        if value < 0:
            raise ValueError("Vĩ độ phải là số không âm")
        return value

    @validator("radius")
    def validate_radius(cls, value):
        if value < 0:
            raise ValueError("Bán kính phải là số không âm")
        return value


class LocationOut(LocationIn):
    ID: int

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class LocationUpdate(BaseModel):
    name: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    radius: Optional[float]

    @validator("longitude")
    def validate_longitude(cls, value):
        if value < 0:
            raise ValueError("Kinh độ phải là số không âm")
        return value

    @validator("latitude")
    def validate_latitude(cls, value):
        if value < 0:
            raise ValueError("Vĩ độ phải là số không âm")
        return value

    @validator("radius")
    def validate_radius(cls, value):
        if value < 0:
            raise ValueError("Bán kính phải là số không âm")
        return value

