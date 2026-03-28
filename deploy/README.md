# Buciwa Internal 部署文档

本文档说明如何将应用部署到 `internal.buciwa.com` 域名。

## 前置条件

1. 一台运行 Ubuntu/Debian 的服务器
2. 域名 `internal.buciwa.com` 已解析到服务器 IP
3. 服务器具有 root 权限
4. 后端 API 密钥等敏感信息（参考 `backend/.env.example`）

## 快速部署

### 1. 克隆代码到服务器

```bash
git clone <repository-url> /root/Buciwa_internal
cd /root/Buciwa_internal
```

### 2. 配置环境变量

复制并编辑后端环境变量文件：

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

需要配置以下关键变量：
- `ark_api_key` - Doubao API 密钥
- `volcano_access_key` - 火山引擎 TTS 密钥
- `volcano_app_id` - 火山引擎应用 ID

### 3. 运行部署脚本

```bash
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

部署脚本会自动完成：
- 安装系统依赖（Nginx, Python, Node.js 等）
- 配置 Python 虚拟环境并安装依赖
- 构建前端静态文件
- 配置 Nginx 和 SSL 证书
- 启动后端服务

### 4. 验证部署

访问 `https://internal.buciwa.com` 确认应用正常运行。

## 文件结构

```
deploy/
├── nginx/
│   └── internal.buciwa.com.conf  # Nginx 配置文件
├── systemd/
│   └── buciwa-internal.service   # 后端服务配置
├── deploy.sh                     # 首次部署脚本
├── update.sh                     # 更新部署脚本
└── README.md                     # 本文档
```

## 更新应用

当有代码更新时，运行更新脚本：

```bash
cd /root/Buciwa_internal
git pull
sudo ./deploy/update.sh
```

## 常用命令

### 后端服务管理

```bash
# 查看服务状态
systemctl status buciwa-internal

# 重启服务
systemctl restart buciwa-internal

# 查看日志
journalctl -u buciwa-internal -f

# 停止服务
systemctl stop buciwa-internal
```

### Nginx 管理

```bash
# 测试配置
nginx -t

# 重载配置
systemctl reload nginx

# 重启 Nginx
systemctl restart nginx

# 查看访问日志
tail -f /var/log/nginx/internal.buciwa.com.access.log

# 查看错误日志
tail -f /var/log/nginx/internal.buciwa.com.error.log
```

### SSL 证书管理

```bash
# 手动续期
certbot renew

# 查看证书状态
certbot certificates
```

## 故障排除

### 502 Bad Gateway

1. 检查后端服务是否运行：
   ```bash
   systemctl status buciwa-internal
   ```

2. 检查后端日志：
   ```bash
   journalctl -u buciwa-internal -n 100
   ```

### 前端页面空白

1. 检查前端是否正确构建：
   ```bash
   ls -la /var/www/buciwa_internal/frontend/dist/
   ```

2. 检查 Nginx 配置：
   ```bash
   nginx -t
   ```

### API 请求失败

1. 检查 CORS 配置
2. 检查后端环境变量是否正确配置
3. 检查 API 密钥是否有效

## 安全建议

1. 定期更新系统和依赖包
2. 配置防火墙只开放 80, 443, 22 端口
3. 定期备份数据库文件
4. 使用强密码并定期更换


建议：定期备份 /var/www/buciwa_internal/backend/word_memory.db 文件