#!/usr/bin/env python3
"""
测试 LLM 总结功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config
from src.summarizer.llm_factory import LLMFactory


def test_summarizer():
    """测试 LLM 总结"""
    print("=" * 60)
    print("测试 LLM 总结功能")
    print("=" * 60)

    # 加载配置
    config = load_config()

    # 创建 LLM 客户端
    llm_config = config.get('llm', {})
    client = LLMFactory.create_client(llm_config)

    # 测试文本
    test_text = """
    Title: Attention Is All You Need

    Abstract: The dominant sequence transduction models are based on complex recurrent or
    convolutional neural networks that include an encoder and a decoder. The best
    performing models also connect the encoder and decoder through an attention
    mechanism. We propose a new simple network architecture, the Transformer, based
    solely on attention mechanisms, dispensing with recurrence and convolutions entirely.
    Experiments on two machine translation tasks show these models to be superior in
    quality while being more parallelizable and requiring significantly less time to
    train.
    """

    print(f"\n使用 LLM 提供商: {llm_config.get('provider')}")
    print(f"模型: {client.model}")
    print("\n测试文本:")
    print(test_text[:200] + "...")

    print("\n开始总结...")
    try:
        summary = client.summarize(test_text, language='zh')
        print("\n总结结果:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        print("\n✓ 测试成功")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_summarizer()