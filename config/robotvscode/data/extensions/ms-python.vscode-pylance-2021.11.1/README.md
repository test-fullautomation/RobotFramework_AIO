Pylance
=====================
### Fast, feature-rich language support for Python

Pylance is an extension that works alongside Python in Visual Studio Code to provide performant language support. Under the hood, Pylance is powered by [Pyright](https://github.com/microsoft/pyright), Microsoft's static type checking tool. Using Pyright, Pylance has the ability to supercharge your Python IntelliSense experience with rich type information, helping you write better code faster.

Pylance is the default language support for [Python in Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and is shipped as part of that extension as an optional dependency. 

The Pylance name is a small ode to Monty Python's Lancelot who was the first knight to answer the bridgekeeper's questions in the Holy Grail.

Quick Start
============
1. Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) from the marketplace. Pylance will be installed as an optional extension.
1. Open a Python (.py) file and the Pylance extension will activate.

Note: If you've previously set a language server and want to try Pylance, make sure you've set `"python.languageServer": "Default" or "Pylance"` in your settings.json file using the text editor, or using the Settings Editor UI.

Features
=========

![ features ](https://github.com/microsoft/pylance-release/raw/main/images/all-features.gif)

Pylance provides some awesome features for Python 3, including:

* Docstrings
* Signature help, with type information
* Parameter suggestions
* Code completion
* Auto-imports (as well as add and remove import code actions)
* As-you-type reporting of code errors and warnings (diagnostics)
* Code outline
* Code navigation
* Type checking mode
* Native multi-root workspace support
* IntelliCode compatibility
* Jupyter Notebooks compatibility
* Semantic highlighting

See the [changelog](https://github.com/microsoft/pylance-release/blob/main/CHANGELOG.md) for the latest release.

Settings and Customization
===============
Pylance provides users with the ability to customize their Python language support via a host of settings which can either be placed in the settings.json file in your workspace, or edited through the Settings Editor UI. 

- `pylance.insidersChannel`
    - Used to control the insiders download channel.
    - Available values:
        - `off` (default)
        - `daily`

- `python.analysis.typeCheckingMode`
    - Used to specify the level of type checking analysis performed;
    - Default: `off`
    - Available values:
        - `off`: No type checking analysis is conducted; unresolved imports/variables diagnostics are produced
        - `basic`: Non-type checking-related rules (all rules in `off`) + basic type checking rules
        - `strict`:	All type checking rules at the highest severity of error (includes all rules in `off` and `basic` categories)

- `python.analysis.diagnosticMode`
    - Used to allow a user to specify what files they want the language server to analyze to get problems flagged in their code.
    - Available values:
        - `workspace`
        - `openFilesOnly` (default)

- `python.analysis.stubPath`
    - Used to allow a user to specify a path to a directory that contains custom type stubs. Each package's type stub file(s) are expected to be in its own subdirectory.
    - Default value: `./typings`

- `python.analysis.autoSearchPaths`
    - Used to automatically add search paths based on some predefined names (like `src`).
    - Available values:
        - `true` (default)
        - `false`

- `python.analysis.extraPaths`
    - Used to specify extra search paths for import resolution. This replaces the old `python.autoComplete.extraPaths` setting.
    - Default value: empty array

- `python.analysis.diagnosticSeverityOverrides`
    - Used to allow a user to override the severity levels for individual diagnostics should they desire
    - Accepted severity values:
        - `error` (red squiggle)
        - `warning` (yellow squiggle)
        - `information` (blue squiggle)
        - `none` (disables the rule)

    - Available rule to use as keys can be found [here](https://github.com/microsoft/pylance-release/blob/main/DIAGNOSTIC_SEVERITY_RULES.md)
    - Example:
    ```
    { 
        "python.analysis.diagnosticSeverityOverrides": { 
            "reportUnboundVariable" : "information", 
            "reportImplicitStringConcatenation" : "warning" 
        } 
    } 
    ```

- `python.analysis.useLibraryCodeForTypes`
    - Used to parse the source code for a package when a typestub is not found
    - Accepted values:
        - `true` (default)
        - `false`

-   `python.analysis.autoImportCompletions`
    -   Used to control the offering of auto-imports in completions.
    -   Accepted values:
        -   `true` (default)
        -   `false`

-   `python.analysis.completeFunctionParens`
    -   Add parentheses to function completions.
    -   Accepted values:
        -   `true`
        -   `false` (default)

Semantic highlighting
=====================

Visual Studio Code uses TextMate grammars as the main tokenization engine. TextMate grammars work on a single file as input and break it up based on lexical rules expressed in regular expressions.

Semantic tokenization allows language servers to provide additional token information based on the language server's knowledge on how to resolve symbols in the context of a project. Themes can opt-in to use semantic tokens to improve and refine the syntax highlighting from grammars. The editor applies the highlighting from semantic tokens on top of the highlighting from grammars.

Here's an example of what semantic highlighting can add:

Without semantic highlighting:

![ semantic highlighting disabled ](https://github.com/microsoft/pylance-release/raw/main/semantic-disabled.png)

With semantic highlighting:

![ semantic highlighting enabled ](https://github.com/microsoft/pylance-release/raw/main/semantic-enabled.png)

Semantic colors can be customized in settings.json by associating the Pylance semantic token types and modifiers with the desired colors.

- Semantic token types
    - class, enum
    - parameter, variable, property, enumMember
    - function, member
    - module
    - intrinsic
    - magicFunction (dunder methods)
    - selfParameter, clsParameter

- Semantic token modifiers
    - declaration
    - readonly, static, abstract
    - async
    - typeHint, typeHintComment
    - decorator
    - builtin

The [scope inspector](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#scope-inspector) tool allows you to explore what semantic tokens are present in a source file and what theme rules they match to. 

Example of customizing semantic colors in settings.json:
```
{
    "editor.semanticTokenColorCustomizations": {
        "[One Dark Pro]": { // Apply to this theme only
            "enabled": true,
            "rules": {
                "magicFunction:python": "#ee0000",
                "function.declaration:python": "#990000",
                "*.decorator:python": "#0000dd",
                "*.typeHint:python": "#5500aa",
                "*.typeHintComment:python": "#aaaaaa"
            }
        }
    }
}
```

Contributing
===============
Pylance leverages Microsoft's open-source static type checking tool, Pyright, to provide performant language support for Python. 

Code contributions are welcomed via the [Pyright](https://github.com/microsoft/pyright) repo.

For information on getting started, refer to the [CONTRIBUTING instructions](https://github.com/microsoft/pyright/blob/main/CONTRIBUTING.md).


Feedback
===============
* File a bug in [GitHub Issues](https://github.com/microsoft/pylance-release/issues/new/choose)
* [Tweet us](https://twitter.com/pythonvscode/) with other feedback
