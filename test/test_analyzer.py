#!/usr/bin/env python3
"""
测试趋势分析
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config
from src.crawler.arxiv_fetcher import ArxivFetcher
from src.analyzer.trend_analyzer import TrendAnalyzer


def test_analyzer():
    """测试趋势分析"""
    print("=" * 60)
    print("测试趋势分析")
    print("=" * 60)

    # 加载配置
    config = load_config()

    # 创建爬取器
    fetcher = ArxivFetcher(config.get('arxiv', {}))

    # 获取论文
    print("\n获取论文...")
    papers = fetcher.fetch_papers()
    print(f"成功获取 {len(papers)} 篇论文")

    if not papers:
        print("未获取到论文，无法进行分析")
        return

    # 创建分析器
    analyzer = TrendAnalyzer(config)

    # 进行分析
    print("\n进行趋势分析...")
    analysis = analyzer.analyze_trends(papers, [])

    print(f"\n分析结果:")
    print(f"  论文数量: {analysis['paper_count']}")
    print(f"  关键词数量: {len(analysis.get('keywords', []))}")
    print(f"  类别数量: {len(analysis.get('categories', []))}")

    # 显示关键词
    print(f"\nTop 10 关键词:")
    for kw in analysis.get('keywords', [])[:10]:
        print(f"  - {kw['keyword']}: {kw['score']:.4f}")

    # 显示类别
    print(f"\nTop 5 类别:")
    for cat in analysis.get('categories', [])[:5]:
        print(f"  - {cat['category']}: {cat['count']}")

    if analysis.get('wordcloud_path'):
        print(f"\n词云图已保存: {analysis['wordcloud_path']}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_analyzer()