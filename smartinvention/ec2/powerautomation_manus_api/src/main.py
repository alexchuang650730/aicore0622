import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.manus import manus_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'powerautomation_manus_secret_key_2025'

# 啟用CORS支持
CORS(app, origins="*")

# 註冊藍圖
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(manus_bp, url_prefix='/api/manus')

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
            return "PowerAutomation Manus API Server - Ready", 200

@app.route('/api/status')
def api_status():
    """API狀態檢查"""
    return {
        'service': 'PowerAutomation Manus API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'manus': '/api/manus/',
            'health': '/api/manus/health',
            'start': '/api/manus/start',
            'stop': '/api/manus/stop',
            'send_message': '/api/manus/send_message',
            'get_conversation': '/api/manus/get_conversation',
            'analyze_conversation': '/api/manus/analyze_conversation',
            'intelligent_intervention': '/api/manus/intelligent_intervention',
            'test': '/api/manus/test'
        },
        'features': [
            'Manus自動登錄',
            '任務列表遍歷',
            '文件分類下載',
            '對話歷史獲取',
            '智能介入分析',
            '批量文件處理'
        ]
    }

if __name__ == '__main__':
    print("🚀 PowerAutomation Manus API Server 啟動中...")
    print("📋 支持的功能:")
    print("  - Manus自動登錄和操作")
    print("  - 任務列表遍歷")
    print("  - 文件分類和批量下載")
    print("  - 對話歷史完整獲取")
    print("  - 智能介入分析")
    print("🌐 服務地址: http://0.0.0.0:5000")
    print("📖 API文檔: http://0.0.0.0:5000/api/status")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

