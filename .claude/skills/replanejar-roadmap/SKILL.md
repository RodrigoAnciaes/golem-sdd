---
name: replanejar-roadmap
description: Revisa e reorganiza specs/roadmap.md à luz do que já foi implementado — junta, divide ou remove fases pendentes e propaga mudanças de requisito para a constituição e para as specs já escritas. Use quando o usuário disser "replanejar", "revisar o roadmap", "mudou o requisito", "essas fases não fazem mais sentido" ou invocar /replanejar-roadmap.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Replanejar o roadmap

**Lê:** `specs/roadmap.md`, `specs/mission.md`, `specs/tech-stack.md` e o `git log` do que foi
entregue.
**Escreve:** `specs/roadmap.md` (só o que está **por fazer**) e propaga para as specs de fase
afetadas. Fase concluída fica como linha na tabela de concluídas e **não** volta ao corpo.
**Decide:** **para e pede aprovação antes de aplicar.** Reordenar a fila é decisão do usuário, não
conclusão da análise: a skill diagnostica e propõe.

## 1. Levantar o estado real

- Fases concluídas e o que elas de fato entregaram (leia as specs delas, não só o roadmap)
- O que apareceu durante a implementação e não estava previsto (tabelas "Alterações de escopo" dos
  `plan.md`, itens em "Depois (não planejado)")
- Perguntas em aberto acumuladas nos `requirements.md`
- Dívida registrada em ADRs com gatilho de revisão já atingido
- Lições recentes em `docs/licoes/` que mudam o custo de alguma fase

Cada fato que sustenta uma proposta vem com a fonte (`arquivo:linha`, commit ou PR).

## 2. Diagnosticar antes de alterar

Apresente ao usuário, **sem mexer em nada ainda**:

| Categoria | O que reportar |
|---|---|
| Grandes demais | fases cuja validação não cabe em cinco linhas: proponha o corte |
| Pequenas ou redundantes | fases que sozinhas não entregam nada: proponha a fusão |
| Sem sentido | fases que a realidade dispensou: proponha a remoção, com o motivo |
| Faltando | trabalho descoberto na prática e ainda não planejado |
| Fora de ordem | dependência externa ou decisão pendente que deveria vir antes |

Use o teste de tamanho de fase e as regras de ordenação de `constituicao/references/roadmap.md`.

Cada proposta vai como cartão de decisão: o problema, as opções com a consequência, a recomendada
primeiro e o porquê. Uma decisão aberta por mensagem quando elas não dependem uma da outra.

## 3. Aplicar, depois da aprovação

- **Fases concluídas são histórico.** Não reescreva nem renumere o que já foi entregue
- Toda fase nova ou remodelada precisa de objetivo, entregáveis e critério de pronto
- Se a mudança nasce de um requisito novo, atualize antes `specs/mission.md` e
  `specs/tech-stack.md`: o roadmap é consequência deles, não o contrário

## 4. Propagar

Liste as specs de fase já escritas que ficaram inconsistentes e **espere a decisão do usuário**
antes de alterá-las. Mudança transversal (idioma, responsividade, política de testes) costuma
tocar constituição, várias specs e código: apresente a lista completa do que será alterado antes
de encostar em qualquer arquivo.

Com várias conversas em paralelo, avise a conversa gerente (GER) do novo roadmap: o `roadmap.md` é
arquivo comum e entra em conflito fácil.

## Restrições

- Não replanejar no meio de uma fase em andamento sem o usuário pedir
- Não apagar fase: mova para "Depois (não planejado)" com o motivo, ou registre a remoção
- Não transformar replanejamento em refatoração de código
