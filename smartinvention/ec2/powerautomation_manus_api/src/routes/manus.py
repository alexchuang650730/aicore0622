"""
PowerAutomation Manus 集成 API 路由
提供與Manus瀏覽器控制器的REST API接口
"""

from flask import Blueprint, request, jsonify
import asyncio
import json
import logging
import sys
import os

# 添加shared目錄到路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from manus_browser_controller import ManusAutomationService

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建Blueprint
manus_bp = Blueprint('manus', __name__)

# 全局服務實例
manus_service = None

def get_event_loop():
    """獲取或創建事件循環"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

def run_async(coro):
    """運行異步函數"""
    loop = get_event_loop()
    return loop.run_until_complete(coro)

@manus_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        global manus_service
        
        status = {
            'service': 'PowerAutomation Manus Integration',
            'status': 'healthy',
            'manus_service_running': manus_service is not None and manus_service.is_running,
            'timestamp': '2025-06-22T13:40:00Z'
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return jsonify({
            'service': 'PowerAutomation Manus Integration',
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@manus_bp.route('/start', methods=['POST'])
def start_manus_service():
    """啟動Manus服務"""
    try:
        global manus_service
        
        logger.info("收到啟動Manus服務請求")
        
        if manus_service and manus_service.is_running:
            return jsonify({
                'success': True,
                'message': 'Manus服務已在運行中',
                'status': 'already_running'
            }), 200
        
        # 創建新的服務實例
        manus_service = ManusAutomationService()
        
        # 啟動服務
        success = run_async(manus_service.start_service())
        
        if success:
            logger.info("Manus服務啟動成功")
            return jsonify({
                'success': True,
                'message': 'Manus服務啟動成功',
                'status': 'started'
            }), 200
        else:
            logger.error("Manus服務啟動失敗")
            return jsonify({
                'success': False,
                'message': 'Manus服務啟動失敗',
                'status': 'failed'
            }), 500
            
    except Exception as e:
        logger.error(f"啟動Manus服務時出錯: {e}")
        return jsonify({
            'success': False,
            'message': f'啟動服務時出錯: {str(e)}',
            'status': 'error'
        }), 500

@manus_bp.route('/stop', methods=['POST'])
def stop_manus_service():
    """停止Manus服務"""
    try:
        global manus_service
        
        logger.info("收到停止Manus服務請求")
        
        if not manus_service or not manus_service.is_running:
            return jsonify({
                'success': True,
                'message': 'Manus服務未在運行',
                'status': 'not_running'
            }), 200
        
        # 停止服務
        run_async(manus_service.stop_service())
        manus_service = None
        
        logger.info("Manus服務已停止")
        return jsonify({
            'success': True,
            'message': 'Manus服務已停止',
            'status': 'stopped'
        }), 200
        
    except Exception as e:
        logger.error(f"停止Manus服務時出錯: {e}")
        return jsonify({
            'success': False,
            'message': f'停止服務時出錯: {str(e)}',
            'status': 'error'
        }), 500

@manus_bp.route('/send_message', methods=['POST'])
def send_message():
    """發送消息到Manus"""
    try:
        global manus_service
        
        if not manus_service or not manus_service.is_running:
            return jsonify({
                'success': False,
                'error': 'Manus服務未運行，請先啟動服務'
            }), 400
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '請提供消息內容'
            }), 400
        
        message = data['message']
        context = data.get('context', {})
        
        logger.info(f"收到發送消息請求: {message[:50]}...")
        
        # 發送智能回應
        result = run_async(manus_service.send_intelligent_response(message))
        
        # 添加上下文信息
        result['context'] = context
        result['request_timestamp'] = '2025-06-22T13:40:00Z'
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"發送消息時出錯: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manus_bp.route('/get_conversation', methods=['GET'])
def get_conversation():
    """獲取對話狀態"""
    try:
        global manus_service
        
        if not manus_service or not manus_service.is_running:
            return jsonify({
                'success': False,
                'error': 'Manus服務未運行'
            }), 400
        
        logger.info("獲取對話狀態")
        
        # 獲取對話狀態
        status = run_async(manus_service.get_conversation_status())
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"獲取對話狀態時出錯: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manus_bp.route('/analyze_conversation', methods=['POST'])
def analyze_conversation():
    """分析對話並決定是否需要介入"""
    try:
        global manus_service
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '請提供請求數據'
            }), 400
        
        messages = data.get('messages', [])
        repository = data.get('repository', 'unknown')
        conversation_id = data.get('conversation_id', 'unknown')
        
        if not messages:
            return jsonify({
                'success': False,
                'error': '請提供對話消息'
            }), 400
        
        logger.info(f"分析對話: {repository}/{conversation_id}")
        
        # 分析對話內容
        analysis_result = {
            'repository': repository,
            'conversation_id': conversation_id,
            'messages_count': len(messages),
            'intervention_needed': False,
            'confidence': 0.0,
            'priority': 'low',
            'suggestion': '',
            'manus_available': manus_service is not None and manus_service.is_running
        }
        
        # 簡單的介入判斷邏輯
        last_message = messages[-1] if messages else {}
        content = last_message.get('content', '').lower()
        
        # 檢查是否需要介入
        intervention_keywords = [
            'help', 'error', 'problem', 'issue', 'bug', 'fix',
            '幫助', '錯誤', '問題', '修復', '解決'
        ]
        
        intervention_score = sum(1 for keyword in intervention_keywords if keyword in content)
        
        if intervention_score > 0:
            analysis_result['intervention_needed'] = True
            analysis_result['confidence'] = min(0.7 + (intervention_score * 0.1), 1.0)
            analysis_result['priority'] = 'high' if intervention_score >= 2 else 'medium'
            
            # 生成建議
            if manus_service and manus_service.is_running:
                analysis_result['suggestion'] = "🤖 建議使用Manus進行智能分析和回覆"
            else:
                analysis_result['suggestion'] = "💡 建議啟動Manus服務以獲得智能支持"
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'timestamp': '2025-06-22T13:40:00Z'
        }), 200
        
    except Exception as e:
        logger.error(f"分析對話時出錯: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manus_bp.route('/intelligent_intervention', methods=['POST'])
def intelligent_intervention():
    """智能介入功能"""
    try:
        global manus_service
        
        if not manus_service or not manus_service.is_running:
            return jsonify({
                'success': False,
                'error': 'Manus服務未運行，無法進行智能介入'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '請提供請求數據'
            }), 400
        
        messages = data.get('messages', [])
        intervention_type = data.get('intervention_type', 'suggestion')
        context = data.get('context', {})
        
        if not messages:
            return jsonify({
                'success': False,
                'error': '請提供對話消息'
            }), 400
        
        logger.info(f"執行智能介入: {intervention_type}")
        
        # 構建介入消息
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '')
                break
        
        intervention_message = f"🤖 PowerAutomation智能介入\n\n基於對話分析，我來為您提供專業建議：\n\n{last_user_message}"
        
        # 發送介入消息
        result = run_async(manus_service.send_intelligent_response(intervention_message))
        
        # 添加介入信息
        result['intervention_type'] = intervention_type
        result['context'] = context
        result['original_messages'] = messages
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"智能介入時出錯: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manus_bp.route('/status', methods=['GET'])
def get_status():
    """獲取服務狀態"""
    try:
        global manus_service
        
        status = {
            'service_name': 'PowerAutomation Manus Integration',
            'version': '1.0.0',
            'manus_service': {
                'running': manus_service is not None and manus_service.is_running,
                'logged_in': False
            },
            'capabilities': [
                'automatic_login',
                'message_sending',
                'conversation_monitoring',
                'intelligent_intervention',
                'response_analysis'
            ],
            'timestamp': '2025-06-22T13:40:00Z'
        }
        
        if manus_service and manus_service.is_running:
            # 獲取詳細狀態
            conversation_status = run_async(manus_service.get_conversation_status())
            if conversation_status.get('success'):
                status['manus_service']['logged_in'] = conversation_status.get('is_logged_in', False)
                status['manus_service']['page_info'] = conversation_status.get('page_info', {})
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"獲取狀態時出錯: {e}")
        return jsonify({
            'service_name': 'PowerAutomation Manus Integration',
            'error': str(e),
            'status': 'error'
        }), 500

@manus_bp.route('/test', methods=['POST'])
def test_integration():
    """測試集成功能"""
    try:
        global manus_service
        
        data = request.get_json() or {}
        test_message = data.get('message', '🧪 PowerAutomation集成測試')
        
        logger.info("執行集成測試")
        
        test_results = {
            'test_name': 'PowerAutomation Manus Integration Test',
            'timestamp': '2025-06-22T13:40:00Z',
            'results': []
        }
        
        # 測試1: 服務狀態
        test_results['results'].append({
            'test': 'Service Status',
            'passed': manus_service is not None,
            'details': 'Manus service instance exists'
        })
        
        # 測試2: 服務運行狀態
        test_results['results'].append({
            'test': 'Service Running',
            'passed': manus_service is not None and manus_service.is_running,
            'details': 'Manus service is running'
        })
        
        # 測試3: 發送測試消息（如果服務運行中）
        if manus_service and manus_service.is_running:
            try:
                result = run_async(manus_service.send_intelligent_response(test_message))
                test_results['results'].append({
                    'test': 'Send Message',
                    'passed': result.get('success', False),
                    'details': f"Message sent: {test_message[:30]}..."
                })
            except Exception as e:
                test_results['results'].append({
                    'test': 'Send Message',
                    'passed': False,
                    'details': f"Error: {str(e)}"
                })
        else:
            test_results['results'].append({
                'test': 'Send Message',
                'passed': False,
                'details': 'Service not running, skipped'
            })
        
        # 計算總體結果
        passed_tests = sum(1 for result in test_results['results'] if result['passed'])
        total_tests = len(test_results['results'])
        
        test_results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%",
            'overall_status': 'PASS' if passed_tests == total_tests else 'PARTIAL' if passed_tests > 0 else 'FAIL'
        }
        
        return jsonify(test_results), 200
        
    except Exception as e:
        logger.error(f"測試時出錯: {e}")
        return jsonify({
            'test_name': 'PowerAutomation Manus Integration Test',
            'error': str(e),
            'status': 'ERROR'
        }), 500

