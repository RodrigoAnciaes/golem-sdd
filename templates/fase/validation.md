# <Nome da fase> — Validação

> Modelo. Mora em `specs/AAAA-MM-DD-nome/validation.md`. É o contrato de merge: se tudo passa, a
> fase acabou. Escreva **antes** de implementar. Cada critério é um comando com o resultado
> esperado, ou um passo a passo (regra 4 do `AGENTS.md`).
>
> Marcação, feita pela skill `validar-fase`: `[x]` com a saída colada; `[~]` não exercitado, com o
> motivo; nunca `[x]` por leitura do código ou por analogia.

## Verificações automatizadas

- [ ] `<comando>` → <resultado esperado>

> Ex.: `pytest tests/agenda -q` → 14 passados, 0 falhas, 0 pulados, incluindo os 3 novos de horário.

## Verificações manuais

Passo a passo que uma pessoa executa: abrir X, fazer Y, ver Z.

> Ex.: Abrir `localhost:8000/agenda`, escolher o médico 1 e amanhã, ver a lista começando às 8h00.

## Casos de borda

Toda fase tem ao menos uma entrada inválida e uma dependência indisponível.

> Ex.: `GET /horarios?medico=1&data=31-02` → 400 com `{"erro": "data inválida"}`, nada gravado.

## Requisitos da constituição

Nenhuma dependência fora da stack, as convenções respeitadas, os requisitos não-funcionais da fase.

> Ex.: `git diff main -- requirements.txt` vazio (nenhuma dependência nova).

## Registro

- [ ] `CHANGELOG.md` atualizado
- [ ] fase marcada `[x]` no `specs/roadmap.md`, com data e branch
- [ ] perguntas em aberto do `requirements.md` respondidas ou movidas para o roadmap

## Não exigido nesta fase

O que ficou de fora de propósito, para a revisão não cobrar o que nunca foi combinado.

> Ex.: Desempenho com mais de 10 mil consultas: medido na fase de relatórios.
