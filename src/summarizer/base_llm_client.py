"""
LLM 客户端基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseLLMClient(ABC):
    """LLM 客户端基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', '')
        self.temperature = config.get('temperature', 0.2)
        self.max_tokens = config.get('max_tokens', 8192)

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def summarize(self, text: str, **kwargs) -> str:
        """总结文本"""
        pass

    def _build_summarize_prompt(self, text: str, language: str = 'zh') -> List[Dict[str, str]]:
        """构建总结提示词"""
        if language == 'zh':
            system_prompt = """你是学术论文总结专家。用中文总结论文，150字以内。只输出总结，不要解释格式。"""
            user_prompt = f"总结：\n\n{text[:2000]}\n\n输出格式：\n研究问题：xxx\n主要方法：xxx\n关键贡献：xxx"
        else:
            system_prompt = """Summarize academic papers in English, under 150 words. Output summary only."""
            user_prompt = f"Summarize:\n\n{text[:2000]}\n\nFormat:\nProblem: xxx\nMethod: xxx\nContribution: xxx"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]