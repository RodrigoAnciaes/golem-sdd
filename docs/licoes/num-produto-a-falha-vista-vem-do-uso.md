---
id: num-produto-a-falha-vista-vem-do-uso
data: 2026-11-21
area: processo
tipo: premissa-falsa
custo: "uma melhoria para os projetos de quem usa o kit (a busca nos documentos que crescem) rebaixada por falta de caso no repositório do kit, até o usuário corrigir"
gatilho: "a regra 10 (\"sem uma falha vista que a justifique\") aplicada a um kit que outras pessoas vão usar, ao classificar os aprendizados de outro projeto com o mesmo método"
gatilhos:
  - 'specs/[^/]+/(requirements|plan)\.md$'
  - 'specs/roadmap\.md$'
refs:
  - "AGENTS.md, regra 10, primeiro item (a falha vista)"
  - "a correção do usuário, 2026-11-21: \"a gente tem sempre que pensar no que as pessoas vão usar e não esperar acontecer\""
---

**O que se achava:** que a regra 10 ("nada por precaução... sem uma falha vista que a justifique")
pedia uma falha vista **no repositório do próprio produto**, e que, sem ela, uma peça pensada para
quem usa o produto devia esperar o caso aparecer ali.

**O que é:** num produto, quem usa de verdade são os outros, e o repositório do produto quase não
passa pelo que eles passam. A falha vista vem do uso: do projeto de quem usa (o que o produto faz
crescer, como as lições, as specs e o `AGENTS.md` de um kit) ou de outro projeto que usa o mesmo
método e já a viu. O que a regra 10 barra continua barrado: a peça sem caso nenhum escrito, com a
fonte.

**Como perceber da próxima vez:** ao cortar algo por "não há caso real", pergunte onde o caso
apareceria. Se é no uso de quem recebe o que você entrega, procure-o lá (no uso previsto, num
projeto que já usa o método) antes de cortar. "Não vi aqui" não quer dizer "não existe".
