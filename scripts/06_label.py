"""06_label: concordância assignee x author e contas genéricas/de triagem."""
from common import *

o = Out("06_label")
bc = load("bug_commit", cols="bug_id,assignee,author")
bc["generic"] = bc["assignee"].str.contains(GENERIC)
o("== Nível linha (bug-commit): assignee == author (string exata) ==")
rows = []
for p, g in bc.groupby("project"):
    rows.append(dict(projeto=p, linhas=len(g), iguais=int((g.assignee == g.author).sum()), pct=round((g.assignee == g.author).mean(), 3),
                     pct_iguais_assignee_nao_generico=round((g[~g.generic].assignee == g[~g.generic].author).mean(), 3)))
o.table(pd.DataFrame(rows), index=False)

o("\n== Nível bug: assignee é um dos authors do bug? ==")
rows = []
for p, g in bc.groupby("project"):
    per = g.groupby("bug_id").agg(assignee=("assignee", "first"), generic=("generic", "first"), authors=("author", lambda s: set(s)))
    per["n_authors"] = per.authors.map(len)
    per["assg_in_authors"] = [a in s for a, s in zip(per.assignee, per.authors)]
    per["so_assg"] = [s == {a} for a, s in zip(per.assignee, per.authors)]
    ng = per[~per.generic]
    rows.append(dict(projeto=p, bugs=len(per), bugs_assignee_generico=int(per.generic.sum()), pct_generico=round(per.generic.mean(), 3),
                     bugs_com_2mais_authors=int((per.n_authors > 1).sum()), assg_em_authors=int(per.assg_in_authors.sum()),
                     pct_assg_em_authors_nao_gen=round(ng.assg_in_authors.mean(), 3), pct_unico_author_igual_assg_nao_gen=round(ng.so_assg.mean(), 3),
                     bugs_nao_gen_divergentes=int((~ng.assg_in_authors).sum())))
o.table(pd.DataFrame(rows), index=False)

o("\n== Formato dos identificadores: author sem espaço (parece login) vs assignee ==")
rows = []
for p, g in bc.groupby("project"):
    a_set, s_set = set(g.assignee), set(g.author)
    rows.append(dict(projeto=p, authors_distintos=len(s_set), authors_sem_espaco=sum(" " not in x for x in s_set),
                     authors_que_nunca_aparecem_como_assignee=len(s_set - a_set), assignees_distintos=len(a_set),
                     assignees_genericos=sum(bool(GENERIC.search(x)) for x in a_set)))
o.table(pd.DataFrame(rows), index=False)

o("\n== Contas genéricas/de triagem mais frequentes (bugs distintos; nomes de conta, não de pessoas) ==")
for p, g in bc[bc.generic].groupby("project"):
    o(f"[{p}]")
    o.table(g.drop_duplicates("bug_id").assignee.value_counts().head(8).rename("bugs").to_frame())
o("\nResultados:")
o("(fato) a regra de conta genérica usada é a regex /inbox|triaged|^birt-/ (heurística minha, não validada); a lista acima permite conferência. Contas como 'Birt-ReportDesigner' podem ser componentes, não pessoas (inferência).")
o("(fato) parte dos authors não tem espaço no nome (parecem logins; tabela acima) e muitos authors nunca aparecem como assignee, então a igualdade de strings subestima a concordância real; unificar identidades exige uma decisão metodológica (DECISIONS.md).")
o("(não confirmado) se author == pessoa que corrigiu: o dump não tem o mapeamento login->nome.")
o.save()
