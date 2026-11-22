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

- [x] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem pulados. **N** é 134 (a contagem em `e1483ac`) mais os testes novos dos G1 a G4,
  anotados aqui ao fim de cada grupo. Se a `main` andar, a contagem dela entra no lugar do 134.
  - **G1:** `150 passed`, sem pulados (134 + 16).
  - **G2:** `154 passed`, sem pulados (150 + 4).
  - **G3:** `164 passed`, sem pulados (154 + 10).
  - **G4:** `166 passed`, sem pulados (164 + 2).
  **Saída (2026-11-22):** `166 passed in 72.82s`, sem pulados, no head `f1d52bc` mais a lição do G6 (que não traz teste). A contagem: 134 + 32 (G1 16, G2 4, G3 10, G4 2, G5 0). (`g6-automaticos.txt`)
- [x] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
  **Saída (2026-11-22):** `ok       .claude/indice/licoes.yaml`, com a lição nova (`total: 16`).
- [x] `"$PYR" .claude/golem.py aplicar`, no kit → `nada mudou`, e o `git status --short` continua
  igual: o kit não está no modo plugin (R2).
  **Saída (2026-11-22):** `nada mudou: o AGENTS.md e os agentes já seguem o golem.toml`; o `git status --short` antes e depois, igual.
- [x] `"$CC" plugin validate .` → `Validation passed` (com avisos, lidos e anotados; nenhum erro)
  (R1).
  **Saída (2026-11-22):** `✔ Validation passed with warnings`. Os avisos: o `CLAUDE.md` da raiz (não é lido; é o do desenvolvimento do kit), sem ícone e sem `network.hosts`, do catálogo (`g2-validate.txt`, `g6-automaticos.txt`).
- [x] O teste do G4 que confere que nenhuma skill nem agente cita `.claude/golem.py`,
  `.claude/regua.py`, `.claude/instalar_codex.py` ou `.claude/hooks/` sem o `${CLAUDE_SKILL_DIR}`
  na frente passa, na suíte acima (R4). A busca é pelo arquivo, ocorrência por ocorrência, porque
  há chamadas como `"$PY" .claude/golem.py` e
  `sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"`.
  **Saída (2026-11-22):** passa na suíte acima (`test_nenhuma_skill_nem_agente_chama_um_arquivo_do_kit_pelo_caminho_do_projeto`); a mutação M2 do validador do G4 (uma skill de volta a `python3 .claude/regua.py --gerar`) o fez falhar.
- [x] Numa cópia da árvore (`git archive HEAD`, num `git init` novo):
  `"$PYR" .claude/instalar_codex.py && "$PYR" .claude/instalar_codex.py --conferir` → `ok`, e
  `grep -rn 'CLAUDE_SKILL_DIR' .agents/skills` → nenhuma linha (R4).
  **Saída (2026-11-22):** `24 arquivo(s) mudaram`, `ok       24 arquivos do Codex batem com .claude/`, e 0 linhas com `CLAUDE_SKILL_DIR` nas cópias.
- [x] **A lista do que se copia, no `README.md`** (R5), lida por uma pessoa (o agente, e o
  revisor do G5 confere): em "Instalar o Golem (uma vez)" e "Registrar um jogo", nada se copia à
  mão; em "Usando com o Codex", a lista da cópia bate item por item com a tabela do R5, a
  `.claude/tests/` aparece só como exclusão, e da `docs/` vão só os arquivos nomeados (nunca "a
  pasta `docs/`"). Ajuda: `grep -nE 'a pasta \`(\.claude|docs)/\`|tests' README.md`, e cada
  linha achada lida no contexto.

  **Saída (2026-11-22):** a ajuda acha as linhas 86, 163, 179, 182 e 380, todas como exclusão ou na lista nomeada da cópia. O revisor do G5 conferiu a lista contra a tabela do R5, e o validador do G5 a seguiu como usuário, item por item, na pasta do jogo e no projeto do Codex.
## Verificações sem login (o agente, numa configuração isolada)

O plugin é o worktree da branch, no head do G5. Cada rodada é
`"$CC" -p oi --output-format stream-json --verbose --model haiku`, rodada na pasta do caso, e lê
só o evento `system`/`init` (a lista de plugins, skills e agentes), que sai antes do login. O
`resumo.py` das provas da spec lê o evento. A transcrição de cada rodada fica na pasta de notas
da GER, em `fase-3-provas/`.

- [x] **S1. A instalação:** `"$CC" plugin marketplace add <worktree>` e
  `"$CC" plugin install golem@golem --scope user` → a saída diz "disabled by default", e o
  `"$ISO/cfg/settings.json"` tem `"golem@golem": false` (R1).
  **Saída (2026-11-22):** "This plugin is disabled by default"; `"golem@golem": false` no `settings.json` da configuração à parte (`g6-s1.txt`).
- [x] **S2. O central:** `"$PYR" .claude/golem.py central` → cria `"$ISO/Golem"` com o
  `golem.toml`, o `jogos.md`, a pasta `jogos/` e o "ligado"; sem `CLAUDE.md`. A rodada no central
  → o plugin `golem@golem`, 14 skills `golem:*` e os 2 agentes (cartão 2).
  **Saída (2026-11-22):** `4 arquivo(s) mudaram`, as quatro peças e 0 `CLAUDE.md` (`g6-s2.txt`); a rodada no central lista `golem@golem`, 14 skills e os 2 agentes (`g6-s2-central.jsonl`).
- [x] **S3. Um jogo registrado:** em `"$ISO/Golem/jogos/teste"`, um `git init`, as lições
  (`cp -r <worktree>/docs/licoes docs/`, `git add docs/licoes`) e o índice
  (`"$PYR" <worktree>/.claude/regua.py --gerar`, rodado na pasta do jogo, → `total:` maior que 0);
  depois, `"$PYR" <worktree>/.claude/golem.py registrar "$ISO/Golem/jogos/teste" --nome teste` →
  a linha no `jogos.md`, o "ligado" no `.claude/settings.local.json` (cartão 1) e
  `git check-ignore .claude/settings.local.json` → o caminho (fora do git). Duas rodadas no jogo
  → o plugin, 14 skills e os 2 agentes nas duas.
  **Saída (2026-11-22):** o `registrar` escreveu o `settings.local.json`, o `.gitignore` e o `jogos.md`; o `git check-ignore` deu `.claude/settings.local.json`; as duas rodadas listam o plugin, 14 skills e os 2 agentes (`g6-s3-registrar.txt`, `g6-s3-r1.jsonl`, `g6-s3-r2.jsonl`). As lições do jogo, refeitas em `jogos/teste2` (`g6-s5-s6.txt`), dão `total: 15`.
- [x] **S4. Um projeto fora do registro:** em `"$ISO/outro"`, um `git init`, **as mesmas lições e o
  mesmo índice** do S3 (para que um gancho que rodasse ali tivesse o que injetar). Duas rodadas →
  nem o plugin, nem skill `golem:*`, nem agente `golem:` nas duas.
  **Saída (2026-11-22):** nas duas rodadas, nem o plugin, nem skill, nem agente (`g6-s4-r1.jsonl`, `g6-s4-r2.jsonl`); as mesmas lições e o índice em `outro2`.
- [x] **S5. O gancho do plugin à mão, no jogo** (o comando do `hooks.json`, com o
  `CLAUDE_PLUGIN_ROOT` no worktree e o `CLAUDE_PROJECT_DIR` no jogo do S3, e o JSON de um
  `pytest -q` no stdin) → a lição `suite-verde-so-vale-com-a-linha-de-resumo` vem **do
  `docs/licoes/` do jogo**: tirada do jogo com `git rm` (a régua só vê o que o git rastreia,
  `regua.py:77`) e o índice regerado, ela some da saída, mesmo existindo no kit. Depois, a lição
  volta (nova cópia e `git add`) e o índice se regera, para
  o L1. O mesmo, rodado **sem** o `CLAUDE_PROJECT_DIR` e com a pasta corrente no jogo (como a
  `licao` o roda), dá a mesma lição.
  **Saída (2026-11-22):** com o `CLAUDE_PROJECT_DIR` no jogo e sem ele (pasta corrente no jogo), a lição vem; tirada do jogo com `git rm` (`total: 14`), ela some, embora exista no kit; de volta (`total: 15`), ela vem (`g6-s5-s6.txt`).
- [x] **S6. O `onde`, no jogo:** `cd "$ISO/Golem/jogos/teste" && "$PYR" <worktree>/.claude/golem.py onde`
  → diz o jogo como raiz, o modo plugin, o central em `"$ISO/Golem"` e, com
  `revisor = "nunca"` no `golem.toml` do central, "revisor: nunca (do central)".

  **Saída (2026-11-22):** `modo     plugin: o kit mora em <worktree>`, o central de teste e `revisor: nunca (do central)` (`g6-s5-s6.txt`).
## Verificações com login (o agente, depois do `/login` do autor do kit na configuração isolada)

Rodam só com o sim do autor do kit (`requirements.md`, "Perguntas em aberto"). Sem o sim, ficam
para ele, na configuração dele, com estes mesmos passos, e o PR diz isso. Todas no Haiku.

- [x] **L1. O gancho roda no jogo** (2 rodadas): no jogo do S3, `"$CC" -p` com o Bash liberado,
  pedindo para rodar `python -m pytest --version`. Na transcrição da sessão
  (`"$ISO/cfg/projects/<pasta>/<sessão>.jsonl"`), o `additionalContext` do gancho traz o id
  `suite-verde-so-vale-com-a-linha-de-resumo`.
  **Saída (2026-11-22):** nas duas rodadas, a transcrição traz um anexo `hook_additional_context` do `PreToolUse:Bash` com `**suite-verde-so-vale-com-a-linha-de-resumo**` (`g6-l1-r1.jsonl`, `g6-l1-r2.jsonl`, e as transcrições da configuração à parte).
- [x] **L2. O gancho fora do Golem** (2 rodadas): o mesmo pedido no projeto do S4, que tem as
  mesmas lições e o mesmo índice → a transcrição não tem o texto "Lições registradas" nem o id.
  **Saída (2026-11-22):** nas duas rodadas, nenhum anexo de gancho e nenhum "Lições registradas"; o id só aparece no contexto da sessão, no `git status` que lista os arquivos (`g6-l2-r1.jsonl`, `g6-l2-r2.jsonl`).
- [x] **L3. O `${CLAUDE_SKILL_DIR}`** (1 rodada em cada): pedir a skill `licao` e só o comando da
  régua, sem rodar nada, (a) no jogo, pela skill de plugin `golem:licao`, e (b) numa cópia do kit
  na branch (`git archive`, num `git init` novo), pela skill de projeto `licao` → nas duas
  transcrições, o caminho da pasta da skill no lugar da variável, e nenhum `${CLAUDE_SKILL_DIR}`
  literal.
  **Saída (2026-11-22):** nas duas, a skill carregada traz o caminho absoluto (no jogo, `…/fase-1-configuracao-5e9f91/.claude/skills/licao/../../regua.py`; na cópia do kit, `…/kit-copia/.claude/skills/licao/../../regua.py`), e nenhum `${CLAUDE_SKILL_DIR}` literal (`g6-l3a.jsonl`, `g6-l3b.jsonl`).
- [x] **L4. A subida do `CLAUDE.md`** (1 rodada, sem ferramentas): um `CLAUDE.md` com uma marca,
  posto à mão em `"$ISO/Golem"` só para esta rodada e apagado depois; no jogo de `jogos/`, a
  pergunta "que marca aparece no seu contexto? responda sem ler arquivo" → a marca aparece. Isso
  confirma por que o central nunca tem `CLAUDE.md` (R3).
  **Saída (2026-11-22):** **o contrário do esperado: a marca não apareceu**, em 4 rodadas (o jogo com git, duas vezes no `-p`; uma pasta sem git dentro do central, no `-p`; e o jogo `l5` no modo interativo, depois da confiança), nem no texto que foi ao modelo (`g6-l4.jsonl`, `g6-l4-teste2.jsonl`, `g6-l4-sem-git.jsonl`, `g6-l5.txt`). A decisão do R3 (o central nunca tem `CLAUDE.md`) continua, porque não custa nada; a leitura da documentação era hipótese, e virou a lição `o-claude-md-da-pasta-de-cima-nao-chegou-ao-jogo`.
- [x] **L5. O modo interativo** (1 vez): o `"$CC"` aberto sem `-p`, numa aba do terminal do app,
  numa pasta de jogo registrada e nunca aberta → aparece o diálogo de confiança na pasta; depois
  de aceitar, `/plugin` (ou a pergunta "quais skills golem você tem?") mostra o `golem`. Se o
  agente não conseguir dirigir a tela, o autor do kit faz os mesmos passos e diz o que viu.
  **Saída (2026-11-22):** na primeira abertura do jogo `l5`, o diálogo "Accessing workspace [...] Trusting this folder loads .claude/settings.local.json", com "No, exit" e "Yes, I trust this folder"; o autor do kit aceitou; a resposta: "(1) 14 skills com prefixo golem: · (2) NENHUMA" (`g6-l5.txt`).
- [x] **L6. A `iniciar-sdd` de ponta a ponta** (1 rodada, com as ferramentas liberadas): no
  central do S2, pedir "registrar um jogo", com o nome `l6` e "não tenho pasta" (no `-p`, as
  respostas vão no próprio pedido). Depois, conferir à mão:
  - a pasta `"$ISO/Golem/jogos/l6"`, um repositório git, com cada item da linha "No jogo" da
    tabela do R5 (`ls -R`, item por item);
  - a linha `l6` no `jogos.md` e o "ligado" no jogo;
  - o índice com `total:` maior que 0 (`tail -1 .claude/indice/licoes.yaml`);
  - o bloco "Como o Golem trabalha aqui" no `AGENTS.md` do jogo, com a receita do central;
  - nenhuma `.claude/tests/`, nenhum `docs/plano-produto.md`, nenhum script do kit
    (`golem.py`, `regua.py`, `hooks/`) no jogo.
  **Saída (2026-11-22):** a skill, rodada pelo modelo no central, criou `jogos/l6` (um repositório git) com cada item da linha "No jogo" do R5, o índice `total: 15`, o "ligado" fora do git, o bloco `Receita economico; o guia vem com o kit`, a linha `l6` no `jogos.md`, e nenhum `.claude/tests/`, `docs/plano-produto.md`, script do kit nem `CLAUDE.md` no central (`g6-l6.jsonl`, `g6-l6-conferencia.txt`).
- [x] **L7. O modelo na chamada** (1 rodada): no jogo do S3, pedir que se chame o agente
  `golem:revisor` com `model: haiku` sobre um arquivo pequeno → na transcrição do subagente
  (`"$ISO/cfg/projects/<pasta>/…"`), o modelo das mensagens dele é o Haiku, e não o Opus do
  frontmatter (R4).
  **Saída (2026-11-22):** o `golem:revisor` (frontmatter `model: opus`) chamado com `model: haiku`: todas as mensagens do subagente com `claude-haiku-5-5`, e o uso da sessão só no Haiku (`g6-l7.jsonl`).
- [x] **A limpeza:** `/logout` na configuração isolada e a pasta `"$ISO"` apagada.

  **Saída (2026-11-22):** o `/logout` na aba da L5 ("Successfully logged out"), as duas sessões fechadas, o `.credentials.json` da configuração à parte sumiu, e a pasta à parte foi apagada. O `~/.claude/.credentials.json` real ficou com a data de antes (2026-11-21, 17:15).
## Casos de borda (na suíte, G1 e G3)

- [x] O `CLAUDE_PROJECT_DIR` apontando para uma pasta que não existe → o gancho cai na raiz de
  hoje, sem quebrar.
  **Saída (2026-11-22):** na suíte, `test_plugin_com_claude_project_dir_que_nao_existe_nao_quebra`.
- [x] A régua e o `golem.py` do kit rodados com a pasta corrente fora do kit e fora de um git →
  trabalham na pasta corrente, sem escrever no kit. Quem diz qual é a raiz é o `onde` (G3).
  **Saída (2026-11-22):** na suíte, `test_a_regua_e_o_aplicar_do_kit_fora_de_um_git_trabalham_na_pasta_corrente`.
- [x] Sem central nenhum, no modo plugin → a configuração é a da receita do jogo, sem erro, e o
  gancho entrega a lição.
  **Saída (2026-11-22):** na suíte, `test_plugin_entrega_a_licao_do_jogo_pelo_claude_project_dir` (sem central).
- [x] O `golem.toml` do central com uma linha errada → o `aplicar` do jogo falha dizendo o arquivo
  do central e a linha, e não escreve nada; o gancho segue com o teto padrão (`golem.py:124-129`).
  **Saída (2026-11-22):** na suíte, `test_o_aplicar_do_kit_trabalha_no_jogo_e_acusa_o_central_com_erro` e `test_o_teto_do_gancho_vem_do_central_e_cai_no_padrao_com_erro`.
- [x] O arquivo do "ligado" com JSON quebrado → o `registrar` falha dizendo o arquivo, sem
  escrever.
  **Saída (2026-11-22):** na suíte, `test_o_registrar_com_o_settings_local_quebrado_nao_escreve_nada`.
- [x] O nome do jogo com `|` → recusado.
  **Saída (2026-11-22):** na suíte, `test_o_registrar_recusa_o_nome_com_barra_vertical`.
- [x] O `aplicar --todos` com a pasta de um jogo apagada → avisa esse jogo e aplica nos outros.

  **Saída (2026-11-22):** na suíte, `test_o_aplicar_todos_passa_em_cada_jogo_e_segue_sem_o_que_sumiu` (o jogo do meio).
## A mutação (o validador, numa cópia descartável)

Cada item parte da cópia limpa e deve fazer algum teste falhar. **Saída:** os validadores dos grupos rodaram cada uma, e todas fizeram algum teste falhar: G1 (as 9 da raiz, do central e da ordem), G2 (as 8 do manifesto e do `hooks.json`), G3 (as 10 do `registrar`, do `central`, do `aplicar --todos` e do `onde`, a 6a pega na segunda rodada) e G4 (as 5 das skills e do Codex).

- [x] O `gancho.sh` ignorando o `CLAUDE_PROJECT_DIR`.
- [x] O `licoes_relevantes.py` ignorando o `CLAUDE_PROJECT_DIR`.
- [x] O `gancho.sh` sem `CLAUDE_PROJECT_DIR` usando a posição mesmo quando ela é o plugin.
- [x] A `regua.py` ou o `golem.py` usando a posição no modo plugin.
- [x] O `golem.py` achando o central pelo `Path.home()` antes do `HOME`.
- [x] O `registrar` sem a linha do `.gitignore`.
- [x] A `configuracao` com o central por cima do jogo (a ordem trocada).
- [x] O central lido também fora do modo plugin.
- [x] O `registrar` sem a conferência da pasta repetida.
- [x] O `registrar` sobrescrevendo o arquivo do "ligado" (perdendo as outras chaves).
- [x] O `central` escrevendo um `CLAUDE.md`.
- [x] O `hooks.json` com um `matcher` a menos que o `settings.json`.
- [x] O `instalar_codex.py` sem a troca do `${CLAUDE_SKILL_DIR}`.

## Requisitos da constituição

- [x] Nenhuma dependência nova: só a biblioteca padrão nos scripts, `sh` POSIX no gancho
  (regra 3). `git diff "$BASE" -- '*.py' | grep -E '^\+\s*(import|from) '` → só módulos da
  biblioteca padrão.
  **Saída (2026-11-22):** só `datetime`, `json`, `os`, `subprocess`, `tempfile`, `re`, `shutil` e os módulos da própria suíte (`g6-automaticos.txt`).
- [x] Os arquivos novos do kit com crédito: o `test_credito.py` passa, e o `plugin.json` traz o
  `author`, a `license` e a `homepage`.
  **Saída (2026-11-22):** o `test_credito.py` passa (na suíte), com o `test_plugin.py` na lista; o `test_plugin.py` confere o `author`, a `license` e a `homepage`.
- [x] Nenhum nome de cliente, de outro projeto ou de pessoa além do autor do kit (`AGENTS.md`,
  "Convenções"): o revisor de cada grupo e o guardião leem o diff inteiro procurando nomes, e o
  veredito de cada um diz que leu. Ajuda mecânica:
  `git diff "$BASE" | LC_ALL=C.UTF-8 grep -nP '^\+.*\b\p{Lu}\p{Ll}+ \p{Lu}\p{Ll}+\b'`, cada linha achada lida (a
  lista de nomes de fora não se escreve no repositório).
  **Saída (2026-11-22):** a ajuda acha só nomes de produto ("Claude Code", "Git Bash"), frases ("No Golem", "Sem Python"), o jogo de teste "Meu Jogo" e o nome do autor do kit três vezes, nos lugares de crédito (o `author` do `plugin.json`, o `owner` do `marketplace.json` e a linha de crédito do `test_plugin.py`). O `git clone` do README leva o endereço do repositório do kit, o mesmo da linha de crédito e da `homepage`. Os revisores de cada grupo leram os diffs; o guardião lê o PR.
- [x] O conciliador passa: o `templates/AGENTS.md` e o `AGENTS.md` mudaram juntos (R4).

  **Saída (2026-11-22):** o `test_conciliar.py` passa na suíte, com as duas `PERMITIDAS` novas do G4 (o ferramental e as skills, que no kit moram na `.claude/`).
## Registro

- [x] O `docs/plano-produto.md`, seção 7: a linha da fase 3 marcada como feita, com a branch, a
  spec e a data (pela `validar-fase`).
  **Saída (2026-11-22):** a linha diz "feita: validada em 2026-11-22", com a branch, a spec e o
  tamanho M–G.
- [x] As respostas dos cartões 1 e 2 na spec, com as palavras e a data.
  **Saída (2026-11-22):** no `requirements.md`, "Decisões": "A: settings.local.json (Recomendado)" e "A: na pasta do Golem (Recomendado)", de 2026-11-21.
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
