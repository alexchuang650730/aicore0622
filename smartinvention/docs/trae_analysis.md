# TRAE工具分析

## trae-history 關鍵信息

從GitHub代碼可以看到：

1. **SSH連接配置**：
   - host: serveo.net
   - port: 41269
   - user: alexchuang
   - password: 123456

2. **TRAE數據庫路徑**：
   `/Users/alexchuang/Library/Application Support/Trae/User/workspaceStorage/f002a9b85f221075092022809f5a075f/state.vscdb`

3. **SQL查詢方式**：
   ```sql
   SELECT key, value FROM ItemTable
   WHERE key LIKE '%input-history%' OR key LIKE '%memento%'
   ORDER BY key;
   ```

4. **SSH執行方式**：
   通過SSH連接到Mac，然後使用sqlite3直接查詢TRAE的數據庫文件

5. **數據存儲路徑**：
   `/home/alexchuang/aiengine/trae/git/<倉庫名>/history/`

這說明TRAE沒有API，需要通過SSH連接到Mac，直接訪問SQLite數據庫文件來提取對話歷史和發送消息。

