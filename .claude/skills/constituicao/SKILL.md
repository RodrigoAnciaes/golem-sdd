---
name: constituicao
description: Cria a constituição de um projeto em specs/ (mission.md, tech-stack.md, roadmap.md) a partir do briefing dos stakeholders, entrevistando o usuário antes de escrever qualquer arquivo. Funciona também para projeto legado, reconstruindo a constituição a partir do código existente. Use quando o usuário disser "criar constituição", "começar projeto novo com SDD", "escrever as specs de produto", "documentar este projeto legado" ou invocar /constituicao.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Constituição do projeto

**Lê:** o repositório inteiro quando o projeto é legado; o briefing do usuário quando é novo.
**Escreve:** `specs/mission.md`, `specs/tech-stack.md` e `specs/roadmap.md`.
**Decide:** **entrevista antes de escrever qualquer arquivo.** Constituição escrita por suposição
é pior que nenhuma: ela vira a referência que todo mundo cita depois.

Cria os três documentos que governam todo o resto do trabalho. Nada de código nesta etapa.

## Arquivos de referência

Carregue **apenas** o que estiver escrevendo no momento. Cada um traz seções obrigatórias,
critérios de qualidade, falhas comuns e perguntas de entrevista:

| Ao escrever | Leia |
|---|---|
| `mission.md` | `references/missao.md` |
| `tech-stack.md` | `references/tech-stack.md` |
| `roadmap.md` | `references/roadmap.md` |
| qualquer um deles em projeto que já tem código | `references/legado.md` **primeiro** |

## Fluxo

### 1. Ler o insumo

`briefing.md`, `README.md`, `TODO.md`, issues, documentos apontados pelo usuário. Se já existe
código, leia `references/legado.md` e siga a ordem invertida descrita lá: levantamento, devolução
do entendimento, correção humana, só então documento.

### 2. Entrevistar antes de escrever

Uma rodada de perguntas, agrupada em três temas: missão, stack e roadmap. **Nenhum arquivo é
escrito antes das respostas.** As perguntas de cada tema estão nos arquivos de referência; escolha
as que o insumo ainda não respondeu e descarte o resto.

Resposta do usuário que afirma um fato técnico ("já temos acesso a X", "isso já existe") entra com
as palavras dele e fica marcada "a conferir" até alguém achar o caminho no código ou na config.

### 3. Escrever `specs/`

Um documento por vez, carregando a referência correspondente antes de cada um. Ao terminar cada
documento, confira-o contra a tabela de falhas comuns da referência.

### 4. Fechar

- Mostre o que foi escrito e o que ficou como suposição (`⚠️` em legado)
- Liste as perguntas em aberto e quem responde
- Aponte a Fase 1 como próximo passo, **sem** implementá-la (a skill `spec-de-fase` começa por ela)

## Restrições

- Escolha de stack sem versão fixa e sem justificativa não entra
- Fase de roadmap sem critério de pronto observável não entra
- Missão sem não-objetivos está incompleta
- Em legado, descreva o que existe; o que se deseja vira roadmap
