"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const powerAutomationManager_1 = require("./powerAutomationManager");
function activate(context) {
    console.log('🚀 PowerAutomation 智能自動化助手已啟動');
    // 創建核心管理器
    const powerAutomationManager = new powerAutomationManager_1.PowerAutomationManager(context);
    // 創建狀態欄
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(robot) PowerAutomation: 就緒";
    statusBarItem.command = 'powerautomation.showStatus';
    statusBarItem.show();
    // 註冊所有命令
    const commands = [
        // 🚀 開始智能監控
        vscode.commands.registerCommand('powerautomation.startMonitoring', async () => {
            try {
                await powerAutomationManager.startMonitoring();
                statusBarItem.text = "$(sync~spin) PowerAutomation: 監控中";
                vscode.window.showInformationMessage('🚀 PowerAutomation 智能監控已開始');
            }
            catch (error) {
                vscode.window.showErrorMessage(`❌ 啟動監控失敗: ${error}`);
            }
        }),
        // ⏹️ 停止監控
        vscode.commands.registerCommand('powerautomation.stopMonitoring', async () => {
            powerAutomationManager.stopMonitoring();
            statusBarItem.text = "$(robot) PowerAutomation: 已停止";
            vscode.window.showInformationMessage('⏹️ PowerAutomation 監控已停止');
        }),
        // ☁️ 同步到EC2
        vscode.commands.registerCommand('powerautomation.syncToEC2', async () => {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "☁️ 同步到EC2中...",
                cancellable: false
            }, async (progress) => {
                try {
                    progress.report({ increment: 0, message: "連接EC2..." });
                    await powerAutomationManager.syncToEC2(progress);
                    vscode.window.showInformationMessage('✅ 同步到EC2成功');
                }
                catch (error) {
                    vscode.window.showErrorMessage(`❌ 同步失敗: ${error}`);
                }
            });
        }),
        // 📜 提取對話歷史
        vscode.commands.registerCommand('powerautomation.extractHistory', async () => {
            try {
                const history = await powerAutomationManager.extractConversationHistory();
                // 創建新文檔顯示歷史
                const doc = await vscode.workspace.openTextDocument({
                    content: JSON.stringify(history, null, 2),
                    language: 'json'
                });
                await vscode.window.showTextDocument(doc);
                vscode.window.showInformationMessage(`📜 提取了 ${history.length} 條對話記錄`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`❌ 提取歷史失敗: ${error}`);
            }
        }),
        // 💬 發送智能消息
        vscode.commands.registerCommand('powerautomation.sendMessage', async () => {
            const message = await vscode.window.showInputBox({
                prompt: '💬 輸入要發送的智能消息',
                placeHolder: '請輸入消息內容...',
                validateInput: (value) => {
                    if (!value || value.trim().length === 0) {
                        return '消息不能為空';
                    }
                    return null;
                }
            });
            if (message) {
                try {
                    await powerAutomationManager.sendIntelligentMessage(message);
                    vscode.window.showInformationMessage('✅ 智能消息發送成功');
                }
                catch (error) {
                    vscode.window.showErrorMessage(`❌ 發送消息失敗: ${error}`);
                }
            }
        }),
        // 🧠 智能介入模式
        vscode.commands.registerCommand('powerautomation.intelligentIntervention', async () => {
            const options = ['啟用智能介入', '停用智能介入', '查看介入設置'];
            const choice = await vscode.window.showQuickPick(options, {
                placeHolder: '🧠 選擇智能介入操作'
            });
            switch (choice) {
                case '啟用智能介入':
                    await powerAutomationManager.enableIntelligentIntervention();
                    vscode.window.showInformationMessage('🧠 智能介入已啟用');
                    break;
                case '停用智能介入':
                    powerAutomationManager.disableIntelligentIntervention();
                    vscode.window.showInformationMessage('⏸️ 智能介入已停用');
                    break;
                case '查看介入設置':
                    vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation.automation');
                    break;
            }
        }),
        // 📊 顯示系統狀態
        vscode.commands.registerCommand('powerautomation.showStatus', async () => {
            const status = await powerAutomationManager.getSystemStatus();
            const statusMessage = `
🤖 PowerAutomation 系統狀態

📡 TRAE監控: ${status.trae.isRunning ? '✅ 運行中' : '❌ 未運行'}
💾 數據庫: ${status.trae.dbExists ? '✅ 存在' : '❌ 不存在'}
🕐 最後更新: ${status.trae.lastUpdate || '無'}

☁️ EC2連接: ${status.ec2.connected ? '✅ 已連接' : '❌ 未連接'}
🔄 最後同步: ${status.ec2.lastSync || '無'}

🌐 Manus狀態: ${status.manus.connected ? '✅ 已連接' : '❌ 未連接'}
💬 對話數量: ${status.manus.conversationCount || 0}

🧠 智能介入: ${status.intervention.enabled ? '✅ 已啟用' : '❌ 已停用'}
🎯 介入次數: ${status.intervention.interventionCount || 0}
            `;
            const actions = ['刷新狀態', '打開設置', '查看日誌'];
            const action = await vscode.window.showInformationMessage(statusMessage, { modal: true }, ...actions);
            switch (action) {
                case '刷新狀態':
                    vscode.commands.executeCommand('powerautomation.showStatus');
                    break;
                case '打開設置':
                    vscode.commands.executeCommand('powerautomation.openSettings');
                    break;
                case '查看日誌':
                    powerAutomationManager.showLogs();
                    break;
            }
        }),
        // ⚙️ 打開設置
        vscode.commands.registerCommand('powerautomation.openSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'powerautomation');
        })
    ];
    // 監聽狀態變化
    powerAutomationManager.onStatusChange((status) => {
        if (status.isMonitoring) {
            statusBarItem.text = "$(sync~spin) PowerAutomation: 監控中";
        }
        else if (status.hasError) {
            statusBarItem.text = "$(error) PowerAutomation: 錯誤";
        }
        else {
            statusBarItem.text = "$(robot) PowerAutomation: 就緒";
        }
    });
    // 監聽配置變化
    const configWatcher = vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('powerautomation')) {
            powerAutomationManager.updateConfiguration();
        }
    });
    // 歡迎消息
    const config = vscode.workspace.getConfiguration('powerautomation');
    if (config.get('automation.autoSync')) {
        vscode.window.showInformationMessage('🚀 PowerAutomation 已啟動！自動監控功能已開啟。', '開始監控', '查看設置').then(action => {
            if (action === '開始監控') {
                vscode.commands.executeCommand('powerautomation.startMonitoring');
            }
            else if (action === '查看設置') {
                vscode.commands.executeCommand('powerautomation.openSettings');
            }
        });
    }
    // 添加到context
    context.subscriptions.push(...commands, statusBarItem, configWatcher, powerAutomationManager);
    console.log('✅ PowerAutomation 擴展初始化完成');
}
exports.activate = activate;
function deactivate() {
    console.log('👋 PowerAutomation 智能自動化助手已停用');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map