from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import fitz 
from core.ocr.ocr_model import OCR_Model
from core.rag.splitter.structured_file import TextSplitter
# from config.config import SPPLITTER_MODEL
from config.config_info import settings
from config.splitter_model import SplitterModel
from typing import List
class PDFSplitter(TextSplitter):
    def __init__(self,file_path:str,splitter_args,SPPLITTER_MODEL:SplitterModel=settings.SPPLITTER_MODEL, *args, **kwargs) -> None:
        super().__init__(splitter_args=splitter_args,SPPLITTER_MODEL=settings.SPPLITTER_MODEL,*args, **kwargs)
        self.file_path = (file_path)
        self.ocr_model = OCR_Model()
        # self.splitter_model = splittermodel
    
    def load(self) -> Document:
        doc = fitz.open(self.file_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            images = page.get_images(full=True)
            
            if text.strip():  # 提取到文字
                print("遇到文字")
                full_text += text
            
            if images:  # 如果页面中有图片
                print("遇到图片")
                for img in images:
                    xref = img[0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        ocr_text = self.ocr_model.ocr_image_by_image_bytes(image_bytes)
                        full_text += ocr_text  # 将OCR识别结果添加到全文本中
                    except Exception as e:
                        print(f"Error processing image on page {page_num}: {e}")
                        continue  # 跳过无法处理的图像
                    # print(ocr_text) 
        # print(full_text)
        return full_text 
    def split(self)->List[Document]:
        full_text = self.load()
        return super().split(full_text)
        
        
if __name__ == "__main__":
    file_path = (
        '/Users/markyangkp/WorkSpace/文档/Qanything实现识库问答/Qanything实现识库问答.pdf'
    )
    loader = PDFSplitter(file_path)
    docs = loader.split()
    for doc in docs:
        print(doc.page_content)
        print("###########################")
    # print(pages)
    # for page in pages:
    #     print(page)
    #     print("\n")
