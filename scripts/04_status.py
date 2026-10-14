"""04_status: distribuição de status por projeto (bugs distintos)."""
from common import *

def grp(s):
    s = s.strip()
    if s == "":
        return "vazio"
    st, _, res = s.upper().partition(" ")
    if res == "FIXED":
        return "fechado FIXED"
    if res:
        return "resolvido outro (" + res + ")"
    return "aberto (" + st + ")"

o = Out("04_status")
raw = load("bug_commit", cols="bug_id,status")
incons = int((raw.groupby(["project", "bug_id"])["status"].nunique() > 1).sum())
bc = raw.drop_duplicates(["project", "bug_id"])
bc = bc.assign(status=bc["status"].replace("", "(vazio)"))
baf = load("bug_and_files", cols="bug_id,status")
o("== bug_commit: status completo, bugs distintos ==")
o(f"bugs com mais de um status entre suas linhas: {incons}")
o.table(bc.groupby(["status", "project"]).size().unstack(fill_value=0).assign(total=lambda d: d.sum(axis=1)).sort_values("total", ascending=False))
bc["grupo"] = bc["status"].map(grp)
o("\n== bug_commit: grupos de status, bugs distintos ==")
o.table(bc.groupby(["grupo", "project"]).size().unstack(fill_value=0).assign(total=lambda d: d.sum(axis=1)).sort_values("total", ascending=False))
o("\n== bug_and_files: status (1 linha por bug) ==")
o.table(baf.groupby(["status", "project"]).size().unstack(fill_value=0).assign(total=lambda d: d.sum(axis=1)))
o("\nResultados:")
n_open = bc["grupo"].str.startswith(("aberto", "vazio")).sum()
o(f"(fato) em bug_commit há {n_open} bugs distintos com status aberto (NEW, ASSIGNED, REOPENED) ou vazio, apesar de terem commit vinculado; a hipótese 'só bugs fechados' é refutada para bug_commit.")
o("(fato) em bug_and_files só há status resolvido (fixed ou wontfix), em minúsculas; é um subconjunto filtrado.")
o("(inferência) bugs com commit vinculado e status aberto/vazio podem ser commits que citam o bug sem resolvê-lo; não confirmado, falta inspecionar `log`.")
o("(fato) nenhuma linha de bug_commit tem `commit` vazio (ver 03); bugs WONTFIX/INVALID/WORKSFORME/NOT_ECLIPSE com commit aparecem (574 bugs distintos), logo nem todo bug em bug_commit foi corrigido.")
o("(inferência) bugs atribuídos que nunca receberam commit não estão no dump, o que subestimaria o workload (limitação 2). Não confirmado: o dump não traz a população de bugs sem commit para medir o tamanho do viés; faltaria uma exportação do Bugzilla.")
o.save()
