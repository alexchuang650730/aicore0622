# Manus Playwright操作工具使用指南

## 功能概述

這個工具提供了完整的Manus頁面操作功能：

1. **對話歷史提取** - 使用Playwright抓取所有對話記錄
2. **批量下載** - 自動遍歷和下載所有對話數據
3. **任務列表監控** - 實時監控任務狀態變化
4. **輸入框操作** - 自動發送智能回覆

## 安裝依賴

```bash
# 安裝Python依賴
pip3 install playwright asyncio

# 安裝Playwright瀏覽器
playwright install chromium
```

## 使用方法

### 1. 基本使用

```bash
# 在Mac上運行（因為需要處理認證）
python3 manus_simple_operator.py --action interactive
```

### 2. 具體操作

#### 提取對話歷史
```bash
python3 manus_simple_operator.py --action conversations
```

#### 提取任務列表
```bash
python3 manus_simple_operator.py --action tasks
```

#### 批量下載數據
```bash
python3 manus_simple_operator.py --action download --output ./downloads
```

#### 發送消息
```bash
python3 manus_simple_operator.py --action send --message "這是一條測試消息"
```

#### 監控任務變化
```bash
python3 manus_simple_operator.py --action monitor --duration 120
```

### 3. 交互模式

```bash
python3 manus_simple_operator.py --action interactive
```

交互模式提供以下命令：
- `1` - 提取對話歷史
- `2` - 提取任務列表  
- `3` - 批量下載
- `4` - 發送消息
- `5` - 監控任務 (30秒)
- `q` - 退出

### 4. 自定義URL

```bash
python3 manus_simple_operator.py --url "https://manus.im/app/your-app-id" --action conversations
```

### 5. 無頭模式

```bash
python3 manus_simple_operator.py --headless --action download
```

## 輸出文件

批量下載會創建以下文件：

```
manus_data/
├── conversations_20231222_143022.json  # 對話歷史
├── tasks_20231222_143022.json          # 任務列表
├── screenshot_20231222_143022.png      # 頁面截圖
├── page_content_20231222_143022.html   # 頁面HTML
└── download_0_export.csv               # 自動下載的文件
```

## 數據格式

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
    "element_html": "..."
  }
}
```

### 任務格式
```json
{
  "task_id": "task_1_1703234567",
  "title": "任務標題",
  "status": "pending",
  "priority": "normal",
  "created_at": "2023-12-22T14:30:22",
  "updated_at": "2023-12-22T14:30:22",
  "description": "任務描述",
  "progress": 0.5,
  "assignee": "",
  "metadata": {
    "index": 1,
    "element_html": "..."
  }
}
```

## 智能監控功能

### 任務變化監控
系統會自動檢測：
- 任務數量變化
- 任務狀態變化
- 任務進度更新

### 自動回覆功能
```python
# 設置觸發關鍵詞和回覆模板
trigger_keywords = ["幫助", "問題", "困難"]
response_template = "我注意到您提到了'{keyword}'，讓我來幫助您解決這個問題。"

await operator.auto_reply_with_intelligence(trigger_keywords, response_template)
```

## 注意事項

1. **認證問題** - 必須在Mac本機運行，因為會有認證問題
2. **頁面加載** - 首次運行時需要手動完成登入
3. **選擇器適配** - 如果頁面結構變化，可能需要調整選擇器
4. **網絡穩定** - 確保網絡連接穩定，避免操作中斷

## 故障排除

### 找不到元素
如果提示找不到元素，可以：
1. 檢查頁面是否完全加載
2. 確認登入狀態
3. 檢查選擇器是否正確

### 登入問題
1. 設置 `headless=False` 以便手動登入
2. 等待登入完成後再執行操作
3. 確保瀏覽器會話保持活躍

### 性能優化
1. 使用 `--headless` 模式提高性能
2. 調整監控間隔時間
3. 限制滾動加載次數

## 高級用法

### 自定義選擇器
```python
# 修改 manus_playwright_operator.py 中的選擇器
self.selectors['message_item'].append('.your-custom-selector')
```

### 批量處理多個頁面
```python
urls = [
    "https://manus.im/app/page1",
    "https://manus.im/app/page2"
]

for url in urls:
    operator = ManusPlaywrightOperator(url)
    await operator.initialize()
    await operator.batch_download_data(f"data_{url.split('/')[-1]}")
    await operator.cleanup()
```

### 定時任務
```bash
# 使用cron設置定時任務
# 每小時執行一次數據下載
0 * * * * cd /path/to/script && python3 manus_simple_operator.py --action download --headless
```

## 支援和反饋

如果遇到問題或需要新功能，請檢查：
1. 日誌文件 `logs/manus_operations_YYYYMMDD.log`
2. 確認Playwright和依賴版本
3. 檢查網絡連接和頁面狀態

