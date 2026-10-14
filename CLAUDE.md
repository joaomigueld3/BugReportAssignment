# CLAUDE.md: contexto da análise exploratória (HybridBugRank)

Este arquivo orienta o Claude Code na fase de exploração do dataset da dissertação de mestrado em Engenharia da Computação. Leia-o inteiro antes de qualquer comando. Se algo aqui contradisser o que os dados mostram, os dados prevalecem e a contradição deve ser reportada.

## 1. Papel e regras de conduta

O Claude Code atua como executor da exploração: restaura o dump, roda consultas, mede e reporta. Decisões metodológicas pertencem ao pesquisador e são discutidas fora deste repositório. Quando uma análise exigir uma escolha de método, pare, descreva as alternativas e registre a questão em `DECISIONS.md` como aberta.

Regras:

1. Não invente. Se o dado não confirma uma afirmação, escreva "não confirmado" e diga o que faltou para confirmar.
2. Tudo o que vem do README do dataset é hipótese até o dump confirmar. Isso vale em especial para o schema da seção 3.
3. Separe sempre fato medido (com a consulta que o produziu), inferência e suposição. Rotule cada um.
4. Não proponha nem execute treino de modelos nesta fase.
5. Relatórios em português, em prosa técnica, sem travessão no texto corrido. Tabelas pequenas são bem-vindas.

## 2. Contexto mínimo do projeto

A dissertação propõe o HybridBugRank, um modelo de recomendação de desenvolvedores para bug reports (bug triaging) com dois ramos e um gate de fusão.

- Ramo A: BERT-base-uncased com fine-tuning sobre `summary` + `description` do bug report, produzindo um sinal textual por par (bug, desenvolvedor).
- Ramo B: quatro métricas de desempenho do desenvolvedor, originadas em Rastogi et al. (2013) e usadas em Yadav et al. (2019) e Saxena & Gupta (2024, DDRS): Developer Priority Score, Developer Severity Score, tempo médio de correção e workload.
- Gate: `Score(b_k, d_j) = g(b_k, d_j)·h_A(b_k, d_j) + (1 − g(b_k, d_j))·h_B(m_j)`, com `g` dependente do par.

Perguntas de pesquisa (texto completo no documento de reformulação do projeto, não replicado aqui): RQ1 compara o gate com a fusão heurística estilo DDRS em top-1, top-3 e MRR. RQ2 compara o gate com a fusão global aprendida, na qual o peso é um escalar λ único para todo o dataset. RQ3 pergunta se os pesos aprendidos para tempo médio e workload saem negativos. RQ4 trata da ausência de retreino ao adicionar desenvolvedor.

Duas contribuições metodológicas dependem diretamente destes dados: a comparação dos três mecanismos de fusão sobre o mesmo dataset e o corte temporal estrito no cálculo do Ramo B (cada métrica usa somente informação anterior à data do bug avaliado).

## 3. Dataset

Fonte: repositório `https://github.com/anonymous-programmers/BugReportAssignment`, arquivo `SQL_BugDatabase_Dump.7z`. É o repositório anonimizado para revisão duplo-cega de Alkhazi et al., associado ao artigo do ICPC 2019 segundo o README; o artigo de 2020 da Applied Soft Computing (Alkhazi et al.) o cita como fonte. O README menciona "dataset.zip" enquanto o arquivo é `.7z`. Registrar a inconsistência.

Projetos no dump segundo o README: AspectJ, Birt, Eclipse Platform UI, JDT, SWT e Tomcat. Usaremos apenas Birt, Eclipse Platform UI, JDT e SWT. AspectJ e Tomcat ficam fora.

Schema declarado no README para a tabela `bug_commit` (NÃO VERIFICADO):

- `id`: ID interno do banco, sem significado fora dele
- `bug_id`: ID do bug report
- `summary`, `description`: título e descrição
- `report_time`: criação do bug report
- `reporter`: quem criou
- `assignee`: desenvolvedor a quem foi atribuído
- `status`: status do bug (por exemplo VERIFIED FIXED)
- `product`, `component`: produto e subseção
- `importance`: escala que indica severidade e urgência
- `commit`: hash do commit que resolveu o bug
- `author`: desenvolvedor que escreveu o commit
- `commit_time`: timestamp do commit
- `log`: mensagem do commit
- `files`: lista de arquivos alterados

O README menciona essa tabela como a principal para extração. Podem existir outras tabelas no dump. Listar todas.

Valores de referência da literatura, apenas para conferência (não são metas): Alkhazi et al. (2020) reportam 22.416 bug reports (Birt 4.952, Eclipse UI 6.670, JDT 6.528, SWT 4.266) e 252 desenvolvedores. Kardoost et al. (2022, DevRanker), que derivam seus dados dos de Alkhazi e os complementam via API do Bugzilla, reportam 21.098 (JDT 6.274, Eclipse UI 6.495, BIRT 4.178, SWT 4.151). A diferença de 1.318 bugs entre as duas fontes tem causa desconhecida. Alkhazi descarta bugs INVALID e considera apenas desenvolvedores ativos. O DDRS não informa tamanhos.

Cuidado de grão: se a tabela tiver uma linha por par bug-commit, um bug com vários commits aparece várias vezes. Toda contagem deve distinguir linhas de bugs distintos.

## 4. Perguntas da exploração, em ordem

Execute em ordem e produza, para cada uma, uma saída pequena e agregada. A coluna final indica por que a resposta importa.

1. Restauração e schema. Qual o SGBD exigido pelo dump (inspecione o cabeçalho antes de propor o ambiente)? Quais tabelas, colunas e tipos existem de fato? Há divergência em relação à seção 3? Impacto: valida todas as hipóteses seguintes.
2. Identificação do projeto. Como cada linha pertence a Birt, Eclipse UI, JDT ou SWT? Via `product`/`component`, via alguma outra coluna ou tabela? Quais valores de `product` e `component` existem? Impacto: sem isso não há como separar os quatro projetos.
3. Contagens. Linhas e `bug_id` distintos por projeto; comparação com os valores de referência da seção 3. Impacto: define o tamanho real da amostra e se a diferença 22.416 vs 21.098 se explica.
4. Status. Distribuição de `status` por projeto. Impacto: confirma se só existem bugs fechados e, portanto, o viés no cálculo de workload.
5. Campo `importance`. Valores distintos e frequências. O campo combina prioridade e severidade em uma string (por exemplo uma prioridade seguida de uma severidade)? É possível separá-las por parsing sem perda? Há valores nulos ou fora do padrão? Impacto: viabiliza ou não os dois scores distintos do Ramo B (Priority Score e Severity Score).
6. Rótulo do desenvolvedor. Concordância entre `assignee` e `author` por projeto. Quantos `assignee` são contas genéricas ou de triagem (liste os mais frequentes)? Quantos pares divergem? Impacto: decide qual coluna é o ground truth.
7. Período. Menor e maior `report_time` e `commit_time` por projeto; distribuição por ano. Impacto: define o split cronológico e a ameaça de validade externa por idade dos dados.
8. Desenvolvedores. Número de desenvolvedores por projeto (para `author` e para `assignee`), distribuição de bugs por desenvolvedor (cauda longa, desenvolvedores com poucos bugs), e quantos aparecem somente em períodos tardios. Impacto: SWT e JDT têm poucos desenvolvedores segundo a literatura, o que facilita artificialmente o problema e precisa ser declarado.
9. Intervalo report-commit. Distribuição de `commit_time - report_time` (dias) por projeto: valores negativos, zero, outliers extremos. Impacto: este é o único proxy disponível para tempo de correção.
10. Vazamento temporal no Ramo B. Para uma amostra de bugs de teste simulada por corte cronológico, quantos bugs de treino têm `commit_time` posterior ao `report_time` do bug de teste? Impacto: uma métrica de tempo de correção ou workload só pode usar bugs cuja correção já havia ocorrido na data de referência. Ordenar apenas por `report_time` pode vazar informação futura.
11. Texto. Proporção de `summary` e `description` nulos ou vazios; comprimento em tokens aproximado (por palavras) e presença de stack traces. Impacto: dimensionamento do Ramo A.
12. Mensagens de commit. A coluna `log` está preenchida? Para quantos pares? Impacto: Alkhazi propõe features baseadas em mensagens de commit (φ19 a φ22); se o dump traz os logs, essas features podem ser viáveis sem checkout do código. Apenas reporte a completude. Não implemente features.

## 5. Requisitos do Ramo B que os dados precisam suportar

As quatro métricas, como formuladas na literatura do projeto:

- Developer Priority Score: soma ponderada por prioridade da fração de bugs de cada nível resolvidos pelo desenvolvedor, com pesos que somam 1.
- Developer Severity Score: estrutura análoga, por nível de severidade.
- Tempo médio de correção: tempo total de resolução dividido pelo número de bugs resolvidos, em dias.
- Workload: soma de (prioridade + severidade) vezes o número de bugs atribuídos ao desenvolvedor (Eq. 4 do DDRS).

Limitações já antecipadas, a confirmar ou refutar com os dados:

1. Não há (segundo o README) data de resolução do bug nem data de atribuição. O tempo de correção seria o proxy `commit_time - report_time`, o que inclui o tempo em fila antes da atribuição e o tempo entre o commit e o fechamento.
2. Se o dump só contém bugs com commit vinculado, workload é calculado apenas sobre bugs que acabaram corrigidos. Bugs atribuídos que terminaram INVALID, WONTFIX ou reatribuídos ficam invisíveis, o que subestima a carga real.
3. O corte temporal exige que cada métrica use somente informação anterior à data do bug avaliado (ver pergunta 10).

Para cada limitação, reporte a evidência medida, sem propor correção.

## 6. Split previsto (contexto, não decisão final)

Partição cronológica 80/10/10 (treino, validação, teste), ordenada por data de criação. A escolha do timestamp de ordenação (`report_time` ou `commit_time`) está aberta e depende dos resultados das perguntas 7, 9 e 10.

## 7. Convenções de trabalho

1. Estrutura sugerida: `data/raw/` (dump original, somente leitura, fora do git), `data/interim/`, `sql/`, `scripts/`, `outputs/` (saídas agregadas pequenas), `DECISIONS.md`, `NOTES.md`.
2. Calcule e registre o SHA-256 do arquivo `.7z` baixado em `NOTES.md`, com data de download.
3. Scripts numerados e reexecutáveis do zero (`01_restore.*`, `02_schema.*`, e assim por diante). Cada script grava sua saída em `outputs/` com o mesmo prefixo numérico.
4. Antes e depois de qualquer JOIN ou deduplicação, imprima a contagem de linhas e de `bug_id` distintos.
5. Saídas versionadas devem ser agregadas e pequenas. Não grave amostras grandes de texto de bugs nem dados pessoais (nomes e e-mails de desenvolvedores) em `outputs/`; use identificadores pseudonimizados quando precisar listar desenvolvedores.
6. Semente fixa em qualquer amostragem.
7. Sem chamadas de rede além do download do dump e da instalação de dependências.
8. Ao final de cada etapa, escreva em `NOTES.md` um relatório curto: o que foi feito, consultas usadas, resultados, itens "não confirmados" e o que o resultado muda para o desenho.

## 8. DECISIONS.md (criar na primeira execução)

Formato de cada entrada: data, título, status (aberta ou fechada), evidência (consulta e saída), alternativas consideradas, decisão e responsável. Este arquivo alimentará a seção de metodologia da dissertação, então registre a evidência com precisão.

Entradas abertas iniciais:

1. SGBD e ambiente de restauração (a definir após inspeção do cabeçalho do dump).
2. Rótulo do desenvolvedor: `author` do commit ou `assignee` (decidir após a pergunta 6; Alkhazi assume que quem commitou é quem corrigiu).
3. Separação de `importance` em prioridade e severidade (decidir após a pergunta 5).
4. Proxy de tempo de correção (`commit_time - report_time`) e sua declaração como limitação.
5. Tratamento do viés de workload por ausência de bugs não corrigidos.
6. Timestamp de ordenação do split cronológico e regra de corte para as métricas do Ramo B.
7. Viabilidade das features de mensagem de commit (φ19 a φ22) com os logs do dump. Requer conferência no artigo de Alkhazi (2020) do que cada feature exige.
8. Teste de sanidade com `ExtractedFeatures.zip` e `SVMrank_Models.zip` do repositório: só tentar se as linhas mapearem para `bug_id` e o split for recuperável. Não verificado.
9. Origem da diferença de contagem entre Alkhazi (22.416) e DevRanker (21.098).

## 9. Fora de escopo nesta fase

Dataset Jira (existe um conjunto de CSVs de Jira no Project de pesquisa, mas não faz parte deste trabalho), GitBugs, treino ou avaliação de qualquer modelo, definição do gate e das variantes de ablação, implementação de baselines, e qualquer comparação numérica com resultados publicados.
