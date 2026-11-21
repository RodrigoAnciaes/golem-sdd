# Referência: a entrevista da spec de fase

Uma rodada, três temas, antes de qualquer arquivo. Pergunte só o que a constituição e as fases
anteriores não respondem.

## Escopo

- Que dado entra e que dado sai desta fase? Quais campos, com que tipo e obrigatoriedade?
- O que o usuário final consegue fazer ao fim da fase que não conseguia antes?
- O que alguém vai supor que está incluído e **não** está?
- Existe caminho de erro que precisa ser tratado já nesta fase?

## Decisões

- Onde o dado é guardado, e o que acontece quando ele não existe?
- Validação: onde é feita, o que acontece quando falha, que mensagem aparece?
- Padrão de interface: reaproveita algo existente ou é novo? Qual arquivo serve de modelo?
- Precisa de algo fora de `tech-stack.md`? (Se sim, **pare** e trate como proposta de mudança de
  stack.)

## Contexto

- Tom e idioma dos textos visíveis; termos do glossário que precisam aparecer exatamente assim
- O que já quebrou nesta área do sistema antes (procure em `docs/licoes/`)
- Restrição externa que aperta a fase: prazo, credencial, dependência de terceiro, gasto
- Dúvidas que não bloqueiam o início, mas precisam de resposta antes do merge

## Regras da entrevista

- **Agrupe tudo em uma rodada só.** Perguntar em conta-gotas cansa e produz respostas piores.
- **Não pergunte o que está escrito.** Se a missão já define o tom, use-o.
- **Ofereça opções quando houver caminho óbvio.** É mais fácil escolher do que redigir. Cada opção
  com a consequência, a recomendada primeiro.
- **Com os papéis, a pergunta de produto vai à EST.** Isso vale quando o bloco "Como o Golem
  trabalha aqui" do `AGENTS.md` diz "Conversas: os papéis de `docs/operacao-das-conversas.md`".
  - As perguntas de escopo, de prioridade e do que o usuário vê vão à conversa de estratégia
    (EST), no cartão de decisão, com o texto original: a pergunta, as opções e a consequência de
    cada uma.
  - A resposta volta com as palavras dele e a data, e é assim que entra na spec.
  - Ficam aqui o detalhe técnico e a aprovação da spec escrita
    (`docs/operacao-das-conversas.md`, "O fluxo das decisões").
  - Sem papéis, pergunte ao usuário direto.
- **Registre a resposta na spec com a palavra do usuário**, principalmente termos de domínio.
- **Resposta que implica fato técnico se confere.** "Já tenho acesso ao banco" leva duas perguntas
  baratas: qual, exatamente, e por onde (o caminho no código ou na config). Sem o caminho, escreva
  "a conferir", não o fato.
