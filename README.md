# Tasty

A plugin for quickly running tests from within the Sublime Text editor. Uses your cursor position to idenfity which test(s) you want to run, and runs the tests in your chosen terminal (e.g., a specific tmux or iTerm window).

## INSTALLATION

### Package Control installation

Coming soon...

### Manual installation

Close Sublime Text, then download or clone this repository to a directory named `Tasty` in the Sublime Text Packages directory for your platform:

* Linux: `git clone https://github.com/eanhuddleston/tasty.git ~/.config/sublime-text-3/Packages/Test`
* OSX: `git clone https://github.com/eanhuddleston/tasty.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Test`
* Windows: `git clone https://github.com/eanhuddleston/tasty.git %APPDATA%\Sublime/ Text/ 3/Packages/Test`

## USAGE

### Currently supported test frameworks

Language | Framework
-------- | ---------
Python | Nose
Python | Pytest
Mixed | Sublime Text

### Commands

Command Palette | Command | Description
--------------- | ------- | -----------
`Tasty: test unit` | `run_tests_current_unit` | Run unit test under cursor.
`Tasty: test class` | `run_tests_current_class` | Run all tests in the class under cursor.
`Tasty: test file` | `run_tests_current_file` | Run all tests in current file.
`Tasty: test suite` | `run_tests_current_suite` | Run all tests in the current test suite.

### Key Bindings

Add your preferred key bindings: `Menu > Preferences > Key Bindings`. E.g.:

```json
[
    { "keys": ["ctrl+shift+u"], "command": "run_tests_current_unit" },
    { "keys": ["ctrl+shift+c"], "command": "run_tests_current_class" },
    { "keys": ["ctrl+shift+f"], "command": "run_tests_current_file" },
    { "keys": ["ctrl+shift+a"], "command": "run_tests_current_suite"},
]
```
