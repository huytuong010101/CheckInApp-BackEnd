from peewee import Model
from database_connection import db


class BaseModel(Model):
    class Meta:
        database = db
