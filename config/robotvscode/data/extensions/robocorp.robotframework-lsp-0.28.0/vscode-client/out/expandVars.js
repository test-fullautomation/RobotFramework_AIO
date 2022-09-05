"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getArrayStrFromConfigExpandingVars = exports.getStrFromConfigExpandingVars = exports.expandVars = void 0;
const vscode_1 = require("vscode");
const channel_1 = require("./channel");
/**
 * It'd be nicer is VSCode itself provided such an API, but alas, it's not really
 * available, so, we need to reimplement it...
 */
function expandVars(template) {
    let getVar = function getVar(name) {
        if (name == "${workspace}" || name == "${workspaceRoot}" || name == "${workspaceFolder}") {
            let workspaceFolders = vscode_1.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                return workspaceFolders[0].uri.fsPath;
            }
        }
        else if ((name.startsWith("${env.") || name.startsWith("${env:")) && name.endsWith("}")) {
            let varName = name.substring(6, name.length - 1);
            let value = process.env[varName];
            if (value) {
                return value;
            }
        }
        channel_1.OUTPUT_CHANNEL.appendLine("Unable to resolve variable: " + name);
        return name;
    };
    let ret = template.replace(/\${([^{}]*)}/g, getVar);
    if (ret.startsWith("~")) {
        const homedir = require("os").homedir();
        return homedir + ret.substr(1);
    }
    return ret;
}
exports.expandVars = expandVars;
function getStrFromConfigExpandingVars(config, name) {
    let value = config.get(name);
    if (typeof value !== "string") {
        channel_1.OUTPUT_CHANNEL.appendLine("Expected string for configuration: " + name);
        return undefined;
    }
    return expandVars(value);
}
exports.getStrFromConfigExpandingVars = getStrFromConfigExpandingVars;
function getArrayStrFromConfigExpandingVars(config, name) {
    let array = config.get(name);
    if (array) {
        if (!Array.isArray(array)) {
            channel_1.OUTPUT_CHANNEL.appendLine("Expected string[] for configuration: " + name);
            return undefined;
        }
        let ret = [];
        for (const s of array) {
            if (typeof s !== "string") {
                ret.push(expandVars("" + s));
            }
            else {
                ret.push(expandVars(s));
            }
        }
        return ret;
    }
    return array;
}
exports.getArrayStrFromConfigExpandingVars = getArrayStrFromConfigExpandingVars;
//# sourceMappingURL=expandVars.js.map