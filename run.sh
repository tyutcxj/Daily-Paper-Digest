#!/bin/bash
# Daily arXiv - Linux/macOS 启动脚本

echo "========================================"
echo "Daily arXiv - AI Research Tracker"
echo "========================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.11+"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[提示] 未找到 .env 文件，正在从模板创建..."
    cp .env.example .env
    echo "[提示] 请编辑 .env 文件，填入你的 API Key"
    echo "[提示] 然后重新运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[提示] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[提示] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[提示] 安装依赖..."
pip install -r requirements.txt -q

# 菜单函数
show_menu() {
    echo ""
    echo "========================================"
    echo "请选择操作:"
    echo "========================================"
    echo "1. 获取今日论文并生成总结"
    echo "2. 启动 Web 界面"
    echo "3. 启动定时调度（每日自动执行）"
    echo "4. 测试论文爬取"
    echo "5. 测试 LLM 总结"
    echo "6. 退出"
    echo "========================================"
    echo ""
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (1-6): " choice

    case $choice in
        1)
            echo ""
            echo "[执行] 获取论文并生成总结..."
            python main.py
            echo ""
            echo "[完成] 数据已保存到 data/ 目录"
            read -p "按 Enter 继续..."
            ;;
        2)
            echo ""
            echo "[启动] Web 界面..."
            echo "[访问] http://localhost:5000"
            echo "[停止] 按 Ctrl+C"
            python src/web/app.py
            ;;
        3)
            echo ""
            echo "[启动] 定时调度器..."
            echo "[说明] 每天 09:00 自动执行"
            echo "[停止] 按 Ctrl+C"
            python scheduler.py
            ;;
        4)
            echo ""
            echo "[测试] 论文爬取..."
            python test/test_fetcher.py
            read -p "按 Enter 继续..."
            ;;
        5)
            echo ""
            echo "[测试] LLM 总结..."
            python test/test_summarizer.py
            read -p "按 Enter 继续..."
            ;;
        6)
            echo "再见！"
            exit 0
            ;;
        *)
            echo "[错误] 无效的选项，请重新选择"
            ;;
    esac
done