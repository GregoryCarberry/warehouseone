#!/usr/bin/env bash
set -euo pipefail
export FLASK_APP=app:create_app

case "${1:-}" in
  init)
    flask db init
    ;;
  migrate)
    flask db migrate -m "${2:-auto}"
    ;;
  upgrade)
    flask db upgrade
    ;;
  seed)
    python -m seed.seed_data
    ;;
  run)
    python backend/run.py
    ;;
  *)
    echo "Usage: manage.sh [init|migrate|upgrade|seed|run]"
    ;;
esac
