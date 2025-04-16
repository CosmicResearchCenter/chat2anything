from core.ocr.ocr_model import OCR_Model
from langchain_core.documents import Document as LangChainDocument
from core.rag.splitter.structured_file import TextSplitter
from config.config_info import settings
from config.splitter_model import SplitterModel
from typing import List



class MarkDownSplitter(TextSplitter):
    def __init__(self, file_path: str,splitter_args=None, splitter_model: SplitterModel = settings.SPPLITTER_MODEL, *args, **kwargs):
        super().__init__(splitter_args=splitter_args,SPPLITTER_MODEL=splitter_model,*args, **kwargs)
        self.ocr_model = OCR_Model()
        self.file_path = file_path
        # self.splitter_pattern = splitter_pattern
        self.splitter_model = splitter_model

    def load(self):
        # 读取 markdown 文件
        
    
        full_text = ""

        with open(self.file_path, "r") as f:
            full_text = f.read()
        
        return full_text
    def split(self)->List[LangChainDocument]:
        full_text = self.load()
        return super().split(full_text)

if __name__ == "__main__":
    docx_splitter = MarkDownSplitter("/Users/markyangkp/WorkSpace/简历后端.md")
    print(docx_splitter.load())