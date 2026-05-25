"""
arXiv 论文爬取模块 - 使用 RSS feed 避免 API 限流
"""

import logging
import time
import feedparser
import requests
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
        """获取 arXiv 论文 - 使用 RSS feed"""
        logger.info(f"开始获取 arXiv 论文...")
        logger.info(f"研究领域: {self.categories}")
        logger.info(f"关键词: {self.keywords}")
        logger.info(f"最大结果数: {self.max_results}")

        papers = []

        try:
            # 为每个类别获取 RSS feed
            for category in self.categories:
                rss_url = f"https://rss.arxiv.org/rss/{category}"
                logger.info(f"获取 RSS feed: {rss_url}")

                feed = feedparser.parse(rss_url)

                if feed.bozo:
                    logger.warning(f"RSS feed 解析警告: {feed.bozo_exception}")

                for entry in feed.entries[:self.max_results]:
                    paper = self._parse_rss_entry(entry, category)
                    if paper:
                        # 如果有关键词，检查是否匹配
                        if self.keywords:
                            title_lower = paper.get('title', '').lower()
                            abstract_lower = paper.get('abstract', '').lower()
                            if any(kw.lower() in title_lower or kw.lower() in abstract_lower
                                   for kw in self.keywords):
                                papers.append(paper)
                        else:
                            papers.append(paper)

                # 添加延迟避免限流
                time.sleep(2)

            # 去重（基于 ID）
            seen_ids = set()
            unique_papers = []
            for paper in papers:
                if paper['id'] not in seen_ids:
                    seen_ids.add(paper['id'])
                    unique_papers.append(paper)

            papers = unique_papers[:self.max_results]

            # 如果 RSS 没有返回论文（可能是周末），使用备用方案
            if not papers:
                logger.info("RSS feed 没有返回论文（可能是周末），使用备用方案...")
                papers = self._fetch_from_export()

            logger.info(f"成功获取 {len(papers)} 篇论文")

        except Exception as e:
            logger.error(f"获取论文时出现错误: {e}")
            raise

        return papers

    def _fetch_from_export(self) -> List[Dict[str, Any]]:
        """从 arXiv export API 获取论文（带重试和延迟）"""
        papers = []

        for category in self.categories:
            try:
                # 使用 export API
                url = f"https://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&start=0&max_results={self.max_results}"
                logger.info(f"从 export API 获取: {url}")

                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)

                    ns = {'atom': 'http://www.w3.org/2005/Atom',
                          'arxiv': 'http://arxiv.org/schemas/atom'}

                    for entry in root.findall('atom:entry', ns):
                        paper = self._parse_atom_entry(entry, ns, category)
                        if paper:
                            # 关键词过滤
                            if self.keywords:
                                title_lower = paper.get('title', '').lower()
                                abstract_lower = paper.get('abstract', '').lower()
                                if any(kw.lower() in title_lower or kw.lower() in abstract_lower
                                       for kw in self.keywords):
                                    papers.append(paper)
                            else:
                                papers.append(paper)

                # 长延迟避免限流
                time.sleep(10)

            except Exception as e:
                logger.warning(f"从 export API 获取 {category} 失败: {e}")
                continue

        return papers[:self.max_results]

    def _parse_atom_entry(self, entry, ns: dict, category: str) -> Dict[str, Any]:
        """解析 Atom 条目"""
        try:
            # 提取基本信息
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            link = entry.find('atom:id', ns).text

            # 提取作者
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)

            # 提取 PDF 链接
            pdf_url = ''
            for link_elem in entry.findall('atom:link', ns):
                if link_elem.get('title') == 'pdf':
                    pdf_url = link_elem.get('href', '')
                    break

            if not pdf_url:
                arxiv_id = link.split('/')[-1]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

            # 提取日期
            published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ''
            updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else published

            paper = {
                'id': link,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'categories': [category],
                'published': published,
                'updated': updated,
                'pdf_url': pdf_url,
                'primary_category': category,
                'comment': '',
                'journal_ref': None,
                'doi': None,
                'links': [link]
            }
            return paper
        except Exception as e:
            logger.warning(f"解析 Atom 条目失败: {e}")
            return None

    def _parse_rss_entry(self, entry, category: str) -> Dict[str, Any]:
        """解析 RSS 条目"""
        try:
            # 提取 arXiv ID
            link = entry.get('link', '')
            paper_id = link.replace('http://', 'https://').rstrip('/')

            # 提取标题（去除多余空白）
            title = entry.get('title', '').replace('\n', ' ').strip()
            if title.startswith('arXiv:'):
                title = title.split(':', 1)[1].strip()

            # 提取作者
            authors = []
            if hasattr(entry, 'authors'):
                authors = [a.get('name', '') for a in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]

            # 提取摘要
            abstract = entry.get('summary', '').strip()
            # 清理 HTML 标签
            import re
            abstract = re.sub(r'<[^>]+>', '', abstract)

            # 提取 PDF 链接
            pdf_url = ''
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if link.get('type') == 'application/pdf':
                        pdf_url = link.get('href', '')
                        break

            if not pdf_url:
                # 构造 PDF URL
                arxiv_id = paper_id.split('/')[-1]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"

            paper = {
                'id': paper_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'categories': [category],
                'published': entry.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'updated': entry.get('updated', entry.get('published', '')),
                'pdf_url': pdf_url,
                'primary_category': category,
                'comment': entry.get('arxiv_comment', ''),
                'journal_ref': None,
                'doi': None,
                'links': [link]
            }
            return paper
        except Exception as e:
            logger.warning(f"解析 RSS 条目时出现错误: {e}")
            return None

    def fetch_recent_papers(self, days=1) -> List[Dict[str, Any]]:
        """获取最近几天的论文"""
        return self.fetch_papers()