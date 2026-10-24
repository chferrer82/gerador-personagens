# Proposta — Foco no background e simplificação (P23)

Versão 1 · 24/10/2026 · Status: aguarda aprovação do mestre
Base: versão Flask (PROJETO.md v0.9). Nada foi implementado ainda.

---

## A. Atributos: só compra de pontos, com conjuntos prontos por classe

### A.1 Regra oficial (verificada)
Fonte: Regras Básicas de 2014, D&D Beyond, "Variant: Customizing Ability Scores".
27 pontos; valores de 8 a 15 antes dos bônus raciais.

| Valor | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|
| Custo | 0 | 1 | 2 | 3 | 4 | 5 | 7 | 9 |

É a mesma tabela que a página já usa: o **[NÃO VERIFICADO]** do 7.1 sai.

### A.2 Conjuntos prontos (todos gastam exatamente 27 pontos)
Existem 65 conjuntos que gastam os 27 pontos inteiros. Para não confundir, a página mostra só 5:

| Perfil | Valores | Para quem |
|---|---|---|
| Especialista | 15, 15, 15, 8, 8, 8 | Três atributos fortes, três fracos |
| Dois focos | 15, 15, 14, 10, 8, 8 | Dois atributos principais e um apoio |
| Foco e apoio | 15, 14, 14, 10, 10, 8 | Um principal, dois apoios |
| Padrão | 15, 14, 13, 12, 10, 8 | O array padrão (também custa 27) |
| Versátil | 14, 14, 14, 10, 10, 10 | Sem nenhum ponto fraco |

Conferi a soma de cada um com a tabela A.1.
Quem quiser outro conjunto usa a **compra de pontos livre** (+/−, limite de 27), que a página já tem.

### A.3 Distribuição automática por classe (tabela própria, para aprovar)
O jogador escolhe o perfil, e a página já põe cada valor no atributo certo, na ordem abaixo: o maior valor vai na 1ª prioridade, e assim por diante. O jogador pode trocar dois atributos de lugar, se quiser.

| Classe | Ordem de prioridade |
|---|---|
| Artífice | INT, CON, DES, SAB, FOR, CAR |
| Bárbaro | FOR, CON, DES, SAB, CAR, INT |
| Bardo | CAR, DES, CON, SAB, INT, FOR |
| Bruxo | CAR, CON, DES, SAB, INT, FOR |
| Clérigo — linha de frente | SAB, FOR, CON, CAR, DES, INT |
| Clérigo — retaguarda | SAB, CON, DES, CAR, INT, FOR |
| Druida | SAB, CON, DES, INT, CAR, FOR |
| Feiticeiro | CAR, CON, DES, SAB, INT, FOR |
| Guerreiro — força | FOR, CON, DES, SAB, CAR, INT |
| Guerreiro — destreza | DES, CON, SAB, FOR, INT, CAR |
| Ladino | DES, CON, SAB, INT, CAR, FOR |
| Mago | INT, CON, DES, SAB, CAR, FOR |
| Monge | DES, SAB, CON, FOR, INT, CAR |
| Paladino | FOR, CAR, CON, SAB, DES, INT |
| Patrulheiro | DES, SAB, CON, FOR, INT, CAR |
| Pugilista | **[NÃO VERIFICADO]** — depende do arquivo da classe (P18) |

Clérigo e Guerreiro perguntam o estilo em uma linha ("Luta na linha de frente ou de longe?"), sem falar em armadura nem em regras.

### A.4 Fichas raciais
A página sugere automaticamente: **+2 na 1ª prioridade e +1 na 2ª** (nos formatos com três fichas, +1 na 3ª). O jogador pode mudar.
Efeito: um 15 na 1ª prioridade vira 17, o que gera o evento de dom na crônica (7.4). É um gancho de história, não um problema.

---

## B. Simplificações no resto do gerador

Cada item pode ser aprovado ou recusado separadamente.

| # | Hoje | Proposta | Motivo |
|---|---|---|---|
| B1 | 4 caminhos no início (ideia pronta, ideia vaga, ajuda, surpreenda) | **2 caminhos:** "Eu escolho" (com sugestões nas telas) e "Me surpreenda" | Os 4 caminhos levam às mesmas telas |
| B2 | Questionário da "ideia vaga" (7 perguntas) | Sai; as sugestões ficam dentro de cada tela | Menos uma etapa antes de começar |
| B3 | Atributos: 4d6, array padrão e compra de pontos | Só compra de pontos com os perfis da parte A | Decisão do mestre |
| B4 | Fraqueza para atributo final ≤ 7 (7.4) | Sai | Com compra de pontos o menor valor é 8; a regra nunca dispara |
| B5 | Humano variante: talento com lista "em construção" | A ficha mostra "talento: a escolher"; a página não lista talentos | Talento é regra de jogo, não história |
| B6 | Coerência nas rolagens de origem (P34b): combinações raras pedem d6 extra | Sai; a rolagem aceita qualquer combinação e a crônica explica | Menos dados e avisos na tela |
| B7 | 9 etapas | **6 etapas:** Tom → Quem é você (raça, classe, antecedente) → De onde vem (região, idade, nome) → Atributos → Crônica → Personalidade e ficha | Menos telas, a história no centro |
| B8 | "Rolei na mesa" em toda rolagem (seção 8) | Mantém, mas como link discreto "rolei na mesa" embaixo do dado | Continua possível, sem ocupar espaço |

Itens que **ficam** porque fazem a história: modo livre/leve, crônica completa, dom (≥ 17), escala humana, personalidade, aparência, idade, nome.

---

## C. Pendências que esta proposta toca

- **P18** — Pugilista: sem o arquivo da classe, a ordem de atributos fica em aberto.
- **P21** — Modo leve (trocar pela entrada vizinha ou re-rolar) continua aberta; não muda nada aqui.
- **7.1 do PROJETO.md** — com a aprovação, passa a registrar só a compra de pontos, verificada.
