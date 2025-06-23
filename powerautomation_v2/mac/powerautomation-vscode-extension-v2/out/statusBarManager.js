"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StatusBarManager = void 0;
const vscode = require("vscode");
class StatusBarManager {
    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.text = "$(robot) PowerAutomation";
        this.statusBarItem.tooltip = "PowerAutomation - TRAE智能介入系統";
        this.statusBarItem.command = 'powerautomation.showStatus';
    }
    show() {
        this.statusBarItem.show();
    }
    updateStatus(status, icon) {
        const iconText = icon || '$(robot)';
        this.statusBarItem.text = `${iconText} ${status}`;
    }
    dispose() {
        this.statusBarItem.dispose();
    }
}
exports.StatusBarManager = StatusBarManager;
//# sourceMappingURL=statusBarManager.js.map