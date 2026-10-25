# Gerador de Personagens — Flask + SQLite

Gerador de background para personagens de D&D 5e em Forgotten Realms (1490 DR).
O jogador monta o personagem em 6 etapas, gera a crônica e envia a ficha ao mestre, que consulta tudo numa página protegida por senha.

## Estrutura

| Arquivo | Para quê |
|---|---|
| `app.py` | Servidor Flask: página do gerador, envio de fichas, área do mestre, API de tabelas |
| `banco.py` | Esquema e leitura/gravação das tabelas do gerador (`dados.db`) |
| `fichas.py` | Esquema, validação e busca das fichas enviadas: Postgres (Neon) em produção, SQLite no computador |
| `gerenciar.py` | Linha de comando para criar, exportar, importar e conferir tabelas |
| `dados.db` | Tabelas do gerador (31). Só leitura; vai no repositório |
| `fichas.db` | Fichas no modo local (SQLite). Criado sozinho; **não** vai no repositório (`.gitignore`) |
| `dados/*.json` | Cópia legível de cada tabela, para editar e ver diferenças no Git |
| `templates/index.html` | A página do gerador (os dados entram pelo servidor) |
| `templates/mestre*.html` | Área do mestre |
| `render.yaml`, `requirements.txt` | Implantação |

## Rodar no computador

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
MESTRE_SENHA=escolha-uma-senha python app.py     # http://localhost:5000
```
No Windows (PowerShell): `$env:MESTRE_SENHA="escolha-uma-senha"; python app.py`.

## Variáveis de ambiente

| Variável | Padrão | Para quê |
|---|---|---|
| `MESTRE_SENHA` | (vazia) | Senha da área do mestre. **Sem ela, a área fica fechada.** |
| `MESTRE_USUARIO` | `mestre` | Usuário da área do mestre |
| `DATABASE_URL` | (vazia) | Connection string do Postgres (Neon). Com ela, as fichas vão para o Neon |
| `FICHAS_DB` | `fichas.db` na pasta | Sem `DATABASE_URL`: arquivo SQLite das fichas (uso no computador) |
| `MESTRE_FUSO` | `America/New_York` | Fuso das datas na área do mestre |

## Rotas

- `/` — o gerador
- `POST /api/fichas` — o jogador envia a ficha (nome do jogador e personagem). O mesmo jogador pode enviar várias fichas.
- `/mestre` — lista das fichas com busca por jogador, personagem, raça ou classe (pede usuário e senha)
- `/mestre/ficha/<id>` — ficha completa, com botão de copiar
- `/api/tabelas`, `/api/tabelas/<CHAVE>`, `/api/dados` — tabelas do gerador, só leitura
- `/saude` — checagem para a hospedagem

## Editar uma tabela do gerador

```bash
python gerenciar.py exportar        # banco → dados/*.json
# edite dados/PATRIA.json (por exemplo)
python gerenciar.py importar PATRIA # dados/PATRIA.json → banco
python gerenciar.py verificar       # banco e arquivos iguais?
```
Depois, envie `dados.db` e o JSON alterado para o repositório. `python gerenciar.py listar` mostra as tabelas e as observações (pendências, [NÃO VERIFICADO]).

## Publicar de graça: Render + Neon

O site roda no plano gratuito do Render e as fichas ficam no Postgres gratuito do Neon.
- **Render grátis:** o site dorme após 15 minutos sem acesso e leva cerca de 1 minuto para acordar no próximo acesso. São 750 horas grátis por mês, e o tempo dormindo não conta.
- **Neon grátis:** 1 GB por projeto, sem prazo de validade e sem cartão. O banco também dorme após 5 minutos sem uso e acorda sozinho.

**1. Neon (banco das fichas)**
1. Crie uma conta em neon.com e um projeto.
2. Copie a *connection string*: começa com `postgresql://` e normalmente traz `sslmode=require` no final; copie inteira, como o Neon mostrar. Ela contém a senha do banco; não a coloque no repositório.

**2. GitHub**
Crie um repositório com esta pasta. O `.gitignore` já deixa de fora o `fichas.db` local.

**3. Render (site)**
1. No Render, crie um **Blueprint** a partir do repositório. O `render.yaml` já define o plano gratuito e os comandos.
2. O Render pede dois valores:
   - `DATABASE_URL`: cole a connection string do Neon.
   - `MESTRE_SENHA`: a senha da sua área de consulta.
3. Depois do deploy, o Render mostra o link do site (termina em `.onrender.com`). A tabela de fichas é criada sozinha no primeiro acesso.

**4. Usar**
- Jogadores: mande o link do site.
- Você: abra `<link>/mestre`, usuário `mestre` e a senha que escolheu.

Para mudar a senha depois, edite `MESTRE_SENHA` nas variáveis de ambiente do serviço no Render.

## Conferências feitas

- Tabelas servidas idênticas às do HTML original de 30/09 (migração).
- Versão simplificada: 60 personagens no "Me surpreenda", todos com exatamente 27 pontos e todas as etapas válidas; fluxo "Eu escolho" completo no navegador em tamanho de celular.
- Envio: validação do nome, 3 fichas enviadas (duas do mesmo jogador), área do mestre recusa sem senha e com senha errada, busca funciona, nomes com HTML aparecem como texto. Roteiro rodado nos dois modos: Postgres 16 e SQLite.
