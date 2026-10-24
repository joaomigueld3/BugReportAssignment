#!/usr/bin/env bash
# Reexecuta toda a exploração do zero (restaura o SQLite e roda 02..18).
# Fora daqui: 14_verify_mysql.py e 01b_verify_mysql.py, que exigem um contêiner MySQL ativo.
set -euo pipefail
cd "$(dirname "$0")"
PY=../.venv/bin/python
$PY 01_restore.py > /dev/null
for s in 0[2-9]_*.py 1[0-8]_*.py; do
  case "$s" in *verify_mysql*) continue ;; esac
  echo "== $s"; $PY "$s" > /dev/null
done
