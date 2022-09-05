/*
Original work Copyright (c) Microsoft Corporation (MIT)
See ThirdPartyNotices.txt in the project root for license information.
All modifications Copyright (c) Robocorp Technologies Inc.
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License")
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http: // www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
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
exports.activate = void 0;
const net = require("net");
const path = require("path");
const fs = require("fs");
const vscode = require("vscode");
const vscode_1 = require("vscode");
const vscode_languageclient_1 = require("vscode-languageclient");
const node_1 = require("vscode-languageclient/node");
const progress_1 = require("./progress");
const time_1 = require("./time");
const run_1 = require("./run");
const linkProvider_1 = require("./linkProvider");
const expandVars_1 = require("./expandVars");
const rfInteractive_1 = require("./interactive/rfInteractive");
const channel_1 = require("./channel");
function createClientOptions(initializationOptions) {
    const clientOptions = {
        documentSelector: ["robotframework"],
        synchronize: {
            configurationSection: ["robot", "robocorp.home"],
        },
        outputChannel: channel_1.OUTPUT_CHANNEL,
        initializationOptions: initializationOptions,
    };
    return clientOptions;
}
function startLangServerIO(command, args, initializationOptions) {
    const serverOptions = {
        command,
        args,
    };
    let src = path.resolve(__dirname, "../../src");
    serverOptions.options = { env: Object.assign(Object.assign({}, process.env), { PYTHONPATH: src }) };
    // See: https://code.visualstudio.com/api/language-extensions/language-server-extension-guide
    return new node_1.LanguageClient(command, serverOptions, createClientOptions(initializationOptions));
}
function startLangServerTCP(addr, initializationOptions) {
    const serverOptions = function () {
        return new Promise((resolve, reject) => {
            var client = new net.Socket();
            client.connect(addr, "127.0.0.1", function () {
                resolve({
                    reader: client,
                    writer: client,
                });
            });
        });
    };
    return new node_1.LanguageClient(`tcp lang server (port ${addr})`, serverOptions, createClientOptions(initializationOptions));
}
function findExecutableInPath(executable) {
    const IS_WINDOWS = process.platform == "win32";
    const sep = IS_WINDOWS ? ";" : ":";
    const PATH = process.env["PATH"];
    const split = PATH.split(sep);
    for (let i = 0; i < split.length; i++) {
        const s = path.join(split[i], executable);
        if (fs.existsSync(s)) {
            return s;
        }
    }
    return undefined;
}
class RobotDebugConfigurationProvider {
    provideDebugConfigurations(folder, token) {
        let configurations = [];
        configurations.push({
            "type": "robotframework-lsp",
            "name": "Robot Framework: Launch .robot file",
            "request": "launch",
            "cwd": '^"\\${workspaceFolder}"',
            "target": '^"\\${file}"',
            "terminal": "integrated",
            "env": {},
            "args": [],
        });
        return configurations;
    }
    resolveDebugConfigurationWithSubstitutedVariables(folder, debugConfiguration, token) {
        return __awaiter(this, void 0, void 0, function* () {
            // When we resolve a configuration we add the pythonpath and variables to the command line.
            let args = debugConfiguration.args;
            let config = vscode_1.workspace.getConfiguration("robot");
            let pythonpath = expandVars_1.getArrayStrFromConfigExpandingVars(config, "pythonpath");
            let variables = config.get("variables");
            let targetRobot = debugConfiguration.target;
            // If it's not specified in the language, let's check if some plugin wants to provide an implementation.
            let interpreter = yield vscode_1.commands.executeCommand("robot.resolveInterpreter", targetRobot);
            if (interpreter) {
                pythonpath = pythonpath.concat(interpreter.additionalPythonpathEntries);
                if (interpreter.environ) {
                    if (!debugConfiguration.env) {
                        debugConfiguration.env = interpreter.environ;
                    }
                    else {
                        for (let key of Object.keys(interpreter.environ)) {
                            debugConfiguration.env[key] = interpreter.environ[key];
                        }
                    }
                }
                // Also, overridde env variables in the launch config.
                try {
                    let newEnv = yield vscode_1.commands.executeCommand("robocorp.updateLaunchEnv", {
                        "targetRobot": targetRobot,
                        "env": debugConfiguration.env,
                    });
                    if (newEnv == "cancelled") {
                        channel_1.OUTPUT_CHANNEL.appendLine("Launch cancelled");
                        return undefined;
                    }
                    debugConfiguration.env = newEnv;
                }
                catch (error) {
                    // The command may not be available.
                }
            }
            let newArgs = [];
            pythonpath.forEach((element) => {
                newArgs.push("--pythonpath");
                newArgs.push(element);
            });
            for (let key in variables) {
                if (variables.hasOwnProperty(key)) {
                    newArgs.push("--variable");
                    newArgs.push(key + ":" + expandVars_1.expandVars(variables[key]));
                }
            }
            if (args) {
                args = args.concat(newArgs);
            }
            else {
                args = newArgs;
            }
            debugConfiguration.args = args;
            if (debugConfiguration.cwd) {
                let stat;
                try {
                    stat = yield vscode.workspace.fs.stat(vscode.Uri.file(debugConfiguration.cwd));
                }
                catch (err) {
                    vscode_1.window.showErrorMessage("Unable to launch. Reason: the cwd: " + debugConfiguration.cwd + " does not exist.");
                    return undefined;
                }
                if ((stat.type | vscode.FileType.File) == 1) {
                    vscode_1.window.showErrorMessage("Unable to launch. Reason: the cwd: " +
                        debugConfiguration.cwd +
                        " seems to be a file and not a directory.");
                    return undefined;
                }
            }
            return debugConfiguration;
        });
    }
}
function registerDebugger(languageServerExecutable) {
    function createDebugAdapterExecutable(env, targetRobot) {
        return __awaiter(this, void 0, void 0, function* () {
            let dapPythonExecutable = expandVars_1.getStrFromConfigExpandingVars(vscode_1.workspace.getConfiguration("robot"), "python.executable");
            // If it's not specified in the language, let's check if some plugin wants to provide an implementation.
            let interpreter = yield vscode_1.commands.executeCommand("robot.resolveInterpreter", targetRobot);
            if (interpreter) {
                dapPythonExecutable = interpreter.pythonExe;
                if (interpreter.environ) {
                    if (!env) {
                        env = interpreter.environ;
                    }
                    else {
                        for (let key of Object.keys(interpreter.environ)) {
                            env[key] = interpreter.environ[key];
                        }
                    }
                }
            }
            else if (!dapPythonExecutable && env) {
                // If a `PYTHON_EXE` is specified in the env, give it priority vs using the language server
                // executable.
                dapPythonExecutable = env["PYTHON_EXE"];
            }
            if (!dapPythonExecutable) {
                // If the dapPythonExecutable is not specified, use the default language server executable.
                if (!languageServerExecutable) {
                    vscode_1.window.showWarningMessage("Error getting language server python executable for creating a debug adapter.");
                    return;
                }
                dapPythonExecutable = languageServerExecutable;
            }
            let targetMain = path.resolve(__dirname, "../../src/robotframework_debug_adapter/__main__.py");
            if (!fs.existsSync(targetMain)) {
                vscode_1.window.showWarningMessage("Error. Expected: " + targetMain + " to exist.");
                return;
            }
            if (!fs.existsSync(dapPythonExecutable)) {
                vscode_1.window.showWarningMessage("Error. Expected: " + dapPythonExecutable + " to exist.");
                return;
            }
            if (env) {
                return new vscode_1.DebugAdapterExecutable(dapPythonExecutable, ["-u", targetMain], { "env": env });
            }
            else {
                return new vscode_1.DebugAdapterExecutable(dapPythonExecutable, ["-u", targetMain]);
            }
        });
    }
    try {
        vscode_1.debug.registerDebugConfigurationProvider("robotframework-lsp", new RobotDebugConfigurationProvider());
        vscode_1.debug.registerDebugAdapterDescriptorFactory("robotframework-lsp", {
            createDebugAdapterDescriptor: (session) => {
                let env = session.configuration.env;
                let target = session.configuration.target;
                return createDebugAdapterExecutable(env, target);
            },
        });
    }
    catch (error) {
        // i.e.: https://github.com/microsoft/vscode/issues/118562
        channel_1.logError("Error registering debugger.", error);
    }
}
function getDefaultLanguageServerPythonExecutable() {
    return __awaiter(this, void 0, void 0, function* () {
        channel_1.OUTPUT_CHANNEL.appendLine("Getting language server Python executable.");
        let languageServerPython = expandVars_1.getStrFromConfigExpandingVars(vscode_1.workspace.getConfiguration("robot"), "language-server.python");
        let executable = languageServerPython;
        if (!executable || (executable.indexOf("/") == -1 && executable.indexOf("\\") == -1)) {
            // Try to use the Robocorp Code extension to provide one for us (if it's installed and
            // available).
            try {
                let languageServerPython = yield vscode_1.commands.executeCommand("robocorp.getLanguageServerPython");
                if (languageServerPython) {
                    channel_1.OUTPUT_CHANNEL.appendLine("Language server Python executable gotten from robocorp.getLanguageServerPython.");
                    return {
                        executable: languageServerPython,
                        "message": undefined,
                    };
                }
            }
            catch (error) {
                // The command may not be available (in this case, go forward and try to find it in the filesystem).
            }
            // Search python from the path.
            if (!executable) {
                channel_1.OUTPUT_CHANNEL.appendLine("Language server Python executable. Searching in PATH.");
                if (process.platform == "win32") {
                    executable = findExecutableInPath("python.exe");
                }
                else {
                    executable = findExecutableInPath("python3");
                    if (!fs.existsSync(executable)) {
                        executable = findExecutableInPath("python");
                    }
                }
            }
            else {
                channel_1.OUTPUT_CHANNEL.appendLine("Language server Python executable. Searching " + executable + " from the PATH.");
                executable = findExecutableInPath(executable);
                channel_1.OUTPUT_CHANNEL.appendLine("Language server Python executable. Found: " + executable);
            }
            if (!fs.existsSync(executable)) {
                return {
                    executable: undefined,
                    "message": "Unable to start robotframework-lsp because: python could not be found on the PATH. Do you want to select a python executable to start robotframework-lsp?",
                };
            }
            return {
                executable: executable,
                "message": undefined,
            };
        }
        else {
            if (!fs.existsSync(executable)) {
                return {
                    executable: undefined,
                    "message": "Unable to start robotframework-lsp because: " +
                        executable +
                        " does not exist. Do you want to select a new python executable to start robotframework-lsp?",
                };
            }
            return {
                executable: executable,
                "message": undefined,
            };
        }
    });
}
function activate(context) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            // The first thing we need is the python executable.
            let timing = new time_1.Timing();
            let executableAndMessage = yield getDefaultLanguageServerPythonExecutable();
            if (executableAndMessage.message) {
                channel_1.OUTPUT_CHANNEL.appendLine(executableAndMessage.message);
                let saveInUser = "Yes (save in user settings)";
                let saveInWorkspace = "Yes (save in workspace settings)";
                let selection = yield vscode_1.window.showWarningMessage(executableAndMessage.message, ...[saveInUser, saveInWorkspace, "No"]);
                // robot.language-server.python
                if (selection == saveInUser || selection == saveInWorkspace) {
                    let onfulfilled = yield vscode_1.window.showOpenDialog({
                        "canSelectMany": false,
                        "openLabel": "Select python exe",
                    });
                    if (!onfulfilled || onfulfilled.length == 0) {
                        // There's not much we can do (besides start listening to changes to the related variables
                        // on the finally block so that we start listening and ask for a reload if a related configuration changes).
                        channel_1.OUTPUT_CHANNEL.appendLine("Unable to start (python selection cancelled).");
                        return;
                    }
                    let configurationTarget;
                    if (selection == saveInUser) {
                        configurationTarget = vscode_1.ConfigurationTarget.Global;
                    }
                    else {
                        configurationTarget = vscode_1.ConfigurationTarget.Workspace;
                    }
                    let config = vscode_1.workspace.getConfiguration("robot");
                    try {
                        config.update("language-server.python", onfulfilled[0].fsPath, configurationTarget);
                    }
                    catch (err) {
                        let errorMessage = "Error persisting python to start the language server.\nError: " + err.message;
                        channel_1.logError("Error persisting python to start the language server.", err);
                        if (configurationTarget == vscode_1.ConfigurationTarget.Workspace) {
                            try {
                                config.update("language-server.python", onfulfilled[0].fsPath, vscode_1.ConfigurationTarget.Global);
                                vscode_1.window.showInformationMessage("It was not possible to save the configuration in the workspace. It was saved in the user settings instead.");
                                err = undefined;
                            }
                            catch (err2) {
                                // ignore this one (show original error).
                            }
                        }
                        if (err !== undefined) {
                            vscode_1.window.showErrorMessage(errorMessage);
                        }
                    }
                    executableAndMessage = { "executable": onfulfilled[0].fsPath, message: undefined };
                }
                else {
                    // There's not much we can do (besides start listening to changes to the related variables
                    // on the finally block so that we start listening and ask for a reload if a related configuration changes).
                    channel_1.OUTPUT_CHANNEL.appendLine("Unable to start (no python executable specified).");
                    return;
                }
            }
            let port = vscode_1.workspace.getConfiguration("robot").get("language-server.tcp-port");
            let langServer;
            let initializationOptions = {};
            try {
                let pluginsDir = yield vscode_1.commands.executeCommand("robocorp.getPluginsDir");
                try {
                    if (pluginsDir && pluginsDir.length > 0) {
                        channel_1.OUTPUT_CHANNEL.appendLine("Plugins dir: " + pluginsDir + ".");
                        initializationOptions["pluginsDir"] = pluginsDir;
                    }
                }
                catch (error) {
                    channel_1.logError("Error setting pluginsDir.", error);
                }
            }
            catch (error) {
                // The command may not be available.
            }
            if (port) {
                // For TCP server needs to be started seperately
                channel_1.OUTPUT_CHANNEL.appendLine("Connecting to port: " + port);
                langServer = startLangServerTCP(port, initializationOptions);
            }
            else {
                let targetMain = path.resolve(__dirname, "../../src/robotframework_ls/__main__.py");
                if (!fs.existsSync(targetMain)) {
                    vscode_1.window.showWarningMessage("Error. Expected: " + targetMain + " to exist.");
                    return;
                }
                let args = ["-u", targetMain];
                let lsArgs = vscode_1.workspace.getConfiguration("robot").get("language-server.args");
                if (lsArgs) {
                    args = args.concat(lsArgs);
                }
                channel_1.OUTPUT_CHANNEL.appendLine("Starting RobotFramework Language Server with args: " + executableAndMessage.executable + "," + args);
                langServer = startLangServerIO(executableAndMessage.executable, args, initializationOptions);
            }
            let stopListeningOnDidChangeState = langServer.onDidChangeState((event) => {
                if (event.newState == vscode_languageclient_1.State.Running) {
                    // i.e.: We need to register the customProgress as soon as it's running (we can't wait for onReady)
                    // because at that point if there are open documents, lots of things may've happened already, in
                    // which case the progress won't be shown on some cases where it should be shown.
                    context.subscriptions.push(langServer.onNotification("$/customProgress", (args) => {
                        // OUTPUT_CHANNEL.appendLine(args.id + ' - ' + args.kind + ' - ' + args.title + ' - ' + args.message + ' - ' + args.increment);
                        progress_1.handleProgressMessage(args);
                    }));
                    context.subscriptions.push(langServer.onRequest("$/executeWorkspaceCommand", (args) => __awaiter(this, void 0, void 0, function* () {
                        // OUTPUT_CHANNEL.appendLine(args.command + " - " + args.arguments);
                        let ret;
                        try {
                            ret = yield vscode_1.commands.executeCommand(args.command, args.arguments);
                        }
                        catch (err) {
                            if (!(err.message && err.message.endsWith("not found"))) {
                                // Log if the error wasn't that the command wasn't found
                                channel_1.logError("Error executing workspace command.", err);
                            }
                        }
                        return ret;
                    })));
                    stopListeningOnDidChangeState.dispose();
                }
            });
            let disposable = langServer.start();
            registerDebugger(executableAndMessage.executable);
            yield run_1.registerRunCommands(context);
            yield linkProvider_1.registerLinkProviders(context);
            yield rfInteractive_1.registerInteractiveCommands(context, langServer);
            context.subscriptions.push(disposable);
            // i.e.: if we return before it's ready, the language server commands
            // may not be available.
            channel_1.OUTPUT_CHANNEL.appendLine("Waiting for RobotFramework (python) Language Server to finish activating...");
            yield langServer.onReady();
            let version = vscode_1.extensions.getExtension("robocorp.robotframework-lsp").packageJSON.version;
            try {
                let lsVersion = yield vscode_1.commands.executeCommand("robot.getLanguageServerVersion");
                if (lsVersion != version) {
                    vscode_1.window.showErrorMessage("Error: expected robotframework-lsp version: " +
                        version +
                        ". Found: " +
                        lsVersion +
                        "." +
                        " Please uninstall the older version from the python environment.");
                }
            }
            catch (err) {
                let msg = "Error: robotframework-lsp version mismatch. Please uninstall the older version from the python environment.";
                channel_1.logError(msg, err);
                vscode_1.window.showErrorMessage(msg);
            }
            channel_1.OUTPUT_CHANNEL.appendLine("RobotFramework Language Server ready. Took: " + timing.getTotalElapsedAsStr());
        }
        finally {
            vscode_1.workspace.onDidChangeConfiguration((event) => {
                for (let s of [
                    "robot.language-server.python",
                    "robot.language-server.tcp-port",
                    "robot.language-server.args",
                ]) {
                    if (event.affectsConfiguration(s)) {
                        vscode_1.window
                            .showWarningMessage('Please use the "Reload Window" action for changes in ' + s + " to take effect.", ...["Reload Window"])
                            .then((selection) => {
                            if (selection === "Reload Window") {
                                vscode_1.commands.executeCommand("workbench.action.reloadWindow");
                            }
                        });
                        return;
                    }
                }
            });
        }
    });
}
exports.activate = activate;
//# sourceMappingURL=extension.js.map