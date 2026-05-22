#!/usr/bin/env python3
"""
Daily arXiv - Main Entry Point
自动追踪 arXiv 最新论文，使用 LLM 进行智能总结
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils import load_config, setup_logging
from src.crawler.arxiv_fetcher import ArxivFetcher
from src.crawler.zotero_client import ZoteroClient
from src.crawler.personalized_recommender import PersonalizedRecommender
from src.summarizer.paper_summarizer import PaperSummarizer
from src.analyzer.trend_analyzer import TrendAnalyzer


def main():
    """主函数：执行完整的论文追踪和分析流程"""
    # 加载配置
    config = load_config()

    # 设置日志
    setup_logging(config.get('logging', {}))
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Daily arXiv - 开始执行")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 1. 获取论文
        logger.info("步骤 1/4: 获取 arXiv 论文...")
        fetcher = ArxivFetcher(config.get('arxiv', {}))
        papers = fetcher.fetch_papers()
        logger.info(f"成功获取 {len(papers)} 篇论文")

        if not papers:
            logger.warning("未获取到任何论文，流程结束")
            return

        # 2. 个性化推荐（基于 Zotero 库）
        logger.info("步骤 2/4: 个性化推荐...")
        papers = personalize_papers(config, papers, logger)

        # 3. 使用 LLM 总结论文
        logger.info("步骤 3/4: 使用 LLM 总结论文...")
        summarizer = PaperSummarizer(config.get('llm', {}))
        summaries = summarizer.summarize_papers(papers)
        logger.info(f"成功总结 {len(summaries)} 篇论文")

        # 4. 趋势分析
        logger.info("步骤 4/4: 生成趋势分析报告...")
        analyzer = TrendAnalyzer(config)
        analysis = analyzer.analyze_trends(papers, summaries)
        logger.info("趋势分析完成")

        logger.info("=" * 60)
        logger.info("Daily arXiv - 执行完成")
        logger.info(f"论文数量: {len(papers)}")
        logger.info(f"总结数量: {len(summaries)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"执行过程中出现错误: {e}", exc_info=True)
        raise


def personalize_papers(config, papers, logger):
    """基于 Zotero 库进行个性化推荐"""
    import os

    zotero_user_id = os.getenv('ZOTERO_USER_ID')
    zotero_api_key = os.getenv('ZOTERO_API_KEY')

    if not zotero_user_id or not zotero_api_key:
        logger.warning("未配置 Zotero API，跳过个性化推荐")
        return papers

    try:
        # 初始化 Zotero 客户端
        zotero = ZoteroClient(zotero_user_id, zotero_api_key)

        # 初始化推荐器
        recommender = PersonalizedRecommender(zotero)

        # 加载用户资料
        if not recommender.load_user_profile():
            logger.warning("加载用户资料失败，跳过个性化推荐")
            return papers

        # 个性化排序
        logger.info(f"正在根据你的 Zotero 库推荐 {len(papers)} 篇论文...")
        ranked_papers = recommender.rank_papers(papers, top_n=20)

        # 获取推荐摘要
        summary = recommender.get_recommendation_summary(ranked_papers)
        logger.info(f"推荐结果: 平均相关度 {summary.get('avg_relevance_score', 0):.3f}")

        return ranked_papers

    except Exception as e:
        logger.error(f"个性化推荐失败: {e}")
        return papers


if __name__ == "__main__":
    main()