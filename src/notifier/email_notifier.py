"""
邮件通知模块
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class EmailNotifier:
    """邮件通知器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.sender = config.get('sender', '')
        self.password = config.get('password', '')
        self.recipients = config.get('recipients', [])
        self.on_success = config.get('on_success', True)
        self.on_failure = config.get('on_failure', True)

    def send_success_notification(self, paper_count: int, summary_count: int):
        """发送成功通知"""
        if not self.on_success:
            return

        subject = f"Daily arXiv - 成功获取 {paper_count} 篇论文"
        body = self._build_success_body(paper_count, summary_count)

        self._send_email(subject, body)

    def send_failure_notification(self, error: str):
        """发送失败通知"""
        if not self.on_failure:
            return

        subject = "Daily arXiv - 执行失败"
        body = self._build_failure_body(error)

        self._send_email(subject, body)

    def _build_success_body(self, paper_count: int, summary_count: int) -> str:
        """构建成功通知邮件内容"""
        html = f"""
        <html>
        <body>
            <h2>Daily arXiv 执行成功</h2>
            <p>今日论文追踪任务已完成：</p>
            <ul>
                <li>获取论文数量: {paper_count}</li>
                <li>生成总结数量: {summary_count}</li>
            </ul>
            <p>请访问 Web 界面查看详细信息。</p>
        </body>
        </html>
        """
        return html

    def _build_failure_body(self, error: str) -> str:
        """构建失败通知邮件内容"""
        html = f"""
        <html>
        <body>
            <h2>Daily arXiv 执行失败</h2>
            <p>今日论文追踪任务执行失败：</p>
            <p><strong>错误信息:</strong></p>
            <pre>{error}</pre>
            <p>请检查日志文件以获取更多信息。</p>
        </body>
        </html>
        """
        return html

    def _send_email(self, subject: str, body: str):
        """发送邮件"""
        if not self.sender or not self.recipients:
            logger.warning("邮件配置不完整，跳过发送")
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.recipients)

            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipients, msg.as_string())

            logger.info(f"邮件发送成功: {subject}")

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")