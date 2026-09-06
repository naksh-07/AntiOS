#!/usr/bin/env bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
echo "AntiOS caches cleaned."
