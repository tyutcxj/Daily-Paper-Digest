"""
arXiv 论文爬取模块
"""

import logging
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ArxivFetcher:
    """arXiv 论文爬取器"""

    def __init__(self, config: Dict[str, Any]):
        self.categories = config.get('categories', ['cs.AI'])
        self.keywords = config.get('keywords', [])
        self.max_results = config.get('max_results', 20)
        self.sort_by = config.get('sort_by', 'submittedDate')
        self.sort_order = config.get('sort_order', 'descending')

    def fetch_papers(self) -> List[Dict[str, Any]]:
        """获取 arXiv 论文"""
        logger.info(f"开始获取 arXiv 论文...")
        logger.info(f"研究领域: {self.categories}")
        logger.info(f"关键词: {self.keywords}")
        logger.info(f"最大结果数: {self.max_results}")

        papers = []

        # 构建搜索查询
        query = self._build_query()
        logger.info(f"搜索查询: {query}")

        # 设置排序方式
        sort_criterion = arxiv.SortCriterion.SubmittedDate
        if self.sort_by == 'relevance':
            sort_criterion = arxiv.SortCriterion.Relevance

        sort_order = arxiv.SortOrder.Descending
        if self.sort_order == 'ascending':
            sort_order = arxiv.SortOrder.Ascending

        try:
            # 创建搜索客户端
            client = arxiv.Client()

            # 创建搜索请求
            search = arxiv.Search(
                query=query,
                max_results=self.max_results,
                sort_by=sort_criterion,
                sort_order=sort_order
            )

            # 执行搜索
            for result in client.results(search):
                paper = self._parse_paper(result)
                if paper:
                    papers.append(paper)

            logger.info(f"成功获取 {len(papers)} 篇论文")

        except Exception as e:
            logger.error(f"获取论文时出现错误: {e}")
            raise

        return papers

    def _build_query(self) -> str:
        """构建搜索查询"""
        # 构建类别查询
        category_query = " OR ".join([f"cat:{cat}" for cat in self.categories])

        # 如果有关键词，添加关键词过滤
        if self.keywords:
            keyword_query = " OR ".join([f'ti:"{kw}" OR abs:"{kw}"' for kw in self.keywords])
            query = f"({category_query}) AND ({keyword_query})"
        else:
            query = f"({category_query})"

        return query

    def _parse_paper(self, result) -> Dict[str, Any]:
        """解析论文信息"""
        try:
            paper = {
                'id': result.entry_id,
                'title': result.title,
                'authors': [str(author) for author in result.authors],
                'abstract': result.summary,
                'categories': result.categories,
                'published': result.published.strftime('%Y-%m-%d %H:%M:%S'),
                'updated': result.updated.strftime('%Y-%m-%d %H:%M:%S'),
                'pdf_url': result.pdf_url,
                'primary_category': result.primary_category,
                'comment': result.comment,
                'journal_ref': result.journal_ref,
                'doi': result.doi,
                'links': [str(link) for link in result.links]
            }
            return paper
        except Exception as e:
            logger.warning(f"解析论文时出现错误: {e}")
            return None

    def fetch_recent_papers(self, days=1) -> List[Dict[str, Any]]:
        """获取最近几天的论文"""
        logger.info(f"获取最近 {days} 天的论文...")

        papers = []

        # 构建搜索查询
        query = self._build_query()
        logger.info(f"搜索查询: {query}")

        try:
            client = arxiv.Client()

            search = arxiv.Search(
                query=query,
                max_results=self.max_results * 2,  # 获取更多结果以便过滤
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)

            for result in client.results(search):
                # 检查是否在指定天数内
                if result.published.replace(tzinfo=None) < cutoff_date:
                    continue

                paper = self._parse_paper(result)
                if paper:
                    papers.append(paper)

                    # 达到最大结果数时停止
                    if len(papers) >= self.max_results:
                        break

            logger.info(f"成功获取 {len(papers)} 篇最近 {days} 天的论文")

        except Exception as e:
            logger.error(f"获取论文时出现错误: {e}")
            raise

        return papers