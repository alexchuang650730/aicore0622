import * as vscode from 'vscode';

export class LogManager {
    private context: vscode.ExtensionContext;
    private outputChannel: vscode.OutputChannel;
    private logs: string[] = [];

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('PowerAutomation');
    }

    public log(message: string, level: string = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
        
        this.logs.push(logMessage);
        this.outputChannel.appendLine(logMessage);
        
        // 保持最近1000條日誌
        if (this.logs.length > 1000) {
            this.logs = this.logs.slice(-1000);
        }
    }

    private logWithLevel(level: string, message: string) {
        this.log(message, level);
    }

    info(message: string) {
        this.log(message, 'INFO');
    }

    warn(message: string) {
        this.log(message, 'WARN');
    }

    error(message: string) {
        this.log(message, 'ERROR');
    }

    debug(message: string) {
        const config = vscode.workspace.getConfiguration('powerautomation');
        const logLevel = config.get('logs.level', 'info') as string;
        
        if (logLevel === 'debug') {
            this.log(message, 'DEBUG');
        }
    }

    showLogs() {
        this.outputChannel.show();
    }

    getRecentLogs(count: number = 50): string[] {
        return this.logs.slice(-count);
    }
}

