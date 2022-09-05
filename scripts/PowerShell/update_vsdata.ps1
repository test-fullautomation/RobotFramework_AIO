$PyPath = ($Env:RobotPythonPath) -replace [RegEx]::Escape("\"),"\\"
$WpPath = ([System.Uri]$Env:RobotTestPath).AbsoluteUri
$ToolsPath = ($Env:RobotToolsPath) -replace [RegEx]::Escape("\"),"\\"

$StorageContent = '
{
    "theme": "vs-dark",
    "themeBackground": "#1e1e1e",
    "windowSplash": {
        "baseTheme": "vs-dark",
        "colorInfo": {
            "foreground": "#cccccc",
            "background": "#1e1e1e",
            "editorBackground": "#1e1e1e",
            "titleBarBackground": "#3c3c3c",
            "activityBarBackground": "#333333",
            "sideBarBackground": "#252526",
            "statusBarBackground": "#007acc",
            "statusBarNoFolderBackground": "#68217a"
        },
        "layoutInfo": {
            "sideBarSide": "left",
            "editorPartMinWidth": 220,
            "titleBarHeight": 30,
            "activityBarWidth": 48,
            "sideBarWidth": 256,
            "statusBarHeight": 22,
            "windowBorder": false
        }
    },
    "windowsState": {
        "lastActiveWindow": {
            "folder": "{RobotTestPath}",
            "uiState": {
                "mode": 1,
                "x": 256,
                "y": 48,
                "width": 1024,
                "height": 779
            }
        },
        "openedWindows": []
    },
    "openedPathsList": {
        "entries": [
            {
                "folderUri": "{RobotTestPath}"
            }
        ]
    }
}'

$Content = '{
	"files.autoSave": "afterDelay",
    "files.autoSaveDelay": 5000,
    "editor.tabSize": 3,
    "editor.detectIndentation": true,
    "editor.insertSpaces": true,
    "editor.minimap.enabled": false,
    "vim.useCtrlKeys": false,
    "vim.overrideCopy": false,
    "editor.renderWhitespace": "none",
    "editor.rulers": [80],
    "glassit.alpha" : 255,
    "workbench.colorCustomizations": {},
	"workbench.colorTheme": "Visual Studio Dark",
    "editor.tabSize": 3,
    "editor.minimap.enabled": false,
    "editor.tokenColorCustomizations": {
        "comments" : "#383838",
        "strings": "#af4444",
        "functions": {
            "foreground": "#3bc278",
            "fontStyle": "bold"
        },
        "keywords": "#6449fc",
        "numbers": "#940074",
        "types": "#6e6e6e",
        "variables": "#a8a8a8", 
    },
    "workbench.tree.indent": 20,    

	"latex-workshop.view.pdf.viewer": "tab",
	"latex-workshop.latex.recipes": [
		{
			"name": "pdflatex",
			"tools": [
				"pdflatex"
			]
		}        
	],

	"files.associations": {
		"*.txt": "robot",
        "*.json": "jsonc",
    },
    "rfLanguageServer.includePaths": [
        "**/*.robot",
        "**/*.py"
    ],
    "window.zoomLevel": 0,
    "editor.renderControlCharacters": false,
    "plantuml.commandArgs": [
    
    ],
    "plantuml.previewSnapIndicators": true,
    "http.proxy": "http://rb-proxy-apac.bosch.com:8080",
    "https.proxy": "https://rb-proxy-apac.bosch.com:8080",
    "http.proxyAuthorization": null,
    "http.proxyStrictSSL": false,
    "editor.tabSize": 2,
    "editor.renderWhitespace": "all",
    "robot.language-server.python": "{RobotPythonPath}\\python.exe",
    "robot.python.executable": "{RobotPythonPath}\\python.exe",
    "robot.python.env": {
    
    },
    "python.defaultInterpreterPath": "{RobotPythonPath}\\python.exe",
	"auto-close-tag.activationOnLanguage": [

        "xml",
        "php",
        "blade",
        "ejs",
        "jinja",
        "javascript",
        "javascriptreact",
        "typescript",
        "typescriptreact",
        "plaintext",
        "markdown",
        "vue",
        "liquid",
        "erb",
        "lang-cfml",
        "cfml",
        "HTML (EEx)",
        "HTML (Eex)",
        "plist"
    ],
    "vim.startInInsertMode": true,
    "redhat.telemetry.enabled": false,
    "workbench.editorAssociations": {
        "*.ipynb": "jupyter-notebook"
    },
    "diffEditor.ignoreTrimWhitespace": false,
    "debug.javascript.usePreview": false,
    "terminal.integrated.defaultProfile.windows": "Git Bash",
    "editor.suggestSelection": "first",
    "vsintellicode.modify.editor.suggestSelection": "automaticallyOverrodeDefaultValue",
    "files.exclude": {
        "**/.classpath": true,
        "**/.project": true,
        "**/.settings": true,
        "**/.factorypath": true
    },
	"security.workspace.trust.untrustedFiles": "open",
    "autoDocstring.docstringFormat": "sphinx",
    "timeline.excludeSources": [],
    // Execute file with EcomEmu
    "vs-external-tools.externalCommand1.command": "{RobotToolsPath}\\ConEmu\\ConEmu64.exe",
    "vs-external-tools.externalCommand1.args": ["$(ItemPath)"],
    "vs-external-tools.externalCommand1.cwd": "$(ItemDir)",
}'

$KeyBindingContent = '
// Place your key bindings in this file to override the defaultsauto[]
[
    {
        "key": "ctrl+alt+r",
        "command": "vs-external-tools.externalCommand1"
    }
]'
($Content -replace '{RobotPythonPath}',$PyPath -replace '{RobotToolsPath}',$ToolsPath) | Set-Content -Path $Env:RobotVsCode\data\user-data\User\settings.json
($StorageContent -replace '{RobotTestPath}',$WpPath) | Set-Content -Path $Env:RobotVsCode\data\user-data\storage.json
Set-Content -Path $Env:RobotVsCode\data\user-data\User\keybindings.json -Value $KeyBindingContent


