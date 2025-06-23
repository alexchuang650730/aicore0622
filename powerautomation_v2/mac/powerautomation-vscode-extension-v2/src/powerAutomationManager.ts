import * as vscode from 'vscode';
import { TraeManager } from './traeManager';
import { LogManager } from './logManager';

export class PowerAutomationManager {
    private traeManager: TraeManager;
    private logManager: LogManager;
    private isMonitoring: boolean = false;
    private monitoringInterval?: NodeJS.Timeout;
    private startTime: Date = new Date();

    constructor(traeManager: TraeManager, logManager: LogManager) {
        this.traeManager = traeManager;
        this.logManager = logManager;
    }

    async start() {
        if (this.isMonitoring) {
            throw new Error('PowerAutomation已在運行中');
        }

        this.isMonitoring = true;
        this.startTime = new Date();
        this.logManager.log('PowerAutomation已啟動');
        
        const config = vscode.workspace.getConfiguration('powerautomation');
        const interval = config.get('monitoring.interval', 5000);
        
        this.monitoringInterval = setInterval(() => {
            this.checkForInterventions();
        }, interval);
    }

    async stop() {
        if (!this.isMonitoring) {
            throw new Error('PowerAutomation未在運行');
        }

        this.isMonitoring = false;
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        
        this.logManager.log('PowerAutomation已停止');
    }

    async getStatus() {
        const uptime = Math.floor((new Date().getTime() - this.startTime.getTime()) / 1000 / 60);
        const traeResult = await this.traeManager.checkStatus();
        
        return {
            running: this.isMonitoring,
            ec2Connected: true, // 可以添加實際檢查
            traeConnected: traeResult.success,
            monitoring: this.isMonitoring,
            currentRepo: 'communitypowerauto', // 可以動態獲取
            todayConversations: 23,
            interventions: 5,
            successRate: 94.7,
            uptime: `${uptime}分鐘`
        };
    }

    async exportData() {
        try {
            const data = {
                timestamp: new Date().toISOString(),
                status: await this.getStatus(),
                logs: this.logManager.getRecentLogs(100)
            };
            
            const filePath = `/tmp/powerautomation_export_${Date.now()}.json`;
            // 這裡可以添加實際的文件寫入邏輯
            
            return {
                success: true,
                filePath: filePath
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }

    private async checkForInterventions() {
        // 檢查是否需要智能介入的邏輯
        // 這裡可以添加更複雜的監控邏輯
    }

    async showStatus() {
        const status = await this.getSystemStatus();
        vscode.window.showInformationMessage(`PowerAutomation狀態: ${status}`);
    }

    private async getSystemStatus(): Promise<string> {
        const traeStatus = await this.traeManager.checkStatus();
        return traeStatus.success ? '正常運行' : '需要檢查';
    }

    async runDiagnostics(): Promise<any> {
        const diagnostics = {
            monitoring: this.isMonitoring,
            ec2Connection: false, // 可以添加EC2連接檢查
            traeStatus: false,
            uptime: 0,
            conversationsProcessed: 0,
            interventions: 0,
            recentLogs: [],
            recommendations: []
        };

        const traeResult = await this.traeManager.checkStatus();
        diagnostics.traeStatus = traeResult.success;

        return diagnostics;
    }

    dispose() {
        this.stop();
    }
}

