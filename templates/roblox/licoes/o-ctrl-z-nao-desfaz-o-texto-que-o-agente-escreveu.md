---
id: o-ctrl-z-nao-desfaz-o-texto-que-o-agente-escreveu
data: 2026-11-21
area: codigo
tipo: armadilha
custo: "na fase 2 do Golem, o Ctrl+Z apagou um script criado antes e deixou o texto do agente onde estava"
gatilho: "desfazer no Roblox Studio (Editar ⟩ Desfazer, Ctrl+Z) uma edição feita pelo agente com o multi_edit do Studio MCP"
refs:
  - "Golem SDD, specs/2026-11-13-fase-2-roblox/plan.md (Respostas do G2, resposta 7)"
gatilhos:
  - '^game\.[^\s=(]+$'
---

**O que se achava:** que o Ctrl+Z do Studio desfaz a última coisa que o agente fez no place, como
desfaz o que a gente digita.

**O que é:** o Ctrl+Z desfaz a criação de um script pelo `multi_edit`, mas não a troca de texto. Na
fase 2 do Golem, a última chamada do agente trocou o texto de um módulo (`return 2` para
`return 3`); depois do Ctrl+Z, o módulo continuava com `return 3`, e o que sumiu foi um script que o
agente tinha criado antes. Numa outra vez, o Ctrl+Z apagou de uma vez uma pasta e o script que o
agente tinha acabado de criar. A da pasta foi pelo menu Editar ⟩ Desfazer; a da troca de texto,
pelo Ctrl+Z com o foco na janela 3D. Com o foco no editor de script, o resultado pode ser outro.

**Como perceber da próxima vez:**
1. Depois do Ctrl+Z, o script ainda tem o texto que o agente escreveu, ou sumiu outro script: o
   desfazer pegou outra coisa. Não aperte de novo às cegas.
2. Para voltar atrás do que o agente escreveu, use o histórico de versões (Janela ⟩ Histórico da
   versão) e a versão que o agente salvou antes da fase.
