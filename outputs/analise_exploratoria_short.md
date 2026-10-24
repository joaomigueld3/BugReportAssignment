# Base de bug triaging: o que ela permite (folha de consulta)

Versão de 2026-10-23. Resumo para consulta do Claude Project. Números medidos no dump de Alkhazi et al. (BIRT, Eclipse Platform UI, JDT, SWT). Nada foi treinado. (fato) = medido; (inferência) = conclusão minha; (não confirmado) = falta evidência. A escolha de método é do pesquisador.

## 1. A tarefa que a base suporta

Dado um bug report, ranquear os desenvolvedores que o corrigiram. Rótulo: `author` do commit que resolveu o bug; se houver mais de um author, todos são positivos (3,6% dos bugs). Chave do bug: (projeto, `bug_id`). Base: bugs com resolução FIXED.

| | BIRT | Eclipse UI | JDT | SWT |
|---|---|---|---|---|
| Bugs | 6.658 | 8.854 | 8.277 | 5.594 |
| Authors (classes) | 74 | 138 | 53 | 41 |
| Fatia do author mais frequente | 10,5% | 18,5% | 22,9% | 22,9% |
| Authors com até 5 bugs | 23 | 87 | 29 | 19 |
| Authors ativos nos 365 dias antes (mediana) | 26 | 36 | 8 | 13 |
| Bugs de teste sem nenhum author no treino (split 80/10/10) | 6,3% | 19,8% | 3,6% | 12,0% |
| Descrição vazia | 26% | 20% | 15% | 22% |
| Período dos bugs | 2005 a 2013 | 2001 a 2014 | 2001 a 2014 | 2002 a 2014 |

## 2. Quais campos existem e quando estão disponíveis

Só o que é conhecido no momento do report pode alimentar a previsão. O resto é informação futura.

| Campo | Uso possível | Observação |
|---|---|---|
| `summary`, `description` | texto do bug (Ramo A) | (fato) todo `summary` começa com "Bug <n> – " e `<n>` é o `bug_id`; precisa ser removido. 15% a 26% sem descrição |
| `report_time` | ordenação, janelas, corte temporal | sem fuso; dados até 2014-01-17 |
| `product`, `component` | metadados do bug | `component` informa o author em BIRT e JDT, quase nada em UI e SWT (quase todos os bugs num só componente) |
| `reporter` | quem abriu o bug | 686 a 1.499 valores por projeto; utilidade não medida |
| `importance` | prioridade P1 a P5 e severidade | (fato) separa sem perda em 100% dos bugs. (não confirmado) se é o valor inicial ou o final |
| `author` | rótulo | formatos mistos (nomes e logins); identidades não resolvidas |
| `assignee`, `status`, `commit`, `commit_time`, `log`, `files` | **só histórico, nunca do bug em previsão** | (inferência) vêm da atribuição final e do commit de correção, portanto não existem no momento do report. Usar como feature do próprio bug vazaria o futuro |

## 3. O que se pode construir

- **Sinal textual por par (bug, desenvolvedor)**: texto do bug mais histórico do desenvolvedor.
- **Métricas por desenvolvedor com corte temporal** (Ramo B), usando só bugs com `commit_time` anterior ao `report_time` do bug avaliado: fração por prioridade, fração por severidade, tempo médio de correção (primeiro commit menos `report_time`, em dias), workload.
- **Split cronológico** por `report_time`, por projeto.
- **Pool de candidatos no tempo**: authors ativos numa janela anterior ao bug.
- **Features de arquivos e de mensagens de commit do histórico** (`files` 99,9% a 100% preenchido; `log` 100%), calculadas só sobre bugs já corrigidos antes do bug avaliado. A definição das features de Alkhazi (φ19 a φ22) não foi conferida (não confirmado).

## 4. Propriedades dos dados que limitam a escolha de técnica

- **Cauda longa e poucas classes em JDT e SWT** (53 e 41): o problema é mais fácil nesses dois do que em Eclipse UI.
- **Cold-start real em teste**: até 19,8% dos bugs de Eclipse UI só têm authors inéditos; um modelo restrito aos authors do treino não acerta esses bugs.
- **Pool ativo bem menor que o total** (mediana de 8 em JDT contra 53 classes): o conjunto de desenvolvedores muda com o tempo.
- **Ramo B com pouca dispersão**: prioridade P3 em 82% a 93% dos bugs e severidade `normal` em 69% a 73%; entre authors com 20 ou mais bugs, a fração de `normal` fica em geral entre 0,56 e 0,85.
- **Tempo de correção com cauda pesada**: mediana de 4,5 a 8,9 dias, mas q90 de 64 a 285 dias e máximos de 1.900 a 4.139 dias; 0,1% a 0,7% dos bugs têm intervalo negativo.
- **Vazamento temporal existe e é pequeno** quando se ordena só por `report_time`: 85% a 100% dos bugs de teste têm bugs de treino cuja correção é posterior; vale de 0,2% a 0,6% do treino.

## 5. O que a base não permite

- **Tempo real de correção**: não há data de resolução nem de atribuição; o proxy inclui fila e atraso até o commit.
- **Workload completo**: bugs atribuídos que nunca tiveram commit não estão no dump (subestima a carga; magnitude não mensurável aqui).
- **Contagem de pessoas reais**: `author` mistura nomes e logins; o número de desenvolvedores é só um limite superior.
- **Reproduzir o tamanho de Alkhazi (22.416 bugs, 252 desenvolvedores)**: a base tem 29.383 bugs; 608 filtros testados não reproduzem os números dele.
- **Comparação numérica com resultados publicados**: os arquivos de features do upstream cobrem só Eclipse UI e o split não é recuperável.
- **Generalização além do contexto**: quatro projetos Eclipse, dados de 2001 a 2014.

## 6. Perguntas que a base deixa em aberto

1. Ranking sobre todos os authors do treino, sobre os ativos numa janela, ou com suporte a authors novos?
2. Que tratamento para a cauda longa e para os múltiplos positivos?
3. Como tratar descrição vazia, o prefixo do `summary` e o limite de tokens do texto (razão token por palavra não medida)?
4. Janela e normalização das métricas do Ramo B diante da baixa dispersão e da cauda pesada do tempo?
5. Que resolução de identidades adotar antes dos experimentos?
