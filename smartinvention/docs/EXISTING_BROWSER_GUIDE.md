# 連接現有瀏覽器的使用指南

## 🎯 解決認證問題

這個工具可以連接到您已經打開並登入的瀏覽器，避免重複認證。

## 🚀 使用方法

### 方法1：連接現有瀏覽器

如果您已經有Chrome瀏覽器打開並登入了Manus：

```bash
# 直接嘗試連接
python3 existing_browser_connector.py --action interactive
```

### 方法2：啟動帶調試端口的Chrome

如果連接失敗，可以啟動一個帶調試端口的Chrome：

```bash
# 啟動Chrome並開啟調試端口
python3 existing_browser_connector.py --start-chrome

# 然後連接
python3 existing_browser_connector.py --action interactive
```

### 方法3：手動啟動Chrome

您也可以手動啟動Chrome：

```bash
# 在終端中執行
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --no-first-run \
  https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ
```

然後運行腳本：
```bash
python3 existing_browser_connector.py --action interactive
```

## 📋 交互模式命令

- `1` - 提取對話歷史
- `2` - 發送消息  
- `3` - 頁面截圖
- `4` - 檢查頁面信息
- `q` - 退出

## 💡 優勢

1. **保持登入狀態** - 不需要重複認證
2. **使用現有會話** - 保持所有cookies和狀態
3. **更快啟動** - 直接連接，無需重新加載
4. **靈活操作** - 可以在腳本和手動操作間切換

## 🔧 故障排除

### 連接失敗
```bash
# 檢查Chrome是否在運行
ps aux | grep chrome

# 檢查調試端口是否開啟
lsof -i :9222
```

### 找不到頁面
確保Chrome中已經打開了Manus頁面，或者腳本會自動導航到正確的URL。

### 權限問題
確保腳本有權限連接到Chrome的調試端口。

## 🎮 使用示例

```bash
# 啟動並連接
python3 existing_browser_connector.py --start-chrome

# 發送消息
python3 existing_browser_connector.py --action send --message "測試消息"

# 提取對話
python3 existing_browser_connector.py --action conversations

# 截圖
python3 existing_browser_connector.py --action screenshot
```

這樣您就可以避免每次都要重新認證了！

