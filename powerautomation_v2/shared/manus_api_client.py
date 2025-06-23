"""
PowerAutomation Manus API 客戶端
支持與Manus智能引擎系統的完整集成
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisMode(Enum):
    """分析模式枚舉"""
    SMART = "smart"
    DETAILED = "detailed"
    FAST = "fast"

class AnalysisType(Enum):
    """分析類型枚舉"""
    FRONTEND_CODE = "frontend_code"
    UI_DESIGN = "ui_design"
    PERFORMANCE = "performance"
    USER_EXPERIENCE = "user_experience"
    MOBILE_APP = "mobile_app"

class Domain(Enum):
    """領域枚舉"""
    FRONTEND_DEVELOPMENT = "frontend_development"
    UI_DESIGN = "ui_design"
    PERFORMANCE = "performance"
    USER_EXPERIENCE = "user_experience"
    MOBILE_APP = "mobile_app"

@dataclass
class ManusAPIConfig:
    """Manus API配置"""
    local_url: str = "http://localhost:8082"
    public_url: str = "https://8082-i12ds64takr8ehe1j4goh-1ce18e5a.manusvm.computer"
    timeout: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0
    use_public: bool = False

@dataclass
class AnalysisRequest:
    """分析請求數據結構"""
    content: str
    mode: AnalysisMode = AnalysisMode.SMART
    domain: Optional[Domain] = None
    analysis_type: Optional[AnalysisType] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisResponse:
    """分析響應數據結構"""
    success: bool
    analysis_mode: str
    summary: str
    ai_analysis: Dict[str, Any]
    file_metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class ManusAPIClient:
    """Manus API客戶端"""
    
    def __init__(self, config: Optional[ManusAPIConfig] = None):
        """初始化客戶端"""
        self.config = config or ManusAPIConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PowerAutomation-ManusAPI-Client/1.0'
        })
        
    @property
    def base_url(self) -> str:
        """獲取基礎URL"""
        return self.config.public_url if self.config.use_public else self.config.local_url
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """發送HTTP請求，包含重試機制"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.config.retry_count):
            try:
                logger.info(f"發送請求到 {url} (嘗試 {attempt + 1}/{self.config.retry_count})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"請求失敗，狀態碼: {response.status_code}")
                    if attempt < self.config.retry_count - 1:
                        time.sleep(self.config.retry_delay)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"請求異常: {e}")
                if attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise
        
        raise requests.exceptions.RequestException(f"請求失敗，已重試 {self.config.retry_count} 次")
    
    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            response = self._make_request('GET', '/api/health')
            return {
                'success': True,
                'status': 'healthy',
                'response': response.json() if response.content else {}
            }
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """智能分析"""
        try:
            # 構建請求數據
            data = {
                'content': request.content,
                'mode': request.mode.value
            }
            
            # 添加可選參數
            if request.domain:
                data['domain'] = request.domain.value
            if request.analysis_type:
                data['analysis_type'] = request.analysis_type.value
            if request.context:
                data['context'] = request.context
            
            logger.info(f"發送分析請求: mode={request.mode.value}, content_length={len(request.content)}")
            
            response = self._make_request('POST', '/api/analyze', json=data)
            result = response.json()
            
            return AnalysisResponse(
                success=True,
                analysis_mode=result.get('analysis_mode', request.mode.value),
                summary=result.get('summary', ''),
                ai_analysis=result.get('ai_analysis', {}),
                file_metadata=result.get('file_metadata'),
                timestamp=result.get('timestamp')
            )
            
        except Exception as e:
            logger.error(f"分析請求失敗: {e}")
            return AnalysisResponse(
                success=False,
                analysis_mode=request.mode.value,
                summary='',
                ai_analysis={},
                error=str(e)
            )
    
    def analyze_conversation(self, messages: List[Dict[str, str]], 
                           context: Optional[Dict[str, Any]] = None) -> AnalysisResponse:
        """分析對話內容"""
        # 將對話消息轉換為分析內容
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        
        request = AnalysisRequest(
            content=conversation_text,
            mode=AnalysisMode.SMART,
            domain=Domain.FRONTEND_DEVELOPMENT,
            context=context
        )
        
        return self.analyze(request)
    
    def analyze_code(self, code: str, language: str = "javascript", 
                    mode: AnalysisMode = AnalysisMode.SMART) -> AnalysisResponse:
        """分析代碼"""
        content = f"語言: {language}\n代碼:\n{code}"
        
        request = AnalysisRequest(
            content=content,
            mode=mode,
            domain=Domain.FRONTEND_DEVELOPMENT,
            analysis_type=AnalysisType.FRONTEND_CODE
        )
        
        return self.analyze(request)
    
    def analyze_ui_design(self, description: str, 
                         mode: AnalysisMode = AnalysisMode.DETAILED) -> AnalysisResponse:
        """分析UI設計"""
        request = AnalysisRequest(
            content=description,
            mode=mode,
            domain=Domain.UI_DESIGN,
            analysis_type=AnalysisType.UI_DESIGN
        )
        
        return self.analyze(request)
    
    def analyze_performance(self, metrics: Dict[str, Any], 
                          mode: AnalysisMode = AnalysisMode.DETAILED) -> AnalysisResponse:
        """分析性能數據"""
        content = f"性能指標:\n{json.dumps(metrics, indent=2, ensure_ascii=False)}"
        
        request = AnalysisRequest(
            content=content,
            mode=mode,
            domain=Domain.PERFORMANCE,
            analysis_type=AnalysisType.PERFORMANCE
        )
        
        return self.analyze(request)
    
    def upload_file_analyze(self, file_path: str, 
                           mode: AnalysisMode = AnalysisMode.SMART) -> AnalysisResponse:
        """上傳文件進行分析"""
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {'mode': mode.value}
                
                logger.info(f"上傳文件分析: {file_path}")
                
                response = self._make_request(
                    'POST', 
                    '/api/upload',
                    files=files,
                    data=data
                )
                
                result = response.json()
                
                return AnalysisResponse(
                    success=True,
                    analysis_mode=result.get('analysis_mode', mode.value),
                    summary=result.get('summary', ''),
                    ai_analysis=result.get('ai_analysis', {}),
                    file_metadata=result.get('file_metadata'),
                    timestamp=result.get('timestamp')
                )
                
        except Exception as e:
            logger.error(f"文件上傳分析失敗: {e}")
            return AnalysisResponse(
                success=False,
                analysis_mode=mode.value,
                summary='',
                ai_analysis={},
                error=str(e)
            )
    
    def batch_analyze(self, requests: List[AnalysisRequest]) -> List[AnalysisResponse]:
        """批量分析"""
        try:
            # 構建批量請求數據
            batch_data = {
                'requests': [
                    {
                        'content': req.content,
                        'mode': req.mode.value,
                        'domain': req.domain.value if req.domain else None,
                        'analysis_type': req.analysis_type.value if req.analysis_type else None,
                        'context': req.context
                    }
                    for req in requests
                ]
            }
            
            logger.info(f"發送批量分析請求: {len(requests)} 個項目")
            
            response = self._make_request('POST', '/api/batch_analyze', json=batch_data)
            results = response.json()
            
            # 處理批量響應
            responses = []
            for i, result in enumerate(results.get('results', [])):
                responses.append(AnalysisResponse(
                    success=result.get('success', True),
                    analysis_mode=result.get('analysis_mode', requests[i].mode.value),
                    summary=result.get('summary', ''),
                    ai_analysis=result.get('ai_analysis', {}),
                    file_metadata=result.get('file_metadata'),
                    timestamp=result.get('timestamp'),
                    error=result.get('error')
                ))
            
            return responses
            
        except Exception as e:
            logger.error(f"批量分析失敗: {e}")
            # 返回錯誤響應列表
            return [
                AnalysisResponse(
                    success=False,
                    analysis_mode=req.mode.value,
                    summary='',
                    ai_analysis={},
                    error=str(e)
                )
                for req in requests
            ]

class PowerAutomationManusIntegration:
    """PowerAutomation與Manus API的集成類"""
    
    def __init__(self, config: Optional[ManusAPIConfig] = None):
        """初始化集成"""
        self.client = ManusAPIClient(config)
        self.complexity_threshold = 0.7
        
    def should_use_manus_analysis(self, content: str, context: Optional[Dict] = None) -> bool:
        """判斷是否需要使用Manus分析"""
        # 簡單的複雜度評估邏輯
        complexity_indicators = [
            'react', 'vue', 'angular', 'javascript', 'typescript',
            'css', 'html', 'performance', 'optimization', 'ui', 'ux',
            'mobile', 'responsive', 'frontend', 'backend'
        ]
        
        content_lower = content.lower()
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in content_lower)
        complexity_ratio = complexity_score / len(complexity_indicators)
        
        return complexity_ratio >= self.complexity_threshold
    
    def analyze_trae_conversation(self, messages: List[Dict[str, str]], 
                                 repository: str, conversation_id: str) -> Dict[str, Any]:
        """分析TRAE對話並決定是否需要介入"""
        try:
            # 提取對話內容
            conversation_content = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in messages
            ])
            
            # 判斷是否需要Manus分析
            use_manus = self.should_use_manus_analysis(conversation_content)
            
            result = {
                'repository': repository,
                'conversation_id': conversation_id,
                'use_manus_analysis': use_manus,
                'intervention_needed': False,
                'confidence': 0.0,
                'priority': 'low',
                'suggestion': '',
                'manus_analysis': None
            }
            
            if use_manus:
                # 使用Manus API進行深度分析
                context = {
                    'repository': repository,
                    'conversation_id': conversation_id,
                    'analysis_purpose': 'intervention_check'
                }
                
                manus_response = self.client.analyze_conversation(messages, context)
                result['manus_analysis'] = {
                    'success': manus_response.success,
                    'summary': manus_response.summary,
                    'ai_analysis': manus_response.ai_analysis,
                    'error': manus_response.error
                }
                
                if manus_response.success:
                    # 基於Manus分析結果決定介入策略
                    ai_content = manus_response.ai_analysis.get('content', '')
                    
                    # 簡單的介入判斷邏輯（可以根據實際需求優化）
                    intervention_keywords = [
                        '需要改進', '建議', '優化', '問題', '錯誤', 
                        'improvement', 'suggestion', 'optimize', 'issue', 'error'
                    ]
                    
                    intervention_score = sum(1 for keyword in intervention_keywords 
                                           if keyword.lower() in ai_content.lower())
                    
                    if intervention_score > 0:
                        result['intervention_needed'] = True
                        result['confidence'] = min(0.8 + (intervention_score * 0.1), 1.0)
                        result['priority'] = 'high' if intervention_score >= 3 else 'medium'
                        result['suggestion'] = self._generate_intervention_suggestion(
                            manus_response.ai_analysis
                        )
            else:
                # 使用本地簡單分析
                result['suggestion'] = self._generate_simple_suggestion(conversation_content)
            
            return result
            
        except Exception as e:
            logger.error(f"對話分析失敗: {e}")
            return {
                'repository': repository,
                'conversation_id': conversation_id,
                'use_manus_analysis': False,
                'intervention_needed': False,
                'confidence': 0.0,
                'priority': 'low',
                'suggestion': '',
                'error': str(e)
            }
    
    def _generate_intervention_suggestion(self, ai_analysis: Dict[str, Any]) -> str:
        """基於Manus分析生成介入建議"""
        content = ai_analysis.get('content', '')
        models_used = ai_analysis.get('models_used', [])
        
        suggestion = f"🤖 基於 {', '.join(models_used)} 模型的智能分析建議：\n\n"
        
        # 提取關鍵建議（簡化版本）
        if 'react' in content.lower():
            suggestion += "📱 React開發建議：\n"
            suggestion += "- 使用函數組件和Hooks\n"
            suggestion += "- 實現適當的狀態管理\n"
            suggestion += "- 注意性能優化\n\n"
        
        if 'performance' in content.lower():
            suggestion += "⚡ 性能優化建議：\n"
            suggestion += "- 優化資源載入\n"
            suggestion += "- 實現代碼分割\n"
            suggestion += "- 使用緩存策略\n\n"
        
        if 'ui' in content.lower() or 'design' in content.lower():
            suggestion += "🎨 UI/UX設計建議：\n"
            suggestion += "- 保持設計一致性\n"
            suggestion += "- 優化用戶體驗\n"
            suggestion += "- 確保響應式設計\n\n"
        
        suggestion += f"💡 詳細分析：\n{content[:500]}..."
        
        return suggestion
    
    def _generate_simple_suggestion(self, content: str) -> str:
        """生成簡單的本地建議"""
        if 'game' in content.lower() or '遊戲' in content:
            return "🎮 遊戲開發建議：建議使用HTML5 Canvas或現代遊戲框架進行開發。"
        
        if 'python' in content.lower():
            return "🐍 Python學習建議：建議從基礎語法開始，逐步學習數據結構和算法。"
        
        if 'web' in content.lower() or '網站' in content:
            return "🌐 Web開發建議：建議使用現代前端框架如React或Vue.js進行開發。"
        
        return "💡 建議：請提供更多具體信息，以便提供更準確的建議。"

# 使用示例
if __name__ == "__main__":
    # 創建配置
    config = ManusAPIConfig(use_public=False)  # 使用本地API
    
    # 創建集成實例
    integration = PowerAutomationManusIntegration(config)
    
    # 測試健康檢查
    health = integration.client.health_check()
    print(f"健康檢查: {health}")
    
    # 測試對話分析
    test_messages = [
        {"role": "user", "content": "我想要開發一個React應用"},
        {"role": "trae", "content": "我可以幫您創建一個React應用的基礎結構"}
    ]
    
    result = integration.analyze_trae_conversation(
        messages=test_messages,
        repository="communitypowerauto",
        conversation_id="conv_test_001"
    )
    
    print(f"對話分析結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

