"use strict";
/**
 * The idea is doing an Interactive Console for Robot Framework inside of VSCode.
 *
 * There is previous work on this in https://github.com/microsoft/vscode-jupyter.
 *
 * Interesting docs related to webviews:
 * https://medium.com/younited-tech-blog/reactception-extending-vs-code-extension-with-webviews-and-react-12be2a5898fd
 * https://github.com/Ciaanh/reactception/
 * https://code.visualstudio.com/api/extension-guides/webview
 * https://marketplace.visualstudio.com/items?itemName=leocll.vscode-extension-webview-template
 * https://github.com/leocll/vscode-extension-webview-template
 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerInteractiveCommands = void 0;
const vscode_1 = require("vscode");
const vscode = require("vscode");
const channel_1 = require("../channel");
const RF_INTERACTIVE_LOCAL_RESOURCE_ROOT = process.env.RF_INTERACTIVE_LOCAL_RESOURCE_ROOT;
function getWebviewOptions(localResourceRoot) {
    return {
        // Enable javascript in the webview
        enableScripts: true,
        // We may have a lot of context in the interactive shell webview, and it may be tricky to save/restore it all.
        retainContextWhenHidden: true,
        // And restrict the webview to only loading content from our extension's directory.
        localResourceRoots: [localResourceRoot],
    };
}
function executeCheckedCommand(commandId, args) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            return yield vscode_1.commands.executeCommand(commandId, args);
        }
        catch (err) {
            return {
                "success": false,
                "message": "" + err.message,
                "result": undefined,
            };
        }
    });
}
let _lastActive = undefined;
class InteractiveShellPanel {
    constructor(panel, localResourceRoot, interpreterId, persistable) {
        this.disposables = [];
        this._lastMessageId = 0;
        this._panel = panel;
        this._localResourceRoot = localResourceRoot;
        this._interpreterId = interpreterId;
        this._persistable = persistable;
        let interactiveShell = this;
        this.initialized = new Promise((resolve, reject) => {
            interactiveShell._finishInitialized = resolve;
        });
        // Set the webview's initial html content
        const webview = this._panel.webview;
        this._panel.webview.html = this._getHtmlForWebview(webview);
        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programmatically
        this._panel.onDidDispose(() => this.dispose(), null, this.disposables);
        let nextMessageSeq = this.nextMessageSeq.bind(this);
        function handleEvaluate(message) {
            return __awaiter(this, void 0, void 0, function* () {
                let result = { "success": false, "message": "<error evaluating>", "result": undefined };
                try {
                    let code = message.arguments["expression"];
                    result = yield executeCheckedCommand("robot.internal.rfinteractive.evaluate", {
                        "interpreter_id": interpreterId,
                        "code": code,
                    });
                }
                catch (err) {
                    channel_1.logError("Error in evaluation.", err);
                }
                finally {
                    let response = {
                        type: "response",
                        seq: nextMessageSeq(),
                        command: message.command,
                        request_seq: message.seq,
                        body: "<evaluated from vscode>",
                    };
                    webview.postMessage(response); // Send the response, even if it was an error.
                }
                // Errors should be shown in the console already...
                // if (!result['success']) {
                //     window.showErrorMessage('Error evaluating in interactive console: ' + result['message'])
                // }
            });
        }
        function handleSemanticTokens(message) {
            return __awaiter(this, void 0, void 0, function* () {
                let result = undefined;
                try {
                    let code = message.arguments["code"];
                    // result is {'data': [...], 'resultId': ...}
                    result = yield vscode_1.commands.executeCommand("robot.internal.rfinteractive.semanticTokens", {
                        "interpreter_id": interpreterId,
                        "code": code,
                    });
                }
                catch (err) {
                    channel_1.logError("Error getting semantic tokens.", err);
                }
                finally {
                    let response = {
                        type: "response",
                        seq: nextMessageSeq(),
                        command: message.command,
                        request_seq: message.seq,
                        body: result,
                    };
                    webview.postMessage(response);
                }
            });
        }
        function handleCompletions(message) {
            return __awaiter(this, void 0, void 0, function* () {
                let result = undefined;
                try {
                    let code = message.arguments["code"];
                    let position = message.arguments["position"];
                    let context = message.arguments["context"];
                    // result is {'suggestions': [...], ...}
                    result = yield vscode_1.commands.executeCommand("robot.internal.rfinteractive.completions", {
                        "interpreter_id": interpreterId,
                        "code": code,
                        "position": {
                            "line": position["lineNumber"] - 1,
                            "character": position["column"] - 1,
                        },
                        "context": context,
                    });
                }
                catch (err) {
                    channel_1.logError("Error getting completions.", err);
                }
                finally {
                    let response = {
                        type: "response",
                        seq: nextMessageSeq(),
                        command: message.command,
                        request_seq: message.seq,
                        body: result,
                    };
                    webview.postMessage(response);
                }
            });
        }
        function handlePersistState(message) {
            return __awaiter(this, void 0, void 0, function* () {
                let result = undefined;
                try {
                    let stateToPersist = message.arguments["state"];
                    persistable.setState(stateToPersist);
                }
                catch (err) {
                    channel_1.logError("Error persisting state.", err);
                }
                finally {
                    let response = {
                        type: "response",
                        seq: nextMessageSeq(),
                        command: message.command,
                        request_seq: message.seq,
                        body: result,
                    };
                    webview.postMessage(response);
                }
            });
        }
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage((message) => __awaiter(this, void 0, void 0, function* () {
            if (message.type == "request") {
                let result = undefined;
                switch (message.command) {
                    case "evaluate":
                        yield handleEvaluate(message);
                        return;
                    case "semanticTokens":
                        yield handleSemanticTokens(message);
                        return;
                    case "completions":
                        yield handleCompletions(message);
                        return;
                    case "persistState":
                        yield handlePersistState(message);
                        return;
                }
            }
            else if (message.type == "event") {
                if (message.event == "initialized") {
                    interactiveShell._finishInitialized();
                }
            }
        }), null, this.disposables);
    }
    nextMessageSeq() {
        this._lastMessageId += 1;
        return this._lastMessageId;
    }
    static create(extensionUri, interpreterId, persistable) {
        return __awaiter(this, void 0, void 0, function* () {
            const column = vscode.window.activeTextEditor ? vscode.window.activeTextEditor.viewColumn : undefined;
            let localResourceRoot = vscode.Uri.joinPath(extensionUri, "src", "robotframework_ls", "vendored", "vscode-interpreter-webview");
            if (RF_INTERACTIVE_LOCAL_RESOURCE_ROOT) {
                localResourceRoot = vscode.Uri.file(RF_INTERACTIVE_LOCAL_RESOURCE_ROOT);
            }
            const panel = vscode.window.createWebviewPanel(InteractiveShellPanel.viewType, "Robot Framework Interactive Console", (column || vscode.ViewColumn.One) + 1, getWebviewOptions(localResourceRoot));
            let interactiveShellPanel = new InteractiveShellPanel(panel, localResourceRoot, interpreterId, persistable);
            _lastActive = interactiveShellPanel;
            panel.onDidChangeViewState(() => {
                if (panel.active) {
                    channel_1.OUTPUT_CHANNEL.appendLine("Changed active: " + interactiveShellPanel._interpreterId);
                    _lastActive = interactiveShellPanel;
                }
            });
            panel.onDidDispose(() => {
                if (_lastActive === interactiveShellPanel) {
                    _lastActive = undefined;
                }
            });
            return interactiveShellPanel;
        });
    }
    onOutput(category, output) {
        this._panel.webview.postMessage({
            "type": "event",
            "seq": this.nextMessageSeq(),
            "event": "output",
            "category": category,
            "output": output,
        });
    }
    dispose() {
        // Clean up our resources
        this._panel.dispose();
        while (this.disposables.length) {
            const x = this.disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
    _getHtmlForWebview(webview) {
        // Note: we can't really load from file://
        // See: https://github.com/microsoft/vscode/issues/87282
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._localResourceRoot, "bundle.js"));
        const initialState = JSON.stringify(this._persistable.getState());
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Robot Framework Interactive Console</title>
                <script>
                const vscode = acquireVsCodeApi();
                const initialState = ${initialState};
                </script>
                <script defer src="${scriptUri}"></script>
            </head>
			<body style="padding: 0 0 0 0">
			</body>
			</html>`;
    }
    evaluate(args) {
        const webview = this._panel.webview;
        let request = {
            type: "request",
            seq: this.nextMessageSeq(),
            command: "evaluate",
            body: args,
        };
        // We have to ask the UI to evaluate it (to add it to the UI and
        // then actually do the work in the backend).
        webview.postMessage(request);
    }
}
InteractiveShellPanel.viewType = "InteractiveShellPanel";
function registerInteractiveCommands(context, languageClient) {
    return __awaiter(this, void 0, void 0, function* () {
        let extensionUri = context.extensionUri;
        function interactiveShellCreateOrSendContentToEvaluate(args) {
            var _a;
            return __awaiter(this, void 0, void 0, function* () {
                let uri;
                if (args) {
                    // If we have an active window, use it.
                    if (_lastActive) {
                        _lastActive.evaluate(args);
                        return;
                    }
                    uri = args.uri;
                }
                else {
                    let activeFile = (_a = vscode.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.document;
                    let currUri = activeFile === null || activeFile === void 0 ? void 0 : activeFile.uri;
                    let msg = "Unable to create Robot Framework Interactive Console. Please open the related .robot/.resource file to provide the path used to create the Interactive Console.";
                    if (!currUri) {
                        vscode_1.window.showErrorMessage(msg);
                        return;
                    }
                    if (!currUri.fsPath.endsWith(".robot") && !currUri.fsPath.endsWith(".resource")) {
                        vscode_1.window.showErrorMessage(msg);
                        return;
                    }
                    uri = currUri.toString();
                }
                let interpreterId = -1;
                let buffered = new Array();
                let interactiveShellPanel = undefined;
                function onOutput(args) {
                    return __awaiter(this, void 0, void 0, function* () {
                        if (args["interpreter_id"] === interpreterId) {
                            let category = args["category"];
                            let output = args["output"];
                            interactiveShellPanel === null || interactiveShellPanel === void 0 ? void 0 : interactiveShellPanel.onOutput(category, output);
                        }
                    });
                }
                let disposeNotification = languageClient.onNotification("interpreter/output", (args) => {
                    if (buffered !== undefined) {
                        buffered.push(args);
                    }
                    else {
                        onOutput(args);
                    }
                });
                context.subscriptions.push(disposeNotification);
                // Note that during the creation, it's possible that we already have output, so, we
                // need to buffer anything up to the point where we actually have the interpreter.
                let result = yield vscode_1.commands.executeCommand("robot.internal.rfinteractive.start", { "uri": uri });
                if (!result["success"]) {
                    vscode_1.window.showErrorMessage("Error creating interactive console: " + result["message"]);
                    return;
                }
                interpreterId = result["result"]["interpreter_id"];
                const SAVE_IN_KEY = "interactiveConsoleState";
                let persistable = {
                    setState: (state) => {
                        let currState = persistable.getState();
                        if (!currState) {
                            context.globalState.update(SAVE_IN_KEY, state);
                        }
                        else {
                            // Note: merge the keys in the existing state.
                            Object.entries(state).forEach(([key, value]) => (currState[key] = value));
                            context.globalState.update(SAVE_IN_KEY, currState);
                        }
                    },
                    getState: () => {
                        return context.globalState.get(SAVE_IN_KEY);
                    },
                };
                interactiveShellPanel = yield InteractiveShellPanel.create(extensionUri, interpreterId, persistable);
                interactiveShellPanel.disposables.push(disposeNotification);
                function disposeInterpreter() {
                    executeCheckedCommand("robot.internal.rfinteractive.stop", {
                        "interpreter_id": interpreterId,
                    });
                }
                interactiveShellPanel.disposables.push({
                    "dispose": disposeInterpreter,
                });
                channel_1.OUTPUT_CHANNEL.appendLine("Waiting for Robot Framework Interactive Console UI (id: " + interpreterId + ") initialization.");
                yield interactiveShellPanel.initialized;
                channel_1.OUTPUT_CHANNEL.appendLine("Robot Framework Interactive Console UI (id: " + interpreterId + ") initialized.");
                while (buffered.length) {
                    buffered.splice(0, buffered.length).forEach((el) => {
                        onOutput(el);
                    });
                }
                // Start sending contents directly to the interactive shell now that we processed the
                // output backlog from the startup.
                buffered = undefined;
                if (args) {
                    interactiveShellPanel.evaluate(args);
                }
            });
        }
        context.subscriptions.push(vscode_1.commands.registerCommand("robot.interactiveShell", interactiveShellCreateOrSendContentToEvaluate));
    });
}
exports.registerInteractiveCommands = registerInteractiveCommands;
//# sourceMappingURL=rfInteractive.js.map