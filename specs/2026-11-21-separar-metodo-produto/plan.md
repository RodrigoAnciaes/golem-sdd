# Separar o método que usamos do produto que entregamos — Plano

O fluxo desta fase é o completo, pelo prompt da GER, porque o kit ainda não tem o `golem.toml`
dele: revisor e validador, os dois no Opus, a cada grupo, e o guardião sobre o diff do PR. O G1
cria esse `golem.toml`, e a partir dele o bloco do `AGENTS.md` da raiz passa a dizer o mesmo.

**Antes do G1:**

1. o PR 2 da MET mergeado na `main`: cumprido (PR 5, `30b87db`, a base desta branch);
2. a ordem do autor do kit nesta conversa;
3. a branch trazida para a `main` do momento, se ela tiver andado; as linhas citadas na spec,
   reconferidas. Com a fase 2 mergeada, o G1 parte dos agentes e do `test_golem.py` dela
   (`requirements.md`, "Perguntas em aberto");
4. a GER avisada dos arquivos comuns: `AGENTS.md`, `README.md`, `templates/` e `.claude/tests/`.

## G1 — O modelo e a raiz do kit (R1, R2, e o `copia_do_kit` do R6)

- [ ] `templates/AGENTS.md`: copiar o `AGENTS.md` da `main` e tirar a frase do kit
  (`AGENTS.md:108-109` em `30b87db`).
- [ ] `.claude/tests/conftest.py`: o `copia_do_kit` copia o `templates/AGENTS.md` como
  `AGENTS.md`, com recuo ao `AGENTS.md` da raiz quando o modelo não existe (R6). A docstring
  muda junto (`:150-151`, `:156`).
- [ ] `golem.toml` na raiz: `receita = "completo"` e o comentário de uma linha.
- [ ] `python .claude/golem.py aplicar`: o bloco da `completo` no `AGENTS.md` da raiz e
  `model: opus` nos dois agentes. Ler a saída: `2 arquivo(s) mudaram` (o `AGENTS.md` e o
  revisor; o validador já está em `opus`, `validador.md:5`).
- [ ] O `AGENTS.md` da raiz com o texto do R2.
- [ ] A suíte inteira, com a linha de resumo lida: `123 passed` (nenhum teste novo no G1). O
  `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml` passa contra a `completo`, e o
  `test_segunda_rodada_do_aplicar_nao_muda_nada` passa com a cópia partindo do modelo.

**Revisão:** revisor e validador sobre o diff do grupo.

## G2 — O conciliador (R3)

- [ ] `.claude/tests/test_conciliar.py`, com a linha de crédito, a `PERMITIDAS` (um trio por
  diferença do G1, cada uma com o motivo) e três testes:
  - `test_o_agents_md_do_kit_concilia_com_o_modelo`;
  - `test_cada_diferenca_permitida_tem_motivo_e_acha_o_trecho`;
  - `test_o_modelo_traz_o_bloco_da_economico`.

  O módulo se pula, com o motivo, quando o `AGENTS.md` da raiz não traz a frase de abertura do kit
  (R3).
- [ ] `.claude/tests/test_credito.py`: o caminho novo na `ARQUIVOS_DO_KIT`.
- [ ] A mutação do `validation.md` ("A mutação do conciliador"), numa cópia da árvore de trabalho.

**Revisão:** revisor e validador sobre o diff do grupo.

## G3 — A instalação mínima e a varredura (R4, R5, R6)

Só as duas linhas que a separação obriga (decisão 5). O resto do que viaja espera a decisão
M1 × M2.

- [ ] `README.md`, "Instalar num projeto":
  - o passo 1 (`:99`): o `AGENTS.md` é o `templates/AGENTS.md`, copiado como `AGENTS.md` (R5);
  - o passo 4: o `aplicar` junto da régua, o `git add .claude/agents` depois dele e a linha do caso
    sem Python (R4).
- [ ] A docstring de `test_golem.py:202-203`.
- [ ] A busca do que ainda trata o `AGENTS.md` da raiz como o modelo que o usuário copia:

  ```bash
  git grep -n -e 'o que o usuário copia' -e 'AGENTS.md` do kit' -- '*.md' '*.py'
  git grep -n 'AGENTS.md' -- 'docs/*.md' '.claude/*.md' 'WORKFLOW.md' 'README.md'
  ```

  Corrigir só as linhas que dizem que o `AGENTS.md` da raiz é o modelo. As que falam da cópia
  inteira da `.claude/` e da `docs/` continuam certas até a decisão M1 × M2. Nas specs das fases
  feitas (`specs/2026-11-*`), nada muda: elas registram o que era verdade na época. A lição
  `o-grep-do-git-for-windows-aborta-com-i-e-varios-e` vale aqui: não juntar `-i` com vários `-e`.
- [ ] O recado à GER: o passo 3 do `roteiro-teste-golem.md` (copiar o `templates/AGENTS.md` e rodar
  o `aplicar`) muda depois do merge.

**Revisão:** revisor e validador sobre o diff do grupo. O grupo é quase só documentação, mas o
caminho completo vale para a fase toda.

## G4 — As decisões no plano de produto (R7)

Só depois do merge da fase 2. Se ela não tiver mergeado quando o G3 fechar, a GER decide se este
grupo vai num PR à parte.

- [ ] `docs/plano-produto.md`, seção 8: a decisão nova, com as palavras do autor do kit (as cinco
  respostas e as duas de antes, que estão no `requirements.md`, "Decisões"). Ela diz que a 7
  ("Econômica no kit") e a "Completo pelo prompt" deixam de valer.
- [ ] As frases que dizem que o kit roda na `economico`, no mesmo arquivo
  (`git grep -n "economico" docs/plano-produto.md`).

**Revisão:** revisor e validador sobre o diff do grupo.

## G5 — Verificação

- [ ] O `validation.md` inteiro, com a saída colada.
- [ ] O guardião: o `revisor`, numa conversa ou subagente novo, sobre o diff inteiro do PR.
- [ ] A spec e o código reconciliados.

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Decidido por |
|---|---|---|---|

## Estado para a retomada

A spec foi escrita em 2026-11-21 e revisada duas vezes; depois veio a decisão 5 (instalação
mínima até a decisão M1 × M2). Aprovada pelo autor do kit em 2026-11-21: "Aprovo
(Recomendado)". Ainda não há código: o G1 espera a ordem dele nesta conversa.
