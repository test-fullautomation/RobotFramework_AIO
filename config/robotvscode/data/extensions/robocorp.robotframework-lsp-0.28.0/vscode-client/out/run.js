"use strict";
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
exports.registerRunCommands = exports.robotDebugSuite = exports.robotRunSuite = exports.robotDebug = exports.robotRun = void 0;
const vscode_1 = require("vscode");
const channel_1 = require("./channel");
const path = require("path");
const jsonc_parser_1 = require("jsonc-parser");
const fs = require("fs");
function robotRun(params) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            yield _debug(params, true);
        }
        catch (error) {
            channel_1.logError("Error running robot.", error);
        }
    });
}
exports.robotRun = robotRun;
function robotDebug(params) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            yield _debug(params, false);
        }
        catch (error) {
            channel_1.logError("Error debugging robot.", error);
        }
    });
}
exports.robotDebug = robotDebug;
function robotRunSuite(resource) {
    return __awaiter(this, void 0, void 0, function* () {
        yield _debugSuite(resource, true);
    });
}
exports.robotRunSuite = robotRunSuite;
function robotDebugSuite(resource) {
    return __awaiter(this, void 0, void 0, function* () {
        yield _debugSuite(resource, false);
    });
}
exports.robotDebugSuite = robotDebugSuite;
function checkFileExists(file) {
    return __awaiter(this, void 0, void 0, function* () {
        return fs.promises
            .access(file, fs.constants.F_OK)
            .then(() => true)
            .catch(() => false);
    });
}
function readAllDebugConfigs(workspaceFolder) {
    return __awaiter(this, void 0, void 0, function* () {
        const filename = path.join(workspaceFolder.uri.fsPath, ".vscode", "launch.json");
        if (!(yield checkFileExists(filename))) {
            return [];
        }
        try {
            const text = yield fs.promises.readFile(filename, "utf-8");
            const parsed = jsonc_parser_1.parse(text, [], { allowTrailingComma: true, disallowComments: false });
            if (!parsed.configurations || !Array.isArray(parsed.configurations)) {
                throw Error("Missing field in launch.json: configurations");
            }
            if (!parsed.version) {
                throw Error("Missing field in launch.json: version");
            }
            // We do not bother ensuring each item is a DebugConfiguration...
            return parsed.configurations;
        }
        catch (exc) {
            channel_1.logError("Error reading debug configurations to find the code-lens template.\nlaunch.json target: " + filename, exc);
            return [];
        }
    });
}
function readLaunchTemplate(workspaceFolder) {
    return __awaiter(this, void 0, void 0, function* () {
        const configs = yield readAllDebugConfigs(workspaceFolder);
        for (const cfg of configs) {
            if (cfg.type == "robotframework-lsp" &&
                cfg.name &&
                cfg.name.toLowerCase() == "robot framework: launch template") {
                return cfg;
            }
        }
        return undefined;
    });
}
function _debugSuite(resource, noDebug) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            if (!resource) {
                // i.e.: collect the tests from the file and ask which one to run.
                let activeTextEditor = vscode_1.window.activeTextEditor;
                if (!activeTextEditor) {
                    vscode_1.window.showErrorMessage("Can only run a test/task suite if the related file is currently opened.");
                    return;
                }
                resource = activeTextEditor.document.uri;
            }
            yield _debug({ "uri": resource.toString(), "path": resource.fsPath, "name": "*" }, noDebug);
        }
        catch (error) {
            channel_1.logError("Error debugging suite.", error);
        }
    });
}
function _debug(params, noDebug) {
    return __awaiter(this, void 0, void 0, function* () {
        let executeUri;
        let executePath;
        let executeName;
        if (!params) {
            // i.e.: collect the tests from the file and ask which one to run.
            let activeTextEditor = vscode_1.window.activeTextEditor;
            if (!activeTextEditor) {
                vscode_1.window.showErrorMessage("Can only run a test/task if the related file is currently opened.");
                return;
            }
            let uri = activeTextEditor.document.uri;
            let tests = yield vscode_1.commands.executeCommand("robot.listTests", { "uri": uri.toString() });
            if (!tests) {
                vscode_1.window.showErrorMessage("No tests/tasks found in the currently opened editor.");
                return;
            }
            executeUri = uri;
            executePath = uri.fsPath;
            if (tests.length == 1) {
                executeName = tests[0].name;
            }
            else {
                let items = [];
                for (const el of tests) {
                    items.push(el.name);
                }
                let selectedItem = yield vscode_1.window.showQuickPick(items, {
                    "canPickMany": false,
                    "placeHolder": "Please select Test / Task to run.",
                    "ignoreFocusOut": true,
                });
                if (!selectedItem) {
                    return;
                }
                executeName = selectedItem;
            }
        }
        else {
            executeUri = vscode_1.Uri.file(params.path);
            executePath = params.path;
            executeName = params.name;
        }
        let workspaceFolder = vscode_1.workspace.getWorkspaceFolder(executeUri);
        if (!workspaceFolder) {
            let folders = vscode_1.workspace.workspaceFolders;
            if (folders) {
                // Use the currently opened folder.
                workspaceFolder = folders[0];
            }
        }
        let cwd;
        let launchTemplate = undefined;
        if (workspaceFolder) {
            cwd = workspaceFolder.uri.fsPath;
            launchTemplate = yield readLaunchTemplate(workspaceFolder);
        }
        else {
            cwd = path.dirname(executePath);
        }
        let args;
        if (executeName == "*") {
            args = [];
        }
        else {
            args = ["-t", executeName];
        }
        let debugConfiguration = {
            "type": "robotframework-lsp",
            "name": "Robot Framework: Launch " + executeName,
            "request": "launch",
            "cwd": cwd,
            "target": executePath,
            "terminal": "integrated",
            "env": {},
            "args": args,
        };
        if (launchTemplate) {
            for (var key of Object.keys(launchTemplate)) {
                if (key !== "type" && key !== "name" && key !== "request") {
                    let value = launchTemplate[key];
                    if (value !== undefined) {
                        if (key === "args") {
                            try {
                                debugConfiguration.args = debugConfiguration.args.concat(value);
                            }
                            catch (err) {
                                channel_1.logError("Unable to concatenate: " + debugConfiguration.args + " to: " + value, err);
                            }
                        }
                        else {
                            debugConfiguration[key] = value;
                        }
                    }
                }
            }
        }
        let debugSessionOptions = { "noDebug": noDebug };
        vscode_1.debug.startDebugging(workspaceFolder, debugConfiguration, debugSessionOptions);
    });
}
function registerRunCommands(context) {
    return __awaiter(this, void 0, void 0, function* () {
        context.subscriptions.push(vscode_1.commands.registerCommand("robot.runTest", robotRun));
        context.subscriptions.push(vscode_1.commands.registerCommand("robot.debugTest", robotDebug));
        context.subscriptions.push(vscode_1.commands.registerCommand("robot.runSuite", robotRunSuite));
        context.subscriptions.push(vscode_1.commands.registerCommand("robot.debugSuite", robotDebugSuite));
    });
}
exports.registerRunCommands = registerRunCommands;
//# sourceMappingURL=run.js.map