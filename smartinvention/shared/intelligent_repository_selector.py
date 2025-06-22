#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能倉庫選擇器 - PowerAutomation
根據對話內容智能選擇合適的TRAE倉庫
"""

import re
from typing import Dict, List, Optional

class IntelligentRepositorySelector:
    """智能倉庫選擇器"""
    
    def __init__(self):
        # 倉庫配置 - 基於用戶的實際倉庫
        self.repositories = {
            'communitypowerauto': {
                'keywords': ['社區', '社群', 'community', '用戶', '公共', '開源', '協作'],
                'description': '社區PowerAutomation項目',
                'priority': 1
            },
            'final_integration_fixed': {
                'keywords': ['最終', '集成', '整合', 'final', 'integration', '修復', 'fixed', '完成'],
                'description': '最終集成修復版本',
                'priority': 2
            },
            'automation': {
                'keywords': ['自動化', 'automation', '腳本', 'script', '工作流', 'workflow', '批處理'],
                'description': '自動化工具和腳本',
                'priority': 3
            },
            'powerauto.ai_0.53': {
                'keywords': ['ai', '人工智能', '機器學習', 'ml', '智能', '0.53', 'v0.53'],
                'description': 'PowerAuto AI版本0.53',
                'priority': 4
            },
            'powerauto_v0.3': {
                'keywords': ['v0.3', '0.3', '版本', 'version', '舊版'],
                'description': 'PowerAuto版本0.3',
                'priority': 5
            },
            'subtitles': {
                'keywords': ['字幕', 'subtitle', '翻譯', '視頻', 'video', '音頻'],
                'description': '字幕處理工具',
                'priority': 6
            }
        }
        
        # 默認倉庫（當前選中的）
        self.default_repository = 'communitypowerauto'
    
    def analyze_conversation(self, user_message: str, context: str = "") -> Dict:
        """
        分析對話內容，選擇合適的倉庫
        
        Args:
            user_message: 用戶消息
            context: 對話上下文
            
        Returns:
            分析結果包含推薦倉庫和原因
        """
        analysis = {
            'recommended_repository': self.default_repository,
            'confidence': 0.0,
            'reasons': [],
            'alternatives': []
        }
        
        # 合併用戶消息和上下文
        full_text = f"{user_message} {context}".lower()
        
        # 計算每個倉庫的匹配分數
        scores = {}
        for repo_name, repo_config in self.repositories.items():
            score = self._calculate_repository_score(full_text, repo_config)
            if score > 0:
                scores[repo_name] = score
        
        if scores:
            # 選擇得分最高的倉庫
            best_repo = max(scores.keys(), key=lambda x: scores[x])
            analysis['recommended_repository'] = best_repo
            analysis['confidence'] = min(scores[best_repo] / 10.0, 1.0)  # 標準化到0-1
            
            # 添加選擇原因
            analysis['reasons'] = self._get_selection_reasons(full_text, best_repo)
            
            # 添加備選倉庫
            sorted_repos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            analysis['alternatives'] = [
                {'repository': repo, 'score': score} 
                for repo, score in sorted_repos[1:3]  # 取前2個備選
            ]
        
        return analysis
    
    def _calculate_repository_score(self, text: str, repo_config: Dict) -> float:
        """計算倉庫匹配分數"""
        score = 0.0
        
        # 關鍵詞匹配
        for keyword in repo_config['keywords']:
            if keyword.lower() in text:
                # 完整詞匹配得分更高
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
                    score += 3.0
                else:
                    score += 1.0
        
        # 優先級調整（優先級越高，基礎分越高）
        priority_bonus = (7 - repo_config['priority']) * 0.5
        score += priority_bonus
        
        return score
    
    def _get_selection_reasons(self, text: str, repository: str) -> List[str]:
        """獲取選擇該倉庫的原因"""
        reasons = []
        repo_config = self.repositories[repository]
        
        matched_keywords = []
        for keyword in repo_config['keywords']:
            if keyword.lower() in text:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            reasons.append(f"匹配關鍵詞: {', '.join(matched_keywords[:3])}")
        
        reasons.append(f"倉庫描述: {repo_config['description']}")
        
        return reasons
    
    def get_sync_strategy(self, repository: str, conversation_type: str = "general") -> Dict:
        """
        獲取倉庫同步策略
        
        Args:
            repository: 目標倉庫
            conversation_type: 對話類型
            
        Returns:
            同步策略配置
        """
        strategies = {
            'communitypowerauto': {
                'sync_command': 'trae sync communitypowerauto --verbose',
                'priority': 'high',
                'auto_sync': True,
                'sync_interval': 300  # 5分鐘
            },
            'final_integration_fixed': {
                'sync_command': 'trae sync final_integration_fixed --force',
                'priority': 'critical',
                'auto_sync': True,
                'sync_interval': 180  # 3分鐘
            },
            'automation': {
                'sync_command': 'trae sync automation',
                'priority': 'medium',
                'auto_sync': False,
                'sync_interval': 600  # 10分鐘
            },
            'powerauto.ai_0.53': {
                'sync_command': 'trae sync powerauto.ai_0.53',
                'priority': 'medium',
                'auto_sync': False,
                'sync_interval': 900  # 15分鐘
            },
            'powerauto_v0.3': {
                'sync_command': 'trae sync powerauto_v0.3',
                'priority': 'low',
                'auto_sync': False,
                'sync_interval': 1800  # 30分鐘
            },
            'subtitles': {
                'sync_command': 'trae sync subtitles',
                'priority': 'low',
                'auto_sync': False,
                'sync_interval': 1200  # 20分鐘
            }
        }
        
        return strategies.get(repository, strategies['communitypowerauto'])
    
    def should_trigger_sync(self, repository: str, last_sync_time: float, 
                          conversation_importance: str = "normal") -> bool:
        """
        判斷是否應該觸發同步
        
        Args:
            repository: 倉庫名稱
            last_sync_time: 上次同步時間戳
            conversation_importance: 對話重要性
            
        Returns:
            是否應該同步
        """
        import time
        
        strategy = self.get_sync_strategy(repository)
        current_time = time.time()
        time_since_sync = current_time - last_sync_time
        
        # 根據重要性調整同步間隔
        interval_multiplier = {
            'low': 2.0,
            'normal': 1.0,
            'high': 0.5,
            'critical': 0.2
        }.get(conversation_importance, 1.0)
        
        adjusted_interval = strategy['sync_interval'] * interval_multiplier
        
        return time_since_sync >= adjusted_interval
    
    def get_repository_status(self) -> Dict:
        """獲取所有倉庫的狀態信息"""
        return {
            'repositories': list(self.repositories.keys()),
            'default': self.default_repository,
            'total_count': len(self.repositories),
            'active_repositories': [
                repo for repo, config in self.repositories.items()
                if self.get_sync_strategy(repo)['auto_sync']
            ]
        }

# 使用示例
if __name__ == "__main__":
    selector = IntelligentRepositorySelector()
    
    # 測試案例
    test_cases = [
        "我想要為社區開發一個新功能",
        "需要修復最終集成版本的bug",
        "創建一個自動化腳本來處理數據",
        "AI功能需要優化",
        "處理視頻字幕的問題"
    ]
    
    print("🧪 智能倉庫選擇器測試")
    print("=" * 50)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n測試 {i}: {message}")
        result = selector.analyze_conversation(message)
        print(f"推薦倉庫: {result['recommended_repository']}")
        print(f"信心度: {result['confidence']:.2f}")
        print(f"原因: {', '.join(result['reasons'])}")
        
        # 獲取同步策略
        strategy = selector.get_sync_strategy(result['recommended_repository'])
        print(f"同步策略: {strategy['sync_command']}")
        print(f"優先級: {strategy['priority']}")

