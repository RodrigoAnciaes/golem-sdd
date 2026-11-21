# Separar o método que usamos do produto que entregamos — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, que não tem pytest e roda a régua.
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`. O `git diff "$BASE"`
  mostra só o que a fase mudou, mesmo depois de a branch trazer a `main` com a fase 2.

## Verificações automatizadas

- [x] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem pulados.
  - **N** é a contagem da `main` na hora de trazer a branch para ela, mais os 3 testes novos do
    G2.
  - Na `30b87db`, a base, a contagem é `123 passed`: o esperado é `126 passed`.
  - Se a `main` andar (a fase 2 traz testes do gancho), anote aqui a contagem lida nela antes do
    G1. Se um teste mudar de forma na fase, a contagem nova entra aqui e na tabela de alterações
    do `plan.md`.
  - **Saída (2026-11-21, com a `main` `49ef7c1`):** `126 passed in 64.67s`, sem pulados. A `main` `49ef7c1` tem 123: os PRs 6 e 7 não trouxeram teste.
- [x] `"$PY" -m pytest .claude/tests/test_conciliar.py -o addopts= -q -p no:cacheprovider -rs` →
  `3 passed`.
  **Saída:** `3 passed in 0.03s`.
- [x] `"$PY" .claude/golem.py aplicar`, no kit → `nada mudou`, e `git status --short` continua sem
  mudança (R2).
  **Saída:** `nada mudou: o AGENTS.md e os agentes já seguem o golem.toml`; o `git status --short` antes e depois, igual.
- [x] `cat golem.toml` → a linha `receita = "completo"` e o comentário, e nada mais (R2).
  **Saída:** o comentário `# golem.toml do repositório do kit: [...] Não viaja ao usuário.` e `receita = "completo"`.
- [x] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' AGENTS.md | grep -n 'Receita'` →
  ``Receita `completo` ``. E `grep -n '^model:' .claude/agents/revisor.md .claude/agents/validador.md`
  → `model: opus` nos dois (R2).
  **Saída:** ``6:Receita `completo` ``, `12:- **Parar a cada parte:** nunca: siga grupo a grupo.`, `revisor.md:5:model: opus`, `validador.md:5:model: opus`; `golem.teto_do_gancho()` → `4`.
- [x] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' templates/AGENTS.md | grep -n 'Receita'`
  → ``Receita `economico` `` (R1).
  **Saída:** ``6:Receita `economico` ``.
- [x] `grep -c '<<' templates/AGENTS.md` → o mesmo número que `git show "$BASE":AGENTS.md | grep -c '<<'`
  (15 em `30b87db`): as lacunas continuam no modelo (R1).
  **Saída:** `15` e `15` (com `BASE` = `49ef7c1`).
- [x] `grep -c '<<' AGENTS.md` → `0`: nenhuma lacuna aberta na raiz, e a frase de abertura do kit
  (R2) não usa `<<`.
  **Saída:** `0`.
- [x] `grep -n 'O repositório do próprio kit' templates/AGENTS.md AGENTS.md` → só a linha do
  `AGENTS.md` da raiz (R1).
  **Saída:** só `AGENTS.md:114`.
- [x] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
  **Saída:** `  ok       .claude/indice/licoes.yaml`.
- [x] `"$PY" -m pytest .claude/tests/test_credito.py -o addopts= -q -p no:cacheprovider -rs` →
  passa, com o `test_conciliar.py` na lista. Numa cópia, apagar a linha de crédito do
  `test_conciliar.py` faz o teste falhar.
  **Saída:** `2 passed`; na cópia sem a linha, o validador do G2 leu `.claude/tests/test_conciliar.py: 0 linha(s) de crédito, esperada 1`, `1 failed, 1 passed`.

## A mutação do conciliador (R3)

Numa cópia da árvore de trabalho, sem a `.git` (`cp -r` de `.claude`, `AGENTS.md`, `templates`,
`docs` e `golem.toml` para uma pasta descartável; sem o `golem.toml`, vale a `economico` e o
`test_golem.py` já falha na cópia limpa; o `git archive` não serve antes do commit do grupo), rodando na cópia
`"$PY" -m pytest .claude/tests/test_conciliar.py .claude/tests/test_golem.py -o addopts= -q -p no:cacheprovider`.
Cada item parte da cópia limpa:

- [x] Trocar uma palavra da regra 4 só no `AGENTS.md` da raiz → falha o
  `test_o_agents_md_do_kit_concilia_com_o_modelo`. A mensagem traz o diff com a linha mudada e diz
  que a MET decide entre o modelo e a `PERMITIDAS`.
- [x] Trocar a mesma palavra só no `templates/AGENTS.md` → o mesmo teste falha.
- [x] Apagar do `templates/AGENTS.md` uma linha que uma permitida cita → falha o
  `test_cada_diferenca_permitida_tem_motivo_e_acha_o_trecho`, dizendo qual permitida envelheceu.
- [x] Repetir no `templates/AGENTS.md` uma linha que uma permitida cita → o mesmo teste falha
  (trecho ambíguo).
- [x] Deixar vazio o motivo de uma permitida → o mesmo teste falha.
- [x] Trocar o bloco do `templates/AGENTS.md` pelo da `completo` → falha o
  `test_o_modelo_traz_o_bloco_da_economico`.
- [x] Apagar a frase de abertura do kit do `AGENTS.md` da raiz → `3 skipped`, com o motivo no
  `-rs`. É o sinal de que, no kit, o pulo só acontece se a frase sumir, e a contagem "0 pulados"
  acima o acusa (regra 8).
- [x] Mudar uma linha **dentro** do bloco do `AGENTS.md` da raiz → o `test_conciliar.py` passa (o
  bloco fica fora da comparação), e o `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml`
  falha (é ele quem confere o bloco).

**Saída (validador do G2, segunda rodada, 2026-11-21):** a cópia limpa, `21 passed`. Itens 1 e 2: `1 failed, 20 passed`, com o diff da linha e a instrução à MET. Item 3: `PERMITIDAS[13] [...] aparece 0 vez(es)`. Item 4: `aparece 2 vez(es)`. Item 5: `PERMITIDAS[9]: sem motivo`. Item 6: falha o `test_o_modelo_traz_o_bloco_da_economico`. Item 7: `18 passed, 3 skipped`, com os três motivos. Item 8: só o `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml` falha. A `PERMITIDAS` ganhou depois uma entrada (o achado 3 do guardião); a suíte com ela, `126 passed`.

## A instalação (R4, R5)

- [x] **Seguindo só o `README.md` novo**, numa pasta descartável fora do kit, com `git init` e as
  cópias que o passo 1 lista, a partir de uma cópia do head da fase:
  - `grep -n 'Receita' AGENTS.md` → `economico`, e `grep -c '<<' AGENTS.md` → o mesmo número do
    `templates/AGENTS.md` do kit (é o modelo, e não o `AGENTS.md` do kit);
  - depois do passo 4, `grep -n '^model:' .claude/agents/revisor.md` → `model: sonnet`, e
    `git diff --stat -- .claude/agents` → vazio (a troca está no stage);
  - na mesma pasta, `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → sem
    falhas. Os 3 do `test_conciliar.py` aparecem pulados, com o motivo "não é o repositório do
    kit". Isso vale com e sem a `templates/` copiada: rode uma vez com ela e outra depois de
    `rm -rf templates` (o recuo do `copia_do_kit`, R6);
  - os passos 4 e 5 do `README.md` dão o que eles dizem: o `ok` da régua e a lição no JSON do
    gancho.
  **Saída:** (validador do G3, 2026-11-21) ``69:Receita `economico` ``, `15` lacunas; `aplicar` → `escrito  .claude/agents/revisor.md`, `1 arquivo(s) mudaram.`; `5:model: sonnet`, `git diff --stat -- .claude/agents` vazio; a régua `ok`, `total: 9`; o gancho com `suite-verde-so-vale-com-a-linha-de-resumo`; a suíte `123 passed, 3 skipped` com a `templates/` e depois do `rm -rf templates`, os 3 do conciliador com o motivo; depois de um `git commit` comum, `git show HEAD:.claude/agents/revisor.md` → `model: sonnet`. O caso sem Python, à mão, dá o mesmo blob que o `aplicar`.
- [x] Na mesma pasta, `"$PYR" .claude/instalar_codex.py` e depois `--conferir` → `ok`.
  **Saída:** `ok       24 arquivos do Codex batem com .claude/`.
- [x] Os textos novos estão no lugar:
  - `git grep -n 'templates/AGENTS.md' -- README.md` → o passo 1;
  - `git grep -n 'golem.py aplicar' -- README.md` → o passo 4;
  - `git grep -n 'model: sonnet' -- README.md` → a linha do caso sem Python, no passo 4.
  **Saída:** `README.md:99`, `README.md:133` e `README.md:142`.
- [x] O que espera a decisão M1 × M2 ficou como está:
  `git diff "$BASE" --stat -- .claude/skills/iniciar-sdd .claude/tests/test_credito.py`
  → 1 arquivo, o `test_credito.py`.
  **Saída:** `.claude/tests/test_credito.py | 1 +`, `1 file changed`.

## Verificações manuais

- [x] **Pelo `claude -p`, duas rodadas**, numa cópia descartável do head da fase, fora da pasta
  principal: perguntar "que receita vale aqui, e o revisor roda a cada grupo ou por fase?".
  Esperado na transcrição: a `completo`, com o revisor a cada grupo, lida do bloco do `AGENTS.md`,
  sem nada no prompt sobre a receita.
  **Saída:** (`claude -p --model sonnet`, 2026-11-21; transcrições `kit-rodada1.jsonl` e `kit-rodada2.jsonl` em `separacao-prova-claude-p/`, na pasta de notas da GER) as duas responderam "Receita: `completo`, definida em `golem.toml:2` e [...] no bloco [...] do `AGENTS.md:75`" e "Revisor: roda a cada grupo [...] (`AGENTS.md:77`)". O prompt só perguntava; não citava receita.
- [x] **Pelo `claude -p`, uma rodada**, numa pasta descartável instalada pelo `README.md` novo
  (como em "A instalação"): a mesma pergunta. Esperado: a `economico`, com o revisor uma vez por
  fase.
  **Saída:** (`proj-rodada1.jsonl`) "Receita: `economico`, segundo `AGENTS.md:69` [...]" e "Revisor: roda uma vez por fase, antes da verificação [...] com o modelo `sonnet`".

## Casos de borda

- [x] O fim de linha: `git ls-files --eol AGENTS.md templates/AGENTS.md`. Com `w/crlf` (o caso
  desta máquina, `i/lf w/crlf` em `30b87db`), a suíte normal já roda o conciliador sobre CRLF:
  registre a saída. Com `w/lf`, numa cópia, `sed -i 's/$/\r/' AGENTS.md` → o conciliador passa
  (a leitura é em LF, como o `golem._ler`).
  **Saída:** `i/lf w/crlf` nos dois; a suíte normal já roda sobre CRLF (`126 passed`). O validador do G2 também passou com os dois em LF e com um em cada.
- [x] Um trecho permitido que aparece duas vezes no modelo → falha (coberto na mutação acima).
- [x] Um projeto sem `golem.toml` e sem a linha `python` (a instalação acima) → o `aplicar` roda
  com a `economico` e escreve o `sonnet` (`.claude/golem.py:116-121`). Coberto pela instalação
  acima.

## Requisitos da constituição

- [x] Nenhuma dependência nova: o `test_conciliar.py` importa só a biblioteca padrão e o
  `conftest` (`grep -n '^import\|^from' .claude/tests/test_conciliar.py`).
  **Saída:** `difflib`, `pathlib`, `pytest`, `conftest`.
- [x] O `golem.py`, o `regua.py` e o gancho não mudam:
  `git diff "$BASE" --stat -- .claude/golem.py .claude/regua.py .claude/hooks` → vazio.
  **Saída:** vazio.
- [x] Nenhum nome de cliente, de outro projeto ou de pessoa entra no diff. Depois do commit dos
  grupos (sem ele, os arquivos novos não aparecem no `git diff`), o revisor lê as linhas
  acrescentadas (`git diff "$BASE" | grep '^+'`) e diz que não há nenhum. A linha de crédito do
  autor do kit, que já existe, é a exceção.
  **Saída:** o guardião (2026-11-21): "o único nome de pessoa é a linha de crédito".

## Registro

- [x] `CHANGELOG.md`: o kit ainda não tem um na raiz (`ls CHANGELOG.md` → "No such file"; os
  releases são ideia anotada). Fica como está, salvo se a GER mandar criar.
  **Saída:** `ls: cannot access 'CHANGELOG.md'`.
- [x] A seção 8 do `docs/plano-produto.md` com a decisão nova (R7), ou o G4 num PR à parte, com a
  decisão da GER registrada no `plan.md`.
  **Feito:** o G4 sai da fase e vai ao PR do replanejar (a GER, opção (a)); o texto em `separacao-g4-secao-8.md`, na pasta de notas da GER.
- [x] A GER avisada de que o passo 3 do `roteiro-teste-golem.md` muda depois do merge.
  **Feito:** o recado à GER em 2026-11-21.
- [x] As perguntas em aberto do `requirements.md` respondidas ou levadas à GER.
  **Feito:** a ordem (cumprida), o `README.md` (sem conflito até agora) e os agentes (a fase 2 ainda não mergeou: quem mergear depois resolve) estão com a GER; o número da fase é do replanejar.

## Não exigido nesta fase

- O que mais viaja ao usuário, até a decisão M1 × M2 (decisão 5): a `.claude/` sem os testes, a
  `docs/` só com o produto, a `templates/` obrigatória, o "Mapa das pastas" e a `iniciar-sdd`
  usando o modelo.
- O zip, o plugin e a release.
- Separar as lições do kit das de exemplo, e tirar do índice que viaja as lições do kit: fase 4.
- Preencher as lacunas do `docs/operacao-das-conversas.md` para o kit.
- Que o conciliador compare outro arquivo além do `AGENTS.md`.
- Um aviso para o modelo apagado: o conciliador só roda no kit, onde o arquivo existe.
- A linha desta fase no roteiro (seção 7): é da GER, depois do merge da fase 2.
