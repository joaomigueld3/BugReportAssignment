# Proveniência e reprodutibilidade

Dados para a seção de materiais e para a declaração de disponibilidade de dados.

## Origem dos arquivos

Repositório: `https://github.com/anonymous-programmers/BugReportAssignment`, versão anonimizada para revisão duplo-cega de Alkhazi et al., associada ao artigo do ICPC 2019 segundo o README. O artigo de 2020 da Applied Soft Computing cita-o como fonte.

(fato) Os três arquivos vieram de um `git clone` do repositório, não de downloads avulsos. O mtime local é 2026-10-06; os commits que os adicionaram são de 2019-02-09. **Data de aquisição registrada: 2026-10-06.**

| Arquivo | Bytes | SHA-256 |
|---|---|---|
| `SQL_BugDatabase_Dump.7z` | 16.033.854 | `ae1f9670e90c71b35090aed9ecf2db021c1385a2e317651a83225414f3d3b19d` |
| `ExtractedFeatures.zip` | 21.161.853 | `729430abeea966c455529d52cd5b6ff20f5ccc755c1bcd93621170837f21421a` |
| `SVMrank_Models.zip` | 23.993.991 | `9f42557c94c52149f513a70bbcbac6d5700385e6e60b15e6e4ad006d1285e737` |

(fato) O `.7z` contém um único arquivo, `SQL_BugDatabase_Dump.sql`, de 167.009.039 bytes, sem pasta.

## Inconsistências documentais da fonte

(fato) O README do dataset menciona "dataset.zip" e diz que "once unzipped, the dataset folder will contain a SQL dump". O arquivo é `.7z`, não `.zip`, e contém um arquivo solto, não uma pasta. Registrado conforme pedido na seção 3 do CLAUDE.md.

(fato) O README lista seis projetos (AspectJ, Birt, Eclipse Platform UI, JDT, SWT, Tomcat) e descreve apenas a tabela `bug_commit`. O dump tem 7 bancos e 35 tabelas, incluindo `bug_and_files`, `file_history`, `api_descriptions` e cinco tabelas auxiliares em `eclipse_platform_ui`, nenhuma documentada.

(fato) O link do projeto de Azure Machine Learning está omitido no README por causa da revisão duplo-cega, portanto os resultados de aprendizado profundo do artigo não são reproduzíveis a partir deste repositório.

## Versões de software

| Componente | Versão |
|---|---|
| Dump gerado por | `mysqldump 10.13`, Distrib MySQL 8.0.12, Win64 (x86_64) |
| Servidor declarado no dump | MySQL 8.0.12 |
| MySQL de verificação | imagem Docker `mysql:8.0.12`, digest `sha256:8fdc47e9ccb8112a62148032ae70484e3453b628ab6fe02bccf159e2966b750e` |
| Docker | 27.4.0 |
| SQLite (ambiente de trabalho) | 3.45.1 |
| Python | 3.12.3 |
| Dependências Python | `py7zr`, `pandas`, `numpy`, `pymysql` |
| Sistema | Linux 6.18.33.2 microsoft-standard-WSL2 |

(fato) As únicas chamadas de rede foram a aquisição dos arquivos, a instalação dessas dependências e o download da imagem Docker, conforme a regra 7 da seção 7 do CLAUDE.md.

## Restauração e reprodução

Restauração em MySQL, para conferência:

```
docker run -d --name bugdump-mysql -e MYSQL_ROOT_PASSWORD=<senha> \
  -p 127.0.0.1:33306:3306 -v "$PWD/data/interim:/dump:ro" \
  mysql:8.0.12 --character-set-server=latin1
docker exec bugdump-mysql sh -c 'mysql -uroot -p<senha> < /dump/SQL_BugDatabase_Dump.sql'
```

(fato, 14) Concluída sem erros em cerca de 76 segundos. A senha usada é local e o contêiner escuta apenas em 127.0.0.1.

Ambiente de trabalho e reexecução completa da exploração:

```
scripts/run_all.sh
```

(fato) Reexecuta `01_restore.py` e os scripts 02 a 13 do zero, em cerca de 45 segundos, gravando em `outputs/`. O script 14 fica fora porque exige o contêiner MySQL ativo.

## Verificação da fidelidade da restauração

(fato, 14) `14_verify_mysql.py` compara, para cada uma das 35 tabelas, a contagem de linhas e o SHA-256 do conteúdo entre o MySQL real e o SQLite. Resultado: **35 de 35 tabelas idênticas, zero divergentes.**

Parâmetros da comparação: hash por linha ordenado, independente da ordem das linhas; floats arredondados a 6 casas decimais; datetimes normalizados como `YYYY-MM-DD HH:MM:SS`; leitura via conexão utf8mb4.

(fato) Existe uma segunda verificação independente, `01b_verify_mysql`, contra um contêiner distinto com servidor MySQL 8.0.46, por MD5 por linha excluindo as colunas float/double. Sua saída reporta 35 de 35 tabelas idênticas e 0 linhas divergentes. Não foi executada pelo autor deste registro; a afirmação vem da leitura do código e da saída gravada.

(inferência) As duas verificações diferem em servidor, método e contêiner, e concordam, o que torna a fidelidade da restauração mais bem sustentada do que por uma medida isolada. Ao escrever a dissertação, relatar as duas ou escolher uma e declarar o critério.

## Valores de referência da literatura

Para conferência apenas, não são metas.

| Fonte | Total | BIRT | Eclipse UI | JDT | SWT | Desenvolvedores |
|---|---|---|---|---|---|---|
| Alkhazi et al. (2020) | 22.416 | 4.952 | 6.670 | 6.528 | 4.266 | 252 |
| Kardoost et al. (2022, DevRanker) | 21.098 | 4.178 | 6.495 | 6.274 | 4.151 | não registrado |
| Medido em `bug_and_files` | 21.098 | 4.178 | 6.495 | 6.274 | 4.151 | ver resultados |
| Medido em `bug_commit` | 30.781 | 6.820 | 9.424 | 8.620 | 5.917 | ver resultados |

(fato, 03) `bug_and_files` reproduz DevRanker em todos os projetos. Alkhazi não é reproduzido por nenhuma tabela nem pelo filtro de status testado. DevRanker declara derivar seus dados dos de Alkhazi, complementando-os via API do Bugzilla; Alkhazi declara descartar bugs INVALID e considerar apenas desenvolvedores ativos.

(não confirmado) A causa da diferença de 1.318 bugs (D9), e o número de desenvolvedores de Alkhazi, não verificado contra o dump.

## Organização dos arquivos

```
data/raw/        dump original, somente leitura, fora do git
data/interim/    SQL extraído, bugs.sqlite, zips extraídos, fora do git
scripts/         01_restore.py a 14_verify_mysql.py, common.py, run_all.sh
outputs/         saídas agregadas, uma por script, versionadas
dissertacao/     material por seção da dissertação
registro/        log bruto das sessões, append-only
NOTES.md         registro cronológico por etapa
DECISIONS.md     decisões com evidência, abertas e fechadas
```

(fato) Nenhum nome ou e-mail de desenvolvedor aparece em `outputs/`. Os endereços presentes na lista de contas genéricas (`Birt-Data-inbox@eclipse.org` e similares) são caixas de componente, não pessoais, conforme a regra 5 da seção 7 do CLAUDE.md.
