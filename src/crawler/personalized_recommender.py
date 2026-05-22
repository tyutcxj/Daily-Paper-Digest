"""
个性化论文推荐器 - 基于用户 Zotero 库推荐相关论文
"""

import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class PersonalizedRecommender:
    """个性化论文推荐器"""

    def __init__(self, zotero_client):
        self.zotero = zotero_client
        self.user_interests = None
        self.user_papers = None
        self.vectorizer = None
        self.user_vectors = None

    def load_user_profile(self, max_papers: int = 200):
        """加载用户论文库并构建兴趣模型"""
        logger.info("加载用户 Zotero 论文库...")

        # 获取用户论文
        self.user_papers = self.zotero.get_all_items(limit=max_papers)

        if not self.user_papers:
            logger.warning("未能获取用户论文库")
            return False

        # 提取研究兴趣
        self.user_interests = self.zotero.extract_research_interests(self.user_papers)

        logger.info(f"用户论文库: {self.user_interests['total_papers']} 篇")
        logger.info(f"Top 关键词: {self.user_interests['top_keywords'][:10]}")

        # 构建用户论文向量
        self._build_user_vectors()

        return True

    def _build_user_vectors(self):
        """构建用户论文的 TF-IDF 向量"""
        if not self.user_papers:
            return

        # 合并标题和摘要作为文档
        documents = []
        for paper in self.user_papers:
            doc = f"{paper['title']} {paper['abstract']} {' '.join(paper['tags'])}"
            documents.append(doc)

        # 创建 TF-IDF 向量
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        self.user_vectors = self.vectorizer.fit_transform(documents)
        logger.info(f"构建用户向量: {self.user_vectors.shape}")

    def rank_papers(self, papers: List[Dict[str, Any]], top_n: int = 20) -> List[Dict[str, Any]]:
        """根据用户兴趣对论文进行排序"""
        if not self.user_papers or not self.vectorizer:
            logger.warning("用户资料未加载，返回原始论文")
            return papers[:top_n]

        # 构建候选论文的向量
        candidate_docs = []
        for paper in papers:
            doc = f"{paper['title']} {paper['abstract']}"
            candidate_docs.append(doc)

        candidate_vectors = self.vectorizer.transform(candidate_docs)

        # 计算与用户论文的相似度
        # 使用平均相似度作为匹配分数
        similarities = cosine_similarity(candidate_vectors, self.user_vectors)

        # 计算每篇候选论文与用户库的最大相似度和平均相似度
        max_similarities = np.max(similarities, axis=1)
        mean_similarities = np.mean(similarities, axis=1)

        # 综合分数：最大相似度 * 0.7 + 平均相似度 * 0.3
        scores = max_similarities * 0.7 + mean_similarities * 0.3

        # 添加分数到论文
        for i, paper in enumerate(papers):
            paper['relevance_score'] = float(scores[i])
            paper['max_similarity'] = float(max_similarities[i])

        # 按分数排序
        ranked_papers = sorted(papers, key=lambda x: x['relevance_score'], reverse=True)

        # 过滤低分论文（可选）
        min_score = 0.1
        filtered_papers = [p for p in ranked_papers if p['relevance_score'] >= min_score]

        logger.info(f"推荐排序完成: {len(filtered_papers)}/{len(papers)} 篇论文通过过滤")

        return filtered_papers[:top_n]

    def get_recommendation_summary(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取推荐摘要"""
        if not self.user_interests:
            return {}

        scores = [p.get('relevance_score', 0) for p in papers]

        return {
            "user_papers_count": self.user_interests['total_papers'],
            "user_top_keywords": self.user_interests['top_keywords'][:15],
            "recommended_count": len(papers),
            "avg_relevance_score": np.mean(scores) if scores else 0,
            "max_relevance_score": np.max(scores) if scores else 0,
            "min_relevance_score": np.min(scores) if scores else 0
        }

    def find_similar_to_paper(self, paper: Dict[str, Any], top_n: int = 5) -> List[Dict[str, Any]]:
        """查找与指定论文相似的用户已有论文"""
        if not self.user_papers or not self.vectorizer:
            return []

        # 构建查询向量
        query_doc = f"{paper['title']} {paper['abstract']}"
        query_vector = self.vectorizer.transform([query_doc])

        # 计算相似度
        similarities = cosine_similarity(query_vector, self.user_vectors)[0]

        # 获取最相似的论文
        top_indices = np.argsort(similarities)[::-1][:top_n]

        similar_papers = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # 相似度阈值
                user_paper = self.user_papers[idx].copy()
                user_paper['similarity'] = float(similarities[idx])
                similar_papers.append(user_paper)

        return similar_papers