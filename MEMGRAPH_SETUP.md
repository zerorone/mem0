# Memgraph 图数据库部署指南

## 手动 Docker 部署命令

### 1. 创建必要的目录
```bash
mkdir -p memgraph_data memgraph_logs
```

### 2. 启动 Memgraph 容器（与服务端配置一致）
```bash
docker run -d \
  --name mem0-memgraph \
  -p 8687:7687 \
  -p 8474:3000 \
  -v $(pwd)/memgraph_data:/var/lib/memgraph \
  -v $(pwd)/memgraph_logs:/var/log/memgraph \
  -e MEMGRAPH_USER=memgraph \
  -e MEMGRAPH_PASSWORD=mem0graph \
  memgraph/memgraph:latest \
  --log-level=INFO --bolt-port=7687 --bolt-address=0.0.0.0
```

### 3. 验证 Memgraph 是否运行
```bash
# 检查容器状态
docker ps | grep memgraph

# 检查容器日志
docker logs mem0-memgraph

# 测试连接
docker exec -it mem0-memgraph mgconsole --host localhost --port 7687 --username memgraph --password mem0password
```

### 4. 停止和重启
```bash
# 停止
docker stop mem0-memgraph

# 启动
docker start mem0-memgraph

# 删除（重新部署时）
docker rm -f mem0-memgraph
```

## 端口说明

- **8687**: Bolt 协议端口（用于数据库连接）
- **8474**: Memgraph Lab Web UI（图形界面）

## Web 访问

启动后可通过以下地址访问：
- **Memgraph Lab**: http://localhost:8474
  - 用户名: `memgraph`  
  - 密码: `mem0graph`

## 配置文件

已修改 `config/development.json`：
```json
{
  "graph_store_provider": "memgraph",
  "graph_store_config": {
    "url": "bolt://localhost:8687",
    "username": "memgraph", 
    "password": "mem0graph"
  }
}
```

## 服务端 Docker Compose

已修改 `server/docker-compose.yaml` 使用 Memgraph：
- 替换了 Neo4j 服务为 Memgraph 服务
- 端口映射：8687:7687 (Bolt), 8474:3000 (Web UI)
- 健康检查和依赖配置已更新

## 数据持久化

数据存储在以下目录：
- **数据文件**: `./memgraph_data/`
- **日志文件**: `./memgraph_logs/`

## 常见问题

### Q: 端口 7688 被占用？
```bash
# 查看端口使用
lsof -i :7688

# 或修改为其他端口
docker run -d --name mem0-memgraph -p 7689:7687 ...
# 同时修改配置文件中的端口
```

### Q: 权限问题？
```bash
# 确保目录权限正确
sudo chown -R $(id -u):$(id -g) memgraph_data memgraph_logs
```

### Q: 容器启动失败？
```bash
# 查看详细日志
docker logs mem0-memgraph --tail 50

# 重新启动
docker restart mem0-memgraph
```

## 与 Mem0 集成测试

运行以下命令测试集成：
```bash
# 确保 Memgraph 运行
docker ps | grep memgraph

# 重启 Mem0 API 服务器以应用新配置
# (需要手动重启 api_server.py)

# 运行测试
python test_dual_database.py
```