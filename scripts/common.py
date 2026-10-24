"""Utilitários compartilhados pelos scripts de exploração."""
import os
import re
import sqlite3

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "data/interim/bugs.sqlite")
PROJECTS = {"BIRT": "birt", "Eclipse UI": "eclipse_platform_ui", "JDT": "jdt", "SWT": "swt"}
# Referências da literatura (CLAUDE.md seção 3), apenas para conferência.
ALKHAZI = {"BIRT": 4952, "Eclipse UI": 6670, "JDT": 6528, "SWT": 4266}
DEVRANKER = {"BIRT": 4178, "Eclipse UI": 6495, "JDT": 6274, "SWT": 4151}
# Contas genéricas/de triagem (heurística, rotulada como inferência nos relatórios).
GENERIC = re.compile(r"inbox|triaged|^birt-", re.I)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 200)


def con():
    return sqlite3.connect(DB)


def load(table, where="", cols="*"):
    """Carrega <projeto>__<table> de cada projeto em um único DataFrame com coluna `project`."""
    c = con()
    frames = []
    for name, db in PROJECTS.items():
        df = pd.read_sql(f'SELECT {cols} FROM "{db}__{table}" {where}', c)
        df.insert(0, "project", name)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def pseudonyms(series, prefix="dev"):
    """Mapeia nomes para dev_001... por frequência decrescente (determinístico)."""
    order = series.value_counts().index
    return {n: f"{prefix}_{i + 1:03d}" for i, n in enumerate(order)}


class Out:
    """Acumula texto, imprime e grava em outputs/<prefixo>.txt."""

    def __init__(self, prefix):
        self.prefix, self.buf = prefix, []

    def __call__(self, *a):
        self.buf.append(" ".join(str(x) for x in a))

    def table(self, df, **kw):
        self.buf.append(df.to_string(**kw))

    def save(self):
        os.makedirs(os.path.join(ROOT, "outputs"), exist_ok=True)
        txt = "\n".join(self.buf) + "\n"
        open(os.path.join(ROOT, "outputs", self.prefix + ".txt"), "w").write(txt)
        print(txt)
