# EC2端組件 - PowerAutomation

EC2端負責接收Mac端數據、智能分析、存儲和提供API服務。

## 📁 組件結構

### 🎯 **核心服務**
- `ec2_api_server.py` - 主API服務器
- `working_powerautomation.py` - 核心工作系統
- `powerautomation_ec2_system.py` - EC2系統管理

### 🧠 **智能分析**
- `conversation_sync_system.py` - 對話同步系統
- `real_conversation_extractor.py` - 真實對話數據提取

### 🚀 **部署工具**
- `deploy_to_ec2.sh` - 自動化部署腳本

## ✅ 已驗證功能

- ✅ API服務器運行正常 (PID: 182486)
- ✅ 端口8000正常監聽
- ✅ 健康檢查通過
- ✅ 對話同步功能正常
- ✅ 智能介入分析正常

## 🔧 API端點

### 系統管理
- `GET /api/health` - 健康檢查
- `GET /api/statistics` - 統計信息

### 對話管理
- `POST /api/sync/conversations` - 同步對話
- `GET /api/conversations/latest` - 最新對話
- `GET /api/interventions/needed` - 需要介入的對話

## 🚀 部署方法

```bash
# 自動部署
./deploy_to_ec2.sh

# 檢查狀態
ssh -i alexchuang.pem ec2-user@18.212.97.173 'cd /home/ec2-user/powerautomation && ./status_powerautomation.sh'
```

