# Referência: `roadmap.md`

Carregue este arquivo ao escrever ou replanejar o roadmap.

## O teste do tamanho de fase

Uma fase tem o tamanho certo quando:

- a validação dela cabe em cinco linhas verificáveis;
- ela vira uma branch mergeável sem depender de outra fase em andamento;
- alguém consegue revisar o diff inteiro em uma sentada;
- se ela for abandonada no meio, a `main` continua funcionando.

Falhou em qualquer um dos quatro? Divida.

## Estrutura de cada fase

```markdown
## Fase N: Nome curto  `[ ]`

**Objetivo:** o que passa a existir, em uma frase

- [ ] entregável
- [ ] entregável

**Pronto quando:** critério observável (comando que passa, tela que abre, endpoint que responde)
**Depende de:** Fase M (só quando houver dependência real)
```

## Ordenação

1. **Primeiro o que prova que o esqueleto funciona:** rodar, servir, testar. A Fase 1 quase sempre
   é encanamento.
2. **Depois o caminho feliz mais estreito** de ponta a ponta, com dado real.
3. **Depois largura:** mais entidades, mais telas, mais casos.
4. **Por último o que só melhora o que já existe:** polimento, acessibilidade, endurecimento.

Dependência externa (contrato, credencial, API de terceiro) puxa a fase para o começo, porque
espera de terceiro não acelera com esforço seu.

## Falhas comuns

| Sintoma | Correção |
|---|---|
| Fase "Backend" e fase "Frontend" | fatie por funcionalidade vertical, não por camada |
| Fase sem critério de pronto | escreva o comando ou o passo que prova a entrega |
| Vinte fases planejadas em detalhe | detalhe as três próximas; o resto vira "Depois (não planejado)" |
| Fase que depende de decisão não tomada | a decisão vira a fase anterior, ou um ADR |
| Fases concluídas reescritas no replanejamento | histórico é registro; mexa só nas pendentes |

## Marcação de estado

`[ ]` pendente · `[~]` em andamento · `[x]` concluída, com data e branch na tabela de concluídas.
O agente lê essa marcação para descobrir sozinho qual é a próxima fase: mantenha-a honesta.

A fase concluída sai do corpo do roadmap e fica só como linha na tabela de concluídas. O roadmap
mostra o que está **por fazer**; a história está no Git e nas pastas de spec.

## Perguntas de entrevista

1. O que precisa existir primeiro para todo o resto poder ser testado?
2. Qual é a menor coisa que alguém conseguiria usar de verdade?
3. O que depende de terceiro, de credencial ou de aprovação que não é sua?
4. O que dá para deixar feio agora e arrumar depois sem retrabalho?
5. Tem prazo externo? Qual fase precisa estar de pé antes dele?
