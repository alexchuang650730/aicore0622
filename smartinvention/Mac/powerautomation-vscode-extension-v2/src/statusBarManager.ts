import * as vscode from 'vscode';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.text = "$(robot) PowerAutomation";
        this.statusBarItem.tooltip = "PowerAutomation - TRAE智能介入系統";
        this.statusBarItem.command = 'powerautomation.showStatus';
    }

    show() {
        this.statusBarItem.show();
    }

    updateStatus(status: string, icon?: string) {
        const iconText = icon || '$(robot)';
        this.statusBarItem.text = `${iconText} ${status}`;
    }

    dispose() {
        this.statusBarItem.dispose();
    }
}

