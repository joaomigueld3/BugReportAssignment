"""13_features_sanity: D8. Inspeção de ExtractedFeatures.zip e SVMrank_Models.zip e mapeamento para bug_id do dump.

Entrada: data/interim/zips/ (extraído dos .zip do repositório). Sem nomes de desenvolvedores na saída.
"""
import numpy as np
from common import *

import zipfile

Z = os.path.join(ROOT, "data/interim/zips")
for zname in ("ExtractedFeatures.zip", "SVMrank_Models.zip"):
    zipfile.ZipFile(os.path.join(ROOT, zname)).extractall(Z)
o = Out("13_features_sanity")
bc = load("bug_commit", cols="bug_id,report_time,commit_time,assignee,author")
bugs = {p: set(g.bug_id) for p, g in bc.groupby("project")}
baf = load("bug_and_files", cols="bug_id")
baf_ids = {p: set(g.bug_id) for p, g in baf.groupby("project")}
ds = {}
for ap, suf, nf in (("OurNewApproach", "New", 18), ("PreviousApproach", "Previous", 14)):
    for k in (1, 2, 3):
        df = pd.read_csv(f"{Z}/ExtractedFeatures/{ap}/Fold{k}_{suf}.csv", header=None)
        assert df.shape[1] == 3 + nf + 1, df.shape
        df.columns = ["qid", "bug_id", "dev"] + [f"f{i}" for i in range(1, nf + 1)] + ["label"]
        ds[(ap, k)] = df
o("== Formato dos CSV (sem cabeçalho): qid, bug_id, dev, features, label ==")
rows = []
for (ap, k), d in ds.items():
    g = d.groupby("qid")
    rows.append(dict(abordagem=ap, fold=k, linhas=len(d), n_feat=d.shape[1] - 4, qids=d.qid.nunique(), bug_ids=d.bug_id.nunique(), devs=d.dev.nunique(),
                     cand_por_qid_min=int(g.size().min()), cand_por_qid_max=int(g.size().max()), qid_min=int(d.qid.min()), qid_max=int(d.qid.max()),
                     qids_sem_positivo=int((g.label.sum() == 0).sum()), qids_mais_de_1_positivo=int((g.label.sum() > 1).sum()), labels=sorted(d.label.unique().tolist())))
o.table(pd.DataFrame(rows), index=False)

o("\n== Mesmos (qid,bug_id,dev) nos três folds? ==")
for ap in ("OurNewApproach", "PreviousApproach"):
    keys = [set(zip(ds[(ap, k)].qid, ds[(ap, k)].bug_id, ds[(ap, k)].dev)) for k in (1, 2, 3)]
    bk = [set(ds[(ap, k)].bug_id) for k in (1, 2, 3)]
    o(ap, "| chaves (qid,bug,dev) iguais entre folds:", keys[0] == keys[1] == keys[2], "| conjuntos de bug_id iguais:", bk[0] == bk[1] == bk[2])
d1, d2, d3 = (ds[("OurNewApproach", k)] for k in (1, 2, 3))
o("bug_id da linha i coincide entre fold1 e fold2?", bool((d1.bug_id.values == d2.bug_id.values).all()), "| qid coincide?", bool((d1.qid.values == d2.qid.values).all()))
o("Bugs distintos nos CSV:", d1.bug_id.nunique(), "| qids distintos por fold:", d1.qid.nunique(), d2.qid.nunique(), d3.qid.nunique())

o("\n== Um mesmo bug_id aparece com vários qid? ==")
for k in (1, 2, 3):
    d = ds[("OurNewApproach", k)]
    per = d.groupby("bug_id").qid.nunique()
    o(f"fold{k}: bug_ids com >1 qid: {int((per > 1).sum())} de {len(per)}")

o("\n== Features da abordagem anterior == subconjunto das da nova? (primeiras 14 colunas) ==")
for k in (1, 2, 3):
    a, b = ds[("OurNewApproach", k)], ds[("PreviousApproach", k)]
    same = np.allclose(a[[f"f{i}" for i in range(1, 15)]].values, b[[f"f{i}" for i in range(1, 15)]].values)
    o(f"fold{k}: f1..f14 idênticas: {same}; label idêntico: {bool((a.label.values == b.label.values).all())}")

o("\n== Linhas 'todas zero' (desenvolvedor sem histórico no fold) ==")
for (ap, k), d in ds.items():
    if ap != "OurNewApproach":
        continue
    z = (d[[f"f{i}" for i in range(1, 19)]].abs().sum(axis=1) == 0)
    o(f"fold{k}: linhas com 18 features = 0: {int(z.sum())} ({z.mean():.1%}); desses, positivos: {int(d.label[z].sum())}")

o("\n== Mapeamento bug_id para o dump ==")
allb = ds[("OurNewApproach", 1)].bug_id.drop_duplicates()
rows = []
for p in PROJECTS:
    rows.append(dict(projeto=p, bugs_csv_em_bug_commit=int(allb.isin(bugs[p]).sum()), bugs_csv_em_bug_and_files=int(allb.isin(baf_ids[p]).sum()),
                     bugs_bug_commit=len(bugs[p]), bugs_bug_and_files=len(baf_ids[p])))
o.table(pd.DataFrame(rows), index=False)
o("bugs do CSV sem match em nenhum dos 4 projetos:", int((~allb.isin(set().union(*bugs.values()))).sum()))
o("bugs do CSV presentes em mais de 1 projeto do dump (ambíguos):", int((pd.Series([sum(b in bugs[p] for p in PROJECTS) for b in allb]) > 1).sum()))

o("\n== Rótulo (label=1) vs assignee/author do dump, para bugs do projeto de melhor match ==")
best = max(PROJECTS, key=lambda p: allb.isin(bugs[p]).sum())
o("projeto de melhor match:", best)
g = bc[bc.project == best]
ref = g.groupby("bug_id").agg(assignee=("assignee", "first"), authors=("author", lambda s: set(s))).reset_index()
rows = []
for k in (1, 2, 3):
    d = ds[("OurNewApproach", k)]
    pos = d[d.label == 1][["qid", "bug_id", "dev"]].merge(ref, on="bug_id", how="left")
    m = pos.assignee.notna()
    rows.append(dict(fold=k, positivos=len(pos), com_match_no_dump=int(m.sum()), dev_eq_assignee=int((pos.dev == pos.assignee)[m].sum()),
                     dev_em_authors=int(sum(dv in a for dv, a in zip(pos.dev[m], pos.authors[m])))))
o.table(pd.DataFrame(rows), index=False)

o("\n== Positivos por fold: desenvolvedores distintos e candidatos vs authors/assignees do projeto ==")
u = bc[bc.project == best]
for k in (1, 2, 3):
    d = ds[("OurNewApproach", k)]
    pv = d[d.label == 1]
    o(f"fold{k}: positivos={len(pv)}; devs distintos entre positivos={pv.dev.nunique()}; maior dev concentra {pv.dev.value_counts().iloc[0] / len(pv):.1%}")
cand = set(d1.dev)
o(f"candidatos por query={len(cand)}; presentes como author no dump={len(cand & set(u.author))} (authors distintos no dump={u.author.nunique()}); como assignee={len(cand & set(u.assignee))} (assignees distintos={u.assignee.nunique()})")
q1 = d1.drop_duplicates("qid")
last_c = bc[bc.project == best].assign(commit_time=lambda x: pd.to_datetime(x.commit_time)).groupby("bug_id").commit_time.max()
o("ordem das queries (fold1) por commit_time do último commit no dump é decrescente:", bool(last_c.reindex(q1.bug_id.drop_duplicates()).is_monotonic_decreasing))
nq = d1.groupby("bug_id").qid.nunique()
nr = u[u.bug_id.isin(nq.index)].groupby("bug_id").size()
o(f"queries por bug no CSV == linhas bug_commit do bug: {(nq == nr).mean():.1%} dos {len(nq)} bugs")

o("\n== Cobertura do ID do bug no tempo: report_time dos bugs do CSV ==")
rt = bc[bc.project == best].drop_duplicates("bug_id").set_index("bug_id").report_time
rt = pd.to_datetime(rt.reindex(allb.values).dropna())
o("bugs do CSV com report_time no dump:", len(rt), "| min:", rt.min(), "| max:", rt.max())

o("\n== Arquivos .dat (SVMrank) ==")
for ap, suf in (("OurNewApproach", "New"), ("PreviousApproach", "Previous")):
    for k in (1, 2, 3):
        lines = open(f"{Z}/SVMrank_Models/{ap}/SVMrank_Input/Fold{k}_{suf}.dat").read().splitlines()
        q = [int(l.split()[1].split(":")[1]) for l in lines]
        d = ds[(ap, k)]
        o(f"{ap} fold{k}.dat: linhas={len(lines)}; qid igual ao CSV: {q == d.qid.tolist()}; ranks distintos: {sorted(set(int(l.split()[0]) for l in lines))}")
for ap, suf in (("OurNewApproach", "New"), ("PreviousApproach", "Previous")):
    for k in (2, 3):
        t = open(f"{Z}/SVMrank_Models/{ap}/TrainedOnFold{k}_{suf}.dat").read().splitlines()
        info = {l.split("#")[1].strip(): l.split("#")[0].strip() for l in t[1:10] if "#" in l}
        o(f"{ap} TrainedOnFold{k}: kernel={info.get('kernel type')} (0=linear), highest feature={info.get('highest feature index')}, training documents={info.get('number of training documents')}")
o.save()
