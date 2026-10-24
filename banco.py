"""Banco SQLite das tabelas do Gerador de Personagens.

Modelo
------
tabela  — uma linha por tabela de dados (chave usada pelo front-end, descrição, fonte, observação).
item    — o conteúdo. Cada tabela é de um dos tipos:
    faixas  lista de linhas [min, max, ...]   → uma linha de `item` por faixa (min, max, valor)
    json    estrutura qualquer                → uma linha de `item` com o JSON inteiro
    grupos  dicionário de subtabelas          → linhas de `item` com `grupo` preenchido;
            cada grupo é faixas (min/max preenchidos) ou json (min/max nulos)

`valor` guarda, em JSON, as colunas da faixa depois de min e max
(ex.: ["Waterdeep"] ou ["texto", "P"]).
"""
import json
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS tabela (
    chave       TEXT PRIMARY KEY,
    tipo        TEXT NOT NULL CHECK (tipo IN ('faixas', 'json', 'grupos')),
    descricao   TEXT NOT NULL DEFAULT '',
    fonte       TEXT NOT NULL DEFAULT '',
    observacao  TEXT NOT NULL DEFAULT '',
    ordem       INTEGER NOT NULL,
    atualizado  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS item (
    tabela  TEXT NOT NULL REFERENCES tabela(chave) ON DELETE CASCADE,
    grupo   TEXT NOT NULL DEFAULT '',
    ordem   INTEGER NOT NULL,
    min     INTEGER,
    max     INTEGER,
    valor   TEXT NOT NULL,
    PRIMARY KEY (tabela, grupo, ordem)
);
CREATE INDEX IF NOT EXISTS item_tabela ON item (tabela, grupo, ordem);
"""


def conectar(caminho):
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA)
    return con


def _e_faixas(v):
    return (
        isinstance(v, list)
        and len(v) > 0
        and all(
            isinstance(r, list) and len(r) >= 3
            and type(r[0]) is int and type(r[1]) is int
            for r in v
        )
    )


def _dump(v):
    return json.dumps(v, ensure_ascii=False)


def _gravar_faixas(con, chave, grupo, linhas):
    con.executemany(
        "INSERT INTO item (tabela, grupo, ordem, min, max, valor) VALUES (?,?,?,?,?,?)",
        [(chave, grupo, i, r[0], r[1], _dump(r[2:])) for i, r in enumerate(linhas)],
    )


def gravar_tabela(con, chave, valor, ordem, meta=None, tipo=None):
    """Substitui o conteúdo de uma tabela. `tipo` força o tipo; senão é detectado."""
    meta = meta or {}
    if tipo is None:
        if _e_faixas(valor):
            tipo = "faixas"
        elif isinstance(valor, dict) and any(_e_faixas(x) for x in valor.values()):
            tipo = "grupos"
        else:
            tipo = "json"
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    con.execute("DELETE FROM item WHERE tabela = ?", (chave,))
    con.execute(
        """INSERT INTO tabela (chave, tipo, descricao, fonte, observacao, ordem, atualizado)
           VALUES (?,?,?,?,?,?,?)
           ON CONFLICT(chave) DO UPDATE SET tipo=excluded.tipo, descricao=excluded.descricao,
             fonte=excluded.fonte, observacao=excluded.observacao, ordem=excluded.ordem,
             atualizado=excluded.atualizado""",
        (chave, tipo, meta.get("descricao", ""), meta.get("fonte", ""),
         meta.get("observacao", ""), ordem, agora),
    )
    if tipo == "faixas":
        _gravar_faixas(con, chave, "", valor)
    elif tipo == "json":
        con.execute(
            "INSERT INTO item (tabela, grupo, ordem, min, max, valor) VALUES (?,?,?,?,?,?)",
            (chave, "", 0, None, None, _dump(valor)),
        )
    else:  # grupos: a ordem global preserva a ordem das chaves do dicionário
        n = 0
        for g, sub in valor.items():
            if _e_faixas(sub):
                for r in sub:
                    con.execute(
                        "INSERT INTO item (tabela, grupo, ordem, min, max, valor) VALUES (?,?,?,?,?,?)",
                        (chave, g, n, r[0], r[1], _dump(r[2:])),
                    )
                    n += 1
            else:
                con.execute(
                    "INSERT INTO item (tabela, grupo, ordem, min, max, valor) VALUES (?,?,?,?,?,?)",
                    (chave, g, n, None, None, _dump(sub)),
                )
                n += 1
    return tipo


def ler_tabela(con, chave):
    row = con.execute("SELECT tipo FROM tabela WHERE chave = ?", (chave,)).fetchone()
    if row is None:
        raise KeyError(chave)
    tipo = row[0]
    itens = con.execute(
        "SELECT grupo, min, max, valor FROM item WHERE tabela = ? ORDER BY ordem", (chave,)
    ).fetchall()
    if tipo == "faixas":
        return [[mn, mx, *json.loads(v)] for _, mn, mx, v in itens]
    if tipo == "json":
        return json.loads(itens[0][3])
    out = {}
    for g, mn, mx, v in itens:
        if mn is None:
            out[g] = json.loads(v)
        else:
            out.setdefault(g, []).append([mn, mx, *json.loads(v)])
    return out


def listar(con):
    cols = ["chave", "tipo", "descricao", "fonte", "observacao", "atualizado"]
    rows = con.execute(f"SELECT {', '.join(cols)} FROM tabela ORDER BY ordem").fetchall()
    return [dict(zip(cols, r)) for r in rows]


def ler_tudo(con):
    chaves = [r[0] for r in con.execute("SELECT chave FROM tabela ORDER BY ordem")]
    return {k: ler_tabela(con, k) for k in chaves}
