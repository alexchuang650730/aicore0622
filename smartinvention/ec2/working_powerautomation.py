#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PowerAutomation 工作版本 - 經過測試驗證的完整系統
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
import os

class WorkingPowerAutomation:
    """經過驗證的PowerAutomation系統"""
    
    def __init__(self):
        self.setup_logging()
        self.config = {
            "ec2_endpoint": "http://18.212.97.173:8000",
            "local_endpoint": "http://localhost:8000",  # 用於測試
            "sync_interval": 30,
            "max_retries": 3
        }
        
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('powerautomation_working.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_test_conversation(self, user_message: str = "我想要生成一個貪吃蛇") -> Dict:
        """創建測試對話數據"""
        current_time = datetime.now().isoformat()
        
        conversation = {
            "id": f"working_test_{int(time.time())}",
            "user_message": user_message,
            "assistant_message": "",
            "status": "正在分析問題...",
            "timestamp": current_time,
            "session_id": f"working_session_{datetime.now().strftime('%Y%m%d')}",
            "metadata": {
                "source": "working_test",
                "ui_state": {
                    "user_avatar": "Alex Chuang",
                    "assistant_status": "analyzing",
                    "interface": "trae_desktop"
                },
                "extraction_method": "direct_input",
                "request_type": "code_generation",
                "programming_language": "python",
                "project_type": "game"
            },
            "source": "trae_working",
            "sync_time": current_time
        }
        
        # 添加智能分析
        conversation["intervention_analysis"] = self.analyze_conversation(conversation)
        
        return conversation
    
    def analyze_conversation(self, conversation: Dict) -> Dict:
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
        
        recommended_action = None
        if "specific_game_request" in triggered_categories and "貪吃蛇" in user_message:
            recommended_action = {
                "action_type": "provide_code_template",
                "message": "我可以幫您生成一個完整的貪吃蛇遊戲！包含HTML、CSS和JavaScript的完整實現。",
                "follow_up": "需要我提供基礎版本還是進階版本？",
                "code_template": "snake_game_template",
                "estimated_time": "5分鐘"
            }
        
        return {
            "intervention_needed": intervention_needed,
            "confidence_score": min(confidence_score, 1.0),
            "triggered_categories": triggered_categories,
            "analysis_time": datetime.now().isoformat(),
            "recommended_action": recommended_action,
            "priority": "high" if confidence_score > 0.7 else "medium" if confidence_score > 0.4 else "low"
        }
    
    def test_ec2_connection(self) -> bool:
        """測試EC2連接"""
        try:
            response = requests.get(f"{self.config['ec2_endpoint']}/api/health", timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ EC2連接正常")
                return True
            else:
                self.logger.error(f"❌ EC2響應錯誤: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ EC2連接失敗: {e}")
            return False
    
    def sync_conversation_to_ec2(self, conversation: Dict) -> bool:
        """同步單個對話到EC2"""
        try:
            sync_data = {
                "conversations": [conversation],
                "sync_metadata": {
                    "total_count": 1,
                    "sync_time": datetime.now().isoformat(),
                    "source_system": "powerautomation_working",
                    "sync_type": "single_conversation"
                }
            }
            
            response = requests.post(
                f"{self.config['ec2_endpoint']}/api/sync/conversations",
                json=sync_data,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ 成功同步對話: {result.get('message', '成功')}")
                return True
            else:
                self.logger.error(f"❌ 同步失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 同步過程出錯: {e}")
            return False
    
    def get_ec2_statistics(self) -> Optional[Dict]:
        """獲取EC2統計信息"""
        try:
            response = requests.get(f"{self.config['ec2_endpoint']}/api/statistics", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ 獲取統計失敗: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ 獲取統計出錯: {e}")
            return None
    
    def get_interventions_needed(self) -> Optional[List[Dict]]:
        """獲取需要介入的對話"""
        try:
            response = requests.get(f"{self.config['ec2_endpoint']}/api/interventions/needed", timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get("interventions", [])
            else:
                self.logger.error(f"❌ 獲取介入需求失敗: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ 獲取介入需求出錯: {e}")
            return None
    
    def run_complete_test(self) -> Dict:
        """運行完整測試"""
        test_result = {
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "overall_success": False
        }
        
        self.logger.info("🧪 開始PowerAutomation完整測試")
        
        # 1. 測試EC2連接
        self.logger.info("1. 測試EC2連接...")
        test_result["tests"]["ec2_connection"] = self.test_ec2_connection()
        
        if not test_result["tests"]["ec2_connection"]:
            self.logger.error("❌ EC2連接失敗，停止測試")
            test_result["end_time"] = datetime.now().isoformat()
            return test_result
        
        # 2. 創建測試對話
        self.logger.info("2. 創建測試對話...")
        test_conversation = self.create_test_conversation()
        test_result["tests"]["conversation_creation"] = True
        self.logger.info(f"✅ 創建測試對話: {test_conversation['user_message']}")
        
        # 3. 測試對話同步
        self.logger.info("3. 測試對話同步...")
        test_result["tests"]["conversation_sync"] = self.sync_conversation_to_ec2(test_conversation)
        
        # 4. 測試統計信息
        self.logger.info("4. 測試統計信息...")
        stats = self.get_ec2_statistics()
        test_result["tests"]["statistics"] = stats is not None
        if stats:
            test_result["statistics"] = stats
            self.logger.info(f"✅ 統計信息: {stats['statistics']['total_conversations']} 條對話")
        
        # 5. 測試介入需求
        self.logger.info("5. 測試介入需求...")
        interventions = self.get_interventions_needed()
        test_result["tests"]["interventions"] = interventions is not None
        if interventions:
            test_result["interventions_count"] = len(interventions)
            self.logger.info(f"✅ 介入需求: {len(interventions)} 條需要介入")
        
        # 計算總體成功率
        successful_tests = sum(1 for success in test_result["tests"].values() if success)
        total_tests = len(test_result["tests"])
        test_result["success_rate"] = successful_tests / total_tests
        test_result["overall_success"] = test_result["success_rate"] >= 0.8
        
        test_result["end_time"] = datetime.now().isoformat()
        
        if test_result["overall_success"]:
            self.logger.info(f"🎉 測試完成！成功率: {test_result['success_rate']:.1%}")
        else:
            self.logger.warning(f"⚠️  測試部分失敗，成功率: {test_result['success_rate']:.1%}")
        
        return test_result
    
    def generate_snake_game_response(self) -> str:
        """生成貪吃蛇遊戲的智能回覆"""
        return """我可以為您生成一個完整的貪吃蛇遊戲！這個遊戲將包含：

🎮 **遊戲功能**
- 經典貪吃蛇玩法
- 方向鍵控制
- 分數統計
- 遊戲結束檢測
- 重新開始功能

💻 **技術實現**
- HTML5 Canvas 繪圖
- JavaScript 遊戲邏輯
- CSS 樣式設計
- 響應式設計

🚀 **立即開始**
我可以提供：
1. **基礎版本** - 簡單的貪吃蛇遊戲
2. **進階版本** - 包含特效和音效
3. **自定義版本** - 根據您的需求調整

請告訴我您想要哪個版本，我立即為您生成完整的代碼！"""

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation 工作版本")
    parser.add_argument("--action", choices=["test", "sync", "stats", "interventions", "demo"], 
                       default="test", help="執行動作")
    parser.add_argument("--message", type=str, default="我想要生成一個貪吃蛇", 
                       help="測試消息內容")
    
    args = parser.parse_args()
    
    system = WorkingPowerAutomation()
    
    if args.action == "test":
        # 運行完整測試
        result = system.run_complete_test()
        print("\n" + "="*50)
        print("📊 測試結果摘要")
        print("="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.action == "sync":
        # 同步單個對話
        conversation = system.create_test_conversation(args.message)
        success = system.sync_conversation_to_ec2(conversation)
        print(f"同步結果: {'成功' if success else '失敗'}")
        
    elif args.action == "stats":
        # 獲取統計信息
        stats = system.get_ec2_statistics()
        if stats:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("無法獲取統計信息")
            
    elif args.action == "interventions":
        # 獲取介入需求
        interventions = system.get_interventions_needed()
        if interventions:
            print(f"需要介入的對話: {len(interventions)} 條")
            for i, intervention in enumerate(interventions, 1):
                print(f"\n{i}. {intervention['user_message']}")
                print(f"   優先級: {intervention['priority']}")
                print(f"   信心度: {intervention['confidence_score']}")
        else:
            print("無法獲取介入需求")
            
    elif args.action == "demo":
        # 演示模式
        print("🎮 PowerAutomation 演示模式")
        print("="*50)
        
        # 創建貪吃蛇對話
        conversation = system.create_test_conversation("我想要生成一個貪吃蛇")
        print(f"用戶問題: {conversation['user_message']}")
        
        # 分析結果
        analysis = conversation["intervention_analysis"]
        print(f"介入分析: {'需要介入' if analysis['intervention_needed'] else '不需要介入'}")
        print(f"信心度: {analysis['confidence_score']:.1%}")
        print(f"優先級: {analysis['priority']}")
        
        # 智能回覆
        if analysis["intervention_needed"]:
            response = system.generate_snake_game_response()
            print(f"\n智能回覆:\n{response}")
        
        # 同步到EC2
        print(f"\n同步到EC2: {'成功' if system.sync_conversation_to_ec2(conversation) else '失敗'}")

if __name__ == "__main__":
    main()

