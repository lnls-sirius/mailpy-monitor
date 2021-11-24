#!/bin/sh
pip install pylint
pyreverse --colorized -o png -p mailpy --all-ancestors src/mailpy --output-directory=./docs
