# RunThisTest

A plugin for quickly running tests from within the Sublime Text editor. Uses your cursor position to identify which test(s) you want to run, and runs them in your chosen terminal (currently supports tmux and iTerm).

Currently supports Python unittest and Pytest tests, but can be easily extended for other languages and test frameworks.

## INSTALLATION

### Package Control installation

Install [Package Control](https://packagecontrol.io/) use it within Sublime Text to search for and install `RunThisTest`.

### Manual installation

Copy this repository to a directory named `RunThisTest` in the Sublime Text Packages directory. E.g., for OS X:

`git clone https://github.com/eanhuddleston/sublime-RunThisTest.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/RunThisTest`

## USAGE

### Currently supported test frameworks

Language | Framework
-------- | ---------
Python | unittest
Python | Pytest

### Configuration

You need to tell RunThisTest how to run the tests in your different projects and also in which terminal the tests should be executed (currently tmux and iTerm are supported).

Example settings:

```
{
    "config_per_test_suite": [
        {
            "test_suite_path": "/Users/Bob/awesome_project/tests",
            "test_framework": "pytest",
            "command_template": "pytest {}"
        }
    ],
    "test_output_options": {
        "iterm": {}
    }
}
```

Access settings in `Preferences > Package Settings > RunThisTest`.

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
