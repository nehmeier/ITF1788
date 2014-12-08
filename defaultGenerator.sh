#!/bin/bash

ITF1788_HOME=$(pwd)
cd ${ITF1788_HOME}/src

if [ ! $@ ]; then
    python3 main.py -s "${ITF1788_HOME}/ITL files/" -o "${ITF1788_HOME}/output/"
else
    python3 main.py $@
fi
