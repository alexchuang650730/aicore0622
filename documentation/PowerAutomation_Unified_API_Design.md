# PowerAutomation 統一API架構設計

## 概述

PowerAutomation統一API架構旨在提供一個標準化、一致性的接口系統，統一Manus和TRAE的調用方式，並為VSCode擴展和Manus網站提供統一的調用標準。

## 設計原則

### 1. 統一性原則
所有API接口遵循相同的請求/響應格式，無論底層調用的是Manus還是TRAE服務。

### 2. 可擴展性原則
API架構支持未來添加新的服務類型，而不需要修改現有的調用方式。

### 3. 簡化性原則
提供簡潔明了的API接口，讓curl、VSCode擴展和網站都能輕鬆調用。

## 統一API格式規範

### 基礎URL結構
```
/api/v1/powerautomation/{service}/{action}
```

其中：
- `service`: 服務類型 (manus, trae, unified)
- `action`: 操作類型 (send, sync, analyze, intervene等)

### 統一請求格式
```json
{
  "service": "manus|trae|unified",
  "action": "send|sync|analyze|intervene|connect|status",
  "payload": {
    "message": "消息內容",
    "repository": "倉庫名稱",
    "options": {
      "force": true,
      "timeout": 30
    }
  },
  "metadata": {
    "client": "vscode|website|curl",
    "version": "1.0.0",
    "timestamp": "2025-06-22T14:30:00Z"
  }
}
```

### 統一響應格式
```json
{
  "success": true,
  "service": "manus|trae|unified",
  "action": "send|sync|analyze|intervene",
  "data": {
    "result": "操作結果",
    "details": "詳細信息"
  },
  "metadata": {
    "execution_time": 1.23,
    "timestamp": "2025-06-22T14:30:00Z",
    "request_id": "req_12345"
  },
  "error": null
}
```

## API端點設計

### 1. 統一消息發送
```
POST /api/v1/powerautomation/unified/send
```

### 2. 統一數據同步
```
POST /api/v1/powerautomation/unified/sync
```

### 3. 統一智能分析
```
POST /api/v1/powerautomation/unified/analyze
```

### 4. 統一智能介入
```
POST /api/v1/powerautomation/unified/intervene
```

### 5. 服務狀態檢查
```
GET /api/v1/powerautomation/unified/status
```

