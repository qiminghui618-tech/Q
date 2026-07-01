#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  Q - 股票分析智能体 部署脚本${NC}"
echo -e "${GREEN}=====================================${NC}"

# 检查 Python
echo -e "${YELLOW}检查 Python 版本...${NC}"
python --version
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 未找到 Python${NC}"
    exit 1
fi

# 创建虚拟环境
echo -e "${YELLOW}创建虚拟环境...${NC}"
python -m venv venv

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate || . venv/Scripts/activate

# 升级 pip
echo -e "${YELLOW}升级 pip...${NC}"
pip install --upgrade pip

# 安装依赖
echo -e "${YELLOW}安装依赖包...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}✗ 依赖安装失败${NC}"
    exit 1
fi

# 启动应用
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  启动应用...${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${YELLOW}应用运行地址:${NC}"
echo -e "${GREEN}  Web 仪表板: http://localhost:8000/index.html${NC}"
echo -e "${GREEN}  API 文档: http://localhost:8000/docs${NC}"
echo -e ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

python -m src.main
