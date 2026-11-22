---
id: proibir-pelo-efeito-deixa-a-brecha-do-que-nao-tem-o-efeito
data: 2026-11-21
area: processo
tipo: premissa-falsa
custo: "uma decisão do usuário reaberta na verificação manual 1 da fase 2, e o texto do validador e da spec reescritos"
gatilho: "chamar o agente validador sobre uma fase cujo código mora num place do Roblox Studio"
refs:
  - ".claude/agents/validador.md (seção Código num place do Roblox Studio)"
  - "specs/2026-11-13-fase-2-roblox/requirements.md (R4, o texto dos dois)"
gatilhos:
  - '\.claude/agents/validador\.md$'
---

**O que se achava:** que as frases "o `execute_luau` só roda o executor e leituras; nunca muda o
place" e "no place, a mutação não se faz" bastavam para o validador pular a mutação no place.

**O que é:** o validador fez a mutação assim mesmo, por um caminho que não muda o place. Com o
jogo ligado, trocou as funções da tabela que o `require(Moedas)` devolve por cópias quebradas,
rodou o executor numa rodada de controle (`3 passed`) e em três mutações (`1 passed, 2 failed`;
`2 passed, 1 failed`; `2 passed, 1 failed`),
restaurou e desligou o jogo. Ele relatou "Não alterei o `Source` de nenhum script", e o hash do
`Moedas` ficou igual (847 bytes, `481808074`). Mas, com o jogo ligado, os scripts do jogo rodam
junto e podem gravar o resultado da função quebrada no `DataStore` de verdade, o risco que a
proibição queria evitar. O usuário decidiu proibir também esse caminho (2026-11-21). No mesmo
dia, a premissa do risco se mostrou parcial (lição `o-studio-nao-acessa-o-datastore-por-padrao`),
e a regra virou: a mutação em memória vale quando nenhum script do place usa `DataStore`. O texto
novo diz o risco (o `DataStore`) e o caminho, e não só o efeito.

**Como perceber da próxima vez:**
1. Uma proibição a um agente escrita pelo efeito ("nunca muda X") deixa aberto o que chega ao
   mesmo risco sem esse efeito. Escreva o risco e nomeie o caminho proibido que se conhece.
2. Num relatório do validador sobre um place, uma tabela de mutações "pegas" é o sinal de que
   ele achou um caminho que o texto não fechou.
