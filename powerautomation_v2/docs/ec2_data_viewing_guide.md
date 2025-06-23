# EC2 PowerAutomation 數據查看指南

## 📊 當前數據狀態

### ❌ 為什麼data目錄是空的？

1. **VSIX擴展未安裝** - Mac端數據收集器還沒啟動
2. **TRAE連接未建立** - 沒有從TRAE數據庫提取數據
3. **智能監控未開始** - 系統等待啟動信號

## 🔍 EC2數據查看命令

### 1. 登入EC2
```bash
ssh -i alexchuang.pem ec2-user@18.212.97.173
```

### 2. 查看目錄結構
```bash
cd /home/ec2-user/powerautomation
tree . || ls -la
```

### 3. 檢查系統狀態
```bash
python3 powerautomation_system.py status
```

### 4. 查看配置文件
```bash
cat config.json
```

### 5. 監控日誌（實時）
```bash
tail -f logs/system.log
```

### 6. 查看所有日誌文件
```bash
ls -la logs/
cat logs/*.log 2>/dev/null || echo "暫無日誌文件"
```

## 📈 數據收集流程

### 階段1：VSIX安裝後
- 🔄 開始TRAE歷史提取
- 📁 創建 `data/trae_history_YYYYMMDD.json`
- 📝 記錄 `logs/trae_extraction.log`

### 階段2：智能監控啟動
- 👁️ 實時監控Manus對話
- 📊 記錄 `data/conversation_monitor_YYYYMMDD.jsonl`
- 🧠 智能分析 `data/intervention_analysis_YYYYMMDD.json`

### 階段3：自動介入
- 💬 發送智能回覆
- 📤 記錄 `logs/message_send_YYYYMMDD.jsonl`
- 📈 效果追蹤 `data/intervention_results_YYYYMMDD.json`

## 🚀 手動啟動數據收集

### 如果VSIX有問題，可以手動測試：

```bash
# 1. 測試TRAE連接
python3 powerautomation_system.py test-trae

# 2. 手動提取TRAE歷史
python3 powerautomation_system.py extract-history

# 3. 測試EC2系統
python3 powerautomation_system.py self-test

# 4. 模擬數據收集
python3 powerautomation_system.py demo-data
```

## 📊 預期的數據文件

### data/ 目錄將包含：
```
data/
├── trae_history_20250622.json          # TRAE對話歷史
├── conversation_monitor_20250622.jsonl # 實時對話監控
├── intervention_analysis_20250622.json # 智能分析結果
├── intervention_results_20250622.json  # 介入效果統計
└── system_stats_20250622.json         # 系統運行統計
```

### logs/ 目錄將包含：
```
logs/
├── system.log                          # 系統運行日誌
├── trae_extraction.log                 # TRAE提取日誌
├── message_send_20250622.jsonl        # 消息發送記錄
├── error.log                           # 錯誤日誌
└── performance.log                     # 性能監控日誌
```

## 💡 故障排除

### 如果數據收集失敗：

1. **檢查網絡連接**
```bash
ping google.com
curl -I https://manus.im
```

2. **檢查Python環境**
```bash
python3 --version
pip3 list | grep -E "(requests|json|sqlite)"
```

3. **檢查權限**
```bash
ls -la /home/ec2-user/powerautomation/
chmod +x powerautomation_system.py
```

4. **查看詳細錯誤**
```bash
python3 powerautomation_system.py debug
```

## 🎯 下一步行動

1. **安裝VSIX擴展** - 在VSCode中安裝powerautomation-1.0.0.vsix
2. **配置連接** - 設置EC2和TRAE連接參數
3. **啟動監控** - 按Ctrl+Alt+P開始智能監控
4. **查看數據** - 使用上述命令查看收集的數據

**一旦VSIX啟動，EC2的data目錄就會開始填充數據！**

