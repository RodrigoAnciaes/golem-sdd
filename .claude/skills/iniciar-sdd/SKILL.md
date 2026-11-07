---
name: iniciar-sdd
description: Prepara um projeto para trabalhar com spec-driven development — cria a estrutura specs/, AGENTS.md, CHANGELOG.md, docs/licoes/ e template de PR, e confere quais skills de SDD estão instaladas. Use quando o usuário disser "iniciar SDD neste projeto", "preparar o projeto para specs", "montar o ambiente de spec-driven", "reproduzir meu setup de SDD aqui" ou invocar /iniciar-sdd.
---

# Iniciar ambiente SDD

**Lê:** o repositório, para descobrir o que já existe.
**Escreve:** `specs/`, `AGENTS.md`, `CHANGELOG.md`, `docs/licoes/` e o template de PR, **só o que
falta.**
**Decide:** o que já existe e não deve ser recriado. Sobrescrever o `AGENTS.md` de um projeto vivo
apaga regra comprada com falha.

Deixa o repositório pronto para o fluxo. **Não escreve a constituição**: isso é a skill
`constituicao`, chamada depois.

**Os modelos.** O `CHANGELOG.md`, o modelo de PR e o modelo de ADR saem de três arquivos curtos do
kit: `templates/CHANGELOG.md`, `templates/pull_request_template.md` e `templates/adr.md`. Procure
`templates/` na raiz do projeto; se não estiver lá, pergunte ao usuário o caminho da pasta do kit.
Não invente o conteúdo de memória.

## Fluxo

### 1. Diagnóstico

Antes de criar qualquer coisa, levante e reporte:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null && git log --oneline -1
ls specs/ docs/ .claude/skills/ AGENTS.md CLAUDE.md CHANGELOG.md 2>/dev/null
```

- É repositório git? Se não, pergunte antes de rodar `git init`.
- Projeto novo ou já tem código? Legado muda a ordem: a constituição descreve o que existe.
- Já existe `specs/` ou instruções de agente? **Nunca sobrescreva**: proponha o merge do conteúdo.

### 2. Criar a estrutura

```
specs/                          # constituição + specs de fase (vazio por enquanto)
AGENTS.md                       # instruções permanentes do agente
CLAUDE.md                       # uma linha apontando para o AGENTS.md
CHANGELOG.md                    # registro por data (de templates/CHANGELOG.md)
docs/operacao-das-conversas.md  # papéis, níveis de autonomia, PEDIDO/LIBERADO, o fecho
docs/licoes/README.md           # o formato das lições
docs/adr/modelo.md              # o modelo de ADR (de templates/adr.md)
.claude/skills/                 # skills de SDD versionadas com o projeto
.claude/regua.py                # gera e confere o índice das lições
.github/pull_request_template.md  # o modelo de PR (de templates/pull_request_template.md)
```

A pasta `specs/` vazia não entra no git: ela passa a existir de verdade com a constituição.

Se o projeto usa o Codex, rode também `python3 .claude/instalar_codex.py`: ele gera
`.agents/skills/`, `.codex/agents/` e `.codex/hooks.json` a partir de `.claude/` (detalhe no
`README.md` do kit, "Usando com o Codex").

O `AGENTS.md` precisa conter: a ordem de leitura das specs, os comandos reais do projeto, as
convenções, e as regras. As que não se negociam:

- spec antes do código; uma fase por branch;
- nenhuma dependência nova sem aprovação;
- revisor e validador independentes antes de marcar uma tarefa feita;
- todo fato que sustenta spec ou decisão vem com `arquivo:linha`;
- hipótese refutada vira lição;
- parar e perguntar quando algo exige decisão humana.

Preencha os comandos lendo `package.json`, `Makefile`, `pyproject.toml` ou equivalente. Não invente
comando: se não achar, pergunte.

### 3. Conferir as peças do kit

```bash
ls .claude/skills/
git add docs/licoes                   # a régua só indexa as lições que o git conhece
python3 .claude/regua.py --gerar      # escreve .claude/indice/licoes.yaml
python3 .claude/regua.py --conferir
```

No Windows, `python` ou `py -3` no lugar de `python3`. Confira que a última linha do índice é
`total:` com o número de lições de `docs/licoes/` (fora o `README.md`). Se o `--gerar` recusar
porque nenhuma lição está no git, faltou o `git add`.

Skills esperadas: `constituicao`, `spec-de-fase`, `implementar-fase`, `validar-fase`,
`replanejar-roadmap`, `auditar-specs`, `adr`, `changelog`, `licao`, `iniciar-conversa`,
`sessao-gerente` e esta. Reporte as que faltam.

### 4. Reprodutibilidade

- Faça o commit de `.claude/skills/` junto do projeto, quando o usuário pedir: é isso que faz o
  ambiente ser reproduzível por quem clonar o repositório. Confira com
  `git check-ignore -v .claude/skills/adr/SKILL.md` que o `.gitignore` não engole a pasta.
- Registre no `AGENTS.md` quais skills o projeto espera ter disponíveis.
- Avise o usuário que **skills novas só aparecem em uma sessão nova**.

### 5. Fechar

Mostre a árvore criada, o que foi preenchido e o que ficou como `<< a preencher >>`. Ofereça a
skill `constituicao` como próximo passo. Termine com o fecho (Resumo, O que você faz agora,
Worktree, Espera; formato em `docs/operacao-das-conversas.md`).

## Restrições

- Nunca sobrescrever arquivo existente sem mostrar o diff e pedir confirmação.
- Não criar `specs/mission.md` vazio: documento vazio dá falsa sensação de spec pronta.
- Não commitar nada sem o usuário pedir.
