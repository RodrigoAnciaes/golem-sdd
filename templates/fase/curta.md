# <Nome da fase> — Spec curta

> Modelo do formato curto (regra 1 do `AGENTS.md`): só para a fase **sem borda externa** (API
> pública, outro sistema), **sem deploy** e que **cabe num dia**. Mora em
> `specs/AAAA-MM-DD-nome/requirements.md`, e o `validation.md` vem na mesma pasta, numa página;
> aqui os dois aparecem juntos para ver a forma. O que não encolhe: os critérios são comando ou
> passo a passo, e a spec é aprovada antes do código.

## requirements.md

### Objetivo

O que passa a existir, em uma frase.

> Ex.: A lista de horários mostra o encaixe com um selo "encaixe".

### Escopo e fora de escopo

> Ex.: R1. O horário de encaixe sai com `"encaixe": true` em `GET /horarios`. Fora: a tela de
> marcar encaixe (é outra fase).

### Decisões

Cada uma com a alternativa descartada; a do usuário, com as palavras dele e a data.

> Ex.: O campo vem do modelo que já existe, sem coluna nova; descartada a coluna (migração para
> um dado derivável).

### Contexto

Os fatos com a fonte (`arquivo:linha`).

> Ex.: O encaixe já é marcado em `src/agenda/modelos.py:31` (`tipo = "encaixe"`).

### Como fazer

O plano, numa lista curta, no lugar do `plan.md`. O último passo é a verificação.

1. `src/agenda/horarios.py`: incluir `encaixe` na resposta.
2. Teste novo em `tests/agenda/test_horarios.py`.
3. Rodar o `validation.md`.

## validation.md

- [ ] `<comando>` → <resultado esperado>

> Ex.: `pytest tests/agenda -q` → a linha de resumo com 0 falhas e 0 pulados, incluindo o teste
> novo do encaixe.

- [ ] Caso de borda: <entrada inválida ou dependência indisponível> → <o que acontece>

> Ex.: médico sem encaixe no dia → nenhum horário com `"encaixe": true`.

- [ ] `CHANGELOG.md` atualizado e a fase marcada `[x]` no `specs/roadmap.md`.
