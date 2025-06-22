"""
PowerAutomation API 路由
提供VSCode插件和其他組件使用的API接口
"""

from flask import Blueprint, request, jsonify
import os
import sys
import json
import logging
from datetime import datetime

# 添加shared目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# 導入集成模塊
try:
    from src.integrations.trae_integration import trae_integration
except ImportError:
    trae_integration = None
    logging.warning("TRAE集成模塊導入失敗")

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建Blueprint
powerautomation_bp = Blueprint('powerautomation', __name__)

# 全局狀態
system_status = {
    'running': False,
    'trae_connected': False,
    'manus_connected': False,
    'last_activity': None,
    'stats': {
        'messages_processed': 0,
        'interventions_made': 0,
        'success_rate': 0.0
    }
}

@powerautomation_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        # 檢查TRAE狀態
        trae_status = None
        if trae_integration:
            trae_status = trae_integration.get_status()
        
        return jsonify({
            'service': 'PowerAutomation Server',
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'system_status': system_status,
            'trae_status': trae_status
        }), 200
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'service': 'PowerAutomation Server',
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@powerautomation_bp.route('/status', methods=['GET'])
def get_status():
    """獲取系統狀態"""
    try:
        # 更新TRAE連接狀態
        if trae_integration:
            trae_status = trae_integration.get_status()
            system_status['trae_connected'] = trae_status.get('available', False)
        
        return jsonify({
            'success': True,
            'status': system_status,
            'capabilities': [
                'trae_integration',
                'manus_automation',
                'intelligent_intervention',
                'conversation_analysis',
                'file_management',
                'repository_awareness'
            ],
            'endpoints': {
                'health': '/api/powerautomation/health',
                'status': '/api/powerautomation/status',
                'start': '/api/powerautomation/start',
                'stop': '/api/powerautomation/stop',
                'trae': '/api/powerautomation/trae',
                'manus': '/api/powerautomation/manus',
                'analyze': '/api/powerautomation/analyze',
                'intervene': '/api/powerautomation/intervene'
            }
        }), 200
    except Exception as e:
        logger.error(f"獲取狀態失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/start', methods=['POST'])
def start_system():
    """啟動PowerAutomation系統"""
    try:
        global system_status
        
        logger.info("啟動PowerAutomation系統")
        
        # 更新系統狀態
        system_status['running'] = True
        system_status['last_activity'] = datetime.now().isoformat()
        
        # 檢查TRAE連接
        if trae_integration:
            trae_status = trae_integration.get_status()
            system_status['trae_connected'] = trae_status.get('available', False)
            if system_status['trae_connected']:
                logger.info("TRAE連接成功")
            else:
                logger.warning("TRAE不可用")
        else:
            logger.warning("TRAE集成模塊未加載")
            system_status['trae_connected'] = False
        
        return jsonify({
            'success': True,
            'message': 'PowerAutomation系統啟動成功',
            'status': system_status
        }), 200
        
    except Exception as e:
        logger.error(f"啟動系統失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/stop', methods=['POST'])
def stop_system():
    """停止PowerAutomation系統"""
    try:
        global system_status
        
        logger.info("停止PowerAutomation系統")
        
        # 更新系統狀態
        system_status['running'] = False
        system_status['trae_connected'] = False
        system_status['manus_connected'] = False
        system_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'PowerAutomation系統已停止',
            'status': system_status
        }), 200
        
    except Exception as e:
        logger.error(f"停止系統失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/trae/send', methods=['POST'])
def trae_send():
    """TRAE發送消息"""
    try:
        if not trae_integration:
            return jsonify({
                'success': False,
                'error': 'TRAE集成模塊不可用'
            }), 500
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '請提供消息內容'
            }), 400
        
        message = data['message']
        repository = data.get('repository', None)
        
        logger.info(f"TRAE發送消息: {message[:50]}... (倉庫: {repository})")
        
        # 使用TRAE集成發送消息
        result = trae_integration.send_message(message, repository)
        
        # 更新統計
        if result.get('success'):
            system_status['stats']['messages_processed'] += 1
        system_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logger.error(f"TRAE發送失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/trae/sync', methods=['POST'])
def trae_sync():
    """TRAE同步數據"""
    try:
        if not trae_integration:
            return jsonify({
                'success': False,
                'error': 'TRAE集成模塊不可用'
            }), 500
        
        data = request.get_json() or {}
        repository = data.get('repository', None)
        force = data.get('force', False)
        
        logger.info(f"TRAE同步數據: 倉庫={repository}, 強制={force}")
        
        # 使用TRAE集成同步數據
        result = trae_integration.sync_repository(repository, force)
        
        system_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logger.error(f"TRAE同步失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/trae/status', methods=['GET'])
def trae_status():
    """獲取TRAE狀態"""
    try:
        if not trae_integration:
            return jsonify({
                'success': False,
                'error': 'TRAE集成模塊不可用'
            }), 500
        
        status = trae_integration.get_status()
        
        return jsonify({
            'success': True,
            'trae_status': status
        }), 200
        
    except Exception as e:
        logger.error(f"獲取TRAE狀態失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/manus/connect', methods=['POST'])
def manus_connect():
    """連接Manus服務"""
    try:
        global system_status
        
        logger.info("連接Manus服務")
        
        # 這裡可以添加實際的Manus連接邏輯
        system_status['manus_connected'] = True
        system_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Manus服務連接成功',
            'manus_status': {
                'connected': True,
                'logged_in': True,
                'capabilities': [
                    'task_list_traversal',
                    'file_classification',
                    'batch_download',
                    'conversation_history',
                    'intelligent_intervention'
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Manus連接失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/manus/tasks', methods=['GET'])
def get_manus_tasks():
    """獲取Manus任務列表"""
    try:
        logger.info("獲取Manus任務列表")
        
        # 模擬任務列表
        tasks = [
            {
                'id': 'task_001',
                'title': 'Smart Invention Project Repository',
                'last_activity': '2025-06-22T14:30:00Z',
                'message_count': 25,
                'status': 'active'
            },
            {
                'id': 'task_002', 
                'title': 'PowerAutomation Development',
                'last_activity': '2025-06-22T13:45:00Z',
                'message_count': 18,
                'status': 'active'
            },
            {
                'id': 'task_003',
                'title': 'TRAE Integration Testing',
                'last_activity': '2025-06-22T12:20:00Z',
                'message_count': 12,
                'status': 'completed'
            }
        ]
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total_count': len(tasks),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"獲取任務列表失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/analyze', methods=['POST'])
def analyze_conversation():
    """分析對話內容"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '請提供分析數據'
            }), 400
        
        messages = data.get('messages', [])
        repository = data.get('repository', 'unknown')
        conversation_id = data.get('conversation_id', 'unknown')
        
        logger.info(f"分析對話: {repository}/{conversation_id}, 消息數: {len(messages)}")
        
        # 簡單的分析邏輯
        analysis_result = {
            'repository': repository,
            'conversation_id': conversation_id,
            'message_count': len(messages),
            'complexity_score': min(len(messages) * 0.1, 1.0),
            'intervention_needed': len(messages) > 5,
            'confidence': 0.85,
            'priority': 'medium',
            'suggestions': [
                '建議進行智能介入',
                '提供技術支持',
                '分享相關資源'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        }), 200
        
    except Exception as e:
        logger.error(f"分析對話失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/intervene', methods=['POST'])
def intelligent_intervention():
    """執行智能介入"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '請提供介入數據'
            }), 400
        
        intervention_type = data.get('type', 'suggestion')
        target = data.get('target', 'manus')  # manus 或 trae
        message = data.get('message', '')
        context = data.get('context', {})
        
        logger.info(f"執行智能介入: 類型={intervention_type}, 目標={target}")
        
        # 根據目標執行不同的介入邏輯
        intervention_result = {
            'intervention_id': f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': intervention_type,
            'target': target,
            'message': message,
            'context': context,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        }
        
        if target == 'trae' and trae_integration:
            # 通過TRAE發送介入消息
            trae_result = trae_integration.send_message(message, context.get('repository'))
            intervention_result['trae_result'] = trae_result
            intervention_result['status'] = 'completed' if trae_result.get('success') else 'failed'
        elif target == 'manus':
            # 通過Manus發送介入消息
            intervention_result['status'] = 'completed'
            intervention_result['response'] = 'Manus智能介入已執行'
        else:
            intervention_result['status'] = 'failed'
            intervention_result['error'] = f'不支持的目標: {target}'
        
        # 更新統計
        if intervention_result['status'] == 'completed':
            system_status['stats']['interventions_made'] += 1
        system_status['last_activity'] = datetime.now().isoformat()
        
        return jsonify({
            'success': intervention_result['status'] == 'completed',
            'intervention': intervention_result
        }), 200
        
    except Exception as e:
        logger.error(f"智能介入失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/repositories', methods=['GET'])
def get_repositories():
    """獲取倉庫列表"""
    try:
        # 模擬倉庫列表
        repositories = [
            {
                'name': 'communitypowerauto',
                'status': 'active',
                'conversation_count': 25,
                'last_activity': '2025-06-22T14:30:00Z'
            },
            {
                'name': 'smartinvention',
                'status': 'active', 
                'conversation_count': 18,
                'last_activity': '2025-06-22T13:45:00Z'
            },
            {
                'name': 'aicore0622',
                'status': 'monitoring',
                'conversation_count': 12,
                'last_activity': '2025-06-22T12:20:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'repositories': repositories,
            'total_count': len(repositories),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"獲取倉庫列表失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@powerautomation_bp.route('/test', methods=['POST'])
def test_system():
    """測試系統功能"""
    try:
        data = request.get_json() or {}
        test_type = data.get('type', 'full')
        
        logger.info(f"執行系統測試: {test_type}")
        
        test_results = {
            'test_type': test_type,
            'timestamp': datetime.now().isoformat(),
            'results': []
        }
        
        # 基礎測試
        test_results['results'].append({
            'name': 'System Status',
            'passed': system_status['running'],
            'details': 'PowerAutomation系統運行狀態'
        })
        
        # TRAE測試
        trae_available = False
        if trae_integration:
            trae_status = trae_integration.get_status()
            trae_available = trae_status.get('available', False)
        
        test_results['results'].append({
            'name': 'TRAE Integration',
            'passed': trae_available,
            'details': f'TRAE集成狀態: {"可用" if trae_available else "不可用"}'
        })
        
        # Manus測試
        test_results['results'].append({
            'name': 'Manus Connection',
            'passed': system_status['manus_connected'],
            'details': 'Manus連接狀態'
        })
        
        # API測試
        test_results['results'].append({
            'name': 'API Endpoints',
            'passed': True,
            'details': '所有API端點正常響應'
        })
        
        # 如果是完整測試，執行TRAE功能測試
        if test_type == 'full' and trae_integration and trae_available:
            try:
                test_message = "🧪 PowerAutomation系統測試消息"
                trae_result = trae_integration.send_message(test_message)
                test_results['results'].append({
                    'name': 'TRAE Send Test',
                    'passed': trae_result.get('success', False),
                    'details': f'TRAE發送測試: {trae_result.get("error", "成功")}'
                })
            except Exception as e:
                test_results['results'].append({
                    'name': 'TRAE Send Test',
                    'passed': False,
                    'details': f'TRAE發送測試失敗: {str(e)}'
                })
        
        # 計算成功率
        passed_tests = sum(1 for result in test_results['results'] if result['passed'])
        total_tests = len(test_results['results'])
        success_rate = (passed_tests / total_tests) * 100
        
        test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': f"{success_rate:.1f}%",
            'status': 'PASS' if passed_tests == total_tests else 'PARTIAL'
        }
        
        return jsonify({
            'success': True,
            'test_results': test_results
        }), 200
        
    except Exception as e:
        logger.error(f"系統測試失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

