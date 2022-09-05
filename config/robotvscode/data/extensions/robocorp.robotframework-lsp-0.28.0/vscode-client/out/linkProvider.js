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
exports.registerLinkProviders = void 0;
const vscode_1 = require("vscode");
const fs = require("fs");
function registerLinkProviders(extensionContext) {
    return __awaiter(this, void 0, void 0, function* () {
        extensionContext.subscriptions.push(vscode_1.window.registerTerminalLinkProvider({
            provideTerminalLinks(context) {
                let found = 0;
                const FOUND_LOG = 1;
                const FOUND_REPORT = 2;
                if (context.line.startsWith("Log:")) {
                    found = FOUND_LOG;
                }
                else if (context.line.startsWith("Report:")) {
                    found = FOUND_REPORT;
                }
                else {
                    return [];
                }
                if (context.line.endsWith("html")) {
                    let firstNonWhitespaceChar = found == FOUND_LOG ? 4 : 7;
                    for (; firstNonWhitespaceChar < context.line.length; firstNonWhitespaceChar++) {
                        let ch = context.line.charAt(firstNonWhitespaceChar);
                        if (ch != " " && ch != "\t") {
                            break;
                        }
                    }
                    if (firstNonWhitespaceChar < context.line.length - 1) {
                        let path = context.line.substring(firstNonWhitespaceChar).trim();
                        if (fs.existsSync(path)) {
                            return [
                                {
                                    startIndex: firstNonWhitespaceChar,
                                    length: path.length,
                                    tooltip: "Open " + (found == FOUND_LOG ? "Log" : "Report") + " in external Browser.",
                                    path: path,
                                },
                            ];
                        }
                    }
                }
                return [];
            },
            handleTerminalLink(link) {
                vscode_1.env.openExternal(vscode_1.Uri.file(link.path));
            },
        }));
    });
}
exports.registerLinkProviders = registerLinkProviders;
//# sourceMappingURL=linkProvider.js.map