"""14_alkhazi_filter: D9. Busca em grade de filtros sobre bug_commit que reproduzam os tamanhos de Alkhazi (2020).

Alvos por projeto: BIRT 4952, UI 6670, JDT 6528, SWT 4266 (total 22.416), com 252 desenvolvedores.
Exploração: nenhum filtro testado é afirmado como o de Alkhazi; reportamos só o que reproduz ou não.
"""
import itertools

from common import *

o = Out("14_alkhazi_filter")
bc = load("bug_commit", cols="bug_id,status,product,assignee,author,report_time,commit_time")
bc["res"] = bc.status.str.split().str[1].fillna("")
bc["st"] = bc.status.str.split().str[0].fillna("")
TARGET = pd.Series(ALKHAZI)
STAT = {
    "todos": lambda d: d.status == d.status,
    "FIXED": lambda d: d.res == "FIXED",
    "FIXED+WONTFIX": lambda d: d.res.isin(["FIXED", "WONTFIX"]),
    "sem INVALID": lambda d: d.res != "INVALID",
    "sem INVALID/WORKSFORME/NOT_ECLIPSE": lambda d: ~d.res.isin(["INVALID", "WORKSFORME", "NOT_ECLIPSE"]),
    "resolvidos (qualquer resolução)": lambda d: d.res != "",
    "resolvidos sem INVALID": lambda d: (d.res != "") & (d.res != "INVALID"),
    "resolvidos sem INVALID/WORKSFORME/NOT_ECLIPSE": lambda d: (d.res != "") & ~d.res.isin(["INVALID", "WORKSFORME", "NOT_ECLIPSE"]),
}
MAINP = {"BIRT": "BIRT", "Eclipse UI": "Platform", "JDT": "JDT", "SWT": "Platform"}
res = []
for sname, sf in STAT.items():
    for prod in ("qualquer", "principal"):
        base = bc[sf(bc)]
        if prod == "principal":
            base = base[base.apply(lambda r: r["product"] == MAINP[r["project"]], axis=1)]
        for lab in ("author", "assignee"):
            for k in [0, 1, 2, 3, 5, 10, 20, 30, 50, 100]:
                for mode in ("algum", "todos"):
                    if k == 0 and mode == "todos":
                        continue
                    cnt, devs = {}, 0
                    for p, g in base.groupby("project"):
                        pairs = g.drop_duplicates(["bug_id", lab])
                        nb = pairs.groupby(lab).bug_id.nunique()
                        act = set(nb[nb >= k].index) if k else set(nb.index)
                        pairs = pairs.assign(a=pairs[lab].isin(act))
                        per = pairs.groupby("bug_id").a.agg("any" if mode == "algum" else "all")
                        cnt[p] = int(per.sum())
                        devs += len(act)
                    s = pd.Series(cnt).reindex(list(ALKHAZI))
                    res.append(dict(status=sname, produto=prod, rotulo=lab, k_min_bugs=k, modo=mode, **{p: s[p] for p in ALKHAZI}, total=int(s.sum()), devs_soma=devs,
                                    erro_abs=int((s - TARGET).abs().sum()), exatos=int((s == TARGET).sum())))
r = pd.DataFrame(res).sort_values("erro_abs")
o(f"Configurações testadas: {len(r)}. Alvo: {ALKHAZI}, total 22.416; desenvolvedores 252.")
o("\n== 15 melhores (menor erro absoluto somado nos 4 projetos) ==")
o.table(r.head(15), index=False)
o(f"\nConfigurações com os 4 projetos exatos: {int((r.exatos == 4).sum())}; com algum projeto exato: {int((r.exatos >= 1).sum())}.")
o("Melhor erro por 'status' (todas as demais dimensões livres):")
o.table(r.groupby("status").erro_abs.min().sort_values().to_frame())
near = r[(r.total - 22416).abs() <= 150]
o(f"\nConfigurações com total entre 22.266 e 22.566: {len(near)}")
o.table(near.head(10), index=False)
d252 = r[(r.devs_soma - 252).abs() <= 15]
o(f"\nConfigurações com soma de desenvolvedores entre 237 e 267 (alvo 252): {len(d252)}; melhor erro absoluto entre elas: {int(d252.erro_abs.min()) if len(d252) else 'n/a'}")
o.table(d252.head(5), index=False)
o("\n== Considerações ==")
o("(fato) a melhor configuração por tamanho (erro 1.837) fica no limite da grade (k=100) e tem apenas ~69 desenvolvedores; as que têm ~252 desenvolvedores têm erro muito maior. Nenhuma combinação satisfaz tamanho e número de desenvolvedores.")
o("(não confirmado) o critério de Alkhazi: seguem hipóteses não testadas (limiar de 'ativo' por período, deduplicação de identidades, uso de outra fonte de bugs).")
o("(fato) bug_and_files (21.098) é menor que o alvo em todos os projetos, então não pode ser a base de Alkhazi sem acréscimo.")
o("(fato) o resultado acima vale somente para os filtros da grade. Autores/assignees ativos foram definidos por número mínimo de bugs no projeto, definição minha.")
o.save()
