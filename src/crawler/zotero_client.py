"""
Zotero API 客户端 - 用于获取用户论文库
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class ZoteroClient:
    """Zotero API 客户端"""

    BASE_URL = "https://api.zotero.org"

    def __init__(self, user_id: str, api_key: str):
        self.user_id = user_id
        self.api_key = api_key
        self.headers = {
            "Zotero-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_recent_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近添加的论文"""
        url = f"{self.BASE_URL}/users/{self.user_id}/items"
        params = {
            "limit": limit,
            "sort": "dateAdded",
            "direction": "desc",
            "itemType": "-attachment || note"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json()

            papers = []
            for item in items:
                data = item.get("data", {})
                paper = {
                    "id": data.get("key"),
                    "title": data.get("title", ""),
                    "authors": self._extract_authors(data.get("creators", [])),
                    "abstract": data.get("abstractNote", ""),
                    "year": data.get("date", "")[:4],
                    "doi": data.get("DOI", ""),
                    "url": data.get("url", ""),
                    "tags": [t.get("tag") for t in data.get("tags", [])],
                    "publication": data.get("publicationTitle", "") or data.get("proceedingsTitle", ""),
                    "type": data.get("itemType"),
                    "date_added": data.get("dateAdded", "")
                }
                papers.append(paper)

            logger.info(f"从 Zotero 获取了 {len(papers)} 篇论文")
            return papers

        except Exception as e:
            logger.error(f"获取 Zotero 论文失败: {e}")
            return []

    def get_all_items(self, limit: int = 500) -> List[Dict[str, Any]]:
        """获取所有论文（分页）"""
        all_papers = []
        start = 0
        batch_size = 100

        while start < limit:
            url = f"{self.BASE_URL}/users/{self.user_id}/items"
            params = {
                "limit": batch_size,
                "start": start,
                "sort": "dateAdded",
                "direction": "desc",
                "itemType": "-attachment || note"
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                items = response.json()

                if not items:
                    break

                for item in items:
                    data = item.get("data", {})
                    paper = {
                        "id": data.get("key"),
                        "title": data.get("title", ""),
                        "authors": self._extract_authors(data.get("creators", [])),
                        "abstract": data.get("abstractNote", ""),
                        "year": data.get("date", "")[:4],
                        "doi": data.get("DOI", ""),
                        "url": data.get("url", ""),
                        "tags": [t.get("tag") for t in data.get("tags", [])],
                        "publication": data.get("publicationTitle", "") or data.get("proceedingsTitle", ""),
                        "type": data.get("itemType"),
                        "date_added": data.get("dateAdded", "")
                    }
                    all_papers.append(paper)

                start += batch_size

            except Exception as e:
                logger.error(f"获取 Zotero 论文失败: {e}")
                break

        logger.info(f"从 Zotero 获取了 {len(all_papers)} 篇论文")
        return all_papers

    def get_collections(self) -> List[Dict[str, Any]]:
        """获取所有收藏夹"""
        url = f"{self.BASE_URL}/users/{self.user_id}/collections"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            collections = response.json()

            return [
                {
                    "key": c.get("data", {}).get("key"),
                    "name": c.get("data", {}).get("name"),
                    "parent": c.get("data", {}).get("parentCollection")
                }
                for c in collections
            ]

        except Exception as e:
            logger.error(f"获取 Zotero 收藏夹失败: {e}")
            return []

    def get_collection_items(self, collection_key: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取特定收藏夹中的论文"""
        url = f"{self.BASE_URL}/users/{self.user_id}/collections/{collection_key}/items"
        params = {
            "limit": limit,
            "itemType": "-attachment || note"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json()

            papers = []
            for item in items:
                data = item.get("data", {})
                paper = {
                    "id": data.get("key"),
                    "title": data.get("title", ""),
                    "authors": self._extract_authors(data.get("creators", [])),
                    "abstract": data.get("abstractNote", ""),
                    "year": data.get("date", "")[:4],
                    "doi": data.get("DOI", ""),
                    "url": data.get("url", ""),
                    "tags": [t.get("tag") for t in data.get("tags", [])],
                    "publication": data.get("publicationTitle", "") or data.get("proceedingsTitle", ""),
                    "type": data.get("itemType"),
                    "date_added": data.get("dateAdded", "")
                }
                papers.append(paper)

            logger.info(f"从收藏夹获取了 {len(papers)} 篇论文")
            return papers

        except Exception as e:
            logger.error(f"获取收藏夹论文失败: {e}")
            return []

    def _extract_authors(self, creators: List[Dict]) -> List[str]:
        """提取作者列表"""
        authors = []
        for creator in creators:
            if creator.get("creatorType") == "author":
                name = ""
                if creator.get("name"):
                    name = creator["name"]
                elif creator.get("lastName"):
                    name = creator["lastName"]
                    if creator.get("firstName"):
                        name = f"{creator['firstName']} {name}"
                if name:
                    authors.append(name)
        return authors

    def extract_research_interests(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """从用户论文库提取研究兴趣"""
        # 提取关键词
        all_keywords = []
        for paper in papers:
            # 从标题提取
            title_words = paper["title"].lower().split()
            all_keywords.extend([w for w in title_words if len(w) > 3])

            # 从标签提取
            all_keywords.extend([t.lower() for t in paper.get("tags", [])])

            # 从摘要提取关键短语
            abstract = paper.get("abstract", "").lower()
            if abstract:
                # 简单的关键词提取
                keywords = self._extract_keywords_from_text(abstract)
                all_keywords.extend(keywords)

        # 统计词频
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, count in keyword_counts.most_common(50) if count >= 2]

        # 提取研究领域
        publications = Counter()
        for paper in papers:
            pub = paper.get("publication", "")
            if pub:
                publications[pub.lower()] += 1

        return {
            "top_keywords": top_keywords,
            "keyword_counts": dict(keyword_counts.most_common(100)),
            "publications": dict(publications.most_common(20)),
            "total_papers": len(papers),
            "recent_papers": [
                {
                    "title": p["title"],
                    "abstract": p["abstract"][:200],
                    "tags": p["tags"]
                }
                for p in papers[:20]
            ]
        }

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 常见的 AI/ML 关键词
        ai_keywords = [
            "transformer", "attention", "neural", "network", "learning",
            "deep", "machine", "reinforcement", "generative", "adversarial",
            "diffusion", "language", "model", "vision", "multimodal",
            "llm", "vlm", "bert", "gpt", "clip", "sam", "segmentation",
            "detection", "classification", "generation", "translation",
            "reasoning", "agent", "rag", "retrieval", "augmented",
            "fine-tuning", "prompt", "embedding", "encoder", "decoder"
        ]

        found_keywords = []
        for kw in ai_keywords:
            if kw in text:
                found_keywords.append(kw)

        return found_keywords