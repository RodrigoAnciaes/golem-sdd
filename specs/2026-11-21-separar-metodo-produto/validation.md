# Separar o método que usamos do produto que entregamos — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, que não tem pytest e roda a régua.
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`. O `git diff "$BASE"`
  mostra só o que a fase mudou, mesmo depois de a branch trazer a `main` com a fase 2.

## Verificações automatizadas

- [ ] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem pulados.
  - **N** é a contagem da `main` na hora de trazer a branch para ela, mais os 3 testes novos do
    G2.
  - Na `30b87db`, a base, a contagem é `123 passed`: o esperado é `126 passed`.
  - Se a `main` andar (a fase 2 traz testes do gancho), anote aqui a contagem lida nela antes do
    G1. Se um teste mudar de forma na fase, a contagem nova entra aqui e na tabela de alterações
    do `plan.md`.
- [ ] `"$PY" -m pytest .claude/tests/test_conciliar.py -o addopts= -q -p no:cacheprovider -rs` →
  `3 passed`.
- [ ] `"$PY" .claude/golem.py aplicar`, no kit → `nada mudou`, e `git status --short` continua sem
  mudança (R2).
- [ ] `cat golem.toml` → a linha `receita = "completo"` e o comentário, e nada mais (R2).
- [ ] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' AGENTS.md | grep -n 'Receita'` →
  ``Receita `completo` ``. E `grep -n '^model:' .claude/agents/revisor.md .claude/agents/validador.md`
  → `model: opus` nos dois (R2).
- [ ] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' templates/AGENTS.md | grep -n 'Receita'`
  → ``Receita `economico` `` (R1).
- [ ] `grep -c '<<' templates/AGENTS.md` → o mesmo número que `git show "$BASE":AGENTS.md | grep -c '<<'`
  (15 em `30b87db`): as lacunas continuam no modelo (R1).
- [ ] `grep -c '<<' AGENTS.md` → `0`: nenhuma lacuna aberta na raiz, e a frase de abertura do kit
  (R2) não usa `<<`.
- [ ] `grep -n 'O repositório do próprio kit' templates/AGENTS.md AGENTS.md` → só a linha do
  `AGENTS.md` da raiz (R1).
- [ ] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
- [ ] `"$PY" -m pytest .claude/tests/test_credito.py -o addopts= -q -p no:cacheprovider -rs` →
  passa, com o `test_conciliar.py` na lista. Numa cópia, apagar a linha de crédito do
  `test_conciliar.py` faz o teste falhar.

## A mutação do conciliador (R3)

Numa cópia da árvore de trabalho, sem a `.git` (`cp -r` para uma pasta descartável; o
`git archive` não serve antes do commit do grupo), rodando na cópia
`"$PY" -m pytest .claude/tests/test_conciliar.py .claude/tests/test_golem.py -o addopts= -q -p no:cacheprovider`.
Cada item parte da cópia limpa:

- [ ] Trocar uma palavra da regra 4 só no `AGENTS.md` da raiz → falha o
  `test_o_agents_md_do_kit_concilia_com_o_modelo`. A mensagem traz o diff com a linha mudada e diz
  que a MET decide entre o modelo e a `PERMITIDAS`.
- [ ] Trocar a mesma palavra só no `templates/AGENTS.md` → o mesmo teste falha.
- [ ] Apagar do `templates/AGENTS.md` uma linha que uma permitida cita → falha o
  `test_cada_diferenca_permitida_tem_motivo_e_acha_o_trecho`, dizendo qual permitida envelheceu.
- [ ] Repetir no `templates/AGENTS.md` uma linha que uma permitida cita → o mesmo teste falha
  (trecho ambíguo).
- [ ] Deixar vazio o motivo de uma permitida → o mesmo teste falha.
- [ ] Trocar o bloco do `templates/AGENTS.md` pelo da `completo` → falha o
  `test_o_modelo_traz_o_bloco_da_economico`.
- [ ] Apagar a frase de abertura do kit do `AGENTS.md` da raiz → `3 skipped`, com o motivo no
  `-rs`. É o sinal de que, no kit, o pulo só acontece se a frase sumir, e a contagem "0 pulados"
  acima o acusa (regra 8).
- [ ] Mudar uma linha **dentro** do bloco do `AGENTS.md` da raiz → o `test_conciliar.py` passa (o
  bloco fica fora da comparação), e o `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml`
  falha (é ele quem confere o bloco).

## A instalação (R4, R5)

- [ ] **Seguindo só o `README.md` novo**, numa pasta descartável fora do kit, com `git init` e as
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
- [ ] Na mesma pasta, `"$PYR" .claude/instalar_codex.py` e depois `--conferir` → `ok`.
- [ ] Os textos novos estão no lugar:
  - `git grep -n 'templates/AGENTS.md' -- README.md` → o passo 1;
  - `git grep -n 'golem.py aplicar' -- README.md` → o passo 4;
  - `git grep -n 'model: sonnet' -- README.md` → a linha do caso sem Python, no passo 4.
- [ ] O que espera a decisão M1 × M2 ficou como está:
  `git diff "$BASE" --stat -- .claude/skills/iniciar-sdd .claude/tests/test_credito.py`
  → 1 arquivo, o `test_credito.py`.

## Verificações manuais

- [ ] **Pelo `claude -p`, duas rodadas**, numa cópia descartável do head da fase, fora da pasta
  principal: perguntar "que receita vale aqui, e o revisor roda a cada grupo ou por fase?".
  Esperado na transcrição: a `completo`, com o revisor a cada grupo, lida do bloco do `AGENTS.md`,
  sem nada no prompt sobre a receita.
- [ ] **Pelo `claude -p`, uma rodada**, numa pasta descartável instalada pelo `README.md` novo
  (como em "A instalação"): a mesma pergunta. Esperado: a `economico`, com o revisor uma vez por
  fase.

## Casos de borda

- [ ] O fim de linha: `git ls-files --eol AGENTS.md templates/AGENTS.md`. Com `w/crlf` (o caso
  desta máquina, `i/lf w/crlf` em `30b87db`), a suíte normal já roda o conciliador sobre CRLF:
  registre a saída. Com `w/lf`, numa cópia, `sed -i 's/$/\r/' AGENTS.md` → o conciliador passa
  (a leitura é em LF, como o `golem._ler`).
- [ ] Um trecho permitido que aparece duas vezes no modelo → falha (coberto na mutação acima).
- [ ] Um projeto sem `golem.toml` e sem a linha `python` (a instalação acima) → o `aplicar` roda
  com a `economico` e escreve o `sonnet` (`.claude/golem.py:116-121`). Coberto pela instalação
  acima.

## Requisitos da constituição

- [ ] Nenhuma dependência nova: o `test_conciliar.py` importa só a biblioteca padrão e o
  `conftest` (`grep -n '^import\|^from' .claude/tests/test_conciliar.py`).
- [ ] O `golem.py`, o `regua.py` e o gancho não mudam:
  `git diff "$BASE" --stat -- .claude/golem.py .claude/regua.py .claude/hooks` → vazio.
- [ ] Nenhum nome de cliente, de outro projeto ou de pessoa entra no diff. Depois do commit dos
  grupos (sem ele, os arquivos novos não aparecem no `git diff`), o revisor lê as linhas
  acrescentadas (`git diff "$BASE" | grep '^+'`) e diz que não há nenhum. A linha de crédito do
  autor do kit, que já existe, é a exceção.

## Registro

- [ ] `CHANGELOG.md`: o kit ainda não tem um na raiz (`ls CHANGELOG.md` → "No such file"; os
  releases são ideia anotada). Fica como está, salvo se a GER mandar criar.
- [ ] A seção 8 do `docs/plano-produto.md` com a decisão nova (R7), ou o G4 num PR à parte, com a
  decisão da GER registrada no `plan.md`.
- [ ] A GER avisada de que o passo 3 do `roteiro-teste-golem.md` muda depois do merge.
- [ ] As perguntas em aberto do `requirements.md` respondidas ou levadas à GER.

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
