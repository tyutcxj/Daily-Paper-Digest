"""
DeepSeek LLM 客户端
"""

import logging
from typing import List, Dict, Any
from openai import OpenAI

from .base_llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseLLMClient):
    """DeepSeek LLM 客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.get('api_key'),
            base_url=config.get('base_url', 'https://api.deepseek.com/v1')
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise

    def summarize(self, text: str, **kwargs) -> str:
        """总结文本"""
        language = kwargs.get('language', 'zh')
        messages = self._build_summarize_prompt(text, language)
        return self.chat(messages, **kwargs)