"""
论文图片提取器 - 从 arXiv PDF 中提取方法图
"""

import os
import io
import logging
import requests
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)


class FigureExtractor:
    """从 PDF 中提取图片"""

    def __init__(self, output_dir: str = "data/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_figures_from_url(self, pdf_url: str, paper_id: str, max_figures: int = 5) -> List[Dict[str, Any]]:
        """从 PDF URL 提取图片"""
        try:
            # 生成唯一的文件名前缀
            prefix = paper_id.split('/')[-1].replace('v', '_')

            # 检查是否已经提取过
            existing_figures = list(self.output_dir.glob(f"{prefix}_*.png"))
            if existing_figures:
                logger.info(f"已存在 {len(existing_figures)} 张图片，跳过提取")
                return [
                    {
                        "path": str(f),
                        "filename": f.name,
                        "url": f"/data/figures/{f.name}"
                    }
                    for f in sorted(existing_figures)[:max_figures]
                ]

            # 下载 PDF
            logger.info(f"下载 PDF: {pdf_url}")
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()

            # 打开 PDF
            pdf_bytes = io.BytesIO(response.content)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            figures = []
            figure_count = 0

            # 遍历每一页
            for page_num in range(min(len(doc), 15)):  # 只检查前15页
                page = doc[page_num]

                # 获取页面中的图片
                image_list = page.get_images(full=True)

                for img_idx, img in enumerate(image_list):
                    if figure_count >= max_figures:
                        break

                    try:
                        # 提取图片
                        xref = img[0]
                        base_image = doc.extract_image(xref)

                        if base_image:
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]

                            # 过滤太小的图片（可能是图标或装饰）
                            if base_image.get("width", 0) < 100 or base_image.get("height", 0) < 100:
                                continue

                            # 转换为 PNG
                            pil_image = Image.open(io.BytesIO(image_bytes))

                            # 过滤太小的图片
                            if pil_image.width < 150 or pil_image.height < 150:
                                continue

                            # 保存图片
                            filename = f"{prefix}_p{page_num+1}_fig{figure_count+1}.png"
                            filepath = self.output_dir / filename

                            pil_image.save(str(filepath), "PNG")

                            figures.append({
                                "path": str(filepath),
                                "filename": filename,
                                "url": f"/data/figures/{filename}",
                                "page": page_num + 1,
                                "width": pil_image.width,
                                "height": pil_image.height
                            })

                            figure_count += 1
                            logger.info(f"提取图片: {filename}")

                    except Exception as e:
                        logger.warning(f"提取图片失败: {e}")
                        continue

                if figure_count >= max_figures:
                    break

            doc.close()
            logger.info(f"共提取 {len(figures)} 张图片")
            return figures

        except Exception as e:
            logger.error(f"提取图片失败: {e}")
            return []

    def extract_method_figures(self, pdf_url: str, paper_id: str) -> List[Dict[str, Any]]:
        """提取方法图（通常是前几张大图）"""
        figures = self.extract_figures_from_url(pdf_url, paper_id, max_figures=8)

        # 按大小排序，优先返回大图（通常是方法图或架构图）
        figures.sort(key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)

        return figures[:5]  # 返回前5张最大的图

    def get_figure_path(self, filename: str) -> Optional[str]:
        """获取图片路径"""
        filepath = self.output_dir / filename
        if filepath.exists():
            return str(filepath)
        return None