# Fase 4b: o acervo geral de lições — Validação

O contrato de merge da fase. Os comandos rodam da raiz do worktree, no Git Bash.

- `PY` é um Python 3.8+ com pytest. Nesta máquina não há Python no PATH: é o de um `.venv` de outro
  projeto.
- `PYR` é o Python do instalador oficial, sem pytest, que roda a régua, o `golem.py` e o gancho.
- `TMP` é uma pasta descartável no scratchpad da conversa. As verificações manuais rodam numa cópia
  do kit feita ali com `git archive HEAD`, com um central e dois jogos de teste ali dentro, e nunca
  mexem no worktree nem no `~/Golem` da máquina (o `GOLEM_CENTRAL` aponta para `$TMP/Golem`).
- `BASE` é a base comum com a `main`: `git merge-base origin/main HEAD`.

## Verificações automatizadas

- [x] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → `N passed`, sem
  falhas nem puladas. **N** é 209 (a contagem em `53625f6`) mais os testes novos dos G1 a G3,
  anotados aqui ao fim de cada grupo. Se a `main` andar, a contagem dela entra no lugar do 209.
  - G1: 13 novos (12 no `test_gancho.py`, 1 no `test_regua.py`) → `222 passed in 105.02s`.
  - G2: 22 novos (no `test_golem.py`, um deles com 5 casos) → `244 passed`.
  - G3: 7 novos (no `test_regua.py`) → `251 passed in 136.47s`.
  - O nome comum (a decisão do cartão, depois do G3): 1 novo (no `test_golem.py`) → 252.
  - G5, em `ba4d722`: `252 passed in 139.73s (0:02:19)`, sem falhas nem puladas.
  - Do guardião (dois jogos com o mesmo id): 1 novo (no `test_regua.py`) → `253 passed in
    142.35s (0:02:22)`.
- [x] `"$PYR" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`,
  sai 0, sem nenhuma linha `AVISO`. Em `ba4d722`: a única linha é `ok       .claude/indice/licoes.yaml`, `rc=0`.
- [x] `git diff "$BASE"..HEAD --stat -- .claude/indice/ docs/licoes/*.md` → vazio, fora o
  `docs/licoes/README.md`: a fase não cria nem muda lição do kit. Saiu só `docs/licoes/README.md | 10 ++++++++++`.
- [x] `wc -w AGENTS.md templates/AGENTS.md` → os dois abaixo de 3.000: `2604` e `2552`.
- [x] `git diff "$BASE"..HEAD --name-only | grep -v -e '^specs/' -e '^docs/licoes/README\.md$' -e '^\.claude/' -e '^README\.md$' -e '^docs/guia-configuracao\.md$'`
  → vazio: a fase não mexe fora do que a spec cita. Vazio.

## Verificações manuais

Quem executa: o agente, pelo Git Bash, com a saída colada aqui (M1 a M4). As saídas do gancho vêm em
JSON; aqui entra o `additionalContext` decodificado.

**A árvore**, para M1 a M4:
1. `git archive HEAD | tar -x -C "$TMP/kit"` (com o `.claude-plugin/plugin.json`, que põe o kit no
   modo plugin).
2. `export GOLEM_CENTRAL="$TMP/Golem"`, e `"$PYR" "$TMP/kit/.claude/golem.py" central`.
3. Dois jogos, `$TMP/jogo-a` e `$TMP/jogo-b`, cada um com `git init`, registrados pelo
   `golem.py registrar <pasta> --nome <nome>`, e o `jogo-c` registrado com `--terceiros`. Em cada um,
   `docs/licoes/` com uma lição própria, o `git add docs` e o `--gerar` da régua do kit.

**Resultado, em `ba4d722`** (o `$TMP` no scratchpad, `git archive HEAD`; as saídas abaixo, com o
caminho do `$TMP` encurtado): M1 a M4 passaram.
- M1.1: o `subir` deu os três `escrito` (a lição, o `licoes.yaml` e o `subidas.txt` do central),
  `rc=0`; o `git status` do `jogo-a` não mostra a lição (só o `.gitignore` do `registrar`).
- M1.2, no `jogo-b`: "Lições do acervo geral para esta ação (…/Golem/docs/licoes/ — armadilhas que
  valem para todo jogo, no Golem central): **datastore-sem-pcall** (armadilha): sinal de
  datastore-sem-pcall." Com a sessão `m1` do comando abaixo, o gancho não deu nada: a marca
  `claude-licoes-m1` do temp era de uma rodada anterior dos validadores, com o mesmo id; com uma
  sessão nova (`g5m1`), a saída acima. É a deduplicação por sessão, como desenhada.
- M1.3, no `jogo-a` (sessão `g5m1a`): "Lições registradas para esta ação (docs/licoes/ — …
  neste projeto): **datastore-sem-pcall**", uma vez só, no bloco do jogo.
- M2.1: `ERRO este jogo é para terceiros (um estúdio ou outra pessoa): nada dele vai ao acervo
  geral, …`. M2.2: `ERRO o texto cita 'jogo-a', o nome do jogo ou da pasta dele. … rode de novo com
  --palavra-comum …`. M2.3: `ERRO a ref 'src/moedas.lua' cita um arquivo do jogo`. M2.4: `ERRO …
  já existe no acervo geral: para trocá-la, rode de novo com --substituir`. M2.5: `ERRO fora do modo
  plugin não há Golem central`. Todas com `rc=1` e "Nada foi escrito", e a impressão do central
  inteiro igual antes e depois (`c7824357e5c1`). O nome comum: a do item 2 com o `--palavra-comum`
  subiu (três `escrito`, `rc=0`); a do item 3 com ele continuou recusada pela ref. O `onde`:
  `para terceiros: não` no `jogo-a`, `para terceiros: sim (um estúdio ou outra pessoa: …)` no
  `jogo-c`.
- M3 (sessão `g5m3`): nada sai.
- M4: 1, `ok`, `rc=0`, sem aviso; 2, `AVISO datastore-sem-pcall: a lição deste jogo mudou desde a
  subida ao acervo geral (docs/licoes/… e …/Golem/docs/licoes/…). Para pôr em dia, …
  --substituir …`, `rc=0`; 3, depois do `subir --substituir`, só o `ok`; 4, `AVISO …: a versão
  geral mudou desde a subida …`, `rc=0`.

**De novo em `4780e59`** (as correções do guardião: o `subidas.txt` com a pasta do jogo), o M1 e
o M4, numa árvore nova: M1.1, três `escrito`, e a linha do `subidas.txt` com o id, as duas
impressões e a pasta; M1.2, no `jogo-b`, o bloco "Lições do acervo geral" com a
`**datastore-sem-pcall**`; M4.1, nenhum aviso; M4.2, `AVISO … a lição deste jogo mudou desde a
subida`; M4.3, depois do `--substituir`, nenhum aviso; M4.4, `AVISO … a versão geral mudou (à mão,
ou subida de novo por outro jogo)`, `rc=0`.

1. **A subida e a lição em outro jogo (R2, R4).**
   1. No `jogo-a`, uma lição `datastore-sem-pcall` com o gatilho `\bcomando-geral\b`, sem nada do
      jogo. Com a pasta corrente no `jogo-a`: `"$PYR" "$TMP/kit/.claude/golem.py" subir docs/licoes/datastore-sem-pcall.md`.
      **Deve sair** o `escrito` do `$TMP/Golem/docs/licoes/datastore-sem-pcall.md` e do índice do
      central, e a lição do `jogo-a` fica igual (`git status` limpo nela).
   2. Rode o gancho no `jogo-b`:
      `echo '{"session_id":"m1","tool_input":{"command":"comando-geral"}}' | CLAUDE_PROJECT_DIR="$TMP/jogo-b" sh "$TMP/kit/.claude/hooks/gancho.sh"`.
      **Deve sair** o `**datastore-sem-pcall**` no bloco do acervo geral, com o sinal da lição.
   3. O mesmo no `jogo-a` (sessão `m1a`): **deve sair** a lição uma vez só, no bloco do jogo.
2. **As recusas do subir (R3, R4).** Cada uma **deve sair** com `ERRO`, o motivo, e nada escrito
   (`ls "$TMP/Golem/docs/licoes"` igual antes e depois):
   1. no `jogo-c` (para terceiros), a mesma lição: o motivo diz "para terceiros", sem a palavra
      "cliente";
   2. no `jogo-a`, uma lição com o nome `jogo-a` no corpo, em maiúsculas (`JOGO-A`);
   3. no `jogo-a`, uma lição com a ref `'src/moedas.lua:3 \`local x\`'`, com o arquivo criado no
      `jogo-a`;
   4. no `jogo-a`, de novo a `datastore-sem-pcall`, sem o `--substituir`;
   5. no repositório do kit (fora do modo plugin), qualquer lição.

   E o nome comum: no `jogo-a`, a recusa do item 2 **deve dizer** a saída (`--palavra-comum`);
   rodada de novo com ela (numa lição do `jogo-a` que ainda não subiu, ou com o `--substituir`),
   a lição **deve subir**, e a do item 3 com ela **deve continuar**
   recusada pela ref.

   E o `onde`, com a pasta corrente em cada jogo, **deve dizer** `não` na linha "para terceiros" no
   `jogo-a` e `sim` no `jogo-c`.
3. **Fora do modo plugin, o geral não chega (R2).** O repositório do kit tem o manifesto do plugin,
   mas a raiz é o próprio kit, e aí não há modo plugin. Com a pasta corrente no worktree:
   `echo '{"session_id":"m3","tool_input":{"command":"comando-geral"}}' | CLAUDE_PROJECT_DIR="$PWD" GOLEM_CENTRAL="$TMP/Golem" sh .claude/hooks/gancho.sh`.
   **Não deve sair** a `datastore-sem-pcall`, embora o `$TMP/Golem` a tenha.
4. **A divergência (R5).** No `jogo-a`, depois do M1:
   1. `"$PYR" "$TMP/kit/.claude/regua.py" --conferir`, com a pasta corrente no `jogo-a`: **não deve
      sair** `AVISO` sobre a `datastore-sem-pcall`;
   2. acrescente uma linha ao corpo da lição do `jogo-a` e rode de novo: **deve sair** o `AVISO`
      com as duas pastas, e a régua sai 0;
   3. suba a versão geral de novo com o `--substituir` e rode de novo: o aviso **some**;
   4. mude à mão o `$TMP/Golem/docs/licoes/datastore-sem-pcall.md` e rode de novo: **deve sair**
      o `AVISO`.

**Com login** (L1; o autor do kit entra na configuração isolada, como na fase 3, se topar; sem
isso, fica no "Não exigido"):

1. No central da configuração isolada, sem a linha `jogos_para_terceiros`, peça "registrar um
   jogo". **Deve aparecer** a pergunta "Você costuma fazer jogos para estúdios ou outras
   pessoas?", com botões. Com "não": nenhuma pergunta por jogo, a linha "se este jogo for de um
   estúdio ou de outra pessoa, me diga" no relato, e a linha `jogos_para_terceiros = "nao"` no
   `golem.toml` do central. Um segundo registro **não deve** repetir a pergunta geral.
2. Com a linha passada a `"sim"`, um terceiro registro: **deve aparecer** a pergunta por jogo, com o
   texto do R3; com "para outra pessoa", o jogo entra no `jogos.md` com `sim`.
3. Num jogo registrado que não é para terceiros, peça "registre essa lição" sobre uma armadilha da
   plataforma, sem nada do jogo. **Deve aparecer**, depois do commit, a pergunta de copiar ao
   acervo geral, com botões, dizendo que todos os jogos o leem; com o sim, a segunda pergunta traz
   o texto reescrito; com o segundo sim, o `subir` roda e a lição aparece em `~/Golem/docs/licoes/`
   da configuração isolada.
4. No mesmo jogo, uma lição que só existe por causa dele (a chave do save deste jogo): **não deve
   aparecer** a pergunta, e a skill diz em uma linha que ela fica só no jogo, e por quê.
5. No jogo para terceiros, a lição do item 3: **não deve aparecer** a pergunta, e a skill diz em uma
   linha que nada deste jogo vai ao acervo geral. Em nenhum dos itens a palavra "cliente" aparece
   na tela.

## Casos de borda

- [x] O índice do geral cortado ou ilegível: o gancho varre o Markdown do geral, com o aviso que
  aponta o geral, e o do jogo segue pelo índice dele (teste do G1).
- [x] A pasta do geral ausente (o central sem subida nenhuma): a saída do gancho é a de hoje (teste
  do G1).
- [x] O registro antigo, de três colunas: lido, com `não`, e passado a quatro na primeira escrita
  (teste do G2).
- [x] O `golem.toml` do central sem a linha `jogos_para_terceiros`: vale `nao`; com um valor fora de
  `sim`/`nao`: o erro com a linha (teste do G2).
- [x] Só a troca de `\n` por `\r\n` na lição do jogo: nenhum aviso de divergência (teste do G3).
- [x] O `subir` com um arquivo que não existe, ou com o frontmatter que a régua recusa: `ERRO`, nada
  escrito (teste do G2).
- [x] A sessão aberta no próprio central: um acervo só (teste do G1).

## Requisitos da constituição

- [x] Nenhuma dependência nova: só a biblioteca padrão no Python e `sh` POSIX no gancho
  (`git diff "$BASE"..HEAD -- .claude/ | grep '^+import\|^+from'` mostra só módulos da biblioteca
  padrão). Saíram `hashlib`, `importlib.util`, `shutil`, `tempfile` e os `from conftest` dos testes.
- [x] Nenhum nome de cliente, de outro projeto ou de pessoa além do autor do kit, fora do crédito:
  os exemplos usam nomes genéricos (`jogo-a`, `datastore-sem-pcall`).
- [x] A palavra "cliente" não aparece em texto que o usuário lê: a última busca do G4 no
  `plan.md`, com cada linha achada sendo um nome interno do código. Achou só a ordem ao agente
  (`iniciar-sdd`, "nunca 'cliente'") e as Restrições antigas da `licao` (segredo de cliente).
- [x] As cópias do Codex não se versionam no kit: `git diff "$BASE"..HEAD --name-only -- .agents .codex`
  → vazio. Vazio.
- [x] Revisor e validador por grupo, no Opus; o guardião sobre o diff inteiro antes do PEDIDO. Os
  G1 a G4 e os dois commits do nome comum (`f4e9b7a`, `1479840`) tiveram revisor e validador, cada
  um até "sem bloqueio" e "valida" (o G4 pelo caminho completo, depois dos achados importantes).
  O guardião, em `8b14b43`, deu "com bloqueio": o `subidas.txt` com uma linha por id fazia dois
  jogos com o mesmo id se atropelarem. Corrigido com uma linha por id e jogo, e um teste novo.

## Registro

- [ ] O `CHANGELOG.md` do kit, se a `validar-fase` o pedir.
- [ ] A linha da 4b na seção 7 (`docs/plano-produto.md:621`), marcada pela `validar-fase`; o resto
  do roteiro é da GER.
- [ ] As perguntas em aberto do `requirements.md` respondidas ou levadas ao roteiro.

## Não exigido nesta fase

- As regras de área gerais, o estilo em dois níveis e o T1 (fases 6 e 7).
- O histórico do acervo geral no git.
- Descer ou apagar uma lição geral por comando.
- O Codex com o acervo geral.
- A rodada com login L1, se o autor do kit não topar entrar na configuração isolada; aí as
  perguntas novas da `iniciar-sdd` e o passo novo da `licao` ficam provados pela leitura do revisor
  e pelos comandos que eles chamam (M1 a M4).
- Mudar a resposta geral por uma skill, e levar a pergunta geral ao `/golem:comecar` (fase 7).
