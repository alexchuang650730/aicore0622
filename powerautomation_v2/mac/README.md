# Mac端組件 - PowerAutomation

Mac端負責監控TRAE對話、提取數據並與EC2端同步。

## 📁 組件結構

### 🎯 **核心操作器**
- `mac_manus_operator.py` - 主要Manus操作工具
- `manus_playwright_operator.py` - Playwright自動化操作
- `manus_debugger.py` - Manus調試工具
- `ec2_to_mac_operator.py` - EC2到Mac的數據同步

### 🔗 **瀏覽器連接器**
- `existing_browser_connector.py` - 連接現有瀏覽器
- `true_existing_browser.py` - 真實瀏覽器操作

### 📊 **數據提取器**
- `gemini_vision_extractor.py` - Gemini視覺分析
- `improved_gemini_analyzer.py` - 增強版Gemini分析
- `screenshot_ocr_extractor.py` - OCR文字識別
- `fixed_screenshot_ocr.py` - 修正版OCR提取器

### 🔧 **VSCode擴展**
- `powerautomation-vscode-extension/` - 完整VSCode擴展
- `powerautomation-1.0.0.vsix` - 可安裝的擴展包

## 🚀 使用方法

### 1. 安裝VSCode擴展
```bash
cd powerautomation-vscode-extension
code --install-extension powerautomation-1.0.0.vsix
```

### 2. 使用命令行工具
```bash
# 交互式操作
python3 mac_manus_operator.py --action interactive

# 連接現有瀏覽器
python3 existing_browser_connector.py

# 視覺分析
python3 gemini_vision_extractor.py
```

### 3. 自動化操作
```bash
# Playwright自動化
python3 manus_playwright_operator.py --url "https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"

# 調試模式
python3 manus_debugger.py --debug
```

## 📋 功能特色

### ✅ **已驗證功能**
- 🔍 TRAE對話監控
- 📸 截圖和OCR識別
- 🧠 Gemini視覺分析
- 🔄 與EC2端數據同步
- 🎯 Manus自動化操作

### 🎯 **核心能力**
- **實時監控** - 監控TRAE對話狀態
- **智能提取** - 提取對話內容和上下文
- **視覺分析** - 理解界面狀態和內容
- **自動操作** - 自動發送回覆到Manus
- **數據同步** - 與EC2端實時同步

## 🔧 配置說明

### 環境變量
```bash
export TRAE_DB_PATH="/Users/alexchuang/trae/conversations.db"
export EC2_ENDPOINT="http://18.212.97.173:8000"
export MANUS_URL="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"
```

### 依賴安裝
```bash
pip install playwright beautifulsoup4 requests pillow
playwright install
```

## 📊 使用示例

### 監控TRAE對話
```python
from mac_manus_operator import ManusOperator

operator = ManusOperator()
operator.start_monitoring()
```

### 提取對話數據
```python
from gemini_vision_extractor import GeminiExtractor

extractor = GeminiExtractor()
result = extractor.analyze_screenshot("screenshot.png")
```

### 同步到EC2
```python
from ec2_to_mac_operator import EC2Sync

sync = EC2Sync()
sync.upload_conversation_data(data)
```

