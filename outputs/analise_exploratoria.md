# Análise exploratória do dataset de bug triaging (HybridBugRank)

Versão de 2026-10-23. Documento autocontido para uso em um Claude Project. Todos os números vêm de consultas e scripts do repositório (indicados entre parênteses como `NN`, ex.: `18` = `scripts/18_eda_base.py`). Nenhum modelo foi treinado ou avaliado. Nomes de desenvolvedores não aparecem.

Rótulos usados no texto: **(fato)** medido; **(inferência)** conclusão minha a partir de fatos; **(não confirmado)** falta evidência, com o que faltou. A escolha de técnicas e de método pertence ao pesquisador; este documento descreve propriedades dos dados e deixa as perguntas em aberto na seção 11.

## 1. Contexto do projeto

Dissertação de mestrado (Engenharia da Computação) que propõe o **HybridBugRank**, recomendação de desenvolvedores para bug reports com dois ramos e um gate de fusão.

- Ramo A: BERT-base-uncased com fine-tuning sobre `summary` + `description`, gerando um sinal textual por par (bug, desenvolvedor).
- Ramo B: quatro métricas do desenvolvedor (Rastogi et al. 2013; Yadav et al. 2019; Saxena e Gupta 2024, DDRS): Developer Priority Score, Developer Severity Score, tempo médio de correção e workload.
- Gate: `Score(b, d) = g(b, d)·h_A(b, d) + (1 − g(b, d))·h_B(m_d)`, com `g` dependente do par.
- Perguntas de pesquisa: RQ1 gate contra fusão heurística estilo DDRS (top-1, top-3, MRR); RQ2 gate contra fusão global aprendida (λ escalar único); RQ3 os pesos aprendidos para tempo médio e workload saem negativos?; RQ4 adicionar desenvolvedor sem retreino.
- Split previsto: cronológico 80/10/10. Corte temporal estrito no Ramo B (cada métrica usa só informação anterior à data do bug avaliado).

## 2. O dataset e sua proveniência

Fonte: repositório anonimizado de Alkhazi et al. (ICPC 2019 e Applied Soft Computing 2020), arquivo `SQL_BugDatabase_Dump.7z` (SHA-256 `ae1f9670e90c71b35090aed9ecf2db021c1385a2e317651a83225414f3d3b19d`).

- (fato, 01, 02) Dump `mysqldump 10.13` de MySQL 8.0.12, um banco por projeto (birt, eclipse_platform_ui, jdt, swt, aspectj, tomcat) mais `api_descriptions`; 35 tabelas. Restaurado em MySQL real (Docker) e em SQLite por parser próprio; 35 de 35 tabelas idênticas em contagem e hash (duas verificações independentes).
- (fato, 02) A tabela principal `bug_commit` tem as 16 colunas do README: `id, bug_id, summary, description, report_time, reporter, assignee, status, product, component, importance, commit, author, commit_time, log, files`. Não há coluna de projeto (o projeto é o banco), nem data de resolução, nem data de atribuição.
- (fato, 03) Grão de `bug_commit`: uma linha por par bug-commit (1,22 a 1,45 linhas por bug; máximo 142). Existem também `bug_and_files` (1 linha por bug, 21.098 bugs, só resoluções fixed e wontfix, sem assignee, author, importance e log) e `file_history`.
- (fato, 03) `bug_id` repete entre bancos (74 entre Eclipse UI e JDT): a chave de um bug é (projeto, `bug_id`).
- Projetos usados: BIRT, Eclipse Platform UI, JDT, SWT. AspectJ e Tomcat ficam fora.
- (fato, 07) Datas de `report_time` de 2001-10 (UI, JDT), 2002-02 (SWT) e 2005-06 (BIRT) até 2014-01-17. Sem fuso (DATETIME). (não confirmado) o fuso de origem.
- Arquivos adicionais do upstream (13): `ExtractedFeatures.zip` e `SVMrank_Models.zip`, só para Eclipse UI (890 bugs, 142 candidatos por query, 18 features na abordagem nova e 14 na anterior). No fold 1 o positivo é o `author` do dump em 100% das 1.196 queries com positivo; os folds 2 e 3 não alinham com o dump e o split não é recuperável.

## 3. Decisões do pesquisador já tomadas e pendências

Fechadas: **D1** SQLite como base de trabalho, validado contra MySQL. **D2** rótulo = `author` do commit. **D3** (parcial) `importance` separado em prioridade P1 a P5 e severidade. **D4** tempo de correção = `commit_time` do primeiro commit menos `report_time`, em dias. **D6** ordenar por `report_time`; cada métrica do Ramo B usa só bugs com `commit_time` anterior ao `report_time` do bug avaliado. **D10** base = `bug_commit` com resolução FIXED, chave (projeto, `bug_id`). **D13** bugs com mais de um author: todos os authors são positivos.

Abertas: **D5** viés de workload por bugs sem commit. **D7** viabilidade das features de commit φ19 a φ22 (falta a definição no artigo de Alkhazi 2020). **D9** origem da diferença Alkhazi 22.416 contra DevRanker 21.098. **D11** resolução de identidades e contas genéricas. **D12** bugs com status aberto ou vazio (hoje fora da base pela D10). **D14** o que publicar no GitHub.

## 4. A base de análise (D10 + D2 + D13)

(fato, 18) Bugs distintos com resolução FIXED, por projeto:

| Projeto | Bugs | Linhas bug-commit | Authors distintos | Pares bug-author | Positivos por bug | Bugs com 2+ authors |
|---|---|---|---|---|---|---|
| BIRT | 6.658 | 8.713 | 74 | 6.954 | 1,044 | 256 (3,8%) |
| Eclipse UI | 8.854 | 12.079 | 138 | 9.220 | 1,041 | 334 (3,8%) |
| JDT | 8.277 | 10.075 | 53 | 8.525 | 1,030 | 229 (2,8%) |
| SWT | 5.594 | 8.058 | 41 | 5.873 | 1,050 | 244 (4,4%) |
| Total | 29.383 | 38.925 | n/a | 30.572 | 1,040 | 1.063 (3,6%) |

(fato, 03) Referências da literatura: Alkhazi 22.416 bugs (252 desenvolvedores) e DevRanker 21.098. A base tem 6.967 e 8.285 bugs a mais, respectivamente. (fato, 14) 608 configurações de filtro testadas sobre `bug_commit` não reproduziram os tamanhos de Alkhazi para nenhum projeto; as 15 de menor erro somado (totais de 22.844 a 24.735 bugs) têm só 66 a 70 desenvolvedores, contra 252. (não confirmado) o critério de Alkhazi.

(fato, 04) Fora da base: 545 bugs com status aberto (NEW, ASSIGNED, REOPENED), 279 com status vazio e 574 com resolução diferente de FIXED (WONTFIX 242, WORKSFORME 203, INVALID 122, NOT_ECLIPSE 7), todos com commit vinculado. A hipótese "o dump só tem bugs fechados" é falsa para `bug_commit`.

## 5. O rótulo: distribuição, cauda longa e cold-start

(fato, 18) Pares bug-author por author, base FIXED:

| Projeto | Authors | Mediana | Máx | Top-1 | Top-5 | Top-10 | Com até 5 | Com 50+ | Gini |
|---|---|---|---|---|---|---|---|---|---|
| BIRT | 74 | 25 | 727 | 10,5% | 37,1% | 60,6% | 23 | 28 | 0,70 |
| Eclipse UI | 138 | 3 | 1.704 | 18,5% | 51,6% | 72,6% | 87 | 26 | 0,87 |
| JDT | 53 | 2 | 1.951 | 22,9% | 75,0% | 92,7% | 29 | 15 | 0,86 |
| SWT | 41 | 12 | 1.346 | 22,9% | 70,0% | 90,3% | 19 | 14 | 0,79 |

(inferência) Cauda longa forte: em Eclipse UI 87 de 138 authors têm até 5 bugs; em JDT cinco authors concentram 75% dos pares. SWT e JDT têm poucas classes (41 e 53), o que facilita artificialmente o problema e deve ser declarado.

**Cold-start sob split cronológico 80/10/10 por report_time** (por contagem de bugs, por projeto; fato, 18):

| Projeto | Split | Bugs | Pares com author ausente do treino | Bugs sem nenhum author no treino |
|---|---|---|---|---|
| BIRT | val | 666 | 1,2% | 1,1% |
| BIRT | teste | 666 | 6,5% | 6,3% |
| Eclipse UI | val | 885 | 1,9% | 1,5% |
| Eclipse UI | teste | 886 | 20,8% | 19,8% |
| JDT | val | 828 | 0,4% | 0,2% |
| JDT | teste | 828 | 5,1% | 3,6% |
| SWT | val | 559 | 0,0% | 0,0% |
| SWT | teste | 560 | 13,7% | 12,0% |

(fato) Em teste, a fração de bugs cujos authors são todos ausentes do treino é o teto de perda de qualquer modelo restrito aos authors vistos: 6,3% (BIRT), 19,8% (UI), 3,6% (JDT), 12,0% (SWT). Também em teste, 36,2% (UI) e 21,1% (SWT) dos pares têm author com menos de 5 bugs no treino. (inferência) Isto liga diretamente à RQ4 (desenvolvedor novo sem retreino).

**Pool de candidatos no tempo** (fato, 18): authors distintos nos 365 dias anteriores ao `report_time` de cada bug de teste, mediana (q10 a q90): BIRT 26 (23 a 28), UI 36 (30 a 52), JDT 8 (6 a 17), SWT 13 (10 a 16). O histórico completo tem mediana de 60, 97, 32 e 37. (inferência) O conjunto de desenvolvedores ativos em cada momento é bem menor que o total de classes, sobretudo em JDT.

**Deriva temporal** (fato, 18): bugs concentrados em 2005 a 2009 em BIRT (6.216 de 6.658), mais uniformes em UI e SWT, decrescentes em JDT após 2005. Authors ativos por ano: BIRT 8 a 48, UI 18 a 52, JDT 6 a 19, SWT 10 a 18 (2014 excluído por ser parcial). (inferência) O conjunto ativo muda ao longo do tempo; isso afeta o cold-start e a escolha da janela do Ramo B.

**Identidades** (fato, 06, 15): `author` mistura nomes completos e logins (em BIRT, 46 de 74 valores sem espaço; 47 authors nunca aparecem como assignee). `assignee` e `author` coincidem em 32% (BIRT), 62% (UI), 66% (JDT), 81% (SWT) das linhas, por igualdade exata de string. (inferência) é um piso, pois formatos diferentes subestimam a concordância. Strings de author idênticas em mais de um projeto: UI com JDT 13, UI com SWT 8, JDT com SWT 3, BIRT 0. (não confirmado) o número real de pessoas; falta um mapeamento login para nome (D11).

## 6. Ramo B: o que os dados oferecem

**Prioridade e severidade** (fato, 05, 18): 100% dos 30.781 bugs de `bug_commit` seguem `P<1-5> <severidade>`; sem nulos nem exceções; valor constante por bug. Na base FIXED, P3 corresponde a 91,5% (BIRT), 82,1% (UI), 81,7% (JDT), 93,3% (SWT) e severidade `normal` a 72,0%, 68,9%, 68,7%, 73,2%. `enhancement` aparece na posição de severidade (3,9% a 9,8%).

Variação entre authors com 20 ou mais bugs (fato, 18), quantis 10, 50, 90 da fração de bugs `normal`: BIRT 0,56/0,73/0,82; UI 0,56/0,71/0,80; JDT 0,56/0,68/0,75; SWT 0,65/0,73/0,85. Fração P3: BIRT 0,76/0,94/0,99; UI 0,51/0,93/1,00; JDT 0,51/0,77/0,92; SWT 0,80/0,97/1,00. (inferência) A informação de prioridade e severidade por desenvolvedor é pouco dispersa; o poder discriminativo dos dois scores deve ser baixo, a medir na modelagem. (não confirmado) se o valor é o inicial ou o final: o dump não tem histórico.

**Tempo de correção (D4)** (fato, 18), dias do primeiro commit menos `report_time`:

| Projeto | Mediana | q90 | q99 | Máx | Negativos | Acima de 365 dias |
|---|---|---|---|---|---|---|
| BIRT | 4,5 | 64 | 564 | 1.900 | 7 | 121 |
| Eclipse UI | 6,9 | 263 | 1.446 | 4.139 | 58 | 640 |
| JDT | 6,1 | 240 | 1.774 | 3.648 | 41 | 563 |
| SWT | 8,9 | 285 | 1.541 | 3.408 | 38 | 458 |

Entre authors com 20 ou mais bugs, a mediana por author (q10 a q90): BIRT 2,3 a 10,5; UI 3,8 a 43,2; JDT 4,4 a 46,2; SWT 3,9 a 50,9. (fato) Cauda muito pesada, com a mediana na ordem de dias e o q90 na ordem de meses. Esse intervalo é o único proxy disponível e inclui fila antes da atribuição e atraso até o commit (não há data de resolução nem de atribuição).

**Workload e viés** (fato, 04): todas as linhas têm commit; bugs atribuídos que nunca receberam commit não estão no dump. (inferência) O workload seria subestimado; (não confirmado) a magnitude, pois a população ausente não é mensurável aqui (D5).

**Vazamento temporal** (fato, 10, população `bug_commit` completa, corte 80/10/10 por `report_time`): de 85% a 100% dos bugs de teste têm ao menos um bug de treino com commit posterior ao seu `report_time`, em média de 6 a 41 bugs (0,2% a 0,6% do treino). (inferência) O efeito existe e é pequeno em magnitude, porque o commit costuma vir poucos dias após o report. É o que a regra D6 evita.

## 7. Ramo A: texto

(fato, 18, base FIXED) Descrição vazia: 26,4% (BIRT), 19,8% (UI), 15,0% (JDT), 22,2% (SWT); nesses casos só o `summary` está disponível. Comprimento do texto (summary mais description, em palavras separadas por espaço, summary sem o prefixo abaixo): mediana 55, 49, 56, 59; q90 145, 156, 162, 182; q99 310, 424, 364, 599; acima de 300 palavras em 1,1%, 2,2%, 1,9%, 3,4% dos bugs. (não confirmado) a razão tokens WordPiece por palavra; só ela diz quantos bugs excedem 512 tokens.

(fato, 18) **100% dos `summary` começam com "Bug <n> – " e `<n>` é o próprio `bug_id`.** A descrição não contém o id. (inferência) Se o texto for usado como está, o id entra como feature textual e é um proxy monótono do tempo de criação. Remover o prefixo é necessário antes de qualquer modelagem textual. Sem o prefixo, `summary` duplicado exato dentro do projeto: 1,1% (BIRT), 0,4% (UI), 0,3% (JDT), 0,2% (SWT).

(fato, 11, bugs distintos de `bug_commit`) Stack trace (2 ou mais linhas `at ...(Arquivo.java:N)`, heurística não validada) em 5,6% (SWT) a 11,2% (JDT) das descrições; nomes de classes Exception ou Error em 5,3% a 10,9%. Nenhum nulo SQL e `summary` nunca vazio; `summary` tem no máximo 34 palavras, contando o prefixo (tipo tinytext, limite de 255 bytes). 31 a 86 descrições por projeto têm caracteres não ASCII; (não confirmado) se houve perda de acentos na exportação original.

(fato, 12) Mensagem de commit (`log`) preenchida em 100% das linhas; mediana de 7 a 13 palavras. (fato, 13) Os CSV de features liberados têm 18 features, então φ19 a φ22 (commit) não estão neles (inferência). Nada foi implementado (D7).

## 8. Metadados como sinal do rótulo

(fato, 18) `component` como pista do author, em amostra (otimista, mesmos dados): soma por componente do author mais frequente sobre o total de pares, comparada ao Top-1 global.

| Projeto | Componentes | Componente mais frequente | Pureza em amostra | Top-1 global |
|---|---|---|---|---|
| BIRT | 52 | 22,2% | 0,407 | 0,105 |
| Eclipse UI | 36 | 93,9% | 0,202 | 0,185 |
| JDT | 25 | 74,4% | 0,349 | 0,229 |
| SWT | 27 | 98,3% | 0,233 | 0,229 |

(inferência) Em BIRT e JDT o componente carrega informação sobre o author; em Eclipse UI e SWT quase todos os bugs caem em um único componente e a pureza é quase igual ao Top-1 global, ou seja, ele pouco informa. (fato, 03) `product` não separa os projetos (de 11 a 27 valores por projeto).

## 9. Qualidade e limites do dump

- (fato) Datas até 2014-01-17; os dados têm cerca de 12 anos em relação a 2026 (ameaça de validade externa).
- (fato, 09) Intervalo report-commit negativo em 0,1% a 0,7% dos bugs (mínimo de -3.437 dias); (não confirmado) a causa (fuso, commit anterior ao bug ou vínculo errado).
- (fato, 03) Pares (bug, commit) repetidos: 359 em BIRT, 5 em UI, 6 em JDT, 13 em SWT, sempre com `files` idênticos.
- (fato, 04) Status é o final no momento da extração, constante por bug.
- (fato, 15) Dados pessoais: 4.012 nomes distintos em reporter, assignee e author (a maioria é de reporter, ou seja, usuários que abriram bugs); 0 e-mails em `summary` e `description`; nomes completos de desenvolvedores citados em 0,6% das descrições e 1,0% dos logs.

## 10. O que não foi feito

Sem treino nem avaliação de modelos; sem baselines; sem resolução de identidades (D11); sem medida de tokens WordPiece; sem métricas do Ramo B calculadas (apenas as distribuições de entrada); sem comparação numérica com resultados publicados (fora de escopo); sem figuras (só tabelas).

## 11. Perguntas em aberto para o Project (propriedades dos dados que condicionam a escolha)

Cada item é uma pergunta, não uma recomendação. Os números de apoio estão nas seções indicadas.

1. **Conjunto de classes.** Ranking sobre todos os authors do treino, só os ativos numa janela (pool de 8 a 36 na mediana, seção 5), ou algum esquema que aceite authors novos? O cold-start em teste chega a 19,8% dos bugs em Eclipse UI e 12,0% em SWT (seção 5).
2. **Cauda longa e desbalanceamento.** Top-1 do rótulo vai de 10,5% a 22,9% e o Gini de 0,70 a 0,87. Que tratamento (perda, amostragem, métrica por classe) e que protocolo de avaliação (macro contra micro, por projeto)?
3. **Múltiplos positivos.** 3,6% dos bugs têm 2 ou mais authors (D13). Como treinar o Ramo A com pares positivos múltiplos?
4. **Pares bug-desenvolvedor.** O ranking exige gerar candidatos por bug; com 41 a 138 authors e 29 mil bugs, que estratégia de amostragem de negativos?
5. **Texto.** Remoção do prefixo "Bug <id> – "; tratamento de descrição vazia (15% a 26%); truncamento a 512 tokens (a razão token por palavra não foi medida); stack traces (5% a 11%).
6. **Ramo B e o gate.** Prioridade e severidade quase constantes (P3 82% a 93%; `normal` 69% a 73%) e pouca dispersão entre desenvolvedores. O tempo de correção tem cauda pesada (mediana de dias, q90 de meses). Que normalização e que janela temporal para as métricas, e como isso afeta o aprendizado do gate e a RQ3?
7. **Corte temporal.** A regra D6 usa só bugs corrigidos antes do `report_time` do bug avaliado; qual a janela de histórico e o tratamento de desenvolvedores sem histórico (todas as métricas zero)?
8. **Metadados.** `component` informa o author em BIRT e JDT, quase nada em UI e SWT. Entra como feature do Ramo A, do Ramo B ou do gate?
9. **Identidades (D11).** O ruído de rótulo por identidades heterogêneas muda o teto de acurácia; que resolução adotar antes de qualquer experimento?
10. **Validade.** Quatro projetos Eclipse e dados de 2001 a 2014; que ameaças de validade externa e interna declarar (seção 9)?
11. **Fonte de features de commit.** φ19 a φ22 dependem da definição no artigo de Alkhazi (D7); `log` está 100% preenchido.

## Apêndice: mapa de scripts e saídas

Reexecução completa: `scripts/run_all.sh`. Saídas em `outputs/NN_*.txt`: 02 schema, 03 contagens, 04 status, 05 importance, 06 rótulo, 07 período, 08 desenvolvedores, 09 intervalo, 10 vazamento, 11 texto, 12 log de commit, 13 features do upstream, 14 filtro de Alkhazi (D9), 15 dados pessoais, 16 amostras, 18 base decidida (as seções 4 a 8 e parte da 7 acima).
