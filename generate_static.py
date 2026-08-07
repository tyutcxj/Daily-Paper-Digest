#!/usr/bin/env python3
"""
生成静态网页 - 用于 GitHub Pages 部署
支持多天历史数据
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


def load_json(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def generate_html(papers, summaries, analysis, today=None, all_dates=None, is_daily_page=False):
    """生成 HTML 页面"""

    if today is None:
        today = datetime.now().strftime('%Y-%m-%d')

    # 根据页面位置确定路径前缀
    daily_prefix = "" if is_daily_page else "daily/"
    index_href = "../index.html" if is_daily_page else "index.html"

    # 构建日期选择器 HTML
    date_selector_html = ""
    if all_dates and len(all_dates) > 1:
        options = ""
        for d in all_dates:
            selected = 'selected' if d['date'] == today else ''
            options += f'<option value="{daily_prefix}{d["date"]}.html" {selected}>{d["date"]} ({d["count"]}篇)</option>'
        date_selector_html = f'''
        <select class="form-select form-select-sm date-selector" onchange="if(this.value) window.location.href=this.value">
            {options}
        </select>'''
    else:
        date_selector_html = f'<span class="navbar-text text-white"><i class="bi bi-calendar"></i> {today}</span>'

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

        # 计算相似度星级 (0-5星)
        relevance_score = paper.get('relevance_score', 0)
        if relevance_score >= 0.5:
            stars = 5
            star_color = "text-success"
        elif relevance_score >= 0.4:
            stars = 4
            star_color = "text-success"
        elif relevance_score >= 0.3:
            stars = 3
            star_color = "text-warning"
        elif relevance_score >= 0.2:
            stars = 2
            star_color = "text-warning"
        elif relevance_score >= 0.1:
            stars = 1
            star_color = "text-secondary"
        else:
            stars = 0
            star_color = "text-muted"

        stars_html = f'<span class="{star_color}">{"★" * stars}{"☆" * (5 - stars)}</span>'
        score_text = f'<small class="text-muted">({relevance_score:.2f})</small>' if relevance_score > 0 else ''

        # 论文卡片
        papers_html += f'''
        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0 flex-grow-1">
                            <a href="#" onclick="showModal('modal-{i}'); return false;" class="text-decoration-none text-dark">
                                {title}
                            </a>
                        </h5>
                        <div class="ms-2 text-nowrap" title="相关度: {relevance_score:.2f}">
                            {stars_html} {score_text}
                        </div>
                    </div>
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
                        <div class="mb-3">
                            <span class="badge bg-primary me-2">相关度 {stars_html} {score_text}</span>
                        </div>
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
        .date-selector {{
            min-width: 200px;
            background-color: rgba(255,255,255,0.9) !important;
            color: #333 !important;
            border: 1px solid rgba(255,255,255,0.5);
            font-weight: 500;
        }}
        .date-selector:focus {{
            background-color: white !important;
            box-shadow: 0 0 0 0.2rem rgba(255,255,255,0.5);
        }}
        .date-selector option {{
            color: #333;
            background-color: white;
            padding: 8px;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{index_href}">
                <i class="bi bi-journal-richtext"></i> Daily arXiv
            </a>
            <div class="d-flex align-items-center">
                {date_selector_html}
            </div>
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


def generate_history_html(all_dates):
    """生成历史记录页面"""

    dates_html = ""
    for date_info in all_dates:
        dates_html += f'''
        <div class="col-md-4 mb-3">
            <div class="card">
                <div class="card-body text-center">
                    <h5><i class="bi bi-calendar3"></i> {date_info["date"]}</h5>
                    <p class="text-muted">{date_info["count"]} 篇论文</p>
                    <a href="daily/{date_info["date"]}.html" class="btn btn-primary btn-sm">
                        <i class="bi bi-eye"></i> 查看
                    </a>
                </div>
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily arXiv - 历史记录</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.html">
                <i class="bi bi-journal-richtext"></i> Daily arXiv - AI Research Tracker
            </a>
            <a href="index.html" class="btn btn-outline-light btn-sm">
                <i class="bi bi-arrow-left"></i> 返回最新
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <h4 class="mb-4"><i class="bi bi-calendar-week"></i> 历史记录</h4>
        <div class="row">
            {dates_html}
        </div>
    </div>

    <footer class="mt-5 py-3 bg-light text-center">
        <p class="text-muted mb-0">
            Powered by <a href="https://github.com/tyutcxj/Daily-Paper-Digest">Daily arXiv</a>
        </p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

    return html


def main():
    """主函数"""
    print("生成静态网页...")

    # 数据目录
    data_dir = Path('data/papers')
    summaries_dir = Path('data/summaries')
    analysis_dir = Path('data/analysis')

    # docs 目录
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    docs_daily_dir = docs_dir / 'daily'
    docs_daily_dir.mkdir(exist_ok=True)
    docs_data_dir = docs_dir / 'data'
    docs_data_dir.mkdir(exist_ok=True)
    docs_analysis_dir = docs_data_dir / 'analysis'
    docs_analysis_dir.mkdir(exist_ok=True)

    # 获取所有可用的日期
    papers_files = sorted(data_dir.glob('papers_*.json'), reverse=True)
    all_dates = []

    for papers_file in papers_files:
        date_str = papers_file.stem.replace('papers_', '')
        papers = load_json(papers_file)
        if papers:
            all_dates.append({
                'date': date_str,
                'count': len(papers)
            })

    if not all_dates:
        print("未找到论文数据")
        return

    # 生成每日页面
    for date_info in all_dates:
        date_str = date_info['date']
        papers = load_json(data_dir / f'papers_{date_str}.json')
        summaries = load_json(summaries_dir / f'summaries_{date_str}.json') or []

        analysis = None
        for analysis_file in analysis_dir.glob(f'analysis_{date_str.replace("-", "")}*.json'):
            analysis = load_json(analysis_file)
            if analysis:
                break

        print(f"日期: {date_str}, 论文: {len(papers)} 篇, 总结: {len(summaries)} 篇")

        # 生成每日页面
        html = generate_html(papers, summaries, analysis, today=date_str, all_dates=all_dates, is_daily_page=True)
        daily_file = docs_daily_dir / f'{date_str}.html'
        with open(daily_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # 复制该日期的词云图片
        if analysis and analysis.get('wordcloud_path'):
            wordcloud_path = Path(analysis['wordcloud_path'])
            if wordcloud_path.exists():
                import shutil
                shutil.copy(wordcloud_path, docs_analysis_dir / wordcloud_path.name)

    # 生成主页（显示最新一天）
    latest_date = all_dates[0]
    latest_papers = load_json(data_dir / f'papers_{latest_date["date"]}.json')
    latest_summaries = load_json(summaries_dir / f'summaries_{latest_date["date"]}.json') or []

    latest_analysis = None
    for analysis_file in sorted(analysis_dir.glob('analysis_*.json'), reverse=True):
        latest_analysis = load_json(analysis_file)
        if latest_analysis:
            break

    # 生成主页
    index_html = generate_html(latest_papers, latest_summaries, latest_analysis, today=latest_date['date'], all_dates=all_dates)

    with open(docs_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

    # 生成历史记录页面
    history_html = generate_history_html(all_dates)
    with open(docs_dir / 'history.html', 'w', encoding='utf-8') as f:
        f.write(history_html)

    print(f"生成完成！共 {len(all_dates)} 天的数据")
    print(f"- 主页: docs/index.html")
    print(f"- 历史: docs/history.html")
    print(f"- 每日: docs/daily/*.html")


if __name__ == '__main__':
    main()