"""
增強版簡化Agent架構配置
Enhanced Simplified Agent Architecture Configuration
支持Smart Tool Engine和Adapter MCP整合
"""

import os
from typing import Dict, Any, List

class EnhancedAgentConfig:
    """增強版Agent配置"""
    
    @staticmethod
    def get_config(environment: str = 'development') -> Dict[str, Any]:
        """
        獲取環境配置
        
        Args:
            environment: 環境名稱 ('development', 'production', 'testing')
            
        Returns:
            配置字典
        """
        base_config = EnhancedAgentConfig._get_base_config()
        env_config = EnhancedAgentConfig._get_environment_config(environment)
        
        # 合併配置
        config = {**base_config, **env_config}
        
        # 環境變量覆蓋
        config = EnhancedAgentConfig._apply_environment_overrides(config)
        
        return config
    
    @staticmethod
    def _get_base_config() -> Dict[str, Any]:
        """基礎配置"""
        return {
            # Agent Core配置
            'agent_core': {
                'name': 'enhanced_simplified_agent',
                'version': '2.0.0',
                'description': '增強版簡化Agent架構',
                'max_concurrent_requests': 10,
                'default_timeout': 30,
                'enable_caching': True,
                'cache_ttl': 300
            },
            
            # 增強功能配置
            'enhanced_features': {
                'enable_smart_routing': True,
                'enable_cost_optimization': True,
                'enable_performance_monitoring': True,
                'enable_adapter_integration': True,
                'intelligent_fallback': True,
                'quality_threshold': 0.8,
                'max_alternatives': 3
            },
            
            # Tool Registry配置
            'tool_registry': {
                'enable_auto_discovery': True,
                'discovery_interval': 60,
                'health_check_interval': 30,
                'max_tools': 100,
                'enable_tool_caching': True
            },
            
            # Smart Tool Engine配置
            'smart_engine': {
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
                },
                'performance_thresholds': {
                    'max_response_time': 5000,
                    'min_success_rate': 0.95,
                    'min_reliability': 0.9
                }
            },
            
            # Adapter MCP配置
            'adapter_mcp': {
                'enable_adapters': True,
                'auto_discover_adapters': True,
                'adapter_timeout': 15,
                'max_adapters': 20,
                'adapters': {
                    'advanced_analysis': {
                        'enabled': True,
                        'url': 'http://localhost:8098',
                        'capabilities': ['深度分析', '量化評估', '專業洞察'],
                        'priority': 'high'
                    },
                    'cloud_search': {
                        'enabled': True,
                        'url': 'http://localhost:8096',
                        'capabilities': ['雲端搜索', '信息檢索', '數據發現'],
                        'priority': 'medium'
                    },
                    'github_integration': {
                        'enabled': True,
                        'url': 'http://localhost:8095',
                        'capabilities': ['代碼管理', 'GitHub操作', '版本控制'],
                        'priority': 'medium'
                    },
                    'smartui': {
                        'enabled': True,
                        'url': 'http://localhost:8099',
                        'capabilities': ['UI分析', '用戶體驗評估', '界面設計'],
                        'priority': 'low'
                    }
                }
            },
            
            # Action Executor配置
            'action_executor': {
                'default_execution_mode': 'parallel',
                'max_parallel_tasks': 5,
                'task_timeout': 60,
                'enable_result_aggregation': True,
                'retry_policy': {
                    'max_retries': 3,
                    'retry_delay': 1,
                    'exponential_backoff': True
                }
            },
            
            # 日誌配置
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'enhanced_agent.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            
            # 監控配置
            'monitoring': {
                'enable_metrics': True,
                'metrics_interval': 60,
                'enable_health_checks': True,
                'health_check_interval': 30,
                'enable_alerts': True,
                'alert_thresholds': {
                    'error_rate': 0.05,
                    'response_time': 10.0,
                    'memory_usage': 0.8
                }
            }
        }
    
    @staticmethod
    def _get_environment_config(environment: str) -> Dict[str, Any]:
        """環境特定配置"""
        configs = {
            'development': {
                'logging': {'level': 'DEBUG'},
                'agent_core': {'max_concurrent_requests': 5},
                'smart_engine': {
                    'enable_cloud_tools': False,  # 開發環境禁用雲端工具
                    'cost_budget': {'monthly_budget': 10.0}
                },
                'monitoring': {'enable_alerts': False}
            },
            
            'testing': {
                'logging': {'level': 'WARNING'},
                'agent_core': {
                    'max_concurrent_requests': 2,
                    'enable_caching': False
                },
                'smart_engine': {
                    'enable_cloud_tools': False,
                    'enable_cost_optimization': False
                },
                'adapter_mcp': {'enable_adapters': False},
                'monitoring': {'enable_metrics': False}
            },
            
            'production': {
                'logging': {'level': 'INFO'},
                'agent_core': {'max_concurrent_requests': 20},
                'smart_engine': {
                    'cost_budget': {'monthly_budget': 1000.0}
                },
                'monitoring': {
                    'enable_alerts': True,
                    'alert_thresholds': {
                        'error_rate': 0.01,
                        'response_time': 5.0
                    }
                }
            }
        }
        
        return configs.get(environment, {})
    
    @staticmethod
    def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """應用環境變量覆蓋"""
        # Agent Core覆蓋
        if os.getenv('AGENT_MAX_CONCURRENT'):
            config['agent_core']['max_concurrent_requests'] = int(os.getenv('AGENT_MAX_CONCURRENT'))
        
        if os.getenv('AGENT_TIMEOUT'):
            config['agent_core']['default_timeout'] = int(os.getenv('AGENT_TIMEOUT'))
        
        # Smart Engine覆蓋
        if os.getenv('SMART_ENGINE_ENABLE_CLOUD'):
            config['smart_engine']['enable_cloud_tools'] = os.getenv('SMART_ENGINE_ENABLE_CLOUD').lower() == 'true'
        
        if os.getenv('SMART_ENGINE_MONTHLY_BUDGET'):
            config['smart_engine']['cost_budget']['monthly_budget'] = float(os.getenv('SMART_ENGINE_MONTHLY_BUDGET'))
        
        # Adapter MCP覆蓋
        if os.getenv('ADAPTER_MCP_ENABLE'):
            config['adapter_mcp']['enable_adapters'] = os.getenv('ADAPTER_MCP_ENABLE').lower() == 'true'
        
        # 日誌覆蓋
        if os.getenv('LOG_LEVEL'):
            config['logging']['level'] = os.getenv('LOG_LEVEL')
        
        return config
    
    @staticmethod
    def get_adapter_configs() -> Dict[str, Dict[str, Any]]:
        """獲取Adapter MCP配置"""
        return {
            'advanced_analysis_mcp': {
                'name': '高級分析MCP',
                'description': '提供深度分析和專業洞察能力',
                'url': 'http://localhost:8098',
                'health_endpoint': '/health',
                'capabilities': [
                    '深度分析', '量化評估', '專業洞察', 
                    '戰略建議', '風險評估', '趨勢分析'
                ],
                'input_types': ['text', 'json', 'structured_data'],
                'output_types': ['analysis_report', 'insights', 'recommendations'],
                'timeout': 30,
                'retry_count': 3,
                'priority': 'high'
            },
            
            'cloud_search_mcp': {
                'name': '雲端搜索MCP',
                'description': '提供雲端搜索和信息檢索能力',
                'url': 'http://localhost:8096',
                'health_endpoint': '/health',
                'capabilities': [
                    '雲端搜索', '信息檢索', '數據發現',
                    '內容聚合', '實時搜索', '多源整合'
                ],
                'input_types': ['search_query', 'filters', 'parameters'],
                'output_types': ['search_results', 'aggregated_data', 'insights'],
                'timeout': 20,
                'retry_count': 2,
                'priority': 'medium'
            },
            
            'github_mcp': {
                'name': 'GitHub整合MCP',
                'description': '提供GitHub操作和代碼管理能力',
                'url': 'http://localhost:8095',
                'health_endpoint': '/health',
                'capabilities': [
                    '代碼管理', 'GitHub操作', '版本控制',
                    'PR管理', 'Issue追蹤', '代碼分析'
                ],
                'input_types': ['github_operation', 'repository_info', 'code_data'],
                'output_types': ['operation_result', 'code_analysis', 'repository_status'],
                'timeout': 25,
                'retry_count': 3,
                'priority': 'medium'
            },
            
            'smartui_mcp': {
                'name': 'SmartUI MCP',
                'description': '提供UI分析和用戶體驗評估能力',
                'url': 'http://localhost:8099',
                'health_endpoint': '/health',
                'capabilities': [
                    'UI分析', '用戶體驗評估', '界面設計建議',
                    '可用性測試', '設計優化', '交互分析'
                ],
                'input_types': ['ui_data', 'design_requirements', 'user_feedback'],
                'output_types': ['ui_analysis', 'design_recommendations', 'ux_insights'],
                'timeout': 15,
                'retry_count': 2,
                'priority': 'low'
            }
        }
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """驗證配置"""
        errors = []
        
        # 驗證必需的配置項
        required_sections = ['agent_core', 'tool_registry', 'action_executor']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required config section: {section}")
        
        # 驗證數值範圍
        if config.get('agent_core', {}).get('max_concurrent_requests', 0) <= 0:
            errors.append("agent_core.max_concurrent_requests must be positive")
        
        if config.get('agent_core', {}).get('default_timeout', 0) <= 0:
            errors.append("agent_core.default_timeout must be positive")
        
        # 驗證Smart Engine配置
        smart_config = config.get('smart_engine', {})
        if smart_config.get('enable_cloud_tools') and not smart_config.get('cost_budget'):
            errors.append("cost_budget required when cloud tools are enabled")
        
        return errors

# 配置工廠函數
def create_enhanced_config(environment: str = None) -> Dict[str, Any]:
    """
    創建增強版配置
    
    Args:
        environment: 環境名稱，如果為None則從環境變量獲取
        
    Returns:
        配置字典
    """
    if environment is None:
        environment = os.getenv('AGENT_ENVIRONMENT', 'development')
    
    config = EnhancedAgentConfig.get_config(environment)
    
    # 驗證配置
    errors = EnhancedAgentConfig.validate_config(config)
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return config

# 默認配置實例
DEFAULT_CONFIG = EnhancedAgentConfig.get_config('development')
PRODUCTION_CONFIG = EnhancedAgentConfig.get_config('production')
TESTING_CONFIG = EnhancedAgentConfig.get_config('testing')

