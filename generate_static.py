#!/usr/bin/env python3
"""
生成静态网页 - 用于 GitHub Pages 部署
"""

import json
import os
from pathlib import Path
from datetime import datetime


def load_json(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def generate_html(papers, summaries, analysis):
    """生成 HTML 页面"""

    # 构建总结映射
    summary_map = {}
    if summaries:
        for s in summaries:
            summary_map[s.get('paper_id')] = s.get('summary', '')

    # 构建论文卡片 HTML
    papers_html = ""
    modals_html = ""
    for i, paper in enumerate(papers):
        paper_id = paper.get('id', '')
        title = paper.get('title', '').replace('"', '&quot;').replace("'", "&#39;")
        authors = ', '.join(paper.get('authors', [])[:5])
        if len(paper.get('authors', [])) > 5:
            authors += ' et al.'
        all_authors = ', '.join(paper.get('authors', []))
        categories = ''.join([f'<span class="badge bg-secondary">{c}</span> ' for c in paper.get('categories', [])[:3]])
        abstract = paper.get('abstract', '')
        published = paper.get('published', '').split(' ')[0]
        pdf_url = paper.get('pdf_url', '#')
        arxiv_url = paper.get('id', '#')
        summary = summary_map.get(paper_id, '暂无总结')
        abstract_short = abstract[:200] + '...' if len(abstract) > 200 else abstract

        # 论文卡片
        papers_html += f'''
        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="#" onclick="showModal('modal-{i}'); return false;" class="text-decoration-none text-dark">
                            {title}
                        </a>
                    </h5>
                    <div class="mb-2">{categories}</div>
                    <p class="text-muted small mb-2">
                        <i class="bi bi-person"></i> {authors}<br>
                        <i class="bi bi-calendar"></i> {published}
                    </p>
                    <p class="card-text small">{abstract_short}</p>
                    <div class="alert alert-info py-2 mb-0" style="font-size: 0.85rem;">
                        <strong>AI 总结：</strong>{summary}
                    </div>
                </div>
                <div class="card-footer bg-transparent">
                    <a href="#" onclick="showModal('modal-{i}'); return false;" class="btn btn-sm btn-outline-primary me-1">
                        <i class="bi bi-info-circle"></i> 详情
                    </a>
                    <a href="{pdf_url}" target="_blank" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-file-pdf"></i> PDF
                    </a>
                </div>
            </div>
        </div>'''

        # 详情弹窗
        modals_html += f'''
        <div class="modal fade" id="modal-{i}" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">{title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>作者：</strong>{all_authors}</p>
                        <p><strong>发布日期：</strong>{published}</p>
                        <p><strong>类别：</strong>{categories}</p>
                        <hr>
                        <h6>摘要</h6>
                        <p>{abstract}</p>
                        <hr>
                        <div class="alert alert-info">
                            <h6><i class="bi bi-robot"></i> AI 总结</h6>
                            <p class="mb-0">{summary}</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <a href="{arxiv_url}" target="_blank" class="btn btn-outline-secondary">
                            <i class="bi bi-link-45deg"></i> arXiv 页面
                        </a>
                        <a href="{pdf_url}" target="_blank" class="btn btn-primary">
                            <i class="bi bi-file-pdf"></i> 查看 PDF
                        </a>
                    </div>
                </div>
            </div>
        </div>'''

    # 构建关键词 HTML
    keywords_html = ""
    if analysis and analysis.get('keywords'):
        for kw in analysis.get('keywords', [])[:15]:
            keywords_html += f'<span class="badge bg-info text-dark me-1 mb-1">{kw.get("keyword", "")}</span> '

    # 构建类别 HTML
    categories_html = ""
    if analysis and analysis.get('categories'):
        for cat in analysis.get('categories', [])[:10]:
            categories_html += f'''
            <div class="d-flex justify-content-between mb-1">
                <span>{cat.get("category", "")}</span>
                <span class="badge bg-primary">{cat.get("count", 0)}</span>
            </div>'''

    # 词云图片
    wordcloud_html = ""
    if analysis and analysis.get('wordcloud_path'):
        wordcloud_filename = analysis['wordcloud_path'].split('\\')[-1].split('/')[-1]
        wordcloud_html = f'<img src="data/analysis/{wordcloud_filename}" class="img-fluid" alt="词云">'

    # 生成日期
    today = datetime.now().strftime('%Y-%m-%d')

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily arXiv - AI Research Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: all 0.3s; }}
        .card-title a:hover {{ color: #0d6efd !important; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="bi bi-journal-richtext"></i> Daily arXiv - AI Research Tracker
            </a>
            <span class="navbar-text">
                <i class="bi bi-calendar"></i> 更新日期: {today}
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-8">
                <h4 class="mb-3">
                    <i class="bi bi-file-text"></i> 今日论文
                    <span class="badge bg-secondary">{len(papers)} 篇</span>
                </h4>
                <div class="row">
                    {papers_html}
                </div>
            </div>

            <div class="col-lg-4">
                <div class="card mb-4">
                    <div class="card-header bg-info text-white">
                        <i class="bi bi-tags"></i> 热门关键词
                    </div>
                    <div class="card-body">
                        {keywords_html if keywords_html else '<p class="text-muted">暂无数据</p>'}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-success text-white">
                        <i class="bi bi-bar-chart"></i> 研究类别
                    </div>
                    <div class="card-body">
                        {categories_html if categories_html else '<p class="text-muted">暂无数据</p>'}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header bg-warning text-dark">
                        <i class="bi bi-cloud"></i> 词云
                    </div>
                    <div class="card-body text-center">
                        {wordcloud_html if wordcloud_html else '<p class="text-muted">暂无数据</p>'}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 详情弹窗 -->
    {modals_html}

    <footer class="mt-5 py-3 bg-light text-center">
        <p class="text-muted mb-0">
            Powered by <a href="https://github.com/tyutcxj/Daily-Paper-Digest">Daily arXiv</a>
            | Data from <a href="https://arxiv.org">arXiv</a>
        </p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showModal(modalId) {{
            var modal = new bootstrap.Modal(document.getElementById(modalId));
            modal.show();
        }}
    </script>
</body>
</html>'''

    return html


def main():
    """主函数"""
    print("生成静态网页...")

    # 查找最新的数据文件
    data_dir = Path('data/papers')
    summaries_dir = Path('data/summaries')
    analysis_dir = Path('data/analysis')

    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')

    # 加载论文数据
    papers_file = data_dir / f'papers_{today}.json'
    if not papers_file.exists():
        # 尝试查找最新的文件
        papers_files = sorted(data_dir.glob('papers_*.json'), reverse=True)
        if papers_files:
            papers_file = papers_files[0]
        else:
            print("未找到论文数据")
            return

    papers = load_json(papers_file)
    if not papers:
        print("加载论文数据失败")
        return

    # 加载总结数据
    summaries_file = summaries_dir / f'summaries_{today}.json'
    if not summaries_file.exists():
        summaries_files = sorted(summaries_dir.glob('summaries_*.json'), reverse=True)
        if summaries_files:
            summaries_file = summaries_files[0]

    summaries = load_json(summaries_file) or []

    # 加载分析数据
    analysis_files = sorted(analysis_dir.glob('analysis_*.json'), reverse=True)
    analysis = load_json(analysis_files[0]) if analysis_files else None

    print(f"论文: {len(papers)} 篇")
    print(f"总结: {len(summaries)} 篇")

    # 生成 HTML
    html = generate_html(papers, summaries, analysis)

    # 保存到 docs 目录（GitHub Pages 默认目录）
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    # 复制数据文件到 docs
    docs_data_dir = docs_dir / 'data'
    docs_data_dir.mkdir(exist_ok=True)

    # 复制分析文件
    docs_analysis_dir = docs_data_dir / 'analysis'
    docs_analysis_dir.mkdir(exist_ok=True)

    # 复制词云图片
    if analysis and analysis.get('wordcloud_path'):
        wordcloud_path = Path(analysis['wordcloud_path'])
        if wordcloud_path.exists():
            import shutil
            shutil.copy(wordcloud_path, docs_analysis_dir / wordcloud_path.name)

    # 保存 HTML
    html_file = docs_dir / 'index.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"静态网页已生成: {html_file}")


if __name__ == '__main__':
    main()