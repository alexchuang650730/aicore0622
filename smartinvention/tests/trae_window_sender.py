#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
發送消息到現有TRAE窗口的測試腳本
測試各種方法將消息發送到已打開的TRAE會話
"""

import subprocess
import json
import time
from datetime import datetime
import os

class TraeWindowSender:
    """TRAE窗口發送器"""
    
    def __init__(self):
        self.trae_path = "/usr/local/bin/trae"
        self.test_results = []
        
    def test_trae_session_methods(self):
        """測試TRAE會話相關方法"""
        print("🔍 測試TRAE會話方法")
        print("=" * 50)
        
        test_message = "🎯 發送到現有TRAE窗口的測試消息"
        
        session_methods = [
            {
                "name": "指定會話ID",
                "command": f"echo '{test_message}' | {self.trae_path} - --session current"
            },
            {
                "name": "使用活動會話",
                "command": f"echo '{test_message}' | {self.trae_path} - --active"
            },
            {
                "name": "發送到最後會話",
                "command": f"echo '{test_message}' | {self.trae_path} - --last"
            },
            {
                "name": "指定窗口",
                "command": f"echo '{test_message}' | {self.trae_path} - --window main"
            },
            {
                "name": "使用target參數",
                "command": f"echo '{test_message}' | {self.trae_path} - --target existing"
            }
        ]
        
        for method in session_methods:
            print(f"\n📤 測試: {method['name']}")
            print(f"🔗 命令: {method['command']}")
            
            try:
                result = subprocess.run(
                    ["sh", "-c", method['command']],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                print(f"📊 返回碼: {result.returncode}")
                if result.stdout:
                    print(f"✅ 輸出: {result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤: {result.stderr}")
                
                self.test_results.append({
                    "method": method['name'],
                    "command": method['command'],
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                })
                
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 執行失敗: {e}")
    
    def test_applescript_methods(self):
        """測試AppleScript方法（Mac專用）"""
        print("\n🍎 測試AppleScript方法")
        print("=" * 50)
        
        test_message = "🍎 通過AppleScript發送的消息"
        
        applescript_methods = [
            {
                "name": "激活TRAE並發送",
                "script": f'''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                end tell
                
                tell application "Trae"
                    activate
                    delay 0.5
                end tell
                
                tell application "System Events"
                    keystroke "{test_message}"
                    key code 36  -- Enter key
                end tell
                '''
            },
            {
                "name": "查找TRAE窗口",
                "script": '''
                tell application "System Events"
                    set traeProcesses to every application process whose name contains "Trae"
                    repeat with traeProcess in traeProcesses
                        set windowList to every window of traeProcess
                        return (count of windowList)
                    end repeat
                end tell
                '''
            }
        ]
        
        for method in applescript_methods:
            print(f"\n🍎 測試: {method['name']}")
            
            try:
                result = subprocess.run(
                    ["osascript", "-e", method['script']],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                print(f"📊 返回碼: {result.returncode}")
                if result.stdout:
                    print(f"✅ 輸出: {result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤: {result.stderr}")
                
                self.test_results.append({
                    "method": f"AppleScript - {method['name']}",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                })
                
            except Exception as e:
                print(f"❌ AppleScript執行失敗: {e}")
    
    def test_trae_api_methods(self):
        """測試TRAE API方法"""
        print("\n🌐 測試TRAE API方法")
        print("=" * 50)
        
        test_message = "🌐 通過API發送的消息"
        
        # 常見的本地API端口
        api_ports = [3000, 8080, 8000, 9000, 7777]
        
        for port in api_ports:
            print(f"\n🔌 測試端口: {port}")
            
            api_methods = [
                {
                    "name": f"POST到端口{port}",
                    "command": f"curl -X POST http://localhost:{port}/api/send -H 'Content-Type: application/json' -d '{{\"message\": \"{test_message}\"}}'",
                    "timeout": 5
                },
                {
                    "name": f"WebSocket到端口{port}",
                    "command": f"curl -X GET http://localhost:{port}/api/status",
                    "timeout": 3
                }
            ]
            
            for method in api_methods:
                try:
                    result = subprocess.run(
                        ["sh", "-c", method['command']],
                        capture_output=True,
                        text=True,
                        timeout=method['timeout']
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        print(f"✅ {method['name']} 成功!")
                        print(f"📄 回應: {result.stdout}")
                        
                        self.test_results.append({
                            "method": method['name'],
                            "command": method['command'],
                            "returncode": result.returncode,
                            "stdout": result.stdout,
                            "success": True
                        })
                        break
                    
                except subprocess.TimeoutExpired:
                    print(f"⏰ {method['name']} 超時")
                except Exception as e:
                    print(f"❌ {method['name']} 失敗: {e}")
    
    def test_process_communication(self):
        """測試進程間通信方法"""
        print("\n🔄 測試進程間通信")
        print("=" * 50)
        
        try:
            # 查找TRAE進程
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            trae_processes = []
            for line in result.stdout.split('\n'):
                if 'trae' in line.lower() or 'Trae' in line:
                    trae_processes.append(line)
            
            print(f"🔍 找到的TRAE進程:")
            for process in trae_processes:
                print(f"  {process}")
            
            # 嘗試發送信號
            if trae_processes:
                print("\n📡 嘗試進程間通信...")
                # 這裡可以添加更多進程通信的方法
                
        except Exception as e:
            print(f"❌ 進程通信測試失敗: {e}")
    
    def test_file_based_communication(self):
        """測試基於文件的通信"""
        print("\n📁 測試文件通信方法")
        print("=" * 50)
        
        test_message = "📁 通過文件通信的消息"
        
        # 可能的TRAE通信文件位置
        comm_paths = [
            "/tmp/trae_input",
            "/tmp/trae_messages",
            "~/.trae/input",
            "~/.trae/messages",
            "/Users/alexchuang/.trae/input"
        ]
        
        for path in comm_paths:
            expanded_path = os.path.expanduser(path)
            print(f"\n📝 測試路徑: {expanded_path}")
            
            try:
                # 嘗試寫入文件
                with open(expanded_path, 'w', encoding='utf-8') as f:
                    f.write(test_message)
                
                print(f"✅ 成功寫入: {expanded_path}")
                
                # 檢查文件是否被讀取（等待一下）
                time.sleep(2)
                
                if os.path.exists(expanded_path):
                    file_size = os.path.getsize(expanded_path)
                    if file_size == 0:
                        print("🔄 文件已被清空，可能被TRAE讀取")
                    else:
                        print(f"📏 文件大小: {file_size} bytes")
                
                self.test_results.append({
                    "method": f"文件通信 - {path}",
                    "path": expanded_path,
                    "success": True
                })
                
            except Exception as e:
                print(f"❌ 文件寫入失敗: {e}")
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🎯 TRAE現有窗口發送測試")
        print("=" * 60)
        print("目標: 發送消息到右邊已打開的TRAE窗口")
        print("=" * 60)
        
        # 1. 測試TRAE會話方法
        self.test_trae_session_methods()
        
        # 2. 測試AppleScript方法
        self.test_applescript_methods()
        
        # 3. 測試API方法
        self.test_trae_api_methods()
        
        # 4. 測試進程通信
        self.test_process_communication()
        
        # 5. 測試文件通信
        self.test_file_based_communication()
        
        # 6. 生成報告
        self.generate_report()
    
    def generate_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 TRAE窗口發送測試報告")
        print("=" * 60)
        
        successful_methods = [r for r in self.test_results if r.get("success", False)]
        
        if successful_methods:
            print("🎉 找到可能的發送方法:")
            for method in successful_methods:
                print(f"✅ {method['method']}")
                if 'command' in method:
                    print(f"   命令: {method['command']}")
        else:
            print("⚠️  沒有找到明確的發送方法")
            print("💡 建議:")
            print("   1. 檢查TRAE是否有特定的API")
            print("   2. 查看TRAE文檔了解會話管理")
            print("   3. 嘗試使用TRAE的內建命令")
        
        # 保存結果
        filename = f"trae_window_send_test_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細結果已保存: {filename}")

def main():
    """主函數"""
    print("🚀 開始測試發送到現有TRAE窗口")
    print("🎯 目標: 讓消息出現在右邊已打開的TRAE會話中")
    
    sender = TraeWindowSender()
    sender.run_all_tests()
    
    print("\n🎉 測試完成!")
    print("💡 請查看結果，找到最適合的發送方法")

if __name__ == "__main__":
    main()

