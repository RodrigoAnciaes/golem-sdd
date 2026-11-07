# Projeto <nome>: fatos estáveis para a GER

Copie este arquivo como `references/<nome-do-projeto>.md` e preencha. Aqui vão fatos que mudam
pouco. O estado do dia (frentes, fila, bloqueios) vai no registro vivo da GER, não aqui.

## Lugares

- **Pasta principal:** `<caminho>`. Diga o que só existe nela (ambiente virtual, dados locais,
  arquivos fora do Git) e quantas fases trabalham nela ao mesmo tempo (o normal é uma; as outras,
  em worktree).
- **Worktrees:** `<caminho-base>/<nome>`. Diga o que **falta** neles (ambiente virtual, dados,
  ganchos) e como a fase contorna.
- **Interpretador:** o caminho absoluto, se não estiver no PATH.
- **Repositório remoto:** `<dono>/<repo>`, visibilidade, se a `main` tem proteção de branch.
- **Outros repositórios** que as fases leem: sempre pelo `origin/main` depois de um `fetch`.

## Armadilhas de ambiente conhecidas

Exemplos do que costuma entrar aqui:

- **Git Bash no Windows:** `git show origin/main:arquivo` é reescrito pelo MSYS; use
  `MSYS_NO_PATHCONV=1` na frente.
- **Fim de linha:** com `core.autocrlf=true`, cópia para Linux sai em CRLF; use
  `-c core.autocrlf=false -c core.eol=lf`, e `eol=lf` para `.sh` no `.gitattributes`.
- **`.claude/` no `.gitignore`:** arquivo novo ali só viaja com exceção `!`. Confira com
  `git check-ignore -v` e com a lista de arquivos do PR.
- **Índice só de arquivos rastreados:** pasta nova sem `git add` fica fora do `regua.py --gerar`, e
  o `--conferir` dá ok falso. Ordem: `git add`, depois `--gerar`.

## Regras da casa que a GER lembra às fases

- Spec (`requirements`, `plan`, `validation`) **na `main` antes do código**, se o `AGENTS.md` assim
  mandar. O formato curto, quando existir, só para fase sem borda externa, sem deploy e que cabe
  num dia.
- Uma fase por branch `fase-N-nome`. O método de merge: `<squash | merge commit>`.
- Quem libera o quê (nível da conversa, da GER, do usuário): ver `docs/operacao-das-conversas.md`.
- Revisor e validador independentes antes de marcar tarefa feita; o caminho rápido (só revisor)
  para PR só de docs ou de testes, se o projeto o adotar.
- O modelo e o esforço que o projeto usa nas conversas e nos subagentes.
- Textos a pessoas de fora do projeto passam pelo usuário; nenhuma conversa fala direto com elas.

## CI e prova

- Onde a CI roda, quantos jobs, o que é verde.
- Se a CI não roda (cobrança, infraestrutura), qual é a prova local aceita e como se registra.
- `--match-head-commit` prende o head, não a base: logo antes do merge, `git ls-remote` da `main`
  tem de bater com a base da prova; se mudou, a prova roda de novo.
