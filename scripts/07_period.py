"""07_period: intervalo temporal e distribuição por ano."""
from common import *

o = Out("07_period")
bc = load("bug_commit", cols="bug_id,report_time,commit_time")
bc["report_time"] = pd.to_datetime(bc.report_time)
bc["commit_time"] = pd.to_datetime(bc.commit_time)
o("== Min/max (linhas bug-commit) ==")
o.table(bc.groupby("project").agg(report_min=("report_time", "min"), report_max=("report_time", "max"),
                                  commit_min=("commit_time", "min"), commit_max=("commit_time", "max")))
b = bc.groupby(["project", "bug_id"]).agg(report_time=("report_time", "first"), first_commit=("commit_time", "min"), last_commit=("commit_time", "max")).reset_index()
o("\n== Bugs por ano de report_time (bugs distintos) ==")
o.table(b.groupby([b.report_time.dt.year.rename("ano"), "project"]).size().unstack(fill_value=0))
o("\n== Bugs por ano do último commit (bugs distintos) ==")
o.table(b.groupby([b.last_commit.dt.year.rename("ano"), "project"]).size().unstack(fill_value=0))
o("\nQuantis de report_time (bugs distintos):")
o.table(b.groupby("project").report_time.quantile([.1, .5, .8, .9]).unstack())
o("\nResultados:")
mx = bc.commit_time.max()
o(f"(fato) maior commit_time do dump: {mx}; o dump não tem dados posteriores a janeiro de 2014.")
o("(fato) datas são DATETIME sem fuso (o dump força TIME_ZONE +00:00 apenas na restauração). (não confirmado) o fuso de origem de report_time vs commit_time.")
o("(inferência) os dados têm ~12 anos de idade em relação a 2026; ameaça de validade externa a declarar.")
o.save()
