# Daily arXiv - AI Research Tracker 📚🤖

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automatically track the latest AI research papers on arXiv daily, use LLMs for intelligent summarization, and support personalized recommendations based on your Zotero library.

**[中文文档](README.md)** | English

## ✨ Features

- 🔍 **Smart Fetching**: Automatically fetch latest papers from arXiv in specified fields
- 🤖 **AI Summarization**: Use LLMs to summarize papers (supports OpenAI, Gemini, Claude, DeepSeek, vLLM)
- 📊 **Trend Analysis**: TF-IDF keyword extraction, word cloud visualization
- 🎯 **Personalized Recommendations**: Recommend papers based on your Zotero library
- 🖼️ **Figure Extraction**: Automatically extract method figures from PDFs
- 🌐 **Web Interface**: Modern responsive web UI
- ⏰ **Scheduled Execution**: Support daily automatic execution

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- LLM API Key (SiliconFlow, DeepSeek, or OpenAI recommended)
- Zotero account (optional, for personalized recommendations)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/daily-arxiv.git
cd daily-arxiv

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your API keys

# Run
python main.py

# Start web interface
python src/web/app.py
```

Visit http://localhost:5000 to view results.

## ⚙️ Configuration

### Environment Variables (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI or compatible API key | Yes |
| `OPENAI_BASE_URL` | API Base URL (for SiliconFlow etc.) | No |
| `ZOTERO_USER_ID` | Zotero user ID | No |
| `ZOTERO_API_KEY` | Zotero API key | No |

### Recommended LLM Providers

| Provider | Model | Get API Key |
|----------|-------|-------------|
| SiliconFlow | Qwen2.5-7B-Instruct | https://cloud.siliconflow.cn |
| DeepSeek | deepseek-chat | https://platform.deepseek.com |
| OpenAI | gpt-4o-mini | https://platform.openai.com |

## 📁 Project Structure

```
daily-arxiv/
├── config/config.yaml     # Configuration
├── src/
│   ├── crawler/           # Paper fetching
│   ├── summarizer/        # LLM summarization
│   ├── analyzer/          # Trend analysis
│   └── web/               # Web interface
├── main.py                # Main entry point
├── scheduler.py           # Scheduler
└── requirements.txt       # Dependencies
```

## 📄 License

MIT License