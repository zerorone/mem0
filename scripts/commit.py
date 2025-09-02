#!/usr/bin/env python3
"""
智能 Git 提交工具
支持 Conventional Commit 格式和 emoji
"""

import subprocess
import sys
import re
from datetime import datetime
from typing import List, Tuple, Optional

# Emoji 映射
COMMIT_TYPES = {
    "feat": "✨",
    "fix": "🐛", 
    "docs": "📝",
    "style": "💄",
    "refactor": "♻️",
    "perf": "⚡️",
    "test": "✅",
    "chore": "🔧",
    "ci": "👷",
    "build": "📦️",
    "revert": "⏪️"
}

def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def get_git_status() -> Tuple[List[str], List[str]]:
    """获取 git 状态"""
    code, stdout, stderr = run_command(["git", "status", "--porcelain"])
    if code != 0:
        print(f"❌ 获取 git 状态失败: {stderr}")
        sys.exit(1)
    
    modified = []
    untracked = []
    
    for line in stdout.strip().split('\n'):
        if not line:
            continue
        status = line[:2]
        filename = line[3:]
        
        if status.startswith('??'):
            untracked.append(filename)
        else:
            modified.append(filename)
    
    return modified, untracked

def analyze_changes(files: List[str]) -> str:
    """分析文件变更类型"""
    if not files:
        return "chore"
    
    # 分析文件类型
    has_src = any(f.startswith(('mem0/', 'mcp_server/')) and f.endswith('.py') for f in files)
    has_tests = any('test' in f.lower() for f in files)
    has_docs = any(f.endswith(('.md', '.rst', '.txt')) for f in files)
    has_config = any(f.endswith(('.json', '.yml', '.yaml', '.toml')) for f in files)
    has_scripts = any(f.startswith('scripts/') for f in files)
    
    # 决定提交类型
    if has_src and not has_tests:
        return "feat"
    elif has_tests:
        return "test"
    elif has_docs and not has_src:
        return "docs"
    elif has_config or has_scripts:
        return "chore"
    else:
        return "feat"

def create_commit_message(commit_type: str, files: List[str]) -> str:
    """创建提交消息"""
    emoji = COMMIT_TYPES.get(commit_type, "🔧")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 分析主要变更
    categories = {
        "源码": [f for f in files if f.startswith(('mem0/', 'mcp_server/')) and f.endswith('.py')],
        "测试": [f for f in files if 'test' in f.lower()],
        "文档": [f for f in files if f.endswith(('.md', '.rst'))],
        "配置": [f for f in files if f.endswith(('.json', '.yml', '.yaml', '.toml'))],
        "脚本": [f for f in files if f.startswith('scripts/')],
        "其他": []
    }
    
    # 归类其他文件
    categorized = set()
    for cat_files in categories.values():
        categorized.update(cat_files)
    
    categories["其他"] = [f for f in files if f not in categorized]
    
    # 构建消息
    if commit_type == "feat":
        title = f"{emoji} feat: 添加新功能和改进"
    elif commit_type == "fix":
        title = f"{emoji} fix: 修复问题和错误"
    elif commit_type == "docs":
        title = f"{emoji} docs: 更新文档"
    elif commit_type == "test":
        title = f"{emoji} test: 添加或更新测试"
    elif commit_type == "chore":
        title = f"{emoji} chore: 维护和配置更新"
    else:
        title = f"{emoji} {commit_type}: 代码更新"
    
    body_parts = [title, ""]
    
    # 添加详细信息
    for category, cat_files in categories.items():
        if cat_files:
            body_parts.append(f"🔸 {category}:")
            for file in cat_files[:5]:  # 最多显示5个文件
                body_parts.append(f"  - {file}")
            if len(cat_files) > 5:
                body_parts.append(f"  - ... 和其他 {len(cat_files) - 5} 个文件")
            body_parts.append("")
    
    body_parts.append(f"📅 提交时间: {timestamp}")
    body_parts.append(f"📊 文件统计: {len(files)} 个文件更改")
    
    return "\n".join(body_parts)

def main():
    """主函数"""
    print("🚀 智能 Git 提交工具")
    print("=" * 50)
    
    # 检查是否有变更
    modified, untracked = get_git_status()
    all_files = modified + untracked
    
    if not all_files:
        print("✅ 工作区干净，无需提交")
        return
    
    print(f"📁 发现 {len(all_files)} 个文件变更:")
    for file in all_files[:10]:  # 显示前10个
        print(f"  - {file}")
    if len(all_files) > 10:
        print(f"  - ... 和其他 {len(all_files) - 10} 个文件")
    
    # 暂存所有文件
    print("\n📦 暂存文件...")
    code, stdout, stderr = run_command(["git", "add", "-A"])
    if code != 0:
        print(f"❌ 暂存文件失败: {stderr}")
        sys.exit(1)
    
    # 分析变更类型
    commit_type = analyze_changes(all_files)
    print(f"🔍 检测到提交类型: {commit_type}")
    
    # 创建提交消息
    commit_message = create_commit_message(commit_type, all_files)
    
    print("\n📝 提交消息:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    # 确认提交
    response = input("\n❓ 确认提交? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ 取消提交")
        return
    
    # 执行提交
    print("\n💾 执行提交...")
    code, stdout, stderr = run_command(["git", "commit", "-m", commit_message])
    if code != 0:
        print(f"❌ 提交失败: {stderr}")
        sys.exit(1)
    
    print("✅ 提交成功!")
    
    # 询问是否推送
    response = input("🚀 是否推送到远程仓库? (y/N): ").lower().strip()
    if response == 'y':
        print("📤 推送中...")
        code, stdout, stderr = run_command(["git", "push", "origin", "main"], capture_output=False)
        if code == 0:
            print("✅ 推送成功!")
        else:
            print(f"❌ 推送失败: {stderr}")
    
    print("\n🎉 完成!")

if __name__ == "__main__":
    main()
