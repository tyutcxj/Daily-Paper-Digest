#!/usr/bin/env python3
"""
测试 arXiv 论文爬取
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config
from src.crawler.arxiv_fetcher import ArxivFetcher


def test_fetch():
    """测试论文爬取"""
    print("=" * 60)
    print("测试 arXiv 论文爬取")
    print("=" * 60)

    # 加载配置
    config = load_config()

    # 创建爬取器
    fetcher = ArxivFetcher(config.get('arxiv', {}))

    # 获取论文
    print("\n开始获取论文...")
    papers = fetcher.fetch_papers()

    print(f"\n成功获取 {len(papers)} 篇论文")

    # 显示前 5 篇论文
    for i, paper in enumerate(papers[:5]):
        print(f"\n--- 论文 {i+1} ---")
        print(f"标题: {paper['title']}")
        print(f"作者: {', '.join(paper['authors'][:3])}...")
        print(f"类别: {', '.join(paper['categories'][:3])}")
        print(f"发布日期: {paper['published']}")
        print(f"PDF: {paper['pdf_url']}")
        print(f"摘要: {paper['abstract'][:100]}...")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_fetch()