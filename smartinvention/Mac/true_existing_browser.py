#!/usr/bin/env python3
"""
真正連接現有Chrome瀏覽器的工具
不會開啟新瀏覽器，只連接已存在的
"""

import asyncio
import json
import subprocess
import time
import requests
from datetime import datetime
from playwright.async_api import async_playwright

class TrueExistingBrowserConnector:
    """真正連接現有瀏覽器的連接器"""
    
    def __init__(self, debug_port=9222):
        self.debug_port = debug_port
        self.playwright = None
        self.browser = None
        self.page = None
        self.cdp_url = f"http://localhost:{debug_port}"
    
    def check_existing_chrome(self):
        """檢查是否有Chrome在運行並開啟了調試端口"""
        print("🔍 檢查現有Chrome瀏覽器...")
        
        try:
            # 檢查調試端口是否可用
            response = requests.get(f"{self.cdp_url}/json/version", timeout=3)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ 找到Chrome瀏覽器: {version_info.get('Browser', 'Unknown')}")
                return True
            else:
                print(f"❌ 調試端口 {self.debug_port} 無回應")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 無法連接到調試端口 {self.debug_port}: {e}")
            return False
    
    def get_existing_tabs(self):
        """獲取現有標籤頁"""
        try:
            response = requests.get(f"{self.cdp_url}/json", timeout=3)
            if response.status_code == 200:
                tabs = response.json()
                print(f"📋 找到 {len(tabs)} 個標籤頁:")
                
                manus_tabs = []
                for i, tab in enumerate(tabs):
                    url = tab.get('url', '')
                    title = tab.get('title', '')
                    print(f"  {i+1}. {title[:50]} - {url[:60]}")
                    
                    if 'manus.im' in url:
                        manus_tabs.append(tab)
                        print(f"     ⭐ 這是Manus頁面!")
                
                return tabs, manus_tabs
            else:
                print("❌ 無法獲取標籤頁列表")
                return [], []
        except Exception as e:
            print(f"❌ 獲取標籤頁失敗: {e}")
            return [], []
    
    def guide_user_to_enable_debug(self):
        """指導用戶開啟調試模式"""
        print("\n" + "="*60)
        print("🔧 需要在現有Chrome中開啟調試模式")
        print("="*60)
        print("請按照以下步驟操作:")
        print()
        print("1. 完全關閉所有Chrome視窗")
        print("2. 在終端中執行以下命令:")
        print()
        print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
        print(f"     --remote-debugging-port={self.debug_port} \\")
        print("     --user-data-dir=/tmp/chrome-debug \\")
        print("     https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ")
        print()
        print("3. 在新開啟的Chrome中登入Manus")
        print("4. 保持Chrome開啟，然後重新運行此腳本")
        print()
        print("💡 或者，如果您已經有Chrome開啟，可以:")
        print("   - 在地址欄輸入: chrome://settings/")
        print("   - 搜索 '實驗性功能' 或 '開發者工具'")
        print("="*60)
    
    async def connect_to_existing_browser_only(self):
        """只連接現有瀏覽器，不創建新的"""
        print("🔗 嘗試連接到現有Chrome瀏覽器...")
        
        # 首先檢查是否有可用的Chrome
        if not self.check_existing_chrome():
            self.guide_user_to_enable_debug()
            return False
        
        # 獲取現有標籤頁
        tabs, manus_tabs = self.get_existing_tabs()
        if not tabs:
            print("❌ 沒有找到可用的標籤頁")
            return False
        
        try:
            self.playwright = await async_playwright().start()
            
            # 連接到現有瀏覽器（不創建新的）
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            
            print("✅ 成功連接到現有瀏覽器")
            
            # 獲取現有頁面
            contexts = self.browser.contexts
            if not contexts:
                print("❌ 沒有找到瀏覽器上下文")
                return False
            
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ 沒有找到打開的頁面")
                return False
            
            # 優先選擇Manus頁面
            manus_page = None
            for page in pages:
                try:
                    url = page.url
                    if 'manus.im' in url:
                        manus_page = page
                        print(f"✅ 找到Manus頁面: {url}")
                        break
                except:
                    continue
            
            if manus_page:
                self.page = manus_page
            else:
                # 如果沒有Manus頁面，使用第一個頁面
                self.page = pages[0]
                current_url = self.page.url
                print(f"📄 使用當前頁面: {current_url}")
                
                # 詢問是否導航到Manus
                if 'manus.im' not in current_url:
                    navigate = input("是否導航到Manus頁面? (y/n): ").strip().lower()
                    if navigate == 'y':
                        manus_url = "https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"
                        await self.page.goto(manus_url, wait_until='networkidle')
                        print(f"✅ 已導航到: {manus_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    async def extract_conversations_debug(self):
        """調試版對話提取"""
        print("🔍 調試模式 - 分析頁面結構...")
        
        try:
            # 等待頁面穩定
            await asyncio.sleep(2)
            
            # 獲取頁面基本信息
            title = await self.page.title()
            url = self.page.url
            print(f"📄 當前頁面: {title}")
            print(f"🌐 URL: {url}")
            
            # 嘗試多種方法查找消息
            methods = [
                self._method_1_role_listitem,
                self._method_2_message_classes,
                self._method_3_text_elements,
                self._method_4_generic_divs
            ]
            
            all_results = []
            
            for i, method in enumerate(methods, 1):
                print(f"\n🔍 方法 {i}: {method.__name__}")
                try:
                    results = await method()
                    if results:
                        print(f"  ✅ 找到 {len(results)} 個元素")
                        all_results.extend(results)
                        
                        # 顯示前3個示例
                        for j, result in enumerate(results[:3]):
                            print(f"    {j+1}. {result[:80]}...")
                    else:
                        print(f"  ❌ 沒有找到元素")
                except Exception as e:
                    print(f"  ❌ 方法失敗: {e}")
            
            # 去重
            unique_results = list(set(all_results))
            print(f"\n📊 總結: 找到 {len(unique_results)} 條唯一消息")
            
            return unique_results
            
        except Exception as e:
            print(f"❌ 調試提取失敗: {e}")
            return []
    
    async def _method_1_role_listitem(self):
        """方法1: 使用role=listitem"""
        elements = await self.page.query_selector_all('[role="listitem"]')
        results = []
        
        for element in elements:
            try:
                if await element.is_visible():
                    text = await element.inner_text()
                    if text and len(text.strip()) > 10:
                        results.append(text.strip())
            except:
                continue
        
        return results
    
    async def _method_2_message_classes(self):
        """方法2: 使用消息相關類名"""
        selectors = ['.message', '.chat-message', '[class*="message"]', '[class*="chat"]']
        results = []
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        text = await element.inner_text()
                        if text and len(text.strip()) > 10:
                            results.append(text.strip())
            except:
                continue
        
        return results
    
    async def _method_3_text_elements(self):
        """方法3: 使用文本元素"""
        selectors = ['p', 'div p', '.text', '.content']
        results = []
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        text = await element.inner_text()
                        if text and len(text.strip()) > 20:  # 更長的文本
                            results.append(text.strip())
            except:
                continue
        
        return results
    
    async def _method_4_generic_divs(self):
        """方法4: 通用div掃描"""
        results = []
        
        try:
            # 獲取所有div
            divs = await self.page.query_selector_all('div')
            
            for div in divs:
                try:
                    if await div.is_visible():
                        text = await div.inner_text()
                        # 檢查是否像對話消息
                        if text and 50 < len(text.strip()) < 1000:  # 合理的消息長度
                            # 檢查是否包含對話特徵
                            if any(keyword in text.lower() for keyword in 
                                  ['user', 'assistant', '用戶', 'ai', 'bot', '回覆', 'reply']):
                                results.append(text.strip())
                except:
                    continue
        
        except Exception as e:
            print(f"通用掃描失敗: {e}")
        
        return results
    
    async def send_message_to_existing(self, message):
        """向現有頁面發送消息"""
        print(f"📤 在現有頁面發送消息: {message[:50]}...")
        
        try:
            # 確保頁面是活躍的
            await self.page.bring_to_front()
            await asyncio.sleep(1)
            
            # 查找輸入框
            input_selectors = [
                'textarea',
                'input[type="text"]',
                '[contenteditable="true"]',
                '.input',
                '.message-input',
                '[placeholder*="輸入"]',
                '[placeholder*="input"]',
                '[placeholder*="message"]'
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
                # 嘗試點擊頁面激活輸入
                await self.page.click('body')
                await asyncio.sleep(1)
                return False
            
            # 清空並輸入
            await input_element.click()
            await asyncio.sleep(0.5)
            await input_element.fill("")
            await asyncio.sleep(0.5)
            await input_element.type(message, delay=50)  # 模擬真實輸入
            await asyncio.sleep(1)
            
            # 查找發送按鈕
            button_selectors = [
                'button[type="submit"]',
                '.send-button',
                '.send',
                'button:has-text("發送")',
                'button:has-text("Send")',
                '[aria-label*="send"]',
                '[aria-label*="發送"]'
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
    
    async def take_screenshot_existing(self, filename=None):
        """對現有頁面截圖"""
        if not filename:
            filename = f"existing_browser_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        try:
            await self.page.screenshot(path=filename, full_page=True)
            print(f"📸 截圖已保存: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 截圖失敗: {e}")
            return None
    
    async def cleanup(self):
        """清理（不關閉瀏覽器）"""
        try:
            # 只清理playwright連接，不關閉瀏覽器
            if self.playwright:
                await self.playwright.stop()
            print("✅ 已斷開連接（瀏覽器保持打開）")
        except Exception as e:
            print(f"❌ 清理失敗: {e}")

async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='連接現有Chrome瀏覽器（不開啟新的）')
    parser.add_argument('--action', choices=['connect', 'conversations', 'send', 'screenshot', 'interactive'],
                       default='interactive', help='要執行的操作')
    parser.add_argument('--message', help='要發送的消息')
    parser.add_argument('--port', type=int, default=9222, help='Chrome調試端口')
    
    args = parser.parse_args()
    
    connector = TrueExistingBrowserConnector(debug_port=args.port)
    
    try:
        # 連接到現有瀏覽器
        success = await connector.connect_to_existing_browser_only()
        if not success:
            print("❌ 無法連接到現有瀏覽器")
            return 1
        
        # 執行操作
        if args.action == 'conversations':
            await connector.extract_conversations_debug()
        
        elif args.action == 'send':
            if not args.message:
                message = input("請輸入要發送的消息: ")
            else:
                message = args.message
            await connector.send_message_to_existing(message)
        
        elif args.action == 'screenshot':
            await connector.take_screenshot_existing()
        
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
    print("🎮 真正的現有瀏覽器連接 - 交互模式")
    print("="*50)
    print("可用命令:")
    print("  1 - 調試模式提取對話")
    print("  2 - 發送消息")
    print("  3 - 頁面截圖")
    print("  4 - 檢查頁面信息")
    print("  5 - 檢查瀏覽器標籤頁")
    print("  q - 退出")
    print("="*50)
    
    while True:
        try:
            command = input("\n請輸入命令 (1-5, q): ").strip()
            
            if command == 'q':
                print("👋 退出交互模式")
                break
            elif command == '1':
                await connector.extract_conversations_debug()
            elif command == '2':
                message = input("請輸入要發送的消息: ").strip()
                if message:
                    await connector.send_message_to_existing(message)
                else:
                    print("❌ 消息不能為空")
            elif command == '3':
                await connector.take_screenshot_existing()
            elif command == '4':
                try:
                    title = await connector.page.title()
                    url = connector.page.url
                    print(f"📄 頁面標題: {title}")
                    print(f"🌐 當前URL: {url}")
                except Exception as e:
                    print(f"❌ 獲取頁面信息失敗: {e}")
            elif command == '5':
                connector.get_existing_tabs()
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

