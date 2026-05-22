// Daily arXiv - 前端 JavaScript

// 全局变量
let currentDate = '';
let papers = [];
let summaries = [];

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    loadDates();
    loadSummaries();
    loadPapers();
    loadAnalysis();
    loadZoteroProfile();
});

// 加载可用日期
async function loadDates() {
    try {
        const response = await fetch('/api/dates');
        const data = await response.json();

        const selector = document.getElementById('dateSelector');
        selector.innerHTML = '<option value="">选择日期</option>';

        data.dates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            selector.appendChild(option);
        });

        // 选择第一个日期
        if (data.dates.length > 0) {
            selector.value = data.dates[0];
            currentDate = data.dates[0];
        }

        // 添加日期选择事件
        selector.addEventListener('change', function() {
            currentDate = this.value;
            loadPapers();
            loadAnalysis();
        });

    } catch (error) {
        console.error('加载日期失败:', error);
    }
}

// 加载论文列表
async function loadPapers() {
    try {
        const url = currentDate ? `/api/papers?date=${currentDate}` : '/api/papers';
        const response = await fetch(url);
        const data = await response.json();

        papers = data.papers || [];
        document.getElementById('paperCount').textContent = papers.length;

        renderPapers();

    } catch (error) {
        console.error('加载论文失败:', error);
        document.getElementById('papersList').innerHTML =
            '<div class="col-12"><p class="text-muted">暂无论文数据</p></div>';
    }
}

// 渲染论文列表
function renderPapers() {
    const container = document.getElementById('papersList');

    if (papers.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-muted">暂无论文数据</p></div>';
        return;
    }

    container.innerHTML = papers.map(paper => `
        <div class="col-md-6 mb-4">
            <div class="card card-paper h-100">
                <div class="card-body">
                    <h6 class="card-title">
                        <a href="#" onclick="showPaperDetail('${paper.id}'); return false;"
                           class="text-decoration-none">
                            ${paper.title}
                        </a>
                    </h6>
                    <div class="mb-2">
                        ${paper.categories.slice(0, 3).map(cat =>
                            `<span class="badge category-badge bg-secondary me-1">${cat}</span>`
                        ).join('')}
                    </div>
                    <p class="abstract-text">${paper.abstract.substring(0, 200)}...</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${paper.published.split(' ')[0]}</small>
                        <a href="${paper.pdf_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-file-pdf"></i> PDF
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// 显示论文详情
async function showPaperDetail(paperId) {
    try {
        const response = await fetch(`/api/paper/${encodeURIComponent(paperId)}`);
        const paper = await response.json();

        document.getElementById('paperModalTitle').textContent = paper.title;
        document.getElementById('paperPdfLink').href = paper.pdf_url;

        // 查找对应的总结
        const summary = summaries.find(s => s.paper_id === paperId);

        document.getElementById('paperModalBody').innerHTML = `
            <div class="mb-3">
                <strong>作者:</strong> ${paper.authors.join(', ')}
            </div>
            <div class="mb-3">
                <strong>发布日期:</strong> ${paper.published}
            </div>
            <div class="mb-3">
                <strong>类别:</strong>
                ${paper.categories.map(cat =>
                    `<span class="badge bg-secondary me-1">${cat}</span>`
                ).join('')}
            </div>
            <div class="mb-3">
                <strong>摘要:</strong>
                <p class="mt-2">${paper.abstract}</p>
            </div>
            ${summary ? `
                <div class="mb-3">
                    <strong>AI 总结:</strong>
                    <div class="alert alert-info mt-2">
                        ${summary.summary}
                    </div>
                </div>
            ` : ''}
            ${paper.comment ? `
                <div class="mb-3">
                    <strong>备注:</strong> ${paper.comment}
                </div>
            ` : ''}
            <div class="mb-3">
                <strong>方法图:</strong>
                <div id="figuresContainer" class="mt-2">
                    <div class="text-center">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <span class="ms-2 text-muted">正在提取论文图片...</span>
                    </div>
                </div>
            </div>
        `;

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('paperModal'));
        modal.show();

        // 异步加载图片
        loadPaperFigures(paperId, paper.pdf_url);

    } catch (error) {
        console.error('加载论文详情失败:', error);
    }
}

// 加载论文图片
async function loadPaperFigures(paperId, pdfUrl) {
    try {
        const response = await fetch(`/api/paper/figures?paper_id=${encodeURIComponent(paperId)}&pdf_url=${encodeURIComponent(pdfUrl)}`);
        const data = await response.json();

        const container = document.getElementById('figuresContainer');

        if (data.error || !data.figures || data.figures.length === 0) {
            container.innerHTML = '<p class="text-muted">未找到方法图</p>';
            return;
        }

        let html = '<div class="row">';
        data.figures.forEach((fig, index) => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <img src="${fig.url}" class="card-img-top" alt="Figure ${index + 1}" style="cursor: pointer;" onclick="showFullImage('${fig.url}')">
                        <div class="card-body p-2">
                            <small class="text-muted">图 ${index + 1} (第 ${fig.page} 页)</small>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;

    } catch (error) {
        console.error('加载图片失败:', error);
        document.getElementById('figuresContainer').innerHTML =
            '<p class="text-muted">图片加载失败</p>';
    }
}

// 显示大图
function showFullImage(url) {
    window.open(url, '_blank');
}

// 加载趋势分析
async function loadAnalysis() {
    try {
        const url = currentDate ? `/api/analysis?date=${currentDate.replace(/-/g, '')}` : '/api/analysis';
        const response = await fetch(url);
        const data = await response.json();

        // 渲染关键词
        renderKeywords(data.keywords || []);

        // 渲染类别
        renderCategories(data.categories || []);

        // 渲染词云
        if (data.wordcloud_path) {
            const img = document.getElementById('wordcloudImage');
            // 从完整路径中提取文件名
            const filename = data.wordcloud_path.split('\\').pop().split('/').pop();
            img.src = `/data/analysis/${filename}`;
            img.style.display = 'block';
            document.getElementById('wordcloudPlaceholder').style.display = 'none';
        }

    } catch (error) {
        console.error('加载分析失败:', error);
    }
}

// 渲染关键词
function renderKeywords(keywords) {
    const container = document.getElementById('keywordsContainer');

    if (keywords.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无关键词数据</p>';
        return;
    }

    container.innerHTML = keywords.slice(0, 10).map(kw =>
        `<span class="badge keyword-badge me-1 mb-1">${kw.keyword}</span>`
    ).join('');
}

// 渲染类别
function renderCategories(categories) {
    const container = document.getElementById('categoriesContainer');

    if (categories.length === 0) {
        container.innerHTML = '<p class="text-muted">暂无类别数据</p>';
        return;
    }

    container.innerHTML = categories.map(cat => `
        <div class="d-flex justify-content-between mb-1">
            <span>${cat.category}</span>
            <span class="badge bg-primary">${cat.count}</span>
        </div>
    `).join('');
}

// 加载总结
async function loadSummaries() {
    try {
        const url = currentDate ? `/api/summaries?date=${currentDate}` : '/api/summaries';
        const response = await fetch(url);
        const data = await response.json();

        summaries = data.summaries || [];

    } catch (error) {
        console.error('加载总结失败:', error);
    }
}

// 加载 Zotero 库信息
async function loadZoteroProfile() {
    try {
        const response = await fetch('/api/zotero/profile');
        const data = await response.json();

        const container = document.getElementById('zoteroProfile');

        if (data.error) {
            container.innerHTML = '<p class="text-muted">未配置 Zotero</p>';
            return;
        }

        let html = `
            <div class="mb-2">
                <strong>论文数量:</strong> ${data.total_papers}
            </div>
            <div class="mb-2">
                <strong>研究兴趣:</strong><br>
                ${data.top_keywords.slice(0, 8).map(kw =>
                    `<span class="badge bg-warning text-dark me-1 mb-1">${kw}</span>`
                ).join('')}
            </div>
            <div class="mb-2">
                <strong>最近收藏:</strong>
                <ul class="list-unstyled mt-1" style="font-size: 0.85rem;">
                    ${data.recent_papers.slice(0, 5).map(p =>
                        `<li class="mb-1">• ${p.title.substring(0, 40)}...</li>`
                    ).join('')}
                </ul>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        console.error('加载 Zotero 信息失败:', error);
        document.getElementById('zoteroProfile').innerHTML =
            '<p class="text-muted">加载失败</p>';
    }
}