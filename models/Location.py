from peewee import *
from models.BaseModel import BaseModel


class Location(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # Info
    name = TextField()
    longitude = DoubleField()
    latitude = DoubleField()
    radius = DoubleField()

    def __str__(self):
        return str(self.name)
