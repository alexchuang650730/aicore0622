#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRAE-send 調試腳本
專門測試trae-send命令的各種用法
"""

import subprocess
import json
import time
from datetime import datetime
import os

class TraeSendDebugger:
    """TRAE-send調試器"""
    
    def __init__(self, trae_send_path):
        self.trae_send_path = trae_send_path
        self.test_results = []
        
    def test_trae_send_help(self):
        """測試trae-send幫助信息"""
        print("🔍 測試trae-send幫助信息")
        print("=" * 50)
        
        help_commands = [
            [self.trae_send_path, "--help"],
            [self.trae_send_path, "-h"],
            [self.trae_send_path, "help"],
            [self.trae_send_path]  # 無參數執行
        ]
        
        for cmd in help_commands:
            print(f"\n📋 嘗試: {' '.join(cmd)}")
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                print(f"返回碼: {result.returncode}")
                if result.stdout:
                    print(f"標準輸出:\n{result.stdout}")
                if result.stderr:
                    print(f"錯誤輸出:\n{result.stderr}")
                    
                self.test_results.append({
                    "test": "help",
                    "command": cmd,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
            except subprocess.TimeoutExpired:
                print("⏰ 命令執行超時")
            except Exception as e:
                print(f"❌ 執行錯誤: {e}")
    
    def test_trae_send_variations(self):
        """測試trae-send的各種參數組合"""
        print("\n🧪 測試trae-send參數組合")
        print("=" * 50)
        
        test_message = "🧪 PowerAutomation測試消息"
        test_repo = "test"
        
        # 各種可能的參數組合
        variations = [
            # 基本格式
            {
                "name": "基本格式 - repo參數",
                "command": [self.trae_send_path, test_repo],
                "input": test_message
            },
            {
                "name": "基本格式 - message參數",
                "command": [self.trae_send_path, "--message", test_message, test_repo],
                "input": None
            },
            {
                "name": "長參數格式",
                "command": [self.trae_send_path, "--repo", test_repo, "--message", test_message],
                "input": None
            },
            {
                "name": "短參數格式",
                "command": [self.trae_send_path, "-r", test_repo, "-m", test_message],
                "input": None
            },
            # 不同的輸入方式
            {
                "name": "stdin輸入",
                "command": [self.trae_send_path, test_repo],
                "input": test_message
            },
            {
                "name": "echo管道",
                "command": ["sh", "-c", f"echo '{test_message}' | {self.trae_send_path} {test_repo}"],
                "input": None
            },
            # 嘗試不同的倉庫名
            {
                "name": "main倉庫",
                "command": [self.trae_send_path, "main"],
                "input": test_message
            },
            {
                "name": "default倉庫",
                "command": [self.trae_send_path, "default"],
                "input": test_message
            },
            # 嘗試絕對路徑
            {
                "name": "當前目錄",
                "command": [self.trae_send_path, "."],
                "input": test_message
            }
        ]
        
        for i, variation in enumerate(variations, 1):
            print(f"\n📤 測試 {i}: {variation['name']}")
            print(f"🔗 命令: {' '.join(variation['command'])}")
            if variation['input']:
                print(f"📝 輸入: {variation['input']}")
            
            try:
                if variation['input']:
                    # 需要stdin輸入
                    process = subprocess.Popen(
                        variation['command'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate(input=variation['input'], timeout=15)
                    returncode = process.returncode
                else:
                    # 直接執行
                    result = subprocess.run(
                        variation['command'],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    stdout, stderr = result.stdout, result.stderr
                    returncode = result.returncode
                
                print(f"📊 返回碼: {returncode}")
                if stdout:
                    print(f"✅ 標準輸出:\n{stdout}")
                if stderr:
                    print(f"⚠️  錯誤輸出:\n{stderr}")
                
                # 判斷是否成功
                success = returncode == 0 and (stdout or not stderr)
                if success:
                    print("🎉 這個方法可能成功了！")
                
                self.test_results.append({
                    "test": "variation",
                    "name": variation['name'],
                    "command": variation['command'],
                    "input": variation['input'],
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
            except subprocess.TimeoutExpired:
                print("⏰ 命令執行超時")
                self.test_results.append({
                    "test": "variation",
                    "name": variation['name'],
                    "error": "timeout"
                })
            except Exception as e:
                print(f"❌ 執行錯誤: {e}")
                self.test_results.append({
                    "test": "variation",
                    "name": variation['name'],
                    "error": str(e)
                })
    
    def test_trae_send_environment(self):
        """測試trae-send的執行環境"""
        print("\n🔧 測試trae-send執行環境")
        print("=" * 50)
        
        # 檢查文件信息
        try:
            import stat
            file_stat = os.stat(self.trae_send_path)
            print(f"📁 文件路徑: {self.trae_send_path}")
            print(f"📏 文件大小: {file_stat.st_size} bytes")
            print(f"🔐 文件權限: {oct(file_stat.st_mode)}")
            print(f"⏰ 修改時間: {datetime.fromtimestamp(file_stat.st_mtime)}")
            
            # 檢查是否可執行
            if os.access(self.trae_send_path, os.X_OK):
                print("✅ 文件可執行")
            else:
                print("❌ 文件不可執行")
                
        except Exception as e:
            print(f"❌ 無法獲取文件信息: {e}")
        
        # 檢查文件類型
        try:
            result = subprocess.run(["file", self.trae_send_path], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📄 文件類型: {result.stdout.strip()}")
        except:
            pass
        
        # 檢查工作目錄
        print(f"📂 當前工作目錄: {os.getcwd()}")
        
        # 檢查環境變量
        relevant_env = {}
        for key in os.environ:
            if 'trae' in key.lower() or 'node' in key.lower() or 'npm' in key.lower():
                relevant_env[key] = os.environ[key]
        
        if relevant_env:
            print("🌍 相關環境變量:")
            for key, value in relevant_env.items():
                print(f"  {key}: {value}")
    
    def test_in_trae_directory(self):
        """在TRAE目錄中測試"""
        print("\n📁 在TRAE目錄中測試")
        print("=" * 50)
        
        trae_dir = "/Users/alexchuang/aiengine/trae/git"
        if os.path.exists(trae_dir):
            print(f"📂 切換到TRAE目錄: {trae_dir}")
            original_dir = os.getcwd()
            
            try:
                os.chdir(trae_dir)
                print(f"✅ 成功切換到: {os.getcwd()}")
                
                # 列出目錄內容
                files = os.listdir(".")
                print(f"📋 目錄內容: {', '.join(files[:10])}")
                
                # 在TRAE目錄中測試發送
                test_message = "🧪 在TRAE目錄中的測試消息"
                
                variations = [
                    {
                        "name": "相對路徑執行",
                        "command": ["./trae-send", "test"],
                        "input": test_message
                    },
                    {
                        "name": "絕對路徑執行",
                        "command": [self.trae_send_path, "test"],
                        "input": test_message
                    }
                ]
                
                for variation in variations:
                    print(f"\n📤 {variation['name']}")
                    print(f"🔗 命令: {' '.join(variation['command'])}")
                    
                    try:
                        process = subprocess.Popen(
                            variation['command'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        stdout, stderr = process.communicate(input=variation['input'], timeout=10)
                        
                        print(f"📊 返回碼: {process.returncode}")
                        if stdout:
                            print(f"✅ 輸出: {stdout}")
                        if stderr:
                            print(f"⚠️  錯誤: {stderr}")
                            
                        self.test_results.append({
                            "test": "trae_directory",
                            "name": variation['name'],
                            "working_dir": trae_dir,
                            "returncode": process.returncode,
                            "stdout": stdout,
                            "stderr": stderr
                        })
                        
                    except Exception as e:
                        print(f"❌ 執行錯誤: {e}")
                
            finally:
                os.chdir(original_dir)
                print(f"🔙 返回原目錄: {os.getcwd()}")
        else:
            print(f"❌ TRAE目錄不存在: {trae_dir}")
    
    def run_all_tests(self):
        """運行所有調試測試"""
        print("🔍 TRAE-send 詳細調試測試")
        print("=" * 60)
        print(f"🎯 測試目標: {self.trae_send_path}")
        print("=" * 60)
        
        # 1. 測試幫助信息
        self.test_trae_send_help()
        
        # 2. 測試執行環境
        self.test_trae_send_environment()
        
        # 3. 測試各種參數組合
        self.test_trae_send_variations()
        
        # 4. 在TRAE目錄中測試
        self.test_in_trae_directory()
        
        # 5. 生成調試報告
        self.generate_debug_report()
    
    def generate_debug_report(self):
        """生成調試報告"""
        print("\n" + "=" * 60)
        print("📊 TRAE-send 調試報告")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r.get("success", False)]
        
        if successful_tests:
            print("🎉 找到可能成功的方法:")
            for test in successful_tests:
                print(f"✅ {test['name']}")
                print(f"   命令: {' '.join(test['command'])}")
                if test.get('input'):
                    print(f"   輸入: {test['input']}")
                print(f"   輸出: {test['stdout']}")
        else:
            print("⚠️  沒有找到明顯成功的方法")
            print("💡 建議檢查:")
            print("   1. trae-send命令的正確用法")
            print("   2. 是否需要特定的工作目錄")
            print("   3. 是否需要配置文件或環境變量")
        
        # 保存詳細結果
        filename = f"trae_send_debug_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細調試結果已保存: {filename}")

def main():
    """主函數"""
    import sys
    
    if len(sys.argv) > 1:
        trae_send_path = sys.argv[1]
    else:
        # 默認路徑，用戶可以修改
        trae_send_path = input("請輸入trae-send的完整路徑: ").strip()
    
    if not os.path.exists(trae_send_path):
        print(f"❌ 文件不存在: {trae_send_path}")
        return
    
    print(f"🚀 開始調試 trae-send: {trae_send_path}")
    
    debugger = TraeSendDebugger(trae_send_path)
    debugger.run_all_tests()
    
    print("\n🎯 調試完成！請查看上面的結果和生成的JSON文件")

if __name__ == "__main__":
    main()

