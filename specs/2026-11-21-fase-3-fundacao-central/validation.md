# Fase 3: a fundação do Golem central — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, sem pytest, que roda a régua e o `golem.py`.
- `CC` é o `claude.exe` do app (2.1.330 nas provas da spec).
- `ISO` é uma pasta descartável no scratchpad da conversa. O `CLAUDE_CONFIG_DIR="$ISO/cfg"` e o
  `GOLEM_CENTRAL="$ISO/Golem"` valem em todo comando que chama o `CC` ou o `golem.py` fora da
  suíte. O `~/.claude` e o `~/Golem` do autor do kit nunca são tocados.
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`.

## Verificações automatizadas

- [ ] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem pulados. **N** é 134 (a contagem em `e1483ac`) mais os testes novos dos G1 a G4,
  anotados aqui ao fim de cada grupo. Se a `main` andar, a contagem dela entra no lugar do 134.
  - **G1:** `150 passed`, sem pulados (134 + 16).
  - **G2:** `154 passed`, sem pulados (150 + 4).
  - **G3:** `164 passed`, sem pulados (154 + 10).
- [ ] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
- [ ] `"$PYR" .claude/golem.py aplicar`, no kit → `nada mudou`, e o `git status --short` continua
  igual: o kit não está no modo plugin (R2).
- [ ] `"$CC" plugin validate .` → `Validation passed` (com avisos, lidos e anotados; nenhum erro)
  (R1).
- [ ] O teste do G4 que confere que nenhuma skill nem agente cita `.claude/golem.py`,
  `.claude/regua.py`, `.claude/instalar_codex.py` ou `.claude/hooks/` sem o `${CLAUDE_SKILL_DIR}`
  na frente passa, na suíte acima (R4). A busca é pelo arquivo, ocorrência por ocorrência, porque
  há chamadas como `"$PY" .claude/golem.py` e
  `sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"`.
- [ ] Numa cópia da árvore (`git archive HEAD`, num `git init` novo):
  `"$PYR" .claude/instalar_codex.py && "$PYR" .claude/instalar_codex.py --conferir` → `ok`, e
  `grep -rn 'CLAUDE_SKILL_DIR' .agents/skills` → nenhuma linha (R4).
- [ ] **A lista do que se copia, no `README.md`** (R5), lida por uma pessoa (o agente, e o
  revisor do G5 confere): em "Instalar o Golem (uma vez)" e "Registrar um jogo", nada se copia à
  mão; em "Usando com o Codex", a lista da cópia bate item por item com a tabela do R5, a
  `.claude/tests/` aparece só como exclusão, e da `docs/` vão só os arquivos nomeados (nunca "a
  pasta `docs/`"). Ajuda: `grep -nE 'a pasta \`(\.claude|docs)/\`|tests' README.md`, e cada
  linha achada lida no contexto.

## Verificações sem login (o agente, numa configuração isolada)

O plugin é o worktree da branch, no head do G5. Cada rodada é
`"$CC" -p oi --output-format stream-json --verbose --model haiku`, rodada na pasta do caso, e lê
só o evento `system`/`init` (a lista de plugins, skills e agentes), que sai antes do login. O
`resumo.py` das provas da spec lê o evento. A transcrição de cada rodada fica na pasta de notas
da GER, em `fase-3-provas/`.

- [ ] **S1. A instalação:** `"$CC" plugin marketplace add <worktree>` e
  `"$CC" plugin install golem@golem --scope user` → a saída diz "disabled by default", e o
  `"$ISO/cfg/settings.json"` tem `"golem@golem": false` (R1).
- [ ] **S2. O central:** `"$PYR" .claude/golem.py central` → cria `"$ISO/Golem"` com o
  `golem.toml`, o `jogos.md`, a pasta `jogos/` e o "ligado"; sem `CLAUDE.md`. A rodada no central
  → o plugin `golem@golem`, 14 skills `golem:*` e os 2 agentes (cartão 2).
- [ ] **S3. Um jogo registrado:** em `"$ISO/Golem/jogos/teste"`, um `git init`, as lições
  (`cp -r <worktree>/docs/licoes docs/`, `git add docs/licoes`) e o índice
  (`"$PYR" <worktree>/.claude/regua.py --gerar`, rodado na pasta do jogo, → `total:` maior que 0);
  depois, `"$PYR" <worktree>/.claude/golem.py registrar "$ISO/Golem/jogos/teste" --nome teste` →
  a linha no `jogos.md`, o "ligado" no `.claude/settings.local.json` (cartão 1) e
  `git check-ignore .claude/settings.local.json` → o caminho (fora do git). Duas rodadas no jogo
  → o plugin, 14 skills e os 2 agentes nas duas.
- [ ] **S4. Um projeto fora do registro:** em `"$ISO/outro"`, um `git init`, **as mesmas lições e o
  mesmo índice** do S3 (para que um gancho que rodasse ali tivesse o que injetar). Duas rodadas →
  nem o plugin, nem skill `golem:*`, nem agente `golem:` nas duas.
- [ ] **S5. O gancho do plugin à mão, no jogo** (o comando do `hooks.json`, com o
  `CLAUDE_PLUGIN_ROOT` no worktree e o `CLAUDE_PROJECT_DIR` no jogo do S3, e o JSON de um
  `pytest -q` no stdin) → a lição `suite-verde-so-vale-com-a-linha-de-resumo` vem **do
  `docs/licoes/` do jogo**: tirada do jogo com `git rm` (a régua só vê o que o git rastreia,
  `regua.py:77`) e o índice regerado, ela some da saída, mesmo existindo no kit. Depois, a lição
  volta (nova cópia e `git add`) e o índice se regera, para
  o L1. O mesmo, rodado **sem** o `CLAUDE_PROJECT_DIR` e com a pasta corrente no jogo (como a
  `licao` o roda), dá a mesma lição.
- [ ] **S6. O `onde`, no jogo:** `cd "$ISO/Golem/jogos/teste" && "$PYR" <worktree>/.claude/golem.py onde`
  → diz o jogo como raiz, o modo plugin, o central em `"$ISO/Golem"` e, com
  `revisor = "nunca"` no `golem.toml` do central, "revisor: nunca (do central)".

## Verificações com login (o agente, depois do `/login` do autor do kit na configuração isolada)

Rodam só com o sim do autor do kit (`requirements.md`, "Perguntas em aberto"). Sem o sim, ficam
para ele, na configuração dele, com estes mesmos passos, e o PR diz isso. Todas no Haiku.

- [ ] **L1. O gancho roda no jogo** (2 rodadas): no jogo do S3, `"$CC" -p` com o Bash liberado,
  pedindo para rodar `python -m pytest --version`. Na transcrição da sessão
  (`"$ISO/cfg/projects/<pasta>/<sessão>.jsonl"`), o `additionalContext` do gancho traz o id
  `suite-verde-so-vale-com-a-linha-de-resumo`.
- [ ] **L2. O gancho fora do Golem** (2 rodadas): o mesmo pedido no projeto do S4, que tem as
  mesmas lições e o mesmo índice → a transcrição não tem o texto "Lições registradas" nem o id.
- [ ] **L3. O `${CLAUDE_SKILL_DIR}`** (1 rodada em cada): pedir a skill `licao` e só o comando da
  régua, sem rodar nada, (a) no jogo, pela skill de plugin `golem:licao`, e (b) numa cópia do kit
  na branch (`git archive`, num `git init` novo), pela skill de projeto `licao` → nas duas
  transcrições, o caminho da pasta da skill no lugar da variável, e nenhum `${CLAUDE_SKILL_DIR}`
  literal.
- [ ] **L4. A subida do `CLAUDE.md`** (1 rodada, sem ferramentas): um `CLAUDE.md` com uma marca,
  posto à mão em `"$ISO/Golem"` só para esta rodada e apagado depois; no jogo de `jogos/`, a
  pergunta "que marca aparece no seu contexto? responda sem ler arquivo" → a marca aparece. Isso
  confirma por que o central nunca tem `CLAUDE.md` (R3).
- [ ] **L5. O modo interativo** (1 vez): o `"$CC"` aberto sem `-p`, numa aba do terminal do app,
  numa pasta de jogo registrada e nunca aberta → aparece o diálogo de confiança na pasta; depois
  de aceitar, `/plugin` (ou a pergunta "quais skills golem você tem?") mostra o `golem`. Se o
  agente não conseguir dirigir a tela, o autor do kit faz os mesmos passos e diz o que viu.
- [ ] **L6. A `iniciar-sdd` de ponta a ponta** (1 rodada, com as ferramentas liberadas): no
  central do S2, pedir "registrar um jogo", com o nome `l6` e "não tenho pasta" (no `-p`, as
  respostas vão no próprio pedido). Depois, conferir à mão:
  - a pasta `"$ISO/Golem/jogos/l6"`, um repositório git, com cada item da linha "No jogo" da
    tabela do R5 (`ls -R`, item por item);
  - a linha `l6` no `jogos.md` e o "ligado" no jogo;
  - o índice com `total:` maior que 0 (`tail -1 .claude/indice/licoes.yaml`);
  - o bloco "Como o Golem trabalha aqui" no `AGENTS.md` do jogo, com a receita do central;
  - nenhuma `.claude/tests/`, nenhum `docs/plano-produto.md`, nenhum script do kit
    (`golem.py`, `regua.py`, `hooks/`) no jogo.
- [ ] **L7. O modelo na chamada** (1 rodada): no jogo do S3, pedir que se chame o agente
  `golem:revisor` com `model: haiku` sobre um arquivo pequeno → na transcrição do subagente
  (`"$ISO/cfg/projects/<pasta>/…"`), o modelo das mensagens dele é o Haiku, e não o Opus do
  frontmatter (R4).
- [ ] **A limpeza:** `/logout` na configuração isolada e a pasta `"$ISO"` apagada.

## Casos de borda (na suíte, G1 e G3)

- [ ] O `CLAUDE_PROJECT_DIR` apontando para uma pasta que não existe → o gancho cai na raiz de
  hoje, sem quebrar.
- [ ] A régua e o `golem.py` do kit rodados com a pasta corrente fora do kit e fora de um git →
  trabalham na pasta corrente, sem escrever no kit. Quem diz qual é a raiz é o `onde` (G3).
- [ ] Sem central nenhum, no modo plugin → a configuração é a da receita do jogo, sem erro, e o
  gancho entrega a lição.
- [ ] O `golem.toml` do central com uma linha errada → o `aplicar` do jogo falha dizendo o arquivo
  do central e a linha, e não escreve nada; o gancho segue com o teto padrão (`golem.py:124-129`).
- [ ] O arquivo do "ligado" com JSON quebrado → o `registrar` falha dizendo o arquivo, sem
  escrever.
- [ ] O nome do jogo com `|` → recusado.
- [ ] O `aplicar --todos` com a pasta de um jogo apagada → avisa esse jogo e aplica nos outros.

## A mutação (o validador, numa cópia descartável)

Cada item parte da cópia limpa e deve fazer algum teste falhar:

- [ ] O `gancho.sh` ignorando o `CLAUDE_PROJECT_DIR`.
- [ ] O `licoes_relevantes.py` ignorando o `CLAUDE_PROJECT_DIR`.
- [ ] O `gancho.sh` sem `CLAUDE_PROJECT_DIR` usando a posição mesmo quando ela é o plugin.
- [ ] A `regua.py` ou o `golem.py` usando a posição no modo plugin.
- [ ] O `golem.py` achando o central pelo `Path.home()` antes do `HOME`.
- [ ] O `registrar` sem a linha do `.gitignore`.
- [ ] A `configuracao` com o central por cima do jogo (a ordem trocada).
- [ ] O central lido também fora do modo plugin.
- [ ] O `registrar` sem a conferência da pasta repetida.
- [ ] O `registrar` sobrescrevendo o arquivo do "ligado" (perdendo as outras chaves).
- [ ] O `central` escrevendo um `CLAUDE.md`.
- [ ] O `hooks.json` com um `matcher` a menos que o `settings.json`.
- [ ] O `instalar_codex.py` sem a troca do `${CLAUDE_SKILL_DIR}`.

## Requisitos da constituição

- [ ] Nenhuma dependência nova: só a biblioteca padrão nos scripts, `sh` POSIX no gancho
  (regra 3). `git diff "$BASE" -- '*.py' | grep -E '^\+\s*(import|from) '` → só módulos da
  biblioteca padrão.
- [ ] Os arquivos novos do kit com crédito: o `test_credito.py` passa, e o `plugin.json` traz o
  `author`, a `license` e a `homepage`.
- [ ] Nenhum nome de cliente, de outro projeto ou de pessoa além do autor do kit (`AGENTS.md`,
  "Convenções"): o revisor de cada grupo e o guardião leem o diff inteiro procurando nomes, e o
  veredito de cada um diz que leu. Ajuda mecânica:
  `git diff "$BASE" | LC_ALL=C.UTF-8 grep -nP '^\+.*\b\p{Lu}\p{Ll}+ \p{Lu}\p{Ll}+\b'`, cada linha achada lida (a
  lista de nomes de fora não se escreve no repositório).
- [ ] O conciliador passa: o `templates/AGENTS.md` e o `AGENTS.md` mudaram juntos (R4).

## Registro

- [ ] O `docs/plano-produto.md`, seção 7: a linha da fase 3 marcada como feita, com a branch, a
  spec e a data (pela `validar-fase`).
- [ ] As respostas dos cartões 1 e 2 na spec, com as palavras e a data.
- [ ] O PEDIDO à GER, com o head, a base e a prova; o merge só com o LIBERADO e o ok do autor do
  kit.

## Não exigido nesta fase

- O `/golem:comecar`, o `diagnostico` completo, o guia do primeiro dia, o T1 inteiro e a release
  com zip (fase 7).
- As lições gerais no central e o gancho lendo os dois acervos (fase 4).
- O estilo em dois níveis (fase 6) e a preferência dos emojis (fase 5).
- O Codex como plugin (fase 9).
- A sessão aberta numa subpasta do jogo.
- Migrar uma instalação por cópia para o plugin.
