#!/usr/bin/env python3
"""
連接現有瀏覽器的Manus操作工具
避免重複認證，保持登入狀態
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
from playwright.async_api import async_playwright

class ExistingBrowserConnector:
    """連接現有瀏覽器的操作器"""
    
    def __init__(self, manus_url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.manus_url = manus_url
        self.playwright = None
        self.browser = None
        self.page = None
        self.debug_port = 9222
    
    async def connect_to_existing_browser(self):
        """連接到現有瀏覽器"""
        print("🔗 嘗試連接到現有瀏覽器...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # 嘗試連接到現有的Chrome實例
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    f"http://localhost:{self.debug_port}"
                )
                print("✅ 成功連接到現有瀏覽器")
                
                # 獲取現有頁面或創建新頁面
                contexts = self.browser.contexts
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    if pages:
                        # 查找Manus頁面
                        for page in pages:
                            if "manus.im" in page.url:
                                self.page = page
                                print(f"✅ 找到Manus頁面: {page.url}")
                                break
                        
                        if not self.page:
                            self.page = pages[0]  # 使用第一個頁面
                            print(f"📄 使用現有頁面: {self.page.url}")
                    else:
                        self.page = await context.new_page()
                        await self.page.goto(self.manus_url)
                        print("📄 創建新頁面並導航到Manus")
                else:
                    context = await self.browser.new_context()
                    self.page = await context.new_page()
                    await self.page.goto(self.manus_url)
                    print("📄 創建新上下文和頁面")
                
                return True
                
            except Exception as e:
                print(f"❌ 連接現有瀏覽器失敗: {e}")
                print("🚀 將啟動新的瀏覽器實例...")
                return await self._start_new_browser_with_debug()
                
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            return False
    
    async def _start_new_browser_with_debug(self):
        """啟動帶調試端口的新瀏覽器"""
        try:
            # 啟動帶調試端口的瀏覽器
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    f'--remote-debugging-port={self.debug_port}',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = await context.new_page()
            await self.page.goto(self.manus_url, wait_until='networkidle')
            
            print("✅ 啟動新瀏覽器成功")
            print(f"🔧 調試端口: {self.debug_port}")
            print("💡 下次可以直接連接到這個瀏覽器實例")
            
            return True
            
        except Exception as e:
            print(f"❌ 啟動新瀏覽器失敗: {e}")
            return False
    
    def start_chrome_with_debug(self):
        """手動啟動Chrome並開啟調試端口"""
        print("🚀 啟動Chrome瀏覽器並開啟調試端口...")
        
        chrome_commands = [
            # macOS Chrome路徑
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            # 可能的其他路徑
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            'google-chrome',
            'chromium'
        ]
        
        for chrome_path in chrome_commands:
            try:
                cmd = [
                    chrome_path,
                    f'--remote-debugging-port={self.debug_port}',
                    '--no-first-run',
                    '--no-default-browser-check',
                    self.manus_url
                ]
                
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ Chrome已啟動: {chrome_path}")
                print(f"🔧 調試端口: {self.debug_port}")
                print(f"🌐 已打開: {self.manus_url}")
                print("⏳ 請等待幾秒鐘讓瀏覽器完全啟動...")
                time.sleep(5)
                return True
                
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"❌ 啟動失敗 {chrome_path}: {e}")
                continue
        
        print("❌ 找不到Chrome瀏覽器")
        return False
    
    async def extract_conversations_simple(self):
        """簡化的對話提取"""
        print("📜 提取對話歷史...")
        
        try:
            # 等待頁面加載
            await asyncio.sleep(3)
            
            # 嘗試多種選擇器
            selectors_to_try = [
                'div[role="listitem"]',
                '.message',
                '.chat-message', 
                '[class*="message"]',
                '[class*="chat"]',
                'p',
                'div p',
                '.content',
                '.text'
            ]
            
            all_messages = []
            
            for selector in selectors_to_try:
                try:
                    elements = await self.page.query_selector_all(selector)
                    messages_found = 0
                    
                    for element in elements:
                        try:
                            if await element.is_visible():
                                text = await element.inner_text()
                                if text and len(text.strip()) > 10:  # 過濾短文本
                                    all_messages.append({
                                        'selector': selector,
                                        'text': text.strip(),
                                        'length': len(text)
                                    })
                                    messages_found += 1
                        except:
                            continue
                    
                    if messages_found > 0:
                        print(f"  ✅ {selector}: 找到 {messages_found} 條消息")
                    
                except Exception as e:
                    print(f"  ❌ {selector}: {e}")
                    continue
            
            # 去重並排序
            unique_messages = []
            seen_texts = set()
            
            for msg in all_messages:
                if msg['text'] not in seen_texts:
                    unique_messages.append(msg)
                    seen_texts.add(msg['text'])
            
            print(f"✅ 總共找到 {len(unique_messages)} 條唯一消息")
            
            # 顯示示例
            if unique_messages:
                print("\n📋 消息示例:")
                for i, msg in enumerate(unique_messages[:5]):
                    print(f"  {i+1}. [{msg['selector']}] {msg['text'][:80]}...")
            
            return unique_messages
            
        except Exception as e:
            print(f"❌ 提取對話失敗: {e}")
            return []
    
    async def send_message_simple(self, message):
        """簡化的發送消息"""
        print(f"📤 發送消息: {message[:50]}...")
        
        try:
            # 查找輸入框
            input_selectors = [
                'textarea',
                'input[type="text"]',
                '[contenteditable="true"]',
                '.input',
                '.message-input',
                '[placeholder*="輸入"]',
                '[placeholder*="input"]'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible() and await element.is_enabled():
                        input_element = element
                        print(f"  ✅ 找到輸入框: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                print("❌ 找不到輸入框")
                return False
            
            # 輸入消息
            await input_element.fill("")
            await asyncio.sleep(0.5)
            await input_element.fill(message)
            await asyncio.sleep(1)
            
            # 查找發送按鈕
            button_selectors = [
                'button[type="submit"]',
                '.send-button',
                '.send',
                'button:has-text("發送")',
                'button:has-text("Send")',
                '[aria-label*="send"]'
            ]
            
            button_found = False
            for selector in button_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button and await button.is_visible() and await button.is_enabled():
                        await button.click()
                        print(f"  ✅ 點擊發送按鈕: {selector}")
                        button_found = True
                        break
                except:
                    continue
            
            if not button_found:
                # 嘗試按Enter
                await input_element.press('Enter')
                print("  ✅ 按下Enter鍵")
            
            await asyncio.sleep(3)
            print("✅ 消息發送完成")
            return True
            
        except Exception as e:
            print(f"❌ 發送消息失敗: {e}")
            return False
    
    async def take_screenshot(self, filename=None):
        """截圖"""
        if not filename:
            filename = f"manus_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        try:
            await self.page.screenshot(path=filename, full_page=True)
            print(f"📸 截圖已保存: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 截圖失敗: {e}")
            return None
    
    async def cleanup(self):
        """清理（但不關閉瀏覽器）"""
        try:
            # 只清理playwright，不關閉瀏覽器
            if self.playwright:
                await self.playwright.stop()
            print("✅ 清理完成（瀏覽器保持打開）")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='連接現有瀏覽器的Manus操作工具')
    parser.add_argument('--action', choices=['connect', 'conversations', 'send', 'screenshot', 'interactive'],
                       default='interactive', help='要執行的操作')
    parser.add_argument('--message', help='要發送的消息')
    parser.add_argument('--start-chrome', action='store_true', help='啟動Chrome並開啟調試端口')
    
    args = parser.parse_args()
    
    connector = ExistingBrowserConnector()
    
    try:
        if args.start_chrome:
            # 手動啟動Chrome
            if connector.start_chrome_with_debug():
                print("⏳ 等待Chrome啟動完成...")
                await asyncio.sleep(5)
            else:
                print("❌ 啟動Chrome失敗")
                return 1
        
        # 連接到瀏覽器
        print("🔗 連接到瀏覽器...")
        success = await connector.connect_to_existing_browser()
        if not success:
            print("❌ 連接失敗")
            return 1
        
        print("✅ 連接成功")
        
        # 執行操作
        if args.action == 'conversations':
            await connector.extract_conversations_simple()
        
        elif args.action == 'send':
            if not args.message:
                message = input("請輸入要發送的消息: ")
            else:
                message = args.message
            await connector.send_message_simple(message)
        
        elif args.action == 'screenshot':
            await connector.take_screenshot()
        
        elif args.action == 'interactive':
            await interactive_mode(connector)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 用戶中斷")
        return 0
    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        return 1
    finally:
        await connector.cleanup()

async def interactive_mode(connector):
    """交互模式"""
    print("\n" + "="*50)
    print("🎮 連接現有瀏覽器 - 交互模式")
    print("="*50)
    print("可用命令:")
    print("  1 - 提取對話歷史")
    print("  2 - 發送消息")
    print("  3 - 頁面截圖")
    print("  4 - 檢查頁面信息")
    print("  q - 退出")
    print("="*50)
    
    while True:
        try:
            command = input("\n請輸入命令 (1-4, q): ").strip()
            
            if command == 'q':
                print("👋 退出交互模式")
                break
            elif command == '1':
                await connector.extract_conversations_simple()
            elif command == '2':
                message = input("請輸入要發送的消息: ").strip()
                if message:
                    await connector.send_message_simple(message)
                else:
                    print("❌ 消息不能為空")
            elif command == '3':
                await connector.take_screenshot()
            elif command == '4':
                try:
                    title = await connector.page.title()
                    url = connector.page.url
                    print(f"📄 頁面標題: {title}")
                    print(f"🌐 當前URL: {url}")
                except Exception as e:
                    print(f"❌ 獲取頁面信息失敗: {e}")
            else:
                print("❌ 無效命令")
        
        except KeyboardInterrupt:
            print("\n👋 用戶中斷")
            break
        except Exception as e:
            print(f"❌ 執行命令錯誤: {e}")

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

