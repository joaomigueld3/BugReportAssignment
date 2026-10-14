"""12_commit_log: completude da coluna log (e files) por linha bug-commit e por bug."""
from common import *

o = Out("12_commit_log")
bc = load("bug_commit", cols="bug_id,\"log\" as log,files")
bc["log_ok"] = bc.log.fillna("").str.strip() != ""
bc["files_ok"] = bc.files.fillna("").str.strip() != ""
bc["log_w"] = bc.log.str.split().str.len()
rows = []
for p, g in bc.groupby("project"):
    per = g.groupby("bug_id").log_ok.any()
    rows.append(dict(projeto=p, linhas=len(g), log_preenchido=int(g.log_ok.sum()), pct_linhas=round(g.log_ok.mean(), 4), bugs=len(per), bugs_com_algum_log=int(per.sum()),
                     pct_bugs=round(per.mean(), 4), log_w_med=int(g[g.log_ok].log_w.median()), log_w_q99=int(g[g.log_ok].log_w.quantile(.99)),
                     files_preenchido=int(g.files_ok.sum()), pct_files=round(g.files_ok.mean(), 4)))
o.table(pd.DataFrame(rows), index=False)
o("\nResultados:")
o("(fato) acima, completude da coluna `log` (mensagem de commit) e `files`. Não foram implementadas features (φ19 a φ22).")
o("(não confirmado) o que cada feature φ19 a φ22 exige: depende de conferência no artigo de Alkhazi (2020).")
o.save()
