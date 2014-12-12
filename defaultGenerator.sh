#!/usr/bin/env bash

ITF1788_HOME="$(dirname "${BASH_SOURCE[0]}")"
# if $ITF1788_HOME does not start with '/', concat with current path
if [[ ! "$ITF1788_HOME" = /* ]]; then
    ITF1788_HOME="$(pwd)/$ITF1788_HOME"
fi

cd "${ITF1788_HOME}/src"

if [ ! $@ ]; then
    python3 $ITF1788_HOME/src/main.py -s "${ITF1788_HOME}/ITL files/" -o "${ITF1788_HOME}/output/"
else
    python3 main.py $@
fi
