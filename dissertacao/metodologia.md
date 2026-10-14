# Metodologia: material de escrita

Fonte de cada afirmação indicada entre parênteses pelo script (`scripts/NN_*.py`, saída em `outputs/NN_*.txt`).

## 1. Ambiente de restauração

(fato, 02) O dump é um `mysqldump 10.13` gerado por MySQL 8.0.12 em Win64, declarando servidor 8.0.12. As tabelas usam engine MyISAM, exceto as tabelas auxiliares de `eclipse_platform_ui`, que usam InnoDB. O charset declarado das tabelas é `latin1`, com as colunas de texto declaradas `utf8`.

(fato, 14) O dump foi restaurado em MySQL 8.0.12 em contêiner Docker, sem erros, em cerca de 76 segundos. O ambiente de trabalho das análises é um SQLite construído por um parser próprio (`01_restore.py`), validado contra essa restauração: as 35 tabelas têm a mesma contagem de linhas e o mesmo hash de conteúdo nos dois. A comparação usou hash por linha ordenado, com floats a 6 casas decimais e datetimes como texto.

(não confirmado) Se a exportação original perdeu acentos ou caracteres. O MySQL e o parser leram os mesmos bytes, logo uma perda, se existe, é anterior ao arquivo.

## 2. Estrutura do dump

(fato, 02) O dump cria 7 bancos (`tomcat`, `birt`, `aspectj`, `api_descriptions`, `eclipse_platform_ui`, `jdt`, `swt`) e 35 tabelas. Cada projeto é um banco separado, com três tabelas em comum:

- `bug_commit`: as 16 colunas declaradas no README do dataset, na mesma ordem, nos quatro projetos usados. Nenhuma divergência.
- `bug_and_files`: uma linha por `bug_id`, com texto stemizado (`bag_of_word_stemmed`, `summary_stemmed`, `description_stemmed`) e timestamps em float, mas **sem** `assignee`, `author`, `importance`, `component`, `product`, `reporter`, `commit_time` e `log`.
- `file_history`: histórico de arquivo por `doc_id`.

(fato, 02) `eclipse_platform_ui` tem ainda `appcommits` (28.621 linhas), `commitfilechanges` (79.022), `repositories` (1), `validationtype` (3) e `migrationmapping` (vazia). O banco `api_descriptions` traz descrições de API por projeto.

(fato, 02) **Não existe coluna de data de resolução nem de data de atribuição** em `bug_commit`. Esta é a origem da limitação 1 da seção 5 do CLAUDE.md.

## 3. Identificação do projeto

(fato, 03) A pertinência de um bug a BIRT, Eclipse UI, JDT ou SWT é dada **pelo banco de dados**, não por coluna. `bug_commit` não tem coluna de projeto, e `product` não separa: o produto majoritário cobre 98,6% dos bugs em BIRT, 85,8% em Eclipse UI (`Platform`), 93,9% em JDT e 99,1% em SWT (`Platform`), e há de 11 a 27 valores distintos de `product` por projeto.

(fato, 03) Alguns `bug_id` aparecem em mais de um banco: 74 entre Eclipse UI e JDT, 43 entre Eclipse UI e SWT, 25 entre JDT e SWT, 2 entre BIRT e cada um de JDT e SWT. **A chave de um bug precisa ser o par (projeto, `bug_id`).**

AspectJ e Tomcat estão no dump mas ficam fora deste trabalho, por decisão de escopo.

## 4. Grão e população-base

(fato, 03) O grão de `bug_commit` é o par bug-commit: de 1,22 a 1,45 linhas por bug, com máximo de 142 linhas em um único bug. Há pares (`bug_id`, `commit`) repetidos (359 em BIRT, 13 em SWT, 6 em JDT, 5 em Eclipse UI), sempre com `files` idênticos. Nenhuma linha tem `commit` vazio.

(fato, 03) `bug_and_files` tem exatamente uma linha por `bug_id` e é subconjunto de `bug_commit`.

Toda contagem deve distinguir linhas de `bug_id` distintos. A escolha da população-base entre as duas tabelas está aberta (D10).

## 5. Campo `importance` e os dois scores do Ramo B

(fato, 05) Os 30.781 bugs distintos de `bug_commit` seguem, sem exceção, o padrão `P<1-5> <severidade>` com um espaço, conforme a regex `^P([1-5]) (blocker|critical|major|normal|minor|trivial|enhancement)$`. Zero nulos, zero vazios, zero fora do padrão. O valor é constante entre as linhas de um mesmo bug.

(fato, 05) **A separação em prioridade e severidade por parsing é possível sem perda.** Isso viabiliza, em termos de dado, o Developer Priority Score e o Developer Severity Score do Ramo B.

(fato, 05) `enhancement` ocupa a posição de severidade da string. (inferência, por conhecimento do Bugzilla externo ao dump) é um valor de severidade, não um tipo de bug.

(não confirmado) Se o valor registrado é o inicial ou o final: o dump não traz histórico de alterações.

## 6. Rótulo do desenvolvedor

(fato, 06) Concordância entre `assignee` e `author`, por linha bug-commit: 32,2% em BIRT, 61,8% em Eclipse UI, 65,6% em JDT, 81,1% em SWT. No nível do bug, restringindo a bugs cujo assignee não é conta genérica, o assignee é um dos authors do bug em 34,1%, 71,6%, 77,0% e 88,0%.

(fato, 06) Os dois campos usam formatos de identificador diferentes. Em BIRT, 46 dos 74 authors não têm espaço no nome (parecem logins) e 47 authors nunca aparecem como assignee. A igualdade de strings, portanto, **subestima** a concordância real.

(fato, 13) Corroboração independente: no fold 1 dos arquivos de features liberados por Alkhazi, o desenvolvedor rotulado como positivo é um dos `author` do bug no dump em 1.196 de 1.196 queries com positivo, e igual ao `assignee` em 68,8%. Os 142 candidatos por query são quase o conjunto de authors de Eclipse UI no dump (139 dos 143). Restrito a Eclipse UI.

(inferência) O rótulo de Alkhazi é o `author` do commit. A escolha para este trabalho permanece aberta (D2), e depende de resolver identidades (D11).

## 7. Contas genéricas e de triagem

(fato, 06) Aplicando a regex `inbox|triaged|^birt-` sobre `assignee`, são classificados como genéricos de 3,1% (SWT) a 13,4% (JDT) dos bugs: 224 em BIRT, 845 em Eclipse UI, 1.153 em JDT, 183 em SWT. As mais frequentes são caixas de componente (`Project Inbox`, `Platform UI Triaged`, `JDT-UI-Inbox`, `JDT-Text-Inbox`, `Platform-SWT-Inbox`).

(fato) **A regex é uma heurística do executor, não validada.** Contas como `Birt-ReportDesigner` podem designar componentes em vez de pessoas. Excluindo-as, os assignees distintos caem de 148, 180, 163 e 109 para 126, 155, 139 e 91.

## 8. Split cronológico previsto

Partição 80/10/10 por data, ordenada cronologicamente. A escolha do timestamp de ordenação está aberta (D6).

(fato, 07) O intervalo coberto vai de 2001-10-10 (Eclipse UI e JDT) e 2005-06-14 (BIRT) até 2014-01-17. O 80º percentil de `report_time` cai em 2009-03 (BIRT), 2010-03 (Eclipse UI), 2007-11 (JDT) e 2009-05 (SWT).

(fato, 10) Sob ordenação por `report_time`, de 85% a 100% dos bugs de teste têm ao menos um bug de treino cujo commit é posterior ao seu `report_time`, em média de 6 a 41 bugs, o que equivale a entre 0,2% e 0,6% do treino. Detalhe em [ameacas_validade.md](ameacas_validade.md).

(inferência) O corte temporal estrito do Ramo B exige que cada métrica use somente bugs cuja correção já havia ocorrido na data de referência do bug avaliado. Ordenar apenas por `report_time` não garante isso.

## 9. Tempo de correção: o proxy disponível

(fato, 02 e 09) Na ausência de data de resolução, a única diferença temporal construível é `commit_time - report_time`. Mediana por bug, usando o primeiro commit: 4,7 dias em BIRT, 6,9 em Eclipse UI, 6,2 em JDT, 9,2 em SWT. O q95 vai de 148 a 649 dias e os máximos de 1.900 a 4.138 dias.

(fato, 09) O proxy inclui o tempo em fila antes da atribuição e o atraso entre a correção e o commit. Entre 0,1% e 0,7% dos bugs têm valor negativo e de 405 a 1.218 bugs por projeto têm intervalo inferior a uma hora.

A definição exata do proxy (primeiro ou último commit, tratamento de outliers e negativos) está aberta (D4).

## 10. Mensagens de commit

(fato, 12) A coluna `log` está preenchida em 100% das 41.062 linhas e dos bugs dos quatro projetos, com mediana de 7 a 13 palavras. A coluna `files` está preenchida em 99,9% a 100%.

(fato, 13) Os arquivos de features liberados por Alkhazi têm 18 features na abordagem nova e 14 na anterior. (inferência) As features φ19 a φ22, baseadas em mensagem de commit, não estão nesses arquivos. O que cada uma exige permanece não verificado (D7).
