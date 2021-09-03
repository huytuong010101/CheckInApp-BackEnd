from pydantic import BaseModel, AnyUrl


class ImageURLOut(BaseModel):
    url: str
    note: str = None
