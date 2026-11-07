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
- **Registre a resposta na spec com a palavra do usuário**, principalmente termos de domínio.
- **Resposta que implica fato técnico se confere.** "Já tenho acesso ao banco" leva duas perguntas
  baratas: qual, exatamente, e por onde (o caminho no código ou na config). Sem o caminho, escreva
  "a conferir", não o fato.
