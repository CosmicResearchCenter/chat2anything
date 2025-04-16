from pydantic import BaseModel
from typing import List,Dict

class ImageBaseInfo(BaseModel):
    img64:str
    height: int
    width: int
    channels:int
    