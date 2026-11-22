---
id: o-studio-nao-acessa-o-datastore-por-padrao
data: 2026-11-21
area: processo
tipo: premissa-falsa
origem: kit
custo: "uma decisão do usuário sobre o validador tomada em cima da premissa e refeita no mesmo dia, mais o guia, os modelos e a spec da fase 2 corrigidos"
gatilho: "escrever no kit o risco de rodar código no Studio com o jogo ligado (o guia, os modelos de Roblox e o validador da fase 2)"
refs:
  - "docs/guia-roblox.md (seção 3, Rodar os testes liga o jogo)"
  - ".claude/agents/validador.md (seção Código num place do Roblox Studio)"
  - "specs/2026-11-13-fase-2-roblox/requirements.md (R4)"
gatilhos:
  - '\bguia-roblox\.md$'
  - '\.claude/agents/validador\.md$'
---

**O que se achava:** que "no Studio, o `DataStore` é o de verdade": qualquer script rodado com o
jogo ligado grava nos dados dos jogadores. O guia, os modelos e a spec da fase 2 diziam isso, e a
decisão de proibir a mutação do validador também em memória se apoiou nisso.

**O que é:** o usuário perguntou se o risco era real num place de desenvolvimento (2026-11-21), e a
documentação da Roblox diz que não, por padrão. O Studio só acessa o `DataStore` com "Enable Studio
Access to API Services" ligado, e a opção vem desligada ("By default, games tested in Studio can't
access data stores"). Sem ela, a gravação dá o erro 403, "Can't write to DataStore from Studio
because API access is not enabled"
([códigos de erro](https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits)).
Com ela, o Studio usa os mesmos dados do
jogo publicado, que são por experiência, e a Roblox recomenda ligá-la só numa versão de teste do
jogo ([data stores](https://create.roblox.com/docs/cloud-services/data-stores)). O usuário decidiu
liberar a mutação em memória quando nenhum script do place usa `DataStore`.

**Como perceber da próxima vez:**
1. Um risco de plataforma escrito como absoluto ("é o de verdade", "grava sempre") sem a
   configuração que o liga: procure na documentação se há uma opção, e qual é o padrão dela.
2. Uma decisão do usuário tomada em cima de um risco: cite a fonte do risco na pergunta. Sem
   fonte, a pergunta leva o risco como fato.
