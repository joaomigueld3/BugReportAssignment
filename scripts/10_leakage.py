"""10_leakage: vazamento temporal no Ramo B sob corte cronológico 80/10/10 por report_time.

Para cada bug de teste t (último 10%), conta bugs de treino (primeiros 80%) cujo commit_time
é posterior ao report_time de t, i.e. cuja correção ainda não havia ocorrido na data de referência.
Usa todos os bugs de teste (sem amostragem, logo sem semente).
bug-level commit_time: primeiro commit (min) e último commit (max).
"""
import numpy as np
from common import *

o = Out("10_leakage")
bc = load("bug_commit", cols="bug_id,report_time,commit_time")
bc["report_time"] = pd.to_datetime(bc.report_time)
bc["commit_time"] = pd.to_datetime(bc.commit_time)
baf_ids = load("bug_and_files", cols="bug_id")
baf_key = set(zip(baf_ids.project, baf_ids.bug_id))
b = bc.groupby(["project", "bug_id"]).agg(report_time=("report_time", "first"), first_c=("commit_time", "min"), last_c=("commit_time", "max")).reset_index()
b["in_baf"] = [(p, i) in baf_key for p, i in zip(b.project, b.bug_id)]
pops = {"bug_commit (todos os bugs)": b, "subconjunto bug_and_files": b[b.in_baf]}
rows = []
for pop, df in pops.items():
    for p, g in df.groupby("project"):
        g = g.sort_values(["report_time", "bug_id"]).reset_index(drop=True)
        n = len(g)
        tr, te = g.iloc[: int(n * .8)], g.iloc[int(n * .9):]
        rt = te.report_time.values
        for col, lab in (("first_c", "1o commit"), ("last_c", "ultimo commit")):
            ct = np.sort(tr[col].values)
            # nº de bugs de treino com commit > report_time(t)
            leak = len(ct) - np.searchsorted(ct, rt, side="right")
            frac = leak / len(ct)
            rows.append(dict(populacao=pop, projeto=p, ref=lab, treino=len(tr), teste=len(te), media_leak=round(leak.mean(), 1),
                             pct_media=round(frac.mean(), 4), pct_mediana=round(float(np.median(frac)), 4), pct_max=round(frac.max(), 4),
                             testes_com_leak=int((leak > 0).sum()), pct_testes_com_leak=round((leak > 0).mean(), 3)))
o.table(pd.DataFrame(rows), index=False)
o("\nAlém do split: bugs de treino com commit posterior ao report_time de teste mais antigo (t = primeiro bug de teste):")
rows = []
for p, g in b.groupby("project"):
    g = g.sort_values(["report_time", "bug_id"]).reset_index(drop=True)
    n = len(g)
    tr = g.iloc[: int(n * .8)]
    t0 = g.iloc[int(n * .9)].report_time
    rows.append(dict(projeto=p, t0=str(t0), treino=len(tr), com_ultimo_commit_apos_t0=int((tr.last_c > t0).sum()), com_primeiro_commit_apos_t0=int((tr.first_c > t0).sum())))
o.table(pd.DataFrame(rows), index=False)
o("\nResultados:")
o("(fato) unidade = bug (bug_id distintos); referência = report_time do bug de teste; treino = primeiros 80% e teste = últimos 10% por report_time, por projeto.")
o("(fato) quase todo bug de teste (85% a 100%, conforme projeto e população) tem pelo menos um bug de treino com commit posterior ao seu report_time; em média 6 a 41 bugs, ou 0,2% a 0,6% do treino.")
o("(inferência) a magnitude é pequena porque o commit costuma ocorrer poucos dias após o report (mediana de 5 a 15 dias, ver 09); o efeito é presente mas de tamanho limitado nesta medida. Não medido: impacto desse vazamento nas métricas do Ramo B em si, que depende do cálculo definido na fase de modelagem.")
o.save()
