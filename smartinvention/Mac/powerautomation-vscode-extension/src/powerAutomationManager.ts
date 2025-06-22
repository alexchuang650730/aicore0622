import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class PowerAutomationManager implements vscode.Disposable {
    private _onStatusChange = new vscode.EventEmitter<any>();
    public readonly onStatusChange = this._onStatusChange.event;
    
    private isMonitoring = false;
    private monitoringTimer?: NodeJS.Timer;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    async startMonitoring(): Promise<void> {
        if (this.isMonitoring) {
            return;
        }

        this.isMonitoring = true;
        const config = vscode.workspace.getConfiguration('powerautomation');
        const interval = config.get<number>('monitoring.interval', 30) * 1000;

        this.monitoringTimer = setInterval(() => {
            this.performMonitoringCycle();
        }, interval);

        this._onStatusChange.fire({ isMonitoring: true });
    }

    stopMonitoring(): void {
        if (this.monitoringTimer) {
            clearInterval(this.monitoringTimer);
            this.monitoringTimer = undefined;
        }
        this.isMonitoring = false;
        this._onStatusChange.fire({ isMonitoring: false });
    }

    private async performMonitoringCycle(): Promise<void> {
        try {
            // 監控TRAE狀態
            const traeStatus = await this.checkTraeStatus();
            
            // 檢查是否需要同步
            if (traeStatus.hasNewData) {
                await this.autoSyncToEC2();
            }

            // 智能介入檢查
            await this.checkIntelligentIntervention();

        } catch (error) {
            console.error('監控週期錯誤:', error);
            this._onStatusChange.fire({ hasError: true, error });
        }
    }

    private async checkTraeStatus(): Promise<any> {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const dbPath = config.get<string>('trae.dbPath');
        
        if (!dbPath || !fs.existsSync(dbPath)) {
            return { isRunning: false, dbExists: false };
        }

        const stats = fs.statSync(dbPath);
        return {
            isRunning: true,
            dbExists: true,
            lastUpdate: stats.mtime,
            hasNewData: Date.now() - stats.mtime.getTime() < 60000 // 1分鐘內有更新
        };
    }

    async syncToEC2(progress?: vscode.Progress<any>): Promise<void> {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const ec2Host = config.get<string>('ec2.host');
        const ec2User = config.get<string>('ec2.user');

        if (progress) {
            progress.report({ increment: 30, message: "提取TRAE數據..." });
        }

        // 模擬數據提取和同步
        await new Promise(resolve => setTimeout(resolve, 1000));

        if (progress) {
            progress.report({ increment: 60, message: "上傳到EC2..." });
        }

        await new Promise(resolve => setTimeout(resolve, 1000));

        if (progress) {
            progress.report({ increment: 100, message: "同步完成" });
        }
    }

    private async autoSyncToEC2(): Promise<void> {
        const config = vscode.workspace.getConfiguration('powerautomation');
        if (config.get<boolean>('automation.autoSync')) {
            await this.syncToEC2();
        }
    }

    async extractConversationHistory(): Promise<any[]> {
        // 模擬對話歷史提取
        return [
            {
                id: 1,
                timestamp: new Date().toISOString(),
                user: "用戶",
                message: "如何使用PowerAutomation？",
                type: "user"
            },
            {
                id: 2,
                timestamp: new Date().toISOString(),
                user: "AI",
                message: "PowerAutomation是一個智能自動化助手...",
                type: "assistant"
            }
        ];
    }

    async sendIntelligentMessage(message: string): Promise<void> {
        // 模擬智能消息發送
        console.log(`發送智能消息: ${message}`);
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    async enableIntelligentIntervention(): Promise<void> {
        const config = vscode.workspace.getConfiguration('powerautomation');
        await config.update('automation.intelligentIntervention', true, vscode.ConfigurationTarget.Global);
    }

    disableIntelligentIntervention(): void {
        const config = vscode.workspace.getConfiguration('powerautomation');
        config.update('automation.intelligentIntervention', false, vscode.ConfigurationTarget.Global);
    }

    private async checkIntelligentIntervention(): Promise<void> {
        const config = vscode.workspace.getConfiguration('powerautomation');
        if (!config.get<boolean>('automation.intelligentIntervention')) {
            return;
        }

        // 智能介入邏輯
        console.log('執行智能介入檢查...');
    }

    async getSystemStatus(): Promise<any> {
        const traeStatus = await this.checkTraeStatus();
        
        return {
            trae: traeStatus,
            ec2: {
                connected: true, // 模擬狀態
                lastSync: new Date().toISOString()
            },
            manus: {
                connected: true,
                conversationCount: 5
            },
            intervention: {
                enabled: vscode.workspace.getConfiguration('powerautomation').get('automation.intelligentIntervention'),
                interventionCount: 3
            }
        };
    }

    updateConfiguration(): void {
        console.log('配置已更新');
        if (this.isMonitoring) {
            this.stopMonitoring();
            this.startMonitoring();
        }
    }

    showLogs(): void {
        vscode.window.showInformationMessage('日誌功能開發中...');
    }

    dispose(): void {
        this.stopMonitoring();
        this._onStatusChange.dispose();
    }
}

