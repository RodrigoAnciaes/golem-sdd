---
id: os-testes-do-place-so-valem-com-o-jogo-ligado
data: 2026-11-21
area: codigo
tipo: premissa-falsa
custo: "na fase 2 do Golem, três rodadas de teste no Studio até achar um jeito de testar o código novo"
gatilho: "rodar módulos do place pelo execute_luau do Studio MCP, em modo de edição, logo depois de editá-los pelo multi_edit"
refs:
  - "Golem SDD, specs/2026-11-13-fase-2-roblox/plan.md (Respostas do G2, resposta 3)"
gatilhos:
  - '\bGolemTestes\b'
  - '\brequire\s*\(\s*game\.'
---

**O que se achava:** que rodar os testes pelo `execute_luau` em modo de edição (`datamodel_type`
`Edit`) testa o código como ele está no place, logo depois de o agente editá-lo.

**O que é:** em modo de edição, o `require` devolve a versão guardada de um módulo. Na fase 2 do
Golem, um módulo com `return 1` foi trocado para `return 2` pelo `multi_edit`; o `script_read`
mostrava `return 2`, e o `require` em modo de edição continuava devolvendo `1`. Clonar o módulo não
resolve: um clone que chama outro módulo pelo `require` também devolveu o valor velho. Com o jogo
ligado (`start_stop_play`, e o `execute_luau` com `datamodel_type` `Server`), o `require` devolveu
`2`, e o console começou limpo.

**Como perceber da próxima vez:**
1. A linha `N passed, N failed, N skipped` não muda depois de mudar o código que o teste cobre, ou um
   teste que devia falhar passa: veja se o executor rodou com o `datamodel_type` `Edit`. Rode de novo
   com o jogo ligado.
2. Sem a linha de resumo no console daquela jogada, não há resultado. "nenhum teste encontrado" com
   `0 passed` quer dizer zero testes, e não verde.
