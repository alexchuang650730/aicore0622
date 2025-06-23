"""
TRAE數據庫操作模組
通過SSH連接到Mac，直接訪問TRAE的SQLite數據庫
"""

import sqlite3
import json
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

@dataclass
class TraeConversation:
    """TRAE對話數據結構"""
    id: str
    content: str
    timestamp: datetime
    conversation_type: str
    metadata: Dict[str, Any] = None

class TraeDatabase:
    """TRAE數據庫操作器"""
    
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # SSH配置
        self.ssh_config = {
            "host": "serveo.net",
            "port": 41269,
            "user": "alexchuang",
            "password": "123456"
        }
        
        # TRAE數據庫路徑
        self.trae_db_path = "/Users/alexchuang/Library/Application Support/Trae/User/workspaceStorage/f002a9b85f221075092022809f5a075f/state.vscdb"
        
        # 本地臨時文件
        self.temp_db_path = None
    
    async def connect(self) -> bool:
        """連接到TRAE數據庫"""
        try:
            self.logger.info("🔗 連接到TRAE數據庫...")
            
            # 通過SSH複製數據庫文件到本地
            success = await self._copy_db_from_remote()
            if not success:
                return False
            
            self.logger.info("✅ TRAE數據庫連接成功")
            return True
            
        except Exception as e:
            self.logger.error(f"連接TRAE數據庫失敗: {e}")
            return False
    
    async def _copy_db_from_remote(self) -> bool:
        """從遠程複製數據庫文件"""
        try:
            # 創建臨時文件
            temp_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
            os.close(temp_fd)
            
            # 構建scp命令
            scp_cmd = [
                "scp",
                "-P", str(self.ssh_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                f"{self.ssh_config['user']}@{self.ssh_config['host']}:{self.trae_db_path}",
                self.temp_db_path
            ]
            
            self.logger.debug(f"執行SCP命令: {' '.join(scp_cmd)}")
            
            # 執行scp命令
            process = subprocess.Popen(
                scp_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 發送密碼
            stdout, stderr = process.communicate(input=f"{self.ssh_config['password']}\n")
            
            if process.returncode == 0:
                self.logger.info("✅ 數據庫文件複製成功")
                return True
            else:
                self.logger.error(f"SCP失敗: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"複製數據庫文件失敗: {e}")
            return False
    
    async def get_conversation_history(self, repo_name: Optional[str] = None) -> List[TraeConversation]:
        """獲取對話歷史"""
        if not self.temp_db_path or not os.path.exists(self.temp_db_path):
            self.logger.error("數據庫文件不存在，請先連接")
            return []
        
        conversations = []
        
        try:
            self.logger.info("📜 從TRAE數據庫提取對話歷史...")
            
            with sqlite3.connect(self.temp_db_path) as conn:
                cursor = conn.cursor()
                
                # 查詢對話歷史
                if repo_name:
                    query = """
                    SELECT key, value FROM ItemTable
                    WHERE key LIKE '%input-history%' OR key LIKE '%memento%'
                    AND value LIKE ?
                    ORDER BY key;
                    """
                    cursor.execute(query, (f"%{repo_name}%",))
                else:
                    query = """
                    SELECT key, value FROM ItemTable
                    WHERE key LIKE '%input-history%' OR key LIKE '%memento%'
                    ORDER BY key;
                    """
                    cursor.execute(query)
                
                rows = cursor.fetchall()
                
                for key, value in rows:
                    try:
                        # 解析JSON數據
                        if value:
                            data = json.loads(value)
                            conversation = self._parse_conversation_data(key, data)
                            if conversation:
                                conversations.append(conversation)
                    except json.JSONDecodeError:
                        # 如果不是JSON，直接作為文本處理
                        conversation = TraeConversation(
                            id=key,
                            content=value,
                            timestamp=datetime.now(),
                            conversation_type="text",
                            metadata={"raw_key": key}
                        )
                        conversations.append(conversation)
            
            self.logger.info(f"✅ 成功提取 {len(conversations)} 條對話記錄")
            
        except Exception as e:
            self.logger.error(f"提取對話歷史失敗: {e}")
        
        return conversations
    
    def _parse_conversation_data(self, key: str, data: Any) -> Optional[TraeConversation]:
        """解析對話數據"""
        try:
            if isinstance(data, dict):
                # 處理結構化數據
                content = data.get('content', '') or data.get('text', '') or str(data)
                timestamp = data.get('timestamp')
                
                if timestamp:
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()
                
                return TraeConversation(
                    id=key,
                    content=content,
                    timestamp=timestamp,
                    conversation_type="structured",
                    metadata=data
                )
            
            elif isinstance(data, list):
                # 處理列表數據
                content = "\n".join([str(item) for item in data])
                return TraeConversation(
                    id=key,
                    content=content,
                    timestamp=datetime.now(),
                    conversation_type="list",
                    metadata={"items": data}
                )
            
            else:
                # 處理其他類型數據
                return TraeConversation(
                    id=key,
                    content=str(data),
                    timestamp=datetime.now(),
                    conversation_type="simple",
                    metadata={"raw_data": data}
                )
                
        except Exception as e:
            self.logger.error(f"解析對話數據失敗: {e}")
            return None
    
    async def send_message_to_trae(self, repo_name: str, message: str) -> bool:
        """向TRAE發送消息"""
        try:
            self.logger.info(f"📤 向TRAE發送消息: {message[:50]}...")
            
            # 構建SSH命令來執行TRAE操作
            ssh_cmd = self._build_ssh_command()
            
            # 構建TRAE發送命令
            trae_cmd = f"cd /home/alexchuang/aiengine/trae/git && echo '{message}' | trae-send {repo_name}"
            
            # 執行命令
            full_cmd = ssh_cmd + [trae_cmd]
            
            process = subprocess.Popen(
                full_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=f"{self.ssh_config['password']}\n")
            
            if process.returncode == 0:
                self.logger.info("✅ 消息發送成功")
                
                # 記錄發送日誌
                await self._log_sent_message(repo_name, message, stdout)
                return True
            else:
                self.logger.error(f"發送消息失敗: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"發送消息到TRAE失敗: {e}")
            return False
    
    def _build_ssh_command(self) -> List[str]:
        """構建SSH命令"""
        return [
            "ssh",
            "-p", str(self.ssh_config["port"]),
            "-o", "StrictHostKeyChecking=no",
            f"{self.ssh_config['user']}@{self.ssh_config['host']}"
        ]
    
    async def _log_sent_message(self, repo_name: str, message: str, response: str):
        """記錄發送的消息"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "repo_name": repo_name,
                "message": message,
                "response": response,
                "status": "sent"
            }
            
            # 這裡可以將日誌保存到本地文件或發送到EC2
            self.logger.debug(f"消息發送日誌: {log_entry}")
            
        except Exception as e:
            self.logger.error(f"記錄發送日誌失敗: {e}")
    
    async def generate_intelligent_response(self, conversation_context: List[str], trigger_type: str) -> Optional[str]:
        """生成智能回覆"""
        try:
            self.logger.info(f"🤖 生成智能回覆，觸發類型: {trigger_type}")
            
            # 構建上下文
            context = "\n".join(conversation_context[-5:])  # 最近5條消息
            
            # 根據觸發類型生成不同的提示詞
            prompts = {
                "delay": f"用戶似乎在等待回覆，請根據以下對話上下文提供有幫助的回應：\n{context}",
                "keyword": f"用戶提到了需要幫助的關鍵詞，請提供支援：\n{context}",
                "emotion": f"檢測到用戶可能有負面情緒，請提供安慰和幫助：\n{context}",
                "repetition": f"用戶重複提問，請提供更詳細的解答：\n{context}"
            }
            
            prompt = prompts.get(trigger_type, f"請根據對話上下文提供有幫助的回覆：\n{context}")
            
            # 使用TRAE生成回覆
            response = await self._call_trae_for_generation(prompt)
            
            if response:
                self.logger.info("✅ 智能回覆生成成功")
                return response
            else:
                self.logger.warning("TRAE回覆生成失敗，使用預設回覆")
                return self._get_fallback_response(trigger_type)
                
        except Exception as e:
            self.logger.error(f"生成智能回覆失敗: {e}")
            return self._get_fallback_response(trigger_type)
    
    async def _call_trae_for_generation(self, prompt: str) -> Optional[str]:
        """調用TRAE生成回覆"""
        try:
            # 構建SSH命令調用TRAE
            ssh_cmd = self._build_ssh_command()
            
            # 使用TRAE生成回覆的命令
            trae_cmd = f"echo '{prompt}' | trae-generate"
            
            full_cmd = ssh_cmd + [trae_cmd]
            
            process = subprocess.Popen(
                full_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=f"{self.ssh_config['password']}\n")
            
            if process.returncode == 0 and stdout.strip():
                return stdout.strip()
            else:
                self.logger.warning(f"TRAE生成失敗: {stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"調用TRAE生成失敗: {e}")
            return None
    
    def _get_fallback_response(self, trigger_type: str) -> str:
        """獲取預設回覆"""
        fallback_responses = {
            "delay": "我注意到您可能在等待回覆，讓我來幫助您解決問題。請告訴我您需要什麼協助？",
            "keyword": "我看到您提到需要幫助，我很樂意為您提供支援。請詳細描述您遇到的問題。",
            "emotion": "我理解您可能感到困擾，讓我來幫助您。請不要擔心，我們一起來解決這個問題。",
            "repetition": "我注意到您重複提到這個問題，讓我提供更詳細的解答來幫助您。"
        }
        
        return fallback_responses.get(trigger_type, "我來幫助您解決問題，請告訴我您需要什麼協助？")
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.temp_db_path and os.path.exists(self.temp_db_path):
                os.unlink(self.temp_db_path)
                self.logger.info("✅ 臨時數據庫文件已清理")
        except Exception as e:
            self.logger.error(f"清理資源失敗: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            "connected": self.temp_db_path is not None,
            "db_path": self.trae_db_path,
            "temp_path": self.temp_db_path,
            "ssh_host": f"{self.ssh_config['user']}@{self.ssh_config['host']}:{self.ssh_config['port']}"
        }

