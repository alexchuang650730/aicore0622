#!/bin/bash
"""
TRAE-Manus智能介入系統啟動腳本
"""

echo "🚀 啟動TRAE-Manus智能介入系統"
echo "=================================="

# 檢查Python環境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安裝"
    exit 1
fi

# 設置執行權限
chmod +x interactive_trae_system.py

# 啟動系統
echo "🔗 正在啟動交互式系統..."
python3 interactive_trae_system.py

echo "👋 系統已退出"

