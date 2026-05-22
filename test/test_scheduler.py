#!/usr/bin/env python3
"""
测试调度器
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config


def test_scheduler():
    """测试调度器"""
    print("=" * 60)
    print("测试调度器")
    print("=" * 60)

    # 加载配置
    config = load_config()
    scheduler_config = config.get('scheduler', {})

    print(f"\n调度器配置:")
    print(f"  启用: {scheduler_config.get('enabled', False)}")
    print(f"  执行时间: {scheduler_config.get('run_time', '09:00')}")
    print(f"  时区: {scheduler_config.get('timezone', 'Asia/Shanghai')}")
    print(f"  启动时运行: {scheduler_config.get('run_on_start', False)}")

    if not scheduler_config.get('enabled', False):
        print("\n调度器未启用，请在 config.yaml 中设置 scheduler.enabled: true")
        return

    print("\n启动调度器...")
    print("按 Ctrl+C 停止")

    try:
        from scheduler import start_scheduler
        start_scheduler()
    except KeyboardInterrupt:
        print("\n调度器已停止")
    except Exception as e:
        print(f"\n启动调度器失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_scheduler()