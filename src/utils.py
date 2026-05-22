"""
工具函数模块
"""

import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv


def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"

    # 加载 .env 文件
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # 加载 YAML 配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 从环境变量中读取 API keys
    _load_env_keys(config)

    return config


def _load_env_keys(config):
    """从环境变量加载 API keys"""
    llm_config = config.get('llm', {})

    # OpenAI
    if 'openai' in llm_config:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            llm_config['openai']['api_key'] = openai_key
        openai_base = os.getenv('OPENAI_BASE_URL')
        if openai_base:
            llm_config['openai']['base_url'] = openai_base

    # Gemini
    if 'gemini' in llm_config:
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            llm_config['gemini']['api_key'] = gemini_key

    # Claude
    if 'claude' in llm_config:
        claude_key = os.getenv('CLAUDE_API_KEY')
        if claude_key:
            llm_config['claude']['api_key'] = claude_key

    # DeepSeek
    if 'deepseek' in llm_config:
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            llm_config['deepseek']['api_key'] = deepseek_key

    # vLLM
    if 'vllm' in llm_config:
        vllm_base = os.getenv('VLLM_BASE_URL')
        if vllm_base:
            llm_config['vllm']['base_url'] = vllm_base
        vllm_model = os.getenv('VLLM_MODEL')
        if vllm_model:
            llm_config['vllm']['model'] = vllm_model


def setup_logging(logging_config):
    """设置日志配置"""
    level = getattr(logging, logging_config.get('level', 'INFO').upper())
    log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = logging_config.get('file', 'logs/daily_arxiv.log')
    console = logging_config.get('console', True)

    # 创建日志目录
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(console_handler)


def save_json(data, filepath):
    """保存数据到 JSON 文件"""
    import json
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath):
    """从 JSON 文件加载数据"""
    import json
    filepath = Path(filepath)

    if not filepath.exists():
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_data_dir(config):
    """获取数据存储目录"""
    storage_config = config.get('storage', {})
    base_path = storage_config.get('json_path', 'data/papers')
    return Path(base_path)


def get_today_str():
    """获取今天的日期字符串"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')