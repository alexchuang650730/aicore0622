#!/usr/bin/env python3
"""
基於截圖OCR的Manus對話提取工具
不依賴DOM選擇器，直接從截圖中識別文字
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# 檢查依賴
try:
    from playwright.async_api import async_playwright
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
except ImportError as e:
    print(f"❌ 缺少依賴: {e}")
    print("請安裝: pip3 install playwright pytesseract pillow opencv-python")
    print("並安裝tesseract: brew install tesseract")
    exit(1)

@dataclass
class ConversationMessage:
    """對話消息"""
    content: str
    sender: str  # user, assistant, unknown
    confidence: float
    position: Dict[str, int]  # x, y, width, height
    timestamp: str

class ScreenshotOCRExtractor:
    """基於截圖OCR的提取器"""
    
    def __init__(self, url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.url = url
        self.playwright = None
        self.browser = None
        self.page = None
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # OCR配置
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?:;()[]{}"\'-/\\@#$%^&*+=<>|~`中文'
    
    async def initialize(self, headless=False):
        """初始化瀏覽器"""
        print("🚀 初始化瀏覽器...")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = await context.new_page()
            await self.page.goto(self.url, wait_until='networkidle')
            
            print("✅ 瀏覽器初始化完成")
            
            # 檢查是否需要登入
            await self._check_and_wait_for_login()
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            return False
    
    async def _check_and_wait_for_login(self):
        """檢查並等待登入"""
        login_indicators = [
            'input[type="password"]',
            '.login',
            '.signin',
            'button:has-text("登入")',
            'button:has-text("Login")'
        ]
        
        for indicator in login_indicators:
            try:
                element = await self.page.query_selector(indicator)
                if element and await element.is_visible():
                    print("🔐 檢測到需要登入")
                    print("請在瀏覽器中完成登入，然後按Enter繼續...")
                    input()
                    await asyncio.sleep(3)
                    return
            except:
                continue
    
    async def extract_conversations_by_screenshot(self) -> List[ConversationMessage]:
        """通過截圖提取對話"""
        print("📸 開始截圖OCR對話提取...")
        
        try:
            # 1. 滾動並截取多張圖片
            screenshots = await self._capture_scrolling_screenshots()
            
            # 2. 對每張截圖進行OCR
            all_messages = []
            for i, screenshot_path in enumerate(screenshots):
                print(f"🔍 處理截圖 {i+1}/{len(screenshots)}: {screenshot_path}")
                messages = await self._extract_text_from_screenshot(screenshot_path)
                all_messages.extend(messages)
            
            # 3. 去重和排序
            unique_messages = self._deduplicate_messages(all_messages)
            
            # 4. 智能分析和分類
            classified_messages = self._classify_messages(unique_messages)
            
            print(f"✅ 總共提取 {len(classified_messages)} 條對話")
            
            return classified_messages
            
        except Exception as e:
            print(f"❌ 截圖提取失敗: {e}")
            return []
    
    async def _capture_scrolling_screenshots(self) -> List[str]:
        """滾動截取多張截圖"""
        print("📜 滾動頁面並截圖...")
        
        screenshots = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 先滾動到頂部
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)
        
        # 獲取頁面高度
        page_height = await self.page.evaluate("document.body.scrollHeight")
        viewport_height = await self.page.evaluate("window.innerHeight")
        
        scroll_position = 0
        screenshot_count = 0
        
        while scroll_position < page_height:
            # 截圖
            screenshot_path = self.screenshots_dir / f"scroll_{timestamp}_{screenshot_count:03d}.png"
            await self.page.screenshot(path=str(screenshot_path))
            screenshots.append(str(screenshot_path))
            
            print(f"  📸 截圖 {screenshot_count + 1}: {screenshot_path.name}")
            
            # 滾動
            scroll_step = viewport_height * 0.8  # 80%重疊
            scroll_position += scroll_step
            await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
            await asyncio.sleep(1)
            
            screenshot_count += 1
            
            # 防止無限滾動
            if screenshot_count > 20:
                print("⚠️ 達到最大截圖數量限制")
                break
        
        print(f"✅ 完成滾動截圖，共 {len(screenshots)} 張")
        return screenshots
    
    async def _extract_text_from_screenshot(self, screenshot_path: str) -> List[Dict]:
        """從單張截圖提取文字"""
        try:
            # 1. 預處理圖片
            processed_image = self._preprocess_image(screenshot_path)
            
            # 2. OCR識別
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # 3. 提取文字塊
            text_blocks = self._extract_text_blocks(ocr_data)
            
            # 4. 過濾和清理
            filtered_blocks = self._filter_text_blocks(text_blocks)
            
            return filtered_blocks
            
        except Exception as e:
            print(f"❌ OCR處理失敗 {screenshot_path}: {e}")
            return []
    
    def _preprocess_image(self, image_path: str) -> Image.Image:
        """預處理圖片以提高OCR準確度"""
        # 使用PIL打開圖片
        image = Image.open(image_path)
        
        # 轉換為灰度
        image = image.convert('L')
        
        # 增強對比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 增強銳度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # 使用OpenCV進一步處理
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
        
        # 去噪
        cv_image = cv2.medianBlur(cv_image, 3)
        
        # 轉回PIL
        processed_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        
        return processed_image
    
    def _extract_text_blocks(self, ocr_data: Dict) -> List[Dict]:
        """從OCR數據提取文字塊"""
        text_blocks = []
        
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            confidence = int(ocr_data['conf'][i])
            text = ocr_data['text'][i].strip()
            
            # 過濾低信心度和空文字
            if confidence > 30 and text:
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                text_blocks.append({
                    'text': text,
                    'confidence': confidence,
                    'position': {'x': x, 'y': y, 'width': w, 'height': h}
                })
        
        return text_blocks
    
    def _filter_text_blocks(self, text_blocks: List[Dict]) -> List[Dict]:
        """過濾和清理文字塊"""
        filtered = []
        
        for block in text_blocks:
            text = block['text']
            
            # 過濾條件
            if (len(text) < 3 or  # 太短
                text.isdigit() or  # 純數字
                len(text) > 1000 or  # 太長
                text in ['|', '-', '_', '=', '+', '*']):  # 特殊符號
                continue
            
            # 清理文字
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            if cleaned_text:
                block['text'] = cleaned_text
                filtered.append(block)
        
        return filtered
    
    def _deduplicate_messages(self, all_messages: List[Dict]) -> List[Dict]:
        """去重消息"""
        seen_texts = set()
        unique_messages = []
        
        for msg in all_messages:
            text = msg['text']
            # 簡單的去重邏輯
            if text not in seen_texts and len(text) > 10:
                seen_texts.add(text)
                unique_messages.append(msg)
        
        return unique_messages
    
    def _classify_messages(self, messages: List[Dict]) -> List[ConversationMessage]:
        """分類和結構化消息"""
        classified = []
        
        for msg in messages:
            text = msg['text']
            
            # 判斷發送者
            sender = self._determine_sender(text)
            
            # 創建結構化消息
            conversation_msg = ConversationMessage(
                content=text,
                sender=sender,
                confidence=msg['confidence'] / 100.0,
                position=msg['position'],
                timestamp=datetime.now().isoformat()
            )
            
            classified.append(conversation_msg)
        
        return classified
    
    def _determine_sender(self, text: str) -> str:
        """判斷消息發送者"""
        text_lower = text.lower()
        
        # 用戶指示詞
        user_indicators = ['user:', '用戶:', 'human:', '我:', 'me:', 'question:', '問:']
        
        # AI指示詞
        ai_indicators = ['assistant:', 'ai:', 'bot:', 'manus:', '回覆:', 'answer:', '答:']
        
        for indicator in user_indicators:
            if indicator in text_lower:
                return 'user'
        
        for indicator in ai_indicators:
            if indicator in text_lower:
                return 'assistant'
        
        # 基於內容特徵判斷
        if any(word in text_lower for word in ['請', '幫', '如何', '什麼', '為什麼', '?', '？']):
            return 'user'
        elif any(word in text_lower for word in ['根據', '建議', '可以', '應該', '以下是']):
            return 'assistant'
        
        return 'unknown'
    
    async def save_results(self, messages: List[ConversationMessage], output_dir: str = "ocr_results"):
        """保存結果"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON格式
        json_file = output_path / f"conversations_ocr_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([{
                'content': msg.content,
                'sender': msg.sender,
                'confidence': msg.confidence,
                'position': msg.position,
                'timestamp': msg.timestamp
            } for msg in messages], f, ensure_ascii=False, indent=2)
        
        # 保存可讀格式
        txt_file = output_path / f"conversations_readable_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Manus對話歷史 (OCR提取) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for i, msg in enumerate(messages, 1):
                f.write(f"[{i:03d}] {msg.sender.upper()} (信心度: {msg.confidence:.2f}):\n")
                f.write(f"{msg.content}\n")
                f.write(f"位置: x={msg.position['x']}, y={msg.position['y']}\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"💾 結果已保存:")
        print(f"  📄 JSON: {json_file}")
        print(f"  📋 文本: {txt_file}")
        
        return json_file, txt_file
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✅ 資源清理完成")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='基於截圖OCR的Manus對話提取工具')
    parser.add_argument('--url', default='https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ', help='Manus頁面URL')
    parser.add_argument('--headless', action='store_true', help='無頭模式')
    parser.add_argument('--output', default='ocr_results', help='輸出目錄')
    
    args = parser.parse_args()
    
    extractor = ScreenshotOCRExtractor(args.url)
    
    try:
        print("🚀 啟動基於截圖OCR的對話提取器...")
        
        # 初始化
        success = await extractor.initialize(headless=args.headless)
        if not success:
            return 1
        
        # 提取對話
        messages = await extractor.extract_conversations_by_screenshot()
        
        if messages:
            print(f"✅ 成功提取 {len(messages)} 條對話")
            
            # 顯示統計
            user_count = sum(1 for msg in messages if msg.sender == 'user')
            assistant_count = sum(1 for msg in messages if msg.sender == 'assistant')
            unknown_count = sum(1 for msg in messages if msg.sender == 'unknown')
            
            print(f"📊 統計:")
            print(f"  👤 用戶消息: {user_count}")
            print(f"  🤖 助手回覆: {assistant_count}")
            print(f"  ❓ 未知類型: {unknown_count}")
            
            # 顯示示例
            print(f"\n📋 消息示例:")
            for i, msg in enumerate(messages[:3]):
                print(f"  {i+1}. [{msg.sender}] {msg.content[:80]}...")
            
            # 保存結果
            await extractor.save_results(messages, args.output)
        else:
            print("❌ 沒有提取到對話")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 用戶中斷")
        return 0
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return 1
    finally:
        await extractor.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

