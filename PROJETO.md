# PROJETO — Gerador de Personagens (Jogadores)

Versão 1.4 · 24/10/2026 · Status: no ar em gerador-personagens.onrender.com; história editável e escolhas alteráveis (P26); revisões pendentes (seção 13)

---

## 0. Regras para o Claude neste projeto

1. Este documento é a fonte de verdade. Ler antes de qualquer tarefa do projeto.
2. Nunca inventar valor de tabela, faixa de dado, bônus ou número de regra. Se não foi verificado na fonte, marcar **[NÃO VERIFICADO]** e avisar.
3. Pendência aberta (seção 13) que afete a tarefa: perguntar antes de implementar. Não assumir em silêncio.
4. Quando uma decisão mudar, entregar o PROJETO.md atualizado (subir a versão e registrar na seção 14).
5. Comunicação direta, em português.

---

## 1. Visão

Uma aplicação web (Flask + banco SQLite), acessível por link público, que conduz o jogador passo a passo até um personagem de D&D 5e com **conceito e história completos**, ambientado em Forgotten Realms.

**Foco principal: gerar um background completo.** Regras de jogo entram só no que a história precisa; tudo o que não serve à história é simplificado ou sai (P23).

## 2. Público e tom

- Jogadores das mesas do mestre, incluindo iniciantes.
- Português simples, sem jargão sem explicação.
- A página **não** exibe avisos de regra nem pedidos de aprovação ("consulte seu mestre", etc.).

## 3. Ambientação

- Forgotten Realms, **ano 1490 DR**.
- Panteão para clérigos e paladinos: lista do mestre (3.3).
- Nomes de regiões e cidades ficam em inglês.

### 3.1 Regiões — base: Heroic Chronicle: Sword Coast and the North (D&D Beyond, 2020)
Dados verificados na fonte (artigo de James Haeck, D&D Beyond, 29/04/2020). Nomes em inglês até a tradução ser checada.

**Pátria (d100)**

| d100 | Região política |
|---|---|
| 1–50 | Lords' Alliance |
| 51–60 | Dwarfholds of the North |
| 61–70 | Island Kingdoms (inclui Moonshaes) |
| 71–95 | Independent Realms |
| 96–100 | Underdark |

**Assentamentos (d100 por região)**

| Região | Faixas |
|---|---|
| Lords' Alliance | 1–10 Amphail · 11–25 Baldur's Gate · 26–39 Daggerford · 40 Longsaddle · 41–50 Mirabar · 51–60 Neverwinter · 61–70 Silverymoon · 71–90 Waterdeep · 91–100 Yartar |
| Dwarfholds of the North | 1–20 Citadel Adbar · 21–40 Citadel Felbarr · 41–60 Gauntlgrym · 61–70 Ironmaster · 71–80 Mithral Hall · 81–99 Sundabar · 100 Thornhold |
| Island Kingdoms e Moonshaes | 1–25 Mintarn · 26–35 Northlander Isles · 36–85 Moonshae Isles · 86–89 Orlumbor · 90–99 Southern Isles · 100 Evermeet |
| Independent Realms | 1 Boareskyr Bridge · 2–4 Candlekeep · 5 Darkhold · 6–31 Elturgard · 32–41 Evereska · 42–48 Hartsvale · 49 Helm's Hold · 50–52 High Moor · 53–55 Trielta Hills · 56–60 Uthgardt Lands · 61–90 Luskan · 91–100 Icewind Dale |
| Underdark | 1–20 Gracklstugh · 21–30 Mantol-Derith · 31–80 Menzoberranzan · 81–100 Blingdenstone |

Do Heroic Chronicle usam-se **somente** as tabelas de pátria, assentamento e antecedentes (6.1). Aliados/rivais, família e momentos decisivos ficam de fora.

### 3.2 Regiões adicionais (fora da Costa da Espada)
- A rolagem usa o d100 original, sem alteração. As regiões adicionais entram **só por escolha**.
- Proposta (aguarda aprovação: P8g): Chult, Anauroch, Cormyr, Dalelands, Moonsea, Sembia, Amn, Tethyr, Calimshan, Thay, Rashemen.

### 3.3 Divindades (lista do mestre)
Nomes exatamente como o mestre definiu. Descrições com palavras próprias.

- **Divindades superiores de Faerûn:** Azuth, Bane, Chauntea, Cyric, Eilistraee, Gond, Helm, Ilmater, Kelemvor, Kossuth, Lathander, Lolth, Malar, Mask, Mielikki, Mystra, Oghma, Selûne, Shar, Shaundakul, Silvanus, Sune, Talos, Tempus, Torm, Tymora, Tyr, Umberlee, Uthgar, Waukeen.
- **Outras divindades de Faerûn:** Akadi, Auril, Beshaba, Cavaleiro Vermelho, Deneir, Eldath, Finder Agulhão da Wyvern, Gargauth, Garagos, Grumbar, Gwaeron Windstrom, Hoar, Istishia, Jergal, Lliira, Loviatar, Lurue, Milil, Nobanion, Savras, Sharess, Shiallia, Siamorphe, Talona, Tiamat, Ubtao, Ulutiu, Valkur, Velsharoon.
- **Panteão anão:** Abbathor, Berronar Prata Genuína, Clangeddin Barba Prateada, Duerra das Profundezas, Dugmaren Manto Brilhante, Dumathoin, Gorm Gulthyn, Haela Machado Brilhante, Laduguer, Marthammor Duin, Moradin, Sharindlar, Thard Harr, Vergadain.
- **Panteão drow:** Ghaunadaur, Kiaransalee, Selvetarm, Vhaeraun.
- **Panteão élfico:** Aerdrie Faenya, Angharradh, Corellon Larethian, Erevan Ilesere, Fenmarel Mestarine, Hanali Celanil, Labelas Enoreth, Rillifane Rallathil, Sashelas das Profundezas, Sehanine Arco da Lua, Shevarash, Solonor Thelandira.
- **Panteão gnomo:** Baervan Andarilho Selvagem, Baravar Manto das Sombras, Callarduran Mãos Suaves, Flandal Pele Blindada, Gaerdal Mão Férrea, Garl Glittergold, Segojan Convocador de Terra, Urdlen.
- **Panteão halfling:** Arvoreen, Brandobaris, Cyrrollalee, Sheela Peryroyl, Urogalan, Yondalla.
- **Panteão mulhorandi:** Anhur, Geb, Hathor, Horus-Re, Ísis, Nephthys, Osíris, Sebek, Set, Thoth.
- **Panteão orc:** Bahgtru, Gruumsh, Ilneval, Luthic, Shargaas, Yurtrus.
- Exibição e vínculo com domínios: P8h, P8i. Situação das divindades em 1490 DR: P8j.

## 4. Fonte de dados e texto

- Base mecânica: dnd5e.wikidot.com (regras 5e de 2014).
- Regiões: Heroic Chronicle: Sword Coast and the North (D&D Beyond).
- Idade: tabela de idade inicial da 3.5 como referência (7.7).
- Tabelas do "This Is Your Life": transcritas pelo mestre no arquivo `This_is_your_life` dos arquivos do projeto. A tabela de treinamento do Artífice foi criada pelo mestre (não é do Xanathar); a do Pugilista também não é do Xanathar.
- Extrair **somente nomes e números** (bônus, faixas de dados, valores).
- Toda descrição exibida na página é escrita com palavras próprias. Nenhum trecho copiado.
- **Armazenamento:** todas as tabelas usadas pela página ficam no banco SQLite `dados.db` (27 tabelas), com uma cópia legível em `dados/*.json`. Cada tabela registra descrição, fonte e observação (pendências e itens [NÃO VERIFICADO]). Ver 12.

## 5. Escopo do protótipo (Fase 1)

- **Nível 1.** Subclasse só para Clérigo, Feiticeiro e Bruxo, que a escolhem no nível 1. Subclasses de todos os livros oficiais de 2014 (PHB, Xanathar, Tasha, SCAG…).
- **Classes (14):** as 13 dos livros oficiais de 2014 (Artífice, Bárbaro, Bardo, Bruxo, Clérigo, Druida, Feiticeiro, Guerreiro, Ladino, Mago, Monge, Paladino, Patrulheiro) + **Pugilista (Pugilist)**, classe de terceiros incluída por decisão do mestre. O Pugilista não escolhe subclasse no nível 1. Fonte dos dados do Pugilista: arquivo com a descrição, a ser enviado pelo mestre aos arquivos do projeto (P18).
- **Raças (12), com sub-raças dentro da raça:** Humano, Anão (inclui Duergar), Elfo, Halfling, Gnomo (inclui Svirfneblin), Meio-elfo, Meio-orc, Draconato, Tiefling, Aasimar, Genasi, Golias. Lista completa de sub-raças e versão dos livros: P7b.
- **Nomes:** português oficial com o inglês entre parênteses, ex.: Patrulheiro (Ranger).
- Sem IA e sem login para o jogador. O jogador envia a ficha ao mestre com nome e e-mail (P24); o mestre consulta numa área com senha.

## 6. Fluxo

Seis etapas (P23):

1. **Tom** — chave "Crônica livre" / "Crônica leve" (7.6) e o caminho: **Eu escolho** (o jogador decide; em cada escolha há um dado de sugestão) ou **Me surpreenda** (os dados decidem tudo; depois o jogador revê).
2. **Quem é você** — raça e sub-raça (povos raros num bloco recolhido), classe (subclasse e divindade quando houver) e antecedente.
3. **De onde vem** — onde nasceu, idade (faixa típica: escolher ou rolar) e nome.
4. **Atributos** — perfis prontos por classe (7.1), bônus raciais sugeridos, escala humana.
5. **Crônica de origem** no estilo "This Is Your Life", com os eventos de dom (7.4).
6. **Personalidade e ficha** — resumo das escolhas com botão **Alterar** para cada etapa; traços, ideal, vínculo e defeito (sorteados, escolhidos ou escritos com as próprias palavras); outros traços livres; aparência; **história final editável** (parte da crônica gerada e pode ser reescrita; botão para voltar ao texto gerado); a ficha final para copiar ou imprimir; e o formulário **Enviar ao mestre**, que envia a versão editada (P24, P26).

Na etapa **Quem é você**, subclasse (Clérigo, Feiticeiro, Bruxo) e divindade (Clérigo) também têm dado de sorteio. Em toda etapa, enquanto o **Continuar** está bloqueado, o rodapé diz o que falta (P25).

Saíram (P23): os caminhos "ideia pronta", "ideia vaga" e "preciso de ajuda"; o questionário guiado; a lista de talentos do humano variante (a ficha mostra "Talento: a escolher"); os d6 de coerência nas rolagens de origem e raça (P34b).

### 6.1 Antecedentes
- Lista: PHB + SCAG. Tabelas "tornei-me X porque…" dos antecedentes do SCAG: arquivo `ANTECEDENTES_SCAG.md` (aguarda aprovação: P17e). Escolha livre; no "Me surpreenda", rolagem d100 (Heroic Chronicle, verificado):

| d100 | Antecedente | d100 | Antecedente |
|---|---|---|---|
| 1–4 | Acolyte (PH) | 53–56 | Inheritor (SCAG) |
| 5–8 | Charlatan (PH) | 57–60 | Knight of the Order (SCAG) |
| 9–12 | City Watch (SCAG) | 61–64 | Mercenary Veteran (SCAG) |
| 13–16 | Clan Crafter (SCAG) | 65–68 | Noble (PH) |
| 17–20 | Cloistered Scholar (SCAG) | 69–72 | Outlander (PH) |
| 21–24 | Courtier (SCAG) | 73–76 | Sage (PH) |
| 25–28 | Criminal (PH) | 77–80 | Sailor (PH) |
| 29–32 | Entertainer (PH) | 81–84 | Soldier (PH) |
| 33–36 | Faction Agent (SCAG) | 85–88 | Spy (PH) |
| 37–40 | Far Traveler (SCAG) | 89–92 | Urban Bounty Hunter (SCAG) |
| 41–44 | Folk Hero (PH) | 93–96 | Urchin (PH) |
| 45–48 | Guild Artisan (PH) | 97–99 | Uthgardt Tribe Member (SCAG) |
| 49–52 | Hermit (PH) | 100 | Waterdhavian Noble (SCAG) |

- Nomes em português oficial com o inglês entre parênteses na página (tradução a conferir).

**Navegação:** o jogador pode voltar a qualquer etapa. As etapas que dependem da alteração são refeitas, com aviso antes.

## 7. Regras mecânicas

### 7.1 Atributos
Só a **compra de pontos oficial** (verificada: Regras Básicas 2014, D&D Beyond, "Variant: Customizing Ability Scores"): 27 pontos, valores de 8 a 15 antes dos bônus raciais.

| Valor | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|
| Custo | 0 | 1 | 2 | 3 | 4 | 5 | 7 | 9 |

- **Perfis prontos** (tabela própria `PERFIS`, todos gastam exatamente 27): Especialista 15/15/15/8/8/8 · Dois focos 15/15/14/10/8/8 · Foco e apoio 15/14/14/10/10/8 · Padrão 15/14/13/12/10/8 · Versátil 14/14/14/10/10/10.
- **Ordem por classe** (tabela própria `ORDEM_CLASSE`): a página põe o maior valor no atributo principal da classe, e assim por diante. Clérigo e Guerreiro perguntam o estilo de luta (linha de frente/retaguarda; força/destreza). Pugilista: sem ordem até P18; usa a compra livre.
- **Compra de pontos livre** para jogadores experientes (+/−, até 27). Um perfil pode ser ajustado à mão depois.
- Saíram: 4d6, array padrão como método separado, "Rolei na mesa" dos atributos.

### 7.2 Fichas raciais (regra do Tasha)
- Ao escolher a raça, os bônus viram **fichas** que o jogador distribui livremente. A página já sugere: na ordem da classe, a 1ª ficha no atributo principal, a 2ª no segundo, e assim por diante (P23).
- Cada ficha vai em um atributo **diferente**.
- Formatos: +2/+1, +2/+2, +2/+1/+1, +1 em seis atributos, +1/+1 + talento. O formato de cada raça e sub-raça deve ser confirmado na fonte.
- Humano variante: talentos do PHB, Xanathar, Tasha, Fizban e Bigby (Glory of the Giants). Talentos raciais aparecem só para a raça correspondente. Pré-requisitos de cada talento (inclusive nível mínimo) a verificar na fonte; só entram os elegíveis no nível 1.
- Limite de 20 por atributo.
- **Sem CA** na ficha.

### 7.3 Escala humana
- Cada valor de atributo recebe uma frase do tipo "como isso aparece no dia a dia", onde **10 é a pessoa comum**.
- Textos próprios, a escrever para toda a faixa possível (3 a 20).

### 7.4 Dom e fraqueza
- Atributo **final** ≥ 17: gera um **evento obrigatório** na crônica explicando a origem do dom (um por atributo).
- ~~Atributo final ≤ 7 gera fraqueza~~: com a compra de pontos o menor valor é 8, então a regra não dispara mais (P23). As tabelas ficam no banco.
- Tabelas próprias do projeto.

### 7.5 Crônica
- Reproduz a **estrutura** do "This Is Your Life": faixas numéricas originais (arquivo `This_is_your_life`), com todo o texto reescrito.
- Infância (Memórias de infância): **3d6 + modificador de Carisma**. As faixas dos extremos ficam abertas ("3 ou menos" e "18 ou mais") para cobrir todos os resultados possíveis (conferir no livro).
- O número de eventos segue a tabela de eventos por idade do arquivo transcrito (raças longevas: P12d).
- **Efeitos mecânicos ficam só na narrativa.** Ouro, itens, cavalo, poção, pergaminho, vantagem/desvantagem e mudança de tendência não entram na ficha.
- Correção da transcrição: a nota "aplique o modificador do Estilo de Vida da Família" vale só para a tabela de Lar na Infância. Sob Estilo de Vida da Família ela é duplicação e é ignorada.
- Classes sem entrada na tabela suplementar de classe (Artífice, Pugilista): a tabela suplementar mantém as faixas originais (ela só define NPCs).

### 7.8 Raças exóticas (tabela suplementar de raça, resultado 96–00)
- O resultado 96–00 ("à escolha do mestre") vira **"Raça exótica"** e leva a uma rolagem nesta tabela.
- Lista definida pelo mestre (33 raças do *Monsters of the Multiverse*). Só nomes; nenhum dado mecânico.
- Distribuição: **tabela própria do projeto**, aprovada. Probabilidade igual para as 33 raças: 3 pontos cada (01–99); 100 = rolar de novo.

| d100 | Raça | d100 | Raça | d100 | Raça |
|---|---|---|---|---|---|
| 01–03 | Aarakocra | 34–36 | Genasi do Fogo (Fire) | 67–69 | Minotauro (Minotaur) |
| 04–06 | Aasimar | 37–39 | Genasi da Água (Water) | 70–72 | Orc |
| 07–09 | Bugbear | 40–42 | Githyanki | 73–75 | Sátiro (Satyr) |
| 10–12 | Centauro (Centaur) | 43–45 | Githzerai | 76–78 | Elfo do mar (Sea Elf) |
| 13–15 | Changeling | 46–48 | Goblin | 79–81 | Shadar-kai |
| 16–18 | Gnomo das profundezas (Deep Gnome) | 49–51 | Golias (Goliath) | 82–84 | Shifter |
| 19–21 | Duergar | 52–54 | Harengon | 85–87 | Tabaxi |
| 22–24 | Eladrin | 55–57 | Hobgoblin | 88–90 | Tortle |
| 25–27 | Fada (Fairy) | 58–60 | Kenku | 91–93 | Tritão (Triton) |
| 28–30 | Firbolg | 61–63 | Kobold | 94–96 | Yuan-ti |
| 31–33 | Genasi do Ar (Air) | 64–66 | Povo-lagarto (Lizardfolk) | 97–99 | Genasi da Terra (Earth) |
| | | | | 100 | Rolar de novo |

- Nomes em português: **[NÃO VERIFICADO]** contra a tradução oficial; conferir (P13d).

### 7.6 Modos da crônica
- **Livre:** relação extensa e completa de eventos, incluindo eventos pesados. Eventos leves também podem sair aleatoriamente.
- **Leve:** lista limitada. **Nunca** gera evento pesado ou sensível (mortes, tragédias graves e similares).
- Cada entrada das tabelas recebe a marcação leve/pesado: arquivo `CRONICA_MARCACAO.md` (aguarda revisão: P14d).
- **Mudar depois (P26):** com a crônica pronta, cada resultado tem **mudar**: o jogador escolhe outra opção ou rola de novo. O que depende dele é refeito ou pede nova rolagem; o resto fica.
- **Escolha manual (P25):** em cada passo da crônica o jogador pode rolar ou escolher a opção numa lista só com os textos, sem números. No modo leve, as opções pesadas não aparecem. Os resultados escolhidos aparecem na lista de resultados sem número.
- No modo leve, se a rolagem cair num evento pesado, a página re-rola até sair um evento leve. As faixas originais são mantidas. (A versão de 30/09 faz diferente: P21.)
- Texto de explicação na tela: escrever na implementação.

### 7.7 Idade
- Na etapa de raça: o jogador escolhe dentro da faixa típica ou rola.
- Fonte: imagem `Idades_Raça_dnd35.png` enviada pelo mestre (Tabelas I-11 e I-12, edição brasileira de Forgotten Realms, 3ª edição). Grupos de classe: mesma divisão da 3.5 (a legenda das colunas não aparece na imagem).

**Idade inicial (Tabela I-11)**

| Raça do projeto | Linha da tabela | Adulta | Simples (Bárbaro, Ladino, Feiticeiro, Bruxo, Pugilista) | Intermediária (Bardo, Guerreiro, Paladino, Patrulheiro) | Complexa (Clérigo, Druida, Monge, Mago, Artífice) |
|---|---|---|---|---|---|
| Humano | Humano | 15 | +1d4 | +1d6 | +2d6 |
| Anão, Duergar | Anão (qualquer) | 40 | +3d6 | +5d6 (P12f) | +7d6 |
| Elfo (todas as sub-raças) | Elfo (qualquer) | 110 | +4d6 | +6d6 | +10d6 |
| Svirfneblin | Gnomo das profundezas | 20 (P12f) | +4d6 | +6d6 | +9d6 |
| Gnomo (demais sub-raças) | Gnomo das rochas | 40 | +4d6 | +6d6 | +9d6 |
| Meio-elfo | Meio-elfo | 20 | +1d6 | +2d6 | +3d6 |
| Meio-orc | Meio-orc | 14 | +1d4 | +1d6 | +2d6 |
| Halfling | Halfling | 20 | +2d4 | +3d6 | +4d6 |
| Aasimar, Tiefling, Genasi | Tocados pelos planos (qualquer) | 15 | +1d6 | +1d8 | +2d8 |
| Golias, Draconato | — | valores próprios (P12e) | | | |

**Efeitos da idade (Tabela I-12)** — referência para a faixa típica e para P12d

| Linha | Meia-idade | Velho | Venerável | Idade máxima |
|---|---|---|---|---|
| Humano | 35 | 53 | 70 | +2d20 |
| Anão (qualquer) | 125 | 188 | 250 | +2d% |
| Elfo do sol | 210 | 315 | 420 | +6d% |
| Elfo, outro | 175 | 263 | 350 | +4d% |
| Gnomo das profundezas | 80 | 120 | 160 | +2d% |
| Gnomo das rochas | 100 | 150 | 200 | +3d% |
| Meio-elfo | 62 | 93 | 125 | +3d20 |
| Meio-orc | 30 | 45 | 60 | +2d10 |
| Halfling | 50 | 75 | 100 | +5d20 |
| Tocados pelos planos | 45 | 68 | 90 | +3d20 |

Nota: na imagem, a primeira coluna da I-12 está rotulada "Maturidade", mas os valores (Humano 35) são de **meia-idade**. Tratado como erro de rótulo.

**Número de eventos para raças longevas (proposta P12d, própria do projeto):** converter a idade do personagem em "idade equivalente humana" = idade × 35 ÷ meia-idade da raça, e usar essa idade na tabela de eventos por idade do "This Is Your Life". Exemplo: elfo de 120 anos → 120 × 35 ÷ 175 = 24 → faixa de 21–30 anos.

## 8. Componente de dados

- Toda aleatoriedade mostra o dado na tela (d6, d20, d100…).
- Dois botões em toda rolagem:
  - **Rolar aqui** — a página rola e mostra o resultado.
  - **Rolei na mesa** — o jogador digita o resultado; a página valida a faixa do dado. Aparece como link discreto abaixo do dado (P23).

## 9. Ficha final

- Versão para copiar (texto) e versão para imprimir.
- Conteúdo: nome, raça/sub-raça, classe, nível 1, idade, região, atributos + modificadores, traços raciais resumidos, antecedente, idiomas, história (crônica), personalidade, aparência.
- A ficha mostra a classe sem o nível (P26).
- Fora: CA, PV, perícias, equipamento, magias.
- **Envio ao mestre (P24):** o jogador informa nome e e-mail e envia. Cada envio é uma ficha nova (o mesmo e-mail pode ter várias). A página avisa que nome e e-mail ficam guardados só para o mestre consultar.
- **Área do mestre:** `/mestre`, com usuário e senha; lista com busca (jogador, e-mail, personagem, raça, classe), ficha completa com botão de copiar.

## 10. Fora do escopo da Fase 1

IA, login de jogador, PDF, CA.

## 11. Roteiro

| Fase | Entrega |
|---|---|
| 1 | Protótipo sem IA, sem login, sem salvar |
| 2 | Coleta de feedback dos jogadores |
| 3 | Exportar PDF (salvar já entrou na 1.1: P24) |
| 4 | IA para redigir a história |
| 5 | ~~Envio da ficha ao mestre~~ (entrou na 1.1: P24) |

## 12. Requisitos técnicos (Fase 1)

- **Servidor:** Python + Flask (`app.py`). A página é o HTML da versão de 30/09, sem dados embutidos (`templates/index.html`); o servidor injeta as tabelas do banco a cada acesso.
- **Bancos:** `dados.db` (29 tabelas do gerador, só leitura, vai no repositório). Fichas dos jogadores: **Postgres no Neon** em produção (`DATABASE_URL`); SQLite (`fichas.db`) só para rodar no computador (P20, P24, P20a).
- **Área do mestre:** autenticação HTTP Basic; senha em `MESTRE_SENHA` (sem ela, a área fica fechada).
- **Edição de tabelas:** pelo `gerenciar.py` (exportar → editar `dados/<CHAVE>.json` → importar). Não há rota de escrita na web.
- **API de leitura:** `/api/tabelas`, `/api/tabelas/<chave>`, `/api/dados`; checagem em `/saude`.
- **Qualquer pessoa com o link abre a página, sem conta e sem login.**
- **Hospedagem (P20a):** Render, plano gratuito (o site dorme após 15 min sem acesso e leva ~1 min para acordar; 750 h/mês) + Neon, plano gratuito (1 GB por projeto, sem prazo, sem cartão). Conferido em render.com/docs/free e neon.com/pricing em 24/10/2026. `render.yaml` pronto; o Render pede `DATABASE_URL` e `MESTRE_SENHA`.
- O artifact de 30/09 deixa de ser a hospedagem oficial quando o servidor entrar no ar.
- Funcionar bem no celular.

---

## 13. Pendências

### Abertas

| ID | Pergunta | Sugestão |
|---|---|---|
| P23a | Aprovar as tabelas próprias `PERFIS` e `ORDEM_CLASSE` (7.1) depois de testar o artifact. | — |
| P21 | Modo leve: a versão de 30/09 troca o resultado pesado pela entrada leve vizinha da tabela; o 7.6 e o texto da tela dizem que a página rola de novo. Qual vale? | Seguir o 7.6 (re-rolar) e manter o texto da tela |
| P22 | A versão de 30/09 tem decisões que não estão neste documento: raças exóticas jogáveis (ligado a P17f), idade das raças exóticas (tabela IDADE_EXO), nomes humanos por estilo regional, sobrenomes e clãs. (A coerência P34b saiu na 1.0.) Registrar aqui? | Mestre confirma; Claude registra |
| P16a' | A página usa 12 nomes por coluna (d12); `NOMES_RACAS.md` v2 tem 30 por coluna. Atualizar a tabela NOMES do banco depois de decidida a P16a? | Sim, após P16a |
| P8g | Aprovar a lista de regiões adicionais (3.2). | — |
| P12d | Número de eventos para raças longevas: aprovar a proposta de "idade equivalente humana" (7.7). | — |
| P12f | Conferir no livro: Anão, coluna Intermediária aparece como +1d6 na imagem (menor que a Simples, +3d6); o SRD 3.5 dá +5d6. Gnomo das profundezas adulto aos 20 (o das rochas, aos 40): confirmar. | Anão +5d6; gnomo das profundezas conforme o livro |
| P8h | Divindades: mostrar todas para qualquer raça, ou destacar o panteão da raça do personagem? | Mostrar todas, com o panteão da raça no topo |
| P8i | Clérigo: o domínio (subclasse) fica restrito aos domínios da divindade? Os domínios por divindade não estão verificados. | Sem restrição; a página só sugere |
| P8j | A lista parece da era da 3ª edição (1372 DR). Algumas divindades podem ter mudado de situação até 1490 DR. Conferir com o SCAG? | Claude confere e aponta divergências; o mestre decide |
| P12e | Golias e Draconato não têm tabela na 3.5. Aprovar valores próprios, derivados do texto de idade da 5e de cada raça? | Claude propõe; o mestre aprova |
| P14d | Revisar `CRONICA_MARCACAO.md`, incluindo os 3 pontos listados no fim do arquivo. | — |
| P17a' | Demais entradas "de escolha do mestre" (item, poção, pergaminho): como resolver sem citar o mestre? | O jogador escolhe ou a página rola |
| P17f | As raças exóticas servem só para NPCs (pais, amigos, rivais) ou também são jogáveis? (A versão de 30/09 as trata como jogáveis: P22.) | Só NPCs; jogáveis continuam as 12 do escopo |
| P13d | Nomes em português das raças exóticas: conferir com a tradução oficial. | Sem tradução oficial, manter o inglês |
| P17b | Irmãos: anão/elfo subtraem 2 do d10; resultado 0 ou menor não tem faixa. | Tratar como "nenhum" |
| P17e | Aprovar `ANTECEDENTES_SCAG.md` (72 entradas próprias). | — |
| P18 | Pugilista: arquivo com a descrição da classe. Também define a ordem de atributos dele (7.1). | Ação do mestre |

### Decididas

| ID | Decisão | Versão |
|---|---|---|
| P20a | Hospedagem gratuita: Render (site) + Neon (Postgres das fichas); SQLite fica só para uso local | 1.2 |
| P26 | Ficha sem nível; história final editável e traços próprios; resumo das escolhas com Alterar; mudar resultados da crônica depois de pronta | 1.4 |
| P25 | Crônica: escolha manual por lista de textos, sem números; dado para subclasse e divindade; aviso do que falta para continuar | 1.3 |
| P24 | Salvar fichas no servidor Flask com nome do jogador e e-mail; várias fichas por e-mail; consulta do mestre com senha, lista com busca (substitui "sem salvar" e antecipa a Fase 5) | 1.1 |
| P23 | Foco no background: 6 etapas, 2 caminhos, só compra de pontos com perfis por classe, fichas sugeridas; saem questionário, talentos, coerência P34b e fraqueza ≤ 7 | 1.0 |
| P11c | Compra de pontos verificada na fonte; 4d6 e array saem como métodos (substitui P11/P11b) | 1.0 |
| P20 | Arquitetura: Python + Flask + SQLite; hospedagem em servidor na nuvem (o banco de tabelas segue só leitura; as fichas ficam em banco próprio desde a 1.1) | 0.9 |
| P1 | Nível 1; todas as classes dos livros oficiais | 0.2 |
| P1b | Subclasse só para Clérigo, Feiticeiro e Bruxo | 0.3 |
| P1c | Subclasses de todos os livros oficiais de 2014 | 0.4 |
| P2 | Antecedente escolhido na etapa de conceito e justificado na crônica | 0.2 |
| P2b | Antecedentes PHB + SCAG; d100 do Heroic Chronicle | 0.4 |
| P5b | Transcrição do "This Is Your Life" entregue pelo mestre (arquivo `This_is_your_life`) | 0.5 |
| P5c | Infância: 3d6 + mod. de Carisma (corrige o "d6" do briefing) | 0.5 |
| P5d | Efeitos mecânicos da crônica só na narrativa | 0.5 |
| P5e | Tabela de treinamento do Artífice: criação do mestre, aceita como fonte | 0.5 |
| P5f | Pugilista incluído no projeto (14 classes) | 0.5 |
| P17a | Raça 96–00 da tabela suplementar → "Raça exótica", com tabela de 33 raças definida pelo mestre | 0.6 |
| P19 | Idade do Pugilista: coluna do Bárbaro; nome "Pugilista (Pugilist)" | 0.6 |
| P14c | Claude faz a marcação leve/pesado; o mestre revisa | 0.7 |
| P17c | Claude cria as tabelas d6 dos antecedentes do SCAG | 0.7 |
| P17d | Raças exóticas: d100 com probabilidade igual (3 pontos cada; 100 = rolar de novo) | 0.7 |
| P3 | Ficha mínima: atributos + modificadores, traços raciais resumidos, antecedente, idiomas, história, personalidade, aparência | 0.2 |
| P4 / P4b | Link público; conta Pro → artifact publicado no claude.ai (substituído por P20 na 0.9) | 0.3 |
| P5 | Estrutura do "This Is Your Life", faixas originais, texto reescrito | 0.2 |
| P6 / P6b | Talentos: PHB + Tasha + Xanathar + Fizban + Bigby; raciais filtrados pela raça | 0.3 |
| P7 / P7b | 12 raças; sub-raças dos livros originais; Duergar em Anão; Svirfneblin em Gnomo | 0.3 |
| P8a | Regiões com base no Heroic Chronicle: Sword Coast, mais áreas emblemáticas | 0.3 |
| P8b | Ano 1490 DR | 0.3 |
| P8c | Divindades principais de Faerûn, lista curta | 0.3 |
| P8d | Rolagem pelo d100 original; regiões adicionais só por escolha | 0.4 |
| P8e | Do Heroic Chronicle, só pátria e assentamento (e a tabela de antecedentes, P2b) | 0.4 |
| P9 | Pronta / Vaga / Ajuda / Surpreenda (substituído por P23 na 1.0) | 0.2 |
| P10 | Fraqueza ≤7: escolher ou rolar d6 (sem efeito desde a 1.0: P23) | 0.2 |
| P11 / P11b | Métodos: 4d6, compra de pontos, array (substituído por P11c na 1.0) | 0.3 |
| P12 / P12b | Idade na etapa de raça; referência na tabela 3.5; lacunas propostas pelo Claude e aprovadas pelo mestre | 0.3 |
| P12c | Bruxo com Feiticeiro; Artífice com Mago; raças faltantes transcritas pelo mestre (entregue: `Idades_Raça_dnd35.png`) | 0.8 |
| P8f | Lista de divindades definida pelo mestre (3.3), substitui a "lista curta" de P8c | 0.8 |
| P13 / P13b | Português oficial + inglês; referência: tradução brasileira atual do Livro do Jogador | 0.3 |
| P13c | Regiões e cidades em inglês | 0.4 |
| P14 / P14b | Chave livre/leve; no modo leve, re-rolar até sair evento leve | 0.3 |
| P15 | Pode voltar; dependentes refeitas com aviso | 0.2 |
| P16 | Nomes por raça/região | 0.2 |

## 14. Registro de decisões

| Data | Versão | Decisão |
|---|---|---|
| 25/09/2026 | 0.1 | Especificação inicial criada a partir do briefing do mestre |
| 25/09/2026 | 0.2 | P1–P16 decididas; compra de pontos adicionada; modos livre/leve; conteúdo da ficha definido; link público obrigatório; pendências derivadas abertas (P1b, P4b, P5b, P6b, P7b, P8a–c, P11b, P12b, P13b, P14b) |
| 25/09/2026 | 0.3 | P1b, P4b, P6b, P7b, P8a–c, P11b, P12b, P13b, P14b decididas; regiões do Heroic Chronicle e tabela de idade 3.5 verificadas e registradas; novas pendências P1c, P2b, P8d–f, P12c–d, P13c |
| 25/09/2026 | 0.4 | P1c, P2b, P8d, P8e, P12c, P13c decididas; tabela d100 de antecedentes registrada; propostas de divindades e regiões adicionais; fontes de idade pesquisadas; novas pendências P8g, P12e |
| 25/09/2026 | 0.5 | Transcrição revisada; infância corrigida para 3d6 + CAR; efeitos mecânicos só narrativos; Artífice (tabela do mestre) aceito; Pugilista incluído; novas pendências P14c, P17a–c, P18, P19 |
| 25/09/2026 | 0.6 | Pugilista: idade pela coluna do Bárbaro e nome definido; raça 96–00 vira "Raça exótica" com tabela de 33 raças (distribuição própria, aguarda aprovação); novas pendências P13d, P17a', P17d |
| 25/09/2026 | 0.7 | Tabela de raças exóticas aprovada; entregues `CRONICA_MARCACAO.md` e `ANTECEDENTES_SCAG.md` para revisão; pendências P14d, P17e, P17f |
| 25/09/2026 | 0.8 | Tabela de idades de Forgotten Realms (I-11 e I-12) registrada; lista completa de divindades do mestre; proposta de idade equivalente humana (P12d); novas pendências P8h–j, P12f |
| 24/10/2026 | 0.9 | P20: migração para Flask + SQLite, banco só com as tabelas, hospedagem em nuvem (substitui P4/P4b); seções 1, 4, 5, 10 e 12 atualizadas; versão de 30/09 migrada sem mudar dados nem comportamento; novas pendências P20a, P21, P22, P16a' |
| 24/10/2026 | 1.0 | P23: foco no background; fluxo de 6 etapas e 2 caminhos; atributos só por compra de pontos (verificada, P11c) com perfis prontos e ordem por classe (tabelas próprias PERFIS e ORDEM_CLASSE no banco); fichas raciais sugeridas; saem questionário, talentos, coerência P34b e fraqueza ≤ 7; 'Rolei na mesa' discreto; nova pendência P23a |
| 24/10/2026 | 1.1 | P24: envio da ficha ao mestre (nome, e-mail, várias fichas por e-mail), banco `fichas.db`, área `/mestre` com senha e busca; hospedagem passa a exigir disco permanente (P20a atualizada) |
| 24/10/2026 | 1.2 | P20a: Render grátis + Neon grátis; fichas passam a usar Postgres em produção (`DATABASE_URL`), SQLite só local; `render.yaml` sem disco |
| 24/10/2026 | 1.3 | P25: escolha manual na crônica (opções só em texto, respeitando o modo leve); dados de subclasse e divindade (o Continuar travava com Clérigo, Feiticeiro e Bruxo sorteados); aviso do que falta; corrigido o nome da etapa atual invisível na barra |
| 24/10/2026 | 1.4 | P26: ficha sem nível; história final editável (a ficha enviada usa a versão editada); traços de personalidade escritos pelo jogador e campo de outros traços; resumo das escolhas com Alterar; resultados da crônica podem ser mudados depois de prontos |
