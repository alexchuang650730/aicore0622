# 截圖OCR對話提取工具安裝指南

## 🎯 **優勢**

✅ **不依賴DOM選擇器** - 直接從截圖識別文字
✅ **適用於任何網頁** - 不受頁面結構變化影響  
✅ **高準確度** - 使用Tesseract OCR引擎
✅ **智能分類** - 自動區分用戶和AI消息
✅ **完整記錄** - 包含位置信息和信心度

## 📦 **安裝依賴**

### 1. Python依賴
```bash
pip3 install playwright pytesseract pillow opencv-python
```

### 2. 安裝Tesseract OCR
```bash
# macOS
brew install tesseract

# 或下載安裝包
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. 安裝Playwright瀏覽器
```bash
playwright install chromium
```

## 🚀 **使用方法**

### 基本使用
```bash
python3 screenshot_ocr_extractor.py
```

### 指定URL
```bash
python3 screenshot_ocr_extractor.py --url "https://manus.im/app/your-page-id"
```

### 無頭模式
```bash
python3 screenshot_ocr_extractor.py --headless
```

### 自定義輸出目錄
```bash
python3 screenshot_ocr_extractor.py --output my_results
```

## 📋 **工作流程**

1. **打開頁面** - 自動導航到Manus頁面
2. **等待登入** - 檢測登入狀態，需要時暫停等待
3. **滾動截圖** - 自動滾動頁面並截取多張圖片
4. **OCR識別** - 使用Tesseract識別每張圖片中的文字
5. **智能分析** - 分類消息類型（用戶/AI/未知）
6. **去重整理** - 移除重複內容，整理格式
7. **保存結果** - 輸出JSON和可讀文本格式

## 📊 **輸出格式**

### JSON格式 (`conversations_ocr_YYYYMMDD_HHMMSS.json`)
```json
[
  {
    "content": "消息內容",
    "sender": "user|assistant|unknown",
    "confidence": 0.95,
    "position": {"x": 100, "y": 200, "width": 300, "height": 50},
    "timestamp": "2024-01-01T12:00:00"
  }
]
```

### 可讀格式 (`conversations_readable_YYYYMMDD_HHMMSS.txt`)
```
[001] USER (信心度: 0.95):
這是用戶的問題
位置: x=100, y=200
----------------------------------------

[002] ASSISTANT (信心度: 0.92):
這是AI的回覆
位置: x=100, y=300
----------------------------------------
```

## 🔧 **故障排除**

### Tesseract未找到
```bash
# 檢查安裝
tesseract --version

# 設置路徑（如果需要）
export PATH="/usr/local/bin:$PATH"
```

### OCR識別率低
- 確保頁面字體清晰
- 調整瀏覽器縮放比例
- 檢查頁面對比度

### 記憶體不足
- 使用 `--headless` 模式
- 減少同時處理的截圖數量

## 💡 **使用技巧**

1. **登入後再運行** - 確保能看到完整對話
2. **調整瀏覽器大小** - 更大的視窗能捕獲更多內容
3. **等待頁面加載** - 確保所有內容都已載入
4. **檢查輸出** - 查看信心度，過濾低質量結果

這個工具完全不依賴頁面結構，只要能看到文字就能提取！

