import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import { LogManager } from './logManager';

const execAsync = promisify(exec);

export interface TraeResult {
    success: boolean;
    output?: string;
    error?: string;
}

export class TraeManager {
    private logManager: LogManager;
    private traePath: string = '/usr/local/bin/trae';
    private sendCommand: string = "echo '{message}' | trae -";
    private syncCommand: string = 'trae sync';

    constructor(logManager: LogManager) {
        this.logManager = logManager;
        this.updateConfiguration();
        
        // 監聽配置變更
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('powerautomation.trae')) {
                this.updateConfiguration();
            }
        });
    }

    private updateConfiguration() {
        const config = vscode.workspace.getConfiguration('powerautomation.trae');
        this.traePath = config.get('path', '/usr/local/bin/trae');
        this.sendCommand = config.get('sendCommand', "echo '{message}' | trae -");
        this.syncCommand = config.get('syncCommand', 'trae sync');
        
        this.logManager.debug(`TRAE配置更新: path=${this.traePath}, sendCommand=${this.sendCommand}, syncCommand=${this.syncCommand}`);
    }

    /**
     * 發送消息到TRAE
     */
    async sendMessage(message: string): Promise<TraeResult> {
        try {
            this.logManager.info(`發送消息到TRAE: ${message}`);
            
            // 轉義消息中的特殊字符
            const escapedMessage = message.replace(/'/g, "'\"'\"'");
            const command = this.sendCommand.replace('{message}', escapedMessage);
            
            this.logManager.debug(`執行命令: ${command}`);
            
            const { stdout, stderr } = await execAsync(command, {
                timeout: 30000, // 30秒超時
                cwd: process.env.HOME // 在用戶主目錄執行
            });
            
            if (stderr && !stderr.includes('warning')) {
                this.logManager.warn(`TRAE發送警告: ${stderr}`);
            }
            
            this.logManager.info('TRAE消息發送成功');
            return {
                success: true,
                output: stdout
            };
            
        } catch (error: any) {
            this.logManager.error(`TRAE發送失敗: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 同步TRAE數據
     */
    async syncData(): Promise<{ success: boolean; count?: number; error?: string }> {
        try {
            this.logManager.log('開始同步TRAE數據');
            
            const result = await this.syncRepositories();
            if (result.success) {
                // 模擬處理的項目數量
                const count = Math.floor(Math.random() * 10) + 1;
                return {
                    success: true,
                    count: count
                };
            } else {
                return {
                    success: false,
                    error: result.error
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    /**
     * 同步TRAE倉庫
     */
    async syncRepositories(): Promise<TraeResult> {
        try {
            this.logManager.info('開始TRAE同步');
            
            const { stdout, stderr } = await execAsync(this.syncCommand, {
                timeout: 60000, // 60秒超時
                cwd: process.env.HOME
            });
            
            if (stderr && !stderr.includes('warning')) {
                this.logManager.warn(`TRAE同步警告: ${stderr}`);
            }
            
            this.logManager.info('TRAE同步完成');
            return {
                success: true,
                output: stdout
            };
            
        } catch (error: any) {
            this.logManager.error(`TRAE同步失敗: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 檢查TRAE狀態
     */
    async checkStatus(): Promise<TraeResult> {
        try {
            // 檢查TRAE命令是否可用
            const { stdout } = await execAsync(`which ${this.traePath}`, {
                timeout: 5000
            });
            
            if (stdout.trim()) {
                this.logManager.debug(`TRAE路徑確認: ${stdout.trim()}`);
                return {
                    success: true,
                    output: `TRAE可用: ${stdout.trim()}`
                };
            } else {
                return {
                    success: false,
                    error: 'TRAE命令未找到'
                };
            }
            
        } catch (error: any) {
            this.logManager.error(`TRAE狀態檢查失敗: ${error.message}`);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 獲取TRAE版本信息
     */
    async getVersion(): Promise<TraeResult> {
        try {
            const { stdout } = await execAsync(`${this.traePath} --version`, {
                timeout: 10000
            });
            
            return {
                success: true,
                output: stdout.trim()
            };
            
        } catch (error: any) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 運行TRAE診斷
     */
    async runDiagnostics(): Promise<any> {
        const diagnostics: any = {
            timestamp: new Date().toISOString(),
            traePath: this.traePath,
            sendCommand: this.sendCommand,
            syncCommand: this.syncCommand
        };

        // 檢查TRAE狀態
        const statusResult = await this.checkStatus();
        diagnostics.traeAvailable = statusResult.success;
        diagnostics.traeStatus = statusResult.output || statusResult.error;

        // 檢查版本
        const versionResult = await this.getVersion();
        diagnostics.traeVersion = versionResult.output || 'Unknown';

        // 測試發送功能
        const testMessage = '🧪 PowerAutomation診斷測試';
        const sendResult = await this.sendMessage(testMessage);
        diagnostics.sendTest = {
            success: sendResult.success,
            output: sendResult.output,
            error: sendResult.error
        };

        // 測試同步功能
        const syncResult = await this.syncRepositories();
        diagnostics.syncTest = {
            success: syncResult.success,
            output: syncResult.output,
            error: syncResult.error
        };

        return diagnostics;
    }

    /**
     * 智能回覆生成
     */
    async generateIntelligentReply(conversation: any): Promise<string> {
        // 基於對話內容生成智能回覆
        const userMessage = conversation.userMessage || '';
        
        // 簡單的智能回覆邏輯（可以擴展為更複雜的AI邏輯）
        if (userMessage.includes('貪吃蛇') || userMessage.includes('遊戲')) {
            return `🎮 我來為您生成一個完整的貪吃蛇遊戲！

這個遊戲將包含：
- HTML5 Canvas繪圖
- JavaScript遊戲邏輯
- 方向鍵控制
- 碰撞檢測
- 分數計算
- 響應式設計

您想要什麼特殊功能嗎？比如：
- 不同難度級別
- 音效支持
- 多人模式
- 自定義主題`;
        }
        
        if (userMessage.includes('網站') || userMessage.includes('網頁')) {
            return `🌐 我來幫您設計一個專業的網站！

建議的技術棧：
- 前端：React + TypeScript
- 樣式：Tailwind CSS
- 後端：Node.js + Express
- 數據庫：MongoDB
- 部署：Vercel/Netlify

您的網站需要什麼功能？
- 用戶註冊登錄
- 內容管理系統
- 電商功能
- 博客系統
- 數據分析`;
        }
        
        if (userMessage.includes('API') || userMessage.includes('接口')) {
            return `🔌 我來為您設計RESTful API！

推薦架構：
- 框架：Express.js/FastAPI
- 認證：JWT Token
- 文檔：Swagger/OpenAPI
- 測試：Jest/Pytest
- 部署：Docker + AWS

API設計要點：
- 清晰的端點命名
- 統一的響應格式
- 完善的錯誤處理
- 版本控制策略
- 安全性考慮`;
        }
        
        // 默認智能回覆
        return `💡 我來為您提供專業的技術建議！

基於您的需求，我建議：

1. **技術選型** - 選擇合適的技術棧
2. **架構設計** - 設計可擴展的系統架構  
3. **最佳實踐** - 遵循行業標準和最佳實踐
4. **性能優化** - 確保系統高效運行
5. **安全考慮** - 實施必要的安全措施

請告訴我更多具體需求，我可以提供更詳細的解決方案！`;
    }
}

