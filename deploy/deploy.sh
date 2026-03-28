#!/bin/bash

# Buciwa Internal 部署脚本
# 用于将应用部署到 internal.buciwa.com
# 支持 Alibaba Cloud Linux / CentOS / RHEL

set -e

# 配置变量
DOMAIN="internal.buciwa.com"
DEPLOY_DIR="/var/www/buciwa_internal"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Buciwa Internal 部署脚本"
echo "域名: $DOMAIN"
echo "项目目录: $PROJECT_DIR"
echo "部署目录: $DEPLOY_DIR"
echo "=========================================="

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "检测到系统: $PRETTY_NAME"
fi

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

# 步骤 1: 安装系统依赖
echo ""
echo "[步骤 1/7] 安装系统依赖..."

if command -v dnf &> /dev/null; then
    # Alibaba Cloud Linux / Fedora / RHEL 8+
    dnf install -y python3 python3-pip python3-devel nodejs nginx certbot python3-certbot-nginx
elif command -v yum &> /dev/null; then
    # CentOS / RHEL 7
    yum install -y python3 python3-pip python3-devel nodejs nginx certbot python3-certbot-nginx
elif command -v apt-get &> /dev/null; then
    # Ubuntu / Debian
    apt-get update
    apt-get install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx
else
    echo "错误: 无法确定包管理器"
    exit 1
fi

# 步骤 2: 创建部署目录
echo ""
echo "[步骤 2/7] 创建部署目录..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/backend
mkdir -p $DEPLOY_DIR/frontend

# 步骤 3: 部署后端
echo ""
echo "[步骤 3/7] 部署后端..."
# 排除数据库文件，避免覆盖已有数据
rsync -av --exclude='*.db' --exclude='*.sqlite' --exclude='*.sqlite3' $PROJECT_DIR/backend/ $DEPLOY_DIR/backend/

# 创建 Python 虚拟环境
cd $DEPLOY_DIR/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 安装 Python 依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn[standard]

# 复制环境变量文件（如果不存在）
if [ ! -f ".env" ]; then
    if [ -f "$PROJECT_DIR/backend/.env" ]; then
        cp $PROJECT_DIR/backend/.env .env
    else
        echo "警告: 未找到 .env 文件，请手动配置 $DEPLOY_DIR/backend/.env"
    fi
fi

# 步骤 4: 部署前端
echo ""
echo "[步骤 4/7] 部署前端..."
cp -r $PROJECT_DIR/frontend/* $DEPLOY_DIR/frontend/

# 安装前端依赖并构建
cd $DEPLOY_DIR/frontend
npm install
npm run build

# 步骤 5: 配置 Nginx
echo ""
echo "[步骤 5/7] 配置 Nginx..."
cp $PROJECT_DIR/deploy/nginx/$DOMAIN.conf /etc/nginx/conf.d/

# 移除默认配置（如果存在）
if [ -f /etc/nginx/conf.d/default.conf ]; then
    mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
fi

# 测试 Nginx 配置
nginx -t

# 步骤 6: 配置 SSL 证书
echo ""
echo "[步骤 6/7] 配置 SSL 证书..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "正在获取 SSL 证书..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@buciwa.com
else
    echo "SSL 证书已存在，跳过获取"
fi

# 步骤 7: 配置并启动后端服务
echo ""
echo "[步骤 7/7] 配置并启动后端服务..."
cp $PROJECT_DIR/deploy/systemd/buciwa-internal.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable buciwa-internal
systemctl restart buciwa-internal

# 重启 Nginx
systemctl restart nginx

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo ""
echo "访问地址: https://$DOMAIN"
echo ""
echo "常用命令:"
echo "  查看后端日志: journalctl -u buciwa-internal -f"
echo "  重启后端服务: systemctl restart buciwa-internal"
echo "  重启 Nginx: systemctl restart nginx"
echo "  更新 SSL 证书: certbot renew"
echo ""
