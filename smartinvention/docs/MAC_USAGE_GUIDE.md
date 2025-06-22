# Mac本地Manus操作工具使用指南

## 🎯 功能特點

這個工具可以直接在您的Mac上運行，無需網絡隧道，實現：

1. **對話歷史提取** - 完整提取Manus頁面的所有對話記錄
2. **批量下載** - 自動保存對話、截圖、HTML等數據
3. **自動發送消息** - 智能查找輸入框並發送回覆
4. **交互式操作** - 提供友好的命令行界面

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 安裝Python依賴
pip3 install playwright

# 安裝Playwright瀏覽器
playwright install chromium
```

### 2. 下載腳本

將 `mac_manus_operator.py` 保存到您的Mac上

### 3. 運行腳本

```bash
# 交互模式 (推薦)
python3 mac_manus_operator.py --action interactive

# 或直接提取對話
python3 mac_manus_operator.py --action conversations

# 或批量下載
python3 mac_manus_operator.py --action download
```

## 📋 使用方法

### 交互模式 (推薦)

```bash
python3 mac_manus_operator.py --action interactive
```

交互模式提供以下選項：
- `1` - 提取對話歷史
- `2` - 發送消息
- `3` - 批量下載數據
- `4` - 執行完整演示
- `5` - 頁面截圖
- `q` - 退出

### 命令行模式

#### 提取對話歷史
```bash
python3 mac_manus_operator.py --action conversations
```

#### 發送消息
```bash
python3 mac_manus_operator.py --action send --message "您好，這是測試消息"
```

#### 批量下載
```bash
python3 mac_manus_operator.py --action download --output ./downloads
```

#### 完整演示
```bash
python3 mac_manus_operator.py --action demo
```

### 自定義選項

```bash
# 使用自定義URL
python3 mac_manus_operator.py --url "https://manus.im/app/your-app-id" --action conversations

# 無頭模式運行 (不顯示瀏覽器)
python3 mac_manus_operator.py --headless --action download
```

## 📁 輸出文件

批量下載會創建以下文件：

```
manus_data/
├── conversations_20231222_143022.json      # 結構化對話數據
├── conversations_readable_20231222_143022.txt  # 可讀格式對話
├── screenshot_20231222_143022.png          # 完整頁面截圖
├── page_content_20231222_143022.html       # 頁面HTML源碼
└── statistics_20231222_143022.json         # 統計報告
```

## 📊 數據格式

### 對話消息格式
```json
{
  "id": "msg_1_1703234567",
  "content": "用戶的問題內容",
  "sender": "user",
  "timestamp": "2023-12-22T14:30:22",
  "message_type": "user_message",
  "conversation_id": "main",
  "attachments": ["image:https://...", "link:https://..."],
  "metadata": {
    "index": 1,
    "element_class": "message user-message",
    "extraction_time": "2023-12-22T14:30:22"
  }
}
```

### 統計報告格式
```json
{
  "extraction_time": "2023-12-22T14:30:22",
  "total_conversations": 150,
  "conversation_types": {
    "user_message": 75,
    "assistant_response": 70,
    "system": 5
  },
  "senders": {
    "user": 75,
    "assistant": 70,
    "system": 5
  },
  "time_range": {
    "earliest": "2023-12-20T10:00:00",
    "latest": "2023-12-22T14:30:22"
  }
}
```

## 🔧 高級功能

### 1. 智能選擇器

腳本使用多組選擇器來適應不同的頁面結構：

```python
# 消息選擇器
'.message', '.chat-message', '.conversation-message'

# 輸入框選擇器  
'textarea[placeholder*="輸入"]', '.message-input', '[contenteditable="true"]'

# 發送按鈕選擇器
'button[type="submit"]', '.send-button', 'button:has-text("發送")'
```

### 2. 自動登入處理

如果檢測到需要登入，腳本會：
1. 暫停執行
2. 提示您在瀏覽器中完成登入
3. 等待您按Enter繼續

### 3. 智能滾動加載

自動滾動頁面以加載所有對話內容：
- 最多滾動50次
- 智能檢測內容變化
- 支持對話容器滾動

### 4. 多種提取方法

如果標準選擇器失效，會自動嘗試：
- 通用元素掃描
- 文本內容分析
- 關鍵詞檢測

## ⚠️ 注意事項

### 首次使用
1. **非無頭模式** - 首次運行建議不使用 `--headless`，方便手動登入
2. **網絡穩定** - 確保網絡連接穩定
3. **瀏覽器權限** - 可能需要授權瀏覽器訪問

### 性能優化
1. **使用無頭模式** - 提高性能：`--headless`
2. **限制滾動** - 如果對話很多，可能需要較長時間
3. **定期清理** - 清理下載的文件以節省空間

### 故障排除

#### 找不到元素
```bash
# 檢查頁面是否完全加載
# 確認登入狀態
# 嘗試非無頭模式觀察頁面
python3 mac_manus_operator.py --action conversations
```

#### 登入問題
```bash
# 使用非無頭模式手動登入
python3 mac_manus_operator.py --action interactive
```

#### 提取失敗
```bash
# 查看日誌文件
cat logs/manus_operations_YYYYMMDD.log

# 嘗試頁面截圖檢查狀態
python3 mac_manus_operator.py --action interactive
# 然後選擇選項 5 進行截圖
```

## 🔄 自動化使用

### 定時任務
```bash
# 使用cron設置定時任務
# 每小時執行一次數據下載
0 * * * * cd /path/to/script && python3 mac_manus_operator.py --headless --action download
```

### 批處理腳本
```bash
#!/bin/bash
# 自動化腳本示例

echo "開始Manus數據提取..."

# 提取對話
python3 mac_manus_operator.py --headless --action conversations

# 批量下載
python3 mac_manus_operator.py --headless --action download --output "backup_$(date +%Y%m%d)"

echo "完成!"
```

## 📞 支援

### 日誌文件
所有操作都會記錄在 `logs/manus_operations_YYYYMMDD.log`

### 常見問題
1. **Playwright安裝失敗** - 確保Python版本 >= 3.7
2. **瀏覽器啟動失敗** - 嘗試重新安裝：`playwright install chromium`
3. **權限問題** - 確保腳本有執行權限：`chmod +x mac_manus_operator.py`

### 自定義修改
如果需要適配特定的頁面結構，可以修改腳本中的選擇器配置。

---

**🎉 現在您可以直接在Mac上運行這個腳本，無需任何網絡隧道！**

