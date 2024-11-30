#!/bin/sh
if ollama list > /dev/null 2>&1; then
    exit 0
else
    exit 1
fi