#!/bin/bash
# Mem0-GLM MCP 服务器启动脚本

set -e

echo "🚀 启动 Mem0-GLM MCP 服务器"

# 检查 Python 环境
PYTHON_PATH="/opt/miniconda3/envs/memos_py311/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python 环境不存在: $PYTHON_PATH"
    echo "请检查 conda 环境 memos_py311 是否存在"
    exit 1
fi

# 设置项目路径
PROJECT_ROOT="/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0"
cd "$PROJECT_ROOT"

# 设置环境变量
export PYTHONPATH="$PROJECT_ROOT"
export GLM_API_KEY="91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS"
export GLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
export GLM_MODEL="glm-4.5"
export VECTOR_STORE_PROVIDER="chroma"
export COLLECTION_NAME="mem0_memories"
export EMBEDDING_PROVIDER="ollama"
export LOG_LEVEL="INFO"

echo "✅ 环境配置完成"
echo "📁 项目根目录: $PROJECT_ROOT"
echo "🐍 Python 路径: $PYTHON_PATH"
echo "🤖 GLM 模型: $GLM_MODEL"

# 检查依赖
echo "🔍 检查依赖..."
$PYTHON_PATH -c "
import sys
try:
    import fastmcp
    print('✅ FastMCP 可用')
except ImportError:
    print('❌ FastMCP 未安装: pip install fastmcp')
    sys.exit(1)

try:
    from mem0 import Memory
    from mem0.llms.glm import GLMLLM
    print('✅ Mem0 + GLM 可用')
except ImportError as e:
    print(f'❌ Mem0/GLM 导入失败: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 依赖检查失败"
    exit 1
fi

echo "✅ 依赖检查通过"

# 创建必要目录
mkdir -p chroma_db
mkdir -p logs

# 启动服务器
echo "🚀 启动 MCP 服务器..."
$PYTHON_PATH mcp_server/server.py