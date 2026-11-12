---
name: spec-de-fase
description: Inicia a próxima fase do roadmap — encontra a fase pendente em specs/roadmap.md, cria a branch, entrevista o usuário sobre escopo, decisões e contexto e escreve specs/AAAA-MM-DD-nome/ com requirements.md, plan.md e validation.md. Use quando o usuário disser "próxima fase", "especificar a fase", "spec de feature", "vamos começar a fase X" ou invocar /spec-de-fase.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Spec de fase

**Lê:** `specs/roadmap.md` (a próxima pendente), `specs/mission.md`, `specs/tech-stack.md` e as
specs das fases anteriores.
**Escreve:** `specs/AAAA-MM-DD-<nome>/` com `requirements.md`, `plan.md` e `validation.md`; e cria
a branch da fase.
**Decide:** **entrevista antes de escrever.** Fase pequena usa o formato curto do `AGENTS.md`, se
ele existir, em vez de improvisar uma "spec enxuta".

## Arquivos de referência

| Ao fazer | Leia |
|---|---|
| a entrevista (passo 3) | `references/entrevista.md` |
| escrever `validation.md` (passo 5) | `references/validacao.md` |

## Fluxo

### 1. Achar a fase

```bash
grep -n "^## Fase" specs/roadmap.md     # a ordem da fila é a ordem das seções
ls specs/                               # quais fases já têm pasta de spec
```

Cada fase é uma seção `## Fase N: Nome`, com a marca `[ ]`, `[~]` ou `[x]` no título. A próxima é
a primeira seção marcada `[ ]` que ainda não tem pasta em `specs/`. O `[ ]` também marca itens
soltos dentro das seções: não confunda item com fase. Havendo ambiguidade, confirme com o usuário.
Derive do nome da fase o nome em kebab-case.

### 2. Criar a branch

O nome é `fase-<<N>>-<<nome-kebab>>` (ex.: `fase-3-horarios-livres`). Primeiro, veja se há remoto:

```bash
git remote
```

- **Com remoto** (a saída traz `origin`): crie a partir da `origin/main`, sem trocar para a `main`.
  Num worktree, a `main` já está aberta na pasta principal e o `git checkout main` falha.

  ```bash
  git fetch origin && git switch -c fase-<<N>>-<<nome-kebab>> origin/main
  ```

- **Sem remoto** (a saída vem vazia): crie a partir da branch atual.

  ```bash
  git switch -c fase-<<N>>-<<nome-kebab>>
  ```

Se várias conversas trabalham em paralelo, confira antes que o número da fase está livre (roadmap,
`git branch -a`) e avise a conversa gerente (GER) que a fase começou.

### 3. Entrevistar, antes de escrever qualquer arquivo

Uma rodada só, agrupada em **escopo**, **decisões** e **contexto**. As perguntas estão em
`references/entrevista.md`. Se a resposta exigir algo fora de `specs/tech-stack.md`, pare: isso é
proposta de mudança de stack e precisa de aprovação humana antes de virar spec.

### 4. Ler a constituição e os precedentes

`specs/mission.md`, `specs/tech-stack.md` e as specs das fases anteriores, para repetir padrões já
estabelecidos em vez de inventar novos.

### 5. Escrever `specs/AAAA-MM-DD-<<nome>>/`

- **`requirements.md`**: escopo, fora de escopo, decisões com justificativa e alternativa
  descartada, contexto, "padrões a seguir" (o arquivo do repositório que serve de modelo), as notas
  do usuário (com as palavras dele e a data) e o teto de gasto, se houver. Modelo em
  `templates/fase/requirements.md`, quando o projeto o tiver
- **`plan.md`**: grupos numerados de tarefas, cada grupo implementável e revisável sozinho; o
  último grupo é sempre verificação. Inclua a tabela vazia "Alterações de escopo durante a fase"
- **`validation.md`**: conforme `references/validacao.md`

**Fato que sustenta decisão vem com fonte.** Cada afirmação sobre o código ou o ambiente leva
`arquivo:linha` e o commit em que foi lida. Decisão do usuário entra com as palavras dele e a data;
o que ela implica tecnicamente fica "a conferir" até alguém verificar o caminho (o host, a
credencial, o comando). Spec escrita de memória é a origem mais comum de retrabalho.

Se a fase gasta dinheiro (API paga, serviço por uso), o teto entra no `requirements.md`, na seção
"Teto de gasto", e o usuário o aprova junto com a spec.

### 6. Fechar

Resuma a spec e **pare**. A implementação é outro passo, com aprovação explícita do usuário. Termine
a mensagem com o fecho do projeto (Resumo, O que você faz agora, Worktree, Espera; formato em
`docs/operacao-das-conversas.md`).

## Restrições

- Nada de dependência fora de `specs/tech-stack.md` sem aprovação humana
- Escopo de uma fase = uma branch mergeável; se não couber, proponha dividir o roadmap
- Critério de validação vago precisa ser reescrito como comando ou passo a passo
- A spec vai à `main` antes do código da fase, quando o `AGENTS.md` assim mandar
