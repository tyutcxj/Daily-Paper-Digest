"""
论文总结器
"""

import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .llm_factory import LLMFactory

logger = logging.getLogger(__name__)


class PaperSummarizer:
    """论文总结器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = LLMFactory.create_client(config)
        self.language = config.get('language', 'zh')
        self.max_workers = config.get('max_workers', 3)

    def summarize_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量总结论文"""
        logger.info(f"开始总结 {len(papers)} 篇论文...")
        summaries = []

        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_paper = {
                executor.submit(self._summarize_single, paper): paper
                for paper in papers
            }

            # 收集结果
            for future in as_completed(future_to_paper):
                paper = future_to_paper[future]
                try:
                    summary = future.result()
                    if summary:
                        summaries.append(summary)
                        logger.info(f"✓ 总结完成: {paper['title'][:50]}...")
                except Exception as e:
                    logger.error(f"✗ 总结失败: {paper['title'][:50]}... - {e}")

        logger.info(f"总结完成: {len(summaries)}/{len(papers)} 篇")
        return summaries

    def _summarize_single(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """总结单篇论文"""
        try:
            # 构建总结文本
            text = self._build_paper_text(paper)

            # 调用 LLM 进行总结
            summary_text = self.client.summarize(text, language=self.language)

            # 构建总结结果
            summary = {
                'paper_id': paper['id'],
                'title': paper['title'],
                'authors': paper['authors'],
                'categories': paper['categories'],
                'published': paper['published'],
                'pdf_url': paper['pdf_url'],
                'summary': summary_text,
                'language': self.language
            }

            return summary

        except Exception as e:
            logger.error(f"总结论文时出现错误: {e}")
            return None

    def _build_paper_text(self, paper: Dict[str, Any]) -> str:
        """构建论文文本"""
        text = f"标题: {paper['title']}\n\n"
        text += f"作者: {', '.join(paper['authors'][:5])}\n\n"
        text += f"摘要: {paper['abstract']}\n\n"

        if paper.get('comment'):
            text += f"备注: {paper['comment']}\n"

        return text

    def summarize_single_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """总结单篇论文（公开接口）"""
        return self._summarize_single(paper)