# Mac端TRAE功能測試指南

## 🚀 **快速開始**

### **1. 下載測試腳本**
```bash
# 在Mac終端執行
curl -o mac_trae_tester.py https://raw.githubusercontent.com/your-repo/mac_trae_tester.py

# 或者手動下載文件到Mac
```

### **2. 運行測試**
```bash
# 在Mac終端執行
python3 mac_trae_tester.py
```

## 📋 **測試內容**

### **環境檢查**
- ✅ Node.js版本檢查
- ✅ npm版本檢查  
- ✅ Python3版本檢查
- ✅ TRAE目錄檢查

### **命令查找**
自動搜索以下位置的TRAE命令：
- `/Users/alexchuang/aiengine/trae/git`
- `/Users/alexchuang/aiengine/trae`
- `/usr/local/bin`
- `/opt/homebrew/bin`
- `~/.npm-global/bin`
- `~/node_modules/.bin`

### **功能測試**
- 🚀 **TRAE-send測試** - 嘗試多種發送方法
- 🔄 **TRAE-sync測試** - 嘗試多種同步方法

## 🔧 **測試方法**

### **TRAE-send測試方法**
1. `trae-send` 直接命令
2. `send_message.py` Python腳本
3. `trae send` 子命令

### **TRAE-sync測試方法**
1. `trae-sync` 直接命令
2. `sync_repositories.py` Python腳本  
3. `trae sync` 子命令

## 📊 **測試輸出**

### **成功示例**
```
✅ 找到: trae-send -> /Users/alexchuang/aiengine/trae/git/trae-send
✅ TRAE-send測試成功！
📄 輸出: Message sent successfully
```

### **失敗示例**
```
❌ 未找到可用的TRAE-send方法
💡 請檢查TRAE是否正確安裝
```

## 🎯 **預期結果**

### **如果TRAE已正確安裝**
- 找到TRAE命令路徑
- 成功執行TRAE-send
- 成功執行TRAE-sync
- 生成詳細測試報告

### **如果TRAE未安裝或配置錯誤**
- 提供詳細的錯誤信息
- 指出缺失的組件
- 建議安裝步驟

## 🔍 **故障排除**

### **如果找不到TRAE命令**
```bash
# 手動查找TRAE
find /Users/alexchuang -name "*trae*" -type f 2>/dev/null

# 檢查npm全局包
npm list -g | grep trae

# 檢查PATH
echo $PATH
```

### **如果Python腳本執行失敗**
```bash
# 檢查Python版本
python3 --version

# 檢查腳本權限
chmod +x mac_trae_tester.py
```

## 📄 **測試報告**

測試完成後會生成：
- `mac_trae_test_results_[timestamp].json` - 詳細測試結果
- 控制台輸出 - 實時測試狀態

## 💡 **下一步**

根據測試結果：
1. **如果成功** - TRAE功能正常，可以集成到PowerAutomation
2. **如果失敗** - 需要安裝或配置TRAE環境
3. **部分成功** - 可以使用找到的功能，修復失敗的部分

## 🆘 **需要幫助？**

如果遇到問題，請提供：
1. 測試輸出的完整日誌
2. 生成的JSON測試報告
3. Mac系統版本和環境信息

