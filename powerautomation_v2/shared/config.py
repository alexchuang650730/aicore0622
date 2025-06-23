"""
Manus-TRAE智能介入系統核心配置
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class SystemConfig:
    """系統核心配置"""
    
    # 系統基本設置
    system_name: str = "Manus-TRAE智能介入系統"
    version: str = "1.0.0"
    debug: bool = True
    
    # 監控設置
    monitoring_interval: int = 5  # 秒
    max_response_delay: int = 300  # 5分鐘無響應觸發介入
    
    # Manus平台設置
    manus_base_url: str = "https://manus.chat"
    manus_check_interval: int = 10  # 檢查間隔（秒）
    
    # TRAE設置
    trae_api_url: str = "http://localhost:8080/api"
    trae_model: str = "gpt-4"
    trae_max_tokens: int = 1000
    trae_temperature: float = 0.7
    
    # 觸發條件設置
    trigger_keywords: List[str] = None
    negative_emotion_threshold: float = 0.6
    repetition_threshold: int = 3
    
    # 數據存儲設置
    data_dir: str = "/home/ec2-user/manus-trae-intelligent-system/data"
    log_dir: str = "/home/ec2-user/manus-trae-intelligent-system/logs"
    backup_interval: int = 3600  # 1小時備份一次
    
    # 學習系統設置
    learning_enabled: bool = True
    min_confidence_score: float = 0.8
    learning_rate: float = 0.01
    
    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = [
                "幫助", "help", "問題", "困難", "卡住", "不知道",
                "怎麼辦", "求助", "急", "緊急", "錯誤", "失敗"
            ]
        
        # 確保目錄存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'system_name': self.system_name,
            'version': self.version,
            'debug': self.debug,
            'monitoring_interval': self.monitoring_interval,
            'max_response_delay': self.max_response_delay,
            'manus_base_url': self.manus_base_url,
            'manus_check_interval': self.manus_check_interval,
            'trae_api_url': self.trae_api_url,
            'trae_model': self.trae_model,
            'trae_max_tokens': self.trae_max_tokens,
            'trae_temperature': self.trae_temperature,
            'trigger_keywords': self.trigger_keywords,
            'negative_emotion_threshold': self.negative_emotion_threshold,
            'repetition_threshold': self.repetition_threshold,
            'data_dir': self.data_dir,
            'log_dir': self.log_dir,
            'backup_interval': self.backup_interval,
            'learning_enabled': self.learning_enabled,
            'min_confidence_score': self.min_confidence_score,
            'learning_rate': self.learning_rate
        }
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'SystemConfig':
        """從文件加載配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

# 全局配置實例
config = SystemConfig()

