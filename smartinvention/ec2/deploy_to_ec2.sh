#!/bin/bash
# PowerAutomation 完整部署腳本

echo "🚀 開始部署PowerAutomation系統到EC2..."

# 設置變量
EC2_HOST="ec2-user@18.212.97.173"
SSH_KEY="alexchuang.pem"
REMOTE_DIR="/home/ec2-user/powerautomation"

# 檢查SSH密鑰
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH密鑰文件不存在: $SSH_KEY"
    exit 1
fi

echo "📁 創建遠程目錄結構..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
    mkdir -p $REMOTE_DIR/{data,logs,scripts}
    chmod 755 $REMOTE_DIR
    chmod 755 $REMOTE_DIR/{data,logs,scripts}
"

echo "📤 上傳核心文件..."

# 上傳對話同步系統
scp -i "$SSH_KEY" conversation_sync_system.py "$EC2_HOST:$REMOTE_DIR/"

# 上傳EC2 API服務器
scp -i "$SSH_KEY" ec2_api_server.py "$EC2_HOST:$REMOTE_DIR/"

# 上傳之前的核心文件
scp -i "$SSH_KEY" powerautomation_ec2_system.py "$EC2_HOST:$REMOTE_DIR/" 2>/dev/null || echo "⚠️  powerautomation_ec2_system.py 不存在，跳過"

echo "⚙️  創建配置文件..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
cat > $REMOTE_DIR/config.json << 'EOF'
{
    \"ec2_endpoint\": \"http://localhost:8000\",
    \"trae_db_path\": \"/Users/alexchuang/trae/conversations.db\",
    \"sync_interval\": 30,
    \"max_retries\": 3,
    \"manus_url\": \"https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ\",
    \"api_settings\": {
        \"host\": \"0.0.0.0\",
        \"port\": 8000,
        \"debug\": false
    },
    \"intervention_settings\": {
        \"confidence_threshold\": 0.3,
        \"priority_threshold\": \"medium\",
        \"auto_respond\": false
    }
}
EOF
"

echo "🔧 創建啟動腳本..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
cat > $REMOTE_DIR/start_powerautomation.sh << 'EOF'
#!/bin/bash
# PowerAutomation 啟動腳本

SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\"
cd \"\$SCRIPT_DIR\"

# 檢查Python環境
if ! command -v python3 &> /dev/null; then
    echo \"❌ Python3 未安裝\"
    exit 1
fi

# 安裝依賴
echo \"📦 檢查Python依賴...\"
pip3 install flask requests sqlite3 --quiet 2>/dev/null || echo \"⚠️  部分依賴可能已存在\"

# 啟動API服務器
echo \"🚀 啟動PowerAutomation API服務器...\"
nohup python3 ec2_api_server.py > logs/api_server.log 2>&1 &
API_PID=\$!
echo \$API_PID > logs/api_server.pid

echo \"✅ API服務器已啟動 (PID: \$API_PID)\"
echo \"📊 API端點: http://localhost:8000\"
echo \"📝 日誌文件: logs/api_server.log\"

# 等待服務器啟動
sleep 3

# 檢查服務器狀態
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo \"✅ API服務器運行正常\"
else
    echo \"❌ API服務器啟動失敗\"
    exit 1
fi

echo \"🎯 PowerAutomation系統已就緒！\"
echo \"\"
echo \"📋 可用的API端點:\"
echo \"  - GET  /api/health                 - 健康檢查\"
echo \"  - POST /api/sync/conversations     - 同步對話\"
echo \"  - GET  /api/conversations/latest   - 獲取最新對話\"
echo \"  - GET  /api/statistics             - 獲取統計信息\"
echo \"  - GET  /api/interventions/needed   - 獲取需要介入的對話\"
echo \"\"
echo \"📊 查看統計: curl http://localhost:8000/api/statistics\"
echo \"🔍 查看日誌: tail -f logs/api_server.log\"
EOF

chmod +x $REMOTE_DIR/start_powerautomation.sh
"

echo "🛑 創建停止腳本..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
cat > $REMOTE_DIR/stop_powerautomation.sh << 'EOF'
#!/bin/bash
# PowerAutomation 停止腳本

SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\"
cd \"\$SCRIPT_DIR\"

echo \"🛑 停止PowerAutomation服務...\"

# 停止API服務器
if [ -f logs/api_server.pid ]; then
    PID=\$(cat logs/api_server.pid)
    if kill -0 \$PID 2>/dev/null; then
        kill \$PID
        echo \"✅ API服務器已停止 (PID: \$PID)\"
    else
        echo \"⚠️  API服務器進程不存在\"
    fi
    rm -f logs/api_server.pid
else
    echo \"⚠️  找不到PID文件\"
fi

# 清理其他相關進程
pkill -f \"ec2_api_server.py\" 2>/dev/null && echo \"🧹 清理殘留進程\"

echo \"✅ PowerAutomation服務已停止\"
EOF

chmod +x $REMOTE_DIR/stop_powerautomation.sh
"

echo "📊 創建狀態檢查腳本..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
cat > $REMOTE_DIR/status_powerautomation.sh << 'EOF'
#!/bin/bash
# PowerAutomation 狀態檢查腳本

SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\"
cd \"\$SCRIPT_DIR\"

echo \"📊 PowerAutomation 系統狀態\"
echo \"================================\"

# 檢查API服務器
if [ -f logs/api_server.pid ]; then
    PID=\$(cat logs/api_server.pid)
    if kill -0 \$PID 2>/dev/null; then
        echo \"✅ API服務器運行中 (PID: \$PID)\"
        
        # 檢查API響應
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo \"✅ API服務響應正常\"
        else
            echo \"❌ API服務無響應\"
        fi
    else
        echo \"❌ API服務器未運行\"
    fi
else
    echo \"❌ API服務器未啟動\"
fi

echo \"\"
echo \"📁 數據目錄狀態:\"
echo \"  - 對話文件: \$(ls data/conversations_*.json 2>/dev/null | wc -l) 個\"
echo \"  - 分析文件: \$(ls data/intervention_analysis_*.json 2>/dev/null | wc -l) 個\"
echo \"  - 日誌文件: \$(ls logs/*.log 2>/dev/null | wc -l) 個\"

echo \"\"
echo \"💾 磁盤使用:\"
du -sh data/ logs/ 2>/dev/null || echo \"  - 目錄為空\"

echo \"\"
echo \"🔗 網絡端口:\"
netstat -tlnp 2>/dev/null | grep :8000 || echo \"  - 端口8000未監聽\"

# 如果API運行，顯示統計信息
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo \"\"
    echo \"📈 系統統計:\"
    curl -s http://localhost:8000/api/statistics | python3 -m json.tool 2>/dev/null || echo \"  - 無法獲取統計信息\"
fi
EOF

chmod +x $REMOTE_DIR/status_powerautomation.sh
"

echo "🧪 創建測試腳本..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
cat > $REMOTE_DIR/test_powerautomation.sh << 'EOF'
#!/bin/bash
# PowerAutomation 測試腳本

SCRIPT_DIR=\"\$(cd \"\$(dirname \"\${BASH_SOURCE[0]}\")\" && pwd)\"
cd \"\$SCRIPT_DIR\"

echo \"🧪 測試PowerAutomation系統\"
echo \"================================\"

# 測試API健康檢查
echo \"1. 測試API健康檢查...\"
if curl -s http://localhost:8000/api/health | python3 -m json.tool; then
    echo \"✅ 健康檢查通過\"
else
    echo \"❌ 健康檢查失敗\"
    exit 1
fi

echo \"\"
echo \"2. 測試對話同步...\"

# 創建測試數據
cat > test_conversation.json << 'TEST_EOF'
{
    \"conversations\": [
        {
            \"id\": \"test_1\",
            \"user_message\": \"我想要生成一個貪吃蛇\",
            \"assistant_message\": \"\",
            \"status\": \"正在分析問題...\",
            \"timestamp\": \"2025-06-22T12:00:00\",
            \"session_id\": \"test_session\",
            \"metadata\": {
                \"source\": \"test\",
                \"ui_state\": {
                    \"user_avatar\": \"Test User\",
                    \"assistant_status\": \"analyzing\"
                }
            },
            \"source\": \"trae_test\",
            \"intervention_analysis\": {
                \"intervention_needed\": true,
                \"confidence_score\": 0.9,
                \"triggered_categories\": [\"code_request\", \"game_development\"],
                \"priority\": \"high\"
            }
        }
    ],
    \"sync_metadata\": {
        \"total_count\": 1,
        \"sync_time\": \"2025-06-22T12:00:00\",
        \"source_system\": \"test_system\"
    }
}
TEST_EOF

# 發送測試數據
if curl -s -X POST http://localhost:8000/api/sync/conversations \
    -H \"Content-Type: application/json\" \
    -d @test_conversation.json | python3 -m json.tool; then
    echo \"✅ 對話同步測試通過\"
else
    echo \"❌ 對話同步測試失敗\"
fi

rm -f test_conversation.json

echo \"\"
echo \"3. 測試統計信息...\"
if curl -s http://localhost:8000/api/statistics | python3 -m json.tool; then
    echo \"✅ 統計信息測試通過\"
else
    echo \"❌ 統計信息測試失敗\"
fi

echo \"\"
echo \"4. 測試介入需求...\"
if curl -s http://localhost:8000/api/interventions/needed | python3 -m json.tool; then
    echo \"✅ 介入需求測試通過\"
else
    echo \"❌ 介入需求測試失敗\"
fi

echo \"\"
echo \"🎉 測試完成！\"
EOF

chmod +x $REMOTE_DIR/test_powerautomation.sh
"

echo "🔧 設置權限..."
ssh -i "$SSH_KEY" "$EC2_HOST" "
    chmod +x $REMOTE_DIR/*.py
    chmod +x $REMOTE_DIR/*.sh
    chmod 755 $REMOTE_DIR
"

echo "🚀 啟動PowerAutomation系統..."
ssh -i "$SSH_KEY" "$EC2_HOST" "cd $REMOTE_DIR && ./start_powerautomation.sh"

echo ""
echo "✅ PowerAutomation系統部署完成！"
echo ""
echo "📋 管理命令:"
echo "  啟動: ssh -i $SSH_KEY $EC2_HOST 'cd $REMOTE_DIR && ./start_powerautomation.sh'"
echo "  停止: ssh -i $SSH_KEY $EC2_HOST 'cd $REMOTE_DIR && ./stop_powerautomation.sh'"
echo "  狀態: ssh -i $SSH_KEY $EC2_HOST 'cd $REMOTE_DIR && ./status_powerautomation.sh'"
echo "  測試: ssh -i $SSH_KEY $EC2_HOST 'cd $REMOTE_DIR && ./test_powerautomation.sh'"
echo ""
echo "🌐 API端點: http://18.212.97.173:8000"
echo "📊 統計信息: curl http://18.212.97.173:8000/api/statistics"

