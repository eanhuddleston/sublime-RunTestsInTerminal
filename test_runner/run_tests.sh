#!/usr/bin/env python3

import sys

from .test_runner import TestRunner

CONFIG_PER_TEST_SUITE = [
    {
        "name": "Hipmunk tests",
        "test_suite_path": "/Hipmunk/tests",
        "beginning_of_path_to_remove_for_test_command": "/Hipmunk/",
        "test_framework": "nose",
        "command_template": "hiptest {}",
    },
    {
        "name": "Concurbot tests",
        "test_suite_path": "/Hipmunk/hipmunk/hello/concur/tests",
        "beginning_of_path_to_remove_for_test_command": "/Hipmunk/",
        "test_framework": "pytest",
        "command_template": "docker exec -it hipmunk_concurbot_1 pytest /hipmunk/{} -s",
    },
]
TEST_OUTPUT_OPTIONS = {
    "tmux": {
        "session": "0",
        "window": "testing",
    }
}


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(
            "Missing an argument. How to run: \
            `run_tests.sh <file_name_with_path> <line_num> <test_type>`"
        )
    file_with_path = sys.argv[1]
    line_num = int(sys.argv[2])
    test_type = sys.argv[3]

    TestRunner().run_unit_tests(
        file_with_path,
        line_num,
        test_type,
        CONFIG_PER_TEST_SUITE,
        TEST_OUTPUT_OPTIONS,
    )
