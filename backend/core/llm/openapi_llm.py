from typing import List,Iterable
import sys
# sys.path.append('..')
from config.config_info import settings as llm_Settings
from .llm import LLM
import requests
import json
class OneApiLLM(LLM):
    def __init__(self, api_key: str=llm_Settings.ONEAPI_API_KEY,base_url:str=llm_Settings.ONEAPI_BASE_URL,model:str=llm_Settings.ONEAPI_MODEL) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.messages: List[Iterable[dict]] = []
        self.model = model

    def setPrompt(self, prompt: str):
        message = {"role": "system", "content": prompt}
        self.messages.append(message)
        
    def addHistory_User(self, content: str):
        message = {"role": "user", "content": content}
        self.messages.append(message)

    def addHistory_Assistant(self, content: str):
        message = {"role": "assistant", "content": content}
        self.messages.append(message)
    def addHistory(self, messages):
        self.messages.extend(messages)
    def ChatToBot(self, content: str):
        self.addHistory_User(content)
        data = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": 10240
        }
        response = requests.post(self.base_url+"/chat/completions", headers=self.headers, json=data, verify=False)
        if response.status_code == 200:
            message_content = response.json()["choices"][0]["message"]["content"]
        
            return message_content
        
    def ChatToBotWithStream(self, content: str):
        self.addHistory_User(content)
        data = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,
            "max_tokens": 10240
        }
       
        
        try:
            # 发送流式请求
            response = requests.post(
                self.base_url+"/chat/completions",
                headers=self.headers,
                json=data,
                stream=True,
                verify=False
            )
            response.raise_for_status()
            
            # 用于累积完整的消息
            full_message = ""
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    # 移除 "data: " 前缀并解析 JSON
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        line = line[6:]
                    if line == "[DONE]":
                        break
                        
                    try:
                        json_data = json.loads(line)
                        delta = json_data["choices"][0]["delta"]
                        if "content" in delta:
                            content_chunk = delta["content"]
                            full_message += content_chunk
                            yield content_chunk
                    except json.JSONDecodeError:
                        continue
            
            # 将完整的回复添加到消息历史
            if full_message:
                self.addHistory_Assistant(full_message)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Stream request failed: {str(e)}")
if __name__ == "__main__":
    # api_key = "sk-"
    # url = "https://api.openai.com/v1/"
    # openai1 = OpenAILLM(api_key=api_key,base_url=url)
    # openai1.setPrompt("你是一个聊天助手")
    # print(openai1.ChatToBot("你是谁？"))
    url = "https://oneapi.k.cn:8443/v1"
    api_key = "sk-Td6hjVG6CqOuWtC7DfA233D083534b51912d4608Ee492565"
    openai1 = OneApiLLM(base_url=url,model="qwen2-instruct",api_key=api_key)
    openai1.setPrompt("如果用户问你你是谁，请你回答：我是一个聊天助手，可以使用多种表达方式回复，但仅限说你是Mark的聊天助手。")
    while True:
        x = input("Mark:")
        res = openai1.ChatToBotWithStream(x)
        for i in res:
            print(i)
    