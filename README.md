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
  skill `diagnostico`), o `.venv` da raiz e o da pasta principal, `python3`, `python` e `py -3` no
  PATH e, no Windows, os lugares do instalador oficial (`%LOCALAPPDATA%\Programs\Python` e
  `%PROGRAMFILES%`). Se o aviso disser que não achou, peça o diagnóstico do Golem.
- **`sh`**, para o gancho. No Linux e no macOS ele já existe; no Windows, vem com o
  [Git for Windows](https://gitforwindows.org/).
- **git**.
- **`gh`** (o [GitHub CLI](https://cli.github.com/)), só para as skills que abrem e mergeiam PR.
- **pytest**, só se quiser rodar os testes do ferramental (`.claude/tests`).

Nos comandos abaixo, `python3` é o Python. **No Windows, rode os comandos no Git Bash** (o terminal
que vem com o Git for Windows: `echo … | sh …`, `tail` e as aspas simples não funcionam no
PowerShell nem no `cmd`), **e use `python` ou `py -3`** no lugar de `python3` (o `python3` do
Windows costuma ser um atalho da loja que não roda nada).

## Instalar num projeto

O projeto precisa ser um repositório git (`git init`, se ainda não for).

1. **Copie para a raiz do projeto:**
   - a pasta `.claude/` inteira (skills, agentes, gancho, régua, `settings.json`, testes, o índice
     das lições, que **já vem pronto** no kit, e o `LICENSE` do kit, que fica junto: é a condição
     da licença, veja "Licença e crédito");
   - a pasta `docs/` (a operação das conversas, o guia de configuração e as lições de exemplo);
   - o `AGENTS.md`, o `WORKFLOW.md` e o `CLAUDE.md` (ele importa o `AGENTS.md` para o Claude
     Code; quem usa só o Codex não precisa dele).

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

4. **Gere e confira o índice das lições:**

   ```bash
   python3 .claude/regua.py --gerar
   python3 .claude/regua.py --conferir
   tail -1 .claude/indice/licoes.yaml
   ```

   O `--conferir` tem de terminar com `ok       .claude/indice/licoes.yaml`, e a última linha do
   índice tem de ser `total:` com um número **maior que zero** (com as cinco lições de exemplo,
   `total: 5`). Se o `--gerar` recusar dizendo que nenhuma lição está no git, faltou o passo 3.
   Daqui para a frente, sempre que o `--gerar` mudar o índice, faça `git add .claude/indice`: o
   `--conferir` avisa (sem falhar) quando o índice da pasta difere do que está no stage.

5. **Confira que o gancho entrega uma lição:**

   ```bash
   echo '{"tool_input":{"command":"pytest -q"}}' | sh .claude/hooks/gancho.sh
   ```

   A saída é um JSON com `suite-verde-so-vale-com-a-linha-de-resumo` dentro. Se vier
   `"systemMessage"` com "falhou", a mensagem diz o motivo (o mais comum: nenhum Python que rode).

6. **Abra uma sessão nova** do agente na pasta do projeto: skill e gancho novos só aparecem em
   sessão nova. Com o Codex, faça antes a seção seguinte.

7. **Opcional: configure o Golem.** Sem `golem.toml`, vale a receita `economico`: um revisor por
   fase, e a implementação para a cada parte para o seu ok. Para mudar, peça "configurar o Golem"
   (skill `configurar`) e responda aos botões. As receitas e o que cada uma custa estão em
   `docs/guia-configuracao.md`. A configuração nova vale numa sessão nova.

O commit desses arquivos é seu: faça quando quiser, junto com o que mais estiver pendente.

A pasta `templates/` é opcional: são os modelos de cada documento, com um exemplo por seção, para
quem quer ver a forma sem rodar a skill. A skill `iniciar-sdd` usa três deles (o do PR, o do
`CHANGELOG.md` e o do ADR); se `templates/` não estiver no projeto, ela pergunta onde está o kit.

## Usando com o Codex

O Codex lê o mesmo `AGENTS.md`, mas procura o resto em outros lugares. A fonte continua sendo
`.claude/`; um instalador gera as cópias que o Codex lê, e elas vão para o git com o projeto.

| No Claude Code | No Codex | De onde vem |
|---|---|---|
| `CLAUDE.md` (importa o `AGENTS.md`) | `AGENTS.md`, lido direto; o `CLAUDE.md` não é necessário | o kit |
| `.claude/skills/` | `.agents/skills/` | cópia de `.claude/skills/` |
| `.claude/agents/*.md` | `.codex/agents/*.toml` | gerado de `.claude/agents/` |
| `.claude/settings.json` (o gancho) | `.codex/hooks.json`, com uma entrada para `Bash` e outra para `apply_patch` (as edições de arquivo) | gerado; chama o mesmo `.claude/hooks/gancho.sh` |

Depois dos passos 1 a 5 da instalação:

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

- **Projeto do zero ou sem nada de SDD:** peça "iniciar SDD neste projeto" (skill `iniciar-sdd`).
  Ela confere o que existe e cria só o que falta (a pasta `specs/`, o `CHANGELOG.md`, o modelo de
  PR).
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

| Pasta ou arquivo | O que é |
|---|---|
| `AGENTS.md` | as regras permanentes do projeto, lidas em toda sessão |
| `CLAUDE.md` | o Claude Code lê este arquivo sozinho, e ele importa o `AGENTS.md` (`@AGENTS.md`); o Codex não usa |
| `WORKFLOW.md` | o fluxo, etapa por etapa |
| `golem.toml` | (opcional, a skill `configurar` cria) a receita e as linhas que mudam como o Golem trabalha; sem ele, vale a `economico` |
| `docs/guia-configuracao.md` | as receitas, o que cada linha do `golem.toml` faz e o que custa |
| `docs/operacao-das-conversas.md` | os papéis das conversas, quem decide o quê, o fecho, o merge e as travas |
| `docs/licoes/` | as lições: o formato no `README.md` e uma lição por arquivo |
| `docs/regras-de-area.md` | (opcional, você cria) regras que só valem para quem mexe numa área; o gancho as entrega junto com as lições. Formato no topo do `.claude/hooks/licoes_relevantes.py` |
| `.claude/skills/` | as skills do fluxo, uma pasta por skill |
| `.claude/agents/` | os subagentes `revisor` e `validador` |
| `.claude/hooks/` | o gancho que entrega as lições antes de uma ação |
| `.claude/golem.py` | o `aplicar`: junta a receita e o `golem.toml` e escreve o bloco "Como o Golem trabalha aqui" do `AGENTS.md` e o `model:` dos agentes |
| `.claude/regua.py` | a régua: gera o índice das lições (`--gerar`) e confere que ele está em dia (`--conferir`) |
| `.claude/indice/licoes.yaml` | o índice das lições, gerado pela régua; nunca se edita à mão |
| `.claude/settings.json` | liga o gancho no Claude Code |
| `.claude/LICENSE` | a licença do kit (MIT), que viaja com a pasta `.claude/`; igual ao `LICENSE` da raiz do kit |
| `.claude/instalar_codex.py` | gera as cópias do Codex (`.agents/skills/`, `.codex/agents/`, `.codex/hooks.json`) e confere que estão em dia (`--conferir`) |
| `.agents/skills/`, `.codex/` | (geradas pelo instalador, só para o Codex) as cópias das skills, dos agentes e do gancho |
| `.claude/tests/` | os testes do ferramental: `python3 -m pytest .claude/tests -o addopts= -q -p no:cacheprovider` |
| `templates/` | os modelos da constituição, da spec de fase (e do formato curto, `templates/fase/curta.md`), do PR, do changelog e do ADR |
| `specs/` | (criada pela `iniciar-sdd`) a constituição e uma pasta por fase |

## O que adaptar primeiro

1. **A seção "Comandos reais" do `AGENTS.md`.** Sem o comando de teste de verdade, as regras de
   validação ficam no ar. É o que mais rende. O comando de teste mora só ali.
2. **A seção "O projeto" do `AGENTS.md`**: uma frase sobre o que é, a stack e onde mora o quê.
3. **O merge**: o método (squash ou merge commit) e a lista do que só você mergeia, no `AGENTS.md`
   ("Convenções") e no `docs/operacao-das-conversas.md` ("Níveis de autonomia").
4. **Os níveis de autonomia** no `docs/operacao-das-conversas.md`: o que a conversa faz sozinha
   no seu projeto, o que precisa de você.
5. **O vocabulário das lições**, se as quatro áreas não servirem:
   - `AREAS_VALIDAS` e `TIPOS_VALIDOS`, no `.claude/regua.py`: os valores que a régua aceita nos
     campos `area` e `tipo` de uma lição (atualize junto a lista do `docs/licoes/README.md`);
   - `POR_CAMINHO` e `POR_COMANDO`, no `.claude/hooks/licoes_relevantes.py`: que trecho de caminho
     de arquivo e que comando acendem cada área, isto é, quais lições sem `gatilhos:` chegam em
     cada ação. As áreas usadas ali têm de estar em `AREAS_VALIDAS` (um teste confere).

O resto pode ficar como está até incomodar. Quando uma regra produzir efeito ruim, mude a regra
(é para isso que existe a conversa de método), em vez de contorná-la em silêncio.

## Licença e crédito

MIT, © 2026 Rodrigo Anciães Patelli. Veja o [LICENSE](LICENSE).

Você pode usar, mudar, juntar ao seu projeto e até vender o kit. A única condição da MIT é manter o
aviso de copyright e o texto da licença em toda cópia, ou parte substancial, do kit. Por isso:

- **O `.claude/LICENSE` viaja com o kit.** Não o apague ao instalar.
- **Cada skill, agente e script traz uma linha de crédito.** Nas skills, ela fica no campo
  `license:` do frontmatter; nos agentes, num comentário no fim; nos scripts, no topo (logo depois
  do shebang, quando há). Se você copiar só um desses arquivos para outro projeto, leve o `LICENSE`
  junto: a linha aponta para ele, não o substitui.
- **O que você escreve é seu.** A constituição, as specs e as lições que você escreve usam os
  modelos só como estrutura. O `AGENTS.md` e as lições de exemplo vêm do kit e ficam cobertos pelo
  `.claude/LICENSE`, que continua no mesmo repositório.

Se o Golem ajudou no seu projeto, um link para o repositório no seu README é um bom jeito de dar o
crédito. É um pedido, não uma condição.
