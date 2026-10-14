"""01_restore: carrega o dump MySQL (8.0.12) em SQLite, reexecutável do zero.

Entrada : data/raw/SQL_BugDatabase_Dump.7z (extraído para data/interim/)
Saída   : data/interim/bugs.sqlite (tabelas nomeadas <banco>__<tabela>)
          outputs/01_restore.txt (contagens e checagens)

O parser é próprio (não há MySQL/Docker no ambiente). Validações: cada tupla
deve ter exatamente o número de colunas do CREATE TABLE e nenhum byte pode
sobrar entre tuplas.
"""
import os
import re
import sqlite3
import sys

import py7zr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data/raw/SQL_BugDatabase_Dump.7z")
SQL = os.path.join(ROOT, "data/interim/SQL_BugDatabase_Dump.sql")
DB = os.path.join(ROOT, "data/interim/bugs.sqlite")
OUT = os.path.join(ROOT, "outputs/01_restore.txt")

if not os.path.exists(SQL):
    py7zr.SevenZipFile(RAW).extract(path=os.path.dirname(SQL))

TOKEN = re.compile(r"'((?:[^'\\]|\\.|'')*)'|(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)|(NULL)|([(),;])", re.S)
ESC = {"0": "\0", "'": "'", '"': '"', "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a", "\\": "\\"}
UNESC = re.compile(r"\\(.)|''", re.S)


def unescape(s):
    if "\\" not in s and "''" not in s:
        return s
    return UNESC.sub(lambda m: "'" if m.group(0) == "''" else ESC.get(m.group(1), m.group(1)), s)


def parse_values(body, ncols):
    """body = texto após 'VALUES ' sem o ';' final. Gera tuplas."""
    row, pos, n = None, 0, len(body)
    for m in TOKEN.finditer(body):
        if m.start() != pos:
            gap = body[pos:m.start()].strip()
            if gap:
                raise ValueError(f"bytes não reconhecidos: {gap[:60]!r}")
        pos = m.end()
        s, num, null, punct = m.groups()
        if punct == "(":
            row = []
        elif punct == ")":
            if len(row) != ncols:
                raise ValueError(f"tupla com {len(row)} colunas, esperado {ncols}")
            yield tuple(row)
            row = None
        elif punct in (",", ";"):
            pass
        elif s is not None:
            row.append(unescape(s))
        elif num is not None:
            row.append(float(num) if ("." in num or "e" in num.lower()) else int(num))
        elif null:
            row.append(None)
    if body[pos:].strip():
        raise ValueError(f"resto não consumido: {body[pos:pos+60]!r}")


def sqltype(coldef):
    t = coldef.split()[1].lower()
    if t.startswith(("int", "bigint", "tinyint", "smallint")):
        return "INTEGER"
    if t.startswith(("float", "double", "decimal")):
        return "REAL"
    return "TEXT"


if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
cur = con.cursor()
report = []
db = table = None
cols = []
in_create = False
with open(SQL, encoding="utf-8", errors="strict", newline="") as f:
    for line in f:
        line = line.rstrip("\r\n")
        m = re.match(r"CREATE DATABASE.*?`(\w+)`", line)
        if m:
            continue
        m = re.match(r"USE `(\w+)`;", line)
        if m:
            db = m.group(1)
            continue
        m = re.match(r"CREATE TABLE `(\w+)` \(", line)
        if m:
            table, cols, in_create = m.group(1), [], True
            continue
        if in_create:
            m = re.match(r"\s+`(\w+)` (.*?),?$", line)
            if m:
                cols.append((m.group(1), sqltype(f"{m.group(1)} {m.group(2)}")))
            elif line.startswith(")"):
                name = f"{db}__{table}"
                cur.execute(f'CREATE TABLE "{name}" (' + ", ".join(f'"{c}" {t}' for c, t in cols) + ")")
                in_create = False
            continue
        if line.startswith("INSERT INTO `"):
            m = re.match(r"INSERT INTO `(\w+)` VALUES (.*);$", line, re.S)
            assert m and m.group(1) == table, line[:80]
            name = f"{db}__{table}"
            ph = ",".join("?" * len(cols))
            cur.executemany(f'INSERT INTO "{name}" VALUES ({ph})', parse_values(m.group(2), len(cols)))
con.commit()

tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")]
report.append(f"sqlite {sqlite3.sqlite_version}; tabelas: {len(tabs)}")
report.append("tabela | linhas | colunas")
for t in tabs:
    n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    nc = len(cur.execute(f'PRAGMA table_info("{t}")').fetchall())
    report.append(f"{t} | {n} | {nc}")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write("\n".join(report) + "\n")
print("\n".join(report))
