---
name: licao
description: Registra uma armadilha técnica ou erro de diagnóstico em docs/licoes/, no formato do projeto, e regera o índice das lições. Use quando uma hipótese sua foi refutada por evidência, uma premissa do projeto se revelou falsa, um defeito custou mais de uma rodada para diagnosticar, ou o usuário corrigiu um entendimento seu — e também quando ele disser "registre essa lição", "isso vale uma lição" ou invocar /licao.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Registrar uma lição

**Lê:** `docs/licoes/` (para não duplicar) e `docs/licoes/README.md` (o formato).
**Escreve:** `docs/licoes/<id>.md`; **e obrigatoriamente** `.claude/indice/licoes.yaml`, pelo
`--gerar`. Lição fora do índice chega pelo gancho só lida do Markdown, com o aviso de índice
defasado em toda sessão. Se a lição implicar ação obrigatória, escreve também a regra: no
`AGENTS.md`, se ela vale para toda tarefa; no `docs/regras-de-area.md`, se ela só muda a decisão de
quem mexe numa área (passo 3).
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
refs:                                 # entre aspas simples, como os gatilhos
  - 'caminho/do/arquivo.py:123 `def a_funcao_citada`'
gatilhos:                             # opcional: em que ação o gancho entrega
  - '\bpytest\b'
---

**O que se achava:** duas a quatro linhas.

**O que é:** duas a quatro linhas, com a evidência: número medido, saída real, linha de código.

**Como perceber da próxima vez:** o sinal observável.
```

Regras de escrita:

- **`refs` com linha e âncora**, sempre que houver código: o caminho, a linha e, entre crases, um
  trecho que está naquela linha (`` agenda.py:142 `def horarios_livres` ``). A régua confere que o
  trecho continua na linha citada e, quando ele muda de lugar, avisa a linha nova. `agenda.py` não
  ajuda; `agenda.py:142` sem o trecho a régua não confere. Ponha o item entre aspas simples: sem
  elas, um ` #` na âncora (o tamanho de uma tabela no Luau, um comentário) corta o item. A aspa
  simples dentro da âncora vai dobrada (`print(''oi'')`); sem isso, a régua pula a ref sem
  avisar. A ref em
  prosa (sem caminho no começo) vale, e a régua a pula; o caminho de um script do place
  (`game.ServerScriptService.…`) também, porque a régua não lê o place.
- **Evidência, não impressão.** "Ficou lento" não; "a busca de horários foi de 120 ms para 3,1 s
  com 10 mil consultas no banco" sim.
- **"Como perceber" é a seção que vale.** Um sinal observável, não um conselho. "Tome cuidado com
  fuso horário" não serve; "se a consulta marcada aparece uma hora adiantada só nas datas depois
  da mudança de horário, o servidor está gravando em hora local" serve.
- **Vocabulário controlado** de `area` e `tipo`: use os valores do README. Valor novo exige
  atualizar o `docs/licoes/README.md` e o `AREAS_VALIDAS` ou o `TIPOS_VALIDOS` da régua
  (`${CLAUDE_SKILL_DIR}/../../regua.py`) no mesmo commit. No Golem central, a régua é do kit: o
  valor novo vira um pedido ao kit.

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
  - **O gatilho casa com a ação, não com a ferramenta:** com a ação em que o erro acontece, e não
    com a ferramenta que o revelou. `\bgit\s+push\b`, não `git`. Antes de gravar, pense em três
    ações comuns que **não** deveriam receber a lição e confira que nenhuma casa.
  - O detalhe está em `docs/licoes/README.md`, "`gatilhos:` — em que ação a lição chega".

E nenhum dos dois é um dos **quatro motivos** (o que justifica escrever a lição, acima): os motivos
decidem **se** a lição existe; o `gatilho:` conta **onde** ela nasceu; os `gatilhos:` decidem
**quando** ela chega.

## 3. Propagar, se for o caso

- **Implica ação obrigatória daqui para frente?** Escreva a regra, curta e imperativa,
  **citando** a lição. A regra manda; a lição explica. Ela vai a um de dois lugares:
  - **vale para toda tarefa** → o `AGENTS.md`, que entra inteiro em toda conversa;
  - **só muda a decisão de quem mexe numa área** → o `docs/regras-de-area.md`. O gancho o
    entrega regra a regra: cada uma inteira, sem a introdução do arquivo, uma vez por sessão, a
    quem toca uma das áreas dela. **Cada regra se basta:** o que a introdução disser não chega com
    ela (lição `a-regra-de-area-chega-sem-a-introducao-do-arquivo`). O formato é o que o gancho
    lê: um título `## Regra N — Título`, com travessão (—), e a linha `areas:` logo abaixo, com
    áreas do README:

    ```markdown
    ## Regra 3 — Título curto do que fazer
    areas: codigo

    O que fazer e por quê, citando a lição (`docs/licoes/<id>.md`).
    ```

    Se o arquivo não existe, crie-o com um título e uma linha que diga, a quem o abre, o que ele é
    ("as regras que só valem para quem mexe numa área; o gancho entrega cada uma a quem a toca").
    Essa linha não chega a quem age. O número é o próximo livre. A régua confere o formato no
    `--gerar` e no `--conferir`.

  O `AGENTS.md` tem teto de palavras (`agents_teto`, no `golem.toml`), e a régua avisa quando ele
  passa.
- **Contradiz uma spec ou um ADR?** Diga ao usuário. Não corrija spec fechada por conta própria.
- **É preferência do usuário ou estado do projeto?** Não é lição: vai para a memória do agente.

## 4. Regerar o índice: sem isto o gancho avisa em toda sessão

**Primeiro o `git add` da lição, depois o `--gerar`.** Se o índice só vê o que o git rastreia, sem o
`git add` a lição fica de fora sem erro nenhum.

```bash
git add docs/licoes/<id>.md        # e o AGENTS.md ou o docs/regras-de-area.md, se o passo 3 mudou
python3 "${CLAUDE_SKILL_DIR}/../../regua.py" --gerar      # no Windows, python ou py -3
python3 "${CLAUDE_SKILL_DIR}/../../regua.py" --conferir
```

**Não é opcional.** O gancho, que entrega as lições a cada ação, lê `.claude/indice/licoes.yaml`
e confere, pelos nomes da pasta, se falta lição nele. A que falta chega lida do Markdown, mas com o
aviso "índice defasado" em toda sessão de todo agente, até o índice ser regerado com ela.

Se o comando recusar o arquivo (id fora de `[a-z0-9-]`, id diferente do nome do arquivo), o
problema está no frontmatter, não no comando.

**Sem Python nesta máquina** (nenhum Python 3.8+ que rode, conferido como na skill `diagnostico`):
pule o `--gerar` e o `--conferir` e diga ao usuário que pulou. A lição já vale para quem a busca
em `docs/licoes/`; o índice fica defasado até alguém rodar a régua numa máquina com Python, e esse
alguém faz o commit do índice (a skill `diagnostico` confere o índice quando acha o Python).

## 5. Provar que a lição chega

O índice em dia não prova que o gancho entrega a lição na ação certa. Rode o gancho com a ação
que **deve** recebê-la (o caminho ou o comando que o `gatilhos:` descreve, ou um da área) e
procure o id na saída:

```bash
echo '{"tool_input":{"file_path":"<caminho da ação>"}}' | sh "${CLAUDE_SKILL_DIR}/../../hooks/gancho.sh" | grep -o '\*\*<id>\*\*'
echo '{"tool_input":{"command":"<comando da ação>"}}' | sh "${CLAUDE_SKILL_DIR}/../../hooks/gancho.sh" | grep -o '\*\*<id>\*\*'
```

- O id tem de sair. Se não sair, o gatilho não alcança a ação em que o erro acontece: corrija os
  `gatilhos:` (ou a `area`), regere o índice e rode de novo. Se a saída traz outras lições e não
  esta, pode ser o teto de lições por ação (`gancho_teto`, no `${CLAUDE_SKILL_DIR}/../../../docs/guia-configuracao.md`): a que
  casa por `gatilhos:` vem antes das que vêm só pela área.
- Com `gatilhos:`, rode também as três ações comuns que **não** devem receber a lição (o passo
  2): nenhuma deve trazer o id. Sem eles, a lição chega em toda ação da área, por desenho.
- Sem Python, ou com o gancho desligado, pule este passo e diga ao usuário que pulou.

**Com os papéis** (o bloco "Como o Golem trabalha aqui" do `AGENTS.md` diz "Conversas: os papéis
de `docs/operacao-das-conversas.md`"), avise a conversa de método (MET) numa linha: o id da
lição, o commit ou o PR, e a regra que mudou junto ou "nenhuma regra mudou".
A MET confere a saúde do acervo (duplicatas, gatilhos, a regra que a lição pede). Sem MET aberta,
o aviso vai à conversa gerente. A própria MET, quando registra, não se avisa.

## 6. Fechar

Commit em português, com a lição no corpo da mensagem **e o `licoes.yaml` regerado junto**: os dois
no mesmo commit, senão o índice chega defasado na `main`. A regra do passo 3 (no `AGENTS.md` ou no
`docs/regras-de-area.md`) vai no mesmo commit. Sem Python, o commit leva só a lição, e a
mensagem diz que o índice ficou para depois. Se a lição nasceu de uma correção do
usuário, **cite a frase dele**: é o que torna o registro verificável depois.

## Restrições

- Nada de segredo, token, identificador interno, endereço de e-mail, hostname de cliente ou
  conteúdo de documento de cliente.
- Nunca registre como lição algo que você não verificou. Suspeita não confirmada vira pendência no
  roadmap, não lição.
- Não reescreva lição antiga para parecer que já se sabia. O acervo vale pelo registro honesto do
  erro.
