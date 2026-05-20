#!/usr/bin/env sh
set -eu

BASE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
GLOBAL_CONFIG="$HOME/Library/Application Support/ngrok/ngrok.yml"
LOCAL_CONFIG="$BASE_DIR/ngrok.yml"

if [ ! -f "$LOCAL_CONFIG" ]; then
  echo "Missing local config: $LOCAL_CONFIG" >&2
  exit 1
fi

if [ ! -f "$GLOBAL_CONFIG" ]; then
  echo "Missing global ngrok config: $GLOBAL_CONFIG" >&2
  echo "Run: ngrok config add-authtoken <YOUR_TOKEN>" >&2
  exit 1
fi

exec ngrok start --all --config "$GLOBAL_CONFIG,$LOCAL_CONFIG"
