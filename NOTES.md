# NOTES: análise exploratória (HybridBugRank)

Data da execução: 2026-10-06. Rótulos: **(fato)** medido pelo script citado; **(inferência)**; **(não confirmado)**. Saídas completas em `outputs/NN_*.txt`, geradas por `scripts/NN_*.py`. Reexecução do zero: `scripts/run_all.sh` (cerca de 45 s).

## Proveniência do dump

- Arquivo: `SQL_BugDatabase_Dump.7z`, 16.033.854 bytes, SHA-256 `ae1f9670e90c71b35090aed9ecf2db021c1385a2e317651a83225414f3d3b19d`.
- (fato) O arquivo veio de um `git clone` do repositório, não de um download avulso. O mtime local é 2026-10-06 13:46; o commit que o adicionou é de 2019-02-09. Data de aquisição registrada: 2026-10-06.
- (fato) O README diz "dataset.zip" e "dataset folder"; o arquivo é `.7z` e contém um único arquivo, `SQL_BugDatabase_Dump.sql` (167.009.039 bytes), sem pasta. Inconsistência registrada.
- Cópia somente leitura em `data/raw/`; extração em `data/interim/` (ambos fora do git).

## Etapa 1 e 2: restauração, schema e identificação de projeto (scripts 01, 02, 03)

**Feito.** Inspecionado o cabeçalho; construído um parser próprio que carrega o dump em SQLite (`data/interim/bugs.sqlite`, tabelas `<banco>__<tabela>`).

- (fato) SGBD exigido: MySQL, `mysqldump 10.13 Distrib 8.0.12`, servidor 8.0.12, plataforma Win64. Engines MyISAM (e InnoDB nas tabelas extras de `eclipse_platform_ui`), `DEFAULT CHARSET=latin1` com colunas de texto declaradas utf8.
- (fato) O dump cria 7 bancos: `tomcat, birt, aspectj, api_descriptions, eclipse_platform_ui, jdt, swt`. São 35 tabelas ao todo (listadas em `outputs/02_schema.txt`).
- (fato) Validação do parser: toda tupla INSERT tem o número de colunas do CREATE TABLE e nenhum byte ficou sem consumir; o `AUTO_INCREMENT` do dump bate com as contagens (ex.: JDT `bug_commit` 10.494 linhas contra `AUTO_INCREMENT=10495`). Limite: não foi feita comparação com uma restauração real em MySQL (não confirmado que valores de campos, como strings com escapes raros, sejam idênticos).
- (fato) Schema de `bug_commit`: as 16 colunas, tipos e ordem do README conferem nos quatro projetos. Nenhuma divergência. Não há coluna de data de resolução nem de atribuição.
- (fato) Além de `bug_commit`, cada projeto tem `bug_and_files` (1 linha por bug, com texto stemizado, `commit`, `files`, timestamps em float, sem assignee/author/importance/log) e `file_history`. `eclipse_platform_ui` tem ainda `appcommits`, `commitfilechanges`, `migrationmapping` (vazia), `repositories`, `validationtype`. `api_descriptions` tem descrições de API por projeto.
- (fato) Identificação do projeto: **pelo banco**, não por coluna. `bug_commit` não tem coluna de projeto. `product` não separa: o produto majoritário cobre 98,6% (BIRT), 85,8% (UI, "Platform"), 93,9% (JDT) e 99,1% (SWT, "Platform") dos bugs, e há de 11 a 27 valores de `product` por projeto.
- (fato) Alguns `bug_id` aparecem em mais de um banco (74 entre UI e JDT, 43 UI e SWT, 25 JDT e SWT, 2 BIRT com JDT e SWT). A chave do bug deve ser (projeto, `bug_id`).

**Contagens (script 03).**

| Projeto | linhas bug_commit | bugs distintos bug_commit | bugs `bug_and_files` | Alkhazi | DevRanker |
|---|---|---|---|---|---|
| BIRT | 8.913 | 6.820 | 4.178 | 4.952 | 4.178 |
| Eclipse UI | 13.090 | 9.424 | 6.495 | 6.670 | 6.495 |
| JDT | 10.494 | 8.620 | 6.274 | 6.528 | 6.274 |
| SWT | 8.565 | 5.917 | 4.151 | 4.266 | 4.151 |
| Total | 41.062 | 30.781 | 21.098 | 22.416 | 21.098 |

- (fato) `bug_and_files` tem exatamente os valores de DevRanker por projeto (21.098 no total) e é subconjunto de `bug_commit` (todos os bug_id estão contidos). Não reproduz os valores de Alkhazi.
- (fato) `bug_commit` tem 30.781 bugs distintos (1,22 a 1,45 linhas por bug; máximo 142 linhas em um bug). Há pares (bug_id, commit) repetidos (359 em BIRT, 5 UI, 6 JDT, 13 SWT), sempre com `files` idênticos.
- (inferência) A origem dos 21.098 de DevRanker parece ser `bug_and_files`; o critério de filtro que gerou `bug_and_files` a partir de `bug_commit` não está no dump.
- (não confirmado) A causa da diferença 22.416 vs 21.098. O único filtro testado (status com FIXED, 29.383 bugs) não explica; falta o critério de Alkhazi (INVALID, desenvolvedores ativos).
- Muda para o desenho: a população-base (30.781 em `bug_commit` ou 21.098 em `bug_and_files`) precisa ser decidida.

## Etapa 3: status (script 04)

- (fato) Em `bug_commit` (bugs distintos): 29.383 com resolução FIXED (RESOLVED, VERIFIED ou CLOSED), 574 com outra resolução (WONTFIX 242, WORKSFORME 203, INVALID 122, NOT_ECLIPSE 7), 545 abertos (NEW 345, ASSIGNED 120, REOPENED 80) e 279 com status vazio. O status é consistente por bug.
- (fato) A hipótese "só bugs fechados" é refutada para `bug_commit`. Em `bug_and_files` só há `fixed` e `wontfix` (21.098: 20.934 fixed, 164 wontfix).
- (fato) Nenhuma linha de `bug_commit` tem `commit` vazio.
- (inferência) Bugs atribuídos que nunca tiveram commit não estão no dump e o workload seria subestimado (limitação 2). (não confirmado) magnitude: o dump não traz essa população.

## Etapa 4: `importance` (script 05)

- (fato) 100% dos 30.781 bugs seguem `P<1-5> <severidade>` (regex `^P([1-5]) (blocker|critical|major|normal|minor|trivial|enhancement)$`). Zero nulos, vazios ou fora do padrão. Separação por parsing sem perda. O valor é constante por bug.
- (fato) Distribuição concentrada: P3 representa 81% a 93% e "normal" 69% a 73% dos bugs por projeto. "enhancement" ocupa a posição de severidade.
- (não confirmado) Se o valor é o inicial ou o final: o dump não tem histórico.
- Muda para o desenho: os dois scores do Ramo B são viáveis em termos de dado; a baixa variância é um risco a medir depois.

## Etapa 5: rótulo do desenvolvedor (script 06)

- (fato) `assignee == author` (string exata), nível linha: BIRT 32,2%, UI 61,8%, JDT 65,6%, SWT 81,1%.
- (fato) Nível bug, entre bugs com assignee não genérico, o assignee é um dos authors do bug em 34,1% (BIRT), 71,6% (UI), 77,0% (JDT), 88,0% (SWT).
- (fato) Os identificadores têm formatos distintos: BIRT tem 46 de 74 authors sem espaço (parecem logins) e 47 authors que nunca aparecem como assignee. A igualdade de strings subestima a concordância real.
- (fato) Contas genéricas (regex `inbox|triaged|^birt-`, heurística minha, não validada): 224 bugs em BIRT, 845 UI, 1.153 JDT, 183 SWT (3,1% a 13,4%). Mais frequentes: `Project Inbox` e `Platform UI Triaged` (UI), `JDT-UI-Inbox` e `JDT-Text-Inbox` (JDT), `Platform-SWT-Inbox` (SWT). Listas em `outputs/06_label.txt`.
- (não confirmado) Se `author` é quem corrigiu e o mapeamento login para nome.
- Muda para o desenho: a escolha do rótulo depende de resolver identidades (DECISIONS 2 e 10).

## Etapa 6: período (script 07)

- (fato) `report_time` vai de 2001-10-10 (UI, JDT) e 2005-06-14 (BIRT) até 2014-01-17. O maior `commit_time` é 2014-01-17.
- (fato) Volume por ano: BIRT concentra 2005 a 2009 (6.359 de 6.820 bugs); UI e SWT são mais uniformes; JDT é decrescente após 2005. O 80º percentil de `report_time` cai em 2009-03 (BIRT), 2010-03 (UI), 2007-11 (JDT), 2009-05 (SWT).
- (inferência) Dados com 12 anos de idade em relação a 2026: ameaça de validade externa. Fuso de origem de `report_time` e `commit_time` não confirmado.

## Etapa 7: desenvolvedores (script 08)

- (fato) Desenvolvedores distintos (assignee / author): BIRT 148 / 74, UI 180 / 143, JDT 163 / 55, SWT 109 / 42. O assignee inclui contas genéricas (sem elas: 126, 155, 139, 91).
- (fato) Cauda longa: a mediana de bugs por assignee é 2 a 4; 80 a 100 assignees por projeto têm até 5 bugs. Top 10 assignees cobrem 43% (BIRT), 64% (UI), 78% (JDT), 85% (SWT) dos bugs.
- (fato) Desenvolvedores que só aparecem após o corte de 80%: 12 a 33 por projeto (assignee) e 14 a 65 (author). Itens pós-corte de desenvolvedores nunca vistos: 1,2% a 6,3% (assignee) e 2,9% a 10,0% (author).
- (inferência) SWT e JDT têm poucos authors (42 e 55), o que é consistente com a literatura citada no CLAUDE.md e deve ser declarado como limitação.

## Etapa 8: intervalo report-commit (script 09)

- (fato) Mediana por bug (primeiro commit) de 4,7 dias (BIRT), 6,9 (UI), 6,2 (JDT), 9,2 (SWT); q95 de 148 a 649 dias; máximos de 1.900 a 4.138 dias.
- (fato) Negativos: 8 (BIRT), 62 (UI), 42 (JDT), 43 (SWT) bugs por primeiro commit (0,1% a 0,7%); mínimo de -3.437 dias; a maioria é de magnitude muito pequena. Entre 405 e 1.218 bugs por projeto têm intervalo < 1 hora.
- (não confirmado) Causa dos negativos (fuso, commit anterior ao bug, vínculo errado).
- Confirma a limitação 1: não há data de resolução ou de atribuição; o intervalo é o único proxy e mistura fila, correção e atraso até o commit.

## Etapa 9: vazamento temporal (script 10)

Corte 80/10/10 por `report_time`, todos os bugs de teste (sem amostragem, logo sem semente).

- (fato) De 85% a 100% dos bugs de teste têm ao menos um bug de treino com commit posterior ao seu `report_time`. Em média, de 6 a 41 bugs por bug de teste (0,2% a 0,6% do treino). Para o primeiro bug de teste: 20 a 92 bugs de treino com primeiro commit posterior.
- (inferência) O vazamento existe e é pequeno em magnitude porque o commit costuma vir poucos dias após o report. Não medido: o efeito nas métricas do Ramo B.

## Etapa 10: texto (script 11)

- (fato) Nenhum nulo SQL; `summary` nunca vazio; `description` vazia em 26,3% (BIRT), 19,9% (UI), 15,1% (JDT), 22,1% (SWT) dos bugs.
- (fato) Mediana de palavras: summary 10 a 12; description 41 a 51 (q90 de 136 a 176; q99 de 301 a 594). Descrições com mais de 300 palavras: 1,0% a 3,4%.
- (fato, heurística não validada) stack trace (2 ou mais linhas `at ...(Arquivo.java:N)`) em 5,6% (SWT) a 11,2% (JDT) das descrições; classe Exception/Error em 5,3% a 10,9%.
- (fato) 31 a 86 descrições por projeto têm caracteres não ASCII. (não confirmado) se houve perda de acentos na exportação original (colunas utf8 em tabelas com DEFAULT CHARSET latin1).
- (não confirmado) Razão entre tokens WordPiece e palavras.

## Etapa 11: mensagens de commit (script 12)

- (fato) `log` preenchido em 100% das linhas e dos bugs nos quatro projetos (41.062 linhas); `files` preenchido em 99,9% a 100%. Mediana de 7 a 13 palavras por mensagem.
- Nada implementado. (não confirmado) O que φ19 a φ22 exigem.

## Etapa 12: D8, inspeção de `ExtractedFeatures.zip` e `SVMrank_Models.zip` (script 13)

Aquisição: ambos vieram do `git clone` (mtime 2026-10-06; commits de 2019). SHA-256 `ExtractedFeatures.zip` = `729430abeea966c455529d52cd5b6ff20f5ccc755c1bcd93621170837f21421a` (21.161.853 bytes); `SVMrank_Models.zip` = `9f42557c94c52149f513a70bbcbac6d5700385e6e60b15e6e4ad006d1285e737` (23.993.991 bytes). Extraídos em `data/interim/zips/` (fora do git). Não foi treinado nem avaliado nenhum modelo.

**Conteúdo (fato).**
- `ExtractedFeatures`: 6 CSV sem cabeçalho (`OurNewApproach` e `PreviousApproach`, `Fold1..3`), todos com 171.536 linhas. Colunas por linha: 3 identificadores, 18 features (14 em `PreviousApproach`) e uma coluna final em {0,1}. Leitura do layout como qid, bug_id, nome do desenvolvedor e rótulo é inferência minha (não há documentação nem cabeçalho). As 14 features de `PreviousApproach` são idênticas às 14 primeiras de `OurNewApproach`, e o rótulo também.
- Estrutura: 1.208 queries por fold, 142 candidatos por query (171.536 = 1.208 x 142), 890 `bug_id` distintos. Faixas de qid: 1 a 1378 (fold 1), 1379 a 2714 (fold 2), 2715 a 3986 (fold 3), com lacunas. A sequência de `bug_id` por query é idêntica nos três folds. 96,9% dos bugs têm tantas queries quanto linhas em `bug_commit` (inferência: uma query por par bug-commit).
- `SVMrank_Models`: os 6 `.dat` de entrada (mesmas linhas e qid dos CSV, rank 1 ou 2, nome do desenvolvedor como comentário) e 4 modelos SVM-light V6.20 (`TrainedOnFold2` e `TrainedOnFold3`, nas duas abordagens), todos com kernel linear, índice máximo de feature 19 (nova) e 15 (anterior). Não há modelo treinado no fold 1. Não confirmado: o significado de "training documents" (48 a 54), muito menor que 1.208 queries.
- Ordem das queries: decrescente pelo último `commit_time` do bug no dump (fato, fold 1).

**Mapeamento para o dump (fato).**
- Os 890 bugs existem todos em `eclipse_platform_ui.bug_commit` (890 de 9.424, 9,4%); 622 estão em `bug_and_files`. Os outros três projetos têm no máximo coincidências de `bug_id` (3 JDT, 8 SWT, 0 BIRT; 10 ids ambíguos entre projetos). Os CSV cobrem só Eclipse UI.
- Os 142 candidatos são quase o conjunto de `author` de UI no dump (139 dos 143 authors); só 55 coincidem com algum `assignee` (de 180).
- Fold 1: o desenvolvedor positivo é um dos `author` do bug no dump em 1.196 de 1.196 queries com positivo (100%); é igual ao `assignee` em 823 (68,8%). 12 queries do fold 1 não têm positivo. Inferência: o rótulo usado é `author` do commit, e as 12 queries sem positivo têm o autor fora dos candidatos.
- Folds 2 e 3: a sequência de `bug_id` é a mesma do fold 1, mas o positivo está entre os `author` do bug no dump em apenas 145 de 1.208 (12,0%) e 159 de 1.208 (13,2%). Os positivos se concentram em 21 e 18 desenvolvedores (um deles com 40%), contra 91 no fold 1 (maior com 22,4%). Testei deslocamentos de posição de -2 a +2 e o casamento não melhora (fora do script, exploração descartável).
- Linhas com as 18 features todas zero: 36,6% (fold 1), 58,5% (fold 2) e 60,4% (fold 3).

**Leitura (rotulada).**
- (inferência) Os folds 2 e 3 não são alinháveis ao dump pela coluna `bug_id` (talvez a coluna tenha sido copiada do fold 1 na exportação). Não confirmado; seria preciso o código de geração ou os autores.
- (fato) Os CSV têm 18 features, não 22. (inferência) Logo φ19 a φ22 (mensagens de commit) não estão nos arquivos liberados; o que as features 15 a 18 são não está confirmado.
- Condição do CLAUDE.md para o teste de sanidade: "as linhas mapearem para `bug_id` e o split ser recuperável". Mapeamento: sim para o fold 1 (Eclipse UI), não para os folds 2 e 3. Split recuperável: **não**; não há definição de quais bugs pertencem a cada fold, nem a data de corte, e os folds 2 e 3 contradizem o dump. Por isso **o teste de sanidade não foi tentado** (treino e avaliação estão fora do escopo da fase de qualquer forma).
- Muda para o desenho: uma comparação numérica com os resultados do ICPC 2019 não é viável a partir destes arquivos. O fold 1 serve apenas como corroboração independente de que `author` é o rótulo de Alkhazi, restrita a Eclipse UI.

## Etapa 13: verificação do SQLite contra uma restauração real em MySQL (script 14)

- (fato) Docker ficou disponível em 2026-10-13. Imagem `mysql:8.0.12` (digest `sha256:8fdc47e9ccb8112a62148032ae70484e3453b628ab6fe02bccf159e2966b750e`), contêiner `bugdump-mysql` (porta 127.0.0.1:33306, `--character-set-server=latin1`, dump montado somente leitura). O contêiner `jellyfin` que já existia não foi tocado.
- (fato) Comando: `mysql -uroot < /dump/SQL_BugDatabase_Dump.sql`. Restauração concluída sem nenhum erro em cerca de 76 s.
- (fato) `14_verify_mysql.py`: para cada uma das 35 tabelas, contagem de linhas e SHA-256 do conteúdo (hash por linha, ordenado) no MySQL real e no SQLite. Resultado: **35 de 35 tabelas idênticas**, 0 divergentes. Detalhe por tabela em `outputs/14_verify_mysql.txt`.
- Limites da comparação (fato): floats comparados com 6 casas decimais; datetimes comparados como texto `YYYY-MM-DD HH:MM:SS`; leitura via conexão utf8mb4. A identidade vale entre o que o MySQL guardou e o que o meu parser leu; não diz nada sobre perdas anteriores ao dump.
- (não confirmado) Se houve perda de acentos na exportação original (colunas utf8 em tabelas com DEFAULT CHARSET latin1). Tanto o MySQL quanto o parser leram os mesmos caracteres, então a perda, se existe, está no próprio arquivo.
- Muda para o desenho: as análises 02 a 13 feitas sobre o SQLite valem para o MySQL; nenhum número precisa ser refeito. O script 14 não está em `run_all.sh` porque exige o contêiner ativo. Dependência instalada: `pymysql`.
- Operação: contêiner parado ao final (`docker stop bugdump-mysql`); para reusar, `docker start bugdump-mysql` (os dados ficam no contêiner). Senha de root `local_only_pw` é local, exposta só em 127.0.0.1.

**Segunda verificação, independente desta.** Existe no repositório um par `scripts/01b_verify_mysql.py` e `outputs/01b_verify_mysql.txt` que não foi produzido nesta sessão (mtime 2026-10-14 00:43 e 00:46). (fato, por inspeção dos arquivos e de `docker ps`) Ele compara o mesmo SQLite com um contêiner distinto, `bugtriage-mysql`, imagem `mysql:8.0`, e sua saída declara servidor 8.0.46. O método também difere: MD5 por linha via `docker exec mysql`, comparando multiconjuntos de hashes e **excluindo as colunas float/double** (duas por tabela `bug_and_files`), o que permite contar linhas divergentes em vez de só comparar um hash agregado. A saída reporta 35 de 35 tabelas com hashes idênticos e 0 linhas divergentes no total.

(fato) Não executei esse script; o que afirmo acima vem da leitura do código e da saída gravada. (inferência) As duas verificações são independentes em servidor (8.0.12 e 8.0.46), em método (SHA-256 agregado com floats a 6 casas, e MD5 por linha sem floats) e em contêiner, e chegam à mesma conclusão, o que é uma corroboração mais forte do que qualquer uma isolada. A cobertura é complementar: o script 14 compara as colunas float e o 01b conta as linhas divergentes.

(pendência) Há colisões de numeração a resolver, todas decisão do pesquisador. Primeira: `01b_verify_mysql` e `14_verify_mysql` cumprem a mesma finalidade, e `01b` não entra em `run_all.sh` porque não casa com os globs `0[2-9]_*.py` nem `1[0-3]_*.py`. Segunda: existe `scripts/14_alkhazi_filter.py` (mtime 2026-10-14 00:46), que disputa o número 14 com `14_verify_mysql.py`. (fato) Esse script faz uma busca em grade de filtros sobre `bug_commit` para tentar reproduzir os tamanhos de Alkhazi (D9) e **não possui saída em `outputs/`**, ou seja, não foi executado. Não o executei, para não gerar evidência sobre uma decisão aberta a partir de um script cuja versão final não me foi confirmada.

## Etapa 14: infraestrutura de registro para a dissertação (2026-10-14)

**Feito.** Configurada a captura automática do que é feito no projeto e um agente que a transforma em material de escrita. Nenhuma análise nova; nenhum número desta etapa.

Componentes:

- `scripts/registro_sessao.sh`: captura bruta e mecânica, sem julgamento. Nos hooks `SessionStart` e `SessionEnd` de `.claude/settings.json`, grava em `registro/sessoes.log` (append-only) o intervalo de HEAD, os commits novos, os arquivos tocados desde o início da sessão e o `git status` final. Testado por pipe com JSON sintético; sai sempre com 0 para nunca interromper a sessão.
- `.claude/agents/registro-dissertacao.md`: agente que lê o log bruto, o git e as saídas de `outputs/`, e escreve em `NOTES.md`, `DECISIONS.md` e `dissertacao/`. A definição herda as regras do CLAUDE.md: rotular fato, inferência e não confirmado; não decidir método; não inventar; não gravar nomes de desenvolvedores; não fazer commit.
- `.claude/commands/registro.md`: comando `/registro` para invocar o agente.
- `dissertacao/`: material agrupado por seção da dissertação (`metodologia.md`, `resultados.md`, `ameacas_validade.md`, `caminhos_descartados.md`, `proveniencia.md`), semeado nesta etapa com as etapas 1 a 13 reorganizadas. `NOTES.md` segue cronológico e `dissertacao/` é por seção, então um mesmo fato aparece nos dois com recortes diferentes; os números devem coincidir.

**Decisões do pesquisador registradas nesta etapa** (respostas às alternativas apresentadas): manter `NOTES.md` e `DECISIONS.md` como registro primário e acrescentar material por seção; captura automática por hook com curadoria sob demanda; registrar também os caminhos descartados, em seção separada.

**Itens novos em `dissertacao/caminhos_descartados.md`**: além das hipóteses refutadas já em `NOTES.md`, ficaram registrados os erros do executor corrigidos no caminho (C7 a C9), entre eles a afirmação errada de que o dump era ASCII puro.

**Pendência operacional**: hooks e definições de agente são carregados no início da sessão, e `.claude/` não existia quando esta sessão começou. A captura automática e o `/registro` passam a valer **na próxima sessão**. Nada a fazer além de reiniciar.

**Não confirmado**: o comportamento do hook `SessionEnd` em encerramentos abruptos (queda do terminal, `kill`). O pipe-test cobre a invocação normal.

## Itens que precisam do pesquisador

Ver `DECISIONS.md`. Pendências desta etapa: população-base, resolução de identidades, tratamento de contas genéricas e de bugs não fechados, e teste de sanidade com os arquivos de features (D8 inspecionado e encerrado; ver Etapa 12).

## Observações operacionais

- `outputs/` contém só contagens agregadas. Nenhum nome de desenvolvedor aparece; a lista de contas genéricas contém endereços de caixas de componente (ex.: `Birt-Data-inbox@eclipse.org`), que não são pessoais.
- Dependências instaladas (rede só para isso): `py7zr`, `pandas`, `numpy` em `.venv/`.
