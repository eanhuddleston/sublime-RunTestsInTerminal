# RunThisTest

A plugin for quickly running tests from within the Sublime Text editor. Uses your cursor position to identify which test(s) you want to run, and runs them in your chosen terminal (currently supports tmux and iTerm).

## INSTALLATION

### Package Control installation

Coming soon...

### Manual installation

Close Sublime Text, then download or clone this repository to a directory named `RunThisTest` in the Sublime Text Packages directory for your platform:

* OSX: `git clone https://github.com/eanhuddleston/sublime-RunThisTest.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/RunThisTest`
* Linux (untested): `git clone https://github.com/eanhuddleston/sublime-RunThisTest.git ~/.config/sublime-text-3/Packages/RunThisTest`
* Windows (untested): `git clone https://github.com/eanhuddleston/sublime-RunThisTest.git %APPDATA%\Sublime/ Text/ 3/Packages/RunThisTest`

## USAGE

### Currently supported test frameworks

Language | Framework
-------- | ---------
Python | Nose
Python | Pytest

### Commands

Command Palette | Command | Description
--------------- | ------- | -----------
`RunThisTest: test unit` | `run_tests_current_unit` | Run unit test under cursor
`RunThisTest: test class` | `run_tests_current_class` | Run all tests in the class under cursor
`RunThisTest: test file` | `run_tests_current_file` | Run all tests in current file
`RunThisTest: test suite` | `run_tests_current_suite` | Run all tests in the current test suite

### Key Bindings

Add your preferred key bindings: `Menu > Preferences > Key Bindings`.  E.g.:

```json
[
    { "keys": ["ctrl+shift+u"], "command": "run_tests_current_unit" },
    { "keys": ["ctrl+shift+c"], "command": "run_tests_current_class" },
    { "keys": ["ctrl+shift+f"], "command": "run_tests_current_file" },
    { "keys": ["ctrl+shift+s"], "command": "run_tests_current_suite"}
]
```
