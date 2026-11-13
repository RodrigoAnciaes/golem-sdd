---
name: changelog
description: Mantém o CHANGELOG.md na raiz do projeto, com seções por data geradas a partir do histórico do git. Use quando o usuário disser "atualizar o changelog", "gerar changelog", pedir para registrar o que mudou antes de um merge, ou invocar /changelog.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Changelog

**Lê:** `git log` desde a última seção e o `CHANGELOG.md` atual.
**Escreve:** **só** o `CHANGELOG.md`, acrescentando no topo. Nunca reescreve seção antiga: o
arquivo é cronológico por desenho.
**Decide:** o que é mudança visível (entra) e o que é ruído de implementação (não entra).

## Fluxo

### 1. Descobrir o ponto de partida

```bash
head -20 CHANGELOG.md 2>/dev/null
```

- **Arquivo não existe:** gere o histórico completo.
- **Arquivo existe:** encontre o cabeçalho de data mais recente (`## AAAA-MM-DD`) e considere só o
  que veio depois.

### 2. Coletar os commits

Histórico completo:

```bash
git log --date=short --pretty=format:"%ad %s" --reverse
```

Somente o que é novo (a partir da última data registrada):

```bash
git log --since="AAAA-MM-DD" --date=short --pretty=format:"%ad %s"
```

Trabalho de uma branch específica, antes do merge:

```bash
git log origin/main..HEAD --date=short --pretty=format:"%ad %s"
```

### 3. Escrever

Agrupe por data, mais recente no topo. **Reescreva** o assunto do commit em termos do efeito para
quem usa o sistema; não copie a mensagem literal. Descarte ruído (`wip`, `fix typo`, merges).

```markdown
# Changelog

## 2026-09-01

### Adicionado
- Validação automática dos campos obrigatórios no formulário de cadastro

### Corrigido
- A consulta marcada no último horário do dia não aparecia na agenda do médico
```

Use as seções `Adicionado`, `Alterado`, `Corrigido`, `Removido`; omita as vazias. Em projeto
pequeno, uma lista simples por data também serve, desde que consistente com o que já existe no
arquivo.

### 4. Fechar

Mostre o trecho novo para revisão e inclua o `CHANGELOG.md` no commit da fase.

## Restrições

- Rodar da raiz do projeto (mesmo diretório do `.git/`)
- Nunca reescrever seções de datas já registradas
- Se nada novo houver desde a última data, diga isso e não altere o arquivo
- O `CHANGELOG.md` é arquivo comum: com várias fases em paralelo, conflito nele se resolve
  mantendo as duas entradas, nunca escolhendo um lado
