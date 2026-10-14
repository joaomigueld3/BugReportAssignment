"""08_developers: desenvolvedores por projeto, cauda longa, desenvolvedores tardios. Sem nomes na saída."""
from common import *

o = Out("08_developers")
bc = load("bug_commit", cols="bug_id,report_time,assignee,author")
bc["report_time"] = pd.to_datetime(bc.report_time)
bug = bc.groupby(["project", "bug_id"]).agg(report_time=("report_time", "first"), assignee=("assignee", "first")).reset_index()
pairs = bc.drop_duplicates(["project", "bug_id", "author"]).merge(bug[["project", "bug_id"]], on=["project", "bug_id"])
rot = {"assignee (1 por bug)": ("assignee", bug), "author (pares bug-author distintos)": ("author", pairs)}
o("Corte cronológico 80% de report_time por projeto (bugs distintos), usado só para medir desenvolvedores tardios.")
for lab, (col, df) in rot.items():
    o(f"\n===== Rótulo: {lab} =====")
    rows = []
    for p, g in df.groupby("project"):
        cut = bug[bug.project == p].report_time.quantile(0.8)
        cnt = g[col].value_counts()
        first = g.groupby(col).report_time.min()
        tardios = first[first >= cut].index
        n_late_bugs = int(g[g.report_time >= cut][col].isin(tardios).sum())
        n_after = int((g.report_time >= cut).sum())
        rows.append(dict(projeto=p, devs=len(cnt), mediana_bugs=int(cnt.median()), max_bugs=int(cnt.max()), devs_ate_5=int((cnt <= 5).sum()), devs_ate_10=int((cnt <= 10).sum()),
                         top5_share=round(cnt.head(5).sum() / cnt.sum(), 3), top10_share=round(cnt.head(10).sum() / cnt.sum(), 3),
                         devs_so_apos_corte=len(tardios), itens_pos_corte=n_after, itens_de_devs_nao_vistos=n_late_bugs,
                         pct_nao_vistos=round(n_late_bugs / n_after, 3)))
    o.table(pd.DataFrame(rows), index=False)
    o("Número de desenvolvedores com >= k itens:")
    ks = [1, 5, 10, 20, 50, 100]
    o.table(pd.DataFrame({p: [int((g[col].value_counts() >= k).sum()) for k in ks] for p, g in df.groupby("project")}, index=[f">={k}" for k in ks]))
    ng = df[~df[col].str.contains(GENERIC)] if col == "assignee" else df
    if col == "assignee":
        o("assignee excluindo contas genéricas (regex de 06): devs distintos por projeto:", ng.groupby("project")[col].nunique().to_dict(),
          "; bugs removidos:", (len(df) - len(ng)))
o("\nResultados:")
o("(fato) 'itens_de_devs_nao_vistos' = itens após o corte de 80% cujo desenvolvedor só aparece pela primeira vez depois do corte (cold-start para o split cronológico).")
o("(fato) author é um identificador heterogêneo (ver 06), então a contagem de authors distintos pode superestimar pessoas; a de assignee inclui contas genéricas.")
o("(inferência) com 42 a 55 authors em SWT e JDT contra 143 em Eclipse UI, os dois primeiros têm espaço de classes pequeno (ameaça a declarar), o que é consistente com a observação da literatura citada no CLAUDE.md (número de desenvolvedores por projeto não verificado contra Alkhazi).")
o.save()
