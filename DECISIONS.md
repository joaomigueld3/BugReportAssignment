# DECISIONS

Formato: data, título, status, evidência, alternativas, decisão, responsável. As entradas D1 a D12 foram abertas em 2026-10-06; D13 em 2026-10-14. Decisões metodológicas pertencem ao pesquisador. A evidência remete a `outputs/` (gerado por `scripts/`).

## D1. SGBD e ambiente de restauração
- Status: fechada (2026-10-14).
- Evidência: `02_schema`: dump `mysqldump 10.13 / MySQL 8.0.12`, MyISAM/InnoDB, 7 bancos. `14_verify_mysql`: restauração real em `mysql:8.0.12` (Docker) sem erros; 35 de 35 tabelas com mesma contagem e mesmo hash de conteúdo que o SQLite construído pelo parser próprio (`01_restore.py`).
- Alternativas consideradas: MySQL/MariaDB em Docker; MariaDB via apt (exigia sudo); parser próprio para SQLite.
- Decisão: MySQL 8.0.46 real em Docker (container `bugtriage-mysql`, imagem `mysql:8.0`, sem porta publicada) como restauração de referência; o SQLite continua como base de análise, validado contra o MySQL. Evidência: `01b_verify_mysql`: 35 de 35 tabelas com contagens e hashes MD5 de linha idênticos (colunas float/double, 2 por `bug_and_files`, não comparadas); 0 linhas divergentes. Diferença de versão: dump de 8.0.12, servidor 8.0.46.
- Responsável: pesquisador (autorizou o Docker); execução: Claude Code.

## D2. Rótulo do desenvolvedor: `author` ou `assignee`
- Status: fechada (2026-10-14), sujeita à D11.
- Evidência: `06_label`. `assignee == author` por linha: 32,2% (BIRT), 61,8% (UI), 65,6% (JDT), 81,1% (SWT). Entre bugs com assignee não genérico, assignee é um dos authors em 34,1%, 71,6%, 77,0%, 88,0%. Assignees genéricos em 3,1% a 13,4% dos bugs. Formatos de identificador heterogêneos. `author` tem 42 a 143 valores distintos por projeto; `assignee`, 109 a 180.
- Corroboração (D8): no fold 1 de `ExtractedFeatures`, o positivo é `author` do dump em 100% das 1.196 queries com positivo (só Eclipse UI) e igual ao `assignee` em 68,8%; os 142 candidatos são quase o conjunto de authors de UI no dump (139 de 143). Alternativas: author (premissa de Alkhazi, quem commitou corrigiu); assignee excluindo contas genéricas; author com resolução de identidades; restringir a bugs em que os dois concordam.
- Decisão: `author` do commit. Bugs com mais de um author: todos os authors são positivos (ver D13).
- Responsável: pesquisador.

## D3. Separação de `importance` em prioridade e severidade
- Status: parcialmente decidida (2026-10-14).
- Evidência: `05_importance`: 30.781 de 30.781 bugs seguem `P<1-5> <severidade>`, sem nulos nem exceções; valor constante por bug. P3 em 81% a 93% e "normal" em 69% a 73% dos bugs.
- Alternativas: parsing direto em dois campos; tratar "enhancement" como severidade ou excluir; decidir como mapear níveis categóricos em pesos que somam 1.
- Decisão: aprovado o parsing de `importance` em dois campos (prioridade P1 a P5 e severidade). Tratamento de "enhancement" e pesos dos níveis adiados para a modelagem do Ramo B.
- Responsável: pesquisador.

## D4. Proxy de tempo de correção
- Status: fechada (2026-10-14).
- Evidência: `02_schema` (sem data de resolução ou atribuição); `09_interval`: mediana por bug de 4,7 a 9,2 dias, cauda até 4.138 dias, 0,1% a 0,7% de bugs com intervalo negativo, 405 a 1.218 bugs com intervalo < 1 hora.
- Alternativas: `commit_time - report_time` do primeiro commit; do último commit; truncamento ou winsorização de outliers; descarte de negativos.
- Decisão: `commit_time` do primeiro commit menos `report_time`, em dias. Tratamento de negativos e de outliers (descarte, truncamento) ainda não definido; declarar como limitação.
- Responsável: pesquisador.

## D5. Viés de workload por ausência de bugs não corrigidos
- Status: aberta (2026-10-14): adiada até o pesquisador enviar o trecho de limitações de Rastogi et al. (2013), Yadav et al. (2019), Saxena & Gupta (2024) e/ou Alkhazi (2020). Opções explicadas: declarar limitação, declarar com sensibilidade interna, complementar via Bugzilla (exige exceção à regra de rede). Nenhuma foi confirmada como embasada na literatura.
- Evidência: `04_status`: nenhuma linha sem commit; 574 bugs distintos com resolução não FIXED e 545 abertos, todos com commit. Bugs sem commit não existem no dump (população ausente não mensurável aqui).
- Alternativas: declarar a limitação; complementar via API do Bugzilla (fora do escopo e da regra de rede desta fase); restringir a análise a bugs FIXED.
- Decisão: pendente.
- Responsável: pesquisador.

## D6. Timestamp de ordenação do split e regra de corte do Ramo B
- Status: fechada (2026-10-14), a regra de corte será implementada na fase de modelagem.
- Evidência: `07_period`: dados até 2014-01-17. `10_leakage`: com ordenação por `report_time`, 85% a 100% dos bugs de teste têm bugs de treino cuja correção é posterior ao seu `report_time` (média de 6 a 41 bugs, 0,2% a 0,6% do treino). `09_interval` mostra commits antes do report em 0,1% a 0,7% dos bugs.
- Alternativas: ordenar por `report_time` e restringir as métricas do Ramo B a bugs com `commit_time` anterior ao `report_time` do bug avaliado; ordenar por `commit_time`.
- Decisão: ordenar por `report_time`; cada métrica do Ramo B usa só bugs com `commit_time` anterior ao `report_time` do bug avaliado.
- Responsável: pesquisador.

## D7. Viabilidade das features de commit (φ19 a φ22)
- Status: aberta (2026-10-14): aguardando o pesquisador colar o trecho de Alkhazi (2020) que define φ19 a φ22.
- Evidência: `12_commit_log`: `log` preenchido em 100% das linhas e dos bugs; `files` em 99,9% a 100%.
- Pendente: conferir no artigo de Alkhazi (2020) o que cada feature exige. Nada implementado.
- Evidência adicional (`13_features_sanity`): os CSV liberados têm 18 features (14 na abordagem anterior); φ19 a φ22 não aparecem nos arquivos (inferência).
- Responsável: pesquisador.

## D8. Teste de sanidade com `ExtractedFeatures.zip` e `SVMrank_Models.zip`
- Status: aberta por escolha do pesquisador (2026-10-14); inspeção concluída em 2026-10-13, sem ação pendente do Claude Code.
- Evidência: `13_features_sanity`. Só Eclipse UI: 890 bugs, todos em `bug_commit` (9,4% dos 9.424), 622 em `bug_and_files`. No fold 1 o positivo é `author` do dump em 1.196 de 1.196 queries com positivo; nos folds 2 e 3 só em 12,0% e 13,2%, com a mesma sequência de `bug_id`. Os arquivos não definem o split. Modelos só para os folds 2 e 3, kernel linear.
- Alternativas: (a) não fazer o teste (adotada nesta fase, pela condição do CLAUDE.md não satisfeita); (b) usar apenas o fold 1 como corroboração do rótulo `author`; (c) pedir aos autores o código de geração.
- Decisão: (a), com (b) registrado como evidência para D2. Comparação numérica com resultados publicados está fora de escopo.
- Responsável: pesquisador (confirmar).

## D9. Origem da diferença de contagem Alkhazi (22.416) vs DevRanker (21.098)
- Status: aberta, tentativa de reconstrução executada (2026-10-14).
- Evidência: `03_counts`: `bug_and_files` tem 21.098 bugs, igual a DevRanker por projeto; `bug_commit` tem 30.781. O filtro FIXED (29.383) não reproduz nenhum dos dois. A diferença não é explicada pelo dump.
- Tentativa de reconstrução (`14_alkhazi_filter`): 608 configurações (status, produto principal, rótulo author ou assignee, limiar de bugs por desenvolvedor, modo algum ou todos). Nenhuma reproduz os 4 projetos (nenhuma reproduz sequer um projeto). Melhor erro absoluto somado: 1.837 (total 24.253, só 69 desenvolvedores); as configurações com ~252 desenvolvedores têm erro mínimo de 5.010. Nenhuma satisfaz tamanho e número de desenvolvedores ao mesmo tempo. `bug_and_files` (21.098) é menor que o alvo em todos os projetos.
- Alternativas: aceitar a diferença como não explicada; testar outras hipóteses (limiar de 'ativo' por período, dedup de identidades); consultar os autores.
- Decisão: pendente; recomendo registrar como 'não confirmado', já que a base foi decidida em D10 sem depender disso.
- Responsável: pesquisador.

## Entradas novas surgidas dos dados

## D10. População-base e chave do bug
- Status: fechada (2026-10-14).
- Evidência: `03_counts`: `bug_commit` (30.781 bugs, grão bug-commit, pares repetidos) contra `bug_and_files` (21.098 bugs, 1 linha por bug, só fixed e wontfix, sem assignee/author/importance/log). `bug_id` repete entre bancos (74 entre UI e JDT).
- Alternativas: base `bug_commit` filtrada por status; base `bug_and_files` unida a `bug_commit` por (projeto, `bug_id`); outra.
- Decisão: base `bug_commit` com chave (projeto, `bug_id`), filtrada por resolução FIXED (29.383 bugs distintos: BIRT 6.658, UI 8.854, JDT 8.277, SWT 5.594). `bug_and_files` não é a base.
- Responsável: pesquisador.

## D11. Resolução de identidades e contas genéricas
- Status: aberta (2026-10-14): o pesquisador ainda não aprovou o método híbrido recomendado.
- Evidência: `06_label`: `author` mistura nomes completos e logins (46 de 74 sem espaço em BIRT; 47 authors de BIRT nunca aparecem como assignee). Contas genéricas por regex `inbox|triaged|^birt-`: 224 a 1.153 bugs por projeto; a regex é heurística minha, não validada. `08_developers`: 12 a 65 desenvolvedores aparecem só depois do corte de 80%.
- Alternativas: mapeamento manual login para nome; normalização por heurística; descartar bugs com assignee genérico; tratar desenvolvedores novos como cold-start.
- Responsável: pesquisador.

## D12. Bugs com status aberto ou vazio em `bug_commit`
- Status: aberta, com instrução do pesquisador: investigar `log` antes de decidir. Nota: com o filtro FIXED da D10, esses 824 bugs já ficam fora; a investigação só importa se a D10 mudar.
- Evidência: `04_status`: 545 abertos (NEW, ASSIGNED, REOPENED) e 279 vazios, todos com commit vinculado; origem do vínculo não confirmada (falta inspecionar `log`).
- Alternativas: excluir; manter; investigar `log` antes.
- Responsável: pesquisador.

## D13. Rótulo de bugs com mais de um author
- Status: fechada (2026-10-14).
- Evidência: `06_label`: bugs com 2 ou mais authors: 259 (BIRT), 379 (UI), 240 (JDT), 262 (SWT).
- Alternativas: todos positivos; author do primeiro commit; author do último commit.
- Decisão: todos os authors do bug são positivos (acerto no top-k se algum estiver no ranking). Implicação a tratar na modelagem: o treino do Ramo A precisa de um critério para pares positivos múltiplos.
- Responsável: pesquisador.

## D14. Publicação de dados no GitHub
- Status: fechada (2026-10-23); aberta em 2026-10-16. (fato, `git branch -vv`) O `origin` (`joaomigueld3/BugReportAssignment`) já tem `master` e `exploracao-dataset` com os commits `341a3f2` e `40627f3` (CLAUDE.md, NOTES, DECISIONS, `dissertacao/`, `registro/`, `.claude/`, scripts e saídas agregadas, sem nomes de pessoas); só `74e47ee` está local. O histórico herdado do upstream inclui `SQL_BugDatabase_Dump.7z`, `ExtractedFeatures.zip` e `SVMrank_Models.zip`, que contêm os dados completos, com nomes. `data/samples/` não está versionado. (não confirmado) se o repositório é público ou privado.
- Evidência: `15_pii_scan` (nomes de usuários que reportaram bugs, nomes em texto livre, 8 e-mails em logs) e `16_make_samples` (amostras pseudonimizadas de cerca de 1,2 MB, 0 nomes reais pela busca exata). Reidentificação continua possível por `bug_id` e hash de commit.
- Alternativas: (a) versionar só scripts, saídas agregadas e amostras pseudonimizadas, com instruções e SHA-256 para obter o dump do upstream (recomendada); (b) versionar também dados completos pseudonimizados (reidentificáveis, licença do dataset não verificada); (c) não publicar dados.
- Respostas do pesquisador (2026-10-23): o repositório original (upstream) é público; aceita que `dissertacao/`, `NOTES.md` e `registro/` fiquem expostos; considera a licença aberta por o dataset ser fonte de artigo científico.
- Ressalva do Claude Code: (fato) o upstream não tem arquivo de licença; (inferência) a publicação em artigo não concede licença por si, então a redistribuição segue "não confirmada". O risco prático parece baixo, pois o conteúdo já é público no upstream; mitigação proposta: aviso de atribuição à fonte no README. Visibilidade do `origin` (o fork) continua não confirmada.
- Decisão (2026-10-23): manter o que já está publicado e versionar as amostras **pseudonimizadas** (`data/samples/`, `reporter` incluído, também pseudonimizado) e o visualizador offline. Cru foi considerado e descartado: é defensável, pois o fork público já carrega os dados completos no histórico, mas um CSV em texto seria pesquisável e o `.7z` não. A coluna `reporter` foi mantida por fidelidade ao esquema, mesmo sendo usuários comuns (não medido se ajuda a prever o desenvolvedor). Verificação antes do commit: 0 nomes completos reais e 0 e-mails pessoais nos 4 CSV e no HTML (busca exata). Limite: nomes parciais e de terceiros em texto livre não são detectados, e `bug_id` e hash de commit permitem reidentificar.
- Status final: fechada (2026-10-23). Pendente fora do repositório: o aviso de fonte está no README; o `push` ao `origin` é do pesquisador.
- Responsável: pesquisador.

