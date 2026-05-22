#!/usr/bin/env python3
"""
测试 Web 服务
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config


def test_web():
    """测试 Web 服务"""
    print("=" * 60)
    print("测试 Web 服务")
    print("=" * 60)

    # 加载配置
    config = load_config()
    web_config = config.get('web', {})

    print(f"\nWeb 服务配置:")
    print(f"  主机: {web_config.get('host', '0.0.0.0')}")
    print(f"  端口: {web_config.get('port', 5000)}")
    print(f"  调试模式: {web_config.get('debug', True)}")

    print("\n启动 Web 服务...")
    print(f"访问地址: http://localhost:{web_config.get('port', 5000)}")
    print("\n按 Ctrl+C 停止服务")

    try:
        from src.web.app import run_web
        run_web()
    except KeyboardInterrupt:
        print("\nWeb 服务已停止")
    except Exception as e:
        print(f"\n启动 Web 服务失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_web()