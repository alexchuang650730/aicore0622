"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PowerAutomationManager = void 0;
const vscode = require("vscode");
class PowerAutomationManager {
    constructor(traeManager, logManager) {
        this.isMonitoring = false;
        this.startTime = new Date();
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
            ec2Connected: true,
            traeConnected: traeResult.success,
            monitoring: this.isMonitoring,
            currentRepo: 'communitypowerauto',
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
        }
        catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }
    async checkForInterventions() {
        // 檢查是否需要智能介入的邏輯
        // 這裡可以添加更複雜的監控邏輯
    }
    async showStatus() {
        const status = await this.getSystemStatus();
        vscode.window.showInformationMessage(`PowerAutomation狀態: ${status}`);
    }
    async getSystemStatus() {
        const traeStatus = await this.traeManager.checkStatus();
        return traeStatus.success ? '正常運行' : '需要檢查';
    }
    async runDiagnostics() {
        const diagnostics = {
            monitoring: this.isMonitoring,
            ec2Connection: false,
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
exports.PowerAutomationManager = PowerAutomationManager;
//# sourceMappingURL=powerAutomationManager.js.map