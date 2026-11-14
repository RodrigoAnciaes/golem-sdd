---
id: frontmatter-invalido-some-com-o-agente-sem-aviso
data: 2026-11-13
area: processo
tipo: armadilha
custo: "uma verificação manual inteira refeita; o revisor e o validador do grupo que quebrou o arquivo não viram nada"
gatilho: "a fase 1 reescreveu a description do revisor.md com um ': ' no meio, e numa sessão nova o agente revisor não existia mais"
refs:
  - ".claude/agents/revisor.md:3 (a description; no commit 48970f9, \"do AGENTS.md: por grupo\")"
  - ".claude/tests/test_codex.py:276 (test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido)"
gatilhos:
  - '\.claude/agents/[^/]+\.md$'
  - '/SKILL\.md$'
---

**O que se achava:** que a `description` de um agente ou de uma skill é texto livre, e que um
agente com o frontmatter quebrado daria erro visível ao carregar.

**O que é:** o frontmatter é YAML. Um `: ` num valor sem aspas o torna inválido ("mapping values are
not allowed here"), e o Claude Code descarta o agente **calado**. Na sessão de teste de 2026-11-13,
a chamada voltou "Agent type 'revisor' not found. Available agents: ..., validador", e o agente
caiu num `general-purpose` no Sonnet, sem as instruções do revisor. A suíte (122 testes), o
revisor, o validador e o instalador do Codex passaram: o instalador lê o frontmatter com uma
expressão regular, e não com YAML.

**Como perceber da próxima vez:**
1. "Agent type '<nome>' not found" numa sessão em que `.claude/agents/<nome>.md` existe: o
   frontmatter desse arquivo não é YAML válido. Procure `: `, ` #` ou uma aspa sem fechar num valor.
2. Ao editar o frontmatter, troque `: ` por `, ` no texto ou ponha o valor entre aspas. O
   `test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido` acusa o caso.
3. Mudança num agente só se prova numa sessão nova que o chame pelo nome. Ler o arquivo, ou
   rodar a suíte, não prova que ele carrega.
