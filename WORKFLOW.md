# O fluxo, etapa por etapa

Cada etapa tem uma skill que a dispara, uma entrada, uma saída e um ponto em que **o usuário
decide**. O agente decide o detalhe de implementação sozinho; o que muda o produto, a stack, o
escopo ou o que sai para fora é do usuário (regra 10 do `AGENTS.md`).

```
preparar → constituição → spec da fase → implementar por grupos → validar a fase → replanejar
                               ▲            (revisor + validador         │
                               └──────────── a cada grupo)  ◄────────────┘
```

---

## 0. Preparar o projeto

| | |
|---|---|
| **Skill** | `iniciar-sdd` ("iniciar SDD neste projeto") |
| **Entra** | o repositório como está |
| **Sai** | `specs/`, `AGENTS.md`, `CHANGELOG.md` e o modelo de PR, **só o que falta** |
| **O usuário decide** | o que fazer com o que já existe: a skill nunca sobrescreve `AGENTS.md` nem `specs/`; ela propõe a junção |

---

## 1. Constituição

| | |
|---|---|
| **Skill** | `constituicao` ("criar a constituição") |
| **Entra** | o briefing do usuário (projeto novo) ou o código existente (projeto legado) |
| **Sai** | `specs/mission.md` (o problema, para quem, o sucesso, os não-objetivos, o glossário), `specs/tech-stack.md` (as escolhas com versão fixa e o porquê; os comandos literais vão para a seção "Comandos reais" do `AGENTS.md`), `specs/roadmap.md` (as fases, no formato `## Fase N: Nome`, cada uma com critério de pronto) |
| **O usuário decide** | responde à entrevista, que vem **antes** de qualquer arquivo, e aprova os três documentos |

A constituição é o que todas as specs citam depois. Escrita por suposição, ela é pior que nenhuma.
Modelos na pasta `templates/constituicao/` do kit (a pasta `templates/` não precisa ir para o
projeto).

**O teste do tamanho de fase.** Uma fase do roadmap tem o tamanho certo quando a validação cabe em
cinco linhas verificáveis, ela vira uma branch mergeável sozinha, alguém revisa o diff inteiro de
uma vez e, abandonada no meio, a `main` continua funcionando. Falhou em um? Divida.

---

## 2. Spec da fase

| | |
|---|---|
| **Skill** | `spec-de-fase` ("próxima fase") |
| **Entra** | a próxima fase pendente do `specs/roadmap.md`, a constituição e as specs anteriores (para repetir padrões) |
| **Sai** | a branch da fase (`fase-N-nome`) e `specs/AAAA-MM-DD-nome/` com `requirements.md`, `plan.md` e `validation.md` |
| **O usuário decide** | responde à entrevista (escopo, decisões, contexto) e **aprova a spec**; a implementação é outro pedido |

- **`requirements.md`**: o escopo, o fora de escopo, as decisões com a alternativa descartada, o
  contexto e o padrão a seguir no código.
- **`plan.md`**: grupos numerados, cada um implementável e revisável sozinho; o último grupo é
  sempre verificação.
- **`validation.md`**: o contrato de merge. Cada critério é um comando com o resultado esperado ou
  um passo a passo (regra 4). Escrito **antes** de implementar: critério escrito depois só descreve
  o que o código já faz.

**Formato curto.** Fase pequena (sem borda externa, sem deploy, cabe num dia) usa só
`requirements.md` e `validation.md`, numa página, com o plano numa seção "Como fazer" dentro do
`requirements.md` (regra 1 do `AGENTS.md`). Os critérios continuam sendo comando.

Se a entrevista revelar algo fora de `specs/tech-stack.md`, a skill para: é mudança de stack e pede
aprovação (regra 3). Modelos na pasta `templates/fase/` do kit, que não precisa ir para o projeto
(o formato curto em `templates/fase/curta.md`).

---

## 3. Implementar por grupos

| | |
|---|---|
| **Skill** | `implementar-fase` ("implementar a fase") |
| **Entra** | a spec aprovada, na branch da fase |
| **Sai** | o código de cada grupo, as tarefas marcadas no `plan.md` e a spec atualizada quando a realidade a contradiz |
| **O usuário decide** | só quando a skill para (abaixo); o resto ela leva até o fim sem pedir licença entre os grupos |

Um grupo por vez, na ordem. Cada grupo fecha com:

1. a suíte das pastas tocadas, com a **linha de resumo lida** (regra 8);
2. o veredito do **revisor** e do **validador** (etapa 4);
3. o commit do grupo na branch da fase, **se o usuário pediu commits** ao aprovar o plano (regra 6);
4. as tarefas marcadas no `plan.md` e uma linha curta do que mudou.

Fim de grupo não é fim de turno: com o próximo grupo liberado, a conversa segue no mesmo turno.

**A skill para e pergunta quando:**

- aparece dependência fora de `specs/tech-stack.md`, inclusive transitiva;
- a spec é ambígua a ponto de duas implementações razoáveis divergirem no que o usuário ou o
  cliente vê;
- o caminho exige migração destrutiva, mudança de schema em produção ou credencial;
- **a realidade contradiz a spec.** Aí a ordem é: parar, explicar ao usuário o que se descobriu e
  as opções, atualizar `requirements.md` e `plan.md` (com a linha em "Alterações de escopo"), e só
  então voltar ao código.

Achado fora do escopo não se corrige no meio da fase: vira lição (se cumprir um dos quatro
motivos da regra 7), aviso à gerente ou um item na caixa de achados
(`docs/operacao-das-conversas.md`).

---

## 4. Revisar e validar (a cada grupo)

| | |
|---|---|
| **Agentes** | `revisor` e `validador`, abertos pela própria conversa, independentes entre si (no Claude Code, `.claude/agents/`; no Codex, `.codex/agents/`) |
| **Entra** | o diff do grupo, a spec da fase e o `AGENTS.md` |
| **Sai** | revisor: achados com `arquivo:linha` e gravidade, e "sem bloqueio" ou "com bloqueio"; validador: a prova por execução real e por mutação, e "valida" ou "não valida" |
| **O usuário decide** | nada, no caso normal: a conversa aplica os achados e segue; o usuário entra quando a conversa discorda de um bloqueio ou quando o achado muda o escopo |

Os dois só leem e nunca editam. **Caminho rápido:** grupo ou PR só de documentação ou só de testes
leva só o revisor, que confere fato por fato contra a fonte (regra 11).

**O guardião.** PR com código passa também pelo guardião antes do merge: é o mesmo agente
`revisor`, rodado sobre o **diff inteiro do PR**, numa conversa nova (ou num subagente novo, sem o
contexto de quem escreveu), depois da revisão por grupo. Ele vê o efeito somado dos grupos, que
nenhuma revisão de grupo viu. Com uma conversa só, o guardião é opcional.

---

## 5. Validar a fase

| | |
|---|---|
| **Skill** | `validar-fase` ("validar a fase") |
| **Entra** | o `validation.md`, o código e a saída real das suítes |
| **Sai** | cada item marcado com evidência, a spec reconciliada com o código, o `CHANGELOG.md` (skill `changelog`), a fase marcada no `roadmap.md` e, se houve decisão cara de reverter, um ADR (skill `adr`) |
| **O usuário decide** | executa as verificações manuais e pede o commit e o PR. O merge é liberado pela gerente (PEDIDO → LIBERADO; sem gerente, pelo usuário); o merge de nível 3 (`AGENTS.md`, "Convenções") espera também a palavra do usuário |

- `[x]` **só com evidência**: o comando e a saída colada, nunca leitura do código.
- Item que não pôde ser exercitado vira `[~]` com o motivo. Nunca `[x]` por analogia.
- Divergência entre spec e código: se veio para ficar, atualiza a spec; se foi engano, corrige o
  código.
- A ordem do fechamento: a revisão lê o diff primeiro (no PR com código, também o guardião); a
  prova (a suíte ou o CI) roda **uma vez**, no head final. O merge segue "Merge" em
  `docs/operacao-das-conversas.md`: conferir head e base numa chamada, mergear em outra.
- Nunca merge com validação incompleta, mesmo que "falte pouco".

---

## 6. Replanejar

| | |
|---|---|
| **Skill** | `replanejar-roadmap` ("replanejar", "mudou o requisito") |
| **Entra** | o `roadmap.md`, a constituição e o que foi entregue (`git log`) |
| **Sai** | o `roadmap.md` só com o que falta, as fases pendentes juntadas, divididas ou removidas, e a mudança propagada às specs afetadas |
| **O usuário decide** | aprova a nova ordem e qualquer mudança na missão ou na stack |

Fase concluída não se reescreve: histórico é registro. Detalhe só as três próximas fases; o resto
fica em "Depois (não planejado)".

---

## Em volta de tudo

| Skill | Quando |
|---|---|
| `licao` | um dos quatro motivos aconteceu: hipótese refutada por evidência, premissa do projeto falsa, defeito que custou mais de uma rodada, correção do usuário (regra 7). Formato em `docs/licoes/README.md` |
| `adr` | uma decisão técnica com alternativa real e consequência duradoura |
| `changelog` | antes de fechar a fase |
| `auditar-specs` | de tempos em tempos: a distância entre o que as specs dizem e o que o código faz. Só relata; corrigir é decisão do usuário |
| `iniciar-conversa` | no começo de toda sessão: confere o git e o registro da gerente e abre só o que a tarefa de hoje exige |
| `sessao-gerente` | faz de uma conversa a gerente (GER), quando há várias frentes em paralelo (`docs/operacao-das-conversas.md`) |

A lista completa das skills está em `.claude/skills/`.
