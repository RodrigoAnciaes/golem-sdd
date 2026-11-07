---
name: auditar-specs
description: Audita a distância entre o que as specs dizem e o que o código faz — dependências fora da stack, fases marcadas erradas, requisitos não implementados e comportamento sem respaldo em spec. Só relata, não corrige. Use quando o usuário disser "as specs estão em dia?", "auditar as specs", "o que saiu do combinado", "revisar a constituição" ou invocar /auditar-specs.
---

# Auditar specs contra o código

**Lê:** `specs/` inteiro e o código que cada spec descreve. É a skill que mais lê: comece pelos
manifestos e pelas specs, e abra o código só para conferir um ponto concreto.
**Escreve:** **nada.** O resultado é um relatório na conversa; corrigir é decisão do usuário.
**Decide:** o que é desvio do código e o que é spec desatualizada. São defeitos diferentes, com
donos diferentes, e confundi-los faz corrigir o lado errado.

Spec envelhece em silêncio. Esta auditoria torna o desvio visível antes que ele custe caro.

## O que verificar

### 1. Stack

Compare `specs/tech-stack.md` com o manifesto de dependências real (`package.json`,
`pyproject.toml`, `go.mod`, …).

- Dependência instalada e não declarada: como entrou?
- Versão divergente da registrada
- Comando de teste ou lint documentado que não existe mais
- Tecnologia listada em "o que não usamos" e presente no código

### 2. Roadmap

- Fase marcada `[x]` cujos entregáveis não estão no código
- Fase `[ ]` já implementada, marcada errada
- Funcionalidade em produção que nunca passou por fase alguma

### 3. Specs de fase

- Requisito de `requirements.md` sem implementação correspondente
- Item de `validation.md` que hoje falharia
- "Fora de escopo" que foi implementado assim mesmo
- Perguntas em aberto que continuam abertas depois do merge

### 4. Missão

- Funcionalidade que não serve a nenhuma persona nem a nenhum critério de sucesso
- Não-objetivo violado
- Termo de domínio usado no código com sentido diferente do glossário

### 5. Lições e regras

- `python3 .claude/regua.py --conferir`: o índice das lições bate com `docs/licoes/`
- Lição que manda uma ação obrigatória sem a regra correspondente no `AGENTS.md`

## Relatório

Uma tabela, ordenada por custo de deixar como está:

| Desvio | Onde | Evidência | Correção sugerida |
|---|---|---|---|
| dependência não declarada | `package.json:24` | `zod 3.23.8` | declarar em `tech-stack.md` ou remover |

Para cada desvio, diga de que lado corrigir: **spec desatualizada** (o código está certo, o
documento envelheceu) ou **código fora do combinado** (o documento está certo, alguém desviou).
São correções opostas: não misture.

## Restrições

- Não altere nenhum arquivo nesta skill; proponha e espere
- Evidência sempre com arquivo e linha, lidos no commit atual (diga qual)
- Não confunda desvio com dívida já registrada em ADR: cite o ADR e siga
