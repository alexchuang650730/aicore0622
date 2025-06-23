"""
完整的Manus-TRAE智能介入系統
整合所有功能模組，提供完整的智能介入服務
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import argparse

# 導入自定義模組
from config import SystemConfig
from manus_operator import ManusOperator, ManusMessage
from trae_database import TraeDatabase, TraeConversation

class IntelligentInterventionSystem:
    """智能介入系統主類"""
    
    def __init__(self, config_path: Optional[str] = None):
        # 加載配置
        if config_path and Path(config_path).exists():
            self.config = SystemConfig.load_from_file(config_path)
        else:
            self.config = SystemConfig()
        
        # 設置日誌
        self.logger = self._setup_logger()
        
        # 初始化組件
        self.manus_operator = ManusOperator(self.config, self.logger)
        self.trae_db = TraeDatabase(self.config, self.logger)
        
        # 系統狀態
        self.is_running = False
        self.start_time = None
        
        # 數據存儲
        self.intervention_history = []
        self.performance_stats = {
            'total_interventions': 0,
            'successful_interventions': 0,
            'failed_interventions': 0,
            'messages_monitored': 0,
            'tasks_monitored': 0
        }
        
        # 學習數據
        self.learning_patterns = {}
        self.trigger_weights = {
            'delay': 1.0,
            'keyword': 0.8,
            'emotion': 0.9,
            'repetition': 0.7
        }
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌系統"""
        logger = logging.getLogger("IntelligentIntervention")
        logger.setLevel(logging.DEBUG if self.config.debug else logging.INFO)
        
        # 清除現有處理器
        logger.handlers.clear()
        
        # 文件處理器
        log_file = Path(self.config.log_dir) / f"system_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def start(self):
        """啟動智能介入系統"""
        if self.is_running:
            self.logger.warning("系統已經在運行中")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        self.logger.info("🚀 啟動Manus-TRAE智能介入系統...")
        self.logger.info(f"📋 系統配置: {self.config.system_name} v{self.config.version}")
        
        try:
            # 啟動TRAE數據庫連接
            self.logger.info("🔗 連接TRAE數據庫...")
            trae_connected = await self.trae_db.connect()
            if not trae_connected:
                self.logger.error("TRAE數據庫連接失敗")
                return False
            
            # 啟動Manus操作器
            self.logger.info("🌐 啟動Manus操作器...")
            await self.manus_operator.start()
            
            # 開始監控循環
            self.logger.info("👁️ 開始智能監控...")
            await self._start_monitoring()
            
        except Exception as e:
            self.logger.error(f"系統啟動失敗: {e}")
            await self.stop()
            return False
        
        return True
    
    async def stop(self):
        """停止系統"""
        self.is_running = False
        self.logger.info("🛑 正在停止智能介入系統...")
        
        try:
            # 停止Manus操作器
            await self.manus_operator.stop()
            
            # 清理TRAE數據庫
            await self.trae_db.cleanup()
            
            # 保存統計數據
            await self._save_performance_stats()
            
            self.logger.info("✅ 系統已安全停止")
            
        except Exception as e:
            self.logger.error(f"停止系統時發生錯誤: {e}")
    
    async def _start_monitoring(self):
        """開始監控循環"""
        self.logger.info("🔍 開始智能監控循環...")
        
        # 啟動監控任務
        tasks = [
            asyncio.create_task(self._monitor_conversations()),
            asyncio.create_task(self._monitor_tasks()),
            asyncio.create_task(self._learning_optimization_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"監控循環錯誤: {e}")
    
    async def _monitor_conversations(self):
        """監控對話"""
        self.logger.info("💬 開始對話監控...")
        
        last_message_count = 0
        last_check_time = datetime.now()
        
        while self.is_running:
            try:
                # 獲取最新對話
                messages = await self.manus_operator.get_conversation_history()
                current_message_count = len(messages)
                
                # 檢查新消息
                if current_message_count > last_message_count:
                    new_messages = messages[last_message_count:]
                    self.logger.info(f"🆕 檢測到 {len(new_messages)} 條新消息")
                    
                    # 分析每條新消息
                    for message in new_messages:
                        await self._analyze_message(message, messages)
                    
                    last_message_count = current_message_count
                    self.performance_stats['messages_monitored'] += len(new_messages)
                
                # 檢查響應延遲
                await self._check_response_delays(messages, last_check_time)
                last_check_time = datetime.now()
                
                await asyncio.sleep(self.config.manus_check_interval)
                
            except Exception as e:
                self.logger.error(f"對話監控錯誤: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_tasks(self):
        """監控任務"""
        self.logger.info("📋 開始任務監控...")
        
        last_task_count = 0
        
        while self.is_running:
            try:
                # 獲取任務列表
                tasks = await self.manus_operator.get_task_list()
                current_task_count = len(tasks)
                
                if current_task_count != last_task_count:
                    self.logger.info(f"📊 任務數量變化: {last_task_count} -> {current_task_count}")
                    
                    # 分析任務狀態
                    await self._analyze_tasks(tasks)
                    
                    last_task_count = current_task_count
                    self.performance_stats['tasks_monitored'] = current_task_count
                
                await asyncio.sleep(self.config.manus_check_interval * 2)
                
            except Exception as e:
                self.logger.error(f"任務監控錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_message(self, message: ManusMessage, all_messages: List[ManusMessage]):
        """分析單條消息"""
        try:
            # 檢查觸發條件
            triggers = []
            
            # 1. 關鍵詞觸發
            keyword_trigger = self._check_keyword_trigger(message)
            if keyword_trigger:
                triggers.append(keyword_trigger)
            
            # 2. 情緒觸發
            emotion_trigger = self._check_emotion_trigger(message)
            if emotion_trigger:
                triggers.append(emotion_trigger)
            
            # 3. 重複問題觸發
            repetition_trigger = self._check_repetition_trigger(message, all_messages)
            if repetition_trigger:
                triggers.append(repetition_trigger)
            
            # 處理觸發的介入
            for trigger in triggers:
                await self._handle_intervention(message, trigger, all_messages)
                
        except Exception as e:
            self.logger.error(f"分析消息失敗: {e}")
    
    def _check_keyword_trigger(self, message: ManusMessage) -> Optional[Dict[str, Any]]:
        """檢查關鍵詞觸發"""
        content = message.content.lower()
        
        for keyword in self.config.trigger_keywords:
            if keyword.lower() in content:
                confidence = self.trigger_weights['keyword']
                
                return {
                    'type': 'keyword',
                    'confidence': confidence,
                    'keyword': keyword,
                    'message_id': message.id
                }
        
        return None
    
    def _check_emotion_trigger(self, message: ManusMessage) -> Optional[Dict[str, Any]]:
        """檢查情緒觸發"""
        content = message.content.lower()
        
        # 簡單的負面情緒檢測
        negative_words = [
            '生氣', '憤怒', '失望', '沮喪', '煩躁', '困擾', '痛苦', '難過',
            'angry', 'frustrated', 'disappointed', 'upset', 'annoyed'
        ]
        
        negative_count = sum(1 for word in negative_words if word in content)
        
        if negative_count > 0:
            confidence = min(negative_count * 0.3, 1.0) * self.trigger_weights['emotion']
            
            if confidence >= self.config.negative_emotion_threshold:
                return {
                    'type': 'emotion',
                    'confidence': confidence,
                    'negative_words': negative_count,
                    'message_id': message.id
                }
        
        return None
    
    def _check_repetition_trigger(self, message: ManusMessage, all_messages: List[ManusMessage]) -> Optional[Dict[str, Any]]:
        """檢查重複問題觸發"""
        if len(all_messages) < self.config.repetition_threshold:
            return None
        
        # 獲取最近的消息
        recent_messages = all_messages[-10:]  # 最近10條消息
        current_content = message.content.lower()
        
        # 計算相似度
        similar_count = 0
        for msg in recent_messages[:-1]:  # 排除當前消息
            if msg.sender == message.sender:  # 同一發送者
                similarity = self._calculate_similarity(current_content, msg.content.lower())
                if similarity > 0.7:
                    similar_count += 1
        
        if similar_count >= self.config.repetition_threshold:
            confidence = min(similar_count / 5.0, 1.0) * self.trigger_weights['repetition']
            
            return {
                'type': 'repetition',
                'confidence': confidence,
                'similar_count': similar_count,
                'message_id': message.id
            }
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _check_response_delays(self, messages: List[ManusMessage], last_check: datetime):
        """檢查響應延遲"""
        if not messages:
            return
        
        # 找到最後一條用戶消息
        last_user_message = None
        for message in reversed(messages):
            if message.sender == 'user':
                last_user_message = message
                break
        
        if not last_user_message:
            return
        
        # 檢查是否有後續的助手回覆
        has_response = False
        for message in messages:
            if (message.timestamp > last_user_message.timestamp and 
                message.sender == 'assistant'):
                has_response = True
                break
        
        # 如果沒有回覆且超過延遲閾值
        if not has_response:
            delay_seconds = (datetime.now() - last_user_message.timestamp).total_seconds()
            
            if delay_seconds > self.config.max_response_delay:
                trigger = {
                    'type': 'delay',
                    'confidence': min(delay_seconds / self.config.max_response_delay, 1.0) * self.trigger_weights['delay'],
                    'delay_seconds': delay_seconds,
                    'message_id': last_user_message.id
                }
                
                await self._handle_intervention(last_user_message, trigger, messages)
    
    async def _handle_intervention(self, message: ManusMessage, trigger: Dict[str, Any], all_messages: List[ManusMessage]):
        """處理介入"""
        try:
            self.logger.info(f"🎯 觸發介入: {trigger['type']} (信心度: {trigger['confidence']:.2f})")
            
            # 檢查信心度閾值
            if trigger['confidence'] < self.config.min_confidence_score:
                self.logger.info(f"信心度不足，跳過介入: {trigger['confidence']:.2f} < {self.config.min_confidence_score}")
                return
            
            # 生成智能回覆
            context = [msg.content for msg in all_messages[-5:]]  # 最近5條消息
            response = await self.trae_db.generate_intelligent_response(context, trigger['type'])
            
            if not response:
                self.logger.warning("無法生成智能回覆")
                self.performance_stats['failed_interventions'] += 1
                return
            
            # 發送回覆
            success = await self.manus_operator.send_message(response)
            
            # 記錄介入結果
            intervention_record = {
                'timestamp': datetime.now().isoformat(),
                'trigger': trigger,
                'original_message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender
                },
                'generated_response': response,
                'sent_successfully': success,
                'confidence': trigger['confidence']
            }
            
            self.intervention_history.append(intervention_record)
            
            # 更新統計
            self.performance_stats['total_interventions'] += 1
            if success:
                self.performance_stats['successful_interventions'] += 1
                self.logger.info("✅ 介入成功完成")
            else:
                self.performance_stats['failed_interventions'] += 1
                self.logger.warning("❌ 介入發送失敗")
            
            # 學習優化
            await self._update_learning_data(trigger, success)
            
        except Exception as e:
            self.logger.error(f"處理介入失敗: {e}")
            self.performance_stats['failed_interventions'] += 1
    
    async def _analyze_tasks(self, tasks):
        """分析任務狀態"""
        try:
            # 統計任務狀態
            status_counts = {}
            for task in tasks:
                status = task.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            self.logger.info(f"📊 任務狀態統計: {status_counts}")
            
            # 檢查是否有卡住的任務需要介入
            stuck_tasks = [task for task in tasks if task.status in ['pending', 'stuck']]
            
            if stuck_tasks:
                self.logger.info(f"⚠️ 發現 {len(stuck_tasks)} 個可能需要介入的任務")
                
                for task in stuck_tasks:
                    # 可以在這裡添加任務相關的介入邏輯
                    pass
            
        except Exception as e:
            self.logger.error(f"分析任務失敗: {e}")
    
    async def _learning_optimization_loop(self):
        """學習優化循環"""
        self.logger.info("🧠 開始學習優化循環...")
        
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # 每小時運行一次
                
                if len(self.intervention_history) >= 10:  # 至少有10次介入記錄
                    await self._optimize_trigger_weights()
                    await self._clean_old_data()
                
            except Exception as e:
                self.logger.error(f"學習優化錯誤: {e}")
    
    async def _update_learning_data(self, trigger: Dict[str, Any], success: bool):
        """更新學習數據"""
        try:
            trigger_type = trigger['type']
            
            if trigger_type not in self.learning_patterns:
                self.learning_patterns[trigger_type] = {
                    'total_attempts': 0,
                    'successful_attempts': 0,
                    'success_rate': 0.0
                }
            
            pattern = self.learning_patterns[trigger_type]
            pattern['total_attempts'] += 1
            
            if success:
                pattern['successful_attempts'] += 1
            
            pattern['success_rate'] = pattern['successful_attempts'] / pattern['total_attempts']
            
            self.logger.debug(f"更新學習數據 - {trigger_type}: {pattern}")
            
        except Exception as e:
            self.logger.error(f"更新學習數據失敗: {e}")
    
    async def _optimize_trigger_weights(self):
        """優化觸發權重"""
        try:
            self.logger.info("🎯 優化觸發權重...")
            
            for trigger_type, pattern in self.learning_patterns.items():
                if pattern['total_attempts'] >= 5:  # 至少5次嘗試
                    success_rate = pattern['success_rate']
                    
                    # 根據成功率調整權重
                    if success_rate > 0.8:
                        self.trigger_weights[trigger_type] *= 1.1  # 增加權重
                    elif success_rate < 0.3:
                        self.trigger_weights[trigger_type] *= 0.9  # 減少權重
                    
                    # 限制權重範圍
                    self.trigger_weights[trigger_type] = max(0.1, min(2.0, self.trigger_weights[trigger_type]))
            
            self.logger.info(f"✅ 權重優化完成: {self.trigger_weights}")
            
        except Exception as e:
            self.logger.error(f"優化觸發權重失敗: {e}")
    
    async def _clean_old_data(self):
        """清理舊數據"""
        try:
            # 清理超過7天的介入記錄
            cutoff_time = datetime.now() - timedelta(days=7)
            
            old_count = len(self.intervention_history)
            self.intervention_history = [
                record for record in self.intervention_history
                if datetime.fromisoformat(record['timestamp']) > cutoff_time
            ]
            
            cleaned_count = old_count - len(self.intervention_history)
            if cleaned_count > 0:
                self.logger.info(f"🧹 清理了 {cleaned_count} 條舊的介入記錄")
            
        except Exception as e:
            self.logger.error(f"清理舊數據失敗: {e}")
    
    async def _save_performance_stats(self):
        """保存性能統計"""
        try:
            stats_file = Path(self.config.data_dir) / f"performance_stats_{datetime.now().strftime('%Y%m%d')}.json"
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'performance_stats': self.performance_stats,
                'learning_patterns': self.learning_patterns,
                'trigger_weights': self.trigger_weights,
                'total_intervention_records': len(self.intervention_history)
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📊 性能統計已保存: {stats_file}")
            
        except Exception as e:
            self.logger.error(f"保存性能統計失敗: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'performance_stats': self.performance_stats,
            'learning_patterns': self.learning_patterns,
            'trigger_weights': self.trigger_weights,
            'manus_stats': self.manus_operator.get_stats(),
            'trae_stats': self.trae_db.get_stats(),
            'config': {
                'system_name': self.config.system_name,
                'version': self.config.version,
                'debug': self.config.debug
            }
        }

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Manus-TRAE智能介入系統')
    parser.add_argument('--config', help='配置文件路徑')
    parser.add_argument('--debug', action='store_true', help='啟用調試模式')
    
    args = parser.parse_args()
    
    # 創建系統實例
    system = IntelligentInterventionSystem(args.config)
    
    if args.debug:
        system.config.debug = True
    
    # 設置信號處理
    def signal_handler(signum, frame):
        print("\n收到停止信號，正在安全關閉系統...")
        asyncio.create_task(system.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 啟動系統
        success = await system.start()
        
        if success:
            print("✅ 智能介入系統啟動成功！")
            print("按 Ctrl+C 停止系統")
            
            # 保持運行
            while system.is_running:
                await asyncio.sleep(1)
        else:
            print("❌ 系統啟動失敗")
            return 1
            
    except KeyboardInterrupt:
        print("\n用戶中斷，正在停止系統...")
    except Exception as e:
        print(f"系統運行錯誤: {e}")
        return 1
    finally:
        await system.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

