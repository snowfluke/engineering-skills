#!/bin/sh
# Keeps existing hook settings working: the logic lives in block_dangerous_git.py next to this file.
exec python3 "$(dirname "$0")/block_dangerous_git.py"
