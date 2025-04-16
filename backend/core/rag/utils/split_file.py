from ..splitter import PDFSplitter,TextSplitter,DocxSplitter,ExcelSplitter,MarkDownSplitter
from langchain_core.documents import Document
from typing import List
from core.ocr.ocr_model import OCR_Model
from config.splitter_model import SplitterModel
from config.config_info import settings
def split_file(file_path:str,splitter_args,splitterModel:SplitterModel=settings.SPPLITTER_MODEL)->List[Document]:
    docs:List[Document] = []
    # 判断文件类型
    if file_path.lower().endswith(".txt"):
        print("txt file")
        with open(file_path) as f:
            state_of_the_union = f.read()
        textSplitter = TextSplitter(splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = textSplitter.split(state_of_the_union)
        return docs
    elif file_path.lower().endswith(".pdf"):
        print("pdf file")
        # pdf文件
        loader = PDFSplitter(file_path=file_path,splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = loader.split()
        # print(docs)
    elif file_path.lower().endswith(".doc"):
        loader = DocxSplitter(file_path=file_path,splitter_args=splitter_args,splitter_model=splitterModel)
        docs = loader.split()
    elif file_path.lower().endswith(".docx"):
        loader = DocxSplitter(file_path=file_path,splitter_args=splitter_args,splitter_model=splitterModel)
        docs = loader.split()
    elif file_path.lower().endswith(".xls"):
        loader = ExcelSplitter(file_path=file_path,splitter_args=splitter_args,splitter_model=splitterModel)
        docs = loader.split()
    elif file_path.lower().endswith(".xlsx"):
        loader = ExcelSplitter(file_path=file_path,splitter_args=splitter_args,splitter_model=splitterModel)
        docs = loader.split()
    elif file_path.lower().endswith(".ppt"):
        pass
    elif file_path.lower().endswith(".pptx"):
        pass
    elif file_path.lower().endswith(".png"):
        ocr_model = OCR_Model()        
        state_of_the_union = ocr_model.ocr_image_by_file(file_path) 
        textSplitter = TextSplitter(splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = textSplitter.split(state_of_the_union)
    elif file_path.lower().endswith(".jpg"):
        ocr_model = OCR_Model()        
        state_of_the_union = ocr_model.ocr_image_by_file(file_path) 
        textSplitter = TextSplitter(splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = textSplitter.split(state_of_the_union)
    elif file_path.lower().endswith(".jpeg"):
        ocr_model = OCR_Model()        
        state_of_the_union = ocr_model.ocr_image_by_file(file_path) 
        textSplitter = TextSplitter(splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = textSplitter.split(state_of_the_union)
    elif file_path.lower().endswith(".png"):
        ocr_model = OCR_Model()        
        state_of_the_union = ocr_model.ocr_image_by_file(file_path) 
        textSplitter = TextSplitter(splitter_args=splitter_args,SPPLITTER_MODEL=splitterModel)
        docs = textSplitter.split(state_of_the_union)
    elif file_path.lower().endswith(".md"):
        loader = MarkDownSplitter(file_path=file_path,splitter_args=splitter_args,splitter_model=splitterModel)
        docs = loader.split()
    else:
        raise Exception("File type not support")

    return docs

if __name__ == "__main__":
    file_path = "/Users/markyangkp/Desktop/Projects/llmqa/ocr/testimg.png"
    docs:List[Document] = split_file(file_path,SplitterModel.LLMSplitter)
    print(docs)