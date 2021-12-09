#!/usr/bin/env bash

# A script for running mypy,
# with all its dependencies installed.
set -o errexit
# Change directory to the project root directory.
# cd "$(dirname "$0")"

# Run on all files,
# ignoring the paths passed to this script,
# so as not to miss type errors.
# My repo makes use of namespace packages.
# Use the namespace-packages flag
# and specify the package to run on explicitly.
# Note that we do not use --ignore-missing-imports,
# as this can give us false confidence in our results.
mypy \
    --namespace-packages \
    --explicit-package-bases .
