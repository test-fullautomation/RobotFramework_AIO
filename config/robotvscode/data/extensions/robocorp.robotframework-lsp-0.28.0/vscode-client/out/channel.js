"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.logError = exports.OUTPUT_CHANNEL = exports.OUTPUT_CHANNEL_NAME = void 0;
const vscode_1 = require("vscode");
exports.OUTPUT_CHANNEL_NAME = "Robot Framework";
exports.OUTPUT_CHANNEL = vscode_1.window.createOutputChannel(exports.OUTPUT_CHANNEL_NAME);
function logError(msg, err) {
    exports.OUTPUT_CHANNEL.appendLine(msg);
    let indent = "    ";
    if (err.message) {
        exports.OUTPUT_CHANNEL.appendLine(indent + err.message);
    }
    if (err.stack) {
        let stack = "" + err.stack;
        exports.OUTPUT_CHANNEL.appendLine(stack.replace(/^/gm, indent));
    }
}
exports.logError = logError;
//# sourceMappingURL=channel.js.map