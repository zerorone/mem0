# Memgraph 图数据库账号信息

## 服务信息
- **服务地址**: http://localhost:3000 (Memgraph Lab Web UI)
- **数据库连接**: bolt://localhost:7687
- **容器名称**: mem0-memgraph

## 账号信息

### 管理员账号
```
用户名: mem0_admin
密码: Mem0Graph2025!SecurePass
权限: 全部权限（管理、读写、删除等）
用途: 数据库管理和维护
```

### 应用账号
```
用户名: mem0_app  
密码: App2025$GraphPass
权限: 读写权限（MATCH, CREATE, DELETE, MERGE, SET, REMOVE）
用途: Mem0 应用连接使用
```

## 配置文件位置

### 开发环境配置
**文件**: `config/development.json`
```json
{
  "graph_store_provider": "memgraph",
  "graph_store_config": {
    "url": "bolt://localhost:7687",
    "username": "mem0_app",
    "password": "App2025$GraphPass"
  }
}
```

### 服务端环境变量
**文件**: `server/.env.example`
```bash
MEMGRAPH_URI=bolt://memgraph:7687
MEMGRAPH_USERNAME=mem0_app
MEMGRAPH_PASSWORD=App2025$GraphPass
```

## Docker 部署命令

### 启动所有服务
```bash
docker-compose up -d
```

### 仅启动 Memgraph
```bash
docker-compose up -d memgraph
```

### 查看 Memgraph 日志
```bash
docker logs mem0-memgraph -f
```

## Web 界面访问

1. **访问地址**: http://localhost:3000
2. **连接设置**:
   - Host: localhost
   - Port: 7687
   - Username: mem0_admin 或 mem0_app
   - Password: 对应密码

## 数据持久化

- **数据目录**: `./memgraph_data/`
- **日志目录**: `./memgraph_logs/`
- **初始化脚本**: `./memgraph_init/`

## 安全注意事项

⚠️ **重要安全提醒**:
1. 生产环境请修改默认密码
2. 不要将密码提交到版本控制系统
3. 考虑使用环境变量或密钥管理系统
4. 定期更换密码
5. 限制网络访问权限

## 故障排查

### 连接失败
```bash
# 检查容器状态
docker ps | grep memgraph

# 检查端口占用
lsof -i :7687
lsof -i :3000

# 测试连接
docker exec -it mem0-memgraph mg_client -h localhost -p 7687 -u mem0_app -P "App2025$GraphPass"
```

### 重置数据库
```bash
# 停止容器
docker stop mem0-memgraph

# 删除数据（谨慎操作）
rm -rf memgraph_data memgraph_logs

# 重新启动
docker-compose up -d memgraph
```