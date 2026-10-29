"""Gerador de Personagens — servidor Flask.

Rotas públicas
  /                      a página do gerador, com as tabelas do banco embutidas
  POST /api/fichas       o jogador envia a ficha (nome do jogador e personagem)
  /api/tabelas           lista das tabelas (chave, tipo, descrição, fonte, observação)
  /api/tabelas/<chave>   conteúdo de uma tabela
  /api/dados             todas as tabelas, no formato usado pela página
  /saude                 verificação simples para o serviço de hospedagem

  /campanha              Descobridor de Campanha: questionário de 10 perguntas
  POST /api/campanha     o jogador envia as respostas (nome e 10 letras)

Rotas do mestre (usuário e senha nas variáveis MESTRE_USUARIO e MESTRE_SENHA)
  /mestre                lista das fichas, com busca
  /mestre/ficha/<id>     uma ficha completa
  /mestre/campanha       envios do questionário e grupos
  /mestre/campanha/grupo/<id>   ranking de aderência de um grupo

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

from flask import Flask, Response, abort, g, jsonify, redirect, render_template, request, url_for

import banco
import campanha
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


@app.post("/mestre/ficha/<int:fid>/apagar")
def mestre_ficha_apagar(fid):
    _exige_mestre(); _mesma_origem()
    fichas.apagar(con_fichas(), fid)
    return redirect(url_for("mestre_lista"))


# ---------- descobridor de campanha ----------

@app.get("/campanha")
def campanha_pagina():
    dados = _json_para_script(campanha.perguntas_publicas())
    return render_template("campanha.html", perguntas_json=dados)


@app.post("/api/campanha")
def api_campanha_enviar():
    try:
        nome, resp = campanha.validar(request.get_json(silent=True))
    except campanha.Invalido as e:
        return jsonify(ok=False, erro=str(e)), 400
    eid = campanha.salvar_envio(con_fichas(), nome, resp)
    return jsonify(ok=True, id=eid, resumo=campanha.resumo_jogador(nome, resp)), 201


def _mesma_origem():
    """Recusa POST do mestre vindo de outro site (o navegador reenvia a senha sozinho)."""
    from urllib.parse import urlparse
    origem = request.headers.get("Origin") or request.headers.get("Referer") or ""
    if origem and urlparse(origem).netloc != request.host:
        abort(403, description="Pedido de outra origem recusado.")


def _ids_form():
    return request.form.getlist("envio")


@app.get("/mestre/campanha")
def mestre_campanha():
    _exige_mestre()
    db = con_fichas()
    return render_template("mestre_campanha.html", envios=campanha.envios_soltos(db),
                           grupos=campanha.grupos(db), aviso=request.args.get("aviso", ""),
                           melhores=campanha.melhores, AV=campanha.AVENTURAS, perfil=campanha.perfil,
                           erro=request.args.get("erro", ""))


@app.post("/mestre/campanha/agrupar")
def mestre_campanha_agrupar():
    _exige_mestre(); _mesma_origem()
    db = con_fichas()
    destino = request.form.get("destino", "novo")
    acao = request.form.get("acao", "agrupar")
    try:
        if acao == "excluir":
            campanha.excluir_envios(db, _ids_form())
            return redirect(url_for("mestre_campanha", aviso="Envios excluídos."))
        if destino == "novo":
            gid = campanha.criar_grupo(db, request.form.get("nome", ""), _ids_form())
        else:
            gid = int(destino)
            campanha.adicionar_ao_grupo(db, gid, _ids_form())
    except (campanha.Invalido, ValueError) as e:
        return redirect(url_for("mestre_campanha", erro=str(e)))
    return redirect(url_for("mestre_campanha_grupo", gid=gid))


@app.post("/mestre/campanha/envio/<int:eid>/apagar")
def mestre_campanha_apagar_envio(eid):
    _exige_mestre(); _mesma_origem()
    campanha.excluir_envio(con_fichas(), eid)
    volta = request.form.get("volta", "")
    if volta.isdigit():
        return redirect(url_for("mestre_campanha_grupo", gid=int(volta), aviso="Resposta apagada."))
    return redirect(url_for("mestre_campanha", aviso="Resposta apagada."))


@app.get("/mestre/campanha/grupo/<int:gid>")
def mestre_campanha_grupo(gid):
    _exige_mestre()
    db = con_fichas()
    g_ = campanha.obter_grupo(db, gid)
    if g_ is None:
        abort(404, description="Grupo não encontrado.")
    membros = campanha.membros_do_grupo(db, gid)
    nivel1 = request.args.get("nivel1") == "1"
    res = campanha.calcular([m["respostas"] for m in membros], nivel1=nivel1)
    return render_template("mestre_grupo.html", g=g_, membros=membros, res=res, nivel1=nivel1,
                           descrever=campanha.descrever, aviso=request.args.get("aviso", ""),
                           melhores=campanha.melhores, AV=campanha.AVENTURAS, perfil=campanha.perfil)


@app.post("/mestre/campanha/grupo/<int:gid>/<acao>")
def mestre_campanha_grupo_acao(gid, acao):
    _exige_mestre(); _mesma_origem()
    db = con_fichas()
    if campanha.obter_grupo(db, gid) is None:
        abort(404, description="Grupo não encontrado.")
    if acao == "devolver":
        eid = request.form.get("envio", "")
        if not eid.isdigit():
            abort(400)
        campanha.devolver(db, gid, int(eid))
        return redirect(url_for("mestre_campanha_grupo", gid=gid, aviso="Pessoa devolvida aos envios."))
    if acao == "desfazer":
        campanha.desfazer_grupo(db, gid)
        return redirect(url_for("mestre_campanha", aviso="Grupo desfeito. As pessoas voltaram para os envios."))
    if acao == "excluir":
        campanha.excluir_grupo(db, gid)
        return redirect(url_for("mestre_campanha", aviso="Grupo e respostas excluídos."))
    abort(404)


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
