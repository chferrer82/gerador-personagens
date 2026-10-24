"""Gerencia o banco de tabelas (dados.db).

Comandos:
  python gerenciar.py criar      Recria dados.db a partir dos arquivos em dados/
  python gerenciar.py exportar   Grava cada tabela do banco em dados/<CHAVE>.json
  python gerenciar.py importar CHAVE   Regrava uma tabela a partir de dados/<CHAVE>.json
  python gerenciar.py listar     Lista as tabelas com descrição e observações
  python gerenciar.py verificar  Confere se banco e arquivos em dados/ têm o mesmo conteúdo

Fluxo para editar uma tabela: exportar → editar dados/<CHAVE>.json → importar CHAVE.
dados/_metadados.json guarda descrição, fonte e observação de cada tabela, na ordem do banco.
"""
import json
import sys
from pathlib import Path

import banco

RAIZ = Path(__file__).resolve().parent
DB = RAIZ / "dados.db"
PASTA = RAIZ / "dados"
META = PASTA / "_metadados.json"


def _meta():
    return json.loads(META.read_text(encoding="utf-8"))


def _ler_arquivo(chave):
    return json.loads((PASTA / f"{chave}.json").read_text(encoding="utf-8"))


def criar():
    if DB.exists():
        DB.unlink()
    con = banco.conectar(DB)
    for i, (chave, meta) in enumerate(_meta().items()):
        tipo = banco.gravar_tabela(con, chave, _ler_arquivo(chave), i, meta)
        print(f"{chave:14} {tipo}")
    con.commit()
    print(f"\n{DB.name} criado com {i + 1} tabelas.")


def exportar():
    con = banco.conectar(DB)
    meta = {}
    for t in banco.listar(con):
        meta[t["chave"]] = {k: t[k] for k in ("descricao", "fonte", "observacao")}
        (PASTA / f"{t['chave']}.json").write_text(
            json.dumps(banco.ler_tabela(con, t["chave"]), ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(meta)} tabelas exportadas para {PASTA.name}/")


def importar(chave):
    meta = _meta()
    if chave not in meta:
        sys.exit(f"Tabela desconhecida: {chave}. Inclua-a em {META.name} primeiro.")
    con = banco.conectar(DB)
    ordem = list(meta).index(chave)
    tipo = banco.gravar_tabela(con, chave, _ler_arquivo(chave), ordem, meta[chave])
    con.commit()
    print(f"{chave} regravada ({tipo}).")


def listar():
    con = banco.conectar(DB)
    for t in banco.listar(con):
        print(f"{t['chave']:14} {t['tipo']:7} {t['descricao']}")
        if t["observacao"]:
            print(f"{'':23}↳ {t['observacao']}")


def verificar():
    con = banco.conectar(DB)
    erros = 0
    for chave in _meta():
        if banco.ler_tabela(con, chave) != _ler_arquivo(chave):
            print(f"DIFERENTE: {chave}")
            erros += 1
    print("OK: banco e arquivos iguais." if not erros else f"{erros} tabela(s) diferente(s).")
    return erros


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "criar":
        criar()
    elif cmd == "exportar":
        exportar()
    elif cmd == "importar" and len(sys.argv) == 3:
        importar(sys.argv[2])
    elif cmd == "listar":
        listar()
    elif cmd == "verificar":
        sys.exit(1 if verificar() else 0)
    else:
        print(__doc__)
