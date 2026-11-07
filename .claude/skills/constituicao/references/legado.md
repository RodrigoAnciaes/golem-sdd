# Referência: constituição de projeto legado

Carregue este arquivo quando o código já existe e não há specs.

## A inversão de ordem

Em projeto novo: entrevista → documento.
Em legado: **leitura do código → devolução do entendimento → correção humana → documento.**

Pular a devolução do entendimento é a falha característica aqui. O modelo lê 200 arquivos,
entende 70% e documenta os 30% errados com a mesma confiança.

## Passo a passo

### 1. Levantamento (sem escrever nada em disco)

- Dependências e **versões reais**, lidas dos arquivos de lock ou manifesto, nunca de memória
- Pontos de entrada: como sobe, como testa, como faz deploy
- Fluxos principais, seguidos no código de ponta a ponta
- Onde estão os dados e quem os toca
- O que está morto: código sem chamada, feature desligada, teste ignorado

Anote cada fato com `arquivo:linha`. É o que permite ao usuário conferir a devolução.

### 2. Devolução

Apresente ao usuário: o que o sistema faz, para quem, como está organizado, o que parece dívida.
Liste separadamente **o que você não conseguiu determinar**. Espere a correção antes de escrever.

### 3. Documentos

- `mission.md`: descreve o produto **como ele é hoje**, não a versão idealizada
- `tech-stack.md`: o que está de fato instalado, incluindo a dívida, marcada como dívida
- `roadmap.md`: construído a partir de `TODO.md`, backlog, issues ou da lista de dores do usuário

### 4. Marcação de incerteza

Toda linha inferida do código sem confirmação humana leva `⚠️ suposição`. Elas são a pauta da
revisão. Só remova a marca quando alguém confirmar.

## Primeira fase em legado

Escolha a menor fase que entregue valor **sem tocar na área frágil**. O `validation.md` dela
precisa incluir prova de que o comportamento anterior não regrediu: caracterização do
comportamento atual antes da mudança, se não houver testes.

## Falhas comuns

| Sintoma | Correção |
|---|---|
| Missão que descreve o sistema que o time queria ter | documente o que existe; o desejo vira roadmap |
| Stack listada pelo que "geralmente se usa" | releia o manifesto de dependências |
| Roadmap que começa por refatoração grande | comece pequeno e reversível; refatoração vira ADR |
| Suposições misturadas com fatos | separe visualmente e revise com o usuário |
