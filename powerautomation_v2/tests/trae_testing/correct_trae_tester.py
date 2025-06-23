#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版TRAE測試腳本
使用正確的TRAE語法進行測試
"""

import subprocess
import json
import time
from datetime import datetime

class CorrectTraeTester:
    """修正版TRAE測試器"""
    
    def __init__(self):
        self.trae_path = "/usr/local/bin/trae"
        self.test_results = []
        
    def test_trae_send_correct(self):
        """使用正確的TRAE語法測試發送"""
        print("🚀 使用正確語法測試TRAE發送")
        print("=" * 50)
        
        test_messages = [
            "🧪 PowerAutomation測試消息 - 第一次嘗試",
            "🎮 我想要生成一個貪吃蛇遊戲",
            "📝 這是一個智能介入系統的測試消息"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 測試 {i}: 發送消息")
            print(f"💬 消息內容: {message}")
            
            try:
                # 使用正確的語法: echo "message" | trae -
                cmd = ["sh", "-c", f"echo '{message}' | {self.trae_path} -"]
                print(f"🔗 執行命令: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                print(f"📊 返回碼: {result.returncode}")
                if result.stdout:
                    print(f"✅ 標準輸出:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤輸出:\n{result.stderr}")
                
                success = result.returncode == 0
                if success:
                    print("🎉 消息發送成功！")
                else:
                    print("❌ 消息發送失敗")
                
                self.test_results.append({
                    "test": "correct_send",
                    "message": message,
                    "command": cmd,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 等待一下再發送下一條
                time.sleep(2)
                
            except subprocess.TimeoutExpired:
                print("⏰ 命令執行超時")
                self.test_results.append({
                    "test": "correct_send",
                    "message": message,
                    "error": "timeout"
                })
            except Exception as e:
                print(f"❌ 執行錯誤: {e}")
                self.test_results.append({
                    "test": "correct_send",
                    "message": message,
                    "error": str(e)
                })
    
    def test_trae_interactive(self):
        """測試TRAE交互模式"""
        print("\n🔄 測試TRAE交互模式")
        print("=" * 50)
        
        try:
            print("📝 嘗試直接與TRAE交互...")
            
            # 嘗試交互模式
            process = subprocess.Popen(
                [self.trae_path, "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            test_input = "🧪 交互模式測試消息\n"
            print(f"📤 發送: {test_input.strip()}")
            
            stdout, stderr = process.communicate(input=test_input, timeout=15)
            
            print(f"📊 返回碼: {process.returncode}")
            if stdout:
                print(f"✅ 輸出:\n{stdout}")
            if stderr:
                print(f"⚠️  錯誤:\n{stderr}")
            
            self.test_results.append({
                "test": "interactive",
                "input": test_input.strip(),
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "success": process.returncode == 0,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ 交互測試失敗: {e}")
            self.test_results.append({
                "test": "interactive",
                "error": str(e)
            })
    
    def test_trae_with_context(self):
        """測試帶上下文的TRAE發送"""
        print("\n🎯 測試帶上下文的TRAE發送")
        print("=" * 50)
        
        # 模擬真實的PowerAutomation場景
        context_messages = [
            {
                "context": "用戶問題: 我想要生成一個貪吃蛇遊戲",
                "response": "🎮 我來為您生成一個完整的貪吃蛇遊戲！包含HTML5 Canvas繪圖、JavaScript遊戲邏輯、CSS3樣式設計等完整功能。"
            },
            {
                "context": "用戶問題: 如何學習Python",
                "response": "📚 Python學習建議：1. 從基礎語法開始 2. 練習小項目 3. 閱讀優秀代碼 4. 參與開源項目"
            }
        ]
        
        for i, msg in enumerate(context_messages, 1):
            print(f"\n📋 場景 {i}:")
            print(f"🔍 上下文: {msg['context']}")
            print(f"💡 智能回覆: {msg['response']}")
            
            try:
                # 發送智能回覆到TRAE
                cmd = ["sh", "-c", f"echo '{msg['response']}' | {self.trae_path} -"]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                print(f"📊 發送結果: {result.returncode}")
                if result.stdout:
                    print(f"✅ TRAE回應:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤:\n{result.stderr}")
                
                self.test_results.append({
                    "test": "context_send",
                    "context": msg['context'],
                    "response": msg['response'],
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0,
                    "timestamp": datetime.now().isoformat()
                })
                
                time.sleep(3)  # 等待TRAE處理
                
            except Exception as e:
                print(f"❌ 上下文發送失敗: {e}")
    
    def test_trae_status(self):
        """測試TRAE狀態和信息"""
        print("\n📊 測試TRAE狀態")
        print("=" * 50)
        
        status_commands = [
            {
                "name": "TRAE版本",
                "command": [self.trae_path, "--version"]
            },
            {
                "name": "TRAE幫助",
                "command": [self.trae_path, "--help"]
            },
            {
                "name": "TRAE狀態",
                "command": [self.trae_path, "status"]
            }
        ]
        
        for cmd_info in status_commands:
            print(f"\n🔍 {cmd_info['name']}")
            try:
                result = subprocess.run(
                    cmd_info['command'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    print(f"✅ 輸出:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤:\n{result.stderr}")
                    
            except Exception as e:
                print(f"❌ 執行失敗: {e}")
    
    def run_all_tests(self):
        """運行所有修正版測試"""
        print("🎯 TRAE修正版功能測試")
        print("=" * 60)
        print("使用正確的TRAE語法: echo 'message' | trae -")
        print("=" * 60)
        
        # 1. 測試TRAE狀態
        self.test_trae_status()
        
        # 2. 測試正確的發送語法
        self.test_trae_send_correct()
        
        # 3. 測試交互模式
        self.test_trae_interactive()
        
        # 4. 測試帶上下文的發送
        self.test_trae_with_context()
        
        # 5. 生成測試報告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 TRAE修正版測試報告")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r.get("success", False)]
        total_tests = len(self.test_results)
        
        print(f"📋 測試結果:")
        for result in self.test_results:
            status = "✅ 成功" if result.get("success", False) else "❌ 失敗"
            test_name = result.get("test", "unknown")
            print(f"  {test_name}: {status}")
            
            if result.get("success", False) and result.get("stdout"):
                print(f"    輸出: {result['stdout'][:100]}...")
        
        # 保存詳細結果
        filename = f"trae_correct_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細測試結果已保存: {filename}")
        print(f"🎯 測試總結: {len(successful_tests)}/{total_tests} 成功")
        
        if successful_tests:
            print("🎉 TRAE消息發送功能正常工作！")
            print("✅ 可以集成到PowerAutomation系統")
        else:
            print("⚠️  需要進一步調試TRAE發送功能")

def main():
    """主函數"""
    print("🚀 開始TRAE修正版測試")
    print("🎯 使用正確的語法: echo 'message' | trae -")
    
    tester = CorrectTraeTester()
    tester.run_all_tests()
    
    print("\n🎉 測試完成！")
    print("💡 現在我們知道了TRAE的正確用法")

if __name__ == "__main__":
    main()

