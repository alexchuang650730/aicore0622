# TRAE測試工具集 - 完整指南

## 🎯 **概述**

這個目錄包含了完整的TRAE功能測試工具集，用於驗證和調試TRAE-send、TRAE-sync等功能。

## 📁 **文件結構**

```
tests/trae_testing/
├── mac_trae_tester.py          # Mac端TRAE功能綜合測試
├── correct_trae_tester.py      # 使用正確語法的TRAE測試
├── trae_send_debugger.py       # TRAE-send專用調試工具
├── trae_window_sender.py       # 測試發送到現有窗口
├── test_trae_local.py          # 本地模擬測試
└── README.md                   # 本文件
```

## 🚀 **快速開始**

### **1. 基本TRAE功能測試**
```bash
# 在Mac上運行
python3 mac_trae_tester.py
```

### **2. 使用正確語法測試**
```bash
# 測試 echo "message" | trae - 語法
python3 correct_trae_tester.py
```

### **3. 調試TRAE-send問題**
```bash
# 詳細調試TRAE-send命令
python3 trae_send_debugger.py /usr/local/bin/trae-send
```

## 🔍 **測試工具詳解**

### **mac_trae_tester.py**
**功能**: 全面的Mac端TRAE測試
- 自動查找TRAE命令
- 測試環境檢查
- 多種發送方法測試
- 生成詳細報告

**使用場景**: 初次設置或全面檢查TRAE功能

### **correct_trae_tester.py**
**功能**: 使用已驗證的正確語法測試
- 使用 `echo "message" | trae -` 語法
- 測試多種消息類型
- 模擬真實PowerAutomation場景
- 交互模式測試

**使用場景**: 驗證TRAE發送功能正常工作

### **trae_send_debugger.py**
**功能**: 專門調試TRAE-send問題
- 測試各種參數組合
- 檢查執行環境
- 詳細錯誤分析
- 幫助信息提取

**使用場景**: 當TRAE-send不工作時的深度調試

### **trae_window_sender.py**
**功能**: 嘗試發送到現有TRAE窗口
- 測試會話管理
- AppleScript集成
- API方法探索
- 文件通信測試

**使用場景**: 研究如何發送到特定TRAE窗口

### **test_trae_local.py**
**功能**: 本地模擬測試（不需要真實TRAE）
- 邏輯驗證
- 架構測試
- 離線開發
- 功能模擬

**使用場景**: 開發和測試PowerAutomation邏輯

## 📊 **測試結果解讀**

### **成功標誌**
- ✅ 返回碼為0
- ✅ 有標準輸出
- ✅ TRAE窗口顯示消息
- ✅ 無錯誤信息

### **失敗標誌**
- ❌ 返回碼非0
- ❌ 錯誤輸出
- ❌ 命令未找到
- ❌ 超時或異常

### **常見問題**
1. **命令未找到**: 檢查TRAE安裝路徑
2. **權限錯誤**: 檢查文件執行權限
3. **語法錯誤**: 使用正確的參數格式
4. **環境問題**: 檢查Node.js、npm等依賴

## 🎯 **已驗證的工作方法**

### **TRAE-send正確語法**
```bash
# ✅ 正確方法
echo "消息內容" | trae -

# ❌ 錯誤方法
trae send message
trae-send message
```

### **TRAE-sync正確語法**
```bash
# ✅ 正確方法
trae sync
```

## 🔧 **故障排除**

### **如果所有測試都失敗**
1. 檢查TRAE是否正確安裝
2. 確認命令路徑正確
3. 檢查系統環境
4. 查看TRAE文檔

### **如果部分測試成功**
1. 使用成功的方法
2. 分析失敗原因
3. 調整參數或環境
4. 重新測試

### **如果需要幫助**
1. 運行測試並保存日誌
2. 檢查生成的JSON報告
3. 提供系統環境信息
4. 描述具體錯誤現象

## 🚀 **集成到PowerAutomation**

測試成功後，可以將驗證的方法集成到PowerAutomation系統：

```python
# 在PowerAutomation中使用
def send_to_trae(message):
    command = f"echo '{message}' | trae -"
    result = subprocess.run(["sh", "-c", command], ...)
    return result
```

## 📝 **測試記錄**

### **最新測試結果** (2025-06-22)
- ✅ `echo "message" | trae -` 語法驗證成功
- ✅ TRAE會在新窗口顯示結果
- ✅ 消息發送和處理正常
- ❌ 發送到現有窗口的方法未找到

### **推薦工作流程**
1. 使用 `echo "message" | trae -` 發送智能回覆
2. TRAE在新窗口顯示建議
3. 用戶參考建議並手動應用
4. 系統記錄介入效果

## 🎉 **結論**

TRAE測試工具集提供了完整的測試和調試能力，確保PowerAutomation系統能夠可靠地與TRAE集成。通過這些工具，我們驗證了TRAE的核心功能並找到了可行的集成方案。

