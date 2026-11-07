---
name: adr
description: Registra uma decisão técnica em docs/adr/NNN-titulo.md com contexto, opções consideradas, decisão, consequências e gatilho de revisão. Use quando o usuário disser "registrar decisão", "escrever um ADR", "documentar por que escolhemos X", "vale a pena usar A ou B?" ou invocar /adr.
---

# ADR: registro de decisão de arquitetura

**Lê:** `specs/tech-stack.md`, `specs/roadmap.md` e os ADR já existentes em `docs/adr/`.
**Escreve:** **só** `docs/adr/NNN-titulo.md`. Não mexe em código nem em spec sem pedir.
**Decide:** se a decisão merece ADR (tem alternativa real e consequência duradoura) e qual opção
recomendar. **Para e propõe** se a escolha exigir dependência fora da `tech-stack`.

## Quando isto se aplica

Escreva um ADR quando a decisão for **cara de reverter**, **atravessar várias fases** ou
**voltar a ser questionada em seis meses**. Exemplos: escolha de banco, estratégia de
autenticação, adoção de fila, formato de contrato entre serviços.

Decisão pequena e local **não** vira ADR: ela vive na seção "Decisões" do `requirements.md` da
fase. Na dúvida, pergunte: "alguém vai perguntar 'por que isso é assim?' daqui a um ano?"

## Fluxo

### 1. Numerar

```bash
ls docs/adr/[0-9]*.md 2>/dev/null | tail -3
```

Próximo número sequencial, com zero à esquerda: `docs/adr/007-fila-de-lembretes.md`. O
`docs/adr/modelo.md`, se existir, é a forma a copiar, e não entra na conta.

### 2. Levantar as opções de verdade

Um ADR com uma opção só é justificativa, não decisão. Traga no mínimo duas alternativas reais,
cada uma com o que ganha, o que perde e **o custo de reverter**. Se o usuário já escolheu, o seu
trabalho é registrar honestamente o que foi descartado, inclusive o que a alternativa tinha de bom.

Fato técnico que pesa na escolha (limite de uma API, versão instalada, comportamento medido) vem
com a fonte: `arquivo:linha`, documentação com versão, ou a saída do comando.

### 3. Escrever

Seções: status, data, decisores, contexto, opções consideradas, decisão, consequências
(positivas, dívida aceita, impacto no roadmap e na constituição) e **gatilho de revisão**: a
condição objetiva que faz revisitar a decisão. O modelo está em `docs/adr/modelo.md` (ou em
`templates/adr.md` do kit).

O contexto descreve forças, não preferências: requisito, limite técnico, prazo, restrição externa.
A decisão do usuário entra com as palavras dele e a data.

### 4. Propagar

- Mudou a stack? Atualize `specs/tech-stack.md` e cite o ADR lá
- Mudou o plano? Ajuste `specs/roadmap.md`
- Afeta a fase em curso? Referencie o ADR no `requirements.md` dela

## Restrições

- ADR aceito **não se edita**: crie um novo com status "substitui ADR NNN" e marque o antigo
- Sem gatilho de revisão, o ADR vira dogma: sempre escreva a condição de revisitar
- Não registre decisão que o usuário ainda não tomou; marque como "proposta"
