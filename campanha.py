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
# Cada pergunta: t = texto neutro (área do mestre), f = fala do anão, p = a pergunta curta, w = peso.
# Cada opção: (texto, aventuras que ganham pontos, comentário do anão ao confirmar).
PERGUNTAS = [
    {"t": "Quanto tempo quer jogar esta campanha?", "w": 2,
     "f": "Primeiro: quanto tempo você aguenta na estrada? Tem gente que cansa antes da primeira curva. Elfo nem sai de casa, fica admirando a curva.",
     "p": "Quanto tempo vocês querem jogar?", "o": [
        ("Umas sessões soltas, sem compromisso", ["KftGV", "CM", "JttRC", "QftIS", "SWI"],
         "Rápido e sem compromisso. Igual promessa de elfo. Tá, anotado."),
        ("Uns 3 a 4 meses", ["LMoP", "WDH", "DoIP", "LoX"],
         "Três ou quatro meses. O tempo de forjar uma boa lâmina. Gostei."),
        ("Mais ou menos um ano", ["ToA", "CoS", "WBtW", "SotDQ", "RotF", "SKT", "PaBTSO", "GoS", "PS", "CotN"],
         "Um ano inteiro. Agora sim estamos falando de trabalho de verdade."),
        ("Anos, até a barba arrastar no chão", ["DiA", "ToD", "PotA", "OotA", "WDMM", "VEoR", "DF"],
         "Anos! Isso é teimosia de anão. Respeito. Muito respeito.")]},
    {"t": "Que clima quer na mesa?", "w": 1,
     "f": "E o clima da coisa? Quer sair cantando vitória na taverna ou sair da masmorra tremendo igual vara verde?",
     "p": "Que clima você quer na mesa?", "o": [
        ("Heroico: salvar a vila e derrubar o vilão", ["LMoP", "DoIP", "SWI", "ToD", "SKT", "SotDQ"],
         "Heroico. Machado na mão, vilão no chão, cerveja depois. Do jeito certo."),
        ("Sombrio, terror e desespero", ["CoS", "RotF", "PaBTSO", "OotA", "DiA"],
         "Escuridão e medo, é? Tem estômago. Ou não tem juízo. Veremos."),
        ("Leve, cômico, meio bobo", ["WBtW", "LoX", "WDH", "PS"],
         "Bobagem e risada. Hmpf. Pelo menos não é poesia élfica."),
        ("Exótico, cheio de mistério", ["ToA", "GoS", "CotN", "JttRC", "QftIS"],
         "Terra estranha e mistério. Leve corda. Sempre leve corda.")]},
    {"t": "Que parte do jogo mais curte?", "w": 1,
     "f": "O que você mais gosta de fazer numa aventura? E não me venha com cantar. Isso é coisa de bardo élfico.",
     "p": "Qual parte do jogo você mais curte?", "o": [
        ("Briga: combate pensado, golpe a golpe", ["WDMM", "ToD", "DiA", "SotDQ", "VEoR"],
         "Briga! Finalmente alguém com bom senso nesta forja."),
        ("Explorar terras e achar coisas", ["ToA", "SKT", "RotF", "OotA", "PotA"],
         "Explorador. Pés firmes e olhos abertos. Serve."),
        ("Conversar, negociar e tramar", ["WDH", "CoS", "WBtW", "DF", "PS"],
         "Lábia. Hmpf. Fala bonito igual elfo. Só não me engane."),
        ("Investigar e resolver mistérios", ["CM", "GoS", "RotF", "PaBTSO", "KftGV"],
         "Cabeça pensante. Bom. Alguém precisa ler as runas enquanto eu bato.")]},
    {"t": "Como quer que a história ande?", "w": 1,
     "f": "E como você quer que a história ande? Tem gente que gosta de trilha marcada. Tem gente que se perde no mato. Adivinha quem.",
     "p": "Como a história deve andar?", "o": [
        ("Em linha reta: cada capítulo, um objetivo", ["ToD", "SotDQ", "LoX", "VEoR", "DiA"],
         "Linha reta. Sem rodeio. Como um bom túnel de mina."),
        ("Mundo aberto: vou para onde eu quiser", ["ToA", "SKT", "PotA", "RotF", "DoIP"],
         "Pra onde quiser, é? Só não venha chorar quando se perder."),
        ("Uma cidade-base para voltar sempre", ["WDH", "LMoP", "GoS", "DoIP", "PS"],
         "Uma casa pra voltar. Todo anão entende isso. Lar é lar."),
        ("Uma masmorra enorme, andar por andar", ["WDMM", "ToA", "PotA", "OotA"],
         "Descer, descer e descer. Agora você está falando a minha língua.")]},
    {"t": "Quanto risco de morte aceita?", "w": 2,
     "f": "Agora a pergunta séria. Larga essa caneca. Quanto você aceita morrer?",
     "p": "Quanto risco de morte você aceita?", "o": [
        ("Pouco: quero meu personagem até o fim", ["WBtW", "SWI", "WDH", "LoX", "CM"],
         "Quer viver bastante. Esperto. Não é covardia, é bom senso. Quase sempre."),
        ("Lutas duras, mas justas", ["LMoP", "DoIP", "SKT", "GoS", "KftGV", "SotDQ"],
         "Duro mas justo. Igual martelo bem calibrado. Anotado."),
        ("Morte acontece e faz parte", ["CoS", "OotA", "RotF", "DiA", "PaBTSO"],
         "Morte faz parte. Fala como anão velho. Gostei de você."),
        ("Brutal: sobreviver já é vitória", ["ToA", "WDMM", "ToD", "VEoR"],
         "Brutal! Já vou deixando a pá separada. Pra cova, não pra mina.")]},
    {"t": "Onde quer passar a maior parte do tempo?", "w": 1,
     "f": "Onde você quer gastar a sola das botas? E não diga floresta. Floresta é cheia de elfo.",
     "p": "Onde você quer passar a maior parte do tempo?", "o": [
        ("Cidade grande: ruas, becos e tavernas", ["WDH", "DiA", "DF", "PS"],
         "Cidade grande. Barulho, ladrão e cerveja cara. Fique de olho na bolsa."),
        ("Selva, mar, costa e ilhas", ["ToA", "GoS", "SWI", "CotN"],
         "Mar e selva. Anão afunda e sua dentro da armadura. Mas o problema é seu."),
        ("Gelo, montanha e ermo", ["RotF", "SKT", "DoIP", "LMoP"],
         "Montanha! Pedra boa e vento frio na cara. Isso sim é lugar decente."),
        ("Debaixo da terra ou em outros planos", ["OotA", "WDMM", "LoX", "VEoR", "QftIS", "JttRC", "WBtW"],
         "Debaixo da terra me agrada. Outros planos, nem tanto. Vá com cuidado.")]},
    {"t": "Que tipo de vilão quer enfrentar?", "w": 1,
     "f": "Quem você quer ver estendido no chão no fim da história? Além de elfo, claro. Isso é sonho de todo anão.",
     "p": "Que tipo de vilão você quer enfrentar?", "o": [
        ("Dragões", ["ToD", "DoIP", "SotDQ", "SWI"],
         "Dragão. Ladrão de ouro com asas. Tenho contas a acertar com essa raça."),
        ("Demônios e diabos", ["DiA", "OotA", "PS"],
         "Demônio e diabo. Fedem a enxofre e mentem mais que elfo. Quase."),
        ("Mortos-vivos, liches e necromantes", ["ToA", "CoS", "DF", "VEoR"],
         "Morto que não fica morto. Martelo resolve. Martelo sempre resolve."),
        ("Cultos e coisas que não têm nome", ["PotA", "PaBTSO", "RotF", "CotN"],
         "Coisa sem nome. Essas são as piores. Durma com o machado do lado.")]},
    {"t": "Que tipo de dilema moral quer?", "w": 1,
     "f": "E a consciência, como fica? Quer saber logo quem é o vilão, ou prefere quebrar a cabeça sem saber quem merece o machado?",
     "p": "Que tipo de dilema você quer?", "o": [
        ("Bem contra mal, sem enrolação", ["LMoP", "ToD", "SotDQ", "SKT"],
         "Bem contra mal. Simples. Honesto. Do jeito que o mundo devia ser."),
        ("Escolhas difíceis com consequência pesada", ["DiA", "CoS", "RotF", "CotN"],
         "Escolha difícil. Vai pesar mais que bigorna nas costas. Avisado."),
        ("Conto de fadas: dá para resolver sem matar", ["WBtW", "SWI", "CM"],
         "Sem matar ninguém? Hmpf. Coisa de fada. Ou de elfo. Mesma laia."),
        ("Crime e espionagem: o fim justifica os meios", ["KftGV", "WDH", "DF", "GoS"],
         "Crime e trapaça. Não conte pra mim o que você roubou. Não quero saber.")]},
    {"t": "Qual a sua experiência com D&D?", "w": 1,
     "f": "Diga a verdade. Quantas vezes você já sentou numa mesa dessas? Eu sei quando estão mentindo. Já negociei com elfo.",
     "p": "Qual a sua experiência com D&D?", "o": [
        ("É a minha primeira vez", ["SWI", "LMoP", "DoIP", "WDH"],
         "Primeira vez. Bom. Ninguém nasce sabendo bater ferro."),
        ("Já joguei um pouco", ["SKT", "GoS", "WBtW", "RotF", "KftGV", "CM"],
         "Já tem calo na mão. Pouco, mas tem. Serve."),
        ("Sou veterano e quero desafio", ["ToA", "CoS", "OotA", "DiA", "PaBTSO"],
         "Veterano querendo apanhar. Vou lembrar disso quando você chorar."),
        ("Muito experiente, gosto de alto nível", ["WDMM", "VEoR", "DF", "QftIS"],
         "Experiente de verdade. Tá bom, tá bom. Mostre o que sabe.")]},
    {"t": "Que mundo quer?", "w": 1,
     "f": "Última, e aí eu largo do seu pé. Em que mundo você quer pisar?",
     "p": "Em que mundo você quer jogar?", "o": [
        ("Os Reinos Esquecidos de sempre", ["LMoP", "SKT", "ToA", "PotA", "RotF", "DiA", "WDH"],
         "Os Reinos. Terra conhecida, com montanha boa e anão de verdade. Ótimo."),
        ("Terror gótico ou guerra épica em outro mundo", ["CoS", "SotDQ", "GoS"],
         "Outro mundo, é? Só não traga de lá nada que morda."),
        ("Viajar entre mundos e planos", ["PS", "LoX", "JttRC", "QftIS", "VEoR", "CotN"],
         "Pular de mundo em mundo. Hmpf. Anão gosta de chão firme. Vá você."),
        ("Tanto faz, me dê a aventura", ["KftGV", "CM", "WBtW", "ToD", "OotA"],
         "Tanto faz! Desse jeito que se fala. Pegue o machado e vamos.")]},
]

# ---------- resumo para o jogador (sem nome de aventura) ----------
# g = do que a pessoa gosta; p = um perigo que ela vai encontrar. Texto próprio, sem nomes da aventura.
SABOR = {
    "SWI": ("explorar uma ilha cheia de naufrágios", "o que dorme debaixo das pedras da ilha"),
    "LMoP": ("caçar uma mina perdida", "a emboscada que espera na estrada"),
    "WDH": ("caça ao tesouro numa cidade grande", "as facções que sorriem na frente e apunhalam pelas costas"),
    "DoIP": ("defender uma vila de fronteira", "o dragão branco que caça nas montanhas"),
    "WBtW": ("um carnaval mágico e terras de fadas", "os acordos doces que cobram caro"),
    "CoS": ("terror gótico numa terra presa na névoa", "o senhor do castelo que nunca envelhece"),
    "PS": ("viagens entre os planos", "as portas que levam para onde você não quer ir"),
    "SKT": ("uma jornada pelo norte atrás de gigantes", "gigantes brigando entre si e pisando em quem estiver no meio"),
    "ToA": ("selva, ruínas e tumbas cheias de armadilhas", "a maldição que não deixa morto voltar"),
    "SotDQ": ("guerra e cavalaria", "o exército de dragões marchando sobre as cidades"),
    "KftGV": ("assaltos planejados nos mínimos detalhes", "cofres que mordem e guardas que não dormem"),
    "GoS": ("aventura marítima numa vila de pescadores", "a casa assombrada na colina e o que sobe do mar"),
    "RotF": ("sobreviver no frio eterno", "a noite que não acaba"),
    "PaBTSO": ("uma mina perdida que leva a horrores debaixo da terra", "os sussurros que entram na sua cabeça"),
    "CotN": ("uma corrida por ruínas antigas", "o que dorme no fundo do abismo e chama em sonho"),
    "DiA": ("uma descida aos infernos", "os pactos com diabos e a cidade que foi engolida"),
    "QftIS": ("masmorras clássicas de outros tempos", "as armadilhas que já mataram muito herói"),
    "JttRC": ("viagens a terras distantes, cada uma com sua história", "os segredos de povos que você não conhece"),
    "ToD": ("uma guerra contra um culto de dragões", "a rainha de cinco cabeças tentando voltar"),
    "PotA": ("cultos escondidos em vales e cavernas", "terra, fogo, água e ar querendo engolir o mundo"),
    "OotA": ("fugir pela escuridão debaixo da terra", "os demônios soltos no escuro e as correntes dos elfos negros"),
    "CM": ("mistérios escondidos em livros antigos", "os livros que mordem quem lê"),
    "LoX": ("aventura entre as estrelas num navio que voa", "a luz que quer apagar um mundo inteiro"),
    "WDMM": ("uma masmorra sem fim, andar por andar", "o mago louco que manda em tudo lá embaixo"),
    "VEoR": ("salvar o multiverso inteiro", "o senhor dos segredos querendo reescrever a realidade"),
    "DF": ("espionagem contra magos poderosos", "o lich que governa uma nação inteira"),
}

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
    """Falas, perguntas, opções e comentários, para a página do jogador (sem as aventuras)."""
    return [{"f": q["f"], "p": q["p"], "w": q["w"], "o": [{"t": o[0], "c": o[2]} for o in q["o"]]}
            for q in PERGUNTAS]


def _juntar(itens):
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " ou " + itens[-1]


def melhores(respostas, n=3):
    """As n aventuras com mais pontos para uma pessoa (sem vetos, que valem só para grupos)."""
    pts = {k: 0 for k in AVENTURAS}
    for qi, letra in enumerate(respostas):
        q = PERGUNTAS[qi]
        for aid in q["o"][LETRAS.index(letra)][1]:
            pts[aid] += q["w"]
    ordem = sorted(AVENTURAS, key=lambda k: (-pts[k], AVENTURAS[k]["n"]))
    return ordem[:n]


def resumo_jogador(nome, respostas):
    """Fala final do anão: do que a pessoa gosta e o que deve temer, sem nomear aventura."""
    top = melhores(respostas)
    gostos = _juntar([SABOR[a][0] for a in top])
    perigos = _juntar([SABOR[a][1] for a in top])
    return (f"Então é isso, {nome}. Você gosta de {gostos}. "
            f"Tome cuidado com {perigos}. "
            "O resto é com o mestre. Agora saia da minha forja, que o fogo está apagando.")


def descrever(respostas):
    """Lista legível das escolhas de uma pessoa: [(pergunta, letra, opção)]."""
    return [(PERGUNTAS[i]["t"], c, PERGUNTAS[i]["o"][LETRAS.index(c)][0]) for i, c in enumerate(respostas)]
