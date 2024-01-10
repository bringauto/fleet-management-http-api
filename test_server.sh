#!/bin/bash


omitted_files="*/__init__.py,*/models/*,*/typing_utils.py,*/util.py,enums.py"

pushd server
coverage run --omit=$omitted_files -m unittest discover -s .. -p "test_*.py"
coverage report --data-file=.coverage
popd