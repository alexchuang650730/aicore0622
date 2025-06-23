"""
PowerAutomation Manus 瀏覽器控制器
使用Playwright自動化操作Manus頁面
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import os

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ManusCredentials:
    """Manus登錄憑證"""
    email: str = "chuang.hsiaoyen@gmail.com"
    password: str = "silentfleet#1234"

@dataclass
class ManusConfig:
    """Manus配置"""
    url: str = "https://manus.chat"
    login_timeout: int = 30000  # 30秒
    page_timeout: int = 60000   # 60秒
    headless: bool = True
    slow_mo: int = 1000        # 操作間隔1秒

class ManusPageController:
    """Manus頁面控制器"""
    
    def __init__(self, config: Optional[ManusConfig] = None, 
                 credentials: Optional[ManusCredentials] = None):
        """初始化控制器"""
        self.config = config or ManusConfig()
        self.credentials = credentials or ManusCredentials()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        
    async def start(self):
        """啟動瀏覽器"""
        try:
            logger.info("啟動Playwright瀏覽器...")
            self.playwright = await async_playwright().start()
            
            # 啟動Chromium瀏覽器
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                slow_mo=self.config.slow_mo
            )
            
            # 創建瀏覽器上下文
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # 創建新頁面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.page_timeout)
            
            logger.info("瀏覽器啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"瀏覽器啟動失敗: {e}")
            return False
    
    async def stop(self):
        """停止瀏覽器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("瀏覽器已停止")
            
        except Exception as e:
            logger.error(f"停止瀏覽器時出錯: {e}")
    
    async def login(self) -> bool:
        """登錄Manus"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return False
            
            logger.info(f"導航到Manus登錄頁面: {self.config.url}")
            await self.page.goto(self.config.url)
            
            # 等待頁面載入
            await self.page.wait_for_load_state('networkidle')
            
            # 檢查是否已經登錄
            if await self.check_login_status():
                logger.info("已經登錄，無需重新登錄")
                self.is_logged_in = True
                return True
            
            # 查找登錄按鈕或登錄表單
            login_selectors = [
                'button:has-text("登錄")',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'a:has-text("登錄")',
                'a:has-text("Login")',
                '[data-testid="login-button"]',
                '.login-button',
                '#login-button'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if login_button:
                        logger.info(f"找到登錄按鈕: {selector}")
                        break
                except:
                    continue
            
            if login_button:
                await login_button.click()
                await self.page.wait_for_load_state('networkidle')
            
            # 查找並填寫郵箱
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email"]',
                'input[placeholder*="郵箱"]',
                '#email',
                '.email-input'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if email_input:
                        logger.info(f"找到郵箱輸入框: {selector}")
                        break
                except:
                    continue
            
            if not email_input:
                logger.error("未找到郵箱輸入框")
                return False
            
            await email_input.fill(self.credentials.email)
            logger.info(f"已填寫郵箱: {self.credentials.email}")
            
            # 查找並填寫密碼
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="password"]',
                'input[placeholder*="密碼"]',
                '#password',
                '.password-input'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if password_input:
                        logger.info(f"找到密碼輸入框: {selector}")
                        break
                except:
                    continue
            
            if not password_input:
                logger.error("未找到密碼輸入框")
                return False
            
            await password_input.fill(self.credentials.password)
            logger.info("已填寫密碼")
            
            # 查找並點擊提交按鈕
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("登錄")',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[type="submit"]',
                '.submit-button',
                '.login-submit'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if submit_button:
                        logger.info(f"找到提交按鈕: {selector}")
                        break
                except:
                    continue
            
            if not submit_button:
                logger.error("未找到提交按鈕")
                return False
            
            await submit_button.click()
            logger.info("已點擊登錄按鈕")
            
            # 等待登錄完成
            await self.page.wait_for_load_state('networkidle')
            
            # 檢查登錄是否成功
            await asyncio.sleep(3)  # 等待3秒讓頁面完全載入
            
            if await self.check_login_status():
                logger.info("登錄成功！")
                self.is_logged_in = True
                return True
            else:
                logger.error("登錄失敗")
                return False
                
        except Exception as e:
            logger.error(f"登錄過程中出錯: {e}")
            return False
    
    async def check_login_status(self) -> bool:
        """檢查登錄狀態"""
        try:
            if not self.page:
                return False
            
            # 檢查是否存在登錄後的元素
            logged_in_indicators = [
                '.user-avatar',
                '.profile-menu',
                '.chat-container',
                '.conversation-list',
                '[data-testid="user-menu"]',
                'button:has-text("登出")',
                'button:has-text("Logout")'
            ]
            
            for selector in logged_in_indicators:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        logger.info(f"檢測到登錄狀態指示器: {selector}")
                        return True
                except:
                    continue
            
            # 檢查URL是否包含登錄後的路徑
            current_url = self.page.url
            logged_in_paths = ['/chat', '/dashboard', '/conversations', '/home']
            
            for path in logged_in_paths:
                if path in current_url:
                    logger.info(f"URL顯示已登錄: {current_url}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"檢查登錄狀態時出錯: {e}")
            return False
    
    async def send_message(self, message: str) -> bool:
        """發送消息到Manus"""
        try:
            if not self.is_logged_in:
                logger.error("未登錄，無法發送消息")
                return False
            
            if not self.page:
                logger.error("頁面未初始化")
                return False
            
            logger.info(f"準備發送消息: {message[:50]}...")
            
            # 查找消息輸入框
            input_selectors = [
                'textarea[placeholder*="輸入"]',
                'textarea[placeholder*="message"]',
                'input[placeholder*="輸入"]',
                'input[placeholder*="message"]',
                '.message-input',
                '.chat-input',
                '[data-testid="message-input"]',
                'textarea',
                'input[type="text"]'
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    message_input = await self.page.wait_for_selector(selector, timeout=5000)
                    if message_input:
                        # 檢查輸入框是否可見和可用
                        is_visible = await message_input.is_visible()
                        is_enabled = await message_input.is_enabled()
                        if is_visible and is_enabled:
                            logger.info(f"找到消息輸入框: {selector}")
                            break
                        else:
                            message_input = None
                except:
                    continue
            
            if not message_input:
                logger.error("未找到消息輸入框")
                return False
            
            # 清空輸入框並輸入消息
            await message_input.click()
            await message_input.fill("")  # 清空
            await message_input.type(message, delay=100)  # 模擬真實輸入
            
            logger.info("消息已輸入到輸入框")
            
            # 查找並點擊發送按鈕
            send_selectors = [
                'button:has-text("發送")',
                'button:has-text("Send")',
                'button:has-text("提交")',
                'button[type="submit"]',
                '.send-button',
                '.submit-button',
                '[data-testid="send-button"]',
                'button[aria-label*="send"]',
                'button[aria-label*="發送"]'
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if send_button:
                        is_visible = await send_button.is_visible()
                        is_enabled = await send_button.is_enabled()
                        if is_visible and is_enabled:
                            logger.info(f"找到發送按鈕: {selector}")
                            break
                        else:
                            send_button = None
                except:
                    continue
            
            if send_button:
                await send_button.click()
                logger.info("已點擊發送按鈕")
            else:
                # 嘗試按Enter鍵發送
                logger.info("未找到發送按鈕，嘗試按Enter鍵")
                await message_input.press('Enter')
            
            # 等待消息發送完成
            await asyncio.sleep(2)
            
            logger.info("消息發送完成")
            return True
            
        except Exception as e:
            logger.error(f"發送消息時出錯: {e}")
            return False
    
    async def get_latest_messages(self, count: int = 5) -> List[Dict[str, str]]:
        """獲取最新的消息"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return []
            
            logger.info(f"獲取最新 {count} 條消息")
            
            # 等待消息載入
            await asyncio.sleep(2)
            
            # 查找消息容器
            message_selectors = [
                '.message',
                '.chat-message',
                '.conversation-message',
                '[data-testid="message"]',
                '.message-item',
                '.chat-item'
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    message_elements = await self.page.query_selector_all(selector)
                    if message_elements:
                        logger.info(f"找到 {len(message_elements)} 條消息，使用選擇器: {selector}")
                        
                        # 取最新的消息
                        recent_elements = message_elements[-count:] if len(message_elements) >= count else message_elements
                        
                        for element in recent_elements:
                            try:
                                # 嘗試提取消息內容和發送者
                                content = await element.inner_text()
                                
                                # 嘗試識別發送者
                                sender = "unknown"
                                
                                # 檢查是否是用戶消息
                                user_indicators = ['.user-message', '.my-message', '.sent-message']
                                for indicator in user_indicators:
                                    if await element.query_selector(indicator):
                                        sender = "user"
                                        break
                                
                                # 檢查是否是AI消息
                                if sender == "unknown":
                                    ai_indicators = ['.ai-message', '.bot-message', '.received-message']
                                    for indicator in ai_indicators:
                                        if await element.query_selector(indicator):
                                            sender = "manus"
                                            break
                                
                                # 如果還是無法確定，根據位置判斷
                                if sender == "unknown":
                                    class_name = await element.get_attribute('class') or ""
                                    if 'right' in class_name or 'user' in class_name:
                                        sender = "user"
                                    elif 'left' in class_name or 'bot' in class_name or 'ai' in class_name:
                                        sender = "manus"
                                
                                if content.strip():
                                    messages.append({
                                        'role': sender,
                                        'content': content.strip(),
                                        'timestamp': time.strftime('%H:%M:%S')
                                    })
                                    
                            except Exception as e:
                                logger.warning(f"提取消息內容時出錯: {e}")
                                continue
                        
                        break  # 找到消息後退出循環
                        
                except Exception as e:
                    logger.warning(f"查找消息時出錯 ({selector}): {e}")
                    continue
            
            logger.info(f"成功獲取 {len(messages)} 條消息")
            return messages
            
        except Exception as e:
            logger.error(f"獲取消息時出錯: {e}")
            return []
    
    async def wait_for_response(self, timeout: int = 30) -> Optional[str]:
        """等待Manus回應"""
        try:
            logger.info(f"等待Manus回應，超時時間: {timeout}秒")
            
            start_time = time.time()
            last_message_count = 0
            
            while time.time() - start_time < timeout:
                messages = await self.get_latest_messages(count=3)
                
                if len(messages) > last_message_count:
                    # 檢查最新消息是否來自Manus
                    latest_message = messages[-1]
                    if latest_message['role'] == 'manus':
                        logger.info("收到Manus回應")
                        return latest_message['content']
                
                last_message_count = len(messages)
                await asyncio.sleep(1)  # 每秒檢查一次
            
            logger.warning("等待回應超時")
            return None
            
        except Exception as e:
            logger.error(f"等待回應時出錯: {e}")
            return None
    
    async def take_screenshot(self, path: str = None) -> str:
        """截圖"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return ""
            
            if not path:
                timestamp = int(time.time())
                path = f"/tmp/manus_screenshot_{timestamp}.png"
            
            await self.page.screenshot(path=path, full_page=True)
            logger.info(f"截圖已保存: {path}")
            return path
            
        except Exception as e:
            logger.error(f"截圖時出錯: {e}")
            return ""
    
    async def get_page_info(self) -> Dict[str, Any]:
        """獲取頁面信息"""
        try:
            if not self.page:
                return {}
            
            info = {
                'url': self.page.url,
                'title': await self.page.title(),
                'is_logged_in': self.is_logged_in,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return info
            
        except Exception as e:
            logger.error(f"獲取頁面信息時出錯: {e}")
            return {}

class ManusAutomationService:
    """Manus自動化服務"""
    
    def __init__(self):
        """初始化服務"""
        self.controller = ManusPageController()
        self.is_running = False
    
    async def start_service(self) -> bool:
        """啟動服務"""
        try:
            logger.info("啟動Manus自動化服務...")
            
            # 啟動瀏覽器
            if not await self.controller.start():
                return False
            
            # 登錄Manus
            if not await self.controller.login():
                await self.controller.stop()
                return False
            
            self.is_running = True
            logger.info("Manus自動化服務啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"啟動服務時出錯: {e}")
            return False
    
    async def stop_service(self):
        """停止服務"""
        try:
            logger.info("停止Manus自動化服務...")
            await self.controller.stop()
            self.is_running = False
            logger.info("服務已停止")
            
        except Exception as e:
            logger.error(f"停止服務時出錯: {e}")
    
    async def send_intelligent_response(self, message: str) -> Dict[str, Any]:
        """發送智能回應"""
        try:
            if not self.is_running:
                return {
                    'success': False,
                    'error': '服務未運行'
                }
            
            # 發送消息
            send_success = await self.controller.send_message(message)
            if not send_success:
                return {
                    'success': False,
                    'error': '發送消息失敗'
                }
            
            # 等待回應
            response = await self.controller.wait_for_response()
            
            # 獲取最新消息
            messages = await self.controller.get_latest_messages(count=5)
            
            return {
                'success': True,
                'message_sent': message,
                'response_received': response,
                'latest_messages': messages,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"發送智能回應時出錯: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_conversation_status(self) -> Dict[str, Any]:
        """獲取對話狀態"""
        try:
            if not self.is_running:
                return {
                    'success': False,
                    'error': '服務未運行'
                }
            
            messages = await self.controller.get_latest_messages(count=10)
            page_info = await self.controller.get_page_info()
            
            return {
                'success': True,
                'is_logged_in': self.controller.is_logged_in,
                'page_info': page_info,
                'recent_messages': messages,
                'message_count': len(messages)
            }
            
        except Exception as e:
            logger.error(f"獲取對話狀態時出錯: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# 使用示例
async def main():
    """主函數示例"""
    service = ManusAutomationService()
    
    try:
        # 啟動服務
        if await service.start_service():
            print("✅ 服務啟動成功")
            
            # 發送測試消息
            result = await service.send_intelligent_response("🧪 PowerAutomation測試消息")
            print(f"發送結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 獲取對話狀態
            status = await service.get_conversation_status()
            print(f"對話狀態: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
        else:
            print("❌ 服務啟動失敗")
            
    finally:
        # 停止服務
        await service.stop_service()

if __name__ == "__main__":
    asyncio.run(main())

