# Resultados exploratórios: tabelas medidas

Agrupado por tema. Todos os números vêm das saídas em `outputs/`, com o script indicado. Nenhum modelo foi treinado ou avaliado.

## 1. Tamanho da amostra

(fato, 03) Linhas e `bug_id` distintos por projeto, comparados aos valores da literatura:

| Projeto | Linhas `bug_commit` | Bugs `bug_commit` | Bugs `bug_and_files` | Alkhazi (2020) | DevRanker (2022) |
|---|---|---|---|---|---|
| BIRT | 8.913 | 6.820 | 4.178 | 4.952 | 4.178 |
| Eclipse UI | 13.090 | 9.424 | 6.495 | 6.670 | 6.495 |
| JDT | 10.494 | 8.620 | 6.274 | 6.528 | 6.274 |
| SWT | 8.565 | 5.917 | 4.151 | 4.266 | 4.151 |
| **Total** | **41.062** | **30.781** | **21.098** | **22.416** | **21.098** |

(fato, 03) `bug_and_files` coincide com DevRanker em **todos** os quatro projetos e no total. Nenhuma tabela reproduz os 22.416 de Alkhazi. O único filtro testado, status contendo FIXED, dá 29.383 bugs e não explica nenhum dos dois valores.

(inferência) Os 21.098 de DevRanker vêm de `bug_and_files`. O critério que gerou essa tabela a partir de `bug_commit` não está no dump.

(não confirmado) A causa da diferença de 1.318 bugs entre Alkhazi e DevRanker (D9).

## 2. Status

(fato, 04) Bugs distintos por grupo de status em `bug_commit`. O status é consistente entre as linhas de um mesmo bug (0 bugs com mais de um valor).

| Grupo | BIRT | Eclipse UI | JDT | SWT | Total |
|---|---|---|---|---|---|
| Resolução FIXED | 6.658 | 8.854 | 8.277 | 5.594 | 29.383 |
| Aberto (NEW) | 25 | 186 | 24 | 110 | 345 |
| Vazio | 48 | 86 | 89 | 56 | 279 |
| WONTFIX | 29 | 58 | 76 | 79 | 242 |
| WORKSFORME | 25 | 85 | 58 | 35 | 203 |
| INVALID | 17 | 55 | 34 | 16 | 122 |
| Aberto (ASSIGNED) | 10 | 48 | 57 | 5 | 120 |
| Aberto (REOPENED) | 5 | 51 | 4 | 20 | 80 |
| NOT_ECLIPSE | 3 | 1 | 1 | 2 | 7 |

(fato, 04) **A hipótese de que o dump contém só bugs fechados é refutada.** São 545 bugs com status aberto e 279 com status vazio, todos com commit vinculado, mais 574 com resolução diferente de FIXED.

(fato, 04) `bug_and_files` contém só resoluções `fixed` (20.934) e `wontfix` (164), em minúsculas. É um subconjunto filtrado.

(inferência) Bugs com commit vinculado e status aberto podem ser commits que citam o bug sem resolvê-lo. (não confirmado) Faltaria inspecionar `log` (D12).

## 3. Prioridade e severidade

(fato, 05) Bugs distintos por nível de prioridade:

| Prioridade | BIRT | Eclipse UI | JDT | SWT |
|---|---|---|---|---|
| P1 | 190 | 439 | 275 | 143 |
| P2 | 334 | 1.022 | 1.175 | 220 |
| P3 | 6.232 | 7.755 | 7.027 | 5.510 |
| P4 | 28 | 126 | 106 | 32 |
| P5 | 36 | 82 | 37 | 12 |

(fato, 05) Bugs distintos por nível de severidade:

| Severidade | BIRT | Eclipse UI | JDT | SWT |
|---|---|---|---|---|
| blocker | 146 | 101 | 23 | 98 |
| critical | 296 | 372 | 155 | 286 |
| major | 747 | 1.227 | 718 | 759 |
| normal | 4.890 | 6.511 | 5.933 | 4.303 |
| minor | 149 | 286 | 592 | 139 |
| trivial | 36 | 183 | 341 | 79 |
| enhancement | 556 | 744 | 858 | 253 |

(fato, 05) Concentração: P3 representa de 81,5% (JDT) a 93,1% (SWT) dos bugs, e `normal` de 68,8% (JDT) a 72,7% (SWT). A célula P3 com `normal` sozinha tem 19.391 dos 30.781 bugs.

(inferência) Com essa concentração, os scores de prioridade e de severidade terão pouca variância entre desenvolvedores. A medir na fase de modelagem.

## 4. Período

(fato, 07) Intervalo por projeto:

| Projeto | `report_time` mínimo | `report_time` máximo | `commit_time` máximo |
|---|---|---|---|
| BIRT | 2005-06-14 | 2013-12-06 | 2013-12-19 |
| Eclipse UI | 2001-10-10 | 2014-01-17 | 2014-01-17 |
| JDT | 2001-10-10 | 2014-01-03 | 2014-01-14 |
| SWT | 2002-02-19 | 2014-01-17 | 2014-01-17 |

(fato, 07) Perfil por ano: BIRT concentra entre 2005 e 2009 (6.359 dos 6.820 bugs); Eclipse UI e SWT distribuem-se de forma mais uniforme; JDT é decrescente após 2005.

(fato, 07) As datas são `DATETIME` sem fuso. (não confirmado) O fuso de origem de `report_time` em relação a `commit_time`.

## 5. Desenvolvedores

(fato, 08) Contagens e concentração, com corte cronológico de 80% por `report_time`:

| | BIRT | Eclipse UI | JDT | SWT |
|---|---|---|---|---|
| Assignees distintos | 148 | 180 | 163 | 109 |
| Assignees sem contas genéricas | 126 | 155 | 139 | 91 |
| Authors distintos | 74 | 143 | 55 | 42 |
| Mediana de bugs por assignee | 4 | 4 | 3 | 2 |
| Assignees com até 5 bugs | 80 | 95 | 100 | 80 |
| Share dos 10 maiores assignees | 43,2% | 64,3% | 78,3% | 84,7% |
| Share dos 10 maiores authors | 60,7% | 72,5% | 92,5% | 90,3% |
| Devs só após o corte (assignee) | 12 | 18 | 33 | 12 |
| Devs só após o corte (author) | 15 | 65 | 27 | 14 |
| Itens pós-corte de dev nunca visto (assignee) | 1,2% | 6,3% | 4,1% | 5,4% |
| Itens pós-corte de dev nunca visto (author) | 3,7% | 10,0% | 2,9% | 6,8% |

(fato, 08) Desenvolvedores com ao menos k itens, por `author`:

| | BIRT | Eclipse UI | JDT | SWT |
|---|---|---|---|---|
| >= 1 | 74 | 143 | 55 | 42 |
| >= 10 | 47 | 44 | 22 | 21 |
| >= 50 | 29 | 26 | 15 | 14 |
| >= 100 | 21 | 20 | 12 | 11 |

(inferência) SWT e JDT têm espaço de classes pequeno (42 e 55 authors), consistente com a observação da literatura citada no CLAUDE.md. O número de desenvolvedores por projeto de Alkhazi não foi verificado.

## 6. Intervalo report-commit, em dias

(fato, 09) Por bug distinto, usando o primeiro commit:

| Projeto | n | Negativos | < 1h | q25 | Mediana | q75 | q95 | q99 | Máximo | > 365d |
|---|---|---|---|---|---|---|---|---|---|---|
| BIRT | 6.820 | 8 | 405 | 0,8 | 4,7 | 18,4 | 147,5 | 639,6 | 1.900,4 | 141 |
| Eclipse UI | 9.424 | 62 | 1.218 | 0,7 | 6,9 | 57,3 | 545,8 | 1.459,4 | 4.138,5 | 698 |
| JDT | 8.620 | 42 | 569 | 1,0 | 6,2 | 46,2 | 567,3 | 1.763,7 | 3.647,5 | 596 |
| SWT | 5.917 | 43 | 425 | 1,1 | 9,2 | 66,0 | 648,7 | 1.550,2 | 3.408,1 | 508 |

(fato, 09) Os 158 valores negativos no nível de linha têm mediana próxima de zero e mínimo de -3.437 dias, ou seja, a maioria é de magnitude muito pequena com poucos casos extremos.

## 7. Vazamento temporal no Ramo B

(fato, 10) Corte 80/10/10 por `report_time`, todos os bugs de teste, sem amostragem. Bugs de treino com commit posterior ao `report_time` do bug de teste:

| População | Projeto | Treino | Teste | Média de bugs vazando | % médio do treino | Testes com vazamento |
|---|---|---|---|---|---|---|
| `bug_commit` | BIRT | 5.456 | 682 | 10,8 | 0,20% | 95,5% |
| `bug_commit` | Eclipse UI | 7.539 | 943 | 25,2 | 0,33% | 99,9% |
| `bug_commit` | JDT | 6.896 | 862 | 39,5 | 0,57% | 98,1% |
| `bug_commit` | SWT | 4.733 | 592 | 14,8 | 0,31% | 89,9% |
| `bug_and_files` | BIRT | 3.342 | 418 | 6,2 | 0,19% | 95,5% |
| `bug_and_files` | Eclipse UI | 5.196 | 650 | 12,9 | 0,25% | 100,0% |
| `bug_and_files` | JDT | 5.019 | 628 | 30,3 | 0,60% | 97,6% |
| `bug_and_files` | SWT | 3.320 | 416 | 7,0 | 0,21% | 85,3% |

(fato, 10) Para o bug de teste mais antigo, os bugs de treino com primeiro commit posterior a ele são 20 (BIRT), 52 (Eclipse UI), 92 (JDT) e 37 (SWT).

(inferência) O vazamento está presente em quase todo bug de teste, mas é pequeno em magnitude, porque o commit costuma ocorrer poucos dias após o report. (não medido) O efeito nas métricas do Ramo B em si, que depende do cálculo a ser definido.

## 8. Texto dos bug reports

(fato, 11) Por bugs distintos. Nenhum nulo SQL e `summary` nunca vazio.

| Projeto | Bugs | `description` vazia | Palavras em `summary` (mediana) | Palavras em `description` (mediana) | q90 | q99 | > 300 palavras | Stack trace | Exception/Error |
|---|---|---|---|---|---|---|---|---|---|
| BIRT | 6.820 | 26,3% | 12 | 46 | 136 | 301 | 1,0% | 6,1% | 8,4% |
| Eclipse UI | 9.424 | 19,9% | 11 | 41 | 149 | 421 | 2,1% | 10,0% | 9,4% |
| JDT | 8.620 | 15,1% | 11 | 48 | 154 | 358 | 1,8% | 11,2% | 10,9% |
| SWT | 5.917 | 22,1% | 10 | 51 | 176 | 594 | 3,4% | 5,6% | 5,3% |

(fato, 11) O comprimento está em palavras separadas por espaço. (não confirmado) A razão entre tokens WordPiece do BERT e palavras, que será maior que 1.

(fato) Stack trace é definido como duas ou mais linhas no formato `at pacote.Classe(Arquivo.java:N)`, e Exception/Error como classe `java.`, `org.` ou `javax.` terminando nesses sufixos. **São heurísticas do executor, não validadas manualmente.**

(fato, 11) De 31 a 86 descrições por projeto têm caracteres não ASCII, e o arquivo SQL tem 79 linhas com esses caracteres.

## 9. Arquivos de features de Alkhazi

(fato, 13) `ExtractedFeatures.zip` tem 6 CSV sem cabeçalho (abordagem nova e anterior, folds 1 a 3), cada um com 171.536 linhas, estruturadas em 1.208 queries de 142 candidatos. São 890 `bug_id` distintos. (inferência, sem documentação nem cabeçalho) O layout é qid, `bug_id`, nome do desenvolvedor, features e rótulo binário.

(fato, 13) As 14 features da abordagem anterior são idênticas às 14 primeiras das 18 da nova, e o rótulo coincide.

(fato, 13) Cobertura: os 890 bugs estão todos em `eclipse_platform_ui.bug_commit`, isto é 9,4% dos 9.424, e 622 estão em `bug_and_files`. Os outros três projetos têm no máximo coincidências de `bug_id` (3 em JDT, 8 em SWT, 0 em BIRT), com 10 ids ambíguos entre projetos.

(fato, 13) Alinhamento do rótulo com o dump, por fold:

| Fold | Positivos | Positivo é `author` do dump | Positivo é o `assignee` | Devs distintos entre positivos |
|---|---|---|---|---|
| 1 | 1.196 | 1.196 (100%) | 823 (68,8%) | 91 |
| 2 | 1.208 | 145 (12,0%) | 116 | 21 |
| 3 | 1.208 | 159 (13,2%) | 121 | 18 |

(fato, 13) Os folds 2 e 3 repetem a sequência de `bug_id` do fold 1 mas quase não alinham com o dump, e seus positivos concentram-se em 18 a 21 desenvolvedores, um deles com 40%. (inferência) A coluna `bug_id` pode ter sido copiada do fold 1 na exportação. (não confirmado) Seria preciso o código de geração ou contato com os autores.

(fato, 13) 12 queries do fold 1 não têm positivo. Linhas com todas as 18 features em zero: 36,6% no fold 1, 58,5% no fold 2, 60,4% no fold 3.

(fato, 13) `SVMrank_Models.zip` traz os 6 `.dat` de entrada, com as mesmas linhas e qid dos CSV e rank 1 ou 2, e 4 modelos SVM-light V6.20 de kernel linear, treinados nos folds 2 e 3 das duas abordagens. Não há modelo para o fold 1. (não confirmado) O significado do campo "number of training documents", entre 48 e 54, muito menor que as 1.208 queries.

(fato, 13) O split **não é recuperável** a partir desses arquivos: nada define quais bugs pertencem a cada fold nem a data de corte. Por isso o teste de sanidade não foi tentado (D8).
