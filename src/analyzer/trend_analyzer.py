"""
趋势分析模块
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_config = config.get('storage', {})
        self.data_dir = Path(self.storage_config.get('json_path', 'data/papers'))
        self.analysis_dir = Path('data/analysis')

        # 创建目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def analyze_trends(self, papers: List[Dict[str, Any]], summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析研究趋势"""
        logger.info("开始分析研究趋势...")

        analysis = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'paper_count': len(papers),
            'summary_count': len(summaries)
        }

        # 1. 关键词提取
        logger.info("提取关键词...")
        keywords = self._extract_keywords(papers)
        analysis['keywords'] = keywords

        # 2. 类别统计
        logger.info("统计研究类别...")
        categories = self._analyze_categories(papers)
        analysis['categories'] = categories

        # 3. 生成词云
        logger.info("生成词云...")
        wordcloud_path = self._generate_wordcloud(papers)
        analysis['wordcloud_path'] = str(wordcloud_path)

        # 4. 保存论文数据
        logger.info("保存论文数据...")
        self._save_papers(papers, summaries)

        # 5. 保存分析结果
        analysis_path = self.analysis_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        logger.info(f"趋势分析完成，结果保存到: {analysis_path}")

        return analysis

    def _extract_keywords(self, papers: List[Dict[str, Any]], top_n: int = 20) -> List[Dict[str, Any]]:
        """使用 TF-IDF 提取关键词"""
        try:
            # 合并所有摘要
            texts = [paper['abstract'] for paper in papers if paper.get('abstract')]

            if not texts:
                return []

            # 使用 TF-IDF 提取关键词
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()

            # 计算平均 TF-IDF 分数
            avg_tfidf = np.mean(tfidf_matrix.toarray(), axis=0)

            # 获取 top_n 关键词
            top_indices = avg_tfidf.argsort()[-top_n:][::-1]

            keywords = []
            for idx in top_indices:
                keywords.append({
                    'keyword': feature_names[idx],
                    'score': float(avg_tfidf[idx])
                })

            return keywords

        except Exception as e:
            logger.error(f"提取关键词时出现错误: {e}")
            return []

    def _analyze_categories(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析研究类别"""
        category_counter = Counter()

        for paper in papers:
            for cat in paper.get('categories', []):
                category_counter[cat] += 1

        categories = [
            {'category': cat, 'count': count}
            for cat, count in category_counter.most_common(10)
        ]

        return categories

    def _generate_wordcloud(self, papers: List[Dict[str, Any]]) -> Path:
        """生成词云图"""
        try:
            # 合并所有摘要
            text = ' '.join([paper['abstract'] for paper in papers if paper.get('abstract')])

            if not text:
                return None

            # 生成词云
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(text)

            # 保存词云图
            wordcloud_path = self.analysis_dir / f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Research Keywords Word Cloud')
            plt.savefig(wordcloud_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"词云图保存到: {wordcloud_path}")

            return wordcloud_path

        except Exception as e:
            logger.error(f"生成词云时出现错误: {e}")
            return None

    def _save_papers(self, papers: List[Dict[str, Any]], summaries: List[Dict[str, Any]]):
        """保存论文和总结数据"""
        today = datetime.now().strftime('%Y-%m-%d')

        # 保存论文数据
        papers_path = self.data_dir / f"papers_{today}.json"
        with open(papers_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

        # 保存总结数据
        summaries_dir = Path('data/summaries')
        summaries_dir.mkdir(parents=True, exist_ok=True)

        summaries_path = summaries_dir / f"summaries_{today}.json"
        with open(summaries_path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)

        logger.info(f"论文数据保存到: {papers_path}")
        logger.info(f"总结数据保存到: {summaries_path}")