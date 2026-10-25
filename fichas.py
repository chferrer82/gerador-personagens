"""Fichas enviadas pelos jogadores (banco separado das tabelas).

Dois modos, escolhidos pelas variáveis de ambiente:
  DATABASE_URL definida  → Postgres (produção: Neon). Ex.: postgresql://usuario:senha@host/banco?sslmode=require
  sem DATABASE_URL       → SQLite no arquivo FICHAS_DB (padrão: fichas.db na pasta), para rodar no computador

As tabelas do gerador continuam em dados.db (só leitura); este módulo cuida só das fichas.
"""
import json
import re
import sqlite3
from datetime import datetime, timezone

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS ficha (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    criada_em    TEXT NOT NULL,
    jogador      TEXT NOT NULL,
    email        TEXT NOT NULL,
    personagem   TEXT NOT NULL,
    resumo       TEXT NOT NULL,
    texto        TEXT NOT NULL,
    estado       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ficha_email ON ficha (email);
CREATE INDEX IF NOT EXISTS ficha_criada ON ficha (criada_em);
"""

SCHEMA_PG = [
    """CREATE TABLE IF NOT EXISTS ficha (
        id           BIGSERIAL PRIMARY KEY,
        criada_em    TEXT NOT NULL,
        jogador      TEXT NOT NULL,
        email        TEXT NOT NULL,
        personagem   TEXT NOT NULL,
        resumo       TEXT NOT NULL,
        texto        TEXT NOT NULL,
        estado       TEXT NOT NULL
    )""",
    "CREATE INDEX IF NOT EXISTS ficha_email ON ficha (email)",
    "CREATE INDEX IF NOT EXISTS ficha_criada ON ficha (criada_em)",
]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LIMITES = {"jogador": 80, "email": 120, "personagem": 120, "resumo": 300, "texto": 60_000, "estado": 200_000}
COLUNAS_LISTA = "id, criada_em, jogador, email, personagem, resumo"


class Invalida(ValueError):
    pass


class Banco:
    """Conexão única com a mesma interface para SQLite e Postgres."""

    _pg_schema_ok = False  # o CREATE TABLE no Postgres roda uma vez por processo

    def __init__(self, url=None, caminho=None):
        self.pg = bool(url)
        if self.pg:
            import psycopg
            from psycopg.rows import dict_row
            self.con = psycopg.connect(url, row_factory=dict_row, connect_timeout=15)
            if not Banco._pg_schema_ok:
                with self.con.cursor() as cur:
                    for sql in SCHEMA_PG:
                        cur.execute(sql)
                self.con.commit()
                Banco._pg_schema_ok = True
        else:
            self.con = sqlite3.connect(caminho)
            self.con.row_factory = sqlite3.Row
            self.con.executescript(SCHEMA_SQLITE)

    def _sql(self, sql):
        return sql.replace("?", "%s") if self.pg else sql

    def todos(self, sql, args=()):
        cur = self.con.execute(self._sql(sql), args)
        return cur.fetchall()

    def um(self, sql, args=()):
        cur = self.con.execute(self._sql(sql), args)
        return cur.fetchone()

    def inserir(self, sql, args):
        if self.pg:
            row = self.con.execute(self._sql(sql) + " RETURNING id", args).fetchone()
            self.con.commit()
            return row["id"]
        cur = self.con.execute(sql, args)
        self.con.commit()
        return cur.lastrowid

    def fechar(self):
        self.con.close()


def validar(dados):
    """Confere o JSON enviado pela página e devolve os campos limpos."""
    if not isinstance(dados, dict):
        raise Invalida("Envio inválido.")
    jogador = str(dados.get("jogador", "")).strip()
    email = ""  # o e-mail deixou de ser pedido (P27); a coluna fica vazia
    personagem = str(dados.get("personagem", "")).strip() or "Sem nome"
    resumo = str(dados.get("resumo", "")).strip()
    texto = str(dados.get("texto", "")).strip()
    estado = dados.get("estado", {})
    if not jogador:
        raise Invalida("Escreva seu nome.")
    if not texto:
        raise Invalida("A ficha está vazia.")
    estado = json.dumps(estado, ensure_ascii=False)
    campos = {"jogador": jogador, "email": email, "personagem": personagem,
              "resumo": resumo, "texto": texto, "estado": estado}
    for k, lim in LIMITES.items():
        if len(campos[k]) > lim:
            raise Invalida(f"O campo {k} passou do tamanho máximo.")
    # O Postgres recusa o caractere nulo em texto.
    return {k: v.replace("\x00", "") for k, v in campos.items()}


def salvar(db, campos):
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return db.inserir(
        """INSERT INTO ficha (criada_em, jogador, email, personagem, resumo, texto, estado)
           VALUES (?,?,?,?,?,?,?)""",
        (agora, campos["jogador"], campos["email"], campos["personagem"],
         campos["resumo"], campos["texto"], campos["estado"]),
    )


def buscar(db, q="", limite=500):
    sql = f"SELECT {COLUNAS_LISTA} FROM ficha"
    args = []
    if q:
        like = "ILIKE" if db.pg else "LIKE"  # sem diferenciar maiúsculas nos dois bancos
        sql += f" WHERE jogador {like} ? OR personagem {like} ? OR resumo {like} ?"
        args = [f"%{q}%"] * 3
    sql += " ORDER BY criada_em DESC, id DESC LIMIT ?"
    args.append(limite)
    return db.todos(sql, args)


def total(db):
    row = db.um("SELECT count(*) AS n FROM ficha")
    return row["n"]


def obter(db, fid):
    return db.um("SELECT * FROM ficha WHERE id = ?", (fid,))
