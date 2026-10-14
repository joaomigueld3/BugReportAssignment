"""14_verify_mysql: compara o SQLite (parser próprio, script 01) com uma restauração real em MySQL 8.0.12 (Docker).

Pré-requisito: contêiner `bugdump-mysql` ativo com o dump restaurado (ver NOTES.md, Etapa 13).
Por tabela: contagem de linhas e SHA-256 do conteúdo (hash por linha, ordenado, independe da ordem das linhas).
"""
import hashlib
import sqlite3

import pymysql
from common import *

o = Out("14_verify_mysql")
my = pymysql.connect(host="127.0.0.1", port=33306, user="root", password="local_only_pw", charset="utf8mb4")
sq = con()


def canon(v):
    if v is None:
        return "N"
    if isinstance(v, float):
        return "F" + repr(round(v, 6))
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf8", "replace")
    if hasattr(v, "strftime"):
        v = v.strftime("%Y-%m-%d %H:%M:%S")
    return ("I" + str(v)) if isinstance(v, int) else ("S" + str(v))


def digest(rows):
    hs = sorted(hashlib.sha256("\x1f".join(canon(c) for c in r).encode("utf8", "surrogatepass")).hexdigest() for r in rows)
    return len(hs), hashlib.sha256("".join(hs).encode()).hexdigest()


cur = my.cursor()
cur.execute("select version()")
o("Servidor MySQL:", cur.fetchone()[0])
rows, bad = [], []
cur.execute("select table_schema, table_name from information_schema.tables where table_schema not in ('mysql','sys','information_schema','performance_schema') order by 1,2")
tabs = cur.fetchall()
for db, t in tabs:
    cur2 = my.cursor(pymysql.cursors.SSCursor)
    cur2.execute(f"select * from `{db}`.`{t}`")
    n_m, h_m = digest(cur2)
    cur2.close()
    n_s, h_s = digest(sq.execute(f'select * from "{db}__{t}"'))
    ok = (n_m, h_m) == (n_s, h_s)
    rows.append(dict(tabela=f"{db}.{t}", linhas_mysql=n_m, linhas_sqlite=n_s, hash_igual=ok))
    if not ok:
        bad.append((db, t))
o.table(pd.DataFrame(rows), index=False)
o(f"\nTabelas comparadas: {len(rows)} (SQLite tem {len(sq.execute(chr(115)+'elect name from sqlite_master where type=' + repr('table')).fetchall())}); divergentes: {len(bad)} {bad}")
o.save()
