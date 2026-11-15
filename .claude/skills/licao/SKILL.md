---
name: licao
description: Registra uma armadilha técnica ou erro de diagnóstico em docs/licoes/, no formato do projeto, e regera o índice das lições. Use quando uma hipótese sua foi refutada por evidência, uma premissa do projeto se revelou falsa, um defeito custou mais de uma rodada para diagnosticar, ou o usuário corrigiu um entendimento seu — e também quando ele disser "registre essa lição", "isso vale uma lição" ou invocar /licao.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Registrar uma lição

**Lê:** `docs/licoes/` (para não duplicar) e `docs/licoes/README.md` (o formato).
**Escreve:** `docs/licoes/<id>.md`; **e obrigatoriamente** `.claude/indice/licoes.yaml`, pelo
`--gerar`. Lição fora do índice **não é encontrada por ninguém**. Se a lição implicar ação
obrigatória, escreve também a regra no `AGENTS.md`.
**Decide:** se é lição mesmo: os quatro motivos abaixo, e nada além deles.

## Antes de escrever: isto é mesmo uma lição?

Responda **"o que se achava"** em uma frase. Se não conseguir, **pare**: não é lição, é
documentação, e o lugar é outro (`AGENTS.md`, `docs/adr/`, `specs/` ou o `CHANGELOG.md`; a tabela
está em `docs/licoes/README.md`).

Os quatro motivos, e só eles:

1. uma **hipótese foi refutada por evidência**;
2. uma **premissa do projeto se revelou falsa**;
3. um **defeito custou mais de uma rodada** para diagnosticar;
4. o **usuário corrigiu** um entendimento seu.

Escrever demais estraga o acervo. Na dúvida, não escreva.

## 1. Conferir se já existe

```bash
grep -ril "<palavra-chave do assunto>" docs/licoes/
```

Se existir uma lição próxima, **atualize-a** em vez de criar outra: acrescente a nova evidência e a
data. Duas lições sobre a mesma armadilha valem menos que uma.

## 2. Escrever `docs/licoes/<id>.md`

O formato que vale é o de `docs/licoes/README.md`. O esqueleto típico:

```yaml
---
id: kebab-case-curto-e-descritivo     # igual ao nome do arquivo
data: AAAA-MM-DD
area: <uma das áreas listadas no README>
tipo: premissa-falsa | armadilha | erro-de-diagnostico | custo-escondido
custo: "uma linha: tempo, rodada, deploy, dinheiro"
gatilho: "em que circunstância apareceu"
refs:
  - caminho/do/arquivo.py:123
gatilhos:                             # opcional: em que ação o gancho entrega
  - '\bpytest\b'
---

**O que se achava:** duas a quatro linhas.

**O que é:** duas a quatro linhas, com a evidência: número medido, saída real, linha de código.

**Como perceber da próxima vez:** o sinal observável.
```

Regras de escrita:

- **`refs` com linha**, sempre que houver código. `agenda.py` não ajuda; `agenda.py:142` ajuda.
- **Evidência, não impressão.** "Ficou lento" não; "a busca de horários foi de 120 ms para 3,1 s
  com 10 mil consultas no banco" sim.
- **"Como perceber" é a seção que vale.** Um sinal observável, não um conselho. "Tome cuidado com
  fuso horário" não serve; "se a consulta marcada aparece uma hora adiantada só nas datas depois
  da mudança de horário, o servidor está gravando em hora local" serve.
- **Vocabulário controlado** de `area` e `tipo`: use os valores do README. Valor novo exige
  atualizar o `docs/licoes/README.md` e o `AREAS_VALIDAS` ou o `TIPOS_VALIDOS` do
  `.claude/regua.py` no mesmo commit.

### `gatilho:` e `gatilhos:` são campos diferentes

Os nomes se parecem; o papel não.

- **`gatilho:`** (singular, obrigatório na prática): a **circunstância**, em prosa, em que a
  armadilha apareceu. É para quem lê a lição. O gancho não o usa.
- **`gatilhos:`** (plural, opcional): a lista de **expressões regulares** que dizem **em que ação**
  o gancho entrega a lição. Cada uma é testada, sem diferenciar maiúsculas, contra o caminho do
  arquivo que o agente vai editar e contra o comando que ele vai rodar; basta uma casar. Sem
  `gatilhos:`, a lição chega por área (toda ação que toca a `area` dela). Com eles, chega só
  quando um casa, e na frente das outras.
  - Lista em bloco, um item por linha, **entre aspas simples** (`  - '\bgit\s+push\b'`): entre
    aspas duplas, `\b` vira outro caractere e a regex nunca casa (a régua acusa).
  - O gatilho descreve a ação em que o erro acontece: `\bgit\s+push\b`, não `git`. Antes de
    gravar, pense em três ações comuns que **não** deveriam receber a lição e confira que nenhuma
    casa.
  - O detalhe está em `docs/licoes/README.md`, "`gatilhos:` — em que ação a lição chega".

E nenhum dos dois é um dos **quatro motivos** (o que justifica escrever a lição, acima): os motivos
decidem **se** a lição existe; o `gatilho:` conta **onde** ela nasceu; os `gatilhos:` decidem
**quando** ela chega.

## 3. Propagar, se for o caso

- **Implica ação obrigatória daqui para frente?** Acrescente a regra no `AGENTS.md`, curta e
  imperativa, **citando** a lição. A regra manda; a lição explica.
- **Contradiz uma spec ou um ADR?** Diga ao usuário. Não corrija spec fechada por conta própria.
- **É preferência do usuário ou estado do projeto?** Não é lição: vai para a memória do agente.

## 4. Regerar o índice: sem isto a lição não é encontrada

**Primeiro o `git add` da lição, depois o `--gerar`.** Se o índice só vê o que o git rastreia, sem o
`git add` a lição fica de fora sem erro nenhum.

```bash
git add docs/licoes/<id>.md
python3 .claude/regua.py --gerar      # no Windows, python ou py -3
python3 .claude/regua.py --conferir
```

**Não é opcional.** Quem consulta as lições (a skill `iniciar-conversa`, um gancho, outra conversa)
lê `.claude/indice/licoes.yaml`, não a pasta. Lição escrita e índice não regerado = lição que
existe no repositório e **nunca chega** a quem toca a área.

Se o comando recusar o arquivo (id fora de `[a-z0-9-]`, id diferente do nome do arquivo), o
problema está no frontmatter, não no comando.

**Sem Python nesta máquina** (nenhum Python 3.8+ que rode, conferido como na skill `diagnostico`):
pule o `--gerar` e o `--conferir` e diga ao usuário que pulou. A lição já vale para quem a busca
em `docs/licoes/`; o índice fica defasado até alguém rodar a régua numa máquina com Python, e esse
alguém faz o commit do índice.

## 5. Fechar

Commit em português, com a lição no corpo da mensagem **e o `licoes.yaml` regerado junto**: os dois
no mesmo commit, senão o índice chega defasado na `main`. Sem Python, o commit leva só a lição, e a
mensagem diz que o índice ficou para depois. Se a lição nasceu de uma correção do
usuário, **cite a frase dele**: é o que torna o registro verificável depois.

## Restrições

- Nada de segredo, token, identificador interno, endereço de e-mail, hostname de cliente ou
  conteúdo de documento de cliente.
- Nunca registre como lição algo que você não verificou. Suspeita não confirmada vira pendência no
  roadmap, não lição.
- Não reescreva lição antiga para parecer que já se sabia. O acervo vale pelo registro honesto do
  erro.
