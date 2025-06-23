#!/usr/bin/env python3
"""
Gemini Vision 對話提取工具
使用Google Gemini API識別截圖中的繁體中文對話
"""

import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

try:
    from playwright.async_api import async_playwright
    from google import genai
except ImportError as e:
    print(f"❌ 缺少依賴: {e}")
    print("請安裝: pip3 install playwright google-genai")
    exit(1)

@dataclass
class ConversationMessage:
    content: str
    sender: str
    timestamp: str
    confidence: float = 0.9

class GeminiVisionExtractor:
    def __init__(self, api_key="AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw", url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.api_key = api_key
        self.url = url
        self.client = genai.Client(api_key=api_key)
        self.playwright = None
        self.browser = None
        self.page = None
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def initialize(self, headless=False):
        """初始化瀏覽器"""
        print("🚀 初始化瀏覽器...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        context = await self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        self.page = await context.new_page()
        await self.page.goto(self.url, wait_until='networkidle')
        
        print("🔐 請在瀏覽器中登入，完成後按Enter...")
        input()
        await asyncio.sleep(3)
        return True
    
    async def extract_conversations(self):
        """提取對話"""
        print("📸 開始截圖並用Gemini分析...")
        
        # 滾動截圖
        screenshots = await self._capture_screenshots()
        
        # 用Gemini分析每張截圖
        all_conversations = []
        for i, screenshot_path in enumerate(screenshots):
            print(f"🔍 Gemini分析截圖 {i+1}/{len(screenshots)}")
            conversations = await self._analyze_with_gemini(screenshot_path)
            all_conversations.extend(conversations)
        
        # 去重
        unique_conversations = self._deduplicate(all_conversations)
        print(f"✅ 提取到 {len(unique_conversations)} 條對話")
        
        return unique_conversations
    
    async def _capture_screenshots(self):
        """截圖"""
        screenshots = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)
        
        page_height = await self.page.evaluate("document.body.scrollHeight")
        viewport_height = await self.page.evaluate("window.innerHeight")
        
        scroll_position = 0
        count = 0
        
        while scroll_position < page_height and count < 10:
            screenshot_path = self.screenshots_dir / f"gemini_{timestamp}_{count:03d}.png"
            await self.page.screenshot(path=str(screenshot_path))
            screenshots.append(str(screenshot_path))
            
            scroll_position += viewport_height * 0.8
            await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await asyncio.sleep(1)
            count += 1
        
        return screenshots
    
    async def _analyze_with_gemini(self, image_path):
        """用Gemini分析截圖"""
        try:
            # 讀取圖片
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Gemini提示詞
            prompt = """
請分析這張Manus對話截圖，提取所有對話內容。

要求：
1. 識別用戶問題和AI回覆
2. 保持原始繁體中文
3. 按時間順序排列
4. 格式：[用戶/AI]: 對話內容

請只返回對話內容，不要其他說明。
"""
            
            # 調用Gemini
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    prompt,
                    {"mime_type": "image/png", "data": image_data}
                ]
            )
            
            # 解析回應
            conversations = self._parse_gemini_response(response.text)
            return conversations
            
        except Exception as e:
            print(f"❌ Gemini分析失敗: {e}")
            return []
    
    def _parse_gemini_response(self, text):
        """解析Gemini回應"""
        conversations = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 解析格式 [用戶/AI]: 內容
            if line.startswith('[用戶]') or line.startswith('[USER]'):
                content = line.split(':', 1)[1].strip() if ':' in line else line
                conversations.append(ConversationMessage(
                    content=content,
                    sender='user',
                    timestamp=datetime.now().isoformat()
                ))
            elif line.startswith('[AI]') or line.startswith('[助手]') or line.startswith('[ASSISTANT]'):
                content = line.split(':', 1)[1].strip() if ':' in line else line
                conversations.append(ConversationMessage(
                    content=content,
                    sender='assistant',
                    timestamp=datetime.now().isoformat()
                ))
            elif len(line) > 10:  # 其他長文本
                conversations.append(ConversationMessage(
                    content=line,
                    sender='unknown',
                    timestamp=datetime.now().isoformat()
                ))
        
        return conversations
    
    def _deduplicate(self, conversations):
        """去重"""
        seen = set()
        unique = []
        
        for conv in conversations:
            if conv.content not in seen:
                seen.add(conv.content)
                unique.append(conv)
        
        return unique
    
    async def save_results(self, conversations, output_dir="gemini_results"):
        """保存結果"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON格式
        json_file = output_path / f"conversations_gemini_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([{
                'content': conv.content,
                'sender': conv.sender,
                'timestamp': conv.timestamp,
                'confidence': conv.confidence
            } for conv in conversations], f, ensure_ascii=False, indent=2)
        
        # 可讀格式
        txt_file = output_path / f"conversations_readable_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Manus對話歷史 (Gemini提取) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for i, conv in enumerate(conversations, 1):
                f.write(f"[{i:03d}] {conv.sender.upper()}:\n")
                f.write(f"{conv.content}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"💾 結果已保存:")
        print(f"  📄 JSON: {json_file}")
        print(f"  📋 文本: {txt_file}")
        
        return json_file, txt_file
    
    async def cleanup(self):
        """清理"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    extractor = GeminiVisionExtractor()
    
    try:
        await extractor.initialize()
        conversations = await extractor.extract_conversations()
        
        if conversations:
            user_count = sum(1 for c in conversations if c.sender == 'user')
            ai_count = sum(1 for c in conversations if c.sender == 'assistant')
            
            print(f"📊 統計: 用戶 {user_count}, AI {ai_count}")
            
            for i, conv in enumerate(conversations[:3]):
                print(f"{i+1}. [{conv.sender}] {conv.content[:50]}...")
            
            await extractor.save_results(conversations)
        else:
            print("❌ 沒有提取到對話")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        await extractor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

