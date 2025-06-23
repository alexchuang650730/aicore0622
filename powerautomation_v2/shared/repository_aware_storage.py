#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倉庫感知數據存儲系統 - PowerAutomation
實現 倉庫/conversationid 的層級數據組織
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class RepositoryAwareDataStorage:
    """倉庫感知的數據存儲系統"""
    
    def __init__(self, base_data_dir: str = "/home/ec2-user/powerautomation/data"):
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 當前倉庫檢測緩存
        self._current_repository_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5分鐘緩存
    
    def detect_current_repository(self) -> str:
        """
        檢測用戶當前正在使用的倉庫
        
        Returns:
            當前倉庫名稱
        """
        current_time = time.time()
        
        # 檢查緩存
        if (self._current_repository_cache and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._current_repository_cache
        
        # 多種方法檢測當前倉庫
        repository = self._detect_repository_from_trae()
        
        if not repository:
            repository = self._detect_repository_from_git()
        
        if not repository:
            repository = "default"  # 默認倉庫
        
        # 更新緩存
        self._current_repository_cache = repository
        self._cache_timestamp = current_time
        
        return repository
    
    def _detect_repository_from_trae(self) -> Optional[str]:
        """從TRAE配置檢測當前倉庫"""
        try:
            import subprocess
            
            # 嘗試獲取TRAE當前倉庫
            result = subprocess.run(
                ['trae', 'status', '--current'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
                
        except Exception as e:
            print(f"TRAE檢測失敗: {e}")
        
        return None
    
    def _detect_repository_from_git(self) -> Optional[str]:
        """從Git配置檢測當前倉庫"""
        try:
            import subprocess
            
            # 獲取當前目錄的Git倉庫名
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                repo_path = result.stdout.strip()
                return os.path.basename(repo_path)
                
        except Exception as e:
            print(f"Git檢測失敗: {e}")
        
        return None
    
    def generate_conversation_id(self, repository: str = None) -> str:
        """
        生成對話ID
        
        Args:
            repository: 倉庫名稱，如果為None則自動檢測
            
        Returns:
            對話ID
        """
        if repository is None:
            repository = self.detect_current_repository()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return f"conv_{timestamp}_{unique_id}"
    
    def get_repository_data_dir(self, repository: str) -> Path:
        """
        獲取倉庫數據目錄
        
        Args:
            repository: 倉庫名稱
            
        Returns:
            倉庫數據目錄路徑
        """
        repo_dir = self.base_data_dir / repository
        repo_dir.mkdir(parents=True, exist_ok=True)
        return repo_dir
    
    def get_conversation_data_dir(self, repository: str, conversation_id: str) -> Path:
        """
        獲取對話數據目錄
        
        Args:
            repository: 倉庫名稱
            conversation_id: 對話ID
            
        Returns:
            對話數據目錄路徑
        """
        conv_dir = self.get_repository_data_dir(repository) / conversation_id
        conv_dir.mkdir(parents=True, exist_ok=True)
        return conv_dir
    
    def save_conversation_data(self, conversation_data: Dict, 
                             repository: str = None, 
                             conversation_id: str = None) -> str:
        """
        保存對話數據
        
        Args:
            conversation_data: 對話數據
            repository: 倉庫名稱，如果為None則自動檢測
            conversation_id: 對話ID，如果為None則自動生成
            
        Returns:
            對話ID
        """
        if repository is None:
            repository = self.detect_current_repository()
        
        if conversation_id is None:
            conversation_id = self.generate_conversation_id(repository)
        
        # 獲取對話數據目錄
        conv_dir = self.get_conversation_data_dir(repository, conversation_id)
        
        # 添加元數據
        conversation_data.update({
            'repository': repository,
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'storage_version': '2.0'
        })
        
        # 保存主要對話數據
        conversation_file = conv_dir / 'conversation.json'
        with open(conversation_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        return conversation_id
    
    def save_intervention_analysis(self, analysis_data: Dict, 
                                 repository: str, 
                                 conversation_id: str) -> None:
        """
        保存智能介入分析數據
        
        Args:
            analysis_data: 分析數據
            repository: 倉庫名稱
            conversation_id: 對話ID
        """
        conv_dir = self.get_conversation_data_dir(repository, conversation_id)
        
        analysis_data.update({
            'repository': repository,
            'conversation_id': conversation_id,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
        analysis_file = conv_dir / 'intervention_analysis.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    def save_intervention_result(self, result_data: Dict, 
                               repository: str, 
                               conversation_id: str) -> None:
        """
        保存智能介入結果
        
        Args:
            result_data: 結果數據
            repository: 倉庫名稱
            conversation_id: 對話ID
        """
        conv_dir = self.get_conversation_data_dir(repository, conversation_id)
        
        result_data.update({
            'repository': repository,
            'conversation_id': conversation_id,
            'result_timestamp': datetime.now().isoformat()
        })
        
        result_file = conv_dir / 'intervention_result.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    def load_conversation_data(self, repository: str, conversation_id: str) -> Optional[Dict]:
        """
        加載對話數據
        
        Args:
            repository: 倉庫名稱
            conversation_id: 對話ID
            
        Returns:
            對話數據或None
        """
        conv_dir = self.get_conversation_data_dir(repository, conversation_id)
        conversation_file = conv_dir / 'conversation.json'
        
        if conversation_file.exists():
            with open(conversation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_repository_conversations(self, repository: str) -> List[str]:
        """
        列出倉庫的所有對話ID
        
        Args:
            repository: 倉庫名稱
            
        Returns:
            對話ID列表
        """
        repo_dir = self.get_repository_data_dir(repository)
        
        conversations = []
        for item in repo_dir.iterdir():
            if item.is_dir() and item.name.startswith('conv_'):
                conversations.append(item.name)
        
        return sorted(conversations, reverse=True)  # 最新的在前
    
    def list_all_repositories(self) -> List[str]:
        """
        列出所有倉庫
        
        Returns:
            倉庫名稱列表
        """
        repositories = []
        for item in self.base_data_dir.iterdir():
            if item.is_dir():
                repositories.append(item.name)
        
        return sorted(repositories)
    
    def get_repository_statistics(self, repository: str) -> Dict:
        """
        獲取倉庫統計信息
        
        Args:
            repository: 倉庫名稱
            
        Returns:
            統計信息
        """
        conversations = self.list_repository_conversations(repository)
        
        stats = {
            'repository': repository,
            'total_conversations': len(conversations),
            'latest_conversation': conversations[0] if conversations else None,
            'data_directory': str(self.get_repository_data_dir(repository))
        }
        
        # 計算介入統計
        intervention_count = 0
        for conv_id in conversations:
            conv_dir = self.get_conversation_data_dir(repository, conv_id)
            if (conv_dir / 'intervention_result.json').exists():
                intervention_count += 1
        
        stats['interventions'] = intervention_count
        stats['intervention_rate'] = intervention_count / len(conversations) if conversations else 0
        
        return stats
    
    def get_system_overview(self) -> Dict:
        """
        獲取系統總覽
        
        Returns:
            系統統計信息
        """
        repositories = self.list_all_repositories()
        current_repo = self.detect_current_repository()
        
        overview = {
            'current_repository': current_repo,
            'total_repositories': len(repositories),
            'repositories': repositories,
            'repository_stats': {}
        }
        
        total_conversations = 0
        total_interventions = 0
        
        for repo in repositories:
            stats = self.get_repository_statistics(repo)
            overview['repository_stats'][repo] = stats
            total_conversations += stats['total_conversations']
            total_interventions += stats['interventions']
        
        overview['total_conversations'] = total_conversations
        overview['total_interventions'] = total_interventions
        overview['overall_intervention_rate'] = total_interventions / total_conversations if total_conversations else 0
        
        return overview

# 使用示例
if __name__ == "__main__":
    storage = RepositoryAwareDataStorage()
    
    print("🗄️ 倉庫感知數據存儲系統測試")
    print("=" * 50)
    
    # 檢測當前倉庫
    current_repo = storage.detect_current_repository()
    print(f"當前倉庫: {current_repo}")
    
    # 模擬保存對話數據
    test_conversation = {
        'user_message': '我想要生成一個貪吃蛇遊戲',
        'trae_response': '好的，我來為您生成貪吃蛇遊戲...',
        'context': 'game development'
    }
    
    conv_id = storage.save_conversation_data(test_conversation)
    print(f"保存對話: {conv_id}")
    
    # 保存分析數據
    analysis = {
        'needs_intervention': True,
        'confidence': 0.85,
        'reason': '遊戲開發請求'
    }
    
    storage.save_intervention_analysis(analysis, current_repo, conv_id)
    print("保存分析數據完成")
    
    # 獲取統計信息
    stats = storage.get_repository_statistics(current_repo)
    print(f"倉庫統計: {stats}")
    
    # 系統總覽
    overview = storage.get_system_overview()
    print(f"系統總覽: {overview}")

