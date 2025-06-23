#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRAE-sync專用測試腳本
專門測試trae sync功能的各種用法和場景
"""

import subprocess
import json
import time
from datetime import datetime
import os

class TraeSyncTester:
    """TRAE-sync測試器"""
    
    def __init__(self):
        self.trae_path = "/usr/local/bin/trae"
        self.test_results = []
        
    def test_basic_sync(self):
        """測試基本的sync功能"""
        print("🔄 測試基本TRAE sync功能")
        print("=" * 50)
        
        sync_commands = [
            {
                "name": "基本sync",
                "command": [self.trae_path, "sync"]
            },
            {
                "name": "sync with verbose",
                "command": [self.trae_path, "sync", "--verbose"]
            },
            {
                "name": "sync with force",
                "command": [self.trae_path, "sync", "--force"]
            },
            {
                "name": "sync all",
                "command": [self.trae_path, "sync", "--all"]
            },
            {
                "name": "sync status",
                "command": [self.trae_path, "sync", "--status"]
            }
        ]
        
        for cmd_info in sync_commands:
            print(f"\n🔄 測試: {cmd_info['name']}")
            print(f"🔗 命令: {' '.join(cmd_info['command'])}")
            
            try:
                result = subprocess.run(
                    cmd_info['command'],
                    capture_output=True,
                    text=True,
                    timeout=60  # 60秒超時
                )
                
                print(f"📊 返回碼: {result.returncode}")
                if result.stdout:
                    print(f"✅ 標準輸出:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤輸出:\n{result.stderr}")
                
                success = result.returncode == 0
                if success:
                    print("🎉 sync命令執行成功！")
                
                self.test_results.append({
                    "test": "basic_sync",
                    "name": cmd_info['name'],
                    "command": cmd_info['command'],
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
                time.sleep(2)  # 等待一下再執行下一個
                
            except subprocess.TimeoutExpired:
                print("⏰ sync命令執行超時")
                self.test_results.append({
                    "test": "basic_sync",
                    "name": cmd_info['name'],
                    "error": "timeout"
                })
            except Exception as e:
                print(f"❌ sync命令執行失敗: {e}")
                self.test_results.append({
                    "test": "basic_sync",
                    "name": cmd_info['name'],
                    "error": str(e)
                })
    
    def test_sync_with_repos(self):
        """測試指定倉庫的sync"""
        print("\n📁 測試指定倉庫的sync")
        print("=" * 50)
        
        # 常見的倉庫名稱
        repo_names = ["main", "test", "default", "current", "active"]
        
        for repo in repo_names:
            print(f"\n📁 測試倉庫: {repo}")
            
            repo_commands = [
                {
                    "name": f"sync {repo}",
                    "command": [self.trae_path, "sync", repo]
                },
                {
                    "name": f"sync --repo {repo}",
                    "command": [self.trae_path, "sync", "--repo", repo]
                }
            ]
            
            for cmd_info in repo_commands:
                print(f"🔗 {cmd_info['name']}: {' '.join(cmd_info['command'])}")
                
                try:
                    result = subprocess.run(
                        cmd_info['command'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ 成功: {result.stdout}")
                    else:
                        print(f"❌ 失敗: {result.stderr}")
                    
                    self.test_results.append({
                        "test": "repo_sync",
                        "repo": repo,
                        "name": cmd_info['name'],
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "success": result.returncode == 0
                    })
                    
                except Exception as e:
                    print(f"❌ 執行失敗: {e}")
    
    def test_sync_help(self):
        """測試sync的幫助信息"""
        print("\n❓ 測試sync幫助信息")
        print("=" * 50)
        
        help_commands = [
            {
                "name": "sync help",
                "command": [self.trae_path, "sync", "--help"]
            },
            {
                "name": "sync -h",
                "command": [self.trae_path, "sync", "-h"]
            },
            {
                "name": "help sync",
                "command": [self.trae_path, "help", "sync"]
            }
        ]
        
        for cmd_info in help_commands:
            print(f"\n❓ {cmd_info['name']}")
            
            try:
                result = subprocess.run(
                    cmd_info['command'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    print(f"📖 幫助信息:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤: {result.stderr}")
                
                self.test_results.append({
                    "test": "sync_help",
                    "name": cmd_info['name'],
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
            except Exception as e:
                print(f"❌ 幫助命令失敗: {e}")
    
    def test_sync_status_check(self):
        """測試sync狀態檢查"""
        print("\n📊 測試sync狀態檢查")
        print("=" * 50)
        
        status_commands = [
            {
                "name": "sync status",
                "command": [self.trae_path, "sync", "--status"]
            },
            {
                "name": "sync list",
                "command": [self.trae_path, "sync", "--list"]
            },
            {
                "name": "sync info",
                "command": [self.trae_path, "sync", "--info"]
            },
            {
                "name": "sync check",
                "command": [self.trae_path, "sync", "--check"]
            }
        ]
        
        for cmd_info in status_commands:
            print(f"\n📊 {cmd_info['name']}")
            
            try:
                result = subprocess.run(
                    cmd_info['command'],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                print(f"返回碼: {result.returncode}")
                if result.stdout:
                    print(f"✅ 狀態信息:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤: {result.stderr}")
                
                self.test_results.append({
                    "test": "sync_status",
                    "name": cmd_info['name'],
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                })
                
            except Exception as e:
                print(f"❌ 狀態檢查失敗: {e}")
    
    def test_sync_with_powerautomation(self):
        """測試PowerAutomation場景下的sync"""
        print("\n🤖 測試PowerAutomation場景下的sync")
        print("=" * 50)
        
        # 模擬PowerAutomation的sync需求
        scenarios = [
            {
                "name": "智能介入後同步",
                "description": "發送智能回覆後同步所有倉庫",
                "command": [self.trae_path, "sync", "--all"]
            },
            {
                "name": "定期同步檢查",
                "description": "定期檢查同步狀態",
                "command": [self.trae_path, "sync", "--status"]
            },
            {
                "name": "強制同步更新",
                "description": "強制同步最新狀態",
                "command": [self.trae_path, "sync", "--force"]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🎯 場景: {scenario['name']}")
            print(f"📝 描述: {scenario['description']}")
            print(f"🔗 命令: {' '.join(scenario['command'])}")
            
            try:
                start_time = time.time()
                
                result = subprocess.run(
                    scenario['command'],
                    capture_output=True,
                    text=True,
                    timeout=45
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"⏱️  執行時間: {duration:.2f}秒")
                print(f"📊 返回碼: {result.returncode}")
                
                if result.stdout:
                    print(f"✅ 輸出:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️  錯誤:\n{result.stderr}")
                
                success = result.returncode == 0
                if success:
                    print("🎉 PowerAutomation場景測試成功！")
                
                self.test_results.append({
                    "test": "powerautomation_sync",
                    "scenario": scenario['name'],
                    "description": scenario['description'],
                    "command": scenario['command'],
                    "duration": duration,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
            except subprocess.TimeoutExpired:
                print("⏰ PowerAutomation場景測試超時")
            except Exception as e:
                print(f"❌ PowerAutomation場景測試失敗: {e}")
    
    def run_all_tests(self):
        """運行所有sync測試"""
        print("🔄 TRAE-sync 完整功能測試")
        print("=" * 60)
        print("測試目標: 驗證trae sync的各種功能和用法")
        print("=" * 60)
        
        # 1. 測試基本sync功能
        self.test_basic_sync()
        
        # 2. 測試幫助信息
        self.test_sync_help()
        
        # 3. 測試狀態檢查
        self.test_sync_status_check()
        
        # 4. 測試指定倉庫sync
        self.test_sync_with_repos()
        
        # 5. 測試PowerAutomation場景
        self.test_sync_with_powerautomation()
        
        # 6. 生成測試報告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 TRAE-sync 測試報告")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r.get("success", False)]
        total_tests = len(self.test_results)
        
        print(f"📋 測試結果總覽:")
        test_categories = {}
        for result in self.test_results:
            category = result.get("test", "unknown")
            if category not in test_categories:
                test_categories[category] = {"success": 0, "total": 0}
            test_categories[category]["total"] += 1
            if result.get("success", False):
                test_categories[category]["success"] += 1
        
        for category, stats in test_categories.items():
            success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"  {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n🎯 總體成功率: {len(successful_tests)}/{total_tests} ({(len(successful_tests)/total_tests)*100:.1f}%)")
        
        if successful_tests:
            print("\n✅ 成功的sync方法:")
            for test in successful_tests:
                if 'command' in test:
                    print(f"  • {test.get('name', 'Unknown')}: {' '.join(test['command'])}")
        
        # 保存詳細結果
        filename = f"trae_sync_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細測試結果已保存: {filename}")
        
        # 給出建議
        if len(successful_tests) > 0:
            print("\n🎉 TRAE-sync功能測試成功！")
            print("✅ 可以集成到PowerAutomation系統")
            print("💡 建議使用成功的sync方法")
        else:
            print("\n⚠️  TRAE-sync功能需要進一步檢查")
            print("💡 建議:")
            print("   1. 檢查TRAE版本和配置")
            print("   2. 查看TRAE文檔了解sync用法")
            print("   3. 確認sync功能是否已啟用")

def main():
    """主函數"""
    print("🚀 開始TRAE-sync功能測試")
    print("🎯 測試目標: 驗證trae sync的完整功能")
    
    tester = TraeSyncTester()
    tester.run_all_tests()
    
    print("\n🎉 TRAE-sync測試完成！")
    print("💡 請查看測試報告和生成的JSON文件")

if __name__ == "__main__":
    main()

