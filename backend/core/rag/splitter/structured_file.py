from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from core.llm.llm_manager import LLM_Manager
from config.config_info import settings
from config.splitter_model import SplitterModel
from concurrent.futures import ThreadPoolExecutor

class TextSplitter:
    def __init__(self,splitter_args,SPPLITTER_MODEL=settings.SPPLITTER_MODEL,split_model:str=settings.LLM_PROVIDER):
        # self.chunk_size = chunk_size
        # self.chunk_overlap = chunk_overlap
        # self.length_function = length_function
        # self.is_separator_regex = is_separator_regex
        self.splitter_args = splitter_args

        self.split_model = split_model
        self.SPPLITTER_MODEL = SPPLITTER_MODEL
        self.result:List[Document] = []
        # self.llm_client = LLM_Manager().creatLLM(split_model)
    # 拆分文本
    def _split_texts(self, text)->List[Document]:
        texst = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=self.splitter_args['chunk_size'],
            chunk_overlap=self.splitter_args['chunk_overlap']
        )
        texts = texst.create_documents([text])
        
        return texts
    def split_texts(self, state_of_the_union:str) -> List[Document]:
        
        return self._split_texts(state_of_the_union)
    
    ###############大模型拆分文本###############
    
    def _SplitText(self,texts:str,splitter_str:str)->List[Document]:
        result:List[Document] = []
        splitted_texts = texts.split(splitter_str)
        for text in splitted_texts:
            result.append(Document(page_content=text))
        return result

    def SplitTextByLLM(self,text:str,splitter_str:str) -> List[Document]:
        print(len(text) )
        if len(text)<int(self.splitter_args['window_size']):
            llm_client = LLM_Manager().creatLLM(self.split_model)
            prompt:str = f"""
            请将以下文本拆分成逻辑清晰、内容独立的段落或部分。每个段落应完整表达一个主要思想或主题，并控制段落的长度，使其便于后续的分析和处理。每个段落之间使用指定的拆分符进行分隔，确保拆分后的内容不被修改

            拆分符: {splitter_str}

            请根据文本的结构、主题和意义进行合理拆分：
            {text}
            """
            llm_client.setPrompt(prompt="你是一名专业的文本拆分助手，你的任务是帮助用户拆分文本内容。")
            texts = llm_client.ChatToBot(content=prompt)
            self.result = self._SplitText(texts,splitter_str)
            
            return self.result
        else:
            # 把text分成多个部分，滑动窗口滑动，然后拆分，确保不丢失过多信息
            window_size = int(self.splitter_args['window_size'])  # 滑动窗口的大小
            step_size = int(self.splitter_args['step_size'])    # 滑动步长
            index = 1
            text_length = len(text)

            with ThreadPoolExecutor(max_workers=6) as executor:
                # 处理完整的窗口块
                for i in range(0, text_length - window_size + 1, step_size):
                    executor.submit(self._LLM_Task, text[i:i + window_size], splitter_str)
                    print(f"正在处理第{index}个块")
                    index += 1
                
                # 如果剩余文本不足一个窗口大小，处理最后的部分
                if text_length % step_size != 0:
                    last_chunk_start = max(text_length - window_size, 0)
                    executor.submit(self._LLM_Task, text[last_chunk_start:], splitter_str)
                    print(f"正在处理最后一个块 (剩余文本)")
            return self.result
    def _LLM_Task(self,retriever_text:str,splitter_str:str)->List[Document]:
        llm_client = LLM_Manager().creatLLM(self.split_model)
        prompt:str = f"""
        请将以下文本拆分成逻辑清晰、内容独立的段落或部分。每个段落应可以完整表达一个主要思想或主题。并控制段落的长度，使其便于后续的分析和处理。每个段落之间使用指定的拆分符进行分隔。请不要修改文本内容，确保拆分后的内容不被修改
        拆分符: {splitter_str}
        需要拆分的文本:
        {retriever_text}
        """               
        llm_client.setPrompt(prompt="你是一名专业的文本拆分助手，你的任务是帮助用户拆分文本。")
        texts = llm_client.ChatToBot(content=prompt)
        item = self._SplitText(texts,splitter_str)
        self.result.extend(item) 
    def split(self,full_text:str)->List[Document]:
            
            if self.SPPLITTER_MODEL == SplitterModel.LLMSplitter:
                return self.SplitTextByLLM(full_text, "&&&&&")
            elif self.SPPLITTER_MODEL == SplitterModel.TextSplitter:
                return self.split_texts(full_text)
    
if __name__ == "__main__":
    # text = "This is a test. This is another test."
    with open("/Users/markyangkp/Desktop/Projects/llmqa/ocr/tmp_files/data.txt", "r") as f:
        text = f.read() 
    splitter = TextSplitter()
    docs = splitter.SplitTextByLLM(text,"&&&&&")
    for i in docs:
        print(i.page_content)
        print("---------------------\n")