"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LogManager = void 0;
const vscode = require("vscode");
class LogManager {
    constructor(context) {
        this.logs = [];
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('PowerAutomation');
    }
    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
        this.logs.push(logMessage);
        this.outputChannel.appendLine(logMessage);
        // 保持最近1000條日誌
        if (this.logs.length > 1000) {
            this.logs = this.logs.slice(-1000);
        }
    }
    logWithLevel(level, message) {
        this.log(message, level);
    }
    info(message) {
        this.log(message, 'INFO');
    }
    warn(message) {
        this.log(message, 'WARN');
    }
    error(message) {
        this.log(message, 'ERROR');
    }
    debug(message) {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const logLevel = config.get('logs.level', 'info');
        if (logLevel === 'debug') {
            this.log(message, 'DEBUG');
        }
    }
    showLogs() {
        this.outputChannel.show();
    }
    getRecentLogs(count = 50) {
        return this.logs.slice(-count);
    }
}
exports.LogManager = LogManager;
//# sourceMappingURL=logManager.js.map