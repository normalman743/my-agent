# models/LLM/base_client.py
from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        根据提示生成响应
        :param prompt: 提示文本
        :return: 生成的响应
        """
        pass