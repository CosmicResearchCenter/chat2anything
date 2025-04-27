from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.chat import ChatCompletionMessage,ChatCompletionSystemMessageParam,ChatCompletionUserMessageParam,ChatCompletionAssistantMessageParam,ChatCompletionRole,ChatCompletionMessageParam
from typing import List,Iterable
from config.config_info import settings as llm_Settings
# (type alias) ChatCompletionMessageParam: type[ChatCompletionSystemMessageParam] | type[ChatCompletionUserMessageParam] | type[ChatCompletionAssistantMessageParam] | type[ChatCompletionToolMessageParam] | type[ChatCompletionFunctionMessageParam]
from .llm import LLM
class DouBaoLLM(LLM):
    def __init__(self,api_key,base_url,model:str) -> None:
        self.client = Ark(api_key=api_key,base_url=base_url)
        self.messages:List[Iterable[ChatCompletionMessageParam]]= []
        self.model:str = model

    def setPrompt(self,prompt:str):
        message:ChatCompletionSystemMessageParam = ChatCompletionSystemMessageParam(role="system",content=prompt) 
        self.messages.append(message)
    def addHistory_User(self,content):
        message:ChatCompletionUserMessageParam = ChatCompletionUserMessageParam(role="user",content=content) 
        self.messages.append(message)
    def addHistory_Assistant(self,content):
        message:ChatCompletionAssistantMessageParam = ChatCompletionAssistantMessageParam(role="assistant",content=content)
        self.messages.append(message)
    def addHistory(self, messages):
        self.messages.extend(messages)
    def ChatToBot(self,content:str):
        self.addHistory_User(content)
        completion = self.client.chat.completions.create(
            model="ep-20240726180335-zb62t",
            messages = self.messages,
            stream=False,
        )
        return completion.choices[0].message.content
    def ChatToBotWithStream(self, content: str):
        self.addHistory_User(content)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        for chunk in response:
            yield chunk.choices[0].delta.content
if __name__ == "__main__":
    doubao = DouBaoLLM()
    doubao.setPrompt("你是一个聊天助手")
    print(doubao.ChatToBot("你好"))