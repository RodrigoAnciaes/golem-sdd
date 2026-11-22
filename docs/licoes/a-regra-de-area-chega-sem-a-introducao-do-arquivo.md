---
id: a-regra-de-area-chega-sem-a-introducao-do-arquivo
data: 2026-11-21
area: processo
tipo: premissa-falsa
origem: kit
custo: "a rodada A da conferência 4 da verificação manual 1 da fase 2 sem o \"me explica\", e as rodadas seguintes até provar o conserto (E e F)"
gatilho: "escrever uma regra de área que se apoia num texto da introdução do docs/regras-de-area.md (o modelo templates/roblox/regras-de-area.md da fase 2)"
refs:
  - "templates/roblox/regras-de-area.md (a introdução \"Avisar e deixar\" e o fim de cada regra)"
  - ".claude/hooks/licoes_relevantes.py (a docstring: o bloco `## Regra N` é o que se entrega)"
gatilhos:
  - '\bregras-de-area\.md$'
---

**O que se achava:** que cada regra do modelo de riscos do Roblox podia terminar em "avise no
resumo, com as três saídas", e o agente saberia quais são, porque a introdução do arquivo as nomeia
("corrigir, deixar assim, me explica").

**O que é:** o gancho entrega a quem edita só o bloco de cada `## Regra N`, e não a introdução do
arquivo. Na rodada A da conferência 4 (2026-11-21, `conf4.jsonl` em `fase-2-g6-pronto/`, nas
notas da conversa da fase 2), o agente criou o Script pelo `multi_edit`, o gancho disparou (a
resposta cita a lição do Ctrl+Z, que chega pela mesma área), e o aviso veio sem bloquear, mas com
saídas inventadas: "deixar como está, validar no servidor, apagar depois do teste", sem o "me
explica". Com cada regra nomeando as três saídas, as rodadas E e F trouxeram as três.

**Como perceber da próxima vez:**
1. Uma regra de área que diz "as três saídas", "o formato acima" ou "como na introdução": o que ela
   cita não chega com ela. Cada `## Regra N` precisa se bastar.
2. Um agente que segue a regra pela metade (faz o aviso, mas com outras palavras) é o sinal de que
   faltou na regra o pedaço que ficou fora do bloco.
