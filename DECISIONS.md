# DECISIONS

Formato: data, título, status, evidência, alternativas, decisão, responsável. Todas as entradas abaixo foram abertas em 2026-10-06. Decisões metodológicas pertencem ao pesquisador. A evidência remete a `outputs/` (gerado por `scripts/`).

## D1. SGBD e ambiente de restauração
- Status: fechada (2026-10-13).
- Evidência: `02_schema`: dump `mysqldump 10.13 / MySQL 8.0.12`, MyISAM/InnoDB, 7 bancos. `14_verify_mysql`: restauração real em `mysql:8.0.12` (Docker) sem erros; 35 de 35 tabelas com mesma contagem e mesmo hash de conteúdo que o SQLite construído pelo parser próprio (`01_restore.py`).
- Alternativas consideradas: MySQL/MariaDB em Docker; MariaDB via apt (exigia sudo); parser próprio para SQLite.
- Decisão: ambiente de trabalho = SQLite (`data/interim/bugs.sqlite`), validado contra MySQL 8.0.12. MySQL em Docker fica como referência para conferência.
- Responsável: pesquisador (confirmar).

## D2. Rótulo do desenvolvedor: `author` ou `assignee`
- Status: aberta.
- Evidência: `06_label`. `assignee == author` por linha: 32,2% (BIRT), 61,8% (UI), 65,6% (JDT), 81,1% (SWT). Entre bugs com assignee não genérico, assignee é um dos authors em 34,1%, 71,6%, 77,0%, 88,0%. Assignees genéricos em 3,1% a 13,4% dos bugs. Formatos de identificador heterogêneos. `author` tem 42 a 143 valores distintos por projeto; `assignee`, 109 a 180.
- Corroboração (D8): no fold 1 de `ExtractedFeatures`, o positivo é `author` do dump em 100% das 1.196 queries com positivo (só Eclipse UI) e igual ao `assignee` em 68,8%; os 142 candidatos são quase o conjunto de authors de UI no dump (139 de 143). Alternativas: author (premissa de Alkhazi, quem commitou corrigiu); assignee excluindo contas genéricas; author com resolução de identidades; restringir a bugs em que os dois concordam.
- Decisão: pendente.
- Responsável: pesquisador.

## D3. Separação de `importance` em prioridade e severidade
- Status: aberta, com evidência favorável.
- Evidência: `05_importance`: 30.781 de 30.781 bugs seguem `P<1-5> <severidade>`, sem nulos nem exceções; valor constante por bug. P3 em 81% a 93% e "normal" em 69% a 73% dos bugs.
- Alternativas: parsing direto em dois campos; tratar "enhancement" como severidade ou excluir; decidir como mapear níveis categóricos em pesos que somam 1.
- Decisão: pendente (parsing é viável sem perda).
- Responsável: pesquisador.

## D4. Proxy de tempo de correção
- Status: aberta.
- Evidência: `02_schema` (sem data de resolução ou atribuição); `09_interval`: mediana por bug de 4,7 a 9,2 dias, cauda até 4.138 dias, 0,1% a 0,7% de bugs com intervalo negativo, 405 a 1.218 bugs com intervalo < 1 hora.
- Alternativas: `commit_time - report_time` do primeiro commit; do último commit; truncamento ou winsorização de outliers; descarte de negativos.
- Decisão: pendente. Declarar como limitação em qualquer caso.
- Responsável: pesquisador.

## D5. Viés de workload por ausência de bugs não corrigidos
- Status: aberta.
- Evidência: `04_status`: nenhuma linha sem commit; 574 bugs distintos com resolução não FIXED e 545 abertos, todos com commit. Bugs sem commit não existem no dump (população ausente não mensurável aqui).
- Alternativas: declarar a limitação; complementar via API do Bugzilla (fora do escopo e da regra de rede desta fase); restringir a análise a bugs FIXED.
- Decisão: pendente.
- Responsável: pesquisador.

## D6. Timestamp de ordenação do split e regra de corte do Ramo B
- Status: aberta.
- Evidência: `07_period`: dados até 2014-01-17. `10_leakage`: com ordenação por `report_time`, 85% a 100% dos bugs de teste têm bugs de treino cuja correção é posterior ao seu `report_time` (média de 6 a 41 bugs, 0,2% a 0,6% do treino). `09_interval` mostra commits antes do report em 0,1% a 0,7% dos bugs.
- Alternativas: ordenar por `report_time` e restringir as métricas do Ramo B a bugs com `commit_time` anterior ao `report_time` do bug avaliado; ordenar por `commit_time`.
- Decisão: pendente.
- Responsável: pesquisador.

## D7. Viabilidade das features de commit (φ19 a φ22)
- Status: aberta.
- Evidência: `12_commit_log`: `log` preenchido em 100% das linhas e dos bugs; `files` em 99,9% a 100%.
- Pendente: conferir no artigo de Alkhazi (2020) o que cada feature exige. Nada implementado.
- Evidência adicional (`13_features_sanity`): os CSV liberados têm 18 features (14 na abordagem anterior); φ19 a φ22 não aparecem nos arquivos (inferência).
- Responsável: pesquisador.

## D8. Teste de sanidade com `ExtractedFeatures.zip` e `SVMrank_Models.zip`
- Status: fechada quanto à inspeção (2026-10-13); a decisão de seguir sem comparação com o ICPC 2019 cabe ao pesquisador.
- Evidência: `13_features_sanity`. Só Eclipse UI: 890 bugs, todos em `bug_commit` (9,4% dos 9.424), 622 em `bug_and_files`. No fold 1 o positivo é `author` do dump em 1.196 de 1.196 queries com positivo; nos folds 2 e 3 só em 12,0% e 13,2%, com a mesma sequência de `bug_id`. Os arquivos não definem o split. Modelos só para os folds 2 e 3, kernel linear.
- Alternativas: (a) não fazer o teste (adotada nesta fase, pela condição do CLAUDE.md não satisfeita); (b) usar apenas o fold 1 como corroboração do rótulo `author`; (c) pedir aos autores o código de geração.
- Decisão: (a), com (b) registrado como evidência para D2. Comparação numérica com resultados publicados está fora de escopo.
- Responsável: pesquisador (confirmar).

## D9. Origem da diferença de contagem Alkhazi (22.416) vs DevRanker (21.098)
- Status: aberta.
- Evidência: `03_counts`: `bug_and_files` tem 21.098 bugs, igual a DevRanker por projeto; `bug_commit` tem 30.781. O filtro FIXED (29.383) não reproduz nenhum dos dois. A diferença não é explicada pelo dump.
- Alternativas: aceitar `bug_and_files` como base; tentar reconstruir o filtro de Alkhazi; consultar os autores.
- Responsável: pesquisador.

## Entradas novas surgidas dos dados

## D10. População-base e chave do bug
- Status: aberta.
- Evidência: `03_counts`: `bug_commit` (30.781 bugs, grão bug-commit, pares repetidos) contra `bug_and_files` (21.098 bugs, 1 linha por bug, só fixed e wontfix, sem assignee/author/importance/log). `bug_id` repete entre bancos (74 entre UI e JDT).
- Alternativas: base `bug_commit` filtrada por status; base `bug_and_files` unida a `bug_commit` por (projeto, `bug_id`); outra.
- Decisão: pendente. A chave deve incluir o projeto.
- Responsável: pesquisador.

## D11. Resolução de identidades e contas genéricas
- Status: aberta.
- Evidência: `06_label`: `author` mistura nomes completos e logins (46 de 74 sem espaço em BIRT; 47 authors de BIRT nunca aparecem como assignee). Contas genéricas por regex `inbox|triaged|^birt-`: 224 a 1.153 bugs por projeto; a regex é heurística minha, não validada. `08_developers`: 12 a 65 desenvolvedores aparecem só depois do corte de 80%.
- Alternativas: mapeamento manual login para nome; normalização por heurística; descartar bugs com assignee genérico; tratar desenvolvedores novos como cold-start.
- Responsável: pesquisador.

## D12. Bugs com status aberto ou vazio em `bug_commit`
- Status: aberta.
- Evidência: `04_status`: 545 abertos (NEW, ASSIGNED, REOPENED) e 279 vazios, todos com commit vinculado; origem do vínculo não confirmada (falta inspecionar `log`).
- Alternativas: excluir; manter; investigar `log` antes.
- Responsável: pesquisador.
