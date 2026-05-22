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
            system_prompt = """你是一个学术论文总结专家。请用简洁的中文总结论文，不超过100字。必须严格按照以下格式输出，每行一个要点，不要添加任何额外内容。"""
            user_prompt = f"""请总结以下论文：

{text[:1500]}

严格按照此格式输出（每行必须完整，不能有重复字符）：
研究问题：xxx
主要方法：xxx
关键贡献：xxx"""
        else:
            system_prompt = """You are an academic paper summarizer. Summarize in English, under 100 words. Follow the exact format below, one point per line, no extra content."""
            user_prompt = f"""Summarize this paper:

{text[:1500]}

Output exactly in this format (each line must be complete, no repeated characters):
Problem: xxx
Method: xxx
Contribution: xxx"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]