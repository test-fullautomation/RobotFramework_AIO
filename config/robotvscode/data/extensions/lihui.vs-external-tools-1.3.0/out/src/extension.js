'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require("vscode");
const process = require("child_process");
const macro = require("./macro");
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "vs-external-tools" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with  registerCommand
    // The commandId parameter must match the command field in package.json
    let commands = vscode.extensions.getExtension('lihui.vs-external-tools').packageJSON.contributes.commands;
    for (let command of commands) {
        let disposable = vscode.commands.registerCommand(command.command, () => {
            // The code you place here will be executed every time your command is executed
            executeCommand(vscode.workspace.getConfiguration(command.command));
        });
        context.subscriptions.push(disposable);
    }
}
exports.activate = activate;
function executeCommand(config) {
    let command = config.get('command');
    let args = config.get('args', []);
    let cwd = config.get('cwd');
    if (!command) {
        return;
    }
    macro.create().then((obj) => {
        let replacedArgs = args.map((arg) => {
            return obj.replace(arg);
        });
        let replacedCwd = obj.replace(cwd) || obj.ProjectDir || obj.ItemDir;
        try {
            process.spawn(command, replacedArgs, {
                cwd: replacedCwd
            });
        }
        catch (err) {
            console.log(err);
        }
    });
}
// this method is called when your extension is deactivated
function deactivate() {
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map