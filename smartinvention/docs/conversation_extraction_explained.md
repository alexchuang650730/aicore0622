# Manus對話歷史提取流程詳解

## 完整提取流程

### 1. 入口函數：`extract_conversation_history()`

```python
async def extract_conversation_history(self) -> List[ConversationMessage]:
    """提取對話歷史 - 主入口函數"""
    
    # 步驟1：滾動加載所有內容
    await self._scroll_to_load_all_content()
    
    # 步驟2：查找所有消息元素
    messages = await self._find_all_messages()
    
    return messages
```

### 2. 滾動加載：`_scroll_to_load_all_content()`

```python
async def _scroll_to_load_all_content(self):
    """滾動頁面，確保加載所有對話內容"""
    
    # 滾動到頂部
    await self.page.evaluate("window.scrollTo(0, 0)")
    
    # 持續滾動到底部，直到沒有新內容
    while scroll_attempts < max_attempts:
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # 點擊"載入更多"按鈕（如果存在）
        load_more_button = await self._find_element(self.selectors['load_more_button'])
        if load_more_button:
            await load_more_button.click()
```

### 3. 查找消息：`_find_all_messages()`

```python
async def _find_all_messages(self) -> List[ConversationMessage]:
    """從DOM中查找所有消息元素"""
    
    # 使用多個選擇器查找消息容器
    message_elements = await self._find_elements(self.selectors['message_item'])
    
    # 對每個消息元素進行解析
    for i, element in enumerate(message_elements):
        message = await self._parse_message_element(element, i)
        if message:
            messages.append(message)
```

### 4. 解析單個消息：`_parse_message_element()`

這是核心函數，從DOM元素中提取對話數據：

```python
async def _parse_message_element(self, element, index: int) -> Optional[ConversationMessage]:
    """從DOM元素中解析出對話消息"""
    
    # 提取消息內容
    content = await self._extract_text_from_element(element, self.selectors['message_content'])
    
    # 提取發送者信息
    sender = await self._extract_text_from_element(element, self.selectors['message_sender'])
    
    # 提取時間戳
    timestamp = await self._extract_timestamp_from_element(element)
    
    # 提取附件
    attachments = await self._extract_attachments_from_element(element)
    
    return ConversationMessage(...)
```

## 數據來源：DOM元素

### Manus頁面的HTML結構（推測）

```html
<!-- 對話容器 -->
<div class="conversation-container">
  <div class="message-list">
    
    <!-- 用戶消息 -->
    <div class="message user-message">
      <div class="message-sender">User</div>
      <div class="message-content">用戶的問題內容</div>
      <div class="message-timestamp" data-time="2023-12-22T14:30:22">2分鐘前</div>
    </div>
    
    <!-- AI回覆 -->
    <div class="message assistant-message">
      <div class="message-sender">Assistant</div>
      <div class="message-content">AI的回覆內容</div>
      <div class="message-timestamp" data-time="2023-12-22T14:32:15">剛剛</div>
      <div class="attachments">
        <img src="image.jpg" />
        <a href="link.html">相關鏈接</a>
      </div>
    </div>
    
  </div>
</div>
```

## 選擇器配置

系統使用多組選擇器來適應不同的頁面結構：

```python
self.selectors = {
    'message_item': [
        '.message',           # 標準消息類
        '.chat-message',      # 聊天消息類
        '.conversation-message', # 對話消息類
        '[data-testid="message"]', # 測試ID
        '.msg',              # 簡短消息類
        '.message-item'      # 消息項目類
    ],
    'message_content': [
        '.message-content',   # 消息內容
        '.message-text',      # 消息文本
        '.content',          # 內容
        '.text',             # 文本
        'p',                 # 段落標籤
        '.message-body'      # 消息主體
    ],
    'message_sender': [
        '.sender',           # 發送者
        '.author',           # 作者
        '.user',             # 用戶
        '.message-sender',   # 消息發送者
        '[data-sender]',     # 發送者屬性
        '.message-author'    # 消息作者
    ]
}
```

## 具體提取過程

### 1. 內容提取：`_extract_text_from_element()`

```python
async def _extract_text_from_element(self, element, selectors: List[str]) -> Optional[str]:
    """從元素中提取文本內容"""
    
    # 嘗試每個選擇器
    for selector in selectors:
        try:
            sub_element = await element.query_selector(selector)
            if sub_element:
                text = await sub_element.inner_text()  # 獲取純文本
                if text and text.strip():
                    return text.strip()
        except:
            continue
    
    # 如果都沒找到，返回整個元素的文本
    return await element.inner_text()
```

### 2. 發送者識別

```python
# 方法1：從專門的發送者元素提取
sender = await self._extract_text_from_element(element, self.selectors['message_sender'])

# 方法2：從CSS類名判斷
if not sender:
    class_name = await element.get_attribute('class') or ""
    if 'user' in class_name.lower():
        sender = 'user'
    elif 'assistant' in class_name.lower():
        sender = 'assistant'
```

### 3. 時間戳解析

```python
async def _extract_timestamp_from_element(self, element) -> datetime:
    """提取時間戳"""
    
    # 從時間元素的屬性獲取
    for attr in ['datetime', 'data-time', 'title', 'data-timestamp']:
        time_str = await time_element.get_attribute(attr)
        if time_str:
            return self._parse_timestamp(time_str)
    
    # 從文本內容解析相對時間
    text = await time_element.inner_text()  # "2分鐘前"
    if "分鐘前" in text:
        minutes = int(re.search(r'(\d+)', text).group(1))
        return datetime.now() - timedelta(minutes=minutes)
```

### 4. 附件提取

```python
async def _extract_attachments_from_element(self, element) -> List[str]:
    """提取附件"""
    
    attachments = []
    
    # 提取圖片
    images = await element.query_selector_all('img')
    for img in images:
        src = await img.get_attribute('src')
        if src:
            attachments.append(f"image:{src}")
    
    # 提取鏈接
    links = await element.query_selector_all('a[href]')
    for link in links:
        href = await link.get_attribute('href')
        if href:
            attachments.append(f"link:{href}")
    
    return attachments
```

## 數據流向圖

```
Manus網頁 (DOM)
    ↓
滾動加載所有內容
    ↓
查找消息元素 (.message, .chat-message, etc.)
    ↓
遍歷每個消息元素
    ↓
提取內容 (.message-content, .text, p)
    ↓
提取發送者 (.sender, .author, CSS類名)
    ↓
提取時間戳 (.timestamp, data-time屬性)
    ↓
提取附件 (img, a[href], .file)
    ↓
組裝成 ConversationMessage 對象
    ↓
返回對話歷史列表
```

## 實際使用示例

```python
# 初始化操作器
operator = ManusPlaywrightOperator("https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ")
await operator.initialize()

# 提取對話歷史
conversations = await operator.extract_conversation_history()

# 查看提取結果
for conv in conversations:
    print(f"[{conv.timestamp}] {conv.sender}: {conv.content}")
    if conv.attachments:
        print(f"  附件: {conv.attachments}")
```

## 故障排除

### 如果提取不到對話：

1. **檢查選擇器**：頁面結構可能與預期不同
2. **確認登入狀態**：未登入可能看不到對話
3. **等待加載完成**：對話可能還在加載中
4. **檢查網絡**：確保頁面完全載入

### 調試方法：

```python
# 查看頁面HTML結構
html_content = await operator.page.content()
print(html_content)

# 查看找到的元素數量
message_elements = await operator._find_elements(operator.selectors['message_item'])
print(f"找到 {len(message_elements)} 個消息元素")

# 手動測試選擇器
test_element = await operator.page.query_selector('.message')
if test_element:
    print("找到測試元素")
    print(await test_element.inner_html())
```

這就是 `_parse_message_element` 獲取對話歷史的完整流程！

