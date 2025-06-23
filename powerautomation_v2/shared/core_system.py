"""
Manus-TRAE智能介入系統核心類
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
import threading
from pathlib import Path

@dataclass
class ConversationMessage:
    """對話消息數據結構"""
    id: str
    user_id: str
    content: str
    timestamp: datetime
    message_type: str  # user, assistant, system
    conversation_id: str
    metadata: Dict[str, Any] = None

@dataclass
class InterventionTrigger:
    """介入觸發條件"""
    trigger_type: str  # delay, keyword, emotion, repetition
    confidence: float
    details: Dict[str, Any]
    timestamp: datetime

@dataclass
class GeneratedResponse:
    """生成的回覆"""
    content: str
    confidence: float
    generation_time: float
    model_used: str
    prompt_used: str
    metadata: Dict[str, Any] = None

class IntelligentInterventionSystem:
    """智能介入系統核心類"""
    
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.logger = self._setup_logger()
        self.db_path = Path(config.data_dir) / "intervention_system.db"
        self._init_database()
        
        # 系統狀態
        self.active_conversations = {}
        self.intervention_history = []
        self.learning_data = []
        
        # 監控線程
        self.monitoring_thread = None
        self.analysis_thread = None
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌系統"""
        logger = logging.getLogger("IntelligentIntervention")
        logger.setLevel(logging.DEBUG if self.config.debug else logging.INFO)
        
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
    
    def _init_database(self):
        """初始化數據庫"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 對話消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    content TEXT,
                    timestamp DATETIME,
                    message_type TEXT,
                    conversation_id TEXT,
                    metadata TEXT
                )
            ''')
            
            # 介入記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    trigger_type TEXT,
                    trigger_confidence REAL,
                    trigger_details TEXT,
                    generated_response TEXT,
                    response_confidence REAL,
                    sent_successfully BOOLEAN,
                    user_reaction TEXT,
                    effectiveness_score REAL,
                    timestamp DATETIME
                )
            ''')
            
            # 學習數據表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    success_rate REAL,
                    usage_count INTEGER,
                    last_updated DATETIME
                )
            ''')
            
            conn.commit()
    
    async def start_system(self):
        """啟動系統"""
        if self.is_running:
            self.logger.warning("系統已經在運行中")
            return
        
        self.is_running = True
        self.logger.info("🚀 智能介入系統啟動中...")
        
        # 啟動監控線程
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # 啟動分析線程
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        self.logger.info("✅ 系統啟動完成")
    
    def stop_system(self):
        """停止系統"""
        self.is_running = False
        self.logger.info("🛑 系統正在停止...")
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        
        self.logger.info("✅ 系統已停止")
    
    def _monitoring_loop(self):
        """監控循環"""
        self.logger.info("🔍 開始監控Manus對話...")
        
        while self.is_running:
            try:
                # 這裡將實現Manus對話監控邏輯
                self._check_manus_conversations()
                time.sleep(self.config.manus_check_interval)
            except Exception as e:
                self.logger.error(f"監控循環錯誤: {e}")
                time.sleep(5)
    
    def _analysis_loop(self):
        """分析循環"""
        self.logger.info("🧠 開始智能分析...")
        
        while self.is_running:
            try:
                # 分析活躍對話
                for conv_id, conv_data in self.active_conversations.items():
                    self._analyze_conversation(conv_id, conv_data)
                
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"分析循環錯誤: {e}")
                time.sleep(5)
    
    def _check_manus_conversations(self):
        """檢查Manus對話（待實現具體邏輯）"""
        # 這裡將實現具體的Manus API調用或網頁抓取邏輯
        pass
    
    def _analyze_conversation(self, conv_id: str, conv_data: Dict):
        """分析單個對話"""
        try:
            # 檢查響應延遲
            delay_trigger = self._check_response_delay(conv_data)
            if delay_trigger:
                self._handle_intervention_trigger(conv_id, delay_trigger)
            
            # 檢查關鍵詞
            keyword_trigger = self._check_keywords(conv_data)
            if keyword_trigger:
                self._handle_intervention_trigger(conv_id, keyword_trigger)
            
            # 檢查情緒
            emotion_trigger = self._check_emotion(conv_data)
            if emotion_trigger:
                self._handle_intervention_trigger(conv_id, emotion_trigger)
            
            # 檢查重複問題
            repetition_trigger = self._check_repetition(conv_data)
            if repetition_trigger:
                self._handle_intervention_trigger(conv_id, repetition_trigger)
                
        except Exception as e:
            self.logger.error(f"分析對話 {conv_id} 時發生錯誤: {e}")
    
    def _check_response_delay(self, conv_data: Dict) -> Optional[InterventionTrigger]:
        """檢查響應延遲"""
        last_message_time = conv_data.get('last_message_time')
        if not last_message_time:
            return None
        
        time_diff = (datetime.now() - last_message_time).total_seconds()
        if time_diff > self.config.max_response_delay:
            return InterventionTrigger(
                trigger_type="delay",
                confidence=min(time_diff / self.config.max_response_delay, 1.0),
                details={"delay_seconds": time_diff},
                timestamp=datetime.now()
            )
        return None
    
    def _check_keywords(self, conv_data: Dict) -> Optional[InterventionTrigger]:
        """檢查關鍵詞觸發"""
        last_message = conv_data.get('last_message', '')
        
        for keyword in self.config.trigger_keywords:
            if keyword.lower() in last_message.lower():
                return InterventionTrigger(
                    trigger_type="keyword",
                    confidence=0.8,
                    details={"keyword": keyword, "message": last_message},
                    timestamp=datetime.now()
                )
        return None
    
    def _check_emotion(self, conv_data: Dict) -> Optional[InterventionTrigger]:
        """檢查情緒觸發（簡化版本）"""
        last_message = conv_data.get('last_message', '')
        
        # 簡單的負面情緒檢測
        negative_words = ['生氣', '憤怒', '失望', '沮喪', '煩躁', '困擾', '痛苦']
        negative_count = sum(1 for word in negative_words if word in last_message)
        
        if negative_count > 0:
            confidence = min(negative_count * 0.3, 1.0)
            if confidence >= self.config.negative_emotion_threshold:
                return InterventionTrigger(
                    trigger_type="emotion",
                    confidence=confidence,
                    details={"negative_words": negative_count, "message": last_message},
                    timestamp=datetime.now()
                )
        return None
    
    def _check_repetition(self, conv_data: Dict) -> Optional[InterventionTrigger]:
        """檢查重複問題"""
        messages = conv_data.get('recent_messages', [])
        if len(messages) < self.config.repetition_threshold:
            return None
        
        # 簡單的重複檢測
        last_message = messages[-1] if messages else ""
        similar_count = sum(1 for msg in messages[-5:] if self._calculate_similarity(msg, last_message) > 0.7)
        
        if similar_count >= self.config.repetition_threshold:
            return InterventionTrigger(
                trigger_type="repetition",
                confidence=0.9,
                details={"repetition_count": similar_count, "message": last_message},
                timestamp=datetime.now()
            )
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似度（簡化版本）"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _handle_intervention_trigger(self, conv_id: str, trigger: InterventionTrigger):
        """處理介入觸發"""
        self.logger.info(f"🎯 檢測到介入觸發: {trigger.trigger_type} (信心度: {trigger.confidence:.2f})")
        
        # 記錄觸發事件
        self.intervention_history.append({
            'conversation_id': conv_id,
            'trigger': trigger,
            'timestamp': datetime.now()
        })
        
        # 異步處理介入
        asyncio.create_task(self._process_intervention(conv_id, trigger))
    
    async def _process_intervention(self, conv_id: str, trigger: InterventionTrigger):
        """處理介入流程"""
        try:
            # 1. 生成回覆
            response = await self._generate_response(conv_id, trigger)
            if not response or response.confidence < self.config.min_confidence_score:
                self.logger.warning(f"生成的回覆信心度不足: {response.confidence if response else 'None'}")
                return
            
            # 2. 發送回覆
            success = await self._send_response(conv_id, response)
            
            # 3. 記錄結果
            await self._record_intervention(conv_id, trigger, response, success)
            
            self.logger.info(f"✅ 介入處理完成: {conv_id}")
            
        except Exception as e:
            self.logger.error(f"處理介入時發生錯誤: {e}")
    
    async def _generate_response(self, conv_id: str, trigger: InterventionTrigger) -> Optional[GeneratedResponse]:
        """生成回覆（待實現TRAE調用）"""
        # 這裡將實現TRAE API調用邏輯
        self.logger.info(f"🤖 正在生成回覆...")
        
        # 模擬回覆生成
        await asyncio.sleep(1)
        
        return GeneratedResponse(
            content="我注意到您可能需要幫助，讓我來協助您解決問題。",
            confidence=0.85,
            generation_time=1.0,
            model_used=self.config.trae_model,
            prompt_used="智能介入提示詞"
        )
    
    async def _send_response(self, conv_id: str, response: GeneratedResponse) -> bool:
        """發送回覆（待實現Manus發送邏輯）"""
        # 這裡將實現Manus自動發送邏輯
        self.logger.info(f"📤 正在發送回覆...")
        
        # 模擬發送
        await asyncio.sleep(0.5)
        
        return True
    
    async def _record_intervention(self, conv_id: str, trigger: InterventionTrigger, 
                                 response: GeneratedResponse, success: bool):
        """記錄介入結果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interventions 
                (conversation_id, trigger_type, trigger_confidence, trigger_details,
                 generated_response, response_confidence, sent_successfully, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conv_id, trigger.trigger_type, trigger.confidence, 
                json.dumps(trigger.details, ensure_ascii=False),
                response.content, response.confidence, success, datetime.now()
            ))
            conn.commit()
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'is_running': self.is_running,
            'active_conversations': len(self.active_conversations),
            'total_interventions': len(self.intervention_history),
            'uptime': time.time() - getattr(self, 'start_time', time.time()),
            'config': self.config.to_dict()
        }

