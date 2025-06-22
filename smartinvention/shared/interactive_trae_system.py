#!/usr/bin/env python3
"""
交互式TRAE-Manus智能介入系統
連接TRAE，接收用戶輸入，智能分析並生成Manus回答
"""

import asyncio
import subprocess
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import sys
import os

class InteractiveTRAESystem:
    """交互式TRAE系統"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # SSH配置
        self.ssh_config = {
            "host": "serveo.net",
            "port": 41269,
            "user": "alexchuang",
            "password": "123456"
        }
        
        # TRAE配置
        self.trae_session = None
        self.is_connected = False
        
        # 智能分析配置
        self.trigger_keywords = [
            "幫助", "help", "問題", "困難", "卡住", "不知道",
            "怎麼辦", "求助", "急", "緊急", "錯誤", "失敗",
            "bug", "error", "issue", "stuck", "confused"
        ]
        
        self.emotion_keywords = {
            "negative": ["生氣", "憤怒", "失望", "沮喪", "煩躁", "困擾", "痛苦", "難過", 
                        "angry", "frustrated", "disappointed", "upset", "annoyed"],
            "urgent": ["急", "緊急", "快", "馬上", "立即", "urgent", "asap", "quickly", "immediately"],
            "confused": ["不懂", "不明白", "搞不清楚", "confused", "don't understand", "unclear"]
        }
        
        # 回答模板
        self.response_templates = {
            "help_request": [
                "我來幫助您解決這個問題。讓我詳細了解一下情況：",
                "我注意到您需要協助，讓我來幫您分析這個問題：",
                "我很樂意幫助您。請告訴我更多詳細信息，這樣我能提供更準確的建議："
            ],
            "technical_issue": [
                "這看起來是一個技術問題。讓我為您提供一些解決方案：",
                "我理解您遇到的技術困難。以下是一些可能的解決方法：",
                "針對您提到的技術問題，我建議您嘗試以下步驟："
            ],
            "emotional_support": [
                "我理解您現在可能感到困擾。讓我們一步步來解決這個問題：",
                "請不要擔心，這種問題是可以解決的。讓我來幫助您：",
                "我明白這可能讓您感到沮喪，但我們可以一起找到解決方案："
            ],
            "clarification": [
                "為了更好地幫助您，我需要了解更多詳細信息：",
                "讓我確認一下我的理解是否正確：",
                "為了提供最準確的建議，請您詳細描述一下："
            ]
        }
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger("InteractiveTRAE")
        logger.setLevel(logging.INFO)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        return logger
    
    async def connect_trae(self) -> bool:
        """連接TRAE"""
        try:
            self.logger.info("🔗 正在連接TRAE...")
            
            # 測試SSH連接
            test_cmd = [
                "ssh", 
                "-p", str(self.ssh_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                "echo 'SSH連接測試成功'"
            ]
            
            process = subprocess.Popen(
                test_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=f"{self.ssh_config['password']}\n", timeout=15)
            
            if process.returncode == 0:
                self.logger.info("✅ SSH連接成功")
                self.is_connected = True
                
                # 檢查TRAE是否可用
                await self._check_trae_availability()
                return True
            else:
                self.logger.error(f"SSH連接失敗: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"連接TRAE失敗: {e}")
            return False
    
    async def _check_trae_availability(self):
        """檢查TRAE可用性"""
        try:
            self.logger.info("🔍 檢查TRAE可用性...")
            
            # 檢查TRAE命令是否存在
            check_cmd = [
                "ssh",
                "-p", str(self.ssh_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                "which trae || echo 'TRAE not found'"
            ]
            
            process = subprocess.Popen(
                check_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=f"{self.ssh_config['password']}\n")
            
            if "trae" in stdout and "not found" not in stdout:
                self.logger.info("✅ TRAE可用")
            else:
                self.logger.warning("⚠️ TRAE命令未找到，將使用模擬模式")
                
        except Exception as e:
            self.logger.error(f"檢查TRAE可用性失敗: {e}")
    
    async def send_to_trae(self, message: str) -> Optional[str]:
        """發送消息到TRAE並獲取回應"""
        try:
            self.logger.info(f"📤 發送到TRAE: {message[:50]}...")
            
            # 構建TRAE命令
            trae_cmd = [
                "ssh",
                "-p", str(self.ssh_config["port"]),
                "-o", "StrictHostKeyChecking=no",
                f"{self.ssh_config['user']}@{self.ssh_config['host']}",
                f"echo '{message}' | trae"
            ]
            
            process = subprocess.Popen(
                trae_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=f"{self.ssh_config['password']}\n",
                timeout=30
            )
            
            if process.returncode == 0 and stdout.strip():
                response = stdout.strip()
                self.logger.info("✅ TRAE回應成功")
                return response
            else:
                self.logger.warning(f"TRAE回應失敗: {stderr}")
                # 返回模擬回應
                return self._generate_simulated_response(message)
                
        except subprocess.TimeoutExpired:
            self.logger.error("TRAE回應超時")
            return self._generate_simulated_response(message)
        except Exception as e:
            self.logger.error(f"發送到TRAE失敗: {e}")
            return self._generate_simulated_response(message)
    
    def _generate_simulated_response(self, message: str) -> str:
        """生成模擬的TRAE回應"""
        return f"基於您的問題「{message[:30]}...」，我建議您考慮以下幾個方面來解決這個問題..."
    
    def analyze_intervention_need(self, user_input: str) -> Dict[str, Any]:
        """分析是否需要介入"""
        analysis = {
            "needs_intervention": False,
            "intervention_type": None,
            "confidence": 0.0,
            "triggers": [],
            "urgency": "low",
            "emotion": "neutral"
        }
        
        user_input_lower = user_input.lower()
        
        # 1. 檢查關鍵詞觸發
        keyword_triggers = []
        for keyword in self.trigger_keywords:
            if keyword.lower() in user_input_lower:
                keyword_triggers.append(keyword)
        
        if keyword_triggers:
            analysis["triggers"].append({
                "type": "keyword",
                "keywords": keyword_triggers,
                "confidence": min(len(keyword_triggers) * 0.3, 1.0)
            })
        
        # 2. 檢查情緒
        emotion_score = 0
        detected_emotions = []
        
        for emotion_type, words in self.emotion_keywords.items():
            emotion_count = sum(1 for word in words if word in user_input_lower)
            if emotion_count > 0:
                emotion_score += emotion_count * 0.2
                detected_emotions.append(emotion_type)
        
        if emotion_score > 0:
            analysis["triggers"].append({
                "type": "emotion",
                "emotions": detected_emotions,
                "confidence": min(emotion_score, 1.0)
            })
            analysis["emotion"] = detected_emotions[0] if detected_emotions else "neutral"
        
        # 3. 檢查緊急程度
        urgent_words = self.emotion_keywords["urgent"]
        urgent_count = sum(1 for word in urgent_words if word in user_input_lower)
        
        if urgent_count > 0:
            analysis["urgency"] = "high"
            analysis["triggers"].append({
                "type": "urgency",
                "confidence": min(urgent_count * 0.4, 1.0)
            })
        
        # 4. 檢查問號和疑問詞
        question_indicators = ["?", "？", "如何", "怎麼", "為什麼", "what", "how", "why", "when", "where"]
        question_count = sum(1 for indicator in question_indicators if indicator in user_input_lower)
        
        if question_count > 0:
            analysis["triggers"].append({
                "type": "question",
                "confidence": min(question_count * 0.2, 1.0)
            })
        
        # 5. 計算總體信心度
        if analysis["triggers"]:
            total_confidence = sum(trigger["confidence"] for trigger in analysis["triggers"])
            analysis["confidence"] = min(total_confidence / len(analysis["triggers"]), 1.0)
            
            # 判斷是否需要介入
            if analysis["confidence"] > 0.3:  # 信心度閾值
                analysis["needs_intervention"] = True
                
                # 確定介入類型
                if any(t["type"] == "emotion" for t in analysis["triggers"]):
                    analysis["intervention_type"] = "emotional_support"
                elif any(t["type"] == "urgency" for t in analysis["triggers"]):
                    analysis["intervention_type"] = "urgent_help"
                elif any(t["type"] == "keyword" for t in analysis["triggers"]):
                    analysis["intervention_type"] = "technical_help"
                else:
                    analysis["intervention_type"] = "general_help"
        
        return analysis
    
    def generate_manus_response(self, user_input: str, trae_response: str, analysis: Dict[str, Any]) -> str:
        """生成Manus回應"""
        try:
            if not analysis["needs_intervention"]:
                return f"根據TRAE的回應：{trae_response}"
            
            intervention_type = analysis["intervention_type"]
            urgency = analysis["urgency"]
            emotion = analysis["emotion"]
            
            # 選擇合適的開場白
            if intervention_type == "emotional_support":
                opening = self._get_random_template("emotional_support")
            elif intervention_type == "urgent_help":
                opening = "我理解這是一個緊急問題，讓我立即為您提供幫助："
            elif intervention_type == "technical_help":
                opening = self._get_random_template("technical_issue")
            else:
                opening = self._get_random_template("help_request")
            
            # 構建完整回應
            response_parts = [opening]
            
            # 添加TRAE的回應（經過處理）
            processed_trae_response = self._process_trae_response(trae_response, analysis)
            response_parts.append(processed_trae_response)
            
            # 根據情況添加額外建議
            if urgency == "high":
                response_parts.append("如果這是緊急情況，建議您也可以考慮尋求即時支援。")
            
            if emotion in ["negative", "confused"]:
                response_parts.append("請不要擔心，我們會一步步解決這個問題。")
            
            # 添加後續引導
            response_parts.append("如果您需要更多協助或有其他問題，請隨時告訴我。")
            
            return "\n\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"生成Manus回應失敗: {e}")
            return f"基於您的問題，這裡是相關的回應：\n\n{trae_response}"
    
    def _get_random_template(self, template_type: str) -> str:
        """獲取隨機模板"""
        import random
        templates = self.response_templates.get(template_type, ["讓我來幫助您："])
        return random.choice(templates)
    
    def _process_trae_response(self, trae_response: str, analysis: Dict[str, Any]) -> str:
        """處理TRAE回應"""
        # 清理和格式化TRAE回應
        processed = trae_response.strip()
        
        # 如果回應太短，添加更多內容
        if len(processed) < 50:
            processed += "\n\n讓我為您提供更詳細的說明和建議。"
        
        # 根據分析結果調整語調
        if analysis["emotion"] == "negative":
            processed = "我理解您的困擾。" + processed
        elif analysis["urgency"] == "high":
            processed = "針對您的緊急需求，" + processed
        
        return processed
    
    async def interactive_session(self):
        """交互式會話"""
        print("=" * 60)
        print("🤖 TRAE-Manus智能介入系統")
        print("=" * 60)
        print("功能說明：")
        print("1. 輸入您的問題")
        print("2. 系統會調用TRAE分析")
        print("3. 智能判斷是否需要介入")
        print("4. 生成適合Manus的回答")
        print("5. 輸入 'quit' 或 'exit' 退出")
        print("=" * 60)
        
        # 連接TRAE
        if not await self.connect_trae():
            print("❌ 無法連接TRAE，將使用模擬模式")
        
        session_count = 0
        
        while True:
            try:
                print(f"\n📝 會話 #{session_count + 1}")
                print("-" * 40)
                
                # 獲取用戶輸入
                user_input = input("🙋 請輸入您的問題: ").strip()
                
                if not user_input:
                    print("⚠️ 請輸入有效的問題")
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 感謝使用，再見！")
                    break
                
                print(f"\n🔍 正在分析您的問題...")
                
                # 1. 智能分析
                analysis = self.analyze_intervention_need(user_input)
                
                print(f"📊 分析結果:")
                print(f"   需要介入: {'是' if analysis['needs_intervention'] else '否'}")
                print(f"   信心度: {analysis['confidence']:.2f}")
                print(f"   緊急程度: {analysis['urgency']}")
                print(f"   情緒狀態: {analysis['emotion']}")
                
                if analysis['triggers']:
                    print(f"   觸發因素: {', '.join([t['type'] for t in analysis['triggers']])}")
                
                # 2. 調用TRAE
                print(f"\n🤖 正在調用TRAE...")
                trae_response = await self.send_to_trae(user_input)
                
                if trae_response:
                    print(f"📥 TRAE原始回應:")
                    print(f"   {trae_response[:100]}{'...' if len(trae_response) > 100 else ''}")
                
                # 3. 生成Manus回應
                print(f"\n🎯 生成Manus回應...")
                manus_response = self.generate_manus_response(user_input, trae_response or "", analysis)
                
                # 4. 顯示最終結果
                print(f"\n" + "=" * 60)
                print(f"📋 Manus回答 (可直接複製使用):")
                print(f"=" * 60)
                print(manus_response)
                print(f"=" * 60)
                
                # 保存記錄
                await self._save_session_record(session_count, user_input, analysis, trae_response, manus_response)
                
                session_count += 1
                
                # 詢問是否繼續
                print(f"\n💡 提示: 您可以繼續輸入問題，或輸入 'quit' 退出")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 用戶中斷，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 處理過程中發生錯誤: {e}")
                print("請重試或輸入 'quit' 退出")
    
    async def _save_session_record(self, session_id: int, user_input: str, analysis: Dict, trae_response: str, manus_response: str):
        """保存會話記錄"""
        try:
            record = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "analysis": analysis,
                "trae_response": trae_response,
                "manus_response": manus_response
            }
            
            # 創建記錄目錄
            records_dir = Path("session_records")
            records_dir.mkdir(exist_ok=True)
            
            # 保存記錄
            record_file = records_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}.json"
            
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"會話記錄已保存: {record_file}")
            
        except Exception as e:
            self.logger.error(f"保存會話記錄失敗: {e}")

async def main():
    """主函數"""
    try:
        system = InteractiveTRAESystem()
        await system.interactive_session()
    except Exception as e:
        print(f"系統錯誤: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))

