"""
TRAE集成模塊
提供TRAE命令行工具的Python接口
"""

import subprocess
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TraeIntegration:
    """TRAE集成類"""
    
    def __init__(self):
        self.trae_available = self._check_trae_availability()
        
    def _check_trae_availability(self) -> bool:
        """檢查TRAE是否可用"""
        try:
            result = subprocess.run(['which', 'trae'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"檢查TRAE可用性失敗: {e}")
            return False
    
    def send_message(self, message: str, repository: Optional[str] = None) -> Dict[str, Any]:
        """通過TRAE發送消息"""
        try:
            if not self.trae_available:
                return {
                    'success': False,
                    'error': 'TRAE命令不可用',
                    'message': message
                }
            
            # 構建TRAE命令
            cmd = ['echo', message]
            trae_cmd = ['trae', '-']
            
            # 執行命令
            echo_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            trae_process = subprocess.Popen(trae_cmd, 
                                          stdin=echo_process.stdout,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          text=True)
            echo_process.stdout.close()
            
            stdout, stderr = trae_process.communicate(timeout=30)
            
            success = trae_process.returncode == 0
            
            result = {
                'success': success,
                'message': message,
                'repository': repository,
                'stdout': stdout,
                'stderr': stderr,
                'return_code': trae_process.returncode,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"TRAE消息發送成功: {message[:50]}...")
            else:
                logger.error(f"TRAE消息發送失敗: {stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error("TRAE命令執行超時")
            return {
                'success': False,
                'error': 'TRAE命令執行超時',
                'message': message
            }
        except Exception as e:
            logger.error(f"TRAE發送消息時出錯: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': message
            }
    
    def sync_repository(self, repository: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """同步TRAE倉庫數據"""
        try:
            if not self.trae_available:
                return {
                    'success': False,
                    'error': 'TRAE命令不可用'
                }
            
            # 構建同步命令
            cmd = ['trae', 'sync']
            if force:
                cmd.append('--force')
            if repository:
                cmd.extend(['--repository', repository])
            
            # 執行命令
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60)
            
            success = result.returncode == 0
            
            sync_result = {
                'success': success,
                'repository': repository,
                'force': force,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"TRAE同步成功: 倉庫={repository}")
                # 嘗試解析同步結果
                try:
                    if result.stdout:
                        # 這裡可以添加解析邏輯
                        sync_result['parsed_output'] = self._parse_sync_output(result.stdout)
                except Exception as e:
                    logger.warning(f"解析同步輸出失敗: {e}")
            else:
                logger.error(f"TRAE同步失敗: {result.stderr}")
            
            return sync_result
            
        except subprocess.TimeoutExpired:
            logger.error("TRAE同步命令執行超時")
            return {
                'success': False,
                'error': 'TRAE同步命令執行超時'
            }
        except Exception as e:
            logger.error(f"TRAE同步時出錯: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_sync_output(self, output: str) -> Dict[str, Any]:
        """解析同步輸出"""
        try:
            # 簡單的解析邏輯
            lines = output.strip().split('\n')
            parsed = {
                'total_lines': len(lines),
                'contains_json': False,
                'summary': {}
            }
            
            # 檢查是否包含JSON
            for line in lines:
                if line.strip().startswith('{') and line.strip().endswith('}'):
                    try:
                        json_data = json.loads(line)
                        parsed['contains_json'] = True
                        parsed['json_data'] = json_data
                        break
                    except:
                        continue
            
            return parsed
            
        except Exception as e:
            logger.warning(f"解析同步輸出時出錯: {e}")
            return {'error': str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """獲取TRAE狀態"""
        try:
            status = {
                'available': self.trae_available,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.trae_available:
                # 嘗試獲取TRAE版本信息
                try:
                    result = subprocess.run(['trae', '--version'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        status['version'] = result.stdout.strip()
                except:
                    status['version'] = 'unknown'
                
                # 嘗試獲取TRAE幫助信息
                try:
                    result = subprocess.run(['trae', '--help'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        status['help_available'] = True
                        status['commands'] = self._parse_help_output(result.stdout)
                except:
                    status['help_available'] = False
            
            return status
            
        except Exception as e:
            logger.error(f"獲取TRAE狀態時出錯: {e}")
            return {
                'available': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_help_output(self, help_output: str) -> List[str]:
        """解析幫助輸出，提取可用命令"""
        try:
            commands = []
            lines = help_output.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('-') and ' ' in line:
                    # 簡單的命令提取邏輯
                    parts = line.split()
                    if len(parts) > 0:
                        commands.append(parts[0])
            
            return list(set(commands))  # 去重
            
        except Exception as e:
            logger.warning(f"解析幫助輸出時出錯: {e}")
            return []

# 全局TRAE實例
trae_integration = TraeIntegration()

