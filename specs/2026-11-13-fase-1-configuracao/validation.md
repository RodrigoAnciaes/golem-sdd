# Fase 1: configuração e receita econômica — Validação

O contrato de merge da fase. `PY` é um Python 3.8+ com pytest. Nesta máquina, não há Python no
PATH: é o de um `.venv` de outro projeto, e o Python do instalador não tem pytest. Os comandos rodam
da raiz do worktree, no Git Bash.

## Verificações automatizadas

- [x] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → **`123 passed`**,
  sem falhas nem pulados: os 96 de antes e os 27 novos do `plan.md` (17 no G2, contando os 3 casos
  do teste parametrizado, 8 no G3, 1 no G5 e 1 no G6, o do frontmatter). Se um teste mudar de
  forma na fase, a contagem nova entra aqui e na tabela de alterações do `plan.md`.
- [x] Os testes novos, cada um pelo nó, passam. Exemplo:
  `"$PY" -m pytest ".claude/tests/test_golem.py::test_sem_golem_toml_vale_a_economico" -o addopts= -q -p no:cacheprovider`
  → `1 passed`. Os nomes estão no `plan.md`, G2, G3 e G5.
- [x] `"$PY" .claude/golem.py aplicar`, rodado no kit → diz que nada mudou, e `git status --short`
  continua sem mudança: o `AGENTS.md` e os dois agentes já estão como o `aplicar` os gera (R10).
- [x] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' AGENTS.md | wc -c` → no máximo 1200
  (R4).
- [x] `grep -n '^model:' .claude/agents/revisor.md .claude/agents/validador.md` →
  `revisor.md:...:model: sonnet` e `validador.md:...:model: opus` (a `economico`, R3).
- [x] `"$PY" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
- [x] Numa cópia descartável dos arquivos rastreados: `"$PY" .claude/instalar_codex.py` e depois
  `--conferir` → `ok`, e `.agents/skills/configurar/SKILL.md` existe na cópia.
- [x] `sh -n .claude/hooks/gancho.sh` → sem saída, código 0; e
  `git ls-files --eol .claude/hooks/gancho.sh` → `i/lf w/lf`.
- [x] O Python 3.8: `"$PY" -c "import ast,sys; [ast.parse(open(f,encoding='utf-8').read(), f, feature_version=(3,8)) for f in sys.argv[1:]]" .claude/golem.py .claude/hooks/licoes_relevantes.py`
  → sem saída, código 0. E `grep -c '^from __future__ import annotations' .claude/golem.py` → `1`:
  a sintaxe do 3.8 não pega anotações como `dict[str, str]`, que quebram no 3.8 sem essa linha
  (o `instalar_codex.py:22` e o `regua.py:31` a usam). No `licoes_relevantes.py`, que não tem
  essa linha: `git diff 1f9f827 -- .claude/hooks/licoes_relevantes.py | grep -nE '^\+.*(-> *|: *)(dict|list|tuple|set)\['`
  → sem resultado.
- [x] O `test_credito.py` passa com `configurar` na lista. Numa cópia, apagar a linha `license:`
  da skill nova faz o teste falhar.
- [x] O aviso do worktree saiu da `diagnostico` (R1):
  `git grep -n -e 'vence a da pasta' -e 'worktree tiver' -e 'raiz/golem.local' -e 'show-toplevel' .claude/skills/diagnostico/SKILL.md`
  → só a linha do passo 7 (o teste do gancho, que usa o `show-toplevel` para achar o
  `gancho.sh`); e `git grep -n 'check-ignore' .claude/skills/diagnostico` → a linha do passo 1
  continua.

## Verificações manuais

**O projeto de teste.** O agente prepara, numa pasta que o autor do kit escolher, fora do kit: um
repositório git com o kit instalado pelo `README.md` a partir do head da fase, sem `golem.toml`, e
uma fase de teste pequena já especificada (a constituição e a spec aprovadas, com dois grupos de
uma função cada). O autor do kit abre cada sessão nova do Claude Code, no app desktop, com essa
pasta como pasta do projeto.

1. **A `economico`, sem `golem.toml`.** Pedir "implementar a fase". Esperado:
   - ao fim do grupo 1, o agente mostra o diff e uma linha do que mudou, e o turno acaba esperando
     o ok, sem revisor;
   - com o ok, ele faz o grupo 2 e, ao fim, roda **um** revisor sobre o diff da fase inteira, e
     nenhum validador;
   - na pasta das transcrições do projeto de teste
     (`~/.claude/projects/<pasta do projeto>/<sessão>/subagents/`), há uma transcrição de
     subagente só, e `grep -o '"model":"[^"]*"' <transcrição> | sort | uniq -c` mostra só modelos
     `claude-sonnet-*`.
   - A conferir: o Sonnet depende da resposta do primeiro usuário sobre o Pro (R3). Se ela mudar
     as receitas, este critério muda junto, com o ok do autor do kit.
2. **O `perguntar`.** No projeto de teste, pôr `revisor = "perguntar"` no `golem.toml`, rodar
   `"$PY" .claude/golem.py aplicar`, voltar a fase de teste ao começo (o agente prepara) e, numa
   sessão nova, pedir "implementar a fase". Esperado: ao fim do último grupo, uma pergunta com
   botões, que diz o custo ("abre 1 conversa extra"). Respondendo "não", nenhuma transcrição de
   subagente nova aparece.
3. **A skill `configurar`, de ponta a ponta.** Numa sessão nova, pedir "configurar o Golem" e
   responder: a receita `completo`, o revisor `nunca`, parar a cada parte "sim". Esperado:
   - `cat golem.toml` → `receita = "completo"`, `revisor = "nunca"` e
     `parar_a_cada_parte = "sempre"`, e nenhuma outra chave;
   - a skill mostra a saída do `aplicar` e diz que vale numa conversa nova;
   - `sed -n '/golem:inicio/,/golem:fim/p' AGENTS.md` → o bloco da `completo` com o revisor
     `nunca` e o parar a cada parte `sempre`;
   - `grep -n '^model:' .claude/agents/*.md` → os dois com `opus`.
4. **O gancho desligado, sem Python.** No projeto de teste, com `gancho = "desligado"` no
   `golem.toml`, num `sh` do Git Bash com o `LOCALAPPDATA` e o `PROGRAMFILES` em pastas vazias e
   `PATH=/usr/bin:/mingw64/bin`:
   `echo '{"session_id":"t1","tool_input":{"command":"pytest -q"}}' | sh .claude/hooks/gancho.sh; echo "rc=$?"`
   → só `rc=0`, e o `.claude/gancho-falhas.log` não ganha linha. Depois, numa sessão nova com a
   mesma linha, pedir uma edição qualquer: nenhum aviso "Gancho das lições falhou".
5. **O aviso do que fica sem revisão, na `economico`.** No projeto de teste, sem `golem.toml`,
   numa sessão nova, pedir "configurar o Golem" e responder: a receita `economico`, o revisor
   "Nunca", parar a cada parte "Sim". Esperado:
   - a descrição do "Nunca", na segunda chamada, diz "Sem revisão, ninguém além desta conversa
     lê o que foi feito; os comandos do `validation.md` continuam rodando.";
   - o texto da pergunta de gravar traz o `golem.toml` inteiro, com os comentários;
   - `cat golem.toml` → `receita = "economico"` e `revisor = "nunca"`, e nenhuma outra chave;
   - a saída do `aplicar` → só `escrito  AGENTS.md` e `1 arquivo(s) mudaram`;
   - `sed -n '/golem:inicio/,/golem:fim/p' AGENTS.md` → o bloco da `economico` com
     `- **Revisor:** nunca.`;
   - `grep -n '^model:' .claude/agents/*.md` → `revisor.md:5:model: sonnet` e
     `validador.md:5:model: opus`.

## Casos de borda

- [x] O `golem.toml` com uma chave escrita errada (`revisr = "nunca"`) →
  `"$PY" .claude/golem.py aplicar` sai com código diferente de 0, a mensagem traz o número da linha
  e a chave, e `git status --short` não mostra mudança no `AGENTS.md` nem nos agentes (teste 12 do
  G2, e o comando rodado numa cópia).
- [x] Um valor fora da tabela (`revisor = "talvez"`) → a mensagem lista `sempre`, `perguntar` e
  `nunca` (teste 7 do G2).
- [x] O `AGENTS.md` sem as marcas → o bloco entra no fim, com as marcas, e o resto do arquivo não
  muda (teste 11 do G2).
- [x] O `golem.toml` com erro, numa ação com gancho → as lições chegam com o teto 2, sem erro
  (teste 8 do G3).
- [x] O `desligado` sem aspas → o gancho segue e entrega a lição (teste 4 do G3); o `aplicar`
  acusa a linha.
- [~] A `configurar` numa máquina sem Python nenhum → deixa o `golem.toml` escrito, diz que o
  `aplicar` fica pendente e oferece o `gancho = "desligado"`. Nesta
  máquina, o agente acha o Python mesmo com o `LOCALAPPDATA` trocado (lição
  `trocar-o-localappdata-nao-esconde-o-python-do-agente`). Não exercitado. O texto da regra está em
  `.claude/skills/configurar/SKILL.md:109-118`.

## Requisitos da constituição

O kit não tem `specs/tech-stack.md`. Valem o README ("Requisitos") e o `AGENTS.md`.

- [x] Nenhuma dependência nova:
  - `grep -nE '^(import|from) ' .claude/golem.py` → só módulos da biblioteca padrão;
  - o `gancho.sh` só usa recursos embutidos do `sh` e os utilitários que já usa (`dirname`,
    `date`, `git`, `printf`): conferir na leitura do diff.
- [x] Os arquivos novos do kit trazem a linha de crédito (`test_credito.py`).
- [x] Nenhum caminho pessoal no repositório:
  `git grep -nE '[A-Za-z]:[\\/]Users[\\/][^<.]|/[a-z]/Users/[^<.]'` sem resultado.
- [x] Nenhum nome de cliente, de outro projeto ou de pessoa nos arquivos novos, além da linha de
  crédito: conferir na leitura do diff.

## Registro

- [x] `docs/plano-produto.md`: a fase 1 marcada como feita, com a data e a branch; a seção 8 com as
  decisões do R1 e as quatro respostas da entrevista; os "Detalhes a conferir" atualizados (as
  duas lições e o "pulado sem Python" das três skills, marcados fase 4).
- [x] As perguntas em aberto do `requirements.md` respondidas ou movidas para o plano. O modelo do
  Pro: a resposta registrada, ou o item mantido "a conferir" com o critério manual 1 dependente
  dele.

## Não exigido nesta fase

- O `effort:` por agente, o `--conferir` do `aplicar`, a página HTML e o medidor: fase 5.
- O modelo por agente no Codex: fase 6.
- O "pulado sem Python" na `validar-fase`, na `auditar-specs` e na `sessao-gerente`: fase 4.
- Uma receita intermediária.
- O vocabulário de equipe só na `completo` e o guia do primeiro dia: fase 4.
- O aviso do gancho para um `golem.toml` com erro.
- O teste com o Codex de verdade: só o instalador numa cópia.
- O `CHANGELOG.md`: o kit não tem um, e criá-lo fica para a fase 6.

## Resultado (2026-11-14, skill `validar-fase`, head `30560cc` mais o registro)

- A suíte: `123 passed in 47.82s`, sem falhas nem pulados. Os 27 nós novos (o `test_golem.py`
  inteiro, os 8 do G3 e o do frontmatter): `27 passed`.
- O `golem.py aplicar` no kit: `nada mudou: o AGENTS.md e os agentes já seguem o golem.toml`, e o
  `git status --short` só mostrava o `plan.md` do registro. O bloco: `764` bytes. O `model:`:
  `revisor.md:5:model: sonnet` e `validador.md:5:model: opus`.
- A régua: `ok       .claude/indice/licoes.yaml` (`total: 7`).
- O instalador do Codex numa cópia (`git archive 30560cc`): `ok       24 arquivos do Codex batem
  com .claude/`, com a `.agents/skills/configurar/SKILL.md`. O `test_credito.py` na cópia:
  `2 passed`; sem a linha `license:` da skill nova: `1 failed, 1 passed`.
- `sh -n`: rc 0; o fim de linha: `i/lf w/lf`. O Python 3.8: o `ast.parse` rc 0, o
  `from __future__` com contagem `1`, e o `grep` das anotações no `licoes_relevantes.py` rc 1.
- A `diagnostico`: o `git grep` acha só a `:130` (o passo 7, o `show-toplevel` do teste do gancho),
  e o `check-ignore` continua na `:26`.
- Os casos de borda do `aplicar`, numa cópia: `revisr` → `ERRO golem.toml:2: a chave revisr não
  existe...`; `talvez` → `os aceitos são sempre, perguntar, nunca`; `gancho = desligado` sem aspas
  → `a linha não é chave = valor`. Nos três, `rc=1`, `Nada foi escrito.` e o `git status` sem
  mudança fora do `golem.toml`. Os outros três casos com teste passaram entre os 27 nós.
- As dependências: o `golem.py` importa só `__future__`, `re`, `sys` e `pathlib`; o diff do
  `gancho.sh` só acrescenta o `printf`, que ele já usava. Caminho pessoal: rc 1, nada. Nomes de
  pessoa, cliente ou outro projeto nos arquivos novos: nenhum, fora a linha de crédito.
- As verificações manuais 1 a 4 passaram, com as sessões abertas pelo autor do kit no app
  desktop, e estão no `plan.md`, G6, com o que se leu de cada transcrição. A 1 passou na segunda
  rodada, depois das correções do G6. A 3 passou com a `configurar` de `f195050` e de novo, de ponta
  a ponta, com a de `30560cc`.
- A revisão: revisor e validador em cada grupo; o guardião sobre `git diff 1f9f827` deu "com
  bloqueio" sobre `1397a98` e sobre as correções, e "sem bloqueio" na terceira rodada, sobre a
  árvore de `f195050`; as correções do G6 passaram também pelo validador; o `30560cc` (só a
  `configurar` e o `plan.md`) passou pelo revisor, pelo caminho rápido. Os achados e as decisões estão na tabela de alterações do
  `plan.md`.

## Resultado (2026-11-15, head `22547bb`, depois da correção da `configurar`)

- A suíte: `123 passed in 48.07s`, sem falhas nem pulados. O `test_golem.py`: `18 passed`; o nó
  `test_sem_golem_toml_vale_a_economico`: `1 passed`.
- O `golem.py aplicar` no kit: `nada mudou: o AGENTS.md e os agentes já seguem o golem.toml`, e o
  `git status --short` vazio. O bloco: `764` bytes. O `model:`: `revisor.md:5:model: sonnet` e
  `validador.md:5:model: opus`.
- A régua: `ok       .claude/indice/licoes.yaml` (`total: 8`).
- O instalador do Codex numa cópia (`git archive 22547bb`): `ok       24 arquivos do Codex batem
  com .claude/`, e a `.agents/skills/configurar/SKILL.md` traz a frase nova do "Nunca". O
  `test_credito.py` na cópia: `2 passed`; sem a linha `license:` da `configurar`: `1 failed, 1
  passed`.
- `sh -n`: rc 0; o fim de linha: `i/lf w/lf`. O Python 3.8: o `ast.parse` rc 0, o
  `from __future__` com contagem `1`, e o `grep` das anotações no `licoes_relevantes.py` rc 1.
- A `diagnostico`: o `git grep` acha só a `:130`, e o `check-ignore` continua na `:26`.
- Caminho pessoal (o `git grep` do critério, na árvore inteira): rc 1, nada. O `golem.py` não mudou
  desde `30560cc`, e os casos de borda do Resultado anterior continuam valendo.
- As verificações manuais 1 a 5 passaram; a 5 em 2026-11-15, com a `configurar` de `22547bb`
  (`plan.md`, G6).
- A revisão da correção: o revisor, pelo caminho rápido, deu "com bloqueio" duas vezes (as marcas
  `[x]` diante da verificação 5 e uma citação de linha) e "sem bloqueio" na terceira rodada.
