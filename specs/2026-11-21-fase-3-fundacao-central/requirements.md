# Fase 3: a fundação do Golem central — Requisitos

Branch `fase-3-fundacao-central`, cortada de `e1483ac` (a `main` em 2026-11-21, com os PRs 10 e
11 do roteiro, conferida com `git fetch` e `git log -1 origin/main`). Os fatos do kit foram lidos
em `e1483ac`, salvo onde se diz outro commit. As provas dos testes do plugin estão fora do
repositório, na pasta de notas da GER (`side-session-notes/local_20f8e1e8-…/fase-3-provas/`), e
cada uma é citada pelo nome.

## Objetivo

O kit passa a ser instalado **uma vez**, como plugin do Claude Code, e a ser ligado **só nos
jogos** (seção 8, decisão 11). Um jogo registrado ganha as skills e os agentes `golem:*` e o
gancho das lições; um projeto fora do registro não ganha nada. A configuração passa a ter dois
níveis: a do central, feita uma vez, e a do jogo, que vale por cima, linha a linha.

**O "pronto" do roteiro** (`docs/plano-produto.md:614`): "num jogo registrado, as skills e os
agentes `golem:*` aparecem e o gancho entrega a lição; num projeto fora do registro, nenhum
aparece".

**Por quê.** Hoje o kit se copia para dentro de cada projeto (`README.md:90-173`). Cada jogo
começa sem a configuração dos outros, atualizar o kit é copiar de novo em cada um, e a instalação
leva o que é só do kit: a `.claude/tests/` e o `docs/plano-produto.md` (`README.md:94-98`; o
segundo é o achado da GER).

## O que já se provou, antes da spec

Numa configuração isolada (`CLAUDE_CONFIG_DIR` numa pasta descartável; o `~/.claude` do usuário
não foi tocado), com o `claude.exe` 2.1.330, pelo evento de abertura da sessão (`system`/`init`
do `stream-json`), que sai antes do login. O plugin foi uma cópia do kit em `e1483ac`
(`git archive`, sem `.git`), com os três JSON abaixo; o G2 refaz a prova no repositório (S1 a S4
do `validation.md`).

| # | O que | Resultado | Prova |
|---|---|---|---|
| P1 | O próprio repositório do kit serve de plugin e de marketplace: um `.claude-plugin/plugin.json` que aponta `skills`, `agents` e `hooks` para dentro de `.claude/`, e um `.claude-plugin/marketplace.json` com `"source": "./"` | o `claude plugin validate` passa com avisos (sem `author`, sem descrição do marketplace e o `CLAUDE.md` da raiz, que não é lido); a sessão lista 14 skills `golem:*` e os agentes `golem:revisor` e `golem:validador` (2 rodadas) | `plugin.json`, `marketplace.json`, `hooks.json`, `validate-mkt.txt`, `p-json-r1.jsonl`, `p-json-r2.jsonl` |
| P2 | `"defaultEnabled": false` no `plugin.json` | o `claude plugin install … --scope user`, sem nenhum passo de desligar, diz "This plugin is disabled by default" e grava `false` no usuário (1 instalação); o projeto sem linha fica sem o plugin (1 rodada) | `plugin-mkt2-defaultEnabled.json`, `install-defaultEnabled.txt`, `d-nada.jsonl` |
| P3 | O "ligado" no `.claude/settings.local.json` do projeto | o plugin aparece, como com o `.claude/settings.json` (2 rodadas com o `false` no usuário, `cfg-settings.json`; 1 com o `defaultEnabled`) | `p-local-r1.jsonl`, `p-local-r2.jsonl`, `d-local2.jsonl` |
| P4 | O "ligado" no `.claude/settings.json` do projeto | o plugin aparece | `p-json-r1.jsonl`, `p-json-r2.jsonl` |
| P5 | Um projeto sem linha nenhuma | nem o plugin, nem as skills, nem os agentes | `p-nada-r1.jsonl`, `p-nada-r2.jsonl` |
| P6 | De onde o plugin roda | da pasta do kit, e não de uma cópia: o `path` do plugin no `init` é a pasta do marketplace | `p-local-r1.jsonl` |

**Da documentação** (lida hoje por um subagente; trechos literais, em `code.claude.com/docs/en/`):
- o plugin de um marketplace local, com `source` relativo, "loads in place from its path inside
  the marketplace folder", e o `CLAUDE_PLUGIN_ROOT` "points at the source directory"
  (`plugins/loading.md`). Edição no kit vale na sessão seguinte, sem `update`;
- o `${CLAUDE_SKILL_DIR}` é "The directory containing the skill's `SKILL.md` file. For plugin
  skills, this is the skill's subdirectory within the plugin" (`skills.md`, a página geral das
  skills, e não a dos plugins: a leitura é que vale também nas de projeto; a conferir no L3). O
  `${CLAUDE_PLUGIN_ROOT}` é "Substituted only in plugin skills" (`skills.md`), e
  as variáveis do plugin "aren't present in the environment of commands Claude runs through the
  Bash tool" (`plugins/manifest-reference.md`);
- no `plugin.json`, o campo `agents` "Replaces the default `agents/` scan", e o `skills` "Adds to
  the default `skills/` scan" (`plugins/manifest-reference.md`). O kit não tem `agents/` nem
  `skills/` na raiz;
- o agente de plugin aceita `model` e `tools`, e ignora `hooks`, `mcpServers` e `permissionMode`
  (`plugins/components.md`);
- a precedência do `enabledPlugins` é "`--add-dir`, `user`, `project`, `local`, `flag`, `managed`"
  (`plugins/loading.md`). O `settings.local.json` é "per-machine overrides, gitignored when Claude
  Code saves a setting there" (`settings-reference.md`): quando quem grava é o kit, o `.gitignore`
  é por conta dele (R3);
- o plugin ligado no projeto e não instalado na máquina não carrega, e "the `/plugin` **Errors**
  tab shows a line ending in `isn't installed here`" (`plugins/loading.md`);
- o `CLAUDE.md` da raiz do plugin não é lido ("Claude Code doesn't load a `CLAUDE.md` at the
  plugin root", `plugins/components.md`);
- o `CLAUDE.md` sobe além do git: "Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from your
  current working directory and every directory above it" (`memory.md`), e a página não fala em
  parar no repositório;
- "A project-scope plugin [...] loads only after the same trust check that applies to project
  allow rules in `.claude/settings.json`. Trusting a parent folder or running with `-p` isn't
  enough." (`plugins/loading.md`). Sobre uma pergunta a mais ao abrir o jogo, a página não diz.

## Escopo

### R1. O esqueleto do plugin

- **`.claude-plugin/plugin.json`**, na raiz do kit: `name` `golem`, `version`, `description`,
  `author` (o autor do kit, o nome do crédito), `license` `MIT`, `homepage` (a URL do crédito),
  `"defaultEnabled": false` (P2), `"skills": "./.claude/skills/"`, `"agents"` com os dois arquivos
  de `.claude/agents/` e `"hooks": "./.claude/hooks/hooks.json"`. O formato é o do P1.
- **`.claude-plugin/marketplace.json`**: o marketplace `golem`, com o plugin `golem` em
  `"source": "./"` (P1). O id do plugin fica `golem@golem`.
- **`.claude/hooks/hooks.json`**: o mesmo gancho do `.claude/settings.json` (os três `matcher`,
  o `timeout`, a `statusMessage` e o `|| printf` de queda), com o lançador em
  `${CLAUDE_PLUGIN_ROOT}/.claude/hooks/gancho.sh` no lugar de `${CLAUDE_PROJECT_DIR:-…}`. Um teste
  confere que os dois arquivos têm os mesmos `matcher` e a mesma queda, para não divergirem.
- **Quem mexe no kit** não instala o plugin para desenvolvê-lo: o repositório do kit continua com
  o `.claude/settings.json` e as skills de projeto, como hoje.

### R2. A raiz do projeto, o modo plugin e o central

Hoje, cinco peças acham a raiz pela própria posição: `gancho.sh:37-38`,
`licoes_relevantes.py:60`, `golem.py:30`, `regua.py:40` e `instalar_codex.py:29`. No plugin, a
posição é a pasta do kit. O `instalar_codex.py` fica como está: ele só roda na instalação por
cópia, em que a posição é o projeto.

- **Duas raízes, separadas.** Hoje a mesma `RAIZ` serve para achar os scripts irmãos (o
  `licoes_relevantes.py:74` carrega o `golem.py`; a `regua.py:43` e `:129`, o gancho) e para achar
  os dados do projeto (as lições, o índice, o `golem.toml`). Nesta fase, **os scripts do kit se
  carregam sempre pela posição**, e só os dados vêm da raiz do projeto. Nada do kit se copia ao
  jogo para "consertar" um caminho.
- **A raiz do projeto:**
  - no gancho, o `CLAUDE_PROJECT_DIR`, quando existe e é uma pasta (é o que o harness passa ao
    gancho); sem ele, a mesma regra do `golem.py` (abaixo): a posição, salvo quando a posição é o
    plugin, e aí o git da pasta corrente; e o git quando o `.py` não está ao lado, como hoje
    (`gancho.sh:42-48`). O caso sem a variável é o do gancho rodado à mão pelas skills, pelo Bash
    (a `licao`, "Provar que a lição chega", `licao/SKILL.md:135-136`; o `diagnostico`, passo 7,
    `diagnostico/SKILL.md:133`): sem essa regra, ele leria as lições e a configuração do kit. O
    `gancho.sh` passa a raiz ao `licoes_relevantes.py` no próprio `CLAUDE_PROJECT_DIR`, e o `.py`
    a lê dali; sem a variável, a posição, como hoje;
  - no `golem.py` e na `regua.py`, que as skills rodam pelo Bash (sem as variáveis do plugin): a
    posição, como hoje, **salvo quando a posição é o plugin** (a pasta dela tem
    `.claude-plugin/plugin.json`). Aí a raiz é a do git da pasta corrente (ou a pasta corrente,
    fora do git). No kit, as duas dão a mesma pasta. Os testes que carregam os módulos de uma
    cópia sem `.claude-plugin/` continuam como hoje.
- **O modo plugin** é a raiz do projeto ser outra que a pasta do kit. Só nele vale o central. No
  repositório do kit e na instalação por cópia (a do Codex), nada muda.
- **O central** é a pasta `~/Golem` (no Windows, `C:\Users\<você>\Golem`), o padrão do estudo
  aprovado na decisão 11. Uma regra só, igual no `sh` e no Python: a variável `GOLEM_CENTRAL`,
  senão `$HOME/Golem`, senão (só no Python, sem `HOME`) o `Path.home()`. O `Path.home()` do Python
  no Windows usa o `USERPROFILE`, e o `sh` usa o `HOME`: com a mesma regra, os dois acham a mesma
  pasta, e um teste confere com um `HOME` diferente do `USERPROFILE`. A `GOLEM_CENTRAL` serve à
  suíte, para não ler o central da máquina de quem roda os testes.
- **A configuração em dois níveis** (o `golem.py` e o `gancho.sh`): no modo plugin, o
  `~/Golem/golem.toml` vale por baixo do `golem.toml` do jogo, linha a linha. Por chave: a linha
  do jogo, senão a do central, senão a da receita; a receita é a do jogo, senão a do central,
  senão a `economico`. O formato e as chaves são os de hoje (`golem.py:11-13`, `:37-49`). É aí que
  a fase 5 grava a preferência dos emojis (decisão 12).
- **O Python em um lugar só:** no modo plugin, o `gancho.sh` procura também a linha `python` do
  `~/Golem/golem.local.toml`, depois da do jogo e da pasta principal (`gancho.sh:205-206`); a
  skill `diagnostico` passa a gravar ali, e a `configurar`, que hoje procura a linha só no projeto
  e na pasta principal (`configurar/SKILL.md:92-103`), passa a ler também a do central.

### R3. O registro dos jogos e o "ligado"

Novos comandos do `golem.py` (a skill chama; quem não tem Python faz à mão, pelos passos da skill):

- **`central`**: cria o `~/Golem`, se não existir, com:
  - o `golem.toml`, só com um comentário que diz o que ele é;
  - o registro, o `jogos.md`;
  - a pasta `jogos/`;
  - o "ligado" do próprio central (cartão 2), no `.claude/settings.local.json` (cartão 1).

  Nunca escreve um `CLAUDE.md` no central: ele subiria para todo jogo de `jogos/` (a
  documentação, acima). Rodado de novo, não muda nada.
- **`registrar <pasta> [--nome <nome>]`**: põe o jogo no `jogos.md` (o nome, a pasta e a data) e
  escreve o "ligado" no jogo. O "ligado" é a chave `enabledPlugins` com `"golem@golem": true`, no
  `.claude/settings.local.json` (cartão 1), juntada ao que o arquivo já tiver. Ele também
  põe a linha `.claude/settings.local.json` no `.gitignore` do jogo, se faltar: quem grava o
  arquivo é o kit, e não o Claude Code, e sem a linha o "ligado" iria ao git de um repositório que
  já existe (o de um cliente, por exemplo). Sem o central, cria antes. Rodado de novo para a mesma
  pasta, não duplica.
- **`aplicar --todos`**: roda o `aplicar` em cada jogo do registro. É o que a `configurar` usa
  quando muda a configuração do central, porque o bloco "Como o Golem trabalha aqui" mora no
  `AGENTS.md` de cada jogo. Um jogo cuja pasta sumiu sai com um aviso, e os outros seguem.
- **`onde`**: diz em poucas linhas a raiz do projeto, o modo (plugin ou cópia), o central e de
  onde vem cada linha da configuração (do central ou do jogo). Quem o usa nesta fase: a
  `configurar` e o `diagnostico`, para saber se estão no modo plugin e em que pasta gravar (o
  `golem.toml` e o `golem.local.toml` do central, ou os do projeto), sem repetir na skill a regra
  do central (R2). Não é o "onde está tudo?" (T1) da fase 7.
- **O `jogos.md`** é uma tabela em Markdown (Jogo, Pasta, Registrado em), legível pelo usuário e
  buscável. O nome não aceita `|` nem quebra de linha.

### R4. As skills, os agentes e o modelo do `AGENTS.md` no modo plugin

- **A `iniciar-sdd` prepara e registra um jogo** (cartão 2: ela roda no central). Ela pergunta o
  nome e "Você já tem uma pasta para este jogo?"; usa a dele ou cria `~/Golem/jogos/<nome>/`;
  oferece o `git init` quando falta; copia o que viaja (R5); roda o `registrar`, a régua e o
  `aplicar` no jogo; e diz para abrir uma sessão nova na pasta do jogo. O fluxo de hoje (num
  projeto com o kit copiado) fica como variante curta, para a instalação por cópia.
- **As skills acham os scripts e os modelos do kit pelo `${CLAUDE_SKILL_DIR}`**: por exemplo,
  `python3 "${CLAUDE_SKILL_DIR}/../../regua.py"` no lugar de `python3 .claude/regua.py`, e
  `${CLAUDE_SKILL_DIR}/../../../templates/…` para os modelos. Vale nas skills de plugin e nas de
  projeto (o kit). Os documentos que moram no jogo (`docs/licoes/`, `docs/operacao-das-conversas.md`,
  o índice) continuam pelo caminho do projeto. As skills que mudam: as que rodam a régua, o
  `golem.py` ou o gancho, ou leem um modelo ou um guia do kit. A busca é pelo arquivo, e não pelo
  jeito de chamar, porque há chamadas como `"$PY" .claude/golem.py aplicar`
  (`configurar/SKILL.md:125`), `sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"`
  (`diagnostico/SKILL.md:133`) e `"<o Python gravado>" .claude/regua.py`
  (`diagnostico/SKILL.md:147`); o comando está no `plan.md`, G4.
- **As cópias do Codex** trocam o `${CLAUDE_SKILL_DIR}/../../../` por
  `$(git rev-parse --show-toplevel)/` e o `${CLAUDE_SKILL_DIR}/../../` por
  `$(git rev-parse --show-toplevel)/.claude/`, no `instalar_codex.py`, porque o Codex não conhece
  a variável. O caminho a partir do git funciona também de uma subpasta, como o
  `diagnostico/SKILL.md:133` de hoje. O Codex continua na instalação por cópia (decisão 11).
- **A `configurar`**, no modo plugin, grava no central por padrão (configurar uma vez, decisão 11)
  e roda o `aplicar --todos`; grava no `golem.toml` do jogo só quando o usuário pede "só neste
  jogo". Fora do modo plugin, como hoje.
- **O modelo dos agentes vai na chamada.** No plugin, o `aplicar` não pode escrever o `model:`
  dos agentes, porque eles moram no kit, e não no jogo. A regra 11 e as skills que chamam o
  revisor e o validador passam a mandar passar na chamada o modelo que o bloco diz, e a chamar o
  agente pelo nome que a sessão lista (`golem:revisor` no plugin, `revisor` no kit e na cópia). Na
  instalação por cópia e no kit, o `aplicar` continua escrevendo o `model:`, como hoje
  (`golem.py:218-230`), e a chamada passa o mesmo valor.
  - **A conferir (L7, com login):** que o `model` da chamada vence o `model:` do frontmatter de
    um agente de plugin. A descrição da ferramenta de agentes do Claude Code diz que o `model`
    "Takes precedence over the agent definition's model frontmatter", mas nenhuma página do plugin
    foi lida sobre isso.
  - **O custo de esquecer:** os agentes do plugin são os do kit, com `model: opus`
    (`revisor.md:5`, `validador.md:5`, escritos pelo `aplicar` do kit na `completo`). Num jogo na
    `economico`, a chamada que omitir o modelo roda o revisor no Opus.
- **O bloco "Como o Golem trabalha aqui"**, no modo plugin, aponta o guia pelo pedido ("peça
  'configurar o Golem'") e não por `docs/guia-configuracao.md`, que não vai ao jogo; e o
  comentário gerado ("Gerado pelo `.claude/golem.py aplicar`", `golem.py:154`) passa a dizer
  "gerado pelo `aplicar` do Golem", sem o caminho.
- **O modelo do `AGENTS.md`** (`templates/AGENTS.md`) deixa de citar como caminho do projeto o
  que no plugin mora no kit: a régua, o `golem.py`, os agentes, as skills e o instalador do Codex
  (`templates/AGENTS.md:19-20`, `:67`, `:100-107`, `:152-153`, `:236-245`). O texto novo diz o que
  fazer (a skill, ou o comando do kit) nos dois modos. A mesma mudança vai ao `AGENTS.md` da raiz,
  e o conciliador confere (`.claude/tests/test_conciliar.py`).

### R5. A lista do que viaja e o mapa das pastas

| Onde mora | O quê |
|---|---|
| **No kit** (o plugin, uma pasta só na máquina) | as skills, os agentes, o gancho, a régua, o `golem.py`, o instalador do Codex, a `templates/` e os guias (`docs/guia-configuracao.md`, `docs/guia-roblox.md`) |
| **No central** (`~/Golem`) | o `golem.toml` (a configuração de todos os jogos), o `golem.local.toml` (o Python desta máquina), o `jogos.md` (o registro), a pasta `jogos/` e o "ligado" do próprio central |
| **No jogo** (a `iniciar-sdd` copia ou cria) | o `AGENTS.md` (do `templates/AGENTS.md`), o `CLAUDE.md` (`@AGENTS.md`), o `WORKFLOW.md`, o `docs/operacao-das-conversas.md`, o `docs/licoes/` (o `README.md` e as lições de exemplo, como hoje: a escolha é da fase 7, decisão 6), o `docs/adr/modelo.md`, a `specs/` (vazia até a constituição), o índice gerado, o `CHANGELOG.md`, o modelo de PR, o `.claude/LICENSE` do kit (o `AGENTS.md` e as lições de exemplo são do kit, e a MIT pede o aviso junto; decisão 1), o `.gitignore` com as linhas do kit, o "ligado" e, se o jogo quiser, um `golem.toml` próprio |
| **Só no kit, nunca vai** | a `.claude/tests/`, a `specs/` do kit, o `docs/plano-produto.md`, o `AGENTS.md` e o `golem.toml` da raiz |

- **O `README.md`** troca a seção "Instalar num projeto" (`:90-173`) por duas: "Instalar o Golem
  (uma vez)" (pôr o kit numa pasta, `claude plugin marketplace add <pasta>`,
  `claude plugin install golem@golem --scope user` e o `golem.py central`) e "Registrar um jogo"
  (cartão 2). A instalação por cópia vai para "Usando com o Codex" (`:175`), com a lista corrigida:
  sem a `.claude/tests/` e, da `docs/`, sem o `plano-produto.md`.
- **Onde pôr o kit:** numa pasta própria, fora do `~/Golem` e de qualquer pasta acima dele (por
  exemplo `~/golem-kit`). O plugin carrega no lugar (a documentação, acima), então um jogo usa o
  que estiver naquela pasta, e o `CLAUDE.md` do kit, se ficasse acima de um jogo, subiria para ele.
  Pelo mesmo motivo, **quem desenvolve o kit** não aponta o marketplace para a pasta em que trabalha
  numa branch: usa um clone na `main`, ou a branch quebrada chega a todos os jogos.
- **O "Mapa das pastas"** (`README.md:259-284`) ganha a coluna "onde mora", com as quatro linhas
  da tabela acima.
- **Os documentos que viajam ao jogo** deixam de citar como do jogo o que mora no kit:
  `docs/licoes/README.md:88-90`, `:108` e `:115` (a régua), `WORKFLOW.md:116` e `:181` (os agentes e
  as skills), e a seção "Licença e crédito" do `README.md` (`:312`, `:319`), que hoje diz que o
  `.claude/LICENSE` viaja na `.claude/` copiada.
- **Quem muda, varre:** os documentos e os agentes que citam a instalação por cópia como a única,
  ou um arquivo do kit como se morasse no jogo (as buscas estão no `plan.md`, G5).

### R6. Os itens a conferir da decisão 11

| Item | Como se fecha nesta fase |
|---|---|
| O arquivo do "ligado" | provado sem login (P3, P4); escolhido o `settings.local.json` (cartão 1) |
| O `CLAUDE_PLUGIN_ROOT` | aponta para a pasta do kit (a documentação e o P6). Nada do central nem do jogo mora nele (o log do gancho fica na `.claude/` do jogo, `gancho.sh:85-86`). A rodada com login confere o gancho rodando (validation.md) |
| A subida do `CLAUDE.md` | a documentação diz que sobe além do git. Por isso o central nunca tem `CLAUDE.md` (R3), e um teste confere. Uma rodada com login confere o caso dos jogos em `~/Golem/jogos/` |
| O gancho fora do Golem | a rodada com login, num projeto sem o "ligado": nenhuma linha do gancho do plugin na transcrição |
| O modo interativo (o diálogo de confiança) | a rodada com login, interativa: a primeira abertura de um jogo pede a confiança na pasta, e depois dela o plugin liga. A documentação diz que o plugin de projeto espera essa confiança |
| A `iniciar-sdd` de ponta a ponta e o que chega ao jogo | a rodada com login, no central (L6) |
| O modelo na chamada | a rodada com login (L7) |

As rodadas com login pedem que o autor do kit entre na configuração isolada (validation.md, "Com
login").

## Fora de escopo

- **O acabamento da instalação (fase 7):** o `/golem:comecar`, o `diagnostico` completo, o guia
  do primeiro dia, o "onde está tudo?" inteiro (T1), a escolha das lições que o kit entrega
  (decisão 6) e a release com zip (decisão 12).
- **Os dois acervos de lições** (o geral no central e o do jogo) e a raiz do gancho para eles: fase
  4. Nesta fase, o gancho lê só as lições do jogo.
- **O estilo em dois níveis:** fase 6.
- **A preferência dos emojis:** fase 5. A fase 3 só cria o lugar (o `~/Golem/golem.toml`).
- **O Codex como plugin:** fica na instalação por cópia (decisão 11) e na fase 9.
- **Marcar o cliente no registro** (`cliente = …` do estudo, pergunta 3): sem uso antes dos dois
  acervos (fase 4).
- **O jogo aberto numa subpasta** (a sessão aberta em `jogo/src/`): o "ligado" e o gancho usam a
  pasta em que a sessão abriu. Fica como limite conhecido, sem falha vista.
- **Migrar uma instalação por cópia para o plugin.** Não há usuário com a cópia além do autor do
  kit; o "atualizar sem perder nada" é da fase 9.
- **O roteiro (seção 7)**: a `validar-fase` marca a fase; o resto é da GER.

## Decisões

**Do autor do kit, pela EST (os cartões com o texto original da fase):**
- **Cartão 1, "Em que arquivo do jogo o kit escreve o 'ligado'?":** `.claude/settings.local.json`
  (fora do git, por máquina, como o registro; nada vai ao git de um cliente) ×
  `.claude/settings.json` (vai ao git; quem clona com o plugin o vê ligado; quem não tem o plugin
  vê "isn't installed here" na aba Errors do `/plugin`, pela documentação). As palavras dele: "A:
  settings.local.json (Recomendado)" (2026-11-21). Descartado: o `settings.json`.
- **Cartão 2, "Onde o iniciante registra o primeiro jogo?":** na pasta do central, que nasce com o
  plugin ligado (a fase 7 reusa o lugar para o `comecar`) × só um comando no terminal. As palavras
  dele: "A: na pasta do Golem (Recomendado)" (2026-11-21). Descartado: só o comando no terminal
  (ele continua existindo por baixo, o `registrar`).
- **Uma nota da EST, fora desta fase:** o `AGENTS.md` e a `specs/` do jogo continuam indo ao git
  dele; num repositório de cliente, isso é uma pergunta maior, anotada na EST para depois.

**A aprovação da spec:** à pergunta "Aprova a spec da fase 3, com um commit por grupo na branch?", "Aprovo" (o autor do kit, 2026-11-22).

**Já tomadas e que esta fase aplica:** a decisão 11 (o central, desligado no usuário e ligado só
nos jogos, o registro, o `CLAUDE_PROJECT_DIR`, o jogo sem Rojo numa subpasta do central ou na pasta
dele); a 12 (os emojis na configuração do central); e a 9 com o "Ficam para depois (Recomendado)"
(as três partes adiadas da separação vêm para cá).

**Do agente, dentro destas:**
- o repositório do kit é o plugin e o marketplace (P1), sem cópia das skills numa pasta `plugin/`:
  uma fonte só, que o kit também usa para se desenvolver;
- o `"defaultEnabled": false` no manifesto, no lugar de um passo "desligar" (P2);
- o central em `~/Golem`, o padrão do estudo, com a `GOLEM_CENTRAL` para os testes;
- o registro em Markdown (`jogos.md`), e não em TOML: o leitor do `golem.toml` não lê tabelas
  (`golem.py:11-13`), e o estudo deixou a escolha para a spec. Descartado: estender o leitor;
- o modo plugin decidido por "a raiz é outra que a pasta do kit", e não pelo registro: o gancho
  não lê o registro a cada ação, e o kit e a instalação por cópia não mudam. O registro só é lido
  pelo `aplicar --todos` e pelo `onde`;
- o gancho não confere o registro: fora dos jogos, o plugin nem entra na sessão (P5). A rodada
  com login confere que o gancho não roda ali (R6);
- os scripts pelo `${CLAUDE_SKILL_DIR}`, e não pelo `${CLAUDE_PLUGIN_ROOT}`, que fica literal nas
  skills de projeto do kit;
- o modelo na chamada, e não um `aplicar` que escreva no kit, que é de todos os jogos.

## Contexto

- **A suíte em `e1483ac`:** `134 passed in 56.62s`, sem pulados, com o comando dos "Comandos
  reais", rodado nesta conversa.
- **O conciliador** compara o `templates/AGENTS.md` com o `AGENTS.md` da raiz fora do bloco
  gerado, com a lista `PERMITIDAS` (`.claude/tests/test_conciliar.py`). A mudança do R4 vai igual
  aos dois.
- **O kit também vira "plugin" para a régua e o `golem.py`.** Depois do G2, a raiz do kit tem
  `.claude-plugin/plugin.json`, e os dois, rodados da pasta do kit com a pasta corrente fora dela,
  passam a pegar a raiz pela pasta corrente (R2). No kit, os comandos rodam da raiz (os "Comandos
  reais"), e a suíte também: a fixture `regua` carrega a régua do kit (`conftest.py:75`) e, com o
  pytest rodado da raiz, a pasta corrente é o kit. Os testes do G1 rodam também com a pasta
  corrente noutro lugar, para o caso ficar visível.
- **O crédito é uma lista fechada** (`test_credito.py:22-40`). O JSON não aceita comentário: o
  `plugin.json` leva o crédito nos campos `author`, `license` e `homepage`, e os três JSON novos
  ficam fora da lista (um teste confere os campos do `plugin.json`).
- **Os testes que rodam o gancho e os scripts** usam o `AMBIENTE` (`conftest.py:32`), que herda o
  ambiente. Ele passa a tirar o `CLAUDE_PROJECT_DIR` e a apontar o `GOLEM_CENTRAL` para uma pasta
  vazia, para a suíte não ler a sessão nem o central de quem a roda.
- **O `.gitignore` do kit** já tem o `.claude/settings.local.json` (`.gitignore:5`).
- **O teste interativo** não se faz pelo `-p`: a documentação diz que o `-p` não basta para a
  confiança do plugin de projeto, embora o `-p` tenha listado o plugin nas provas P3 e P4.

## Padrões a seguir

- **Os comandos novos do `golem.py`** seguem o `aplicar`: dizem o que escreveram, uma linha por
  arquivo, e "nada mudou" na segunda rodada (`golem.py:241-262`).
- **O JSON juntado** (o "ligado" num `settings.local.json` que já existe) segue o `com_bloco`:
  troca só a parte do kit e guarda o resto (`golem.py:185-195`).
- **A leitura em `sh`** da linha `gancho` no central segue a de hoje (`gancho.sh:55-75`).
- **Os testes do central** seguem o `copia_do_kit` (`conftest.py:148-159`): uma árvore
  descartável, sem tocar o `~/Golem` de verdade.

## Notas do usuário

- "é configurado uma só vez, é fácil de usar, guarda as lições, guarda o estilo do usuário [...] a
  gente só teria que ter um documento, que seria um banco de dados, né, dos projetos que ele tem"
  (o autor do kit, 2026-11-21, decisão 11).
- "Eu acho bom a gente pensar que o usuário ele pode já ter pastas assim no PC. É bom combinar com
  ele, mas eu gosto da sua recomendação." (o autor do kit, 2026-11-21, sobre a subpasta do
  central; registro da EST).

## Perguntas em aberto

- **O login na configuração isolada**, para as rodadas do R6: o autor do kit entra uma vez
  (`/login` numa janela com o `CLAUDE_CONFIG_DIR` isolado) e sai no fim. Sem isso, as rodadas
  ficam com ele, na configuração dele. Pergunta-se na hora do G6.
