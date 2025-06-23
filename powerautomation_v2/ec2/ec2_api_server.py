#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PowerAutomation EC2端對話接收API
功能：接收Mac端同步的所有TRAE對話數據
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging
from typing import Dict, List

app = Flask(__name__)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ec2-user/powerautomation/logs/api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 數據存儲目錄
DATA_DIR = "/home/ec2-user/powerautomation/data"
LOGS_DIR = "/home/ec2-user/powerautomation/logs"

# 確保目錄存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

class ConversationStorage:
    """對話數據存儲管理"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
    
    def save_conversations(self, conversations: List[Dict], metadata: Dict) -> str:
        """保存對話數據"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        # 準備保存數據
        save_data = {
            "metadata": metadata,
            "conversations": conversations,
            "total_count": len(conversations),
            "save_time": datetime.now().isoformat(),
            "file_version": "1.0"
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"保存 {len(conversations)} 條對話到 {filename}")
        return filename
    
    def save_intervention_analysis(self, analyses: List[Dict]) -> str:
        """保存介入分析結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"intervention_analysis_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        save_data = {
            "analyses": analyses,
            "total_count": len(analyses),
            "save_time": datetime.now().isoformat(),
            "analysis_version": "1.0"
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"保存 {len(analyses)} 條介入分析到 {filename}")
        return filename
    
    def get_latest_conversations(self, limit: int = 50) -> List[Dict]:
        """獲取最新的對話記錄"""
        conversations = []
        
        # 獲取所有對話文件
        files = [f for f in os.listdir(self.data_dir) if f.startswith("conversations_")]
        files.sort(reverse=True)  # 最新的在前
        
        for filename in files[:5]:  # 最多讀取5個文件
            filepath = os.path.join(self.data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations.extend(data.get("conversations", []))
                    
                if len(conversations) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"讀取文件 {filename} 失敗: {e}")
        
        return conversations[:limit]
    
    def get_statistics(self) -> Dict:
        """獲取統計信息"""
        stats = {
            "total_files": 0,
            "total_conversations": 0,
            "intervention_needed_count": 0,
            "latest_sync_time": None,
            "file_list": []
        }
        
        try:
            # 統計對話文件
            conv_files = [f for f in os.listdir(self.data_dir) if f.startswith("conversations_")]
            stats["total_files"] = len(conv_files)
            
            for filename in conv_files:
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        conversations = data.get("conversations", [])
                        stats["total_conversations"] += len(conversations)
                        
                        # 統計需要介入的對話
                        for conv in conversations:
                            analysis = conv.get("intervention_analysis", {})
                            if analysis.get("intervention_needed", False):
                                stats["intervention_needed_count"] += 1
                        
                        # 記錄文件信息
                        stats["file_list"].append({
                            "filename": filename,
                            "conversation_count": len(conversations),
                            "save_time": data.get("save_time")
                        })
                        
                        # 更新最新同步時間
                        save_time = data.get("save_time")
                        if save_time and (not stats["latest_sync_time"] or save_time > stats["latest_sync_time"]):
                            stats["latest_sync_time"] = save_time
                            
                except Exception as e:
                    logger.error(f"統計文件 {filename} 失敗: {e}")
            
            # 按時間排序文件列表
            stats["file_list"].sort(key=lambda x: x.get("save_time", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"獲取統計信息失敗: {e}")
        
        return stats

# 初始化存儲管理器
storage = ConversationStorage()

@app.route('/api/sync/conversations', methods=['POST'])
def sync_conversations():
    """接收對話同步請求"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "沒有數據"}), 400
        
        conversations = data.get("conversations", [])
        sync_metadata = data.get("sync_metadata", {})
        
        if not conversations:
            return jsonify({"error": "沒有對話數據"}), 400
        
        # 保存對話數據
        filename = storage.save_conversations(conversations, sync_metadata)
        
        # 提取介入分析
        intervention_analyses = []
        for conv in conversations:
            analysis = conv.get("intervention_analysis")
            if analysis:
                intervention_analyses.append({
                    "conversation_id": conv.get("id"),
                    "user_message": conv.get("user_message"),
                    "analysis": analysis,
                    "timestamp": conv.get("timestamp")
                })
        
        # 保存介入分析
        if intervention_analyses:
            analysis_filename = storage.save_intervention_analysis(intervention_analyses)
        else:
            analysis_filename = None
        
        # 記錄同步日誌
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "conversation_sync",
            "conversation_count": len(conversations),
            "intervention_count": len(intervention_analyses),
            "source": sync_metadata.get("source_system", "unknown"),
            "files_created": [filename, analysis_filename] if analysis_filename else [filename]
        }
        
        # 寫入日誌文件
        log_file = os.path.join(LOGS_DIR, "sync_log.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"成功接收並保存 {len(conversations)} 條對話")
        
        return jsonify({
            "success": True,
            "message": f"成功同步 {len(conversations)} 條對話",
            "conversation_count": len(conversations),
            "intervention_count": len(intervention_analyses),
            "files_created": [filename, analysis_filename] if analysis_filename else [filename],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"同步對話失敗: {e}")
        return jsonify({"error": f"同步失敗: {str(e)}"}), 500

@app.route('/api/conversations/latest', methods=['GET'])
def get_latest_conversations():
    """獲取最新對話"""
    try:
        limit = request.args.get('limit', 50, type=int)
        conversations = storage.get_latest_conversations(limit)
        
        return jsonify({
            "success": True,
            "conversations": conversations,
            "count": len(conversations),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"獲取最新對話失敗: {e}")
        return jsonify({"error": f"獲取失敗: {str(e)}"}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """獲取統計信息"""
    try:
        stats = storage.get_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"獲取統計信息失敗: {e}")
        return jsonify({"error": f"獲取統計失敗: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "service": "PowerAutomation EC2 API",
        "timestamp": datetime.now().isoformat(),
        "data_dir": DATA_DIR,
        "logs_dir": LOGS_DIR
    })

@app.route('/api/interventions/needed', methods=['GET'])
def get_interventions_needed():
    """獲取需要介入的對話"""
    try:
        conversations = storage.get_latest_conversations(100)
        
        # 篩選需要介入的對話
        interventions_needed = []
        for conv in conversations:
            analysis = conv.get("intervention_analysis", {})
            if analysis.get("intervention_needed", False):
                interventions_needed.append({
                    "conversation_id": conv.get("id"),
                    "user_message": conv.get("user_message"),
                    "status": conv.get("status"),
                    "confidence_score": analysis.get("confidence_score"),
                    "priority": analysis.get("priority"),
                    "recommended_action": analysis.get("recommended_action"),
                    "timestamp": conv.get("timestamp")
                })
        
        # 按優先級和信心度排序
        interventions_needed.sort(
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 1),
                x.get("confidence_score", 0)
            ),
            reverse=True
        )
        
        return jsonify({
            "success": True,
            "interventions": interventions_needed,
            "count": len(interventions_needed),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"獲取介入需求失敗: {e}")
        return jsonify({"error": f"獲取失敗: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("啟動PowerAutomation EC2 API服務")
    app.run(host='0.0.0.0', port=8000, debug=False)

