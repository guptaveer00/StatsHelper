#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  echo "Please follow the README setup instructions first."
  read "reply?Press Enter to close."
  exit 1
fi
.venv/bin/python app.py
read "reply?Press Enter to close."
