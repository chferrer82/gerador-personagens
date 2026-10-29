"""Descobridor de Campanha: questionário de 10 perguntas, envios e grupos.

Usa o mesmo banco das fichas (fichas.Banco): Postgres no Neon em produção, SQLite no computador.

Tabelas
  campanha_grupo  um grupo criado pelo mestre (nome e data)
  campanha_envio  uma resposta de jogador; grupo_id vazio = ainda na lista geral de envios

O cálculo não é guardado: o ranking de um grupo é refeito a partir das respostas a cada consulta.
"""
import re
from datetime import datetime, timezone

# ---------- aventuras ----------
# s = nível inicial; lv = faixa de níveis da capa; w = cenário
AVENTURAS = {
    "SWI": {"n": "Dragons of Stormwreck Isle", "lv": "1–3", "s": 1, "w": "Forgotten Realms"},
    "LMoP": {"n": "Lost Mine of Phandelver", "lv": "1–5", "s": 1, "w": "Forgotten Realms"},
    "WDH": {"n": "Waterdeep: Dragon Heist", "lv": "1–5", "s": 1, "w": "Forgotten Realms"},
    "DoIP": {"n": "Dragon of Icespire Peak", "lv": "1–6", "s": 1, "w": "Forgotten Realms"},
    "WBtW": {"n": "The Wild Beyond the Witchlight", "lv": "1–8", "s": 1, "w": "Feywild"},
    "CoS": {"n": "Curse of Strahd", "lv": "1–10", "s": 1, "w": "Ravenloft"},
    "PS": {"n": "Planescape: Turn of Fortune's Wheel", "lv": "3–10", "s": 3, "w": "Sigil e Planos"},
    "SKT": {"n": "Storm King's Thunder", "lv": "1–11", "s": 1, "w": "Forgotten Realms"},
    "ToA": {"n": "Tomb of Annihilation", "lv": "1–11", "s": 1, "w": "Forgotten Realms"},
    "SotDQ": {"n": "Shadow of the Dragon Queen", "lv": "1–11", "s": 1, "w": "Dragonlance"},
    "KftGV": {"n": "Keys from the Golden Vault", "lv": "1–11", "s": 1, "w": "Antologia"},
    "GoS": {"n": "Ghosts of Saltmarsh", "lv": "1–12", "s": 1, "w": "Greyhawk"},
    "RotF": {"n": "Icewind Dale: Rime of the Frostmaiden", "lv": "1–12", "s": 1, "w": "Forgotten Realms"},
    "PaBTSO": {"n": "Phandelver and Below: The Shattered Obelisk", "lv": "1–12", "s": 1, "w": "Forgotten Realms"},
    "CotN": {"n": "Call of the Netherdeep", "lv": "3–12", "s": 3, "w": "Exandria"},
    "DiA": {"n": "Baldur's Gate: Descent into Avernus", "lv": "1–13", "s": 1, "w": "Forgotten Realms"},
    "QftIS": {"n": "Quests from the Infinite Staircase", "lv": "1–13", "s": 1, "w": "Antologia"},
    "JttRC": {"n": "Journeys through the Radiant Citadel", "lv": "1–14", "s": 1, "w": "Antologia"},
    "ToD": {"n": "Tyranny of Dragons (Hoard + Rise of Tiamat)", "lv": "1–15", "s": 1, "w": "Forgotten Realms"},
    "PotA": {"n": "Princes of the Apocalypse", "lv": "1–15", "s": 1, "w": "Forgotten Realms"},
    "OotA": {"n": "Out of the Abyss", "lv": "1–15", "s": 1, "w": "Forgotten Realms"},
    "CM": {"n": "Candlekeep Mysteries", "lv": "1–16", "s": 1, "w": "Antologia"},
    "LoX": {"n": "Light of Xaryxis", "lv": "5–8", "s": 5, "w": "Spelljammer"},
    "WDMM": {"n": "Waterdeep: Dungeon of the Mad Mage", "lv": "5–20", "s": 5, "w": "Forgotten Realms"},
    "VEoR": {"n": "Vecna: Eve of Ruin", "lv": "10–20", "s": 10, "w": "Multiverso"},
    "DF": {"n": "Arcana Unleashed: Deadfall", "lv": "11–20", "s": 11, "w": "Forgotten Realms"},
}

# ---------- perguntas ----------
# Cada opção: (texto, aventuras que ganham pontos). w = peso da pergunta.
PERGUNTAS = [
    {"t": "Quanto tempo vocês querem jogar esta campanha?", "w": 2, "o": [
        ("Algumas sessões soltas, sem compromisso", ["KftGV", "CM", "JttRC", "QftIS", "SWI"]),
        ("Uns 3 a 4 meses", ["LMoP", "WDH", "DoIP", "LoX"]),
        ("Cerca de um ano", ["ToA", "CoS", "WBtW", "SotDQ", "RotF", "SKT", "PaBTSO", "GoS", "PS", "CotN"]),
        ("Uma epopeia de anos", ["DiA", "ToD", "PotA", "OotA", "WDMM", "VEoR", "DF"])]},
    {"t": "Que clima vocês querem na mesa?", "w": 1, "o": [
        ("Heroico clássico: salvar a vila, derrotar o vilão", ["LMoP", "DoIP", "SWI", "ToD", "SKT", "SotDQ"]),
        ("Sombrio, terror, desespero", ["CoS", "RotF", "PaBTSO", "OotA", "DiA"]),
        ("Leve, cômico, caprichoso", ["WBtW", "LoX", "WDH", "PS"]),
        ("Pulp, aventura exótica, mistério de outros mundos", ["ToA", "GoS", "CotN", "JttRC", "QftIS"])]},
    {"t": "Qual parte do jogo você mais curte?", "w": 1, "o": [
        ("Combate tático", ["WDMM", "ToD", "DiA", "SotDQ", "VEoR"]),
        ("Exploração de territórios e descobertas", ["ToA", "SKT", "RotF", "OotA", "PotA"]),
        ("Interação social, intriga e política", ["WDH", "CoS", "WBtW", "DF", "PS"]),
        ("Investigação e resolução de mistérios", ["CM", "GoS", "RotF", "PaBTSO", "KftGV"])]},
    {"t": "Como você prefere que a história ande?", "w": 1, "o": [
        ("Linear, com objetivo claro a cada capítulo", ["ToD", "SotDQ", "LoX", "VEoR", "DiA"]),
        ("Mundo aberto: vamos para onde quisermos", ["ToA", "SKT", "PotA", "RotF", "DoIP"]),
        ("Uma cidade-base para a qual sempre voltamos", ["WDH", "LMoP", "GoS", "DoIP", "PS"]),
        ("Masmorra gigante, andar por andar", ["WDMM", "ToA", "PotA", "OotA"])]},
    {"t": "Quanto risco de morte você aceita?", "w": 2, "o": [
        ("Baixo: quero meu personagem até o fim", ["WBtW", "SWI", "WDH", "LoX", "CM"]),
        ("Moderado: lutas difíceis, mas justas", ["LMoP", "DoIP", "SKT", "GoS", "KftGV", "SotDQ"]),
        ("Alto: mortes acontecem e fazem parte", ["CoS", "OotA", "RotF", "DiA", "PaBTSO"]),
        ("Brutal: sobreviver já é a vitória", ["ToA", "WDMM", "ToD", "VEoR"])]},
    {"t": "Onde você quer passar a maior parte do tempo?", "w": 1, "o": [
        ("Cidades grandes, ruas e tavernas", ["WDH", "DiA", "DF", "PS"]),
        ("Selvas, mares, costas e ilhas", ["ToA", "GoS", "SWI", "CotN"]),
        ("Gelo, montanhas e ermos", ["RotF", "SKT", "DoIP", "LMoP"]),
        ("Subterrâneo ou outros planos", ["OotA", "WDMM", "LoX", "VEoR", "QftIS", "JttRC", "WBtW"])]},
    {"t": "Que tipo de vilão você quer enfrentar?", "w": 1, "o": [
        ("Dragões", ["ToD", "DoIP", "SotDQ", "SWI"]),
        ("Demônios e diabos", ["DiA", "OotA", "PS"]),
        ("Mortos-vivos, liches e necromantes", ["ToA", "CoS", "DF", "VEoR"]),
        ("Cultos, aberrações e coisas incompreensíveis", ["PotA", "PaBTSO", "RotF", "CotN"])]},
    {"t": "Que tipo de dilema moral você quer?", "w": 1, "o": [
        ("Bem contra mal, sem ambiguidade", ["LMoP", "ToD", "SotDQ", "SKT"]),
        ("Escolhas cinzentas e consequências pesadas", ["DiA", "CoS", "RotF", "CotN"]),
        ("Conto de fadas: dá para resolver sem matar ninguém", ["WBtW", "SWI", "CM"]),
        ("Crime e espionagem: os fins justificam os meios", ["KftGV", "WDH", "DF", "GoS"])]},
    {"t": "Qual a sua experiência com D&D?", "w": 1, "o": [
        ("Primeira vez jogando", ["SWI", "LMoP", "DoIP", "WDH"]),
        ("Já joguei um pouco", ["SKT", "GoS", "WBtW", "RotF", "KftGV", "CM"]),
        ("Veterano querendo desafio", ["ToA", "CoS", "OotA", "DiA", "PaBTSO"]),
        ("Muito experiente, gosto de alto nível", ["WDMM", "VEoR", "DF", "QftIS"])]},
    {"t": "Que mundo você quer?", "w": 1, "o": [
        ("Forgotten Realms clássico", ["LMoP", "SKT", "ToA", "PotA", "RotF", "DiA", "WDH"]),
        ("Horror gótico ou guerra épica em mundo próprio", ["CoS", "SotDQ", "GoS"]),
        ("Viagens entre mundos e planos", ["PS", "LoX", "JttRC", "QftIS", "VEoR", "CotN"]),
        ("Tanto faz, o importante é a aventura", ["KftGV", "CM", "WBtW", "ToD", "OotA"])]},
]

LETRAS = "ABCD"
LONGAS = set(PERGUNTAS[0]["o"][2][1]) | set(PERGUNTAS[0]["o"][3][1])  # vetadas se a maioria quer sessões soltas
LETAIS = {"ToA", "WDMM", "VEoR"}                                      # vetadas se a maioria quer risco baixo
PONTOS_MAX = sum(q["w"] for q in PERGUNTAS)                            # 12 por votante
RESP_RE = re.compile(r"^[ABCD]{10}$")

# ---------- banco ----------
SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS campanha_grupo (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    criado_em  TEXT NOT NULL,
    nome       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS campanha_envio (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    criado_em  TEXT NOT NULL,
    nome       TEXT NOT NULL,
    respostas  TEXT NOT NULL,
    grupo_id   INTEGER REFERENCES campanha_grupo(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS campanha_envio_grupo ON campanha_envio (grupo_id);
"""
SCHEMA_PG = [
    """CREATE TABLE IF NOT EXISTS campanha_grupo (
        id         BIGSERIAL PRIMARY KEY,
        criado_em  TEXT NOT NULL,
        nome       TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS campanha_envio (
        id         BIGSERIAL PRIMARY KEY,
        criado_em  TEXT NOT NULL,
        nome       TEXT NOT NULL,
        respostas  TEXT NOT NULL,
        grupo_id   BIGINT REFERENCES campanha_grupo(id) ON DELETE SET NULL
    )""",
    "CREATE INDEX IF NOT EXISTS campanha_envio_grupo ON campanha_envio (grupo_id)",
]
_pg_ok = False


class Invalido(ValueError):
    pass


def _agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def garantir_tabelas(db):
    """Cria as tabelas se faltarem (no Postgres, uma vez por processo)."""
    global _pg_ok
    if db.pg:
        if _pg_ok:
            return
        with db.con.cursor() as cur:
            for sql in SCHEMA_PG:
                cur.execute(sql)
        db.con.commit()
        _pg_ok = True
    else:
        db.con.executescript(SCHEMA_SQLITE)


def _exec(db, sql, args=()):
    db.con.execute(db._sql(sql), args)
    db.con.commit()


def validar(dados):
    if not isinstance(dados, dict):
        raise Invalido("Envio inválido.")
    nome = re.sub(r"\s+", " ", str(dados.get("nome", ""))).strip().replace("\x00", "")
    resp = str(dados.get("respostas", "")).strip().upper()
    if not nome:
        raise Invalido("Escreva seu nome.")
    if len(nome) > 40:
        raise Invalido("O nome passou de 40 letras.")
    if not RESP_RE.match(resp):
        raise Invalido("Responda as 10 perguntas antes de enviar.")
    return nome, resp


def salvar_envio(db, nome, resp):
    """Grava a resposta na lista geral. Se a mesma pessoa já tem envio na lista geral, ele é substituído."""
    garantir_tabelas(db)
    _exec(db, "DELETE FROM campanha_envio WHERE grupo_id IS NULL AND lower(nome) = lower(?)", (nome,))
    return db.inserir("INSERT INTO campanha_envio (criado_em, nome, respostas) VALUES (?,?,?)",
                      (_agora(), nome, resp))


def envios_soltos(db):
    garantir_tabelas(db)
    return db.todos("SELECT id, criado_em, nome, respostas FROM campanha_envio "
                    "WHERE grupo_id IS NULL ORDER BY criado_em DESC, id DESC")


def grupos(db):
    garantir_tabelas(db)
    linhas = db.todos("SELECT id, criado_em, nome FROM campanha_grupo ORDER BY criado_em DESC, id DESC")
    saida = []
    for g in linhas:
        membros = membros_do_grupo(db, g["id"])
        res = calcular([m["respostas"] for m in membros], nivel1=False)
        primeiro = next((r for r in res["linhas"] if not r["fora"]), None) if membros else None
        saida.append({"id": g["id"], "criado_em": g["criado_em"], "nome": g["nome"],
                      "n": len(membros), "primeiro": primeiro})
    return saida


def obter_grupo(db, gid):
    garantir_tabelas(db)
    return db.um("SELECT id, criado_em, nome FROM campanha_grupo WHERE id = ?", (gid,))


def membros_do_grupo(db, gid):
    return db.todos("SELECT id, criado_em, nome, respostas FROM campanha_envio "
                    "WHERE grupo_id = ? ORDER BY nome", (gid,))


def _ids(ids):
    limpos = sorted({int(i) for i in ids if str(i).isdigit()})
    if not limpos:
        raise Invalido("Marque pelo menos uma pessoa.")
    return limpos


def criar_grupo(db, nome, ids):
    nome = re.sub(r"\s+", " ", nome or "").strip()[:60]
    if not nome:
        raise Invalido("Dê um nome ao grupo.")
    ids = _ids(ids)
    garantir_tabelas(db)
    gid = db.inserir("INSERT INTO campanha_grupo (criado_em, nome) VALUES (?,?)", (_agora(), nome))
    _mover(db, ids, gid)
    return gid


def adicionar_ao_grupo(db, gid, ids):
    if obter_grupo(db, gid) is None:
        raise Invalido("Grupo não encontrado.")
    _mover(db, _ids(ids), gid)


def _mover(db, ids, gid):
    marcas = ",".join("?" * len(ids))
    _exec(db, f"UPDATE campanha_envio SET grupo_id = ? WHERE grupo_id IS NULL AND id IN ({marcas})",
          (gid, *ids))


def devolver(db, gid, envio_id=None):
    """Devolve uma pessoa (ou todas, sem envio_id) do grupo para a lista geral."""
    if envio_id is None:
        _exec(db, "UPDATE campanha_envio SET grupo_id = NULL WHERE grupo_id = ?", (gid,))
    else:
        _exec(db, "UPDATE campanha_envio SET grupo_id = NULL WHERE grupo_id = ? AND id = ?", (gid, envio_id))


def desfazer_grupo(db, gid):
    devolver(db, gid)
    _exec(db, "DELETE FROM campanha_grupo WHERE id = ?", (gid,))


def excluir_grupo(db, gid):
    _exec(db, "DELETE FROM campanha_envio WHERE grupo_id = ?", (gid,))
    _exec(db, "DELETE FROM campanha_grupo WHERE id = ?", (gid,))


def excluir_envios(db, ids):
    ids = _ids(ids)
    marcas = ",".join("?" * len(ids))
    _exec(db, f"DELETE FROM campanha_envio WHERE grupo_id IS NULL AND id IN ({marcas})", tuple(ids))


# ---------- cálculo ----------

def calcular(respostas, nivel1=False):
    """Ranking de aderência para uma lista de respostas ('ABCDABCDAB' por pessoa)."""
    pts = {k: 0 for k in AVENTURAS}
    n = len(respostas)
    curtas = sum(1 for r in respostas if r[0] == "A")
    seguras = sum(1 for r in respostas if r[4] == "A")
    for r in respostas:
        for qi, letra in enumerate(r):
            q = PERGUNTAS[qi]
            for aid in q["o"][LETRAS.index(letra)][1]:
                pts[aid] += q["w"]
    veto_longas = n > 0 and curtas > n / 2
    veto_letais = n > 0 and seguras > n / 2
    linhas = []
    for aid, a in AVENTURAS.items():
        fora = None
        if veto_longas and aid in LONGAS:
            fora = "veto: duração"
        elif veto_letais and aid in LETAIS:
            fora = "veto: letalidade"
        elif nivel1 and a["s"] > 1:
            fora = f"começa no nível {a['s']}"
        linhas.append({"id": aid, **a, "pts": pts[aid],
                       "pct": (pts[aid] / (PONTOS_MAX * n)) if n else 0.0, "fora": fora})
    linhas.sort(key=lambda x: (x["fora"] is not None, -x["pts"], x["n"]))
    return {"linhas": linhas, "n": n, "curtas": curtas, "seguras": seguras,
            "veto_longas": veto_longas, "veto_letais": veto_letais}


def perguntas_publicas():
    """Só o texto das perguntas e opções, para a página do jogador."""
    return [{"t": q["t"], "w": q["w"], "o": [o[0] for o in q["o"]]} for q in PERGUNTAS]


def descrever(respostas):
    """Lista legível das escolhas de uma pessoa: [(pergunta, letra, opção)]."""
    return [(PERGUNTAS[i]["t"], c, PERGUNTAS[i]["o"][LETRAS.index(c)][0]) for i, c in enumerate(respostas)]
