import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.powerautomation import powerautomation_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'powerautomation_smartinvention_2025'

# 啟用CORS支持，允許VSCode擴展訪問
CORS(app, origins="*")

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(powerautomation_bp, url_prefix='/api/powerautomation')

# 數據庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'service': 'SmartInvention PowerAutomation Server',
                'version': '1.0.0',
                'status': 'running',
                'message': 'PowerAutomation Flask服務器運行中',
                'api_endpoints': {
                    'health': '/api/powerautomation/health',
                    'status': '/api/powerautomation/status',
                    'start': '/api/powerautomation/start',
                    'stop': '/api/powerautomation/stop',
                    'trae_send': '/api/powerautomation/trae/send',
                    'trae_sync': '/api/powerautomation/trae/sync',
                    'manus_connect': '/api/powerautomation/manus/connect',
                    'manus_tasks': '/api/powerautomation/manus/tasks',
                    'analyze': '/api/powerautomation/analyze',
                    'intervene': '/api/powerautomation/intervene',
                    'repositories': '/api/powerautomation/repositories',
                    'test': '/api/powerautomation/test'
                },
                'features': [
                    'VSCode插件支持',
                    'TRAE集成',
                    'Manus自動化',
                    '智能介入分析',
                    '對話歷史管理',
                    '倉庫感知存儲',
                    'RESTful API'
                ]
            }), 200

@app.route('/api/info')
def api_info():
    """API信息端點"""
    return jsonify({
        'service': 'SmartInvention PowerAutomation Server',
        'version': '1.0.0',
        'description': 'Flask服務器支持VSCode插件和PowerAutomation系統',
        'endpoints': {
            'powerautomation': {
                'base_url': '/api/powerautomation',
                'health': 'GET /api/powerautomation/health',
                'status': 'GET /api/powerautomation/status',
                'start': 'POST /api/powerautomation/start',
                'stop': 'POST /api/powerautomation/stop',
                'trae_send': 'POST /api/powerautomation/trae/send',
                'trae_sync': 'POST /api/powerautomation/trae/sync',
                'manus_connect': 'POST /api/powerautomation/manus/connect',
                'manus_tasks': 'GET /api/powerautomation/manus/tasks',
                'analyze': 'POST /api/powerautomation/analyze',
                'intervene': 'POST /api/powerautomation/intervene',
                'repositories': 'GET /api/powerautomation/repositories',
                'test': 'POST /api/powerautomation/test'
            }
        },
        'cors_enabled': True,
        'database': 'SQLite',
        'host': '0.0.0.0',
        'port': 5000
    })

if __name__ == '__main__':
    print("🚀 SmartInvention PowerAutomation Server 啟動中...")
    print("📋 支持的功能:")
    print("  - VSCode插件API支持")
    print("  - TRAE集成和同步")
    print("  - Manus自動化控制")
    print("  - 智能介入分析")
    print("  - 對話歷史管理")
    print("  - 倉庫感知存儲")
    print("🌐 服務地址: http://0.0.0.0:5000")
    print("📖 API文檔: http://0.0.0.0:5000/api/info")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

