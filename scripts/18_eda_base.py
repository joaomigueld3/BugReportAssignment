"""18_eda_base: análise exploratória sobre a base decidida (D10: bug_commit com resolução FIXED, chave (projeto, bug_id);
D2/D13: rótulo = author do commit, todos os authors do bug são positivos; D4: tempo = primeiro commit - report_time; D6: ordem por report_time).

Descritivo, sem treino de modelo. Split 80/10/10 por contagem de bugs, por projeto, só para medir cold-start e tamanho do pool.
Nenhum nome de desenvolvedor na saída.
"""
from common import *

o = Out("18_eda_base")
bc = load("bug_commit", cols="bug_id,summary,description,report_time,status,component,importance,author,commit_time")
bc = bc[bc.status.str.upper().str.endswith(" FIXED")].copy()
bc["report_time"] = pd.to_datetime(bc.report_time)
bc["commit_time"] = pd.to_datetime(bc.commit_time)
K = ["project", "bug_id"]
bug = bc.groupby(K).agg(report_time=("report_time", "first"), first_commit=("commit_time", "min"), component=("component", "first"),
                        importance=("importance", "first"), summary=("summary", "first"), description=("description", "first"),
                        authors=("author", lambda s: frozenset(s)), n_rows=("author", "size")).reset_index()
bug["n_auth"] = bug.authors.map(len)
bug["days"] = (bug.first_commit - bug.report_time).dt.total_seconds() / 86400
bug = bug.sort_values(["project", "report_time", "bug_id"]).reset_index(drop=True)
pairs = bc.drop_duplicates(K + ["author"])[K + ["author"]].merge(bug[K + ["report_time"]], on=K)
bug["split"] = ""
for p, g in bug.groupby("project"):
    n = len(g)
    lab = np.array(["train"] * int(n * .8) + ["val"] * (int(n * .9) - int(n * .8)) + ["test"] * (n - int(n * .9)))
    bug.loc[g.index, "split"] = lab
pairs = pairs.merge(bug[K + ["split"]], on=K)

o("Base: bug_commit com resolução FIXED, chave (projeto, bug_id). Rótulo: author do commit (todos os authors do bug positivos).")
o("\n== 1. Tamanho da base ==")
t = bug.groupby("project").agg(bugs=("bug_id", "size"), linhas_bug_commit=("n_rows", "sum"))
t["authors_distintos"] = pairs.groupby("project").author.nunique()
t["pares_bug_author"] = pairs.groupby("project").size()
t["positivos_por_bug"] = (t.pares_bug_author / t.bugs).round(3)
t["bugs_2mais_authors"] = bug[bug.n_auth > 1].groupby("project").size()
t["pct_2mais"] = (t.bugs_2mais_authors / t.bugs).round(3)
t.loc["TOTAL"] = [t.bugs.sum(), t.linhas_bug_commit.sum(), np.nan, t.pares_bug_author.sum(), round(t.pares_bug_author.sum() / t.bugs.sum(), 3), t.bugs_2mais_authors.sum(), round(t.bugs_2mais_authors.sum() / t.bugs.sum(), 3)]
o.table(t)
o("Distribuição de authors por bug (nº de bugs):")
o.table(bug.groupby(["n_auth", "project"]).size().unstack(fill_value=0).head(8))
o("\n== 2. Distribuição do rótulo (pares bug-author por author) ==")
rows = []
for p, g in pairs.groupby("project"):
    c = g.author.value_counts()
    rows.append(dict(projeto=p, authors=len(c), mediana=int(c.median()), max=int(c.max()), top1_share=round(c.iloc[0] / c.sum(), 3), top5_share=round(c.head(5).sum() / c.sum(), 3),
                     top10_share=round(c.head(10).sum() / c.sum(), 3), ate_5=int((c <= 5).sum()), ate_10=int((c <= 10).sum()), ge_50=int((c >= 50).sum()), ge_100=int((c >= 100).sum()),
                     gini=round(1 - 2 * (c.sort_values().cumsum() / c.sum()).sum() / len(c) + 1 / len(c), 3)))
o.table(pd.DataFrame(rows), index=False)
o("(top1_share é a prioridade da classe mais frequente, uma estatística da distribuição do rótulo, não de um modelo.)")

o("\n== 3. Cold-start sob split cronológico 80/10/10 por report_time ==")
rows = []
for p in PROJECTS:
    tr = set(pairs[(pairs.project == p) & (pairs.split == "train")].author)
    trc = pairs[(pairs.project == p) & (pairs.split == "train")].author.value_counts()
    for sp in ("val", "test"):
        pp = pairs[(pairs.project == p) & (pairs.split == sp)]
        unseen = ~pp.author.isin(tr)
        bb = bug[(bug.project == p) & (bug.split == sp)]
        allun = pp.assign(u=unseen).groupby("bug_id").u.all()
        few = pp.author.map(trc).fillna(0) < 5
        rows.append(dict(projeto=p, split=sp, bugs=len(bb), pares=len(pp), pares_author_nao_visto=int(unseen.sum()), pct_pares_nao_vistos=round(unseen.mean(), 3),
                         bugs_todos_authors_nao_vistos=int(allun.sum()), pct_bugs_sem_acerto_possivel=round(allun.mean(), 3),
                         pct_pares_author_com_menos_de_5_bugs_no_treino=round(few.mean(), 3), authors_treino=len(tr)))
o.table(pd.DataFrame(rows), index=False)
o("(pct_bugs_sem_acerto_possivel = fração de bugs cujos authors todos estão ausentes do treino; é o teto de perda de qualquer modelo de conjunto fechado.)")

o("\n== 4. Tamanho do pool de candidatos: authors ativos nos 365 dias anteriores ao report_time (bugs de teste) ==")
rows = []
for p in PROJECTS:
    pp = pairs[pairs.project == p]
    te = bug[(bug.project == p) & (bug.split == "test")]
    sizes, all_before = [], []
    for rt in te.report_time:
        w = pp[(pp.report_time < rt) & (pp.report_time >= rt - pd.Timedelta(days=365))]
        sizes.append(w.author.nunique())
        all_before.append(pp[pp.report_time < rt].author.nunique())
    rows.append(dict(projeto=p, teste=len(te), pool_365d_q10=int(np.quantile(sizes, .1)), pool_365d_mediana=int(np.median(sizes)), pool_365d_q90=int(np.quantile(sizes, .9)),
                     pool_historico_mediana=int(np.median(all_before))))
o.table(pd.DataFrame(rows), index=False)

o("\n== 5. Deriva temporal: bugs e authors distintos por ano de report_time ==")
bug["ano"] = bug.report_time.dt.year
pairs["ano"] = pairs.report_time.dt.year
a = bug.groupby(["ano", "project"]).size().unstack(fill_value=0).add_prefix("bugs_")
b = pairs.groupby(["ano", "project"]).author.nunique().unstack(fill_value=0).add_prefix("authors_")
o.table(a.join(b))

o("\n== 6. Tempo até o primeiro commit (D4), dias, base FIXED ==")
rows = []
for p, g in bug.groupby("project"):
    x = g.days
    rows.append(dict(projeto=p, n=len(x), negativos=int((x < 0).sum()), q10=round(x.quantile(.1), 1), mediana=round(x.median(), 1), q90=round(x.quantile(.9), 1), q99=round(x.quantile(.99), 1),
                     max=round(x.max(), 1), gt_365d=int((x > 365).sum())))
o.table(pd.DataFrame(rows), index=False)
o("Variação entre authors (authors com >= 20 bugs): quantis da mediana de dias por author")
rows = []
for p, g in pairs.merge(bug[K + ["days"]], on=K).groupby("project"):
    m = g.groupby("author").agg(n=("days", "size"), med=("days", "median"))
    m = m[m.n >= 20]
    rows.append(dict(projeto=p, authors_ge20=len(m), q10=round(m.med.quantile(.1), 1), q50=round(m.med.median(), 1), q90=round(m.med.quantile(.9), 1)))
o.table(pd.DataFrame(rows), index=False)

o("\n== 7. Prioridade e severidade na base ==")
pat = re.compile(r"^P([1-5]) (\w+)$")
bug["prio"] = bug.importance.map(lambda s: pat.match(s).group(1))
bug["sev"] = bug.importance.map(lambda s: pat.match(s).group(2))
o.table(bug.groupby("project").agg(P3=("prio", lambda s: round((s == "3").mean(), 3)), normal=("sev", lambda s: round((s == "normal").mean(), 3)),
                                   enhancement=("sev", lambda s: round((s == "enhancement").mean(), 3))))
o("Variação entre authors (>= 20 bugs): fração de bugs com severidade 'normal' por author, quantis; e fração com P3")
rows = []
for p, g in pairs.merge(bug[K + ["prio", "sev"]], on=K).groupby("project"):
    m = g.groupby("author").agg(n=("sev", "size"), normal=("sev", lambda s: (s == "normal").mean()), p3=("prio", lambda s: (s == "3").mean()))
    m = m[m.n >= 20]
    rows.append(dict(projeto=p, authors_ge20=len(m), normal_q10=round(m.normal.quantile(.1), 2), normal_q50=round(m.normal.median(), 2), normal_q90=round(m.normal.quantile(.9), 2),
                     p3_q10=round(m.p3.quantile(.1), 2), p3_q50=round(m.p3.median(), 2), p3_q90=round(m.p3.quantile(.9), 2)))
o.table(pd.DataFrame(rows), index=False)

o("\n== 8. Metadados como sinal do rótulo: componente ==")
rows = []
for p, g in pairs.merge(bug[K + ["component"]], on=K).groupby("project"):
    pur = g.groupby(["component", "author"]).size().groupby("component").max().sum() / len(g)
    rows.append(dict(projeto=p, componentes=g.component.nunique(), top_componente_share=round(g.component.value_counts(normalize=True).iloc[0], 3),
                     pureza_em_amostra=round(pur, 3), top1_share_global=round(g.author.value_counts(normalize=True).iloc[0], 3)))
o.table(pd.DataFrame(rows), index=False)
o("(pureza_em_amostra = soma, por componente, do author mais frequente, dividida pelo total de pares; calculada nos mesmos dados, portanto otimista. Compare com top1_share_global.)")

o("\n== 9. Texto na base ==")
PRE = r"^Bug (\d+) [\u2013-] "
pre = bug.summary.str.extract(PRE)[0]
o(f"summary começa com 'Bug <n> – ': {pre.notna().mean():.1%} dos bugs; n igual ao bug_id: {(pre.astype(float) == bug.bug_id)[pre.notna()].mean():.1%}")
o(f"descrição contém 'Bug <bug_id>' do próprio bug: {bug.apply(lambda r: f'Bug {r.bug_id}' in r.description, axis=1).mean():.1%}")
bug["summary_limpo"] = bug.summary.str.replace(PRE, "", regex=True).str.strip()
rows = []
for p, g in bug.groupby("project"):
    sw = g.summary_limpo.str.split().str.len()
    dw = g.description.str.split().str.len().fillna(0)
    tot = sw + dw
    dup = g.summary_limpo.str.lower().duplicated(keep=False)
    rows.append(dict(projeto=p, bugs=len(g), desc_vazia=round((dw == 0).mean(), 3), summary_w_med=int(sw.median()), texto_w_med=int(tot.median()), texto_w_q90=int(tot.quantile(.9)),
                     texto_w_q99=int(tot.quantile(.99)), pct_texto_gt_300w=round((tot > 300).mean(), 3), pct_texto_gt_400w=round((tot > 400).mean(), 3),
                     pct_summary_duplicado_sem_prefixo=round(dup.mean(), 3)))
o.table(pd.DataFrame(rows), index=False)
o("(palavras separadas por espaço, summary sem o prefixo 'Bug <id> – '; tokens WordPiece serão mais numerosos, razão não medida. Quando a descrição é vazia, o texto é só o summary.)")

o("\n== 10. Authors em mais de um projeto (strings idênticas) ==")
sets = {p: set(g.author) for p, g in pairs.groupby("project")}
ps = list(PROJECTS)
o.table(pd.DataFrame({b: {a: len(sets[a] & sets[b]) for a in ps} for b in ps}))
o("(strings idênticas apenas; identidades heterogêneas, D11 aberta, subestimam a sobreposição real.)")
o.save()
