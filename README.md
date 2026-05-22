# Daily arXiv - AI Research Tracker 📚🤖

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

每日自动追踪 arXiv 上最新的 AI 研究论文，使用 LLM 进行智能总结，支持基于 Zotero 库的个性化推荐。

## ✨ 核心功能

- 🔍 **智能爬取**: 每天自动从 arXiv 获取指定领域的最新论文
- 🤖 **AI 总结**: 使用 LLM 对论文进行智能总结（支持 OpenAI、Gemini、Claude、DeepSeek、vLLM）
- 📊 **趋势分析**: TF-IDF 关键词提取、词云可视化
- 🎯 **个性化推荐**: 基于你的 Zotero 论文库推荐相关论文
- 🖼️ **方法图提取**: 自动从 PDF 中提取方法图和架构图
- 🌐 **Web 界面**: 现代化响应式 Web 界面
- ⏰ **定时调度**: 支持每日自动执行

## 🚀 快速开始

### 前置要求

- Python 3.11+
- LLM API Key（推荐 SiliconFlow、DeepSeek 或 OpenAI）
- Zotero 账号（可选，用于个性化推荐）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/daily-arxiv.git
cd daily-arxiv
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 或使用 Conda
conda create -n daily-arxiv python=3.11 -y
conda activate daily-arxiv
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 5. 修改研究方向

编辑 `config/config.yaml`，设置你感兴趣的领域和关键词：

```yaml
arxiv:
  categories:
    - "cs.AI"  # 人工智能
    - "cs.LG"  # 机器学习
    - "cs.CV"  # 计算机视觉
    - "cs.CL"  # 自然语言处理
  
  keywords:
    - "large language model"
    - "LLM"
    - "vision language model"
    - "VLM"
```

### 6. 运行

```bash
# 运行完整流程
python main.py

# 启动 Web 界面
python src/web/app.py

# 启动定时调度
python scheduler.py
```

访问 http://localhost:5000 查看结果。

## ⚙️ 配置说明

### 环境变量 (.env)

| 变量 | 说明 | 必需 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI 或兼容 API 的 Key | 是 |
| `OPENAI_BASE_URL` | API Base URL（如使用 SiliconFlow） | 否 |
| `ZOTERO_USER_ID` | Zotero 用户 ID | 否 |
| `ZOTERO_API_KEY` | Zotero API Key | 否 |

### 配置文件 (config/config.yaml)

```yaml
# LLM 配置
llm:
  provider: "openai"  # openai, gemini, claude, deepseek, vllm
  openai:
    model: "Qwen/Qwen2.5-7B-Instruct"  # 或其他模型
    temperature: 0.8
    max_tokens: 2048

# 调度配置
scheduler:
  enabled: true
  run_time: "09:00"
  timezone: "Asia/Shanghai"
```

### 推荐的 LLM 提供商

| 提供商 | 模型 | 获取 API Key |
|--------|------|--------------|
| SiliconFlow | Qwen2.5-7B-Instruct | https://cloud.siliconflow.cn |
| DeepSeek | deepseek-chat | https://platform.deepseek.com |
| OpenAI | gpt-4o-mini | https://platform.openai.com |

## 📁 项目结构

```
daily-arxiv/
├── config/
│   └── config.yaml          # 主配置文件
├── src/
│   ├── crawler/
│   │   ├── arxiv_fetcher.py       # arXiv 论文爬取
│   │   ├── zotero_client.py       # Zotero API 客户端
│   │   ├── personalized_recommender.py  # 个性化推荐
│   │   └── figure_extractor.py    # PDF 图片提取
│   ├── summarizer/
│   │   ├── base_llm_client.py     # LLM 基类
│   │   ├── openai_client.py       # OpenAI 客户端
│   │   ├── claude_client.py       # Claude 客户端
│   │   ├── gemini_client.py       # Gemini 客户端
│   │   ├── deepseek_client.py     # DeepSeek 客户端
│   │   ├── vllm_client.py         # vLLM 客户端
│   │   ├── llm_factory.py         # LLM 工厂
│   │   └── paper_summarizer.py    # 论文总结器
│   ├── analyzer/
│   │   └── trend_analyzer.py      # 趋势分析
│   ├── web/
│   │   ├── app.py                 # Flask Web 应用
│   │   └── templates/
│   │       └── index.html         # Web 界面
│   └── utils.py                   # 工具函数
├── static/
│   └── js/
│       └── main.js               # 前端 JavaScript
├── data/                          # 数据存储（自动生成）
│   ├── papers/                    # 论文 JSON 数据
│   ├── summaries/                 # 总结 JSON 数据
│   ├── analysis/                  # 分析结果和词云
│   └── figures/                   # 提取的论文图片
├── logs/                          # 日志文件
├── main.py                        # 主程序入口
├── scheduler.py                   # APScheduler 调度器
├── requirements.txt               # Python 依赖
├── .env.example                   # 环境变量示例
└── .gitignore
```

## 🎯 个性化推荐

配置 Zotero 后，系统会：

1. 读取你的 Zotero 论文库
2. 提取你的研究兴趣关键词
3. 使用 TF-IDF 计算新论文与你已有论文的相似度
4. 按相关度排序推荐

## 🖼️ 方法图提取

点击论文详情时，系统会自动：
1. 下载论文 PDF
2. 提取其中的图片（过滤掉小图标）
3. 按大小排序展示（大图优先）

## 📝 常见问题

### Q: 如何获取 Zotero API Key？

访问 https://www.zotero.org/settings/keys ，创建一个新的 API Key。

### Q: 推荐使用哪个 LLM？

推荐使用 **SiliconFlow** 的 Qwen2.5-7B-Instruct，性价比高且中文支持好。

### Q: 如何修改执行时间？

编辑 `config/config.yaml`：

```yaml
scheduler:
  run_time: "10:30"  # 修改为你想要的时间
  timezone: "Asia/Shanghai"
```

### Q: 数据保存在哪里？

- 论文数据: `data/papers/`
- 总结数据: `data/summaries/`
- 分析结果: `data/analysis/`
- 论文图片: `data/figures/`
- 日志文件: `logs/`

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🙏 致谢

- [arxiv.py](https://github.com/lukasschwab/arxiv.py) - arXiv API 客户端
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 处理
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Bootstrap](https://getbootstrap.com/) - UI 框架