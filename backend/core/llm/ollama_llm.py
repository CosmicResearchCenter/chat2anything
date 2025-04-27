from ollama import Client
from typing import List, Iterable, Generator
import sys
from config.config_info import settings as llm_Settings
from llm import LLM


class OllamaLLM(LLM):

    def __init__(
            self,
            model: str,
            base_url: str
    ) -> None:
        self.client = Client(host=base_url)
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

    def ChatToBot(self, content: str) -> str:
        self.addHistory_User(content)
        response = self.client.chat(
            model=self.model,
            messages=self.messages
        )
        message_content = response['message']['content']
        self.addHistory_Assistant(message_content)
        return message_content

    def ChatToBotWithStream(self, content: str) -> Generator[str, None, None]:
        self.addHistory_User(content)
        response = self.client.chat(
            model=self.model,
            messages=self.messages,
            stream=True
        )
        for chunk in response:
            content = chunk.get('message', {}).get('content', '')
            if content:
                yield content


if __name__ == "__main__":
    # 示例用法
    ollama = OllamaLLM(
        base_url="http://localhost:11434",
        model="deepseek-r1:7b"
    )
    ollama.setPrompt("如果用户问你你是谁，请回答：我是基于deepseek的本地聊天助手")

    while True:
        user_input = input("User: ")
        # 普通模式
        # print("Assistant:", ollama.ChatToBot(user_input))

        # 流式模式
        print("Assistant: ", end="", flush=True)
        for chunk in ollama.ChatToBotWithStream(user_input):
            print(chunk, end="", flush=True)
        print()
