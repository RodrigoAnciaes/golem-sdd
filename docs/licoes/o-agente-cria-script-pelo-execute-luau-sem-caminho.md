---
id: o-agente-cria-script-pelo-execute-luau-sem-caminho
data: 2026-11-21
area: processo
tipo: premissa-falsa
custo: "duas rodadas da conferência 4 da verificação manual 1 da fase 2 sem regra de risco nenhuma no contexto"
gatilho: "pedir ao agente, num place do Roblox, um script novo, com o gancho das lições acendendo a área codigo só pelo caminho do multi_edit"
refs:
  - ".claude/hooks/licoes_relevantes.py (POR_CAMINHO, os serviços do place; POR_COMANDO, o Luau que cria instância)"
  - ".claude/tests/test_gancho.py (test_execute_luau_que_cria_script_acende_codigo)"
gatilhos:
  - '\.claude/hooks/licoes_relevantes\.py$'
---

**O que se achava:** que o agente cria e edita os scripts do place pelo `multi_edit`, que manda o
caminho (`game.ServerScriptService...`) em `file_path`, e que por isso bastava o `POR_CAMINHO` ter
os serviços do place para as regras da área `codigo` chegarem a quem escreve código no place.

**O que é:** pedido um `RemoteEvent` e um Script, o agente criou os dois num `execute_luau` só, com
`Instance.new` e `Source =`, em duas das quatro rodadas da conferência 4 antes do conserto do
gancho (B e C) (2026-11-21, `conf4b.jsonl`
e `conf4c.jsonl` em `fase-2-g6-pronto/`, nas notas da conversa da fase 2). O `code` do
`execute_luau` vale como comando, e nenhum `POR_COMANDO` dava `codigo`. Perguntada depois pela
própria sessão (`conf4c-gancho.txt`), a rodada C disse que nenhum texto de gancho lhe chegou. O
gancho passou a dar `codigo` ao Luau com `Instance.new` ou `.Source =`.

**Como perceber da próxima vez:**
1. Uma regra de área que não aparece no trabalho do agente: veja por qual ferramenta ele fez a
   mudança. A área sai do caminho ou do comando, e uma ferramenta que cria sem caminho escapa da
   área do caminho.
2. Ao ligar o gancho a uma ferramenta nova, liste todos os jeitos de ela mudar o código, e não só
   o que se viu primeiro.
