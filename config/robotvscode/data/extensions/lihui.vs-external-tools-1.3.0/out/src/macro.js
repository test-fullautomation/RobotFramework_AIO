"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");
const path = require("path");
const clipboardy = require("clipboardy");
class Macro {
    replace(input) {
        if (!input) {
            return undefined;
        }
        let replaced = input;
        for (let key in this) {
            replaced = replaced.replace(`$(${key})`, this[key]);
        }
        return replaced;
    }
}
function create() {
    let macro = new Macro();
    return Promise.all([
        getActiveFilePath().then(value => { macro.ItemPath = value; }),
        getActiveFileDirectory().then(value => { macro.ItemDir = value; }),
        getActiveFileName().then(value => { macro.ItemFileName = value; }),
        getActiveFileExtension().then(value => { macro.ItemExt = value; }),
        getWorkspaceRootPath().then(value => { macro.ProjectDir = value; }),
        getClipboard().then(value => { macro.Clipboard = value; }),
        getCursorPosition().then(value => {
            macro.CurLine = (value.line + 1).toString();
            macro.CurCol = (value.character + 1).toString();
        }),
        getSelection().then(value => { macro.CurText = value; }),
    ]).then(() => {
        return macro;
    });
}
exports.create = create;
function getActiveFilePath() {
    return Promise.resolve(vscode.window.activeTextEditor.document.fileName);
}
function getActiveFileDirectory() {
    return Promise.resolve(path.dirname(vscode.window.activeTextEditor.document.fileName));
}
function getActiveFileName() {
    return getActiveFileExtension().then((ext) => {
        return path.basename(vscode.window.activeTextEditor.document.fileName, ext);
    });
}
function getActiveFileExtension() {
    return Promise.resolve(path.extname(vscode.window.activeTextEditor.document.fileName));
}
function getWorkspaceRootPath() {
    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
        return Promise.resolve(vscode.workspace.workspaceFolders[0].uri.fsPath);
    }
    return Promise.resolve(undefined);
}
function getClipboard() {
    return clipboardy.read().then(value => {
        return value;
    }, error => {
        return '';
    });
}
function getCursorPosition() {
    return Promise.resolve(vscode.window.activeTextEditor.selection.active);
}
function getSelection() {
    let selection = vscode.window.activeTextEditor.selection;
    return Promise.resolve(vscode.window.activeTextEditor.document.getText(selection));
}
//# sourceMappingURL=macro.js.map