"""11_text: nulos/vazios, comprimento em palavras e stack traces em summary e description (bugs distintos)."""
from common import *

o = Out("11_text")
bc = load("bug_commit", cols="bug_id,summary,description")
n_null = int(bc[["summary", "description"]].isna().sum().sum())
b = bc.drop_duplicates(["project", "bug_id"]).copy()
incons = int((bc.groupby(["project", "bug_id"])[["summary", "description"]].nunique() > 1).any(axis=1).sum())
o(f"Nulos SQL (linhas): {n_null}. Bugs com summary/description diferentes entre suas linhas: {incons}.")
STACK = re.compile(r"^\s*at\s+[\w$.<>]+\([\w$.]*(?:\.java)?(?::\d+)?\)", re.M)
EXC = re.compile(r"\b(?:java|org|javax)\.[\w.]*(?:Exception|Error)\b")
for col in ("summary", "description"):
    b[col + "_w"] = b[col].str.split().str.len()
    b[col + "_vazio"] = b[col].str.strip() == ""
b["stack"] = b.description.map(lambda s: len(STACK.findall(s)) >= 2)
b["exc"] = b.description.map(lambda s: bool(EXC.search(s)))
b["nonascii"] = b.description.map(lambda s: any(ord(c) > 127 for c in s))
rows = []
for p, g in b.groupby("project"):
    d = g.description_w
    rows.append(dict(projeto=p, bugs=len(g), summary_vazio=int(g.summary_vazio.sum()), desc_vazia=int(g.description_vazio.sum()), pct_desc_vazia=round(g.description_vazio.mean(), 3),
                     summary_w_med=int(g.summary_w.median()), summary_w_max=int(g.summary_w.max()), desc_w_med=int(d.median()), desc_w_q90=int(d.quantile(.9)), desc_w_q99=int(d.quantile(.99)),
                     desc_gt_300w=round((d > 300).mean(), 3), pct_stack_ge2_linhas_at=round(g["stack"].mean(), 3), pct_com_Exception_Error=round(g.exc.mean(), 3),
                     desc_nao_ascii=int(g.nonascii.sum()), summary_len_max=int(g.summary.str.len().max())))
o.table(pd.DataFrame(rows), index=False)
o("\nResultados:")
o("(fato) comprimento medido em palavras separadas por espaço; tokens WordPiece do BERT serão mais numerosos (razão não medida aqui; não confirmada).")
o("(fato) stack trace = >=2 linhas começando com 'at pacote.Classe(Arquivo.java:N)'; Exception/Error = nome de classe java./org./javax. terminando em Exception ou Error. São heurísticas minhas, não validadas manualmente.")
o("(fato) `desc_nao_ascii` conta descrições com algum caractere não ASCII; o dump foi lido como UTF-8 estrito sem erro. (não confirmado) se houve perda de acentos/caracteres na exportação original (colunas utf8 em tabelas DEFAULT CHARSET=latin1).")
o("(fato) summary é tinytext (limite de 255 bytes no MySQL); `summary_len_max` mostra o maior comprimento em caracteres.")
o.save()
