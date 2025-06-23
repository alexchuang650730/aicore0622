#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mac端TRAE功能測試腳本
直接在Mac上測試真實的TRAE-send和TRAE-sync功能
"""

import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class MacTraeTester:
    """Mac端TRAE功能測試器"""
    
    def __init__(self):
        self.test_results = []
        self.trae_paths = []
        self.found_trae_commands = {}
        
    def find_trae_commands(self):
        """查找TRAE相關命令"""
        print("🔍 查找TRAE命令...")
        print("=" * 50)
        
        # 可能的TRAE路徑
        search_paths = [
            "/Users/alexchuang/aiengine/trae/git",
            "/Users/alexchuang/aiengine/trae",
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "~/.npm-global/bin",
            "~/node_modules/.bin"
        ]
        
        # 可能的命令名稱
        command_names = [
            "trae-send",
            "trae-sync", 
            "trae",
            "send_message.py",
            "sync_repositories.py"
        ]
        
        for search_path in search_paths:
            expanded_path = os.path.expanduser(search_path)
            if os.path.exists(expanded_path):
                print(f"📁 檢查路徑: {expanded_path}")
                
                for command in command_names:
                    command_path = os.path.join(expanded_path, command)
                    if os.path.exists(command_path):
                        self.found_trae_commands[command] = command_path
                        print(f"✅ 找到: {command} -> {command_path}")
                
                # 遞歸查找scripts目錄
                scripts_path = os.path.join(expanded_path, "scripts")
                if os.path.exists(scripts_path):
                    print(f"📁 檢查scripts: {scripts_path}")
                    for command in command_names:
                        script_path = os.path.join(scripts_path, command)
                        if os.path.exists(script_path):
                            self.found_trae_commands[command] = script_path
                            print(f"✅ 找到: {command} -> {script_path}")
        
        # 檢查PATH中的命令
        print("\n🔍 檢查PATH中的TRAE命令...")
        for command in ["trae-send", "trae-sync", "trae"]:
            try:
                result = subprocess.run(["which", command], capture_output=True, text=True)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    self.found_trae_commands[command] = path
                    print(f"✅ PATH中找到: {command} -> {path}")
            except:
                pass
        
        # 檢查npm全局包
        print("\n🔍 檢查npm全局包...")
        try:
            result = subprocess.run(["npm", "list", "-g", "--depth=0"], capture_output=True, text=True)
            if "trae" in result.stdout:
                print("✅ 找到npm全局trae包")
        except:
            pass
        
        print(f"\n📊 總共找到 {len(self.found_trae_commands)} 個TRAE命令")
        return len(self.found_trae_commands) > 0
    
    def test_trae_send(self, message="🧪 Mac端PowerAutomation測試消息", repo="test"):
        """測試TRAE-send功能"""
        print(f"\n🚀 測試TRAE-send功能")
        print("=" * 50)
        
        # 嘗試不同的發送方法
        send_methods = []
        
        # 方法1: 直接使用trae-send命令
        if "trae-send" in self.found_trae_commands:
            send_methods.append({
                "name": "trae-send命令",
                "command": [self.found_trae_commands["trae-send"], repo],
                "input": message
            })
        
        # 方法2: 使用Python腳本
        if "send_message.py" in self.found_trae_commands:
            send_methods.append({
                "name": "send_message.py腳本",
                "command": ["python3", self.found_trae_commands["send_message.py"], "--repo", repo, "--message", message],
                "input": None
            })
        
        # 方法3: 嘗試trae命令
        if "trae" in self.found_trae_commands:
            send_methods.append({
                "name": "trae命令",
                "command": [self.found_trae_commands["trae"], "send", repo],
                "input": message
            })
        
        if not send_methods:
            print("❌ 未找到可用的TRAE-send方法")
            result = {
                "function": "trae-send",
                "success": False,
                "error": "未找到TRAE-send命令",
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        # 嘗試每種方法
        for method in send_methods:
            print(f"\n📤 嘗試方法: {method['name']}")
            print(f"🔗 命令: {' '.join(method['command'])}")
            
            try:
                if method['input']:
                    # 需要stdin輸入的命令
                    process = subprocess.Popen(
                        method['command'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(input=method['input'])
                else:
                    # 直接執行的命令
                    process = subprocess.run(
                        method['command'],
                        capture_output=True,
                        text=True
                    )
                    stdout, stderr = process.stdout, process.stderr
                
                result = {
                    "function": "trae-send",
                    "method": method['name'],
                    "success": process.returncode == 0,
                    "return_code": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "message": message,
                    "repo": repo,
                    "timestamp": datetime.now().isoformat()
                }
                
                if result["success"]:
                    print(f"✅ {method['name']} 測試成功！")
                    print(f"📄 輸出: {stdout}")
                    self.test_results.append(result)
                    return result
                else:
                    print(f"❌ {method['name']} 測試失敗")
                    print(f"❌ 錯誤: {stderr}")
                    
            except Exception as e:
                print(f"❌ {method['name']} 執行異常: {e}")
        
        # 所有方法都失敗
        result = {
            "function": "trae-send",
            "success": False,
            "error": "所有TRAE-send方法都失敗",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        return result
    
    def test_trae_sync(self):
        """測試TRAE-sync功能"""
        print(f"\n🔄 測試TRAE-sync功能")
        print("=" * 50)
        
        # 嘗試不同的同步方法
        sync_methods = []
        
        # 方法1: 直接使用trae-sync命令
        if "trae-sync" in self.found_trae_commands:
            sync_methods.append({
                "name": "trae-sync命令",
                "command": [self.found_trae_commands["trae-sync"]]
            })
        
        # 方法2: 使用Python腳本
        if "sync_repositories.py" in self.found_trae_commands:
            sync_methods.append({
                "name": "sync_repositories.py腳本",
                "command": ["python3", self.found_trae_commands["sync_repositories.py"], "--all"]
            })
        
        # 方法3: 嘗試trae命令
        if "trae" in self.found_trae_commands:
            sync_methods.append({
                "name": "trae sync命令",
                "command": [self.found_trae_commands["trae"], "sync"]
            })
        
        if not sync_methods:
            print("❌ 未找到可用的TRAE-sync方法")
            result = {
                "function": "trae-sync",
                "success": False,
                "error": "未找到TRAE-sync命令",
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
        
        # 嘗試每種方法
        for method in sync_methods:
            print(f"\n🔄 嘗試方法: {method['name']}")
            print(f"🔗 命令: {' '.join(method['command'])}")
            
            try:
                process = subprocess.run(
                    method['command'],
                    capture_output=True,
                    text=True,
                    timeout=60  # 60秒超時
                )
                
                result = {
                    "function": "trae-sync",
                    "method": method['name'],
                    "success": process.returncode == 0,
                    "return_code": process.returncode,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "timestamp": datetime.now().isoformat()
                }
                
                if result["success"]:
                    print(f"✅ {method['name']} 測試成功！")
                    print(f"📄 輸出: {process.stdout}")
                    self.test_results.append(result)
                    return result
                else:
                    print(f"❌ {method['name']} 測試失敗")
                    print(f"❌ 錯誤: {process.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {method['name']} 執行超時")
            except Exception as e:
                print(f"❌ {method['name']} 執行異常: {e}")
        
        # 所有方法都失敗
        result = {
            "function": "trae-sync",
            "success": False,
            "error": "所有TRAE-sync方法都失敗",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        return result
    
    def test_trae_environment(self):
        """測試TRAE環境"""
        print(f"\n🔧 測試TRAE環境")
        print("=" * 50)
        
        env_checks = []
        
        # 檢查Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                env_checks.append(f"✅ Node.js: {result.stdout.strip()}")
            else:
                env_checks.append("❌ Node.js: 未安裝")
        except:
            env_checks.append("❌ Node.js: 未找到")
        
        # 檢查npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                env_checks.append(f"✅ npm: {result.stdout.strip()}")
            else:
                env_checks.append("❌ npm: 未安裝")
        except:
            env_checks.append("❌ npm: 未找到")
        
        # 檢查Python
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                env_checks.append(f"✅ Python3: {result.stdout.strip()}")
            else:
                env_checks.append("❌ Python3: 未安裝")
        except:
            env_checks.append("❌ Python3: 未找到")
        
        # 檢查TRAE目錄
        trae_dir = "/Users/alexchuang/aiengine/trae/git"
        if os.path.exists(trae_dir):
            env_checks.append(f"✅ TRAE目錄: {trae_dir}")
            
            # 列出目錄內容
            try:
                files = os.listdir(trae_dir)
                env_checks.append(f"📁 TRAE文件: {', '.join(files[:5])}...")
            except:
                env_checks.append("❌ 無法讀取TRAE目錄")
        else:
            env_checks.append(f"❌ TRAE目錄不存在: {trae_dir}")
        
        for check in env_checks:
            print(check)
        
        return env_checks
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🧪 Mac端TRAE功能真實測試")
        print("=" * 60)
        print("測試模式: 真實命令測試")
        print("=" * 60)
        
        # 1. 測試環境檢查
        env_checks = self.test_trae_environment()
        
        # 2. 查找TRAE命令
        found_commands = self.find_trae_commands()
        
        if not found_commands:
            print("\n❌ 未找到任何TRAE命令，無法繼續測試")
            print("💡 請檢查TRAE是否正確安裝")
            return False
        
        # 3. 測試TRAE-send
        send_result = self.test_trae_send()
        
        # 4. 測試TRAE-sync
        sync_result = self.test_trae_sync()
        
        # 5. 生成測試報告
        self.generate_test_report(env_checks)
        
        return any(result.get("success", False) for result in self.test_results)
    
    def generate_test_report(self, env_checks):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 Mac端TRAE功能測試報告")
        print("=" * 60)
        
        print("\n🔧 環境檢查:")
        for check in env_checks:
            print(f"  {check}")
        
        print(f"\n🔍 找到的TRAE命令:")
        for command, path in self.found_trae_commands.items():
            print(f"  {command}: {path}")
        
        print(f"\n📋 功能測試結果:")
        for result in self.test_results:
            status = "✅ 成功" if result.get("success", False) else "❌ 失敗"
            method = result.get("method", "")
            print(f"  {result['function']} ({method}): {status}")
            
            if not result.get("success", False) and "error" in result:
                print(f"    錯誤: {result['error']}")
        
        # 保存詳細結果
        filename = f"mac_trae_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "environment_checks": env_checks,
                "found_commands": self.found_trae_commands,
                "test_results": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細測試結果已保存: {filename}")
        
        success_count = sum(1 for r in self.test_results if r.get("success", False))
        total_count = len(self.test_results)
        
        print(f"\n🎯 測試總結: {success_count}/{total_count} 通過")
        
        if success_count > 0:
            print("🎉 部分TRAE功能測試成功！")
            print("✅ 找到可用的TRAE命令")
        else:
            print("⚠️  所有TRAE功能測試失敗")
            print("💡 請檢查TRAE安裝和配置")

def main():
    """主函數"""
    print("🚀 Mac端TRAE功能真實測試開始")
    print("📝 測試項目: 環境檢查, 命令查找, TRAE-send, TRAE-sync")
    print("=" * 60)
    
    tester = MacTraeTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TRAE功能測試完成！")
        print("✅ 找到並測試了可用的TRAE功能")
    else:
        print("\n⚠️  TRAE功能測試需要進一步檢查")
        print("💡 建議檢查TRAE安裝和環境配置")

if __name__ == "__main__":
    main()

