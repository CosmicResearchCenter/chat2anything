from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from config.config_info import settings as llm_Settings
from typing import List,Iterable
from .llm import LLM



class SparkAILLM(LLM):
    def __init__(self, 
                 spark_api_key: str,
                 spark_api_url:str,
                 spark_api_secret:str,
                 spark_llm_domain:str,
                 spark_app_id:str,
            ) -> None:
        self.client = ChatSparkLLM(spark_api_key=spark_api_key,spark_api_secret=spark_api_secret,spark_app_id=spark_app_id,spark_llm_domain=spark_llm_domain,spark_api_url=spark_api_url)
        self.messages: List[ChatMessage] = []

    def setPrompt(self, prompt: str):
        message =ChatMessage(role="system", content=prompt)
        self.messages.append(message)
        
    def addHistory_User(self, content: str):
        message = ChatMessage(role="user", content=content)
        self.messages.append(message)

    def addHistory_Assistant(self, content: str):
        message = ChatMessage(role="assistant", content=content)
        self.messages.append(message)
    def addHistory(self, messages: List[ChatMessage]):
        self.messages.extend(messages)
    def ChatToBot(self, content: str):
        self.addHistory_User(content)
        handler = ChunkPrintHandler()
        a = self.client.generate([self.messages], callbacks=[handler])
        
        return a.generations[0][0].text
    def ChatToBotWithStream(self, content: str):
        self.addHistory_User(content)
        handler = ChunkPrintHandler()
        self.client.streaming = True
        response = self.client.generate([self.messages], callbacks=[handler])
        print(type(response))
        return response
if __name__ == "__main__":
    llm = SparkAILLM()
    llm.setPrompt("你是谁")
    a = llm.ChatToBotWithStream("你是谁")
    print(a)