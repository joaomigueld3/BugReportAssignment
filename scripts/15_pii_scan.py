"""15_pii_scan: onde há dado pessoal no dump, para decidir o que pode ser publicado. Só contagens, sem nomes."""
from common import *

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
o = Out("15_pii_scan")
bc = load("bug_commit", cols="bug_id,summary,description,reporter,assignee,author,\"log\" as log,files")
baf = load("bug_and_files", cols="bug_id,summary,description,bag_of_word_stemmed")
o("== Colunas de pessoas: formato dos valores (valores distintos, % com '@', % com espaço) ==")
rows = []
for col in ("reporter", "assignee", "author"):
    for p, g in bc.groupby("project"):
        v = pd.Series(g[col].unique())
        rows.append(dict(coluna=col, projeto=p, distintos=len(v), pct_com_arroba=round(v.str.contains("@").mean(), 3), pct_com_espaco=round(v.str.contains(" ").mean(), 3),
                         pct_generico=round(v.str.contains(GENERIC).mean(), 3)))
o.table(pd.DataFrame(rows), index=False)
allnames = set()
for col in ("reporter", "assignee", "author"):
    allnames |= set(bc[col])
o(f"\nNomes distintos nas 3 colunas (4 projetos): {len(allnames)}; destes, não genéricos: {sum(not GENERIC.search(n) for n in allnames)}")
o("\n== E-mails em texto livre (linhas com ao menos 1 e-mail) ==")
rows = []
for col in ("summary", "description", "log", "files"):
    for p, g in bc.groupby("project"):
        x = g[col].fillna("").map(lambda s: len(EMAIL.findall(s)))
        rows.append(dict(coluna=f"bug_commit.{col}", projeto=p, linhas=len(g), com_email=int((x > 0).sum()), pct=round((x > 0).mean(), 4), emails_total=int(x.sum())))
for col in ("summary", "description", "bag_of_word_stemmed"):
    for p, g in baf.groupby("project"):
        x = g[col].fillna("").map(lambda s: len(EMAIL.findall(s)))
        rows.append(dict(coluna=f"bug_and_files.{col}", projeto=p, linhas=len(g), com_email=int((x > 0).sum()), pct=round((x > 0).mean(), 4), emails_total=int(x.sum())))
o.table(pd.DataFrame(rows), index=False)
o("\n== Nomes completos de desenvolvedores citados em texto livre (nomes com espaço, não genéricos, >=6 caracteres) ==")
names = {n for n in allnames if " " in n and len(n) >= 6 and not GENERIC.search(n)}
WORD = re.compile(r"[^\W\d_][\w.'-]*")


def has_name(s):
    w = WORD.findall(s)
    return any(" ".join(w[i:i + k]) in names for i in range(len(w)) for k in (2, 3, 4))


b1 = bc.drop_duplicates(["project", "bug_id"])
for col in ("description", "log"):
    src = b1 if col == "description" else bc
    hit = src[col].fillna("").map(has_name)
    o(f"bug_commit.{col}: linhas com algum nome completo = {int(hit.sum())} de {len(src)} ({hit.mean():.1%})")
sig = bc["log"].fillna("").str.contains(r"Signed-off-by|Contributed by|Reviewed-by|Also-by", case=False, regex=True)
o(f"linhas de log com Signed-off-by/Contributed by/Reviewed-by/Also-by: {int(sig.sum())}")
o("\nResultados:")
o("(fato) acima. (inferência) a presença de nomes em texto livre só é detectada para nomes completos já conhecidos; nomes parciais e de terceiros não são detectáveis por este método.")
o.save()
