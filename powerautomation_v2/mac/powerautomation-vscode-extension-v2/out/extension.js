"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const powerAutomationManager_1 = require("./powerAutomationManager");
const traeManager_1 = require("./traeManager");
const statusBarManager_1 = require("./statusBarManager");
const logManager_1 = require("./logManager");
let powerAutomationManager;
let traeManager;
let statusBarManager;
let logManager;
function activate(context) {
    console.log('PowerAutomation擴展正在啟動...');
    // 初始化管理器
    logManager = new logManager_1.LogManager(context);
    statusBarManager = new statusBarManager_1.StatusBarManager();
    traeManager = new traeManager_1.TraeManager(logManager);
    powerAutomationManager = new powerAutomationManager_1.PowerAutomationManager(traeManager, logManager);
    // 註冊命令
    registerCommands(context);
    // 創建側邊欄視圖
    createSidebarView(context);
    // 自動啟動（如果配置啟用）
    const config = vscode.workspace.getConfiguration('powerautomation');
    if (config.get('monitoring.enabled', true)) {
        powerAutomationManager.start();
        statusBarManager.updateStatus('運行中', '$(play)');
    }
    // 自動打開儀表板（如果配置啟用）
    if (config.get('dashboard.autoOpen', false)) {
        openDashboard();
    }
    logManager.log('PowerAutomation擴展已啟動');
    vscode.window.showInformationMessage('🤖 PowerAutomation已啟動！智能介入系統正在運行。');
}
exports.activate = activate;
function registerCommands(context) {
    // 啟動PowerAutomation
    const startCommand = vscode.commands.registerCommand('powerautomation.start', async () => {
        try {
            await powerAutomationManager.start();
            statusBarManager.updateStatus('運行中', '$(play)');
            vscode.window.showInformationMessage('✅ PowerAutomation已啟動');
            logManager.log('PowerAutomation已啟動');
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 啟動失敗: ${error}`);
            logManager.log(`啟動失敗: ${error}`, 'error');
        }
    });
    // 停止PowerAutomation
    const stopCommand = vscode.commands.registerCommand('powerautomation.stop', async () => {
        try {
            await powerAutomationManager.stop();
            statusBarManager.updateStatus('已停止', '$(stop)');
            vscode.window.showInformationMessage('⏹️ PowerAutomation已停止');
            logManager.log('PowerAutomation已停止');
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 停止失敗: ${error}`);
            logManager.log(`停止失敗: ${error}`, 'error');
        }
    });
    // 查看狀態
    const statusCommand = vscode.commands.registerCommand('powerautomation.status', async () => {
        try {
            const status = await powerAutomationManager.getStatus();
            const message = `
🤖 PowerAutomation狀態報告

📊 系統狀態: ${status.running ? '✅ 運行中' : '❌ 已停止'}
🔗 EC2連接: ${status.ec2Connected ? '✅ 已連接' : '❌ 未連接'}
📡 TRAE狀態: ${status.traeConnected ? '✅ 已連接' : '❌ 未連接'}
📈 監控狀態: ${status.monitoring ? '✅ 啟用' : '❌ 停用'}

📋 當前倉庫: ${status.currentRepo || '未檢測到'}
💬 今日對話: ${status.todayConversations || 0}
⚡ 介入次數: ${status.interventions || 0}
🎯 成功率: ${status.successRate || 0}%

⏰ 運行時間: ${status.uptime || '0分鐘'}
            `.trim();
            vscode.window.showInformationMessage(message, { modal: true });
            logManager.log('狀態查詢完成');
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 狀態查詢失敗: ${error}`);
            logManager.log(`狀態查詢失敗: ${error}`, 'error');
        }
    });
    // 測試TRAE發送
    const testSendCommand = vscode.commands.registerCommand('powerautomation.testSend', async () => {
        try {
            const message = await vscode.window.showInputBox({
                prompt: '輸入要發送到TRAE的測試消息',
                value: '🧪 PowerAutomation測試消息'
            });
            if (message) {
                const result = await traeManager.sendMessage(message);
                if (result.success) {
                    vscode.window.showInformationMessage('✅ 消息發送成功！');
                    logManager.log(`測試消息發送成功: ${message}`);
                }
                else {
                    vscode.window.showErrorMessage(`❌ 發送失敗: ${result.error}`);
                    logManager.log(`測試消息發送失敗: ${result.error}`, 'error');
                }
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 測試發送失敗: ${error}`);
            logManager.log(`測試發送失敗: ${error}`, 'error');
        }
    });
    // 同步TRAE數據
    const syncTraeCommand = vscode.commands.registerCommand('powerautomation.syncTrae', async () => {
        try {
            vscode.window.showInformationMessage('🔄 正在同步TRAE數據...');
            const result = await traeManager.syncData();
            if (result.success) {
                vscode.window.showInformationMessage(`✅ 同步完成！處理了 ${result.count || 0} 個項目`);
                logManager.log(`TRAE數據同步完成: ${result.count || 0} 個項目`);
            }
            else {
                vscode.window.showErrorMessage(`❌ 同步失敗: ${result.error}`);
                logManager.log(`TRAE數據同步失敗: ${result.error}`, 'error');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 同步失敗: ${error}`);
            logManager.log(`同步失敗: ${error}`, 'error');
        }
    });
    // 打開儀表板
    const openDashboardCommand = vscode.commands.registerCommand('powerautomation.openDashboard', () => {
        openDashboard();
    });
    // 導出數據
    const exportDataCommand = vscode.commands.registerCommand('powerautomation.exportData', async () => {
        try {
            const result = await powerAutomationManager.exportData();
            if (result.success) {
                vscode.window.showInformationMessage(`✅ 數據已導出到: ${result.filePath}`);
                logManager.log(`數據導出成功: ${result.filePath}`);
            }
            else {
                vscode.window.showErrorMessage(`❌ 導出失敗: ${result.error}`);
                logManager.log(`數據導出失敗: ${result.error}`, 'error');
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`❌ 導出失敗: ${error}`);
            logManager.log(`導出失敗: ${error}`, 'error');
        }
    });
    // 註冊所有命令
    context.subscriptions.push(startCommand, stopCommand, statusCommand, testSendCommand, syncTraeCommand, openDashboardCommand, exportDataCommand, statusBarManager);
}
function createSidebarView(context) {
    // 創建PowerAutomation側邊欄視圖
    const provider = new PowerAutomationViewProvider(context);
    vscode.window.createTreeView('powerautomationView', {
        treeDataProvider: provider,
        showCollapseAll: true
    });
}
function openDashboard() {
    // 創建並顯示儀表板WebView
    const panel = vscode.window.createWebviewPanel('powerautomationDashboard', 'PowerAutomation 儀表板', vscode.ViewColumn.One, {
        enableScripts: true,
        retainContextWhenHidden: true
    });
    // 讀取儀表板HTML文件
    const dashboardPath = vscode.Uri.file(require('path').join(__dirname, '..', '..', 'ui', 'powerautomation_dashboard.html'));
    vscode.workspace.fs.readFile(dashboardPath).then(content => {
        panel.webview.html = content.toString();
    }, error => {
        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>PowerAutomation Dashboard</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', sans-serif; 
                        background: #1e1e1e; 
                        color: #cccccc; 
                        padding: 20px; 
                        text-align: center;
                    }
                    .error { color: #f44747; }
                    .info { color: #007acc; }
                </style>
            </head>
            <body>
                <h1>🤖 PowerAutomation 儀表板</h1>
                <div class="error">⚠️ 無法加載儀表板文件</div>
                <div class="info">請確保儀表板文件存在於正確位置</div>
                <p>錯誤: ${error}</p>
            </body>
            </html>
        `;
    });
    // 處理來自WebView的消息
    panel.webview.onDidReceiveMessage(async (message) => {
        switch (message.command) {
            case 'testSend':
                vscode.commands.executeCommand('powerautomation.testSend');
                break;
            case 'syncTrae':
                vscode.commands.executeCommand('powerautomation.syncTrae');
                break;
            case 'refreshData':
                // 刷新數據邏輯
                break;
            case 'exportData':
                vscode.commands.executeCommand('powerautomation.exportData');
                break;
        }
    }, undefined, []);
    logManager.log('儀表板已打開');
}
// PowerAutomation側邊欄視圖提供者
class PowerAutomationViewProvider {
    constructor(context) {
        this.context = context;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // 根節點
            return Promise.resolve([
                new PowerAutomationItem('🔧 系統狀態', vscode.TreeItemCollapsibleState.Expanded, 'status'),
                new PowerAutomationItem('📊 數據統計', vscode.TreeItemCollapsibleState.Expanded, 'stats'),
                new PowerAutomationItem('🚀 快速操作', vscode.TreeItemCollapsibleState.Expanded, 'actions'),
                new PowerAutomationItem('📋 最近活動', vscode.TreeItemCollapsibleState.Collapsed, 'recent')
            ]);
        }
        else {
            // 子節點
            switch (element.contextValue) {
                case 'status':
                    return Promise.resolve([
                        new PowerAutomationItem('🟢 EC2服務: 運行中', vscode.TreeItemCollapsibleState.None, 'status-item'),
                        new PowerAutomationItem('🔗 TRAE連接: 已連接', vscode.TreeItemCollapsibleState.None, 'status-item'),
                        new PowerAutomationItem('📊 當前倉庫: communitypowerauto', vscode.TreeItemCollapsibleState.None, 'status-item'),
                        new PowerAutomationItem('⚡ 智能介入: 啟用', vscode.TreeItemCollapsibleState.None, 'status-item')
                    ]);
                case 'stats':
                    return Promise.resolve([
                        new PowerAutomationItem('💬 總對話數: 23', vscode.TreeItemCollapsibleState.None, 'stats-item'),
                        new PowerAutomationItem('⚡ 介入率: 15.2%', vscode.TreeItemCollapsibleState.None, 'stats-item'),
                        new PowerAutomationItem('🎯 成功率: 94.7%', vscode.TreeItemCollapsibleState.None, 'stats-item'),
                        new PowerAutomationItem('📅 今日對話: 5', vscode.TreeItemCollapsibleState.None, 'stats-item')
                    ]);
                case 'actions':
                    return Promise.resolve([
                        new PowerAutomationItem('📤 測試TRAE發送', vscode.TreeItemCollapsibleState.None, 'action', {
                            command: 'powerautomation.testSend',
                            title: '測試TRAE發送'
                        }),
                        new PowerAutomationItem('🔄 同步TRAE數據', vscode.TreeItemCollapsibleState.None, 'action', {
                            command: 'powerautomation.syncTrae',
                            title: '同步TRAE數據'
                        }),
                        new PowerAutomationItem('📊 打開儀表板', vscode.TreeItemCollapsibleState.None, 'action', {
                            command: 'powerautomation.openDashboard',
                            title: '打開儀表板'
                        }),
                        new PowerAutomationItem('💾 導出數據', vscode.TreeItemCollapsibleState.None, 'action', {
                            command: 'powerautomation.exportData',
                            title: '導出數據'
                        })
                    ]);
                case 'recent':
                    return Promise.resolve([
                        new PowerAutomationItem('🎮 貪吃蛇游戲: 無需介入', vscode.TreeItemCollapsibleState.None, 'recent-item'),
                        new PowerAutomationItem('💻 Python學習: 已介入', vscode.TreeItemCollapsibleState.None, 'recent-item'),
                        new PowerAutomationItem('🔧 系統配置: 已完成', vscode.TreeItemCollapsibleState.None, 'recent-item')
                    ]);
                default:
                    return Promise.resolve([]);
            }
        }
    }
}
class PowerAutomationItem extends vscode.TreeItem {
    constructor(label, collapsibleState, contextValue, command) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.contextValue = contextValue;
        this.command = command;
        this.tooltip = this.label;
        this.command = command;
    }
}
function deactivate() {
    if (powerAutomationManager) {
        powerAutomationManager.stop();
    }
    if (statusBarManager) {
        statusBarManager.dispose();
    }
    logManager?.log('PowerAutomation擴展已停用');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map