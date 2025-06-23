# -*- coding: utf-8 -*-
"""
增強版Tool Registry - 整合Smart Tool Engine
Enhanced Tool Registry with Smart Tool Engine Integration
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json

# 導入原有的Tool Registry
from .tool_registry import ToolRegistry, ToolInfo, ToolType, ToolCapability

# 導入Smart Tool Engine組件
from .smart_tool_engine_mcp import (
    UnifiedToolRegistry,
    IntelligentRoutingEngine,
    MCPUnifiedExecutionEngine,
    SmartToolEngineMCP
)

logger = logging.getLogger(__name__)

class EnhancedToolType(Enum):
    """增強的工具類型"""
    # 原有類型
    MCP_SERVICE = "mcp_service"
    HTTP_API = "http_api"
    PYTHON_MODULE = "python_module"
    SHELL_COMMAND = "shell_command"
    
    # Smart Engine新增類型
    ACI_DEV_TOOL = "aci_dev_tool"
    MCP_SO_TOOL = "mcp_so_tool"
    ZAPIER_TOOL = "zapier_tool"
    UNIFIED_SMART_TOOL = "unified_smart_tool"

class SmartToolInfo(ToolInfo):
    """增強的工具信息"""
    
    def __init__(self, id: str, name: str, type: EnhancedToolType, description: str, 
                 version: str = "1.0.0", capabilities: List[ToolCapability] = None,
                 platform: str = None, performance_metrics: Dict = None, 
                 cost_model: Dict = None, quality_scores: Dict = None):
        super().__init__(id, name, type, description, version, capabilities)
        
        # Smart Engine擴展屬性
        self.platform = platform or "local"
        self.performance_metrics = performance_metrics or {
            "avg_response_time": 1000,
            "success_rate": 0.95,
            "throughput": 100,
            "reliability_score": 0.9
        }
        self.cost_model = cost_model or {
            "type": "free",
            "cost_per_call": 0.0,
            "monthly_limit": -1,
            "currency": "USD"
        }
        self.quality_scores = quality_scores or {
            "user_rating": 4.0,
            "documentation_quality": 0.8,
            "community_support": 0.7,
            "update_frequency": 0.8
        }

class EnhancedToolRegistry(ToolRegistry):
    """
    增強版Tool Registry
    整合Smart Tool Engine的智能工具發現和選擇能力
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 初始化Smart Tool Engine組件
        self.smart_engine = SmartToolEngineMCP()
        self.unified_registry = self.smart_engine.registry
        self.routing_engine = self.smart_engine.execution_engine.routing_engine
        
        # 增強配置
        self.smart_config = config.get('smart_engine', {
            'enable_cloud_tools': True,
            'enable_intelligent_routing': True,
            'enable_cost_optimization': True,
            'enable_performance_monitoring': True,
            'max_cloud_tools': 100,
            'default_timeout': 30,
            'cost_budget': {
                'max_cost_per_call': 0.01,
                'monthly_budget': 100.0,
                'currency': 'USD'
            }
        })
        
        # 統計信息
        self.enhanced_stats = {
            'smart_tools_discovered': 0,
            'intelligent_selections': 0,
            'cost_optimizations': 0,
            'performance_improvements': 0
        }
        
        logger.info("Enhanced Tool Registry initialized with Smart Tool Engine")
    
    async def initialize(self):
        """初始化增強版Tool Registry"""
        # 調用父類初始化
        await super().initialize()
        
        # 初始化Smart Tool Engine
        await self._initialize_smart_engine()
        
        # 同步工具到統一註冊表
        await self._sync_tools_to_unified_registry()
        
        logger.info("Enhanced Tool Registry initialization completed")
    
    async def _initialize_smart_engine(self):
        """初始化Smart Tool Engine"""
        try:
            # Smart Engine已經在構造函數中初始化了示例工具
            # 這裡可以添加額外的初始化邏輯
            
            # 獲取Smart Engine中的工具數量
            smart_tools = await self._discover_smart_tools()
            self.enhanced_stats['smart_tools_discovered'] = len(smart_tools)
            
            logger.info(f"Smart Tool Engine initialized with {len(smart_tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize Smart Tool Engine: {e}")
    
    async def _sync_tools_to_unified_registry(self):
        """同步本地工具到統一註冊表"""
        try:
            for tool_id, tool_info in self.tools.items():
                # 將本地工具轉換為Smart Tool格式
                smart_tool_info = self._convert_to_smart_tool(tool_info)
                
                # 註冊到統一註冊表
                unified_tool_id = self.unified_registry.register_tool(smart_tool_info)
                
                logger.debug(f"Synced tool {tool_id} to unified registry as {unified_tool_id}")
                
        except Exception as e:
            logger.error(f"Failed to sync tools to unified registry: {e}")
    
    def _convert_to_smart_tool(self, tool_info: ToolInfo) -> Dict:
        """將本地工具信息轉換為Smart Tool格式"""
        return {
            "name": tool_info.name,
            "description": tool_info.description,
            "category": "local_tool",
            "platform": "local",
            "platform_tool_id": tool_info.id,
            "mcp_endpoint": f"local://{tool_info.id}",
            "capabilities": [cap.name for cap in tool_info.capabilities],
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {"type": "object", "properties": {}},
            "version": tool_info.version,
            "avg_response_time": 500,
            "success_rate": 0.95,
            "cost_type": "free",
            "cost_per_call": 0.0,
            "user_rating": 4.0
        }
    
    async def find_optimal_tools(self, requirement: str, context: Dict = None) -> Dict:
        """
        使用智能引擎找到最優工具
        
        Args:
            requirement: 需求描述
            context: 上下文信息
            
        Returns:
            包含最優工具和備選方案的字典
        """
        try:
            context = context or {}
            
            # 添加預算約束
            if 'budget' not in context:
                context['budget'] = self.smart_config['cost_budget']
            
            # 使用智能路由引擎選擇最優工具
            routing_result = self.routing_engine.select_optimal_tool(requirement, context)
            
            if routing_result['success']:
                self.enhanced_stats['intelligent_selections'] += 1
                
                # 如果選擇了成本更低的工具，記錄成本優化
                selected_tool = routing_result['selected_tool']
                if selected_tool['cost_model']['type'] == 'free':
                    self.enhanced_stats['cost_optimizations'] += 1
                
                # 如果選擇了高性能工具，記錄性能改進
                if selected_tool['performance_metrics']['success_rate'] > 0.95:
                    self.enhanced_stats['performance_improvements'] += 1
            
            return routing_result
            
        except Exception as e:
            logger.error(f"Failed to find optimal tools: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': await self._fallback_tool_selection(requirement)
            }
    
    async def _fallback_tool_selection(self, requirement: str) -> List[str]:
        """回退的工具選擇邏輯"""
        # 使用原有的工具發現邏輯作為回退
        return await super().find_tools_by_capability(requirement)
    
    async def discover_cloud_tools(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        發現雲端工具
        
        Args:
            query: 搜索查詢
            filters: 過濾條件
            
        Returns:
            匹配的雲端工具列表
        """
        try:
            if not self.smart_config['enable_cloud_tools']:
                return []
            
            # 使用Smart Engine的工具發現
            result = self.smart_engine.process({
                "action": "discover_tools",
                "parameters": {
                    "query": query,
                    "filters": filters or {},
                    "limit": self.smart_config['max_cloud_tools']
                }
            })
            
            if result['success']:
                return result['tools']
            else:
                logger.warning(f"Cloud tool discovery failed: {result.get('error')}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to discover cloud tools: {e}")
            return []
    
    async def _discover_smart_tools(self) -> List[Dict]:
        """發現Smart Engine中的所有工具"""
        try:
            # 獲取所有可用工具
            result = self.smart_engine.process({
                "action": "discover_tools",
                "parameters": {
                    "query": "",  # 空查詢返回所有工具
                    "limit": 1000
                }
            })
            
            if result['success']:
                return result['tools']
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to discover smart tools: {e}")
            return []
    
    async def register_smart_tool(self, tool_info: Dict) -> str:
        """
        註冊智能工具
        
        Args:
            tool_info: 工具信息字典
            
        Returns:
            工具ID
        """
        try:
            # 使用Smart Engine註冊工具
            result = self.smart_engine.process({
                "action": "register_tool",
                "parameters": {
                    "tool_info": tool_info
                }
            })
            
            if result['success']:
                tool_id = result['tool_id']
                
                # 同時註冊到本地註冊表
                smart_tool_info = SmartToolInfo(
                    id=tool_id,
                    name=tool_info['name'],
                    type=EnhancedToolType.UNIFIED_SMART_TOOL,
                    description=tool_info['description'],
                    platform=tool_info.get('platform', 'unknown'),
                    performance_metrics=tool_info.get('performance_metrics'),
                    cost_model=tool_info.get('cost_model'),
                    quality_scores=tool_info.get('quality_scores')
                )
                
                await super().register_tool(smart_tool_info)
                
                logger.info(f"Smart tool registered: {tool_id}")
                return tool_id
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Failed to register smart tool: {e}")
            raise
    
    async def execute_with_smart_tool(self, tool_id: str, request: str, context: Dict = None) -> Dict:
        """
        使用智能工具執行請求
        
        Args:
            tool_id: 工具ID
            request: 請求內容
            context: 上下文
            
        Returns:
            執行結果
        """
        try:
            # 使用Smart Engine執行
            result = self.smart_engine.process({
                "action": "execute_request",
                "parameters": {
                    "request": request,
                    "context": context or {},
                    "preferred_tool": tool_id
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute with smart tool {tool_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """獲取增強統計信息"""
        base_stats = super().get_registry_stats()
        
        # 獲取Smart Engine統計
        smart_stats = self.smart_engine.process({
            "action": "get_statistics"
        })
        
        return {
            **base_stats,
            'enhanced_features': self.enhanced_stats,
            'smart_engine_stats': smart_stats.get('statistics', {}),
            'cloud_tools_enabled': self.smart_config['enable_cloud_tools'],
            'intelligent_routing_enabled': self.smart_config['enable_intelligent_routing']
        }
    
    async def health_check_enhanced(self) -> Dict[str, Any]:
        """增強的健康檢查"""
        # 基礎健康檢查
        base_health = await super().health_check_all()
        
        # Smart Engine健康檢查
        smart_health = self.smart_engine.process({
            "action": "health_check"
        })
        
        return {
            'base_registry': base_health,
            'smart_engine': smart_health,
            'overall_health': base_health and smart_health.get('success', False),
            'timestamp': time.time()
        }
    
    async def optimize_tool_selection(self, requirement: str, constraints: Dict = None) -> Dict:
        """
        優化工具選擇
        
        Args:
            requirement: 需求描述
            constraints: 約束條件（成本、性能等）
            
        Returns:
            優化後的工具選擇結果
        """
        try:
            # 準備上下文
            context = {
                'optimization_mode': True,
                'constraints': constraints or {},
                'budget': self.smart_config['cost_budget']
            }
            
            # 如果有約束條件，添加到過濾器中
            if constraints:
                context['filters'] = {
                    'max_cost': constraints.get('max_cost', self.smart_config['cost_budget']['max_cost_per_call']),
                    'min_success_rate': constraints.get('min_success_rate', 0.9),
                    'max_response_time': constraints.get('max_response_time', 5000)
                }
            
            # 使用智能路由進行優化選擇
            result = await self.find_optimal_tools(requirement, context)
            
            if result['success']:
                # 添加優化建議
                result['optimization_suggestions'] = self._generate_optimization_suggestions(
                    result['selected_tool'], 
                    result.get('alternatives', [])
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize tool selection: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_optimization_suggestions(self, selected_tool: Dict, alternatives: List[Dict]) -> List[str]:
        """生成優化建議"""
        suggestions = []
        
        # 成本優化建議
        if selected_tool['cost_model']['type'] != 'free':
            free_alternatives = [alt for alt in alternatives if alt['cost_model']['type'] == 'free']
            if free_alternatives:
                suggestions.append(f"考慮使用免費替代工具: {free_alternatives[0]['name']}")
        
        # 性能優化建議
        if selected_tool['performance_metrics']['avg_response_time'] > 1000:
            fast_alternatives = [alt for alt in alternatives 
                               if alt['performance_metrics']['avg_response_time'] < 1000]
            if fast_alternatives:
                suggestions.append(f"考慮使用更快的工具: {fast_alternatives[0]['name']}")
        
        # 質量優化建議
        if selected_tool['quality_scores']['user_rating'] < 4.0:
            high_quality_alternatives = [alt for alt in alternatives 
                                       if alt['quality_scores']['user_rating'] >= 4.0]
            if high_quality_alternatives:
                suggestions.append(f"考慮使用高評分工具: {high_quality_alternatives[0]['name']}")
        
        return suggestions

# 工廠函數
async def create_enhanced_tool_registry(config: Dict[str, Any]) -> EnhancedToolRegistry:
    """
    創建增強版Tool Registry實例
    
    Args:
        config: 配置字典
        
    Returns:
        初始化完成的EnhancedToolRegistry實例
    """
    registry = EnhancedToolRegistry(config)
    await registry.initialize()
    return registry

# 兼容性別名
SmartToolRegistry = EnhancedToolRegistry

