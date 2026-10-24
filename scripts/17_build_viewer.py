"""17_build_viewer: gera data/samples/visualizador.html, página única e offline para ver os dados sem rodar scripts.

Embute (a) as saídas agregadas de outputs/*.txt, uma aba por análise, e (b) as amostras pseudonimizadas de data/samples/*.csv
como tabelas com busca, filtro por projeto, ordenação e paginação. Só dados já pseudonimizados/agregados entram na página.
"""
import glob
import json

from common import *

ABAS = [
    ("02_schema", "Schema", "P1. Quais tabelas e colunas existem? Diverge do README?"),
    ("03_counts", "Contagens", "P2/P3. Como identificar o projeto? Quantos bugs há por projeto?"),
    ("04_status", "Status", "P4. Distribuição de status por projeto."),
    ("05_importance", "Importance", "P5. Prioridade e severidade: dá para separar?"),
    ("06_label", "Rótulo", "P6. assignee x author; contas genéricas."),
    ("07_period", "Período", "P7. Intervalo de datas e bugs por ano."),
    ("08_developers", "Desenvolvedores", "P8. Quantos, cauda longa, desenvolvedores tardios."),
    ("09_interval", "Intervalo", "P9. commit_time - report_time em dias."),
    ("10_leakage", "Vazamento", "P10. Vazamento temporal no corte cronológico."),
    ("11_text", "Texto", "P11. Texto vazio, tamanho e stack traces."),
    ("12_commit_log", "Logs de commit", "P12. Completude da coluna log."),
    ("13_features_sanity", "Features (D8)", "ExtractedFeatures e SVMrank: o que são e como mapeiam para o dump."),
    ("14_alkhazi_filter", "Filtro Alkhazi (D9)", "Busca de filtros que reproduzam 22.416 bugs."),
    ("14_verify_mysql", "MySQL (D1)", "SQLite x MySQL 8.0.12: 35 de 35 tabelas idênticas."),
    ("18_eda_base", "Base decidida", "Descritivos na base FIXED com rótulo author: rótulo, cold-start, pool, tempo, texto."),
    ("15_pii_scan", "Dados pessoais", "Onde há dado pessoal no dump (contagens)."),
    ("16_make_samples", "Amostras", "Como as amostras foram geradas e verificadas."),
]
AMOSTRAS = [
    ("bug_commit_sample", "Amostra: bug_commit"),
    ("bug_and_files_sample", "Amostra: bug_and_files"),
    ("features_OurNewApproach_fold1_sample", "Amostra: features (nova)"),
    ("features_PreviousApproach_fold1_sample", "Amostra: features (anterior)"),
]
SAMP = os.path.join(ROOT, "data/samples")
txt, tab = [], []
for key, nome, desc in ABAS:
    f = os.path.join(ROOT, "outputs", key + ".txt")
    if os.path.exists(f):
        txt.append(dict(id=key, nome=nome, desc=desc, texto=open(f, encoding="utf8").read()))
for key, nome in AMOSTRAS:
    f = os.path.join(SAMP, key + ".csv")
    if os.path.exists(f):
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        tab.append(dict(id=key, nome=nome, cols=list(df.columns), rows=df.values.tolist()))
data = json.dumps(dict(txt=txt, tab=tab), ensure_ascii=False).replace("</", "<\\/")

HTML = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HybridBugRank: visão dos dados</title>
<style>
:root{--bg:#fafaf8;--fg:#1c1c1a;--mut:#6b6b66;--bd:#dcdcd6;--card:#fff;--acc:#2a5db0;--hl:#eef3fb}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ececea;--mut:#9a9a94;--bd:#3a3a36;--card:#1f1f1d;--acc:#7ea6ea;--hl:#232b3a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
header{padding:20px 16px 8px;max-width:1400px;margin:0 auto}h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);font-size:13px}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--bd);padding:8px 16px;z-index:5}
.tabs{max-width:1400px;margin:0 auto;display:flex;flex-wrap:wrap;gap:6px}
.tabs button{background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:6px;padding:5px 10px;font:inherit;font-size:13px;cursor:pointer}
.tabs button.on{background:var(--acc);color:#fff;border-color:var(--acc)}.sep{width:1px;background:var(--bd);margin:0 4px}
main{max-width:1400px;margin:0 auto;padding:16px}.desc{color:var(--mut);margin:0 0 10px}
pre{background:var(--card);border:1px solid var(--bd);border-radius:8px;padding:12px;overflow:auto;font:12.5px/1.45 ui-monospace,Menlo,Consolas,monospace;white-space:pre}
.tools{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;align-items:center}
input,select{background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:6px;padding:5px 8px;font:inherit;font-size:13px}
.tw{overflow:auto;border:1px solid var(--bd);border-radius:8px;background:var(--card);max-height:70vh}
table{border-collapse:collapse;font-size:12.5px;width:max-content;min-width:100%}
th,td{border-bottom:1px solid var(--bd);padding:4px 8px;text-align:left;vertical-align:top;max-width:360px}
th{position:sticky;top:0;background:var(--hl);cursor:pointer;white-space:nowrap}td{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}td.x{white-space:pre-wrap;overflow:visible}
.cnt{color:var(--mut);font-size:13px}.pg button{border:1px solid var(--bd);background:var(--card);color:var(--fg);border-radius:6px;padding:3px 9px;cursor:pointer}
.aviso{background:var(--hl);border:1px solid var(--bd);border-radius:8px;padding:8px 12px;font-size:13px;margin-bottom:12px}
</style></head><body>
<header><h1>HybridBugRank: visão dos dados</h1>
<div class="sub">Análises agregadas (uma aba por pergunta) e amostras pseudonimizadas (50 bugs por projeto, semente 42). Página offline; nada aqui precisa de script ou rede.</div></header>
<nav><div class="tabs" id="tabs"></div></nav><main id="main"></main>
<script>
const D=__DATA__;
const tabs=document.getElementById('tabs'),main=document.getElementById('main');
const items=[...D.txt.map(t=>({k:'t:'+t.id,n:t.nome})),{sep:1},...D.tab.map(t=>({k:'d:'+t.id,n:t.nome}))];
items.forEach(i=>{if(i.sep){const s=document.createElement('span');s.className='sep';tabs.appendChild(s);return}
const b=document.createElement('button');b.textContent=i.n;b.dataset.k=i.k;b.onclick=()=>show(i.k);tabs.appendChild(b)});
function el(t,a,c){const e=document.createElement(t);if(a)Object.assign(e,a);if(c!=null)e.textContent=c;return e}
function show(k){[...tabs.querySelectorAll('button')].forEach(b=>b.classList.toggle('on',b.dataset.k===k));location.hash=k;main.innerHTML='';
if(k.startsWith('t:')){const t=D.txt.find(x=>'t:'+x.id===k);main.appendChild(el('p',{className:'desc'},t.desc));main.appendChild(el('pre',null,t.texto))}
else{const t=D.tab.find(x=>'d:'+x.id===k);grid(t)}}
function grid(t){
main.appendChild(el('div',{className:'aviso'},'Nomes de pessoas foram trocados por pseudônimos (dev_xxxxxxxx); contas genéricas (inbox, triaged) ficam legíveis. É pseudonimização: bug_id, commit e datas são públicos. Clique numa célula para expandir; clique no cabeçalho para ordenar.'));
const tools=el('div',{className:'tools'});const q=el('input',{placeholder:'buscar em todas as colunas',size:30});tools.appendChild(q);
const pi=t.cols.indexOf('project');let sel=null;if(pi>=0){sel=el('select');sel.appendChild(el('option',{value:''},'todos os projetos'));[...new Set(t.rows.map(r=>r[pi]))].forEach(p=>sel.appendChild(el('option',{value:p},p)));tools.appendChild(sel)}
const cnt=el('span',{className:'cnt'});const pg=el('span',{className:'pg'});tools.append(cnt,pg);main.appendChild(tools);
const tw=el('div',{className:'tw'});const tb=el('table');tw.appendChild(tb);main.appendChild(tw);
let rows=t.rows,page=0,per=100,sc=-1,sd=1;
const num=c=>t.rows.slice(0,50).every(r=>r[c]===''||!isNaN(Number(r[c])));
function draw(){const s=q.value.toLowerCase(),p=sel?sel.value:'';
let f=rows.filter(r=>(!p||r[pi]===p)&&(!s||r.some(v=>v.toLowerCase().includes(s))));
if(sc>=0){const n=num(sc);f=[...f].sort((a,b)=>(n?Number(a[sc])-Number(b[sc]):a[sc].localeCompare(b[sc]))*sd)}
const pages=Math.max(1,Math.ceil(f.length/per));page=Math.min(page,pages-1);
cnt.textContent=f.length+' linhas';pg.innerHTML='';
const pv=el('button',null,'‹');pv.onclick=()=>{page=Math.max(0,page-1);draw()};const nx=el('button',null,'›');nx.onclick=()=>{page=Math.min(pages-1,page+1);draw()};
pg.append(pv,document.createTextNode(' página '+(page+1)+' de '+pages+' '),nx);
tb.innerHTML='';const h=el('tr');t.cols.forEach((c,i)=>{const th=el('th',null,c+(i===sc?(sd>0?' ▲':' ▼'):''));th.onclick=()=>{sd=(sc===i)?-sd:1;sc=i;draw()};h.appendChild(th)});tb.appendChild(h);
f.slice(page*per,(page+1)*per).forEach(r=>{const tr=el('tr');r.forEach(v=>{const td=el('td',null,v);td.title=v.length>60?'':'';td.onclick=()=>td.classList.toggle('x');tr.appendChild(td)});tb.appendChild(tr)})}
q.oninput=()=>{page=0;draw()};if(sel)sel.onchange=()=>{page=0;draw()};draw()}
show((location.hash||'#').slice(1)||items[0].k);
</script></body></html>"""
out = os.path.join(SAMP, "visualizador.html")
open(out, "w", encoding="utf8").write(HTML.replace("__DATA__", data))
print(f"{out}: {os.path.getsize(out) / 1e6:.2f} MB; abas de texto={len(txt)}; abas de dados={len(tab)}")
