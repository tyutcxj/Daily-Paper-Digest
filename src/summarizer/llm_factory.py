"""
LLM 工厂模块
"""

import logging
from typing import Dict, Any

from .base_llm_client import BaseLLMClient
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient
from .gemini_client import GeminiClient
from .deepseek_client import DeepSeekClient
from .vllm_client import VLLMClient

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM 工厂类"""

    @staticmethod
    def create_client(config: Dict[str, Any]) -> BaseLLMClient:
        """创建 LLM 客户端"""
        provider = config.get('provider', 'openai').lower()
        logger.info(f"创建 LLM 客户端: {provider}")

        if provider == 'openai':
            return OpenAIClient(config.get('openai', {}))
        elif provider == 'claude':
            return ClaudeClient(config.get('claude', {}))
        elif provider == 'gemini':
            return GeminiClient(config.get('gemini', {}))
        elif provider == 'deepseek':
            return DeepSeekClient(config.get('deepseek', {}))
        elif provider == 'vllm':
            return VLLMClient(config.get('vllm', {}))
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")