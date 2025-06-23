#!/usr/bin/env python3
"""
修復版本的截圖OCR對話提取工具
解決OCR配置和登入問題
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
    exit(1)

@dataclass
class ConversationMessage:
    """對話消息"""
    content: str
    sender: str  # user, assistant, unknown
    confidence: float
    position: Dict[str, int]  # x, y, width, height
    timestamp: str

class FixedScreenshotOCRExtractor:
    """修復版本的截圖OCR提取器"""
    
    def __init__(self, url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.url = url
        self.playwright = None
        self.browser = None
        self.page = None
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # 修復OCR配置 - 移除有問題的字符白名單
        self.tesseract_config = '--oem 3 --psm 6'
    
    async def initialize(self, headless=False):
        """初始化瀏覽器"""
        print("🚀 初始化瀏覽器...")
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            self.page = await context.new_page()
            
            print(f"🌐 導航到: {self.url}")
            await self.page.goto(self.url, wait_until='networkidle', timeout=30000)
            
            print("✅ 瀏覽器初始化完成")
            
            # 改進的登入檢查
            await self._improved_login_check()
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            return False
    
    async def _improved_login_check(self):
        """改進的登入檢查"""
        print("🔐 檢查登入狀態...")
        
        # 等待頁面完全加載
        await asyncio.sleep(5)
        
        # 檢查多種登入指示器
        login_indicators = [
            'input[type="password"]',
            'input[type="email"]',
            '.login',
            '.signin',
            '.auth',
            'button:has-text("登入")',
            'button:has-text("Login")',
            'button:has-text("Sign in")',
            '[placeholder*="密碼"]',
            '[placeholder*="password"]',
            '[placeholder*="email"]'
        ]
        
        needs_login = False
        for indicator in login_indicators:
            try:
                element = await self.page.query_selector(indicator)
                if element and await element.is_visible():
                    needs_login = True
                    print(f"  🔍 發現登入元素: {indicator}")
                    break
            except:
                continue
        
        # 檢查頁面標題和URL
        title = await self.page.title()
        current_url = self.page.url
        
        if needs_login or 'login' in title.lower() or 'signin' in current_url.lower():
            print("⚠️ 需要登入")
            print("📋 請按照以下步驟操作:")
            print("  1. 在瀏覽器中完成登入")
            print("  2. 確保能看到對話頁面")
            print("  3. 按Enter繼續...")
            
            # 等待用戶登入
            input("按Enter繼續...")
            
            # 再次等待頁面穩定
            await asyncio.sleep(3)
            
            # 驗證登入成功
            new_title = await self.page.title()
            new_url = self.page.url
            print(f"✅ 當前頁面: {new_title}")
            print(f"🌐 當前URL: {new_url}")
        else:
            print("✅ 已登入或無需登入")
    
    async def extract_conversations_by_screenshot(self) -> List[ConversationMessage]:
        """通過截圖提取對話"""
        print("📸 開始截圖OCR對話提取...")
        
        try:
            # 1. 等待頁面穩定
            print("⏳ 等待頁面穩定...")
            await asyncio.sleep(3)
            
            # 2. 滾動並截取多張圖片
            screenshots = await self._capture_scrolling_screenshots()
            
            if not screenshots:
                print("❌ 沒有截取到圖片")
                return []
            
            # 3. 對每張截圖進行OCR
            all_messages = []
            for i, screenshot_path in enumerate(screenshots):
                print(f"🔍 處理截圖 {i+1}/{len(screenshots)}: {screenshot_path}")
                messages = await self._extract_text_from_screenshot_fixed(screenshot_path)
                all_messages.extend(messages)
            
            # 4. 去重和排序
            unique_messages = self._deduplicate_messages(all_messages)
            
            # 5. 智能分析和分類
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
        
        try:
            # 先滾動到頂部
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)
            
            # 獲取頁面高度
            page_height = await self.page.evaluate("document.body.scrollHeight")
            viewport_height = await self.page.evaluate("window.innerHeight")
            
            print(f"📏 頁面高度: {page_height}px, 視窗高度: {viewport_height}px")
            
            scroll_position = 0
            screenshot_count = 0
            
            while scroll_position < page_height:
                # 截圖
                screenshot_path = self.screenshots_dir / f"scroll_{timestamp}_{screenshot_count:03d}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=False)
                screenshots.append(str(screenshot_path))
                
                print(f"  📸 截圖 {screenshot_count + 1}: {screenshot_path.name}")
                
                # 滾動
                scroll_step = viewport_height * 0.7  # 70%重疊，確保不遺漏
                scroll_position += scroll_step
                await self.page.evaluate(f"window.scrollTo(0, {scroll_position})")
                await asyncio.sleep(1.5)  # 等待內容加載
                
                screenshot_count += 1
                
                # 防止無限滾動
                if screenshot_count > 15:
                    print("⚠️ 達到最大截圖數量限制")
                    break
            
            print(f"✅ 完成滾動截圖，共 {len(screenshots)} 張")
            return screenshots
            
        except Exception as e:
            print(f"❌ 滾動截圖失敗: {e}")
            return []
    
    async def _extract_text_from_screenshot_fixed(self, screenshot_path: str) -> List[Dict]:
        """修復版本的截圖文字提取"""
        try:
            # 1. 檢查文件是否存在
            if not os.path.exists(screenshot_path):
                print(f"❌ 截圖文件不存在: {screenshot_path}")
                return []
            
            # 2. 預處理圖片
            processed_image = self._preprocess_image_fixed(screenshot_path)
            
            # 3. 簡化的OCR識別
            try:
                # 使用簡化的配置
                text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
                
                if text.strip():
                    print(f"  ✅ OCR成功，提取文字長度: {len(text)}")
                    # 將整個文字作為一個塊處理
                    return [{
                        'text': text.strip(),
                        'confidence': 80,  # 默認信心度
                        'position': {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}
                    }]
                else:
                    print(f"  ⚠️ OCR未提取到文字")
                    return []
                    
            except Exception as ocr_error:
                print(f"  ❌ OCR識別失敗: {ocr_error}")
                
                # 嘗試更簡單的方法
                try:
                    simple_text = pytesseract.image_to_string(processed_image)
                    if simple_text.strip():
                        print(f"  ✅ 簡單OCR成功")
                        return [{
                            'text': simple_text.strip(),
                            'confidence': 70,
                            'position': {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}
                        }]
                except:
                    pass
                
                return []
            
        except Exception as e:
            print(f"❌ 處理截圖失敗 {screenshot_path}: {e}")
            return []
    
    def _preprocess_image_fixed(self, image_path: str) -> Image.Image:
        """修復版本的圖片預處理"""
        try:
            # 使用PIL打開圖片
            image = Image.open(image_path)
            
            # 轉換為RGB（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 轉換為灰度
            image = image.convert('L')
            
            # 適度增強對比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # 適度增強銳度
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            return image
            
        except Exception as e:
            print(f"❌ 圖片預處理失敗: {e}")
            # 返回原始圖片
            return Image.open(image_path)
    
    def _deduplicate_messages(self, all_messages: List[Dict]) -> List[Dict]:
        """去重消息"""
        if not all_messages:
            return []
        
        # 將所有文字合併
        all_text = ""
        for msg in all_messages:
            all_text += msg['text'] + "\n"
        
        # 按行分割並清理
        lines = []
        for line in all_text.split('\n'):
            cleaned_line = re.sub(r'\s+', ' ', line).strip()
            if cleaned_line and len(cleaned_line) > 5:  # 過濾太短的行
                lines.append(cleaned_line)
        
        # 去重
        unique_lines = []
        seen = set()
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append({
                    'text': line,
                    'confidence': 75,
                    'position': {'x': 0, 'y': 0, 'width': 1920, 'height': 50}
                })
        
        print(f"  📝 去重後剩餘 {len(unique_lines)} 行文字")
        return unique_lines
    
    def _classify_messages(self, messages: List[Dict]) -> List[ConversationMessage]:
        """分類和結構化消息"""
        classified = []
        
        for msg in messages:
            text = msg['text']
            
            # 過濾明顯不是對話的內容
            if self._is_conversation_text(text):
                sender = self._determine_sender(text)
                
                conversation_msg = ConversationMessage(
                    content=text,
                    sender=sender,
                    confidence=msg['confidence'] / 100.0,
                    position=msg['position'],
                    timestamp=datetime.now().isoformat()
                )
                
                classified.append(conversation_msg)
        
        return classified
    
    def _is_conversation_text(self, text: str) -> bool:
        """判斷是否是對話文字"""
        text_lower = text.lower()
        
        # 過濾掉明顯不是對話的內容
        filter_keywords = [
            'cookie', 'privacy', 'terms', 'policy', 'copyright',
            'navigation', 'menu', 'header', 'footer', 'sidebar',
            'advertisement', 'ad', 'sponsored', 'loading', 'error'
        ]
        
        for keyword in filter_keywords:
            if keyword in text_lower:
                return False
        
        # 檢查是否包含對話特徵
        conversation_indicators = [
            '?', '？', '請', '幫', '如何', '什麼', '為什麼',
            '謝謝', '感謝', '回覆', '回答', '建議', '可以',
            'user', 'assistant', 'ai', 'bot', 'human'
        ]
        
        for indicator in conversation_indicators:
            if indicator in text_lower:
                return True
        
        # 檢查長度（對話通常有一定長度）
        return 10 <= len(text) <= 2000
    
    def _determine_sender(self, text: str) -> str:
        """判斷消息發送者"""
        text_lower = text.lower()
        
        # 用戶指示詞
        user_indicators = ['user:', '用戶:', 'human:', '我:', 'me:', 'question:', '問:', '請問', '請幫']
        
        # AI指示詞
        ai_indicators = ['assistant:', 'ai:', 'bot:', 'manus:', '回覆:', 'answer:', '答:', '根據', '建議']
        
        for indicator in user_indicators:
            if indicator in text_lower:
                return 'user'
        
        for indicator in ai_indicators:
            if indicator in text_lower:
                return 'assistant'
        
        # 基於內容特徵判斷
        if any(word in text_lower for word in ['請', '幫', '如何', '什麼', '為什麼', '?', '？']):
            return 'user'
        elif any(word in text_lower for word in ['根據', '建議', '可以', '應該', '以下是', '首先', '其次']):
            return 'assistant'
        
        return 'unknown'
    
    async def save_results(self, messages: List[ConversationMessage], output_dir: str = "ocr_results"):
        """保存結果"""
        if not messages:
            print("❌ 沒有消息可保存")
            return None, None
        
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
    
    parser = argparse.ArgumentParser(description='修復版本的截圖OCR對話提取工具')
    parser.add_argument('--url', default='https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ', help='Manus頁面URL')
    parser.add_argument('--headless', action='store_true', help='無頭模式')
    parser.add_argument('--output', default='ocr_results', help='輸出目錄')
    
    args = parser.parse_args()
    
    extractor = FixedScreenshotOCRExtractor(args.url)
    
    try:
        print("🚀 啟動修復版本的截圖OCR對話提取器...")
        
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
            for i, msg in enumerate(messages[:5]):
                print(f"  {i+1}. [{msg.sender}] {msg.content[:80]}...")
            
            # 保存結果
            await extractor.save_results(messages, args.output)
        else:
            print("❌ 沒有提取到對話")
            print("💡 建議:")
            print("  1. 確保已正確登入Manus")
            print("  2. 確保頁面有對話內容")
            print("  3. 檢查截圖是否正確生成")
        
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

