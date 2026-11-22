# Fase 4: lições e índices — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, sem pytest, que roda a régua e o gancho.
- `TMP` é uma pasta descartável no scratchpad da conversa. As verificações manuais rodam numa cópia
  do kit feita ali com `git archive HEAD`, e nunca mexem no worktree.
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`.

## Verificações automatizadas

- [ ] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem puladas. **N** é 166 (a contagem em `746ebf7`) mais os testes novos dos G1 e G2,
  anotados aqui ao fim de cada grupo. Se a `main` andar, a contagem dela entra no lugar do 166.
  - G1: 8 testes novos, 174 no total (`174 passed in 72.66s`).
  - G2: 34 testes novos, 208 no total (`208 passed in 80.53s`), com as correções do revisor e do
    validador e o cartão 5.
- [ ] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`,
  sai 0, e o stderr não traz nenhuma linha `AVISO` de ref nem do teto (as refs do kit em dia, e o
  `AGENTS.md` do kit abaixo do teto).
- [ ] `git diff "$BASE"..HEAD --stat -- .claude/indice/` → vazio. O índice não guarda as `refs:`, e
  nenhuma lição muda de id, área, tipo, data, gatilho ou gatilhos nesta fase.
- [ ] `wc -w AGENTS.md templates/AGENTS.md` → os dois abaixo de 3.000 (o teto padrão do R3; o
  `golem.toml` do kit não traz a linha `agents_teto`).
- [ ] `"$PYR" -c "import sys; sys.path.insert(0, '.claude'); import golem; print(sorted({r['agents_teto'] for r in golem.RECEITAS.values()}))"`
  → `[3000]`.
- [ ] `git diff "$BASE"..HEAD --name-only | grep -v -e '^specs/' -e '^docs/' -e '^\.claude/' -e '^AGENTS\.md$' -e '^templates/AGENTS\.md$'`
  → vazio: a fase não mexe fora do que a spec cita.

## Verificações manuais

Quem executa: o agente, pelo Git Bash, com a saída colada aqui.

1. **A lição fora do índice chega, com o aviso uma vez (R1).**
   1. Copie o kit para `$TMP/kit` (`git archive HEAD | tar -x -C "$TMP/kit"`), rode `git init`,
      `git add -A` e o `--gerar` ali.
   2. Crie `docs/licoes/licao-de-teste.md`, com um `gatilhos:` que casa com `\bcomando-de-teste\b`, e
      **não** regere o índice.
   3. Rode o gancho com a ação, numa sessão de teste:
      `echo '{"session_id":"v1","tool_input":{"command":"comando-de-teste"}}' | CLAUDE_PROJECT_DIR="$TMP/kit" sh "$TMP/kit/.claude/hooks/gancho.sh"`.
      **Deve sair** o `**licao-de-teste**` e o aviso "índice defasado" com o id.
   4. Rode de novo, com a mesma sessão e o comando `ls`. **Não deve sair** o aviso.
   5. Rode `git add docs/licoes/licao-de-teste.md` e o `--gerar` e, numa sessão nova (`"session_id":"v2"`), o mesmo comando do passo 3.
      **Deve sair** a lição, **sem** o aviso.
2. **A ref deslocada sai com a linha nova (R2).** Na mesma cópia, ponha uma linha em branco no topo
   de um arquivo citado com linha e âncora por uma lição do kit, e rode o `--conferir`. **Deve
   sair** uma linha `AVISO` com o id da lição, a ref e "a âncora está agora na `:K`", com o K
   certo, e o código de saída **0**.
3. **O `AGENTS.md` acima do teto (R3).**
   1. Na mesma cópia, acrescente ao `AGENTS.md` palavras até passar de 3.000 (`wc -w`) e rode o
      `--conferir`. **Deve sair** o `AVISO` com o número de palavras, o teto 3000, a saída pelo
      `docs/regras-de-area.md` e a linha `agents_teto`, e o código de saída **0**.
   2. Acrescente ao `golem.toml` da cópia uma linha `agents_teto` acima do número de palavras e
      rode o `--conferir`. **Não deve sair** o aviso.
   3. Troque a linha por `agents_teto = "muito"` e rode o `--conferir`. **Deve sair** o aviso com o
      teto 3000, e o `golem.py aplicar` **deve recusar** a linha, com o número dela.
4. **As lições do kit no jogo, no modo plugin (R2).**
   1. Crie `$TMP/jogo` com `git init` e copie para `docs/licoes/` as lições da cópia do kit, como a
      `iniciar-sdd` faz.
   2. Confira que `$TMP/kit/.claude-plugin/plugin.json` existe (ele vem no `git archive` desde a
      fase 3): é ele que põe a régua no modo plugin.
   3. Rode `"$PYR" "$TMP/kit/.claude/regua.py" --conferir` com a pasta corrente em `$TMP/jogo`.

   **Não deve sair** nenhum `AVISO` de ref que aponte um arquivo do kit.
5. **A instalação por cópia (R2, cartão 5).** Copie para `$TMP/copia` o que o `README.md` manda
   copiar ("Instalar por cópia": a `.claude/` sem a `.claude/tests/`, a `docs/licoes/` e o
   `templates/AGENTS.md` como `AGENTS.md`), rode `git init`, `git add -A` e o `--conferir` ali.
   **Não deve sair** nenhum `AVISO` de ref. Depois, numa lição do jogo (sem `origem: kit`), ponha a
   ref `'.claude/tests/x.py'` e rode o `--conferir`: **deve sair** o `AVISO` "o arquivo não existe".

## Casos de borda

- [ ] Um `docs/licoes/` sem lição nenhuma e sem índice: o gancho não avisa e não cai (o teste de
  hoje continua passando).
- [ ] Uma lição fora do índice com o frontmatter inválido: o gancho a entrega pela área, ou não a
  entrega, e não cai. A régua a acusa, como hoje.
- [ ] Uma ref com a âncora em mais de uma linha: vale a primeira depois da linha citada. Sem ela,
  vale a primeira do arquivo. O aviso diz uma linha só.
- [ ] Um `AGENTS.md` ausente na raiz: nenhum aviso do teto.
- [ ] No modo plugin, a `agents_teto` só no `golem.toml` do central: vale para o jogo, e a do jogo
  vence a do central.
- [ ] A marca da sessão ilegível: o aviso do R1 sai a cada ação, como as lições (degrada para
  avisar, nunca para calar).

## Requisitos da constituição

- [ ] Nenhuma dependência nova: só a biblioteca padrão no gancho e na régua (regra 3).
- [ ] A linha de crédito continua em todo arquivo que a tinha (`test_credito.py`, na suíte).
- [ ] O conciliador passa sem entrada nova em `PERMITIDAS` (a regra 7 igual nos dois `AGENTS.md`).
- [ ] Nenhum nome de cliente, de outro projeto ou de pessoa nos arquivos da fase:
  `git diff "$BASE"..HEAD` lido pelo guardião.

## Registro

- [ ] `docs/plano-produto.md`, seção 7: a fase 4 marcada como feita, com a branch e a spec (pela
  `validar-fase`).
- [ ] A decisão 13 na seção 8 (R5).
- [ ] A tabela "Alterações de escopo" do `plan.md` em dia.

## Não exigido nesta fase

- O acervo geral no central, a subida das lições e o projeto de cliente marcado (cartão 1).
- Conferir que a linha citada ainda diz o mesmo: a âncora mostra que o trecho continua ali, e não
  o sentido.
- Uma rodada com login no Claude Code: o gancho e a régua se provam pelo `sh` e pelo Python, como
  na `licao` (passo 5).
- O `CHANGELOG.md`: o kit não tem um na raiz.
