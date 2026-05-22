"""
Anthropic Claude LLM 客户端
"""

import logging
from typing import List, Dict, Any
import anthropic

from .base_llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude LLM 客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = anthropic.Anthropic(
            api_key=config.get('api_key')
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            # 提取系统消息
            system_message = ""
            user_messages = []

            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    user_messages.append(msg)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                system=system_message,
                messages=user_messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API 调用失败: {e}")
            raise

    def summarize(self, text: str, **kwargs) -> str:
        """总结文本"""
        language = kwargs.get('language', 'zh')
        messages = self._build_summarize_prompt(text, language)
        return self.chat(messages, **kwargs)