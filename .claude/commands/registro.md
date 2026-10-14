---
description: Registra o que foi feito nesta sessão em NOTES.md, DECISIONS.md e dissertacao/
---

Invoque o agente `registro-dissertacao` (ferramenta Agent, `subagent_type: "registro-dissertacao"`), em primeiro plano, com esta instrução:

> Registre o trabalho feito desde a última entrada. Leia `registro/sessoes.log`, o `git log` e as saídas em `outputs/` que mudaram, confira o que já está em `NOTES.md`, `DECISIONS.md` e `dissertacao/` para não duplicar, e atualize os arquivos conforme a tabela de destinos da sua definição. Se nada mudou desde a última entrada, diga isso e não escreva nada.

Argumentos extra do pesquisador, se houver: $ARGUMENTS. Use-os para restringir o escopo do registro (por exemplo a uma etapa ou um script específico).

Depois que o agente terminar, relate ao pesquisador quais arquivos mudaram e quais pendências ficaram, e não faça commit.
