# <Nome da fase> — Plano

> Modelo. Mora em `specs/AAAA-MM-DD-nome/plan.md`. Grupos numerados, cada um implementável e
> revisável sozinho; o último é sempre verificação. A skill `implementar-fase` executa um grupo por
> vez, com revisor e validador ao fim de cada um.

## G1 — <nome do grupo> (R1, R2)

- [ ] tarefa, com o arquivo que muda

> Ex.: - [ ] `src/agenda/horarios.py`: função que calcula os horários livres de um médico numa data.

**Revisão:** revisor + validador | caminho rápido (só docs ou testes: só o revisor)

## G2 — <nome do grupo> (R3)

- [ ] tarefa

> Ex.: - [ ] `src/agenda/rotas.py`: rota `GET /horarios`, com erro 400 para data inválida.

## G3 — Verificação

- [ ] rodar o `validation.md` inteiro, com a saída colada
- [ ] spec e código reconciliados

## Alterações de escopo durante a fase

Quando a realidade contradiz a spec: o que mudou, por quê, quem decidiu e quando.

| Data | O que mudou | Por quê | Decidido por |
|---|---|---|---|
| Ex.: AAAA-MM-DD | intervalo de 30 para 20 minutos | as clínicas usam 20 | o usuário: "pode ser 20" |

## Estado para a retomada

Onde o trabalho parou, para a conversa seguinte ou depois de uma compactação de contexto.

> Ex.: G1 feito e revisado (sem bloqueio, valida); G2 começa pela rota.
