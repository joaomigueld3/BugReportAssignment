# Ameaças à validade: evidência medida

Cada item traz a magnitude medida e o script que a produziu. As limitações 1 a 3 correspondem às antecipadas na seção 5 do CLAUDE.md. Nenhuma correção é proposta aqui, por decisão de escopo da fase exploratória.

## Validade de construto

### A1. Não existe data de resolução nem de atribuição (limitação 1, confirmada)

(fato, 02) O schema de `bug_commit` não tem nenhuma coluna de data de resolução ou de atribuição do bug. A única diferença temporal construível é `commit_time - report_time`.

(fato, 09) Esse proxy mistura três intervalos que a métrica de tempo médio de correção deveria separar: o tempo em fila antes da atribuição, o tempo de correção propriamente dito e o atraso entre a correção e o commit. A mediana por bug fica entre 4,7 e 9,2 dias, mas o q95 vai de 148 a 649 dias e os máximos de 1.900 a 4.138 dias, o que indica que a cauda é dominada por tempo de fila, não de trabalho.

(fato, 09) De 405 a 1.218 bugs por projeto têm intervalo inferior a uma hora, o que é implausível como tempo de correção e sugere bugs já corrigidos quando foram registrados.

Declarar que o tempo médio de correção do Ramo B é medido sobre um proxy, não sobre o tempo de correção.

### A2. O workload é calculado só sobre bugs que acabaram corrigidos (limitação 2)

(fato, 04) Nenhuma linha de `bug_commit` tem `commit` vazio, ou seja, todo bug presente tem ao menos um commit vinculado.

(inferência) Bugs atribuídos que nunca receberam commit, incluindo os que terminaram INVALID ou WONTFIX sem código e os reatribuídos, não estão no dump. O workload calculado sobre esta base **subestima** a carga real.

(não confirmado) A magnitude do viés. O dump não traz a população de bugs sem commit, então o tamanho do que falta não é mensurável aqui; exigiria uma exportação do Bugzilla, fora do escopo e da regra de rede desta fase.

(fato, 04) Observação que atenua parcialmente: 574 bugs com resolução diferente de FIXED e 545 abertos **estão** presentes, porque têm commit. A ausência não é de todos os bugs não corrigidos, apenas dos sem commit.

### A3. O rótulo do desenvolvedor é ambíguo

(fato, 06) `assignee` e `author` concordam em 32,2% (BIRT) a 81,1% (SWT) das linhas. Qualquer das duas escolhas de rótulo discorda da outra numa fração grande dos casos, e em BIRT a discordância é a regra.

(fato, 06) Os identificadores são heterogêneos: nomes completos e logins convivem na mesma coluna, 46 dos 74 authors de BIRT não têm espaço no nome e 47 nunca aparecem como assignee. A concordância medida por igualdade de strings é um piso, não o valor real.

(fato, 06) De 3,1% a 13,4% dos bugs têm assignee que é caixa de componente ou de triagem, não pessoa.

(não confirmado) Se `author` corresponde a quem efetivamente corrigiu, e qual login corresponde a qual nome. O dump não traz o mapeamento.

### A4. Prioridade e severidade são o valor no momento da extração

(não confirmado, 05) Se o `importance` registrado é o valor inicial do bug ou o final. O dump não tem histórico de alterações. Se for o final, os scores do Ramo B usam informação posterior à data de referência do bug, o que é uma forma de vazamento.

## Validade interna

### A5. Vazamento temporal sob ordenação por data de criação (limitação 3)

(fato, 10) Num corte 80/10/10 por `report_time`, de 85,3% a 100% dos bugs de teste têm ao menos um bug de treino cujo commit é posterior ao seu `report_time`. Em média são de 6,2 a 39,5 bugs por bug de teste, o que equivale a entre 0,19% e 0,60% do conjunto de treino.

(inferência) O vazamento é quase universal em incidência e pequeno em magnitude, porque o commit costuma vir poucos dias após o report. Uma métrica de tempo de correção ou de workload calculada sobre o treino inteiro usa informação que não existia na data do bug avaliado.

(não medido) O efeito sobre as métricas do Ramo B, que depende do cálculo a ser definido na modelagem.

### A6. Concentração extrema de prioridade e severidade

(fato, 05) P3 cobre de 81,5% a 93,1% dos bugs e `normal` de 68,8% a 72,7%. A combinação P3 com `normal` responde por 19.391 dos 30.781 bugs.

(inferência) Os dois scores do Ramo B terão pouca variância entre desenvolvedores, o que pode torná-los pouco informativos e enfraquecer a comparação entre mecanismos de fusão. A medir na modelagem.

### A7. Grão bug-commit e risco de dupla contagem

(fato, 03) `bug_commit` tem de 1,22 a 1,45 linhas por bug, com máximo de 142, e contém pares (`bug_id`, `commit`) repetidos. Contar linhas em vez de bugs distintos infla as contagens em até 45%.

(fato, 03) `bug_id` repete entre bancos, com 74 casos entre Eclipse UI e JDT. Usar `bug_id` sozinho como chave mistura bugs de projetos diferentes.

## Validade externa

### A8. Idade dos dados

(fato, 07) Os dados terminam em 2014-01-17 e começam em 2001. (inferência) Têm cerca de doze anos de defasagem em relação a 2026. Práticas de triagem, tamanho de equipe e ferramentas mudaram no período, então a generalização para projetos atuais é limitada.

### A9. Espaço de classes pequeno em SWT e JDT

(fato, 08) Os authors distintos são 42 em SWT e 55 em JDT, contra 143 em Eclipse UI e 74 em BIRT. Os 10 maiores authors cobrem 90,3% dos itens em SWT e 92,5% em JDT.

(inferência) Nesses dois projetos o problema de recomendação é artificialmente mais fácil, porque o espaço de candidatos é pequeno e muito concentrado. Resultados de top-1 e top-3 nesses projetos não são comparáveis aos de projetos com equipes maiores, e isso precisa ser declarado ao reportar as métricas.

### A10. Cauda longa e cold start

(fato, 08) A mediana de bugs por assignee é de 2 a 4, e de 80 a 100 assignees por projeto têm até 5 bugs.

(fato, 08) De 12 a 65 desenvolvedores por projeto só aparecem depois do corte de 80%, respondendo por 1,2% a 10,0% dos itens posteriores ao corte. Esses casos não têm histórico no treino, logo o Ramo B não tem como pontuá-los. Isso se relaciona diretamente com a RQ4, sobre adicionar desenvolvedor sem retreino.

### A11. Representatividade da amostra do dump

(fato, 03) A base é um dump de quatro projetos do ecossistema Eclipse, todos em Java e todos usando Bugzilla. (inferência) Não cobre outras linguagens, outros rastreadores nem projetos corporativos fechados.

(fato, 03) Nenhuma tabela reproduz os 22.416 bugs de Alkhazi, e a origem da diferença de 1.318 em relação ao DevRanker é desconhecida. (inferência) Comparações numéricas diretas com os dois trabalhos ficam prejudicadas, porque não se sabe sobre qual subconjunto cada um mediu.

## Limitações do processo de medição

### A12. Heurísticas não validadas usadas nesta exploração

(fato) Três classificações aqui são heurísticas do executor, sem validação manual:

1. Conta genérica, pela regex `inbox|triaged|^birt-` (script 06).
2. Stack trace, por duas ou mais linhas `at pacote.Classe(Arquivo.java:N)` (script 11).
3. Classe de exceção, por nome `java.`, `org.` ou `javax.` terminando em `Exception` ou `Error` (script 11).

Os números derivados delas carregam erro de classificação não quantificado.

### A13. Restauração validada, leitura do dump não auditada além disso

(fato, 14) O SQLite usado nas análises tem contagem e hash de conteúdo idênticos aos de uma restauração real em MySQL 8.0.12 nas 35 tabelas. A comparação usou floats com 6 casas e datetimes como texto.

(não confirmado) Se a exportação original perdeu caracteres. Os dois leitores viram os mesmos bytes, logo uma perda seria anterior ao arquivo e invisível a esta verificação.
