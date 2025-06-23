#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRAE功能測試腳本
測試TRAE-send和TRAE-sync功能
"""

import asyncio
import subprocess
import json
import time
from datetime import datetime
import logging

class TraeFunctionTester:
    """TRAE功能測試器"""
    
    def __init__(self):
        self.ssh_config = {
            "host": "serveo.net",
            "port": 41269,
            "user": "alexchuang",
            "password": "123456"
        }
        self.test_results = []
        
        # 設置日誌
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _build_ssh_command(self):
        """構建SSH命令"""
        return [
            "sshpass", "-p", self.ssh_config["password"],
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-p", str(self.ssh_config["port"]),
            f"{self.ssh_config['user']}@{self.ssh_config['host']}"
        ]
    
    async def test_trae_send(self, repo_name="test", message="🧪 PowerAutomation測試消息"):
        """測試TRAE-send功能"""
        print(f"\n🚀 測試TRAE-send功能")
        print("=" * 50)
        
        try:
            # 構建SSH命令
            ssh_cmd = self._build_ssh_command()
            
            # 構建TRAE發送命令
            trae_cmd = f"cd /home/alexchuang/aiengine/trae/git && echo '{message}' | trae-send {repo_name}"
            
            print(f"📤 發送消息: {message}")
            print(f"📁 目標倉庫: {repo_name}")
            print(f"🔗 SSH命令: {' '.join(ssh_cmd)} '{trae_cmd}'")
            
            # 執行命令
            full_cmd = ssh_cmd + [trae_cmd]
            
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = await asyncio.get_event_loop().run_in_executor(
                None, process.communicate
            )
            
            result = {
                "function": "trae-send",
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "message": message,
                "repo_name": repo_name,
                "timestamp": datetime.now().isoformat()
            }
            
            if result["success"]:
                print("✅ TRAE-send 測試成功！")
                print(f"📄 輸出: {stdout}")
            else:
                print("❌ TRAE-send 測試失敗")
                print(f"❌ 錯誤: {stderr}")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ TRAE-send 測試異常: {e}")
            result = {
                "function": "trae-send",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    async def test_trae_sync(self):
        """測試TRAE-sync功能"""
        print(f"\n🔄 測試TRAE-sync功能")
        print("=" * 50)
        
        try:
            # 構建SSH命令
            ssh_cmd = self._build_ssh_command()
            
            # 構建TRAE同步命令
            sync_cmd = "cd /home/alexchuang/aiengine/trae/git && python3 scripts/sync_repositories.py --all"
            
            print(f"🔄 執行同步命令")
            print(f"🔗 SSH命令: {' '.join(ssh_cmd)} '{sync_cmd}'")
            
            # 執行命令
            full_cmd = ssh_cmd + [sync_cmd]
            
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = await asyncio.get_event_loop().run_in_executor(
                None, process.communicate
            )
            
            result = {
                "function": "trae-sync",
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            if result["success"]:
                print("✅ TRAE-sync 測試成功！")
                print(f"📄 輸出: {stdout}")
            else:
                print("❌ TRAE-sync 測試失敗")
                print(f"❌ 錯誤: {stderr}")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ TRAE-sync 測試異常: {e}")
            result = {
                "function": "trae-sync",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    async def test_ssh_connection(self):
        """測試SSH連接"""
        print(f"\n🔗 測試SSH連接")
        print("=" * 50)
        
        try:
            ssh_cmd = self._build_ssh_command()
            test_cmd = "echo 'SSH連接測試成功'"
            
            full_cmd = ssh_cmd + [test_cmd]
            
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = await asyncio.get_event_loop().run_in_executor(
                None, process.communicate
            )
            
            result = {
                "function": "ssh-connection",
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            if result["success"]:
                print("✅ SSH連接測試成功！")
                print(f"📄 回應: {stdout.strip()}")
            else:
                print("❌ SSH連接測試失敗")
                print(f"❌ 錯誤: {stderr}")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ SSH連接測試異常: {e}")
            result = {
                "function": "ssh-connection",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    async def run_all_tests(self):
        """運行所有測試"""
        print("🧪 PowerAutomation TRAE功能完整測試")
        print("=" * 60)
        
        # 1. 測試SSH連接
        ssh_result = await self.test_ssh_connection()
        
        if not ssh_result["success"]:
            print("\n❌ SSH連接失敗，無法繼續測試TRAE功能")
            return False
        
        # 2. 測試TRAE-send
        send_result = await self.test_trae_send()
        
        # 3. 測試TRAE-sync
        sync_result = await self.test_trae_sync()
        
        # 4. 生成測試報告
        self.generate_test_report()
        
        return all(result["success"] for result in self.test_results)
    
    def generate_test_report(self):
        """生成測試報告"""
        print("\n" + "=" * 60)
        print("📊 TRAE功能測試報告")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅ 成功" if result["success"] else "❌ 失敗"
            print(f"{result['function']}: {status}")
            
            if not result["success"]:
                if "error" in result:
                    print(f"  錯誤: {result['error']}")
                elif "stderr" in result:
                    print(f"  錯誤: {result['stderr']}")
        
        # 保存詳細結果
        filename = f"trae_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細測試結果已保存: {filename}")
        
        success_count = sum(1 for r in self.test_results if r["success"])
        total_count = len(self.test_results)
        
        print(f"\n🎯 測試總結: {success_count}/{total_count} 通過")
        
        if success_count == total_count:
            print("🎉 所有TRAE功能測試通過！")
        else:
            print("⚠️  部分功能需要檢查")

async def main():
    """主函數"""
    tester = TraeFunctionTester()
    
    print("🚀 開始TRAE功能驗證測試")
    print("測試項目: TRAE-send, TRAE-sync")
    
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 所有TRAE功能驗證完成！")
    else:
        print("\n⚠️  部分功能需要進一步檢查")

if __name__ == "__main__":
    asyncio.run(main())

