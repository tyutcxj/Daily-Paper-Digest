"""
Google Gemini LLM 客户端
"""

import logging
from typing import List, Dict, Any
import google.generativeai as genai

from .base_llm_client import BaseLLMClient

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """Google Gemini LLM 客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        genai.configure(api_key=config.get('api_key'))
        self.model_instance = genai.GenerativeModel(self.model)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            # 转换消息格式
            prompt = self._convert_messages(messages)

            response = self.model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', self.temperature),
                    max_output_tokens=kwargs.get('max_tokens', self.max_tokens)
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API 调用失败: {e}")
            raise

    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表转换为单个提示"""
        parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                parts.append(f"System: {content}")
            elif role == 'user':
                parts.append(f"User: {content}")
            elif role == 'assistant':
                parts.append(f"Assistant: {content}")
        return "\n\n".join(parts)

    def summarize(self, text: str, **kwargs) -> str:
        """总结文本"""
        language = kwargs.get('language', 'zh')
        messages = self._build_summarize_prompt(text, language)
        return self.chat(messages, **kwargs)