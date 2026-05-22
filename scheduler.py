#!/usr/bin/env python3
"""
Daily arXiv - 定时调度器
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src.utils import load_config, setup_logging
from main import main as run_main

logger = logging.getLogger(__name__)


def scheduled_job():
    """定时任务"""
    logger.info("=" * 60)
    logger.info("定时任务开始执行")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        run_main()
        logger.info("定时任务执行完成")
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}", exc_info=True)


def start_scheduler():
    """启动调度器"""
    # 加载配置
    config = load_config()
    setup_logging(config.get('logging', {}))

    scheduler_config = config.get('scheduler', {})

    if not scheduler_config.get('enabled', False):
        logger.info("调度器未启用")
        return

    run_time = scheduler_config.get('run_time', '09:00')
    timezone = scheduler_config.get('timezone', 'Asia/Shanghai')
    run_on_start = scheduler_config.get('run_on_start', False)

    logger.info("=" * 60)
    logger.info("Daily arXiv 调度器启动")
    logger.info(f"执行时间: {run_time}")
    logger.info(f"时区: {timezone}")
    logger.info(f"启动时立即运行: {run_on_start}")
    logger.info("=" * 60)

    # 创建调度器
    scheduler = BlockingScheduler(timezone=timezone)

    # 解析时间
    hour, minute = run_time.split(':')

    # 添加定时任务
    scheduler.add_job(
        scheduled_job,
        CronTrigger(hour=int(hour), minute=int(minute), timezone=timezone),
        id='daily_arxiv',
        name='Daily arXiv 论文追踪',
        replace_existing=True
    )

    # 启动时立即运行一次
    if run_on_start:
        logger.info("启动时立即运行一次...")
        scheduled_job()

    try:
        logger.info("调度器已启动，按 Ctrl+C 停止")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("调度器已停止")
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()