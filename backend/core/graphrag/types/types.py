from typing import List,Dict
from pydantic import BaseModel

class Entity_Label(BaseModel):
    name:str
    
class Entity(BaseModel):
    label:str
    attribute:Dict[str, str]
    ext_info:str

class Entity_Relation(BaseModel):
    source:Entity
    target:Entity
    relation:str
    evidence:str