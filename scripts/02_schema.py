"""02_schema: tabelas, colunas e tipos reais; divergências em relação ao README."""
import re
from common import *

README = ["id", "bug_id", "summary", "description", "report_time", "reporter", "assignee", "status",
          "product", "component", "importance", "commit", "author", "commit_time", "log", "files"]
o = Out("02_schema")
sql = open(os.path.join(ROOT, "data/interim/SQL_BugDatabase_Dump.sql"), encoding="utf-8", newline="").read()
o("Cabeçalho do dump:", re.search(r"-- MySQL dump [^\r\n]+", sql).group(0))
o("Servidor:", re.search(r"-- Server version\s+(\S+)", sql).group(1))
o("Bancos criados:", ", ".join(re.findall(r"CREATE DATABASE\s+IF NOT EXISTS `(\w+)`", sql)))
o("Engine/charset declarados:", set(re.findall(r"ENGINE=(\w+)", sql)), set(re.findall(r"DEFAULT CHARSET=(\w+)", sql)))
c = con()
o("\n== Todas as tabelas (linhas, colunas) ==")
rows = []
for (t,) in c.execute("select name from sqlite_master where type='table' order by 1").fetchall():
    n = c.execute(f'select count(*) from "{t}"').fetchone()[0]
    cols = [r[1] for r in c.execute(f'pragma table_info("{t}")')]
    rows.append((t, n, len(cols), ",".join(cols)))
o.table(pd.DataFrame(rows, columns=["tabela", "linhas", "ncols", "colunas"]), index=False, max_colwidth=90)
o("\n== bug_commit: tipos MySQL declarados por projeto e divergência com o README ==")
for name, db in PROJECTS.items():
    m = re.search(r"USE `%s`;.*?CREATE TABLE `bug_commit` \((.*?)\) ENGINE" % db, sql, re.S)
    decl = re.findall(r"`(\w+)` (\w+(?:\(\d+\))?)", m.group(1))
    cols = [d[0] for d in decl]
    o(f"{name}: colunas={len(cols)}; faltando vs README={set(README) - set(cols) or '-'}; extras={set(cols) - set(README) or '-'}; ordem igual={cols == README}")
    if name == "BIRT":
        o("  tipos:", ", ".join(f"{a}:{b}" for a, b in decl))
o("\nColunas só em bug_and_files (vs bug_commit):",
  sorted(set(r[1] for r in c.execute('pragma table_info("jdt__bug_and_files")')) - set(r[1] for r in c.execute('pragma table_info("jdt__bug_commit")'))))
o("Colunas de bug_commit ausentes em bug_and_files:",
  sorted(set(r[1] for r in c.execute('pragma table_info("jdt__bug_commit")')) - set(r[1] for r in c.execute('pragma table_info("jdt__bug_and_files")'))))
o("\nAchados: (fato) cada projeto é um banco MySQL separado; `bug_commit` tem exatamente as colunas do README.")
o("(fato) nenhuma coluna de data de resolução ou de atribuição existe em bug_commit.")
o.save()
