---
id: o-aviso-entre-duas-perguntas-fica-no-raciocinio
data: 2026-11-15
area: processo
tipo: armadilha
origem: kit
custo: "duas rodadas da verificação manual 3 e uma correção da skill (30560cc) que não pegou"
gatilho: "a skill configurar mandava dizer, numa linha de texto entre duas chamadas da ferramenta de pergunta, o que fica sem revisão; em duas sessões novas, a linha não saiu"
refs:
  - ".claude/skills/configurar/SKILL.md:78-81 `é o aviso do que fica sem revisão` (o aviso, agora na descrição do botão \"Nunca\")"
  - ".claude/skills/configurar/SKILL.md:111-112 `dentro do texto da própria pergunta` (o arquivo, agora no texto da pergunta de gravar)"
  - "specs/2026-11-13-fase-1-configuracao/plan.md, G6, verificação 3 refeita (as duas rodadas)"
gatilhos:
  - '/SKILL\.md$'
---

**O que se achava:** que uma skill que manda "diga numa linha" entre duas perguntas com botões
seria cumprida, e que pôr a instrução "logo depois da segunda chamada" (o `30560cc`) bastaria para
o agente escrevê-la.

**O que é:** nas duas rodadas da verificação 3 (`f195050` e `30560cc`), a linha ficou só no
raciocínio, entre a chamada das perguntas e a de gravar, e o "mostre o arquivo inteiro" virou um
resumo dos valores. Na rodada de `30560cc`, o que estava **dentro** da chamada saiu: a descrição
do "Nunca" ("o validador (a cada parte) e o guardião (antes do merge) continuam").

**Como perceber da próxima vez:** se a instrução de uma skill pede um texto ao usuário no meio de
uma sequência de chamadas de ferramenta (entre duas perguntas, antes de gravar), procure esse texto
na transcrição fora dos blocos de raciocínio. Se ele só aparece no raciocínio, ponha o conteúdo
dentro da própria chamada: na descrição da opção ou no texto da pergunta (visto funcionar na
`completo`; a `economico` é a verificação 5 da fase 1).
