@echo off
REM Daily arXiv - Windows 启动脚本

echo ========================================
echo Daily arXiv - AI Research Tracker
echo ========================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist ".env" (
    echo [提示] 未找到 .env 文件，正在从模板创建...
    copy .env.example .env
    echo [提示] 请编辑 .env 文件，填入你的 API Key
    echo [提示] 然后重新运行此脚本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [提示] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [提示] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [提示] 安装依赖...
pip install -r requirements.txt -q

REM 显示菜单
:menu
echo.
echo ========================================
echo 请选择操作:
echo ========================================
echo 1. 获取今日论文并生成总结
echo 2. 启动 Web 界面
echo 3. 启动定时调度（每日自动执行）
echo 4. 测试论文爬取
echo 5. 测试 LLM 总结
echo 6. 退出
echo ========================================
echo.

set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" (
    echo.
    echo [执行] 获取论文并生成总结...
    python main.py
    echo.
    echo [完成] 数据已保存到 data/ 目录
    pause
    goto menu
)
if "%choice%"=="2" (
    echo.
    echo [启动] Web 界面...
    echo [访问] http://localhost:5000
    echo [停止] 按 Ctrl+C
    python src/web/app.py
    goto menu
)
if "%choice%"=="3" (
    echo.
    echo [启动] 定时调度器...
    echo [说明] 每天 09:00 自动执行
    echo [停止] 按 Ctrl+C
    python scheduler.py
    goto menu
)
if "%choice%"=="4" (
    echo.
    echo [测试] 论文爬取...
    python test/test_fetcher.py
    pause
    goto menu
)
if "%choice%"=="5" (
    echo.
    echo [测试] LLM 总结...
    python test/test_summarizer.py
    pause
    goto menu
)
if "%choice%"=="6" (
    echo 再见！
    exit /b 0
)

echo [错误] 无效的选项，请重新选择
goto menu