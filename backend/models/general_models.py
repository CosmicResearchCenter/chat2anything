from pydantic import BaseModel
from typing import List,Dict,Optional,Any
class GenericResponse(BaseModel):
    message: str
    code: int
    data: List[Any]

