"""09_interval: commit_time - report_time em dias."""
from common import *

o = Out("09_interval")
bc = load("bug_commit", cols="bug_id,report_time,commit_time")
bc["d"] = (pd.to_datetime(bc.commit_time) - pd.to_datetime(bc.report_time)).dt.total_seconds() / 86400
b = bc.groupby(["project", "bug_id"]).d.agg(first="min", last="max").reset_index()
Q = [.01, .05, .25, .5, .75, .95, .99]
def summarize(df, col, label):
    o(f"\n== {label} ==")
    rows = []
    for p, g in df.groupby("project"):
        x = g[col]
        rows.append({"projeto": p, "n": len(x), "negativos": int((x < 0).sum()), "pct_neg": round((x < 0).mean(), 4), "zero_<1h": int((x.abs() < 1 / 24).sum()),
                     "min": round(x.min(), 1), **{f"q{int(q*100)}": round(x.quantile(q), 1) for q in Q}, "max": round(x.max(), 1),
                     ">365d": int((x > 365).sum()), ">1000d": int((x > 1000).sum())})
    o.table(pd.DataFrame(rows), index=False)
summarize(bc, "d", "Linhas bug-commit (dias)")
summarize(b, "first", "Bugs distintos: primeiro commit (dias)")
summarize(b, "last", "Bugs distintos: último commit (dias)")
neg = bc[bc.d < 0].d
o(f"\nNegativos (linhas): {len(neg)}; quantis dos negativos (dias):", neg.quantile([0, .1, .5, .9, 1]).round(2).to_dict())
o("\nResultados:")
o("(fato) valores negativos significam commit_time anterior a report_time; a maioria dos negativos é de magnitude pequena (mediana ~0 dia, mínimo de vários anos). (não confirmado) a causa: fuso, commit anterior ao bug ou erro de vínculo.")
o("(fato) essa é a única diferença temporal disponível; inclui fila antes da atribuição e atraso até o commit (limitação 1 confirmada pelo schema, ver 02).")
o.save()
