# Fase 3: a fundação do Golem central — Plano

O fluxo é o da receita `completo` do kit (`AGENTS.md`, "Como o Golem trabalha aqui"): revisor e
validador a cada grupo, no Opus (o `model: opus` passado na chamada), sem parada entre os grupos,
e o guardião sobre o diff inteiro do PR antes do PEDIDO de merge. Um commit por grupo, na branch
da fase: aprovado junto com a spec, "Aprovo" (2026-11-22).

**Antes do G1:** a spec aprovada pelo autor do kit, com as respostas dos cartões 1 e 2 dentro; a
branch trazida para a `main` do momento, se ela tiver andado, e as linhas citadas reconferidas.

## G1 — A raiz do projeto, o modo plugin e a configuração em dois níveis (R2)

- [x] `.claude/golem.py`:
  - a raiz do projeto (a posição, ou o git da pasta corrente quando a posição é o plugin) e o modo
    plugin;
  - o central (`GOLEM_CENTRAL`, senão `$HOME/Golem`, senão o `Path.home()`);
  - a `configuracao` com o `golem.toml` do central por baixo do do jogo, só no modo plugin. A
    `teto_do_gancho` segue a mesma conta.
- [x] `.claude/hooks/gancho.sh`:
  - a raiz pelo `CLAUDE_PROJECT_DIR`, quando ele existe e é uma pasta; sem ele, a posição, salvo
    quando a posição é o plugin (o git da pasta corrente); e o `CLAUDE_PROJECT_DIR` exportado com
    essa raiz para o `.py`;
  - no modo plugin, a linha `gancho` do `golem.toml` do central antes da do jogo (vale a última),
    e a linha `python` do `golem.local.toml` do central depois das duas de hoje;
  - o cabeçalho do arquivo dizendo a ordem nova.
- [x] `.claude/hooks/licoes_relevantes.py`: a raiz pelo `CLAUDE_PROJECT_DIR`, senão a posição; o
  teto pelo `golem.py` com essa raiz. O `golem.py` continua carregado pela posição (`:74`).
- [x] `.claude/regua.py`: a raiz como no `golem.py`; o gancho continua carregado pela posição
  (`:43`, `:129`).
- [x] `.claude/tests/conftest.py`: o `AMBIENTE` sem `CLAUDE_PROJECT_DIR` e com o `GOLEM_CENTRAL`
  numa pasta vazia.
- [x] Testes novos (em `test_golem.py` e `test_gancho.py`), sobre um "kit" com
  `.claude-plugin/plugin.json` e um "jogo" à parte, numa árvore descartável:
  - o gancho rodado da pasta do kit com o `CLAUDE_PROJECT_DIR` do jogo entrega a lição **do jogo**,
    e não a do kit;
  - o gancho do "kit" rodado **sem** o `CLAUDE_PROJECT_DIR`, com a pasta corrente no jogo (como
    as skills o rodam pelo Bash), também entrega a lição do jogo;
  - no modo plugin, `gancho = "desligado"` no central cala o gancho, e o `ligado` no jogo o religa;
  - no modo plugin, a linha `python` só no `golem.local.toml` do central é usada;
  - a `configuracao` do jogo: uma linha do central vale; a mesma chave no jogo vence; a receita do
    jogo vence a do central;
  - fora do modo plugin (o kit, a cópia), o `golem.toml` do central é ignorado;
  - a régua e o `golem.py` rodados da pasta do kit com a pasta corrente no jogo trabalham no jogo,
    e o jogo não tem nenhum script do kit;
  - o `licoes_relevantes.py` rodado com o `CLAUDE_PROJECT_DIR` do jogo lê as lições do jogo;
  - o central: com o `HOME` numa pasta e o `USERPROFILE` noutra, sem `GOLEM_CENTRAL`, o `gancho.sh`
    e o `golem.py` acham o mesmo `$HOME/Golem`.
- [x] A suíte inteira, com a linha de resumo lida: `150 passed`, sem pulados (134 + 16 novos: 10 no `test_gancho.py`, 6 no `test_golem.py`).

**Revisão:** revisor e validador sobre o diff do grupo.

## G2 — O esqueleto do plugin (R1)

- [x] `.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`, como no R1 (o formato das
  provas P1 e P2, com `author`, `license` e `homepage`).
- [x] `.claude/hooks/hooks.json`, com o lançador em `${CLAUDE_PLUGIN_ROOT}`.
- [x] Testes novos:
  - os caminhos do `plugin.json` existem, e as skills e os agentes que ele aponta são todos os de
    `.claude/skills/` e `.claude/agents/`;
  - o `hooks.json` e o `.claude/settings.json` têm os mesmos `matcher`, `timeout` e a mesma queda,
    com o lançador trocado;
  - o `plugin.json` traz o crédito (`author`, `license`, `homepage`) e o `"defaultEnabled": false`;
  - o `marketplace.json` lista o plugin `golem` em `"./"`.
- [x] `claude plugin validate <kit>` passa ("Validation passed with warnings"): o `version` é o `0.0.1` do P1, como o R1 pede (o
  formato das versões fica para a fase 9); os avisos são o `CLAUDE.md` da raiz (não é lido; é o do desenvolvimento do kit), sem ícone e sem `network.hosts` (avisos do catálogo, que não mudam o resultado). Antecipado do S1: instalado do worktree numa configuração isolada, o plugin nasce desligado e aparece só no projeto com o "ligado" (`fase-3-provas/g2-*`: o `validate` inteiro em `g2-validate.txt`, o "ligado" no `.claude/settings.local.json`, uma rodada por projeto; as duas por projeto estão no relatório do validador do G2, que não se arquivou: refazem-se no S3 e no S4 do G6).
- [x] A suíte inteira: `154 passed`, sem pulados (150 + 4 do `test_plugin.py`).

**Revisão:** revisor e validador sobre o diff do grupo.

## G3 — O central e o registro dos jogos (R3)

- [x] `.claude/golem.py`: os comandos `central`, `registrar <pasta> [--nome]`, `aplicar --todos`
  e `onde`, e o `USO` com os cinco.
  - o "ligado" juntado ao `.claude/settings.local.json` (cartão 1), guardando o que ele já tem; o JSON quebrado falha
    com a mensagem e sem escrever;
  - o `jogos.md` criado com o cabeçalho, uma linha por jogo, sem duplicar a pasta;
  - o central nunca ganha `CLAUDE.md`.
- [x] Testes novos, com o `GOLEM_CENTRAL` numa pasta descartável:
  - o `central` cria as quatro peças, e a segunda rodada diz "nada mudou";
  - o `registrar` põe a linha no `jogos.md` e o "ligado" no jogo; a segunda rodada não duplica;
  - o `registrar` num repositório que já tem `.gitignore`
    sem a linha a acrescenta, uma vez, e o `git check-ignore .claude/settings.local.json` confirma;
    num repositório sem `.gitignore`, ele o cria com a linha;
  - o `registrar` num jogo que já tem o arquivo do "ligado" com outras chaves guarda as outras;
  - o arquivo do "ligado" com JSON quebrado: o `registrar` falha, diz o arquivo e não escreve
    nada;
  - o nome com `|`: recusado;
  - o `aplicar --todos` escreve o bloco em dois jogos, e avisa e segue quando a pasta de um sumiu;
  - o `onde` diz o modo e de onde vem uma linha (do central, do jogo);
  - nenhum `CLAUDE.md` no central depois do `central` e do `registrar`.
- [x] A suíte inteira: `164 passed`, sem pulados (154 + 10 do G3, no `test_golem.py`).

**Revisão:** revisor e validador sobre o diff do grupo.

## G4 — As skills, os agentes e o modelo do `AGENTS.md` (R4)

- [x] A busca do que trocar, pelo arquivo e não pelo jeito de chamar:
  `grep -rnE '\.claude/(golem|regua|instalar_codex)\.py|\.claude/hooks/|templates/|docs/guia-' .claude/skills .claude/agents`.
  Cada ocorrência que aponta um arquivo do kit passa ao `${CLAUDE_SKILL_DIR}`; o que mora no jogo
  fica, e cada linha que sobrar se justifica no PR.
- [x] `.claude/skills/iniciar-sdd/SKILL.md`: o fluxo no central (R4) e a variante da cópia.
- [x] `.claude/skills/configurar/SKILL.md`: o modo pela conferência em `sh` (como a `diagnostico`), e o `onde` depois do `aplicar`, para mostrar de onde vem cada linha; no modo plugin, o central
  por padrão, o `aplicar --todos`, o "só neste jogo" e a linha `python` lida também do central.
- [x] `.claude/skills/diagnostico/SKILL.md`: o modo pela conferência em `sh` (ela roda justamente sem Python); a linha `python` no
  central, no modo plugin.
- [x] `.claude/skills/implementar-fase/SKILL.md` e `validar-fase/SKILL.md`: o modelo do bloco
  passado na chamada do revisor e do validador, e o agente pelo nome que a sessão lista
  (`golem:revisor` no plugin).
- [x] `.claude/golem.py`: o `bloco` no modo plugin aponta o guia pelo pedido, e o comentário
  gerado (`:154`) sai sem o caminho; o `aplicar`, no modo plugin, diz que o modelo vai na chamada
  em vez de "pulado … não existe neste projeto".
- [x] `templates/AGENTS.md` e `AGENTS.md`: a regra 11 (o modelo na chamada) e as linhas do R4, o
  mesmo texto nos dois; a `PERMITIDAS` do conciliador, se alguma diferença permitida mudar.
- [x] `.claude/instalar_codex.py`: a troca do `${CLAUDE_SKILL_DIR}` nas cópias, e o teste.
- [x] Testes: o `${CLAUDE_SKILL_DIR}` só aparece na forma `…/../../` ou `…/../../../` e aponta para
  um arquivo que existe no kit; nenhuma skill nem agente cita `.claude/golem.py`,
  `.claude/regua.py`, `.claude/instalar_codex.py` ou `.claude/hooks/` sem o `${CLAUDE_SKILL_DIR}`
  na frente.
- [x] `python .claude/instalar_codex.py --conferir`, numa cópia com as cópias geradas (`ok       24
  arquivos do Codex batem com .claude/`, nenhum `CLAUDE_SKILL_DIR` nas cópias), e a suíte inteira:
  `166 passed`, sem pulados (164 + 2 do `test_plugin.py`; os testes do Codex e do `aplicar` mudaram
  de forma, sem contar a mais).

**Revisão:** revisor e validador sobre o diff do grupo.

## G5 — A lista do que viaja, o mapa e o `README.md` (R5)

- [ ] `README.md`: "Instalar o Golem (uma vez)", "Registrar um jogo", a cópia em "Usando com o
  Codex" com a lista corrigida (sem a `.claude/tests/` e sem o `docs/plano-produto.md`), e o
  "Mapa das pastas" com o "onde mora".
- [ ] Os documentos que viajam ao jogo (R5): `docs/licoes/README.md`, `WORKFLOW.md`,
  `docs/operacao-das-conversas.md` e a seção "Licença e crédito" do `README.md`, pela busca
  `grep -nE '\.claude/(regua|golem|instalar_codex)\.py|\.claude/(hooks|skills|agents)/|\.claude/LICENSE' docs/licoes/README.md WORKFLOW.md docs/operacao-das-conversas.md README.md`.
  Cada linha diz o que vale no jogo com o plugin, ou se justifica no PR.
- [ ] A busca do que fala da instalação por cópia como a única:
  `grep -rnE "Copie para a raiz|a pasta \`\.claude/\` inteira|a pasta \`docs/\`|Instalar num projeto" --include=*.md --include=*.py .`
  (fora de `specs/`, que guarda o histórico). Cada ocorrência corrigida ou justificada no PR.
- [ ] `docs/plano-produto.md`: a nota da seção 6 e a linha da fase 3 na seção 7 só pelo
  `validar-fase` (o roteiro); nada de decisão nova sem o autor do kit.
- [ ] `python .claude/regua.py --conferir` e a suíte inteira.

**Revisão:** como o G5 é só de documentação, o caminho rápido: só o revisor, que confere fato por
fato contra a fonte. Se ganhar código, volta ao caminho completo.

## G6 — Verificação

- [ ] O `validation.md` inteiro, com a saída de cada comando anotada.
- [ ] As rodadas sem login (o plugin da branch, numa configuração isolada).
- [ ] As rodadas com login, depois da pergunta ao autor do kit (`requirements.md`, "Perguntas em
  aberto").
- [ ] A limpeza da configuração isolada (apagar a pasta; com login, antes o `/logout`).

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|
| 2026-11-22 | A `diagnostico` e a `configurar` sabem o modo por uma conferência em `sh` (a pasta do kit tem o manifesto e é outra que a raiz), e não pelo `onde`; o `onde` fica na `configurar`, depois do `aplicar`, para mostrar ao usuário de onde vem cada linha | a `diagnostico` roda justamente quando o Python falta, e o `onde` pede Python; a `configurar` acha o Python só no passo 4 | o agente, dentro do R3 e do R4 (detalhe de implementação) |
| 2026-11-22 | O modo plugin pede também que a pasta do kit seja o plugin (tenha o manifesto), e não só que a raiz seja outra | o revisor do G1: sem isso, a cópia do Codex, sem o manifesto, entraria no modo plugin ao ser chamada com outra raiz; a cópia e o kit não mudam, como o R2 já dizia. Na suíte, o kit tem o manifesto depois do G2, e quem a protege do central da máquina é o `GOLEM_CENTRAL` do `conftest.py` | o agente, dentro do R2 (detalhe de implementação) |
