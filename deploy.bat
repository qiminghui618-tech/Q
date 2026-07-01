@echo off
REM Windows 部署脚本

echo.
echo =====================================
echo   Q - 股票分析智能体 部署脚本
echo =====================================
echo.

REM 检查 Python
echo 检查 Python 版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python
    exit /b 1
)

REM 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 依赖安装失败
    exit /b 1
)

echo.
echo =====================================
echo   启动应用...
echo =====================================
echo.
echo Web 仪表板: http://localhost:8000/index.html
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m src.main
