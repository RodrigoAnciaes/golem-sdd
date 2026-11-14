---
name: validar-fase
description: Percorre o validation.md da fase com evidência real, atualiza changelog e roadmap, e fecha a fase com PR e merge (pelo PEDIDO → LIBERADO com a conversa gerente) quando tudo passa. Use quando o usuário disser "validar a fase", "rodar a validação", "podemos fechar a fase?", "fechar e mergear" ou invocar /validar-fase.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Validar e fechar a fase

**Lê:** `specs/AAAA-MM-DD-<fase>/validation.md`, o código, e a saída real das suítes.
**Escreve:** as marcas no `validation.md`, o `CHANGELOG.md` e o `specs/roadmap.md`.
**Decide:** `[x]` **só com evidência**: comando e saída, nunca leitura do código. Item não
exercitado vira `[~]` com o motivo escrito; nunca `[x]` por analogia. Não fecha a fase com item
reprovado.

## 1. Validação com evidência

Percorra `specs/AAAA-MM-DD-<<nome>>/validation.md` item por item.

- **Verificações automatizadas:** rode cada comando e **mostre a saída real**. Nada de "deve
  passar": cole o que apareceu, incluindo a contagem de testes.
- **Verificações manuais:** liste os passos para o usuário executar e espere a confirmação dele.
  Você não marca item manual como pronto sozinho.
- **Casos de borda:** exercite-os de fato; se não houver como, diga que não foram cobertos.
- **Requisitos da constituição:** confira dependências contra `specs/tech-stack.md` e as convenções
  contra os arquivos de referência.
- **Correção de defeito:** o defeito reproduzido na `main` e ausente no head final da branch.

Falhou algo? Corrija, rode de novo, e só então siga. Item que não pôde ser verificado é reportado
como não verificado, nunca como aprovado.

## 2. Reconciliar spec e código

Antes de fechar, compare o que foi implementado com `requirements.md`:

- Divergência que veio para ficar → atualize a spec
- Divergência que foi engano → corrija o código
- Pergunta em aberto do `requirements.md` → responda ou mova para o roadmap

## 3. Registro

- `CHANGELOG.md` atualizado (skill `changelog`)
- Fase marcada `[x]` em `specs/roadmap.md`: a seção dela sai do corpo e vira uma linha na tabela de
  concluídas, com data e nome da branch
- Decisão cara de reverter tomada durante a fase vira ADR (skill `adr`)
- Hipótese refutada ou defeito que custou mais de uma rodada vira lição (skill `licao`)
- `python3 .claude/regua.py --conferir`: o índice das lições em dia. Índice desencontrado é defeito
  da fase, não detalhe de arrumação

## 4. Fechamento

Ordem: a revisão sobre o diff primeiro, conforme o bloco "Como o Golem trabalha aqui" do
`AGENTS.md` (o revisor, o validador e o guardião, cada um com `sempre`, `perguntar` ou `nunca`; o
caminho rápido e o guardião como a regra 11 os descreve); a prova (a CI, ou a suíte rodada
localmente se a CI não roda) **uma vez**, no head final. Com o revisor uma vez por fase, a revisão
que a `implementar-fase` já fez sobre o diff da fase vale aqui, se nada mudou depois dela.

Só com tudo acima verde, e **só se o usuário pedir** o commit:

1. Commit só dos arquivos da fase (`git add <arquivos>`, nunca `git add -A`), push da branch e PR
   para a `main`.
2. **PEDIDO → LIBERADO.** Mande à conversa gerente (GER) `PEDIDO: merge do PR <pr>, head <sha>,
   base <sha>, prova: <a linha de resumo da suíte ou o CI no head>; <os vereditos da revisão>` e
   espere o `LIBERADO`. O formato e quem libera o quê estão em `docs/operacao-das-conversas.md`.
   Sem GER no projeto, o usuário faz esse papel. O merge de nível 3 (repositório de terceiros,
   produção, o que o `AGENTS.md` listar) espera também a palavra do usuário nesta conversa.
3. **Conferir e mergear em chamadas separadas.** Numa chamada, `git ls-remote origin` e
   `gh pr view <pr> --json headRefOid`: leia os shas e compare com os do LIBERADO. Só então, **em
   outra chamada**, `gh pr merge <pr> --squash --match-head-commit <sha>` (ou o método que o
   `AGENTS.md` define). Encadeado no mesmo comando, o merge roda antes de alguém ler o sha.
   `--match-head-commit` prende o head, não a base: se a `main` andou desde a prova, pare e avise
   a GER.
4. Depois do PEDIDO, não empurre mais commits na branch sem avisar a GER.
5. O sha do merge só vai à mensagem **depois** de lido na saída do `git log` ou do `gh`.

**Sem remoto** (`git remote` vazio): não há PR, push, GER que confira nem `--match-head-commit`. O
merge é local, na `main`, e é **nível 3**: quem o faz é o usuário. Entregue a ele o
`git log --oneline main..fase-N-nome`, a prova no head da branch e o comando
(`git switch main && git merge --no-ff fase-N-nome`), e espere ele dizer que mergeou.

## Restrições

- Nunca marcar item como aprovado sem evidência
- Nunca fazer merge com validação incompleta, mesmo que "falte pouco"
- Nunca `git merge` local na `main` (sem remoto, ele é do usuário, acima), reescrever histórico
  nem forçar push
- Depois do merge, confirme que a `main` continua verde
- Termine com o fecho do projeto (Resumo, O que você faz agora, Worktree, Espera)
