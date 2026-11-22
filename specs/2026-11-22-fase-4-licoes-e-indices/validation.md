# Fase 4: lições e índices — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, sem pytest, que roda a régua e o gancho.
- `TMP` é uma pasta descartável no scratchpad da conversa. As verificações manuais rodam numa cópia
  do kit feita ali com `git archive HEAD`, e nunca mexem no worktree.
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`.

**Rodado em 2026-11-22**, no head `7460564` (o G3 commitado), com `BASE` = `421b7b6` (a `main` com o
PR 13 do roteiro, trazida pelo merge `60a849d`). As saídas estão abaixo de cada item.

## Verificações automatizadas

- [x] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem puladas. **N** é 166 (a contagem em `746ebf7`) mais os testes novos dos G1 e G2,
  anotados aqui ao fim de cada grupo. Se a `main` andar, a contagem dela entra no lugar do 166.
  - G1: 8 testes novos, 174 no total (`174 passed in 72.66s`).
  - G2: 34 testes novos, 208 no total (`208 passed in 80.53s`), com as correções do revisor e do
    validador e o cartão 5.
  - G3: só documentação, nenhum teste novo. A `main` nova (PR 13) só mudou o
    `docs/plano-produto.md`, e a contagem segue 166 na base.

  Saída: `208 passed in 78.70s (0:01:18)`.
- [x] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`,
  sai 0, e o stderr não traz nenhuma linha `AVISO` de ref nem do teto (as refs do kit em dia, e o
  `AGENTS.md` do kit abaixo do teto).

  Saída: `  ok       .claude/indice/licoes.yaml` e `rc=0`, sem nenhuma outra linha.
- [x] `git diff "$BASE"..HEAD --stat -- .claude/indice/` → vazio. O índice não guarda as `refs:`, e
  nenhuma lição muda de id, área, tipo, data, gatilho ou gatilhos nesta fase. A linha `origem: kit`
  do cartão 5 também não entra no índice.

  Saída: vazia.
- [x] `wc -w AGENTS.md templates/AGENTS.md` → os dois abaixo de 3.000 (o teto padrão do R3; o
  `golem.toml` do kit não traz a linha `agents_teto`).

  Saída: `2604 AGENTS.md` e `2552 templates/AGENTS.md`.
- [x] `"$PYR" -c "import sys; sys.path.insert(0, '.claude'); import golem; print(sorted({r['agents_teto'] for r in golem.RECEITAS.values()}))"`
  → `[3000]`.

  Saída: `[3000]`.
- [x] `git diff "$BASE"..HEAD --name-only | grep -v -e '^specs/' -e '^docs/' -e '^\.claude/' -e '^AGENTS\.md$' -e '^templates/AGENTS\.md$'`
  → vazio: a fase não mexe fora do que a spec cita.

  Saída: vazia.

## Verificações manuais

Quem executa: o agente, pelo Git Bash, com a saída colada aqui. Rodadas numa cópia do head `7460564`
(`git archive HEAD`, com `git init` e um commit), pelo script do scratchpad da conversa. As saídas
do gancho vêm em JSON; abaixo, o `additionalContext` decodificado.

1. **A lição fora do índice chega, com o aviso uma vez (R1).**
   1. Copie o kit para `$TMP/kit` (`git archive HEAD | tar -x -C "$TMP/kit"`), rode `git init`,
      `git add -A` e o `--gerar` ali.
   2. Crie `docs/licoes/licao-de-teste.md`, com um `gatilhos:` que casa com `\bcomando-de-teste\b`, e
      **não** regere o índice.
   3. Rode o gancho com a ação, numa sessão de teste:
      `echo '{"session_id":"v1","tool_input":{"command":"comando-de-teste"}}' | CLAUDE_PROJECT_DIR="$TMP/kit" sh "$TMP/kit/.claude/hooks/gancho.sh"`.
      **Deve sair** o `**licao-de-teste**` e o aviso "índice defasado" com o id.
   4. Rode de novo, com a mesma sessão e o comando `ls`. **Não deve sair** o aviso.
   5. Rode `git add docs/licoes/licao-de-teste.md` e o `--gerar` e, numa sessão nova
      (`"session_id":"v2"`), o mesmo comando do passo 3. **Deve sair** a lição, **sem** o aviso.

   ✓ Passo 3: "⚠️ O índice de lições (`.claude/indice/licoes.yaml`) está defasado: 1 lição(ões) de
   `docs/licoes/` fora dele (licao-de-teste). Elas chegam mesmo assim, lidas do Markdown. [...]" e
   "- **licao-de-teste** (armadilha): sinal da licao-de-teste.". Passo 4: saída vazia. Passo 5:
   `escrito  .claude/indice/licoes.yaml` e só "- **licao-de-teste** (armadilha): sinal da
   licao-de-teste.", sem o aviso.
2. **A ref deslocada sai com a linha nova (R2).** Na mesma cópia, ponha uma linha em branco no topo
   de um arquivo citado com linha e âncora por uma lição do kit, e rode o `--conferir`. **Deve
   sair** uma linha `AVISO` com o id da lição, a ref e "a âncora está agora na `:K`", com o K
   certo, e o código de saída **0**.

   ✓ Com a linha em branco no topo do `.claude/tests/test_codex.py`, o `grep -n` dá as funções na
   `249` e na `284`, e o `--conferir` deu, com `rc=0`:
   ```
   AVISO    frontmatter-invalido-some-com-o-agente-sem-aviso: a ref .claude/tests/test_codex.py:283: a âncora `def test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido` está agora na :284
   AVISO    o-windows-muda-o-que-o-sh-recebe-do-python: a ref .claude/tests/test_codex.py:248: a âncora `def test_lancador_sem_o_proprio_caminho_acha_a_raiz_pelo_git` está agora na :249
   ok       .claude/indice/licoes.yaml
   ```
3. **O `AGENTS.md` acima do teto (R3).**
   1. Na mesma cópia, acrescente ao `AGENTS.md` palavras até passar de 3.000 (`wc -w`) e rode o
      `--conferir`. **Deve sair** o `AVISO` com o número de palavras, o teto 3000, a saída pelo
      `docs/regras-de-area.md` e a linha `agents_teto`, e o código de saída **0**.
   2. Acrescente ao `golem.toml` da cópia uma linha `agents_teto` acima do número de palavras e
      rode o `--conferir`. **Não deve sair** o aviso.
   3. Troque a linha por `agents_teto = "muito"` e rode o `--conferir`. **Deve sair** o aviso com o
      teto 3000, e o `golem.py aplicar` **deve recusar** a linha, com o número dela.

   ✓ 3.1, com 3.051 palavras: "AVISO    AGENTS.md tem 3051 palavras, acima do teto de 3000. Ele
   entra inteiro em toda conversa: a regra que só vale para quem mexe numa área vai ao
   docs/regras-de-area.md (a regra 7 e a skill `licao`). O teto é a linha `agents_teto` do
   golem.toml.", e `rc=0`. 3.2, com `agents_teto = 3100`: só o `ok`, `rc=0`. 3.3: o mesmo aviso,
   com o teto de 3000, e `rc=0`; o `aplicar` deu "ERRO     golem.toml:3: `agents_teto` vale
   'muito'; o aceito é um número de 1 em diante, sem aspas" e "Nada foi escrito.", com `rc=1`.
4. **As lições do kit no jogo, no modo plugin (R2).**
   1. Crie `$TMP/jogo` com `git init` e copie para `docs/licoes/` as lições da cópia do kit, como a
      `iniciar-sdd` faz.
   2. Confira que `$TMP/kit/.claude-plugin/plugin.json` existe (ele vem no `git archive` desde a
      fase 3): é ele que põe a régua no modo plugin.
   3. Rode `"$PYR" "$TMP/kit/.claude/regua.py" --conferir` com a pasta corrente em `$TMP/jogo`.

   **Não deve sair** nenhum `AVISO` de ref que aponte um arquivo do kit.

   ✓ O `ls .claude-plugin/plugin.json` acha o arquivo. Depois do `git add docs` e do `--gerar`
   (`escrito  .claude/indice/licoes.yaml`, `rc=0`), o `--conferir` deu só "AVISO
   .claude/indice/licoes.yaml não está no git" (o índice recém-gerado, esperado) e o `ok`, com
   `rc=0`. Nenhum aviso de ref.
5. **A instalação por cópia (R2, cartão 5).** Copie para `$TMP/copia` o que o `README.md` manda
   copiar ("Instalar por cópia": a `.claude/` sem a `.claude/tests/`, a `docs/licoes/` e o
   `templates/AGENTS.md` como `AGENTS.md`), rode `git init`, `git add -A` e o `--conferir` ali.
   **Não deve sair** nenhum `AVISO` de ref. Depois, numa lição do jogo (sem `origem: kit`), ponha a
   ref `'.claude/tests/x.py'` e rode o `--conferir`: **deve sair** o `AVISO` "o arquivo não existe".

   ✓ A cópia não tem `specs/` nem `.claude/tests/`, e o `--conferir` deu só o `ok`, com `rc=0`.
   Com a `licao-do-jogo` e a ref `'.claude/tests/x.py'`, saiu "AVISO    licao-do-jogo: a ref
   .claude/tests/x.py: o arquivo não existe". O mesmo `--conferir` deu também `DIVERGE`, com
   `rc=1`, porque a lição nova não estava no índice. Esse resultado é esperado e não vem do aviso.

## Casos de borda

- [x] Um `docs/licoes/` sem lição nenhuma e sem índice: o gancho não avisa e não cai (o teste de
  hoje continua passando). Prova: o `test_sem_arquivo_de_regras_nada_muda` e os de entrada vazia,
  na suíte de 208. O validador do G1 também rodou o gancho numa pasta só com o README e numa sem
  `docs/`: `rc=0` e 0 bytes nas duas.
- [x] Uma lição fora do índice com o frontmatter inválido: o gancho a entrega pela área, ou não a
  entrega, e não cai. A régua a acusa, como hoje. Prova: o
  `test_licao_fora_do_indice_com_frontmatter_invalido_nao_derruba`, o
  `test_pasta_com_nome_de_licao_nao_derruba` e o `test_licao_fora_do_indice_vale_pelo_nome_do_arquivo`.
  O validador do G1 rodou três arquivos inválidos: o gancho deu `rc=0`, e o `--conferir`, `rc=1`,
  com `INVÁLIDO` para os três.
- [x] Uma ref com a âncora em mais de uma linha: vale a primeira depois da linha citada. Sem ela,
  vale a primeira do arquivo. O aviso diz uma linha só. Prova: os casos `alvo.py:3` (→ `:4`) e
  `alvo.py:4-4` (→ `:1`) do `test_a_ref_que_nao_bate_da_o_aviso`, e a rodada do validador do G2
  com um `src.lua` com a âncora nas linhas 2, 4 e 6.
- [x] Um `AGENTS.md` ausente na raiz: nenhum aviso do teto. Prova: o
  `test_sem_agents_nao_ha_aviso_do_teto` e, na verificação 4, o jogo sem `AGENTS.md`.
- [x] No modo plugin, a `agents_teto` só no `golem.toml` do central: vale para o jogo, e a do jogo
  vence a do central. Prova: o `test_no_plugin_o_teto_do_central_vale_e_o_do_jogo_vence` e a
  tabela de cinco casos do validador do G2.
- [x] A marca da sessão ilegível: o aviso do R1 sai a cada ação, como as lições (degrada para
  avisar, nunca para calar). Prova: na cópia do head, com o `scratchpad_dir` apontando um arquivo
  e sem `session_id`, três ações `ls` seguidas deram as três "defasado: 1 lição(ões) de
  `docs/licoes/` fora dele (nova)".

## Requisitos da constituição

- [x] Nenhuma dependência nova: só a biblioteca padrão no gancho e na régua (regra 3). Prova:
  `git diff "$BASE"..HEAD -- .claude/hooks .claude/regua.py .claude/golem.py` não traz nenhuma
  linha `import` ou `from` nova.
- [x] A linha de crédito continua em todo arquivo que a tinha (`test_credito.py`, na suíte).
  Prova: o `test_credito.py` passa, dentro dos 208.
- [x] O conciliador passa sem entrada nova em `PERMITIDAS` (a regra 7 igual nos dois `AGENTS.md`).
  Prova: o `git diff "$BASE"..HEAD --stat -- .claude/tests/test_conciliar.py` sai vazio, e o
  `test_conciliar.py` passa.
- [ ] Nenhum nome de cliente, de outro projeto ou de pessoa nos arquivos da fase:
  `git diff "$BASE"..HEAD` lido pelo guardião.

## Registro

- [x] `docs/plano-produto.md`, seção 7: a fase 4 marcada como feita, com a branch e a spec (pela
  `validar-fase`).
- [x] A decisão 13 na seção 8 (R5), escrita no lugar do item "Reservada" do PR 13. A seção 8 numera
  de 1 a 14, sem buraco.
- [x] A tabela "Alterações de escopo" do `plan.md` em dia.

## Não exigido nesta fase

- O acervo geral no central, a subida das lições e o projeto de cliente marcado (cartão 1; é a
  fase 4b, decisão 14).
- Conferir que a linha citada ainda diz o mesmo: a âncora mostra que o trecho continua ali, e não
  o sentido.
- Uma rodada com login no Claude Code: o gancho e a régua se provam pelo `sh` e pelo Python, como
  na `licao` (passo 5).
- O `CHANGELOG.md`: o kit não tem um na raiz.
