#!/usr/bin/env python3
"""
EC2到Mac的Manus操作腳本
通過SSH隧道連接到Mac並執行Playwright操作
"""

import asyncio
import subprocess
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

class EC2ToMacOperator:
    """EC2到Mac的操作器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # SSH配置
        self.ssh_configs = [
            {
                "name": "serveo_tunnel",
                "host": "serveo.net",
                "port": 41269,
                "user": "alexchuang",
                "password": "123456"
            },
            {
                "name": "direct_ip",
                "host": "your-mac-ip",  # 如果有直接IP
                "port": 22,
                "user": "alexchuang",
                "password": "123456"
            }
        ]
        
        self.active_config = None
        self.mac_script_path = "/tmp/manus_operator.py"
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger("EC2ToMac")
        logger.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        return logger
    
    async def test_connections(self) -> bool:
        """測試所有可能的連接"""
        self.logger.info("🔍 測試Mac連接...")
        
        for config in self.ssh_configs:
            self.logger.info(f"測試連接: {config['name']} ({config['host']}:{config['port']})")
            
            if await self._test_ssh_connection(config):
                self.active_config = config
                self.logger.info(f"✅ 連接成功: {config['name']}")
                return True
            else:
                self.logger.warning(f"❌ 連接失敗: {config['name']}")
        
        self.logger.error("所有連接方式都失敗")
        return False
    
    async def _test_ssh_connection(self, config: Dict) -> bool:
        """測試SSH連接"""
        try:
            cmd = [
                "ssh",
                "-p", str(config["port"]),
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                "-o", "BatchMode=yes",  # 非交互模式
                f"{config['user']}@{config['host']}",
                "echo 'connection_test_success'"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=f"{config['password']}\n",
                timeout=15
            )
            
            return process.returncode == 0 and "connection_test_success" in stdout
            
        except Exception as e:
            self.logger.debug(f"連接測試失敗: {e}")
            return False
    
    async def deploy_script_to_mac(self) -> bool:
        """部署腳本到Mac"""
        if not self.active_config:
            self.logger.error("沒有可用的Mac連接")
            return False
        
        self.logger.info("📦 部署腳本到Mac...")
        
        try:
            # 創建簡化的Mac端腳本
            mac_script = self._create_mac_script()
            
            # 將腳本寫入臨時文件
            temp_script = "/tmp/deploy_to_mac.py"
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(mac_script)
            
            # 通過SSH複製腳本到Mac
            scp_cmd = [
                "scp",
                "-P", str(self.active_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                temp_script,
                f"{self.active_config['user']}@{self.active_config['host']}:{self.mac_script_path}"
            ]
            
            process = subprocess.Popen(
                scp_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=f"{self.active_config['password']}\n",
                timeout=30
            )
            
            if process.returncode == 0:
                self.logger.info("✅ 腳本部署成功")
                return True
            else:
                self.logger.error(f"腳本部署失敗: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"部署腳本失敗: {e}")
            return False
    
    def _create_mac_script(self) -> str:
        """創建Mac端執行腳本"""
        return '''#!/usr/bin/env python3
"""
Mac端Manus操作腳本
"""

import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright

class MacManusOperator:
    def __init__(self, manus_url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.manus_url = manus_url
        self.browser = None
        self.page = None
    
    async def initialize(self):
        """初始化Playwright"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=False)
            context = await self.browser.new_context()
            self.page = await context.new_page()
            
            print(f"🌐 導航到: {self.manus_url}")
            await self.page.goto(self.manus_url, wait_until='networkidle')
            
            # 等待頁面加載
            await asyncio.sleep(5)
            
            print("✅ 初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            return False
    
    async def extract_conversations(self):
        """提取對話歷史"""
        try:
            print("📜 提取對話歷史...")
            
            # 滾動加載內容
            await self._scroll_to_load_all()
            
            # 查找消息元素
            message_selectors = [
                '.message',
                '.chat-message', 
                '.conversation-message',
                '[data-testid="message"]'
            ]
            
            messages = []
            for selector in message_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    print(f"使用選擇器 '{selector}' 找到 {len(elements)} 個消息")
                    
                    for i, element in enumerate(elements):
                        try:
                            content = await element.inner_text()
                            if content.strip():
                                messages.append({
                                    'id': f'msg_{i}',
                                    'content': content.strip(),
                                    'timestamp': datetime.now().isoformat(),
                                    'index': i
                                })
                        except:
                            continue
                    break
            
            print(f"✅ 提取了 {len(messages)} 條對話")
            return messages
            
        except Exception as e:
            print(f"❌ 提取對話失敗: {e}")
            return []
    
    async def _scroll_to_load_all(self):
        """滾動加載所有內容"""
        try:
            print("📜 滾動加載內容...")
            
            last_height = 0
            for i in range(20):  # 最多滾動20次
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                print(f"滾動第 {i+1} 次")
            
            print("✅ 滾動完成")
            
        except Exception as e:
            print(f"滾動失敗: {e}")
    
    async def send_message(self, message):
        """發送消息"""
        try:
            print(f"📤 發送消息: {message[:30]}...")
            
            # 查找輸入框
            input_selectors = [
                'textarea[placeholder*="輸入"]',
                'textarea[placeholder*="input"]', 
                'textarea',
                '.input-box',
                '.message-input'
            ]
            
            input_box = None
            for selector in input_selectors:
                input_box = await self.page.query_selector(selector)
                if input_box and await input_box.is_visible():
                    print(f"找到輸入框: {selector}")
                    break
            
            if not input_box:
                print("❌ 找不到輸入框")
                return False
            
            # 輸入消息
            await input_box.fill(message)
            await asyncio.sleep(1)
            
            # 查找發送按鈕
            send_selectors = [
                'button[type="submit"]',
                '.send-button',
                'button:has-text("發送")',
                'button:has-text("Send")'
            ]
            
            send_button = None
            for selector in send_selectors:
                send_button = await self.page.query_selector(selector)
                if send_button and await send_button.is_visible():
                    print(f"找到發送按鈕: {selector}")
                    break
            
            if send_button:
                await send_button.click()
            else:
                await input_box.press('Enter')
            
            await asyncio.sleep(2)
            print("✅ 消息發送成功")
            return True
            
        except Exception as e:
            print(f"❌ 發送消息失敗: {e}")
            return False
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.browser:
                await self.browser.close()
            print("✅ 清理完成")
        except Exception as e:
            print(f"清理失敗: {e}")

async def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("用法: python3 script.py <action> [args]")
        print("actions: conversations, send, test")
        return
    
    action = sys.argv[1]
    operator = MacManusOperator()
    
    try:
        if not await operator.initialize():
            return
        
        if action == "conversations":
            messages = await operator.extract_conversations()
            print(json.dumps(messages, ensure_ascii=False, indent=2))
            
        elif action == "send":
            if len(sys.argv) < 3:
                print("請提供要發送的消息")
                return
            message = sys.argv[2]
            await operator.send_message(message)
            
        elif action == "test":
            print("🧪 執行測試...")
            messages = await operator.extract_conversations()
            print(f"找到 {len(messages)} 條對話")
            
            if messages:
                print("最新對話:")
                for msg in messages[-3:]:
                    print(f"  {msg['content'][:50]}...")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
    finally:
        await operator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    async def execute_on_mac(self, action: str, *args) -> Dict[str, Any]:
        """在Mac上執行操作"""
        if not self.active_config:
            return {"success": False, "error": "沒有可用的Mac連接"}
        
        self.logger.info(f"🚀 在Mac上執行: {action}")
        
        try:
            # 構建SSH命令
            ssh_cmd = [
                "ssh",
                "-p", str(self.active_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                f"{self.active_config['user']}@{self.active_config['host']}",
                f"cd /tmp && python3 {self.mac_script_path} {action} {' '.join(args)}"
            ]
            
            process = subprocess.Popen(
                ssh_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=f"{self.active_config['password']}\n",
                timeout=120  # 2分鐘超時
            )
            
            if process.returncode == 0:
                self.logger.info("✅ Mac執行成功")
                return {
                    "success": True,
                    "output": stdout,
                    "action": action
                }
            else:
                self.logger.error(f"Mac執行失敗: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "action": action
                }
                
        except subprocess.TimeoutExpired:
            self.logger.error("Mac執行超時")
            return {"success": False, "error": "執行超時"}
        except Exception as e:
            self.logger.error(f"Mac執行異常: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_full_demo(self):
        """運行完整演示"""
        self.logger.info("🎬 開始完整演示...")
        
        # 1. 測試連接
        if not await self.test_connections():
            self.logger.error("無法連接到Mac")
            return
        
        # 2. 部署腳本
        if not await self.deploy_script_to_mac():
            self.logger.error("無法部署腳本到Mac")
            return
        
        # 3. 執行測試
        self.logger.info("🧪 執行測試...")
        result = await self.execute_on_mac("test")
        if result["success"]:
            print("測試結果:")
            print(result["output"])
        
        # 4. 提取對話
        self.logger.info("📜 提取對話歷史...")
        result = await self.execute_on_mac("conversations")
        if result["success"]:
            print("對話歷史:")
            print(result["output"])
        
        # 5. 發送測試消息
        self.logger.info("📤 發送測試消息...")
        test_message = "這是從EC2通過SSH發送到Manus的測試消息"
        result = await self.execute_on_mac("send", f'"{test_message}"')
        if result["success"]:
            print("消息發送結果:")
            print(result["output"])
        
        self.logger.info("✅ 演示完成")

async def main():
    """主函數"""
    operator = EC2ToMacOperator()
    await operator.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main())

