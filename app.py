"""Gerador de Personagens — servidor Flask.

Rotas públicas
  /                      a página do gerador, com as tabelas do banco embutidas
  POST /api/fichas       o jogador envia a ficha (nome, e-mail, personagem)
  /api/tabelas           lista das tabelas (chave, tipo, descrição, fonte, observação)
  /api/tabelas/<chave>   conteúdo de uma tabela
  /api/dados             todas as tabelas, no formato usado pela página
  /saude                 verificação simples para o serviço de hospedagem

Rotas do mestre (usuário e senha nas variáveis MESTRE_USUARIO e MESTRE_SENHA)
  /mestre                lista das fichas, com busca
  /mestre/ficha/<id>     uma ficha completa

Bancos
  dados.db   tabelas do gerador, só leitura (edite com gerenciar.py)
  fichas     fichas dos jogadores: Postgres em DATABASE_URL (produção, Neon)
             ou, sem ela, SQLite no arquivo FICHAS_DB (no computador)
"""
import json
import os
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, Response, abort, g, jsonify, render_template, request

import banco
import fichas

RAIZ = Path(__file__).resolve().parent
DB = Path(os.environ.get("GERADOR_DB", RAIZ / "dados.db"))
FICHAS_DB = Path(os.environ.get("FICHAS_DB", RAIZ / "fichas.db"))
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
MESTRE_USUARIO = os.environ.get("MESTRE_USUARIO", "mestre")
MESTRE_SENHA = os.environ.get("MESTRE_SENHA", "")
TEMPLATE = (RAIZ / "templates" / "index.html").read_text(encoding="utf-8")
MARCADOR = "/*__DADOS__*/null"

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False  # a ordem das chaves importa para a página
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024
FUSO = os.environ.get("MESTRE_FUSO", "America/New_York")


@app.template_filter("data")
def _data(iso):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    try:
        return datetime.fromisoformat(iso).astimezone(ZoneInfo(FUSO)).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso


def con():
    if "con" not in g:
        g.con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    return g.con


def con_fichas():
    if "conf" not in g:
        if not DATABASE_URL:
            FICHAS_DB.parent.mkdir(parents=True, exist_ok=True)
        g.conf = fichas.Banco(url=DATABASE_URL or None, caminho=FICHAS_DB)
    return g.conf


@app.teardown_appcontext
def fechar(_):
    c = g.pop("con", None)
    if c is not None:
        c.close()
    f = g.pop("conf", None)
    if f is not None:
        f.fechar()


def _json_para_script(dados):
    # Evita que "</script>" ou "<!--" dentro de um texto fechem a tag.
    return (
        json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(" ", "\\u2028")
        .replace(" ", "\\u2029")
    )


@app.get("/")
def pagina():
    html = TEMPLATE.replace(MARCADOR, _json_para_script(banco.ler_tudo(con())), 1)
    return Response(html, mimetype="text/html")


# ---------- fichas dos jogadores ----------

@app.post("/api/fichas")
def api_enviar_ficha():
    try:
        campos = fichas.validar(request.get_json(silent=True))
    except fichas.Invalida as e:
        return jsonify(ok=False, erro=str(e)), 400
    fid = fichas.salvar(con_fichas(), campos)
    return jsonify(ok=True, id=fid), 201


def _exige_mestre():
    """Autenticação HTTP Basic. Sem MESTRE_SENHA definida, a área do mestre fica fechada."""
    if not MESTRE_SENHA:
        abort(503, description="Área do mestre desativada: defina a variável MESTRE_SENHA.")
    a = request.authorization
    ok = (
        a is not None
        and secrets.compare_digest(a.username or "", MESTRE_USUARIO)
        and secrets.compare_digest(a.password or "", MESTRE_SENHA)
    )
    if not ok:
        resp = Response("Acesso restrito ao mestre.", 401, mimetype="text/plain")
        resp.headers["WWW-Authenticate"] = 'Basic realm="Mestre", charset="UTF-8"'
        abort(resp)


@app.after_request
def sem_cache_mestre(resp):
    if request.path.startswith("/mestre"):
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["X-Robots-Tag"] = "noindex"
    return resp


@app.get("/mestre")
def mestre_lista():
    _exige_mestre()
    q = request.args.get("q", "").strip()[:80]
    linhas = fichas.buscar(con_fichas(), q)
    total = fichas.total(con_fichas())
    return render_template("mestre.html", linhas=linhas, q=q, total=total)


@app.get("/mestre/ficha/<int:fid>")
def mestre_ficha(fid):
    _exige_mestre()
    f = fichas.obter(con_fichas(), fid)
    if f is None:
        abort(404, description="Ficha não encontrada.")
    return render_template("mestre_ficha.html", f=f)


# ---------- tabelas ----------

@app.get("/api/tabelas")
def api_tabelas():
    return jsonify(banco.listar(con()))


@app.get("/api/tabelas/<chave>")
def api_tabela(chave):
    try:
        return jsonify(banco.ler_tabela(con(), chave))
    except KeyError:
        abort(404, description=f"Tabela não encontrada: {chave}")


@app.get("/api/dados")
def api_dados():
    return jsonify(banco.ler_tudo(con()))


@app.get("/saude")
def saude():
    n = con().execute("SELECT count(*) FROM tabela").fetchone()[0]
    return jsonify(ok=True, tabelas=n)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
