#!/bin/bash

# Buciwa Internal 更新脚本
# 用于更新已部署的应用

set -e

DOMAIN="internal.buciwa.com"
DEPLOY_DIR="/var/www/buciwa_internal"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Buciwa Internal 更新脚本"
echo "=========================================="

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

# 更新后端
echo "[1/4] 更新后端代码..."
# 排除数据库文件，避免覆盖已有数据
rsync -av --exclude='*.db' --exclude='*.sqlite' --exclude='*.sqlite3' $PROJECT_DIR/backend/ $DEPLOY_DIR/backend/
cd $DEPLOY_DIR/backend
source venv/bin/activate
pip install -r requirements.txt

# 更新前端
echo "[2/4] 更新前端代码并重新构建..."
cp -r $PROJECT_DIR/frontend/* $DEPLOY_DIR/frontend/
cd $DEPLOY_DIR/frontend
npm install
npm run build

# 重启后端服务
echo "[3/4] 重启后端服务..."
systemctl restart buciwa-internal

# 重载 Nginx
echo "[4/4] 重载 Nginx..."
systemctl reload nginx

echo ""
echo "更新完成!"
echo "访问地址: https://$DOMAIN"
