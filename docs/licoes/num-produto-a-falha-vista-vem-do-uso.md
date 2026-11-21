---
id: num-produto-a-falha-vista-vem-do-uso
data: 2026-11-21
area: processo
tipo: premissa-falsa
custo: "uma melhoria para os projetos de quem usa o kit (a busca nos documentos que crescem) rebaixada por falta de caso no repositório do kit, até o usuário corrigir"
gatilho: "a regra 10 («sem uma falha vista que a justifique») aplicada a um kit que outras pessoas vão usar, ao classificar os aprendizados de outro projeto com o mesmo método"
gatilhos:
  - 'specs/[^/]+/(requirements|plan)\.md$'
  - 'specs/roadmap\.md$'
  - 'docs/plano-produto\.md$'
refs:
  - "AGENTS.md:181-185 (regra 10, primeiro item: a falha vista)"
  - "a correção do usuário, 2026-11-21: «a gente tem sempre que pensar no que as pessoas vão usar e não esperar acontecer»"
---

**O que se achava:** que a regra 10 ("nada por precaução... sem uma falha vista que a justifique")
pedia uma falha vista **no repositório do próprio produto**, e que, sem ela, uma peça pensada para
quem usa o produto devia esperar o caso aparecer ali.

**O que é:** num produto, quem usa de verdade são os outros, e o repositório do produto quase não
passa pelo que eles passam. A falha vista vem do uso de quem recebe o produto, ou de outro projeto
que usa o mesmo método e já a viu. A peça sem caso escrito, com a fonte, continua barrada.

**Como perceber da próxima vez:** ao cortar algo por "não há caso real", pergunte onde o caso
apareceria. Se é no uso de quem recebe o que você entrega, procure lá um caso escrito, com a fonte
(o relato de um usuário, um projeto que já usa o método), antes de cortar. "Não vi aqui" não quer
dizer "não existe".
