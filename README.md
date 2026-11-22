# Golem · kit de SDD para o Claude Code e o Codex

> *A spec-driven development kit for coding agents (Claude Code and Codex): specs before code,
> independent reviewer and validator agents, lessons that come back at the right moment, and
> conversations with clear roles. The kit is written in Brazilian Portuguese.*

O nome vem do golem do folclore, o ser de barro que só se move pelo que está escrito no pergaminho
que lhe dão. Aqui, o pergaminho é a spec: o agente age pelo que foi escrito e aprovado antes.

Um jeito de trabalhar com um agente de código (Claude Code ou Codex) em que **a especificação vem
antes do código**, e em que várias conversas do agente dividem o trabalho com papéis claros. O kit é
o que sobrou de um projeto real depois de alguns meses de uso: as regras, as skills, os agentes e os
modelos de documento que pagaram o próprio custo.

## Para quem nunca viu

**SDD** (*spec-driven development*, desenvolvimento guiado por especificação) é uma ideia simples:
antes de pedir código ao agente, você escreve com ele **o que** vai ser feito, **como** vai ser
feito e **como se prova** que ficou pronto. Só então ele implementa.

Por que isso importa com agentes:

- **O agente esquece.** Cada conversa começa do zero. O que está escrito em arquivo sobrevive; o
  que ficou só na conversa, não.
- **O agente é confiante.** Ele diz "pronto" com a mesma segurança quando está certo e quando está
  errado. Um critério de validação escrito antes, como comando, separa as duas coisas.
- **O agente faz mais do que o pedido.** Uma spec com "fora de escopo" e uma regra de simplicidade
  seguram o código no tamanho do problema.
- **Os erros se repetem.** Uma armadilha descoberta numa semana volta na outra, em outra conversa.
  O kit registra cada uma como **lição** e a entrega ao agente na hora em que ele está prestes a
  cair nela de novo.

## O fluxo

```
   constituição  ──  specs/mission.md, tech-stack.md, roadmap.md   (uma vez; revista quando muda)
        │
        ▼
 ┌─► spec da fase  ──  specs/AAAA-MM-DD-nome/ requirements, plan, validation
 │      │                  (o usuário aprova antes de qualquer código)
 │      ▼
 │   implementar por grupos  ──►  revisor e validador, conforme a receita
 │      │                          (por grupo ou por fase; só leem)
 │      ▼
 │   validar a fase  ──  cada item do validation.md com a saída real  ──►  (guardião)  ──►  merge
 │      │
 └── replanejar o roadmap  ◄──┘

 em volta de tudo:
   lições       docs/licoes/   armadilha registrada, entregue pelo gancho na hora certa
   conversas    gerente · estratégia · método · guardião · frentes (uma por entrega)
```

Cada etapa, com o que entra, o que sai, a skill que a dispara e o ponto em que você decide, está
em [`WORKFLOW.md`](WORKFLOW.md). Como as conversas se dividem está em
[`docs/operacao-das-conversas.md`](docs/operacao-das-conversas.md).

## Glossário curto

| Termo | O que é |
|---|---|
| **lição** | um arquivo em `docs/licoes/` que registra uma armadilha: o que se achava, o que é, e o sinal para perceber da próxima vez |
| **gancho** | um *hook* do agente (Claude Code ou Codex): um comando que o próprio agente roda antes de cada ação dele. O do kit (`.claude/hooks/`) põe no contexto as lições que importam para aquela ação |
| **worktree** | uma segunda pasta de trabalho do mesmo repositório git (`git worktree add`), com a própria branch. Cada conversa trabalha na sua, para duas não escreverem no mesmo lugar |
| **frente** | uma conversa dedicada a uma entrega (uma fase, uma correção), do começo ao merge |
| **fecho** | as quatro linhas com que toda mensagem de fim de turno termina: Resumo, O que você faz agora, Worktree, Espera |
| **cartão de decisão** | o jeito de pedir uma decisão ao usuário: o problema, as opções com a consequência, a recomendada primeiro e o tamanho |
| **PEDIDO / LIBERADO** | o par de mensagens com que uma frente pede à gerente a vez de fazer algo compartilhado (o merge, um recurso) e a gerente libera, depois de conferir |

O detalhe de cada um está em `docs/operacao-das-conversas.md`.

## Requisitos

- **Python 3.8 ou mais novo.** Só a biblioteca padrão: o kit não instala nada. O gancho procura,
  nesta ordem: a linha `python = '<caminho>'` do `golem.local.toml` (fora do git, gravada pela
  skill `diagnostico`; no Golem central, também o do central), o `.venv` da raiz e o da pasta
  principal, `python3`, `python` e `py -3` no PATH e, no Windows, os lugares do instalador oficial
  (`%LOCALAPPDATA%\Programs\Python` e `%PROGRAMFILES%`). Se o aviso disser que não achou, peça o
  diagnóstico do Golem.
- **`sh`**, para o gancho. No Linux e no macOS ele já existe; no Windows, vem com o
  [Git for Windows](https://gitforwindows.org/).
- **git**.
- **O Claude Code com plugins** (o `/plugin`, ou o `claude plugin` no terminal), para o Golem
  central. O Codex usa a cópia (em "Usando com o Codex").
- **`gh`** (o [GitHub CLI](https://cli.github.com/)), só para as skills que abrem e mergeiam PR.
- **pytest**, só se quiser rodar os testes do ferramental (`.claude/tests`, na pasta do kit).

Nos comandos abaixo, `python3` é o Python. **No Windows, rode os comandos no Git Bash** (o terminal
que vem com o Git for Windows: `echo … | sh …`, `tail` e as aspas simples não funcionam no
PowerShell nem no `cmd`), **e use `python` ou `py -3`** no lugar de `python3` (o `python3` do
Windows costuma ser um atalho da loja que não roda nada).

## Instalar o Golem (uma vez)

O Golem é instalado **uma vez** na máquina, como plugin do Claude Code, e liga **só nos jogos** que
você registra. Os seus outros projetos não mudam. A configuração também se faz uma vez, na pasta do
**Golem central** (`~/Golem`; no Windows, `C:\Users\<você>\Golem`), e vale em todos os jogos.

1. **Ponha o kit numa pasta própria**, fora do `~/Golem` e nunca numa pasta que o contenha, por
   exemplo:

   ```bash
   git clone https://github.com/RodrigoAnciaes/golem-sdd ~/golem-kit
   ```

   O plugin roda dessa pasta, sem cópia: atualizar o kit é atualizar a pasta (`git pull`), e vale na
   sessão seguinte. Quem desenvolve o kit aponta aqui um clone na `main`, e não a pasta em que
   trabalha numa branch: senão, a branch pela metade chega a todos os jogos.

2. **Instale o plugin** (no terminal, ou dentro de uma sessão do Claude Code, com `/plugin`):

   ```bash
   claude plugin marketplace add ~/golem-kit
   claude plugin install golem@golem --scope user
   ```

   Na sessão, os mesmos passos são `/plugin marketplace add <a pasta do kit, por extenso>` e
   `/plugin install golem@golem` (a forma provada é a do terminal, acima). A instalação diz "This
   plugin is disabled by default": é o esperado. Ele só liga numa pasta que tenha o "ligado" do Golem, que o kit escreve ao registrar um
   jogo.

3. **Crie o Golem central:**

   ```bash
   python3 ~/golem-kit/.claude/golem.py central
   ```

   Ele cria o `~/Golem` com o `golem.toml` (a configuração de todos os jogos), o `jogos.md` (o
   registro dos jogos), a pasta `jogos/` e o "ligado" do próprio central. Rodado de novo, diz "nada
   mudou".

4. **Registre o primeiro jogo** (abaixo).

5. **Opcional: configure o Golem.** Sem configuração, vale a receita `economico`: um revisor por
   fase, e a implementação para a cada parte para o seu ok. Para mudar, abra o Claude Code no
   `~/Golem` (ou num jogo) e peça "configurar o Golem": a resposta vale para todos os jogos, salvo
   se você disser "só neste jogo". As receitas e o que cada uma custa estão em
   `docs/guia-configuracao.md`.

## Registrar um jogo

1. **Abra o Claude Code na pasta do Golem central** (`~/Golem`). Na primeira vez, ele pergunta se
   você confia na pasta: aceite, e só então o Golem liga ali.
2. **Peça "registrar um jogo"** (a skill `golem:iniciar-sdd`). Ela pergunta o nome do jogo e se você
   já tem uma pasta para ele; sem pasta, cria `~/Golem/jogos/<nome>/`. Depois prepara a pasta (um
   repositório git, com o `AGENTS.md`, as lições e os modelos), põe o jogo no registro, liga o Golem
   nele, gera o índice das lições e aplica a configuração do central ao `AGENTS.md` do jogo.
3. **Abra uma sessão nova do Claude Code na pasta do jogo** e confie na pasta quando ele perguntar.
   Ali, o próximo passo é "criar a constituição" (skill `golem:constituicao`).

O "ligado" vai no `.claude/settings.local.json` do jogo, fora do git. O que a `iniciar-sdd` copia
(o `AGENTS.md`, as lições, a `specs/`, os modelos) e a linha nova do `.gitignore` ficam na pasta do
jogo, que é um repositório git: o commit é seu, e num repositório que outras pessoas usam eles
aparecem para elas. O registro (`~/Golem/jogos.md`) e o "ligado" são desta máquina; noutra máquina,
registre o jogo de novo.

**O que vai para o jogo, e o que não vai.** A pasta do jogo recebe só o que é dela: o `AGENTS.md`
(com as lacunas `<< >>` que você preenche), o `CLAUDE.md`, o `WORKFLOW.md`, o
`docs/operacao-das-conversas.md`, a `docs/licoes/` (o `README.md` do formato e as lições de
exemplo), o modelo de ADR, a `specs/`, o `CHANGELOG.md`, o modelo de PR, o `.claude/LICENSE`, o
índice das lições, as linhas do kit no `.gitignore`, o "ligado" e, se você quiser, um `golem.toml`
só do jogo. O resto do kit (as skills, os agentes, o gancho, a régua, os guias e os modelos) fica na
pasta do kit. Nunca vão ao jogo: os testes do kit (`.claude/tests/`), o `docs/plano-produto.md`, a
`specs/` do kit e o `AGENTS.md` e o `golem.toml` do próprio kit.

## Usando com o Codex

O Codex não usa o plugin do Claude Code: com ele, o kit vai **copiado para dentro do projeto**
(abaixo), e o Golem central não conta. O Codex lê o mesmo `AGENTS.md`, mas procura o resto em outros
lugares. A fonte continua sendo `.claude/`; um instalador gera as cópias que o Codex lê, e elas vão
para o git com o projeto. O repositório do kit não traz as cópias: elas nascem no seu projeto, no
passo 1 de "Gerar as cópias do Codex".

### Instalar por cópia

O projeto precisa ser um repositório git (`git init`, se ainda não for).

1. **Copie para a raiz do projeto:**
   - a pasta `.claude/`, **sem** a `.claude/tests/` (que são os testes do próprio kit): as skills, os
     agentes, o gancho, a régua, o `settings.json`, o índice das lições, que **já vem pronto** no
     kit, e o `LICENSE` do kit, que fica junto (é a condição da licença, veja "Licença e crédito");
   - da pasta `docs/`, só o `docs/operacao-das-conversas.md`, o `docs/guia-configuracao.md`, o
     `docs/guia-roblox.md` e a `docs/licoes/` (as lições de exemplo); o `docs/plano-produto.md` é
     do kit e não vai;
   - o `templates/AGENTS.md`, copiado como `AGENTS.md` (é o modelo, com as lacunas `<< >>` que
     você preenche; o `AGENTS.md` da raiz do kit é o do desenvolvimento do próprio kit e não vai);
   - o `WORKFLOW.md` e o `CLAUDE.md` (ele importa o `AGENTS.md` para o Claude Code; quem usa só o
     Codex não precisa dele).

   Se o projeto já tem algum desses arquivos, **não sobrescreva**: junte à mão. No `CLAUDE.md`
   existente, acrescente a linha `@AGENTS.md`. No `.claude/settings.json`
   existente, junte os blocos `hooks` do kit aos seus.

2. **Junte ao `.gitattributes` e ao `.gitignore` do projeto as linhas do kit** (crie os arquivos se
   não existirem). A do `.gitattributes` mantém o gancho com fim de linha LF, sem o qual o `sh`
   quebra; as do `.gitignore` tiram do git o log do gancho, o registro da gerente e o
   `golem.local.toml`, que guarda o caminho do Python desta máquina.

3. **Ponha os arquivos no git, antes de gerar o índice.** A régua só vê as lições que o git
   conhece:

   ```bash
   git add .claude docs AGENTS.md WORKFLOW.md CLAUDE.md
   git add .gitattributes .gitignore
   ```

   Quem não copiou o `CLAUDE.md` (só Codex) tira ele do primeiro `git add`: um caminho que não
   existe faz o comando inteiro falhar.

   No Windows, o git pode avisar `LF will be replaced by CRLF` para vários arquivos: é normal. O
   `gancho.sh` não aparece na lista, porque o `.gitattributes` o mantém em LF.

4. **Gere e confira o índice das lições, e aplique a configuração:**

   ```bash
   python3 .claude/regua.py --gerar
   python3 .claude/regua.py --conferir
   tail -1 .claude/indice/licoes.yaml
   python3 .claude/golem.py aplicar
   git add .claude/agents AGENTS.md
   ```

   O `aplicar` deixa os agentes no modelo da receita do seu projeto: sem `golem.toml`, a
   `economico`, com o `revisor` no Sonnet. Numa instalação nova, ele diz
   `escrito  .claude/agents/revisor.md` e `1 arquivo(s) mudaram`. Sem o `aplicar`, o `revisor`
   fica no modelo do kit (o Opus). O `git add` põe no stage o que ele escreveu (os agentes e, num
   `AGENTS.md` juntado à mão, o bloco "Como o Golem trabalha aqui"). Sem Python, troque à mão, no
   `.claude/agents/revisor.md`, a linha `model:` por `model: sonnet`, e rode o mesmo `git add`.

   O `--conferir` tem de terminar com `ok       .claude/indice/licoes.yaml`, e a última linha do
   índice tem de ser `total:` com um número **maior que zero**: o de arquivos em `docs/licoes/`,
   fora o `README.md`. Se o `--gerar` recusar dizendo que nenhuma lição está no git, faltou o passo 3.
   Daqui para a frente, sempre que o `--gerar` mudar o índice, faça `git add .claude/indice`: o
   `--conferir` avisa (sem falhar) quando o índice da pasta difere do que está no stage.

5. **Confira que o gancho entrega uma lição:**

   ```bash
   echo '{"tool_input":{"command":"pytest -q"}}' | sh .claude/hooks/gancho.sh
   ```

   A saída é um JSON com `suite-verde-so-vale-com-a-linha-de-resumo` dentro. Se vier
   `"systemMessage"` com "falhou", a mensagem diz o motivo (o mais comum: nenhum Python que rode).

6. **Abra uma sessão nova** do agente na pasta do projeto: skill e gancho novos só aparecem em
   sessão nova. Com o Codex, faça antes "Gerar as cópias do Codex", abaixo.

7. **Opcional: configure o Golem.** Sem `golem.toml`, vale a receita `economico`: um revisor por
   fase, e a implementação para a cada parte para o seu ok. Para mudar, peça "configurar o Golem"
   (skill `configurar`) e responda aos botões. As receitas e o que cada uma custa estão em
   `docs/guia-configuracao.md`. A configuração nova vale numa sessão nova.

O commit desses arquivos é seu: faça quando quiser, junto com o que mais estiver pendente.

A pasta `templates/` é opcional (num jogo do Roblox, não: o executor de testes sai de
`templates/roblox/`, como diz o `docs/guia-roblox.md`): são os modelos de cada documento, com um
exemplo por seção, para
quem quer ver a forma sem rodar a skill. A skill `iniciar-sdd` usa quatro deles (o do
`AGENTS.md`, o do PR, o do `CHANGELOG.md` e o do ADR); se `templates/` não estiver no projeto, ela
pergunta onde está o kit.

### Gerar as cópias do Codex

| No Claude Code | No Codex | De onde vem |
|---|---|---|
| `CLAUDE.md` (importa o `AGENTS.md`) | `AGENTS.md`, lido direto; o `CLAUDE.md` não é necessário | o kit |
| `.claude/skills/` | `.agents/skills/` | cópia de `.claude/skills/` |
| `.claude/agents/*.md` | `.codex/agents/*.toml` | gerado de `.claude/agents/` |
| `.claude/settings.json` (o gancho) | `.codex/hooks.json`, com uma entrada para `Bash` e outra para `apply_patch` (as edições de arquivo) | gerado; chama o mesmo `.claude/hooks/gancho.sh` |

Depois dos passos 1 a 5 da instalação por cópia:

1. **Gere as cópias e confira:**

   ```bash
   python3 .claude/instalar_codex.py
   python3 .claude/instalar_codex.py --conferir
   git add .agents .codex
   ```

   O `--conferir` tem de terminar com `ok`. Rode o instalador **de novo sempre que mudar uma skill
   ou um agente** em `.claude/` (uma segunda rodada sem mudança diz "nada mudou"), e faça o commit
   das cópias junto com a fonte. Não edite as cópias à mão: o `--conferir` acusa.

2. **Confira que o gancho entrega uma lição para as duas ferramentas do Codex:**

   ```bash
   echo '{"tool_name":"Bash","tool_input":{"command":"pytest -q"}}' | sh .claude/hooks/gancho.sh
   printf '%s' '{"tool_name":"apply_patch","tool_input":{"command":"*** Begin Patch\n*** Update File: pyproject.toml\n*** End Patch\n"}}' | sh .claude/hooks/gancho.sh
   ```

   Os dois devolvem `suite-verde-so-vale-com-a-linha-de-resumo`: o primeiro pelo comando
   `pytest`; o segundo porque o patch edita o `pyproject.toml`, onde mora o `addopts` do pytest. No
   `apply_patch`, o gancho olha só os caminhos do cabeçalho do patch (`*** Add File:`,
   `*** Update File:`, `*** Delete File:`, `*** Move to:`), nunca o conteúdo.

3. **Abra o Codex na pasta do projeto e confie no gancho quando ele pedir.** O Codex só carrega o
   `.codex/` de um projeto confiável e mostra a definição exata do gancho antes de rodá-la: leia o
   comando (ele chama `sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"`) e confie.
   Sem isso, nenhuma lição chega.

**O revisor e o validador.** A regra 11 do `AGENTS.md` manda delegar a eles. No Claude Code, são
subagentes (`.claude/agents/`), e o agente os chama sozinho; você também pode pedir "use o
subagente revisor neste diff". No Codex, são os agentes de `.codex/agents/`, que o agente principal
chama quando o `AGENTS.md` ou uma skill manda delegar, ou quando você pede: "delegue ao agente
revisor a revisão deste diff".

**Várias conversas.** A coordenação entre conversas por mensagem é só do app desktop do Claude
Code. No Codex, você repassa as mensagens à mão, como no terminal (abaixo).

**O que muda no uso, e os limites conhecidos.**
- **Chamar uma skill:** no Claude Code, `/nome-da-skill`; no Codex, `$nome-da-skill` (ou `/skills`).
  As descrições citam a forma do Claude, mas nos dois o agente também a escolhe sozinho pelo pedido.
- **"Só leem" vale por instrução no Codex.** No Claude Code, o campo `tools:` do agente restringe as
  ferramentas de fato; no Codex, o agente herda as permissões da conversa principal, e o "não
  edite" vem só das instruções.
- **Codex no Windows:** o gancho roda por `sh`. Fora do Git Bash ou do WSL, o `sh` costuma não estar
  no PATH do Windows: o Codex marca o gancho como falho, avisa e segue sem as lições. Use o Codex no
  WSL ou ponha o `sh.exe` do Git for Windows no PATH.
- **Tamanho:** o Codex recorta a saída de cada gancho (cerca de 2.500 tokens, o começo e o fim).
  Lição longa chega cortada: mantenha o "Como perceber" curto, como o modelo pede.

## Começar

- **Jogo novo:** na pasta do Golem central (`~/Golem`), peça "registrar um jogo" (skill
  `iniciar-sdd`). Ela prepara a pasta do jogo, cria só o que falta e liga o Golem nela; o trabalho
  segue numa sessão nova, aberta no jogo. Na cópia (o Codex), peça "iniciar SDD neste projeto" no
  próprio projeto.
- **Já tem a estrutura:** peça "criar a constituição" (skill `constituicao`). Ela entrevista você
  antes de escrever qualquer arquivo. Em projeto que já tem código, ela reconstrói a constituição
  a partir do que existe.
- **Depois:** "próxima fase" (`spec-de-fase`), "implementar a fase" (`implementar-fase`), "validar
  a fase" (`validar-fase`).

Para um projeto pequeno, uma conversa só basta. Os papéis de várias conversas valem a pena quando
você tem duas ou mais entregas andando ao mesmo tempo.

**Várias conversas, no app, no terminal ou no Codex.** A coordenação entre conversas por mensagem
(uma conversa mandar mensagem a outra, a caixa de pergunta com botões) é só do **app desktop** do
Claude Code. No terminal e no Codex, você mesmo repassa as mensagens, copiando o PEDIDO de uma
conversa para a gerente e o LIBERADO de volta. O método funciona igual; só o carteiro muda.

## Mapa das pastas

Com o Golem central, as pastas moram em três lugares: **no kit** (a pasta do plugin, uma só na
máquina, por exemplo `~/golem-kit`), **no central** (`~/Golem`) e **no jogo** (a pasta de cada
jogo).
Na cópia (o Codex), o que mora no kit vai para dentro do projeto.

| Pasta ou arquivo | Onde mora | O que é |
|---|---|---|
| `AGENTS.md` | no jogo | as regras permanentes do projeto, lidas em toda sessão |
| `CLAUDE.md` | no jogo | o Claude Code lê este arquivo sozinho, e ele importa o `AGENTS.md` (`@AGENTS.md`); o Codex não usa. O central nunca tem um: a documentação do Claude Code diz que ele subiria para os jogos de `~/Golem/jogos/`, e nas rodadas da fase 3 não subiu (lição `o-claude-md-da-pasta-de-cima-nao-chegou-ao-jogo`); sem ele, não há dúvida |
| `WORKFLOW.md` | no jogo | o fluxo, etapa por etapa |
| `golem.toml` | no central, e no jogo se ele quiser | a receita e as linhas que mudam como o Golem trabalha. O do central vale em todos os jogos; o do jogo, se houver, vale por cima, linha a linha. Sem nenhum, vale a `economico` |
| `golem.local.toml` | no central | o caminho do Python desta máquina (a skill `diagnostico` grava); fica fora do git |
| `jogos.md` | no central | o registro dos jogos desta máquina: o nome, a pasta e a data |
| `jogos/` | no central | as pastas dos jogos que não tinham pasta própria, uma por jogo, cada uma um repositório git |
| `.claude/settings.local.json` | no jogo e no central | o "ligado": liga o plugin naquela pasta. Fica fora do git |
| `docs/guia-configuracao.md` | no kit | as receitas, o que cada linha do `golem.toml` faz e o que custa |
| `docs/guia-roblox.md` | no kit | o Golem num jogo do Roblox sem Rojo: o Studio MCP, os modelos, os testes e como voltar atrás |
| `docs/operacao-das-conversas.md` | no jogo | os papéis das conversas, quem decide o quê, o fecho, o merge e as travas |
| `docs/licoes/` | no jogo | as lições: o formato no `README.md` e uma lição por arquivo |
| `docs/regras-de-area.md` | no jogo | (opcional, você cria) regras que só valem para quem mexe numa área; o gancho as entrega junto com as lições. Formato no topo do `.claude/hooks/licoes_relevantes.py` do kit |
| `docs/adr/` | no jogo | as decisões técnicas, uma por arquivo, com o modelo em `docs/adr/modelo.md` |
| `specs/` | no jogo | a constituição e uma pasta por fase |
| `CHANGELOG.md`, `.github/pull_request_template.md` | no jogo | o registro por data e o modelo de PR |
| `.claude/indice/licoes.yaml` | no jogo | o índice das lições, gerado pela régua; nunca se edita à mão |
| `.claude/LICENSE` | no kit e no jogo | a licença do kit (MIT), igual ao `LICENSE` da raiz do kit; a `iniciar-sdd` a copia ao jogo |
| `.claude-plugin/` | no kit | o manifesto do plugin e do marketplace |
| `.claude/skills/` | no kit | as skills do fluxo, uma pasta por skill |
| `.claude/agents/` | no kit | os subagentes `revisor` e `validador` |
| `.claude/hooks/` | no kit | o gancho que entrega as lições antes de uma ação |
| `.claude/golem.py` | no kit | o `aplicar` (o bloco "Como o Golem trabalha aqui" do `AGENTS.md`, e o `model:` dos agentes na cópia), o `central`, o `registrar` e o `onde` |
| `.claude/regua.py` | no kit | a régua: gera o índice das lições (`--gerar`) e confere que ele está em dia (`--conferir`); avisa também da ref de lição que não bate com o arquivo citado e do `AGENTS.md` acima do teto (`agents_teto`); no plugin, no repositório da pasta corrente; na cópia, no projeto em que está |
| `.claude/settings.json` | no kit (na cópia, no projeto) | liga o gancho quando o kit está dentro do projeto; no plugin, quem liga o gancho é o `.claude/hooks/hooks.json` |
| `.claude/instalar_codex.py` | no kit (na cópia, no projeto) | gera as cópias do Codex (`.agents/skills/`, `.codex/agents/`, `.codex/hooks.json`) e confere que estão em dia (`--conferir`) |
| `.agents/skills/`, `.codex/` | na cópia | (geradas pelo instalador, só para o Codex) as cópias das skills, dos agentes e do gancho |
| `templates/` | no kit | os modelos da constituição, da spec de fase (e do formato curto, `templates/fase/curta.md`), do `AGENTS.md`, do PR, do changelog e do ADR; em `templates/roblox/`, os de um jogo do Roblox (o executor de testes, as lições e os riscos de exemplo) |
| `.claude/tests/`, `docs/plano-produto.md`, `specs/` do kit | só no kit | os testes, o plano e as specs do próprio kit; nunca vão ao jogo |

## O que adaptar primeiro

1. **A seção "Comandos reais" do `AGENTS.md`.** Sem o comando de teste de verdade, as regras de
   validação ficam no ar. É o que mais rende. O comando de teste mora só ali.
2. **A seção "O projeto" do `AGENTS.md`**: uma frase sobre o que é, a stack e onde mora o quê.
3. **O merge**: o método (squash ou merge commit) e a lista do que só você mergeia, no `AGENTS.md`
   ("Convenções") e no `docs/operacao-das-conversas.md` ("Níveis de autonomia").
4. **Os níveis de autonomia** no `docs/operacao-das-conversas.md`: o que a conversa faz sozinha
   no seu projeto, o que precisa de você.
5. **O vocabulário das lições**, se as quatro áreas não servirem:
   - `AREAS_VALIDAS` e `TIPOS_VALIDOS`, no `.claude/regua.py` (no Golem central, a régua é do kit:
     mudar ali muda para todos os jogos): os valores que a régua aceita nos
     campos `area` e `tipo` de uma lição (atualize junto a lista do `docs/licoes/README.md`);
   - `POR_CAMINHO` e `POR_COMANDO`, no `.claude/hooks/licoes_relevantes.py` (no Golem central,
     também do kit): que trecho de caminho
     de arquivo e que comando acendem cada área, isto é, quais lições sem `gatilhos:` chegam em
     cada ação. As áreas usadas ali têm de estar em `AREAS_VALIDAS` (um teste confere).

O resto pode ficar como está até incomodar. Quando uma regra produzir efeito ruim, mude a regra
(é para isso que existe a conversa de método), em vez de contorná-la em silêncio.

## Licença e crédito

MIT, © 2026 Rodrigo Anciães Patelli. Veja o [LICENSE](LICENSE).

Você pode usar, mudar, juntar ao seu projeto e até vender o kit. A única condição da MIT é manter o
aviso de copyright e o texto da licença em toda cópia, ou parte substancial, do kit. Por isso:

- **O `.claude/LICENSE` viaja com o kit.** A `iniciar-sdd` o copia a cada jogo, e ele vai junto na
  cópia. Não o apague.
- **Cada skill, agente e script traz uma linha de crédito.** Nas skills, ela fica no campo
  `license:` do frontmatter; nos agentes, num comentário no fim; nos scripts, no topo (logo depois
  do shebang, quando há). Se você copiar só um desses arquivos para outro projeto, leve o `LICENSE`
  junto: a linha aponta para ele, não o substitui.
- **O que você escreve é seu.** A constituição, as specs e as lições que você escreve usam os
  modelos só como estrutura. O `AGENTS.md` e as lições de exemplo vêm do kit e ficam cobertos pelo
  `.claude/LICENSE`, que vai com eles ao jogo.

Se o Golem ajudou no seu projeto, um link para o repositório no seu README é um bom jeito de dar o
crédito. É um pedido, não uma condição.
