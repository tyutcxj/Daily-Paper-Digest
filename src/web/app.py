#!/usr/bin/env python3
"""
Daily arXiv - Web 应用
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

from src.utils import load_config, setup_logging
from src.crawler.figure_extractor import FigureExtractor

# 配置模板和静态文件目录
template_dir = Path(__file__).parent / 'templates'
static_dir = project_root / 'static'

app = Flask(__name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir))
CORS(app)

# 加载配置
config = load_config()
setup_logging(config.get('logging', {}))
logger = logging.getLogger(__name__)

# 数据目录
data_dir = Path(config.get('storage', {}).get('json_path', 'data/papers'))
summaries_dir = Path('data/summaries')
analysis_dir = Path('data/analysis')


@app.route('/')
def index():
    """首页"""
    return render_template('index.html',
                         title=config.get('web', {}).get('title', 'Daily arXiv'),
                         description=config.get('web', {}).get('description', ''))


@app.route('/data/analysis/<path:filename>')
def serve_analysis_file(filename):
    """提供分析文件（如词云图片）"""
    # 使用绝对路径
    abs_analysis_dir = project_root / 'data' / 'analysis'
    return send_from_directory(str(abs_analysis_dir), filename)


@app.route('/data/figures/<path:filename>')
def serve_figure_file(filename):
    """提供论文图片"""
    figures_dir = project_root / 'data' / 'figures'
    return send_from_directory(str(figures_dir), filename)


@app.route('/api/papers')
def get_papers():
    """获取论文列表"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        papers_file = data_dir / f"papers_{date}.json"

        if not papers_file.exists():
            return jsonify({'error': 'No papers found for this date'}), 404

        with open(papers_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)

        return jsonify({
            'date': date,
            'count': len(papers),
            'papers': papers
        })

    except Exception as e:
        logger.error(f"获取论文失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/summaries')
def get_summaries():
    """获取论文总结"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        summaries_file = summaries_dir / f"summaries_{date}.json"

        if not summaries_file.exists():
            return jsonify({'error': 'No summaries found for this date'}), 404

        with open(summaries_file, 'r', encoding='utf-8') as f:
            summaries = json.load(f)

        return jsonify({
            'date': date,
            'count': len(summaries),
            'summaries': summaries
        })

    except Exception as e:
        logger.error(f"获取总结失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis')
def get_analysis():
    """获取趋势分析"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y%m%d'))

        # 查找最新的分析文件
        analysis_files = sorted(analysis_dir.glob(f"analysis_{date}*.json"), reverse=True)

        if not analysis_files:
            return jsonify({'error': 'No analysis found for this date'}), 404

        with open(analysis_files[0], 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        return jsonify(analysis)

    except Exception as e:
        logger.error(f"获取分析失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dates')
def get_dates():
    """获取可用日期列表"""
    try:
        dates = set()

        # 从论文文件获取日期
        for file in data_dir.glob('papers_*.json'):
            date_str = file.stem.replace('papers_', '')
            dates.add(date_str)

        # 从总结文件获取日期
        for file in summaries_dir.glob('summaries_*.json'):
            date_str = file.stem.replace('summaries_', '')
            dates.add(date_str)

        return jsonify({
            'dates': sorted(dates, reverse=True)
        })

    except Exception as e:
        logger.error(f"获取日期列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/paper/<path:paper_id>')
def get_paper(paper_id):
    """获取单篇论文详情"""
    try:
        # 查找所有论文文件
        for papers_file in sorted(data_dir.glob('papers_*.json'), reverse=True):
            with open(papers_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)

            for paper in papers:
                if paper['id'] == paper_id:
                    return jsonify(paper)

        return jsonify({'error': 'Paper not found'}), 404

    except Exception as e:
        logger.error(f"获取论文详情失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/zotero/profile')
def get_zotero_profile():
    """获取用户 Zotero 库信息"""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        zotero_user_id = os.getenv('ZOTERO_USER_ID')
        zotero_api_key = os.getenv('ZOTERO_API_KEY')

        if not zotero_user_id or not zotero_api_key:
            return jsonify({'error': 'Zotero not configured'}), 400

        from src.crawler.zotero_client import ZoteroClient
        zotero = ZoteroClient(zotero_user_id, zotero_api_key)

        # 获取最近的论文
        recent_papers = zotero.get_recent_items(limit=20)

        # 提取研究兴趣
        interests = zotero.extract_research_interests(recent_papers)

        return jsonify({
            'user_id': zotero_user_id,
            'total_papers': interests['total_papers'],
            'top_keywords': interests['top_keywords'][:15],
            'recent_papers': [
                {
                    'title': p['title'],
                    'tags': p['tags'][:3]
                }
                for p in recent_papers[:10]
            ]
        })

    except Exception as e:
        logger.error(f"获取 Zotero 信息失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/paper/figures')
def get_paper_figures():
    """获取论文图片"""
    try:
        pdf_url = request.args.get('pdf_url')
        paper_id = request.args.get('paper_id')

        if not pdf_url or not paper_id:
            return jsonify({'error': 'Missing pdf_url or paper_id'}), 400

        # 初始化图片提取器
        figures_dir = str(project_root / 'data' / 'figures')
        extractor = FigureExtractor(figures_dir)

        # 提取图片
        figures = extractor.extract_method_figures(pdf_url, paper_id)

        return jsonify({
            'paper_id': paper_id,
            'figures': figures,
            'count': len(figures)
        })

    except Exception as e:
        logger.error(f"获取论文图片失败: {e}")
        return jsonify({'error': str(e)}), 500


def run_web():
    """运行 Web 应用"""
    web_config = config.get('web', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', True)

    logger.info(f"启动 Web 应用: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web()