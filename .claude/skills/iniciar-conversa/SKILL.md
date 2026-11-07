---
name: iniciar-conversa
description: Abre uma conversa nova no repositório — confere o estado do git e o registro da conversa gerente, descobre em que fase estamos e abre só os documentos que a tarefa de hoje exige, em vez de mandar ler tudo. Use no começo de qualquer sessão, quando o usuário disser "onde paramos", "continuando", "bom dia", "o que tem para hoje" ou invocar /iniciar-conversa.
---

# Abrir uma conversa

**Lê:** `git status` e `git log`, o registro da conversa gerente (GER) se houver, o roadmap pela
busca, e **só então** o documento que a tarefa pedir.
**Escreve:** nada. Esta skill não altera arquivo nenhum.
**Decide:** qual é a tarefa de hoje e quais documentos ela exige. Para e pergunta se os registros e
o estado do git não concordarem.

> Por que esta skill existe: num projeto com muitas fases, o acervo de `.md` passa de uma janela de
> contexto. Ler "tudo" não é caro, é **impossível**. Aqui se lê o mínimo e se busca o resto.

## 1. O estado, sempre nesta ordem

```bash
git branch --show-current
git status --short
git log --oneline -5
git worktree list
```

Se o projeto usa uma GER, o registro vivo dela (o lugar está em `docs/operacao-das-conversas.md`)
diz quem está fazendo o quê. Registro fora do Git costuma morar na pasta principal, que um worktree
não enxerga pelo caminho relativo. A pasta principal é o pai do `.git` comum:

```bash
dirname "$(git rev-parse --path-format=absolute --git-common-dir)"
```

Leia só a parte mais recente do registro. O resto se busca (`grep`) quando a tarefa pedir um fato
passado.

⚠️ **Se o registro e o git discordarem, pare e pergunte.** Discordância típica: o registro diz que
uma fase está na `main` e o log não mostra o merge; ou o `git status` traz arquivo que o registro
não menciona. Arquivo alheio na árvore pode ser **outra conversa trabalhando no mesmo diretório**:
nesse caso, commit por caminho explícito e nada de `git add -A`.

## 2. A fase de hoje

```bash
grep -n "^## Fase\|\[~\]" specs/roadmap.md   # a fila e o que está em andamento
ls -d specs/*/                               # quais fases já têm spec
```

Não leia o `specs/roadmap.md` inteiro para isso. Ele é para quando você precisa do **porquê** de uma
fase estar onde está.

Se a tarefa já tem spec, o que vale é `specs/AAAA-MM-DD-<fase>/`: `requirements.md` primeiro,
`plan.md` e `validation.md` quando for implementar ou validar.

## 3. Abra só o que a tarefa exige

Não leia esta tabela inteira: ache a sua linha.

| A tarefa é | Abra | Não precisa de |
|---|---|---|
| **entender o repositório pela primeira vez** | `README.md`, `specs/mission.md` | o resto |
| **escrever ou revisar spec** | `specs/mission.md`, a spec da fase | comandos, deploy |
| **mexer em código** | o `README.md` da pasta, `specs/tech-stack.md` | roadmap |
| **decidir stack ou dependência** | `specs/tech-stack.md`, `docs/adr/` | o resto |
| **rodar teste** | a seção "Comandos reais" do `AGENTS.md` (o comando literal mora só ali) | specs de fase |
| **coordenar ou pedir merge** | `docs/operacao-das-conversas.md` | specs de fase |

## 4. As lições da área, antes de tocar nela

```bash
grep "area:" .claude/indice/licoes.yaml | sort | uniq -c          # as áreas que têm lição
grep -B1 -A4 'area: "deploy"' .claude/indice/licoes.yaml          # as da sua área (aqui, deploy)
```

No índice, o valor vem entre aspas (`area: "deploy"`), e o id da lição é a linha de cima.

Abra em `docs/licoes/` só as lições que a busca apontar. Se o projeto tiver um gancho que injeta as
lições automaticamente, não varra a pasta à mão.

## 5. Antes de trabalhar, confirme o combinado

Diga ao usuário, em três linhas: **onde paramos**, **o que você entendeu como tarefa de hoje** e
**o que vai fazer primeiro**. Se houver mais de uma leitura possível do pedido, pergunte agora: é
mais barato que desfazer depois. Frase curta sem ponto de interrogação ("é só…", "não daria…")
pode ser pergunta: responda antes de agir.

Com GER no projeto, a conversa nova se apresenta a ela na primeira mensagem, com o worktree e a
tarefa. Os papéis, os níveis de autonomia e o fecho das mensagens (Resumo, O que você faz agora,
Worktree, Espera) estão em `docs/operacao-das-conversas.md`.

⚠️ Confira se **hoje há deploy** ou outro evento de calendário. Se o registro não disser,
pergunte: deploy não combinado é o erro mais caro de um projeto com várias conversas.
