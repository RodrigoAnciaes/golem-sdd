# Fase 0: o gancho acha o Python — Validação

O contrato de merge da fase. `PY` é um Python 3.8+ com pytest. Nesta máquina, é o de um `.venv` de
outro projeto: não há Python no PATH, e o Python do instalador não tem pytest. Os comandos rodam
da raiz do worktree, no Git Bash.

## Verificações automatizadas

- [ ] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → **`93 passed`**,
  sem falhas nem pulados: os 76 de antes e os 17 novos do `plan.md` (9 no G1, 8 no G2). Se um teste
  mudar de forma na fase, a contagem nova entra aqui e na tabela de alterações do `plan.md`.
- [ ] Os 17 testes novos, cada um pelo nó, passam. Exemplo:
  `"$PY" -m pytest ".claude/tests/test_gancho.py::test_lancador_usa_a_linha_python" -o addopts= -q -p no:cacheprovider`
  → `1 passed`. Os nomes estão no `plan.md`, G1 e G2.
- [ ] `"$PY" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
- [ ] Numa cópia descartável dos arquivos rastreados: `"$PY" .claude/instalar_codex.py` e depois
  `--conferir` → `ok`, e `.agents/skills/diagnostico/SKILL.md` existe na cópia.
- [ ] `sh -n .claude/hooks/gancho.sh` → sem saída, código 0; e `git ls-files --eol
  .claude/hooks/gancho.sh` → `i/lf w/lf`.
- [ ] `git check-ignore -v golem.local.toml` → aponta para a linha do `.gitignore`.
- [ ] O `test_credito.py` passa com `diagnostico` na lista. Numa cópia, apagar a linha `license:`
  da skill nova faz o teste falhar.

## Verificações manuais

Nesta máquina, em que o Python está fora do PATH (só os atalhos da loja no PATH):

1. Sem `golem.local.toml`, rodar
   `echo '{"tool_input":{"command":"where python"}}' | sh .claude/hooks/gancho.sh` (sem
   `session_id`, para poder repetir). Esperado: um JSON com a lição
   `sem-python-no-path-nao-e-maquina-sem-python` e sem `systemMessage`. O gancho achou o Python
   pelo passo 5.
2. Abrir uma sessão nova do Claude Code no worktree e pedir qualquer edição. Esperado: nenhum aviso
   "Gancho das lições falhou".
3. Pedir "diagnóstico do Golem" e responder "Não" à pergunta do Python. Esperado: a skill diz que
   achou um Python em `...\Python312\python.exe` e pergunta se usa. Com "sim", o
   `golem.local.toml` da pasta principal ganha a linha `python = '...'`, e o teste final do gancho
   mostra a lição.
4. Pedir o diagnóstico de novo, responder "Sim, e sei onde" e colar o caminho de um Python de um
   `.venv` de outro projeto. Esperado: a skill testa, grava e o teste final mostra a lição.
5. Este passo exige o terminal, porque o app desktop não muda a variável por sessão. No Git Bash,
   na raiz do worktree, abrir o Claude Code com `LOCALAPPDATA="$(mktemp -d)" claude`, pedir o
   diagnóstico e responder "Sim, mas não sei onde". Esperado: a skill diz que não achou nenhum
   Python e dá o comando de instalação do `winget`, com o id conferido no G3.

## Casos de borda

- [ ] O caminho com aspa simples (`C:\O'Brien\python.exe`) colado na skill → ela recusa e pede
  outro, e o `golem.local.toml` não muda.
- [ ] "Sim, e sei onde" com um caminho que não roda → a skill diz isso e oferece a busca, sem
  gravar.
- [ ] A linha `python` apontando para um arquivo que não existe, sem nenhum outro Python → o aviso
  diz que a linha `python` não roda (teste 13).
- [ ] O `golem.local.toml` em CRLF e com comentário depois da aspa → a linha é lida (teste 4).
- [ ] A entrada do gancho sem `session_id` → o aviso sai em toda ação (teste 12).
- [ ] Os ids hostis → nada fora da pasta temporária (teste 15).
- [ ] O `LOCALAPPDATA` vazio e o `PROGRAMFILES` ausente → o aviso sai, sem erro de `sh` (teste 9).

## Requisitos da constituição

O kit não tem `specs/tech-stack.md`. Valem o README ("Requisitos") e o `AGENTS.md`.

- [ ] Nenhuma dependência nova:
  - o `gancho.sh` só usa recursos embutidos do `sh` e os utilitários que já usa (`dirname`,
    `date`, `git`, `printf`). Conferir com a leitura do diff do `gancho.sh`;
  - `git diff f912da6 -- .claude/hooks/licoes_relevantes.py` sai vazio.
- [ ] Os arquivos novos do kit trazem a linha de crédito (`test_credito.py`).
- [ ] Nenhum caminho pessoal no repositório:
  `git grep -nE '[A-Za-z]:[\\/]Users[\\/][^<.]|/[a-z]/Users/[^<.]'` sem resultado.

## Registro

- [ ] `docs/plano-produto.md`: a fase 0 marcada como feita, com a data e a branch.
- [ ] As perguntas em aberto do `requirements.md` respondidas ou movidas para o plano.

## Não exigido nesta fase

- Os lugares de costume do macOS e do Linux (decisão 1A).
- O modo sem Python (`gancho = "desligado"`), o `golem.toml` e as receitas: fase 1.
- O aviso quando a linha `python` não roda mas outro Python é achado: fica em silêncio.
- Conferir se o arquivo da lição existe antes de citá-lo (decisão 5A).
- Limpar as marcas velhas do aviso.
- O diagnóstico completo (o `sh`, o git, o índice, o Studio MCP): fase 4.
- O teste com o Codex de verdade: só o instalador numa cópia.
- O `CHANGELOG.md`: o kit não tem um, e criá-lo fica para a fase 6 (produto: versões e notas).
