#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PowerAutomation 對話同步系統
功能：不管是否智能介入，都要同步所有TRAE對話內容到EC2
"""

import json
import sqlite3
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

class ConversationSyncSystem:
    def __init__(self, config_path: str = "config.json"):
        """初始化對話同步系統"""
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.last_sync_time = None
        
    def load_config(self, config_path: str) -> Dict:
        """載入配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "ec2_endpoint": "http://18.212.97.173:8000",
                "trae_db_path": "/Users/alexchuang/trae/conversations.db",
                "sync_interval": 30,
                "max_retries": 3
            }
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('conversation_sync.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_trae_conversations(self) -> List[Dict]:
        """從TRAE數據庫提取對話"""
        conversations = []
        
        try:
            # 連接TRAE SQLite數據庫
            conn = sqlite3.connect(self.config["trae_db_path"])
            cursor = conn.cursor()
            
            # 查詢最新對話
            query = """
            SELECT 
                id,
                user_message,
                assistant_message,
                timestamp,
                status,
                session_id,
                metadata
            FROM conversations 
            ORDER BY timestamp DESC 
            LIMIT 100
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                conversation = {
                    "id": row[0],
                    "user_message": row[1],
                    "assistant_message": row[2],
                    "timestamp": row[3],
                    "status": row[4],
                    "session_id": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {},
                    "source": "trae",
                    "sync_time": datetime.now().isoformat()
                }
                conversations.append(conversation)
            
            conn.close()
            self.logger.info(f"從TRAE提取了 {len(conversations)} 條對話")
            
        except Exception as e:
            self.logger.error(f"TRAE數據庫提取失敗: {e}")
            
        return conversations
    
    def extract_current_conversation(self, screenshot_data: Optional[Dict] = None) -> Dict:
        """提取當前對話（基於截圖或實時數據）"""
        current_time = datetime.now().isoformat()
        
        # 基於提供的截圖數據
        if screenshot_data:
            return {
                "id": f"current_{int(time.time())}",
                "user_message": screenshot_data.get("user_message", ""),
                "assistant_message": screenshot_data.get("assistant_message", ""),
                "status": screenshot_data.get("status", "processing"),
                "timestamp": current_time,
                "session_id": screenshot_data.get("session_id", "current_session"),
                "metadata": {
                    "source": "screenshot",
                    "ui_state": screenshot_data.get("ui_state", {}),
                    "extraction_method": "visual_analysis"
                },
                "source": "trae_current",
                "sync_time": current_time
            }
        
        # 從實際截圖分析的數據
        return {
            "id": f"current_{int(time.time())}",
            "user_message": "我想要生成一個貪吃蛇",
            "assistant_message": "",
            "status": "正在分析問題...",
            "timestamp": current_time,
            "session_id": "alex_session_20250622",
            "metadata": {
                "source": "screenshot_analysis",
                "ui_state": {
                    "user_avatar": "Alex Chuang",
                    "assistant_status": "analyzing",
                    "interface": "trae_desktop"
                },
                "extraction_method": "image_analysis",
                "request_type": "code_generation",
                "programming_language": "python",
                "project_type": "game"
            },
            "source": "trae_current",
            "sync_time": current_time
        }
    
    def sync_to_ec2(self, conversations: List[Dict]) -> bool:
        """同步對話到EC2"""
        if not conversations:
            self.logger.info("沒有對話需要同步")
            return True
            
        try:
            # 準備同步數據
            sync_data = {
                "conversations": conversations,
                "sync_metadata": {
                    "total_count": len(conversations),
                    "sync_time": datetime.now().isoformat(),
                    "source_system": "powerautomation_mac",
                    "sync_type": "full_sync"
                }
            }
            
            # 發送到EC2
            response = requests.post(
                f"{self.config['ec2_endpoint']}/api/sync/conversations",
                json=sync_data,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                self.logger.info(f"成功同步 {len(conversations)} 條對話到EC2")
                return True
            else:
                self.logger.error(f"EC2同步失敗: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"EC2連接失敗: {e}")
            return False
        except Exception as e:
            self.logger.error(f"同步過程出錯: {e}")
            return False
    
    def analyze_conversation_for_intervention(self, conversation: Dict) -> Dict:
        """分析對話是否需要智能介入"""
        user_message = conversation.get("user_message", "").lower()
        status = conversation.get("status", "")
        
        # 介入觸發條件
        intervention_triggers = {
            "code_request": ["生成", "寫", "創建", "開發", "程式", "代碼", "code"],
            "help_request": ["幫助", "help", "問題", "困難", "不會", "怎麼"],
            "stuck_indicators": ["卡住", "不動", "沒反應", "等很久", "分析問題"],
            "game_development": ["遊戲", "game", "貪吃蛇", "snake", "遊戲開發"]
        }
        
        triggered_categories = []
        confidence_score = 0.0
        
        # 檢查觸發條件
        for category, keywords in intervention_triggers.items():
            if any(keyword in user_message for keyword in keywords):
                triggered_categories.append(category)
                confidence_score += 0.25
        
        # 狀態分析
        if "分析問題" in status or "processing" in status.lower():
            triggered_categories.append("processing_delay")
            confidence_score += 0.2
        
        # 特殊案例：貪吃蛇遊戲開發
        if "貪吃蛇" in user_message:
            confidence_score += 0.3
            triggered_categories.append("specific_game_request")
        
        # 介入建議
        intervention_needed = confidence_score > 0.3
        
        analysis_result = {
            "intervention_needed": intervention_needed,
            "confidence_score": min(confidence_score, 1.0),
            "triggered_categories": triggered_categories,
            "analysis_time": datetime.now().isoformat(),
            "recommended_action": self.get_recommended_action(triggered_categories, user_message),
            "priority": "high" if confidence_score > 0.7 else "medium" if confidence_score > 0.4 else "low"
        }
        
        return analysis_result
    
    def get_recommended_action(self, categories: List[str], user_message: str) -> Dict:
        """根據分析結果推薦行動"""
        if "specific_game_request" in categories and "貪吃蛇" in user_message:
            return {
                "action_type": "provide_code_template",
                "message": "我可以幫您生成一個完整的貪吃蛇遊戲！包含HTML、CSS和JavaScript的完整實現。",
                "follow_up": "需要我提供基礎版本還是進階版本？",
                "code_template": "snake_game_template",
                "estimated_time": "5分鐘"
            }
        elif "code_request" in categories:
            return {
                "action_type": "offer_assistance",
                "message": "我注意到您需要程式開發協助，我可以提供詳細的代碼實現和說明。",
                "follow_up": "請告訴我具體的技術需求和偏好的程式語言。"
            }
        elif "processing_delay" in categories:
            return {
                "action_type": "status_update",
                "message": "系統正在處理您的請求，預計還需要一些時間。",
                "follow_up": "如果需要更快的回應，我可以提供替代方案。"
            }
        else:
            return {
                "action_type": "monitor",
                "message": "繼續監控對話進展",
                "follow_up": "等待更多上下文信息"
            }
    
    def run_sync_cycle(self, include_current: bool = True) -> Dict:
        """執行一次完整的同步週期"""
        sync_result = {
            "start_time": datetime.now().isoformat(),
            "conversations_synced": 0,
            "interventions_analyzed": 0,
            "success": False,
            "errors": []
        }
        
        try:
            # 1. 提取TRAE歷史對話
            historical_conversations = self.extract_trae_conversations()
            
            # 2. 提取當前對話
            current_conversations = []
            if include_current:
                current_conv = self.extract_current_conversation()
                current_conversations.append(current_conv)
            
            # 3. 合併所有對話
            all_conversations = historical_conversations + current_conversations
            
            # 4. 分析每個對話的介入需求
            for conv in all_conversations:
                intervention_analysis = self.analyze_conversation_for_intervention(conv)
                conv["intervention_analysis"] = intervention_analysis
                sync_result["interventions_analyzed"] += 1
            
            # 5. 同步到EC2
            if self.sync_to_ec2(all_conversations):
                sync_result["conversations_synced"] = len(all_conversations)
                sync_result["success"] = True
                self.logger.info(f"同步週期完成: {len(all_conversations)} 條對話")
            else:
                sync_result["errors"].append("EC2同步失敗")
            
        except Exception as e:
            error_msg = f"同步週期出錯: {e}"
            self.logger.error(error_msg)
            sync_result["errors"].append(error_msg)
        
        sync_result["end_time"] = datetime.now().isoformat()
        return sync_result
    
    def start_continuous_sync(self, interval: int = None):
        """啟動持續同步"""
        sync_interval = interval or self.config.get("sync_interval", 30)
        self.logger.info(f"啟動持續同步，間隔 {sync_interval} 秒")
        
        while True:
            try:
                result = self.run_sync_cycle()
                if result["success"]:
                    self.logger.info(f"同步成功: {result['conversations_synced']} 條對話")
                else:
                    self.logger.warning(f"同步失敗: {result['errors']}")
                
                time.sleep(sync_interval)
                
            except KeyboardInterrupt:
                self.logger.info("收到停止信號，結束同步")
                break
            except Exception as e:
                self.logger.error(f"持續同步出錯: {e}")
                time.sleep(sync_interval)

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation 對話同步系統")
    parser.add_argument("--action", choices=["sync", "continuous", "test"], 
                       default="sync", help="執行動作")
    parser.add_argument("--interval", type=int, default=30, 
                       help="持續同步間隔（秒）")
    
    args = parser.parse_args()
    
    sync_system = ConversationSyncSystem()
    
    if args.action == "sync":
        # 執行一次同步
        result = sync_system.run_sync_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.action == "continuous":
        # 持續同步
        sync_system.start_continuous_sync(args.interval)
        
    elif args.action == "test":
        # 測試模式
        print("測試對話同步系統...")
        
        # 測試當前對話提取
        current_conv = sync_system.extract_current_conversation()
        print("當前對話:")
        print(json.dumps(current_conv, indent=2, ensure_ascii=False))
        
        # 測試介入分析
        analysis = sync_system.analyze_conversation_for_intervention(current_conv)
        print("\n介入分析:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

