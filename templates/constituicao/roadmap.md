# Roadmap

> Modelo. Detalhe só as três próximas fases; o resto vai para "Depois". Fatie por funcionalidade
> vertical (o que o usuário passa a conseguir fazer), não por camada ("backend", "frontend").

**Formato:** cada fase é uma seção `## Fase N: Nome`, com a marca no título, e a branch dela é
`fase-N-nome` (o nome em kebab-case). As skills buscam por `^## Fase`: outro formato some da busca.

**Marcação:** `[ ]` pendente · `[~]` em andamento · `[x]` concluída. A próxima fase é a primeira
`[ ]` desta lista. Mantenha a marcação honesta: o agente a lê para saber o que vem.

**O teste do tamanho:** a validação cabe em cinco linhas verificáveis; vira uma branch mergeável
sozinha; o diff se revisa de uma vez; abandonada no meio, a `main` continua funcionando.

## Concluídas

| Fase | Data | Branch |
|---|---|---|
| Ex.: Fase 1: Esqueleto da API | AAAA-MM-DD | `fase-1-esqueleto-api` |

## Fase 2: Nome curto  `[ ]`

**Objetivo:** o que passa a existir, em uma frase.

> Ex.: O paciente vê os horários livres de um médico numa data.

- [ ] entregável
- [ ] entregável

**Pronto quando:** o comando que passa, a tela que abre ou a rota que responde.

> Ex.: `curl localhost:8000/horarios?medico=1&data=AAAA-MM-DD` devolve 200 com a lista de horários
> livres.

**Depende de:** a fase anterior, só quando houver dependência real.

## Fase 3: Nome curto  `[ ]`

<< mesma estrutura >>

## Depois (não planejado)

Ideias que ainda não viraram fase, uma linha cada.

> Ex.: Lembrete automático um dia antes da consulta.
