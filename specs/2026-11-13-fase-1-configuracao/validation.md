# Fase 1: configuração e receita econômica — Validação

O contrato de merge da fase. `PY` é um Python 3.8+ com pytest. Nesta máquina, não há Python no
PATH: é o de um `.venv` de outro projeto, e o Python do instalador não tem pytest. Os comandos rodam
da raiz do worktree, no Git Bash.

## Verificações automatizadas

- [ ] `"$PY" -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs` → **`123 passed`**,
  sem falhas nem pulados: os 96 de antes e os 27 novos do `plan.md` (17 no G2, contando os 3 casos
  do teste parametrizado, 8 no G3, 1 no G5 e 1 no G6, o do frontmatter). Se um teste mudar de
  forma na fase, a contagem nova entra aqui e na tabela de alterações do `plan.md`.
- [ ] Os testes novos, cada um pelo nó, passam. Exemplo:
  `"$PY" -m pytest ".claude/tests/test_golem.py::test_sem_golem_toml_vale_a_economico" -o addopts= -q -p no:cacheprovider`
  → `1 passed`. Os nomes estão no `plan.md`, G2, G3 e G5.
- [ ] `"$PY" .claude/golem.py aplicar`, rodado no kit → diz que nada mudou, e `git status --short`
  continua sem mudança: o `AGENTS.md` e os dois agentes já estão como o `aplicar` os gera (R10).
- [ ] `sed -n '/<!-- golem:inicio -->/,/<!-- golem:fim -->/p' AGENTS.md | wc -c` → no máximo 1200
  (R4).
- [ ] `grep -n '^model:' .claude/agents/revisor.md .claude/agents/validador.md` →
  `revisor.md:...:model: sonnet` e `validador.md:...:model: opus` (a `economico`, R3).
- [ ] `"$PY" .claude/regua.py --conferir` → termina com `ok       .claude/indice/licoes.yaml`.
- [ ] Numa cópia descartável dos arquivos rastreados: `"$PY" .claude/instalar_codex.py` e depois
  `--conferir` → `ok`, e `.agents/skills/configurar/SKILL.md` existe na cópia.
- [ ] `sh -n .claude/hooks/gancho.sh` → sem saída, código 0; e
  `git ls-files --eol .claude/hooks/gancho.sh` → `i/lf w/lf`.
- [ ] O Python 3.8: `"$PY" -c "import ast,sys; [ast.parse(open(f,encoding='utf-8').read(), f, feature_version=(3,8)) for f in sys.argv[1:]]" .claude/golem.py .claude/hooks/licoes_relevantes.py`
  → sem saída, código 0. E `grep -c '^from __future__ import annotations' .claude/golem.py` → `1`:
  a sintaxe do 3.8 não pega anotações como `dict[str, str]`, que quebram no 3.8 sem essa linha
  (o `instalar_codex.py:22` e o `regua.py:31` a usam). No `licoes_relevantes.py`, que não tem
  essa linha: `git diff 1f9f827 -- .claude/hooks/licoes_relevantes.py | grep -nE '^\+.*(-> *|: *)(dict|list|tuple|set)\['`
  → sem resultado.
- [ ] O `test_credito.py` passa com `configurar` na lista. Numa cópia, apagar a linha `license:`
  da skill nova faz o teste falhar.
- [ ] O aviso do worktree saiu da `diagnostico` (R1):
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

## Casos de borda

- [ ] O `golem.toml` com uma chave escrita errada (`revisr = "nunca"`) →
  `"$PY" .claude/golem.py aplicar` sai com código diferente de 0, a mensagem traz o número da linha
  e a chave, e `git status --short` não mostra mudança no `AGENTS.md` nem nos agentes (teste 12 do
  G2, e o comando rodado numa cópia).
- [ ] Um valor fora da tabela (`revisor = "talvez"`) → a mensagem lista `sempre`, `perguntar` e
  `nunca` (teste 7 do G2).
- [ ] O `AGENTS.md` sem as marcas → o bloco entra no fim, com as marcas, e o resto do arquivo não
  muda (teste 11 do G2).
- [ ] O `golem.toml` com erro, numa ação com gancho → as lições chegam com o teto 2, sem erro
  (teste 8 do G3).
- [ ] O `desligado` sem aspas → o gancho segue e entrega a lição (teste 4 do G3); o `aplicar`
  acusa a linha.
- [ ] A `configurar` numa máquina sem Python nenhum → deixa o `golem.toml` escrito, diz que o
  `aplicar` fica pendente e oferece o `gancho = "desligado"`. Provavelmente não exercitado: nesta
  máquina, o agente acha o Python mesmo com o `LOCALAPPDATA` trocado (lição
  `trocar-o-localappdata-nao-esconde-o-python-do-agente`). O texto da regra fica citado com
  `SKILL.md:linha`.

## Requisitos da constituição

O kit não tem `specs/tech-stack.md`. Valem o README ("Requisitos") e o `AGENTS.md`.

- [ ] Nenhuma dependência nova:
  - `grep -nE '^(import|from) ' .claude/golem.py` → só módulos da biblioteca padrão;
  - o `gancho.sh` só usa recursos embutidos do `sh` e os utilitários que já usa (`dirname`,
    `date`, `git`, `printf`): conferir na leitura do diff.
- [ ] Os arquivos novos do kit trazem a linha de crédito (`test_credito.py`).
- [ ] Nenhum caminho pessoal no repositório:
  `git grep -nE '[A-Za-z]:[\\/]Users[\\/][^<.]|/[a-z]/Users/[^<.]'` sem resultado.
- [ ] Nenhum nome de cliente, de outro projeto ou de pessoa nos arquivos novos, além da linha de
  crédito: conferir na leitura do diff.

## Registro

- [ ] `docs/plano-produto.md`: a fase 1 marcada como feita, com a data e a branch; a seção 8 com as
  decisões do R1 e as quatro respostas da entrevista; os "Detalhes a conferir" atualizados (as
  duas lições e o "pulado sem Python" das três skills, marcados fase 4).
- [ ] As perguntas em aberto do `requirements.md` respondidas ou movidas para o plano. O modelo do
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
