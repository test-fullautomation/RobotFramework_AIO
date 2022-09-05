# External Tools for Visual Studio Code

Inspired by [Visual Studio External Tools](https://docs.microsoft.com/en-us/sql/ssms/menu-help/external-tools).
Use this extension to add external tools, such as Tortoise Git or Notepad.
Adding external tools allows you to easily launch other applications.
You can specify arguments and a working directory when launching the tool.

## Features

This extension contributes 24 commands:

* `vs-external-tools.externalCommand1`
* `vs-external-tools.externalCommand2`
* ...
* `vs-external-tools.externalCommand24`

Two ways to launch external command 1(Other commands are the same):

1. Execute command `External Command 1` in Command Palette(`Ctrl + Shift + P` or `Cmd + Shift + P`).
2. [Binding a key](https://code.visualstudio.com/docs/customization/keybindings) for command `vs-external-tools.externalCommand1`.


## Extension Settings

This extension contributes the following settings:

* vs-external-tools.externalCommand1:
    * `vs-external-tools.externalCommand1.command`: Specify the path to the .exe, .com, .pif, .bat, .cmd, or other file that you intend to launch. 
    * `vs-external-tools.externalCommand1.args`: Specify the variables that are passed to the tool when the tool is executed.
    * `vs-external-tools.externalCommand1.cwd`: Specify the working directory of the tool.
* vs-external-tools.externalCommand2: `command`, `args`, `cwd` are the same as command1.
* ...
* vs-external-tools.externalCommand24: `command`, `args`, `cwd` are the same as command1.

This extension supplies values for when an external tool is launched. 
These values can be used as macros in `args` and `cwd`.

Macro list for external tools:
* `$(ItemPath)` The complete file name of the current source (defined as drive + path + file name).
* `$(ItemDir)` The directory of the current source (defined as drive + path).
* `$(ItemFileName)` The file name of the current source (defined as file name).
* `$(ItemExt)` The file name extension of the current source.
* `$(ProjectDir)` The directory of the current workspace (defined as drive + path).
* `$(Clipboard)` The content from clipboard.
* `$(CurLine)` The current line position of the cursor in the editor.
* `$(CurCol)` The current column position of the cursor in the editor.
* `$(CurText)` The current selection text.

## Sample

Show TortoiseGit log window for current file. 
```javescript
{
    "vs-external-tools.externalCommand1.command": "TortoiseGitProc.exe",
    "vs-external-tools.externalCommand1.args": ["/command:log", "/path:$(ItemPath)"],
    "vs-external-tools.externalCommand1.cwd": "$(ItemDir)"
}
```

## Release Notes

### 1.3.0

Support Macro `$(CurLine)`, `$(CurCol)`, `$(CurText)`

### 1.1.0

Support Macro `$(Clipboard)`

### 1.0.0

Initial release of vs-external-tools


-----------------------------------------------------------------------------------------------------------


**Enjoy!**