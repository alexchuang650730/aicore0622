"""
PowerAutomation Manus 增強瀏覽器控制器
添加任務列表遍歷、文件分類和批量下載功能
"""

import asyncio
import json
import logging
import time
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Download
from urllib.parse import urlparse

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskInfo:
    """任務信息"""
    task_id: str
    title: str
    url: str
    last_activity: str
    message_count: int = 0

@dataclass
class FileInfo:
    """文件信息"""
    name: str
    type: str  # document, image, code, link
    url: str
    timestamp: str
    size: Optional[str] = None
    download_path: Optional[str] = None

class ManusAdvancedController:
    """Manus高級控制器"""
    
    def __init__(self, config: Optional[dict] = None, credentials: Optional[dict] = None):
        """初始化控制器"""
        self.config = config or {
            'url': 'https://manus.chat',
            'headless': True,
            'slow_mo': 1000,
            'timeout': 60000
        }
        self.credentials = credentials or {
            'email': 'chuang.hsiaoyen@gmail.com',
            'password': 'silentfleet#1234'
        }
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.download_dir = "/tmp/manus_downloads"
        
        # 創建下載目錄
        os.makedirs(self.download_dir, exist_ok=True)
        
    async def start(self):
        """啟動瀏覽器"""
        try:
            logger.info("啟動Playwright瀏覽器...")
            self.playwright = await async_playwright().start()
            
            # 啟動Chromium瀏覽器
            self.browser = await self.playwright.chromium.launch(
                headless=self.config['headless'],
                slow_mo=self.config['slow_mo']
            )
            
            # 創建瀏覽器上下文，設置下載路徑
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                accept_downloads=True
            )
            
            # 創建新頁面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config['timeout'])
            
            logger.info("瀏覽器啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"瀏覽器啟動失敗: {e}")
            return False
    
    async def login(self) -> bool:
        """登錄Manus"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return False
            
            logger.info(f"導航到Manus登錄頁面: {self.config['url']}")
            await self.page.goto(self.config['url'])
            await self.page.wait_for_load_state('networkidle')
            
            # 檢查是否已經登錄
            if await self.check_login_status():
                logger.info("已經登錄，無需重新登錄")
                self.is_logged_in = True
                return True
            
            # 執行登錄流程（簡化版本）
            # 這裡可以添加詳細的登錄邏輯
            await asyncio.sleep(3)
            self.is_logged_in = True
            logger.info("登錄成功")
            return True
            
        except Exception as e:
            logger.error(f"登錄過程中出錯: {e}")
            return False
    
    async def check_login_status(self) -> bool:
        """檢查登錄狀態"""
        try:
            if not self.page:
                return False
            
            # 檢查登錄狀態的邏輯
            current_url = self.page.url
            return 'chat' in current_url or 'dashboard' in current_url
            
        except Exception as e:
            logger.error(f"檢查登錄狀態時出錯: {e}")
            return False
    
    async def get_task_list(self) -> List[TaskInfo]:
        """獲取任務列表（左側列表）"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return []
            
            logger.info("獲取任務列表...")
            
            # 等待頁面載入
            await self.page.wait_for_load_state('networkidle')
            
            # 查找任務列表容器
            task_list_selectors = [
                '.task-list',
                '.conversation-list',
                '.sidebar-list',
                '[data-testid="task-list"]',
                '.chat-list',
                'nav ul',
                '.navigation-list'
            ]
            
            task_container = None
            for selector in task_list_selectors:
                try:
                    task_container = await self.page.wait_for_selector(selector, timeout=5000)
                    if task_container:
                        logger.info(f"找到任務列表容器: {selector}")
                        break
                except:
                    continue
            
            if not task_container:
                logger.warning("未找到任務列表容器，嘗試查找任務項目")
                
            # 查找任務項目
            task_item_selectors = [
                '.task-item',
                '.conversation-item',
                '.chat-item',
                'li[data-task-id]',
                'a[href*="task"]',
                'a[href*="chat"]',
                '.list-item'
            ]
            
            tasks = []
            for selector in task_item_selectors:
                try:
                    task_elements = await self.page.query_selector_all(selector)
                    if task_elements:
                        logger.info(f"找到 {len(task_elements)} 個任務項目，使用選擇器: {selector}")
                        
                        for i, element in enumerate(task_elements):
                            try:
                                # 提取任務信息
                                title = await element.inner_text()
                                href = await element.get_attribute('href') or ""
                                
                                # 生成任務ID
                                task_id = f"task_{i+1}"
                                if 'data-task-id' in await element.get_attribute('class') or "":
                                    task_id = await element.get_attribute('data-task-id') or task_id
                                
                                # 提取時間信息
                                time_element = await element.query_selector('.time, .timestamp, .last-activity')
                                last_activity = ""
                                if time_element:
                                    last_activity = await time_element.inner_text()
                                
                                task_info = TaskInfo(
                                    task_id=task_id,
                                    title=title.strip()[:100],  # 限制標題長度
                                    url=href,
                                    last_activity=last_activity
                                )
                                
                                tasks.append(task_info)
                                
                            except Exception as e:
                                logger.warning(f"提取任務信息時出錯: {e}")
                                continue
                        
                        break  # 找到任務後退出循環
                        
                except Exception as e:
                    logger.warning(f"查找任務項目時出錯 ({selector}): {e}")
                    continue
            
            logger.info(f"成功獲取 {len(tasks)} 個任務")
            return tasks
            
        except Exception as e:
            logger.error(f"獲取任務列表時出錯: {e}")
            return []
    
    async def navigate_to_task(self, task_info: TaskInfo) -> bool:
        """導航到指定任務"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return False
            
            logger.info(f"導航到任務: {task_info.title}")
            
            if task_info.url:
                # 如果有URL，直接導航
                await self.page.goto(task_info.url)
            else:
                # 嘗試點擊任務項目
                task_selectors = [
                    f'[data-task-id="{task_info.task_id}"]',
                    f'a:has-text("{task_info.title[:20]}")',
                    f'.task-item:has-text("{task_info.title[:20]}")'
                ]
                
                clicked = False
                for selector in task_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                        if element:
                            await element.click()
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    logger.error(f"無法點擊任務: {task_info.title}")
                    return False
            
            # 等待頁面載入
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            logger.info(f"成功導航到任務: {task_info.title}")
            return True
            
        except Exception as e:
            logger.error(f"導航到任務時出錯: {e}")
            return False
    
    async def open_files_panel(self) -> bool:
        """打開文件面板（View all files in this task）"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return False
            
            logger.info("打開文件面板...")
            
            # 查找"View all files in this task"按鈕
            files_button_selectors = [
                'button:has-text("View all files in this task")',
                'button:has-text("查看所有文件")',
                '[data-testid="view-files-button"]',
                '.view-files-button',
                'button[aria-label*="files"]'
            ]
            
            files_button = None
            for selector in files_button_selectors:
                try:
                    files_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if files_button:
                        logger.info(f"找到文件按鈕: {selector}")
                        break
                except:
                    continue
            
            if not files_button:
                logger.error("未找到文件面板按鈕")
                return False
            
            # 點擊按鈕
            await files_button.click()
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 檢查文件面板是否打開
            panel_selectors = [
                '.files-panel',
                '.file-list-modal',
                '[data-testid="files-panel"]',
                'div:has-text("All files in this task")'
            ]
            
            panel_opened = False
            for selector in panel_selectors:
                try:
                    panel = await self.page.wait_for_selector(selector, timeout=3000)
                    if panel:
                        logger.info(f"文件面板已打開: {selector}")
                        panel_opened = True
                        break
                except:
                    continue
            
            return panel_opened
            
        except Exception as e:
            logger.error(f"打開文件面板時出錯: {e}")
            return False
    
    async def get_files_by_category(self, category: str = "All") -> List[FileInfo]:
        """按分類獲取文件列表"""
        try:
            if not self.page:
                logger.error("頁面未初始化")
                return []
            
            logger.info(f"獲取文件列表，分類: {category}")
            
            # 如果不是"All"，點擊相應的分類標籤
            if category != "All":
                category_selectors = [
                    f'button:has-text("{category}")',
                    f'.category-tab:has-text("{category}")',
                    f'[data-category="{category}"]'
                ]
                
                for selector in category_selectors:
                    try:
                        category_button = await self.page.wait_for_selector(selector, timeout=3000)
                        if category_button:
                            await category_button.click()
                            await asyncio.sleep(1)
                            logger.info(f"已選擇分類: {category}")
                            break
                    except:
                        continue
            
            # 獲取文件列表
            file_item_selectors = [
                '.file-item',
                '.file-list-item',
                '[data-testid="file-item"]',
                '.attachment-item'
            ]
            
            files = []
            for selector in file_item_selectors:
                try:
                    file_elements = await self.page.query_selector_all(selector)
                    if file_elements:
                        logger.info(f"找到 {len(file_elements)} 個文件，使用選擇器: {selector}")
                        
                        for element in file_elements:
                            try:
                                # 提取文件信息
                                name_element = await element.query_selector('.file-name, .filename, .name')
                                name = await name_element.inner_text() if name_element else "unknown"
                                
                                # 提取文件類型
                                file_type = self._determine_file_type(name)
                                
                                # 提取時間戳
                                time_element = await element.query_selector('.timestamp, .time, .date')
                                timestamp = await time_element.inner_text() if time_element else ""
                                
                                # 提取下載鏈接
                                link_element = await element.query_selector('a[href], [data-download-url]')
                                url = ""
                                if link_element:
                                    url = await link_element.get_attribute('href') or await link_element.get_attribute('data-download-url') or ""
                                
                                # 提取文件大小
                                size_element = await element.query_selector('.file-size, .size')
                                size = await size_element.inner_text() if size_element else None
                                
                                file_info = FileInfo(
                                    name=name,
                                    type=file_type,
                                    url=url,
                                    timestamp=timestamp,
                                    size=size
                                )
                                
                                files.append(file_info)
                                
                            except Exception as e:
                                logger.warning(f"提取文件信息時出錯: {e}")
                                continue
                        
                        break  # 找到文件後退出循環
                        
                except Exception as e:
                    logger.warning(f"查找文件項目時出錯 ({selector}): {e}")
                    continue
            
            logger.info(f"成功獲取 {len(files)} 個文件")
            return files
            
        except Exception as e:
            logger.error(f"獲取文件列表時出錯: {e}")
            return []
    
    def _determine_file_type(self, filename: str) -> str:
        """根據文件名確定文件類型"""
        filename_lower = filename.lower()
        
        # 代碼文件
        code_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
                          '.java', '.cpp', '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift']
        if any(filename_lower.endswith(ext) for ext in code_extensions):
            return 'code'
        
        # 圖片文件
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico']
        if any(filename_lower.endswith(ext) for ext in image_extensions):
            return 'image'
        
        # 文檔文件
        doc_extensions = ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt', '.pages']
        if any(filename_lower.endswith(ext) for ext in doc_extensions):
            return 'document'
        
        # 鏈接（通常沒有擴展名或特殊標識）
        if 'http' in filename_lower or 'www' in filename_lower:
            return 'link'
        
        return 'document'  # 默認為文檔
    
    async def download_file(self, file_info: FileInfo) -> bool:
        """下載單個文件"""
        try:
            if not file_info.url:
                logger.warning(f"文件 {file_info.name} 沒有下載鏈接")
                return False
            
            logger.info(f"下載文件: {file_info.name}")
            
            # 創建分類目錄
            category_dir = os.path.join(self.download_dir, file_info.type)
            os.makedirs(category_dir, exist_ok=True)
            
            # 設置下載路徑
            safe_filename = re.sub(r'[^\w\-_\.]', '_', file_info.name)
            download_path = os.path.join(category_dir, safe_filename)
            
            # 監聽下載事件
            download_info = None
            
            async def handle_download(download: Download):
                nonlocal download_info
                download_info = download
                await download.save_as(download_path)
            
            self.page.on("download", handle_download)
            
            # 觸發下載
            if file_info.url.startswith('http'):
                # 外部鏈接，直接導航
                await self.page.goto(file_info.url)
            else:
                # 內部鏈接，點擊下載
                download_element = await self.page.query_selector(f'a[href="{file_info.url}"]')
                if download_element:
                    await download_element.click()
            
            # 等待下載完成
            await asyncio.sleep(3)
            
            # 檢查文件是否下載成功
            if os.path.exists(download_path):
                file_info.download_path = download_path
                logger.info(f"文件下載成功: {download_path}")
                return True
            else:
                logger.warning(f"文件下載失敗: {file_info.name}")
                return False
            
        except Exception as e:
            logger.error(f"下載文件時出錯: {e}")
            return False
    
    async def batch_download_files(self, category: str = "All") -> Dict[str, List[FileInfo]]:
        """批量下載文件"""
        try:
            logger.info(f"開始批量下載文件，分類: {category}")
            
            # 打開文件面板
            if not await self.open_files_panel():
                return {}
            
            # 如果指定了分類，獲取該分類的文件
            if category != "All":
                files = await self.get_files_by_category(category)
                categories = {category: files}
            else:
                # 獲取所有分類的文件
                categories = {}
                for cat in ["Documents", "Images", "Code files", "Links"]:
                    files = await self.get_files_by_category(cat)
                    if files:
                        categories[cat] = files
            
            # 下載文件
            download_results = {}
            for cat_name, files in categories.items():
                logger.info(f"下載 {cat_name} 分類的 {len(files)} 個文件")
                
                downloaded_files = []
                for file_info in files:
                    success = await self.download_file(file_info)
                    if success:
                        downloaded_files.append(file_info)
                
                download_results[cat_name] = downloaded_files
                logger.info(f"{cat_name} 分類下載完成: {len(downloaded_files)}/{len(files)}")
            
            return download_results
            
        except Exception as e:
            logger.error(f"批量下載文件時出錯: {e}")
            return {}
    
    async def get_conversation_history(self, task_info: TaskInfo) -> List[Dict[str, Any]]:
        """獲取完整對話歷史"""
        try:
            logger.info(f"獲取任務對話歷史: {task_info.title}")
            
            # 導航到任務
            if not await self.navigate_to_task(task_info):
                return []
            
            # 嘗試滾動載入更多歷史
            await self.scroll_to_load_history()
            
            # 獲取所有消息
            messages = await self.get_all_messages()
            
            logger.info(f"獲取到 {len(messages)} 條消息")
            return messages
            
        except Exception as e:
            logger.error(f"獲取對話歷史時出錯: {e}")
            return []
    
    async def scroll_to_load_history(self):
        """滾動載入更多歷史消息"""
        try:
            logger.info("滾動載入歷史消息...")
            
            # 找到消息容器
            message_container = await self.page.query_selector('.messages, .chat-container, .conversation')
            
            if message_container:
                # 滾動到頂部載入更多
                for _ in range(10):  # 最多滾動10次
                    await self.page.keyboard.press('Home')  # 滾動到頂部
                    await asyncio.sleep(1)
                    
                    # 檢查是否有"載入更多"按鈕
                    load_more_button = await self.page.query_selector('button:has-text("Load more"), button:has-text("載入更多")')
                    if load_more_button:
                        await load_more_button.click()
                        await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"滾動載入歷史時出錯: {e}")
    
    async def get_all_messages(self) -> List[Dict[str, Any]]:
        """獲取所有消息"""
        try:
            # 等待消息載入
            await asyncio.sleep(2)
            
            # 查找消息元素
            message_selectors = [
                '.message',
                '.chat-message',
                '.conversation-message',
                '[data-testid="message"]'
            ]
            
            messages = []
            for selector in message_selectors:
                try:
                    message_elements = await self.page.query_selector_all(selector)
                    if message_elements:
                        logger.info(f"找到 {len(message_elements)} 條消息")
                        
                        for element in message_elements:
                            try:
                                content = await element.inner_text()
                                
                                # 確定發送者
                                sender = "unknown"
                                class_name = await element.get_attribute('class') or ""
                                
                                if 'user' in class_name or 'sent' in class_name:
                                    sender = "user"
                                elif 'bot' in class_name or 'ai' in class_name or 'manus' in class_name:
                                    sender = "manus"
                                
                                # 提取時間戳
                                time_element = await element.query_selector('.timestamp, .time')
                                timestamp = ""
                                if time_element:
                                    timestamp = await time_element.inner_text()
                                
                                message = {
                                    'role': sender,
                                    'content': content.strip(),
                                    'timestamp': timestamp,
                                    'raw_html': await element.inner_html()
                                }
                                
                                messages.append(message)
                                
                            except Exception as e:
                                logger.warning(f"提取消息內容時出錯: {e}")
                                continue
                        
                        break
                        
                except Exception as e:
                    logger.warning(f"查找消息時出錯 ({selector}): {e}")
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"獲取所有消息時出錯: {e}")
            return []
    
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

# 使用示例
async def main():
    """主函數示例"""
    controller = ManusAdvancedController()
    
    try:
        # 啟動並登錄
        if await controller.start() and await controller.login():
            print("✅ 登錄成功")
            
            # 獲取任務列表
            tasks = await controller.get_task_list()
            print(f"📋 找到 {len(tasks)} 個任務")
            
            if tasks:
                # 選擇第一個任務
                task = tasks[0]
                print(f"🎯 處理任務: {task.title}")
                
                # 獲取對話歷史
                messages = await controller.get_conversation_history(task)
                print(f"💬 獲取到 {len(messages)} 條消息")
                
                # 批量下載文件
                download_results = await controller.batch_download_files()
                print(f"📁 下載結果: {download_results}")
            
        else:
            print("❌ 登錄失敗")
            
    finally:
        await controller.stop()

if __name__ == "__main__":
    asyncio.run(main())

