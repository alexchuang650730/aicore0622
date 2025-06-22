#!/usr/bin/env python3
"""
PowerAutomation EC2端核心系統
智能介入、TRAE通信、Manus控制
"""

import os
import sys
import json
import sqlite3
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
import argparse

class PowerAutomationEC2:
    def __init__(self):
        self.setup_logging()
        self.base_dir = Path("/home/ec2-user/powerautomation")
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        self.config_file = self.base_dir / "config.json"
        
        # 創建目錄
        self.base_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.load_config()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/ec2-user/powerautomation/logs/system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """載入配置"""
        default_config = {
            "mac_ssh": {
                "host": "serveo.net",
                "port": 41269,
                "user": "alexchuang",
                "password": "123456"
            },
            "trae_db_path": "/Users/alexchuang/Library/Application Support/Trae/User/workspaceStorage/f002a9b85f221075092022809f5a075f/state.vscdb",
            "manus_url": "https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ",
            "monitoring": {
                "interval": 30,
                "auto_intervention": True,
                "intervention_delay": 300
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
    def ssh_execute(self, command):
        """通過SSH執行Mac端命令"""
        ssh_config = self.config["mac_ssh"]
        ssh_cmd = f"sshpass -p '{ssh_config['password']}' ssh -p {ssh_config['port']} -o StrictHostKeyChecking=no {ssh_config['user']}@{ssh_config['host']} '{command}'"
        
        try:
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "SSH命令超時"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def extract_trae_history(self, repository_name=None):
        """提取TRAE對話歷史"""
        self.logger.info(f"開始提取TRAE歷史: {repository_name or 'all'}")
        
        # 構建提取命令
        if repository_name:
            command = f"python3 /home/alexchuang/aiengine/trae/git/scripts/extract_history.py --repo {repository_name}"
        else:
            command = f"python3 /home/alexchuang/aiengine/trae/git/scripts/extract_history.py --all"
            
        result = self.ssh_execute(command)
        
        if result["success"]:
            # 保存歷史到本地
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.data_dir / f"trae_history_{timestamp}.json"
            
            try:
                history_data = json.loads(result["stdout"])
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history_data, f, indent=2, ensure_ascii=False)
                    
                self.logger.info(f"TRAE歷史已保存: {history_file}")
                return {"success": True, "file": str(history_file), "data": history_data}
            except json.JSONDecodeError:
                self.logger.error("TRAE歷史數據格式錯誤")
                return {"success": False, "error": "數據格式錯誤"}
        else:
            self.logger.error(f"提取TRAE歷史失敗: {result.get('error', result.get('stderr'))}")
            return result
            
    def send_trae_message(self, repository_name, message):
        """發送消息到TRAE"""
        self.logger.info(f"發送消息到TRAE: {repository_name}")
        
        command = f"python3 /home/alexchuang/aiengine/trae/git/scripts/send_message.py --repo {repository_name} --message '{message}'"
        result = self.ssh_execute(command)
        
        if result["success"]:
            self.logger.info("消息發送成功")
            
            # 記錄發送日誌
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "repository": repository_name,
                "message": message,
                "status": "success"
            }
            self.log_message_send(log_entry)
            
        return result
        
    def sync_repositories(self):
        """同步Git倉庫"""
        self.logger.info("開始同步Git倉庫")
        
        command = "python3 /home/alexchuang/aiengine/trae/git/scripts/sync_repositories.py --all"
        result = self.ssh_execute(command)
        
        if result["success"]:
            self.logger.info("倉庫同步成功")
        else:
            self.logger.error(f"倉庫同步失敗: {result.get('error', result.get('stderr'))}")
            
        return result
        
    def intelligent_intervention_check(self):
        """智能介入檢查"""
        if not self.config["monitoring"]["auto_intervention"]:
            return {"action": "skip", "reason": "智能介入已停用"}
            
        # 提取最新對話
        history_result = self.extract_trae_history()
        if not history_result["success"]:
            return {"action": "error", "reason": "無法提取對話歷史"}
            
        conversations = history_result["data"]
        
        # 分析是否需要介入
        intervention_needed = self.analyze_intervention_need(conversations)
        
        if intervention_needed["needed"]:
            # 生成智能回覆
            response = self.generate_intelligent_response(intervention_needed["context"])
            
            # 發送回覆
            if response:
                send_result = self.send_trae_message(
                    intervention_needed["repository"], 
                    response
                )
                
                if send_result["success"]:
                    self.logger.info(f"智能介入成功: {response[:50]}...")
                    return {
                        "action": "intervened",
                        "response": response,
                        "repository": intervention_needed["repository"]
                    }
                    
        return {"action": "no_intervention", "reason": "無需介入"}
        
    def analyze_intervention_need(self, conversations):
        """分析是否需要智能介入"""
        if not conversations:
            return {"needed": False, "reason": "無對話記錄"}
            
        latest_conv = conversations[-1]
        
        # 檢查時間間隔
        last_time = datetime.fromisoformat(latest_conv.get("timestamp", ""))
        time_diff = (datetime.now() - last_time).total_seconds()
        
        intervention_delay = self.config["monitoring"]["intervention_delay"]
        
        if time_diff > intervention_delay:
            # 檢查關鍵詞
            message = latest_conv.get("message", "").lower()
            keywords = ["幫助", "問題", "困難", "不知道", "怎麼辦", "錯誤"]
            
            if any(keyword in message for keyword in keywords):
                return {
                    "needed": True,
                    "reason": "檢測到求助關鍵詞且超時",
                    "context": latest_conv,
                    "repository": latest_conv.get("repository", "default")
                }
                
        return {"needed": False, "reason": "無需介入"}
        
    def generate_intelligent_response(self, context):
        """生成智能回覆"""
        message = context.get("message", "")
        
        # 簡單的回覆生成邏輯
        if "幫助" in message or "問題" in message:
            return "我來協助您解決這個問題。請提供更多詳細信息，我會盡力幫助您。"
        elif "錯誤" in message:
            return "看起來遇到了錯誤。請檢查錯誤信息並提供詳細的錯誤日誌，我會幫您分析解決方案。"
        elif "不知道" in message:
            return "沒關係，讓我們一步步來解決。請告訴我您想要實現什麼功能，我會提供具體的指導。"
        else:
            return "我注意到您可能需要協助。如果有任何問題，請隨時告訴我，我會盡力幫助您。"
            
    def log_message_send(self, log_entry):
        """記錄消息發送日誌"""
        log_file = self.logs_dir / "message_send.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
    def start_monitoring(self):
        """開始監控"""
        self.logger.info("PowerAutomation EC2監控已啟動")
        
        try:
            while True:
                # 執行監控週期
                self.logger.info("執行監控週期...")
                
                # 智能介入檢查
                intervention_result = self.intelligent_intervention_check()
                self.logger.info(f"智能介入結果: {intervention_result['action']}")
                
                # 等待下一個週期
                time.sleep(self.config["monitoring"]["interval"])
                
        except KeyboardInterrupt:
            self.logger.info("監控已停止")
        except Exception as e:
            self.logger.error(f"監控錯誤: {e}")
            
    def get_status(self):
        """獲取系統狀態"""
        return {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "directories": {
                "base": str(self.base_dir),
                "data": str(self.data_dir),
                "logs": str(self.logs_dir)
            }
        }

def main():
    parser = argparse.ArgumentParser(description='PowerAutomation EC2系統')
    parser.add_argument('action', choices=['monitor', 'extract', 'send', 'sync', 'status'], 
                       help='執行的操作')
    parser.add_argument('--repo', help='倉庫名稱')
    parser.add_argument('--message', help='要發送的消息')
    
    args = parser.parse_args()
    
    system = PowerAutomationEC2()
    
    if args.action == 'monitor':
        system.start_monitoring()
    elif args.action == 'extract':
        result = system.extract_trae_history(args.repo)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == 'send':
        if not args.repo or not args.message:
            print("錯誤: 發送消息需要 --repo 和 --message 參數")
            sys.exit(1)
        result = system.send_trae_message(args.repo, args.message)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == 'sync':
        result = system.sync_repositories()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == 'status':
        status = system.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

