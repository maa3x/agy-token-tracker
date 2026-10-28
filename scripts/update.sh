#!/usr/bin/env bash
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -d "$PLUGIN_DIR/.git" ]; then
    echo "Fetching latest version from GitHub..."
    git -C "$PLUGIN_DIR" pull origin main
else
    echo "Initializing git tracking..."
    cd "$PLUGIN_DIR"
    git init -b main
    git remote add origin https://github.com/maa3x/agy-token-tracker.git 2>/dev/null || git remote set-url origin https://github.com/maa3x/agy-token-tracker.git
    git fetch origin main
    git reset --hard origin/main
fi

echo "✅ token-tracker plugin is now up to date."
