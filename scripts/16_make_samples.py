"""16_make_samples: amostras pequenas e pseudonimizadas dos datasets, versionáveis em data/samples/.

- bug_commit e bug_and_files: 50 bugs por projeto (semente 42), com TODAS as linhas bug-commit de cada bug (preserva o grão).
- ExtractedFeatures: 20 queries do fold 1, com os 142 candidatos de cada (folds 2 e 3 não alinham com o dump, ver 13).
- Nomes (reporter, assignee, author, dev): HMAC-SHA256 com chave local em data/interim/pseudonym.key (fora do git).
  Contas genéricas (regex GENERIC) ficam legíveis. É pseudonimização, não anonimização: bug_id, commit e datas são públicos
  e permitem reidentificar via Bugzilla/GitHub.
- Texto livre: e-mails viram <email>; nomes completos conhecidos viram o pseudônimo. Nomes parciais e de terceiros não são tratados.
- Colunas *_stemmed de bug_and_files são omitidas (derivadas do texto, grandes).
"""
import hashlib
import hmac
import secrets

from common import *

SEED, N_BUGS, N_QUERIES = 42, 50, 20
OUTDIR = os.path.join(ROOT, "data/samples")
KEYF = os.path.join(ROOT, "data/interim/pseudonym.key")
FEAT = os.path.join(ROOT, "data/interim/zips/ExtractedFeatures")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
os.makedirs(OUTDIR, exist_ok=True)
if not os.path.exists(KEYF):
    open(KEYF, "w").write(secrets.token_hex(32))
    os.chmod(KEYF, 0o600)
KEY = bytes.fromhex(open(KEYF).read().strip())

o = Out("16_make_samples")
bc = load("bug_commit")
baf = load("bug_and_files", cols="id,bug_id,summary,description,report_time,report_timestamp,status,\"commit\",commit_timestamp,files")
feats = {ap: pd.read_csv(f"{FEAT}/{ap}/Fold1_{suf}.csv", header=None) for ap, suf in (("OurNewApproach", "New"), ("PreviousApproach", "Previous"))}
for ap, d in feats.items():
    d.columns = ["qid", "bug_id", "dev"] + [f"f{i}" for i in range(1, d.shape[1] - 3)] + ["label"]

names = set(bc.reporter) | set(bc.assignee) | set(bc.author)
for d in feats.values():
    names |= set(d.dev)
names = {n for n in names if n}
P = {n: (n if GENERIC.search(n) else "dev_" + hmac.new(KEY, n.encode(), hashlib.sha256).hexdigest()[:8]) for n in names}
real = [n for n in names if not GENERIC.search(n)]
assert len({P[n] for n in real}) == len(real), "colisão de pseudônimos"
o(f"Nomes distintos: {len(names)}; pseudonimizados: {len(real)}; genéricos mantidos: {len(names) - len(real)}; colisões de pseudônimo: 0")

full = sorted((n for n in real if " " in n and len(n) >= 6), key=len, reverse=True)
NAMEPAT = re.compile("|".join(re.escape(n) for n in full))
stats = dict(emails=0, nomes=0)


def scrub(s):
    if not isinstance(s, str):
        return s
    s, n1 = EMAIL.subn("<email>", s)
    s, n2 = NAMEPAT.subn(lambda m: P[m.group(0)], s)
    stats["emails"] += n1
    stats["nomes"] += n2
    return s


# ---- bug_commit / bug_and_files
rng = np.random.default_rng(SEED)
pick = {}
for p, g in bc.groupby("project"):
    ids = np.sort(g.bug_id.unique())
    pick[p] = set(rng.choice(ids, size=N_BUGS, replace=False).tolist())
sel = bc[[b in pick[p] for p, b in zip(bc.project, bc.bug_id)]].copy()
for c in ("reporter", "assignee", "author"):
    sel[c] = sel[c].map(P)
for c in ("summary", "description", "log"):
    sel[c] = sel[c].map(scrub)
sel = sel.sort_values(["project", "bug_id", "id"])
sel.to_csv(f"{OUTDIR}/bug_commit_sample.csv", index=False)
selb = baf[[b in pick[p] for p, b in zip(baf.project, baf.bug_id)]].copy()
for c in ("summary", "description"):
    selb[c] = selb[c].map(scrub)
selb.sort_values(["project", "bug_id"]).to_csv(f"{OUTDIR}/bug_and_files_sample.csv", index=False)
o(f"\nbug_commit_sample.csv: {len(sel)} linhas, {sel.groupby('project').bug_id.nunique().to_dict()} bugs por projeto (semente {SEED})")
o(f"bug_and_files_sample.csv: {len(selb)} linhas (bugs sorteados que existem em bug_and_files; {len(selb)} de {N_BUGS * 4})")

# ---- features
q1 = feats["OurNewApproach"].drop_duplicates("qid").qid.values
rngf = np.random.default_rng(SEED)
qs = set(rngf.choice(np.sort(q1), size=N_QUERIES, replace=False).tolist())
for ap, d in feats.items():
    s = d[d.qid.isin(qs)].copy()
    s["dev"] = s.dev.map(P)
    s.to_csv(f"{OUTDIR}/features_{ap}_fold1_sample.csv", index=False)
    o(f"features_{ap}_fold1_sample.csv: {len(s)} linhas, {s.qid.nunique()} queries, {s.shape[1] - 4} features")

o(f"\nTexto livre tratado: {stats['emails']} e-mails trocados por <email>, {stats['nomes']} nomes completos trocados por pseudônimo.")

# ---- verificação de vazamento
leak = 0
for f in os.listdir(OUTDIR):
    if not f.endswith(".csv"):
        continue
    txt = open(os.path.join(OUTDIR, f), encoding="utf8").read()
    hits = [n for n in full if n in txt]
    leak += len(hits)
    o(f"{f}: nomes reais ainda presentes (busca exata) = {len(hits)}")
o(f"Total de nomes completos reais encontrados nos arquivos de amostra: {leak}")
o("\nResultados:")
o("(fato) a verificação acima é por busca exata de nomes conhecidos (colunas de pessoas e nomes completos); não detecta nomes parciais, apelidos ou terceiros em texto livre.")
o("(fato) a chave do HMAC fica em data/interim/pseudonym.key (ignorada pelo git); sem ela os pseudônimos não se refazem, mas as amostras versionadas continuam válidas.")
o.save()
