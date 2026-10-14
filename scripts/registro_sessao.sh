#!/usr/bin/env bash
# registro_sessao.sh: captura bruta e mecânica do que mudou no projeto, sem julgamento.
#
# Chamado pelos hooks SessionStart e SessionEnd (ver .claude/settings.json).
# Uso: registro_sessao.sh inicio|fim        (JSON do hook em stdin, opcional)
#
# Grava em registro/sessoes.log, append-only. Não interpreta nada: lista commits,
# arquivos alterados e scripts/saídas tocadas. A curadoria em prosa é feita depois
# pelo agente `registro-dissertacao`, que lê este log.
#
# Nunca interrompe a sessão: qualquer erro é silenciado e a saída é sempre 0.

set -uo pipefail

RAIZ="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$RAIZ" 2>/dev/null || exit 0

FASE="${1:-fim}"
REG="$RAIZ/registro"
LOG="$REG/sessoes.log"
MARC="$REG/.marcador"
mkdir -p "$REG" 2>/dev/null || exit 0

JSON=$(cat 2>/dev/null || true)
SID=$(printf '%s' "$JSON" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("session_id","?")[:8])' 2>/dev/null) || SID="?"
[ -n "$SID" ] || SID="?"
AGORA=$(date "+%Y-%m-%d %H:%M:%S")
HEAD_AGORA=$(git rev-parse --short HEAD 2>/dev/null) || HEAD_AGORA="?"

if [ "$FASE" = "inicio" ]; then
    printf '%s\n' "$HEAD_AGORA" > "$MARC" 2>/dev/null
    exit 0
fi

# Fase "fim": compara com o marcador escrito no início da sessão.
HEAD_INICIO=$(cat "$MARC" 2>/dev/null) || HEAD_INICIO=""
[ -n "$HEAD_INICIO" ] || HEAD_INICIO="$HEAD_AGORA"

COMMITS=$(git log --oneline "$HEAD_INICIO..HEAD" 2>/dev/null | sed 's/^/    /')
ESTADO=$(git status --porcelain 2>/dev/null | sed 's/^/    /')
DIFFSTAT=$(git diff --stat HEAD 2>/dev/null | tail -1 | sed 's/^ *//')

# Arquivos tocados desde o início da sessão (pega também o que está fora do git,
# como data/interim). O marcador serve de referência de mtime.
if [ -f "$MARC" ]; then
    TOCADOS=$(find scripts outputs dissertacao registro sql data/interim \
        -type f -newer "$MARC" ! -name ".marcador" ! -name "sessoes.log" \
        ! -name "*.sqlite" ! -name "*.sql" 2>/dev/null | sort | sed 's/^/    /')
else
    TOCADOS=""
fi

{
    printf '\n=== sessão %s | fim em %s | HEAD %s -> %s\n' "$SID" "$AGORA" "$HEAD_INICIO" "$HEAD_AGORA"
    if [ -n "$COMMITS" ]; then printf '  commits novos:\n%s\n' "$COMMITS"; fi
    if [ -n "$TOCADOS" ]; then printf '  arquivos tocados:\n%s\n' "$TOCADOS"; fi
    if [ -n "$ESTADO" ]; then printf '  git status ao fim:\n%s\n' "$ESTADO"; fi
    if [ -n "$DIFFSTAT" ]; then printf '  diff vs HEAD: %s\n' "$DIFFSTAT"; fi
    if [ -z "$COMMITS$TOCADOS$ESTADO" ]; then printf '  (nada mudou)\n'; fi
} >> "$LOG" 2>/dev/null

exit 0
