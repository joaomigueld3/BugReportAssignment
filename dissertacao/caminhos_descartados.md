# Caminhos descartados, hipóteses refutadas e correções

Registro do que foi tentado e não deu em nada, para sustentar a seção de metodologia e evitar retrabalho. Inclui erros do executor corrigidos no caminho.

## Hipóteses refutadas pelos dados

### C1. "O dump contém só bugs fechados"

Hipótese derivada da leitura inicial do README. **Refutada** (fato, 04): `bug_commit` tem 545 bugs com status aberto (NEW, ASSIGNED, REOPENED) e 279 com status vazio, todos com commit vinculado, mais 574 com resolução diferente de FIXED.

A hipótese só vale para `bug_and_files`, que contém apenas `fixed` e `wontfix`. Consequência: o viés de workload é mais sutil do que se supunha, porque a ausência é de bugs **sem commit**, não de bugs não corrigidos.

### C2. "`product` ou `component` identificam o projeto"

Hipótese da pergunta 2 da exploração. **Refutada** (fato, 03): o produto majoritário cobre apenas 85,8% dos bugs em Eclipse UI, e há de 11 a 27 valores distintos de `product` por projeto. A identificação é pelo banco de dados, já que cada projeto é um banco MySQL separado.

### C3. "O filtro de status explica os 22.416 bugs de Alkhazi"

Tentativa de reconstruir a contagem da literatura. **Não funcionou** (fato, 03): o filtro de status contendo FIXED dá 29.383 bugs distintos, longe dos 22.416 de Alkhazi e dos 21.098 de DevRanker. `bug_and_files` dá exatamente 21.098, coincidindo com DevRanker em todos os projetos.

Nenhum outro filtro foi testado. A origem dos 22.416 permanece desconhecida (D9). Não repetir a tentativa com status sem antes ter o critério de Alkhazi sobre desenvolvedores ativos.

### C4. Alinhamento dos folds 2 e 3 dos arquivos de features

Tentativa de mapear os rótulos dos folds 2 e 3 de `ExtractedFeatures.zip` para o dump. **Não funcionou** (fato, 13): o positivo é `author` do bug no dump em apenas 12,0% e 13,2% das queries, contra 100% no fold 1.

Testei deslocamentos de posição de -2 a +2 entre a sequência de queries e a de positivos, e o casamento não melhorou (162, 158, 145, 152 e 139 acertos, contra 1.196 no fold 1). Exploração descartável, feita fora dos scripts versionados.

(inferência) A coluna `bug_id` desses folds pode ter sido copiada do fold 1 na exportação. Sem o código de geração, não há como confirmar. Não insistir nesse alinhamento.

## Decisões de execução revistas

### C5. Ambiente de restauração: parser próprio antes do Docker

Na primeira sessão (2026-10-06) não havia MySQL nem MariaDB no WSL, o `sudo` exigia senha e o Docker Desktop não estava integrado ao WSL. Escrevi um parser próprio para carregar o dump em SQLite (`01_restore.py`), validado por contagem de colunas por tupla e pelos valores de `AUTO_INCREMENT`, mas sem comparação com uma restauração real.

Quando o Docker ficou disponível (2026-10-13), restaurei o dump em MySQL 8.0.12 e comparei: as 35 tabelas têm contagem e hash de conteúdo idênticos (fato, 14). O parser ficou validado a posteriori e nenhum número anterior precisou ser refeito.

Lição para a escrita: o SQLite é o ambiente de trabalho e o MySQL é a referência de conferência. A D1 foi fechada com essa evidência.

### C6. Teste de sanidade com os arquivos de features, não tentado

A condição posta no CLAUDE.md para tentar o teste era que as linhas mapeassem para `bug_id` **e** o split fosse recuperável. O mapeamento funciona só para o fold 1 e só para Eclipse UI; o split não é recuperável, porque nada nos arquivos define a que fold cada bug pertence nem a data de corte (fato, 13).

Portanto o teste não foi tentado, e a comparação numérica com os resultados do ICPC 2019 não é viável a partir desses arquivos. O fold 1 ficou aproveitado apenas como corroboração independente de que o rótulo de Alkhazi é o `author` (evidência em D2).

## Correções de erros do executor

Registrados porque afetaram números que chegaram a ser afirmados.

### C7. Afirmação errada de que o dump era ASCII puro

Na etapa 10 escrevi que o arquivo SQL era ASCII puro, com base na saída do comando `file`. Está errado: uma contagem direta encontrou **79 linhas com caracteres não ASCII**. A afirmação foi corrigida no script 11 e em `NOTES.md`, e a dúvida real, se houve perda de acentos na exportação original, ficou registrada como não confirmada.

Lição: `file` amostra o início do arquivo e não é evidência sobre o conteúdo inteiro.

### C8. Erros de script corrigidos durante a execução

Nenhum alterou resultado publicado, mas todos interromperam a execução:

| Script | Erro | Correção |
|---|---|---|
| 03 | A linha TOTAL somava `linhas_por_bug`, produzindo 5,37 sem significado | Coluna excluída da soma |
| 10, 13 | `numpy` usado sem import | Import acrescentado |
| 11 | `g.stack` colidia com o método `DataFrame.stack` | Trocado por `g["stack"]` |
| 13 | `commit_time` não estava entre as colunas carregadas | Coluna acrescentada ao `load` |

### C9. Rótulo impreciso sobre concordância entre assignee e author

Na primeira versão do script 06 escrevi que os formatos heterogêneos de identificador eram a causa da subestimação, apresentando isso como fato. A formulação foi corrigida para separar o que é medido (parte dos authors não tem espaço no nome, e muitos nunca aparecem como assignee) do que é inferência (que a igualdade de strings subestima a concordância real).

## Itens não medidos, por decisão de escopo

Para não serem confundidos com lacunas:

- Efeito do vazamento temporal sobre as métricas do Ramo B. Depende do cálculo a definir.
- Razão entre tokens WordPiece do BERT e palavras.
- Variância efetiva dos scores de prioridade e severidade entre desenvolvedores.
- Validação manual das três heurísticas de classificação (A12).
- Qualquer treino, avaliação ou comparação numérica com resultados publicados.
