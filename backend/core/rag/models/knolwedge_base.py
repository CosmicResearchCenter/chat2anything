from pydantic import BaseModel
from typing import List
from .source_document import SourceDocumentReRanked

class ResultByDoc(BaseModel):
    source:List[SourceDocumentReRanked]
    query:str
