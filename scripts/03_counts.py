"""03_counts: identificação do projeto e contagens (linhas vs bug_id distintos)."""
from common import *

o = Out("03_counts")
bc = load("bug_commit", cols="id,bug_id,product,component,status,\"commit\",files")
baf = load("bug_and_files", cols="id,bug_id,status")
o("== Identificação do projeto ==")
o("(fato) o dump tem um banco MySQL por projeto (birt, eclipse_platform_ui, jdt, swt, aspectj, tomcat); `bug_commit` não tem coluna de projeto.")
o("`product` não separa os projetos: share do produto majoritário e nº de valores distintos de product/component por projeto.")
rows = []
for p, g in bc.groupby("project"):
    top = g.drop_duplicates("bug_id")["product"].value_counts()
    rows.append((p, g["product"].nunique(), g["component"].nunique(), top.index[0], round(top.iloc[0] / g["bug_id"].nunique(), 3)))
o.table(pd.DataFrame(rows, columns=["projeto", "n_product", "n_component", "product_top", "share_bugs_product_top"]), index=False)

o("\n== Overlap de bug_id entre bancos (bug_commit) ==")
ids = {p: set(g["bug_id"]) for p, g in bc.groupby("project")}
for a in ids:
    o(a, {b: len(ids[a] & ids[b]) for b in ids if b != a})

o("\n== Contagens: linhas e bug_id distintos ==")
rows = []
fixed = bc["status"].str.contains("FIXED")
for p in PROJECTS:
    g = bc[bc.project == p]
    b = baf[baf.project == p]
    rows.append(dict(projeto=p, bc_linhas=len(g), bc_bugs=g.bug_id.nunique(), linhas_por_bug=round(len(g) / g.bug_id.nunique(), 2),
                     bc_bugs_FIXED=g[fixed[g.index]].bug_id.nunique(),
                     baf_linhas=len(b), baf_bugs=b.bug_id.nunique(), baf_subconj_bc=b.bug_id.isin(g.bug_id).all(),
                     ref_Alkhazi=ALKHAZI[p], ref_DevRanker=DEVRANKER[p]))
t = pd.DataFrame(rows)
tot = t.drop(columns=["linhas_por_bug"]).select_dtypes("number").sum()
t = pd.concat([t, pd.DataFrame([{"projeto": "TOTAL", **tot.to_dict()}])], ignore_index=True)
o.table(t, index=False)

o("\n== Grão de bug_commit ==")
rows = []
for p in PROJECTS:
    g = bc[bc.project == p]
    per = g.groupby("bug_id").size()
    dup = g.groupby(["bug_id", "commit"]).size()
    nfiles = g.groupby(["bug_id", "commit"])["files"].nunique()
    rows.append(dict(projeto=p, bugs_1_linha=int((per == 1).sum()), bugs_2mais=int((per > 1).sum()), max_linhas_bug=int(per.max()),
                     pares_bug_commit_repetidos=int((dup > 1).sum()), repetidos_com_files_distintos=int((nfiles > 1).sum()),
                     commit_vazio=int((g["commit"] == "").sum())))
o.table(pd.DataFrame(rows), index=False)
o("\nResultados:")
o("(fato) o grão de bug_commit é bug-commit (e há pares bug_id+commit repetidos); bug_and_files tem exatamente 1 linha por bug_id.")
o("(fato) a soma de bug_and_files por projeto coincide com os valores de DevRanker (21.098); não coincide com Alkhazi (22.416).")
o("(fato) bug_commit tem mais bugs distintos que ambas as referências (30.781 contra 22.416 e 21.098). O único filtro testado aqui (status contendo FIXED, 29.383) não reproduz Alkhazi; outros filtros não foram testados.")
o("(fato) alguns bug_id aparecem em mais de um banco (ex.: 74 entre Eclipse UI e JDT); a chave de um bug precisa ser (projeto, bug_id).")
o("(não confirmado) a causa da diferença 22.416 vs 21.098. Falta: critério de filtro de Alkhazi (INVALID, desenvolvedores ativos), não presente no dump.")
o.save()
