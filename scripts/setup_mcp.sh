#!/bin/bash
# Mem0-GLM MCP 快速设置脚本

set -e

echo "🚀 Mem0-GLM MCP 快速设置"

# 项目根目录
PROJECT_ROOT="/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0"
cd "$PROJECT_ROOT"

# 1. 检查 Python 环境
PYTHON_ENV="/opt/miniconda3/envs/memos_py311/bin/python"
if [ ! -f "$PYTHON_ENV" ]; then
    echo "❌ Python 环境不存在，创建 conda 环境..."
    conda create -n memos_py311 python=3.11 -y
    conda activate memos_py311
    PYTHON_ENV="/opt/miniconda3/envs/memos_py311/bin/python"
fi

echo "✅ Python 环境: $PYTHON_ENV"

# 2. 安装依赖
echo "📦 安装 MCP 依赖..."
$PYTHON_ENV -m pip install fastmcp httpx

echo "📦 安装 mem0 依赖..."
$PYTHON_ENV -m pip install -e .

# 3. 创建目录
echo "📁 创建必要目录..."
mkdir -p config
mkdir -p scripts
mkdir -p logs
mkdir -p chroma_data
mkdir -p qdrant_data
mkdir -p neo4j_data
mkdir -p neo4j_logs
mkdir -p ollama_data
mkdir -p redis_data

# 4. 设置权限
chmod +x scripts/start_mcp_server.sh

# 5. 创建 Claude Desktop 配置
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"

cat > "$CLAUDE_DIR/mcp_settings.json" << EOF
{
  "mcpServers": {
    "mem0-glm": {
      "command": "$PYTHON_ENV",
      "args": [
        "$PROJECT_ROOT/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "$PROJECT_ROOT"
      }
    }
  }
}
EOF

# 6. 创建环境变量文件
cat > config/.env << EOF
# GLM API 配置
GLM_API_KEY=91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
GLM_MODEL=glm-4.5
ENABLE_THINKING=true

# Vector Store 配置
VECTOR_STORE_PROVIDER=chroma
COLLECTION_NAME=mem0_memories
CHROMA_PATH=$PROJECT_ROOT/chroma_data

# 嵌入模型配置
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=bge-m3

# 日志配置
LOG_LEVEL=INFO
EOF

# 7. 验证安装
echo "🔍 验证安装..."
$PYTHON_ENV -c "
import sys
try:
    import fastmcp
    print('✅ FastMCP 可用')
except ImportError:
    print('❌ FastMCP 不可用')
    sys.exit(1)

try:
    from mem0 import Memory
    from mem0.llms.glm import GLMLLM
    print('✅ Mem0 + GLM 可用')
except ImportError as e:
    print(f'❌ Mem0/GLM 不可用: {e}')
    sys.exit(1)

print('🎉 所有依赖验证通过！')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Mem0-GLM MCP 设置完成！"
    echo ""
    echo "📋 下一步操作："
    echo "1️⃣  启动数据库服务: docker-compose up -d"
    echo "2️⃣  下载 Ollama 嵌入模型: ollama pull bge-m3"
    echo "3️⃣  启动 MCP 服务器: ./scripts/start_mcp_server.sh"
    echo "4️⃣  配置 Claude Desktop: 复制 ~/.claude/mcp_settings.json 到 Claude 配置"
    echo ""
    echo "🔗 相关文件:"
    echo "  - 配置文件: config/development.json"
    echo "  - 环境变量: config/.env"
    echo "  - MCP 设置: ~/.claude/mcp_settings.json"
    echo "  - Docker 服务: docker-compose.yml"
    echo ""
    echo "🚀 准备就绪！"
else
    echo "❌ 设置失败，请检查错误信息"
    exit 1
fi