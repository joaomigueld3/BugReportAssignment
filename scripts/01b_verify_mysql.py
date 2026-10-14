"""01b_verify_mysql: compara a restauração em MySQL real (container Docker `bugtriage-mysql`) com o SQLite do script 01.

Por tabela: contagem de linhas e multiconjunto de MD5 por linha (todas as colunas exceto float/double,
cujo texto difere entre MySQL e SQLite). Pré-requisito: container com o dump já restaurado (ver NOTES.md).
"""
import hashlib
import subprocess
from collections import Counter

from common import *

CT = "bugtriage-mysql"


def mysql(sql):
    r = subprocess.run(["docker", "exec", "-i", "-e", "MYSQL_PWD=local_only_pw", CT, "mysql", "-uroot", "--default-character-set=utf8mb4", "-B", "-N", "--quick"],
                       input=sql, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout


o = Out("01b_verify_mysql")
o("Servidor de comparação:", mysql("select version()").strip(), "| character_set_server:", mysql("select @@character_set_server").strip())
c = con()
meta = mysql("select table_schema, table_name, column_name, data_type from information_schema.columns "
             "where table_schema in ('tomcat','birt','aspectj','api_descriptions','eclipse_platform_ui','jdt','swt') order by 1,2,ordinal_position")
tabs = {}
for line in meta.splitlines():
    s, t, col, dt = line.split("\t")
    tabs.setdefault((s, t), []).append((col, dt))
rows = []
for (s, t), cols in tabs.items():
    use = [col for col, dt in cols if dt not in ("float", "double", "decimal")]
    sk = [col for col, dt in cols if dt in ("float", "double", "decimal")]
    expr = ",".join(f"IFNULL(CAST(`{c_}` AS CHAR CHARACTER SET utf8mb4),'<N>')" for c_ in use)
    out = mysql(f"select MD5(CONCAT_WS(CHAR(31),{expr})) from `{s}`.`{t}`;")
    h_my = Counter(out.splitlines())
    n_my = int(mysql(f"select count(*) from `{s}`.`{t}`").strip())
    qcols = ",".join(f'"{c_}"' for c_ in use)
    h_sq = Counter()
    for r in c.execute(f'select {qcols} from "{s}__{t}"'):
        h_sq[hashlib.md5(chr(31).join("<N>" if v is None else str(v) for v in r).encode("utf-8")).hexdigest()] += 1
    n_sq = c.execute(f'select count(*) from "{s}__{t}"').fetchone()[0]
    same = h_my == h_sq
    diff = sum((h_my - h_sq).values())
    rows.append(dict(tabela=f"{s}.{t}", linhas_mysql=n_my, linhas_sqlite=n_sq, colunas_hash=len(use), colunas_float_ignoradas=len(sk), hashes_identicos=same, linhas_divergentes=diff))
df = pd.DataFrame(rows)
o.table(df, index=False)
o(f"\nTabelas: {len(df)}; com hashes idênticos: {int(df.hashes_identicos.sum())}; linhas divergentes no total: {int(df.linhas_divergentes.sum())}.")
o("(fato) comparação linha a linha por MD5 do texto das colunas não float; colunas float/double não foram comparadas.")
o.save()
