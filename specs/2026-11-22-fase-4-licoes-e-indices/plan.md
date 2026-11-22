# Fase 4: lições e índices — Plano

O fluxo é o da receita `completo` do kit (`AGENTS.md`, "Como o Golem trabalha aqui"):
- o revisor e o validador rodam a cada grupo, no Opus, com o `model: opus` passado na chamada;
- não há parada entre os grupos;
- o guardião lê o diff inteiro do PR antes do PEDIDO de merge.

O grupo só de documentação (G3) leva só o revisor, pelo caminho rápido da regra 11. Um commit por
grupo, na branch da fase, se o autor do kit o aprovar junto com a spec.

**Antes do G1:**
- a spec aprovada pelo autor do kit, com as respostas dos cartões 1 a 4 dentro;
- a branch trazida para a `main` do momento, se ela tiver andado, e as linhas citadas reconferidas.

## G1 — O gancho percebe a lição que falta no índice (R1)

- [x] `.claude/hooks/licoes_relevantes.py`:
  - com o índice legível, a lista dos `docs/licoes/*.md` (sem o `README.md`), comparada com os ids
    do índice; cada lição que falta é lida do Markdown e entra no acervo;
  - a `candidatas` devolve também os ids que faltam;
  - o aviso "índice defasado" sai uma vez por sessão e por agente, pela marca, com os ids e o que
    fazer. Ele sai mesmo quando a ação não tem lição nem regra a receber, e é devolvido à marca se
    a entrega falhar, como as lições;
  - a docstring, na lista "Degradação".
- [x] `docs/licoes/README.md`, "Como o gancho entrega as lições" (`:108-111`): o gancho lê o índice
  e confere se falta alguma lição nele.
- [x] Testes novos em `.claude/tests/test_gancho.py`, sobre a árvore `acervo`:
  - com o índice em dia e uma lição nova fora dele, a ação que casa com o gatilho da nova recebe a
    lição e o aviso, com o id;
  - na mesma sessão, a segunda ação não recebe o aviso de novo;
  - a ação sem lição a receber recebe só o aviso, na primeira vez;
  - com o índice em dia, nada de aviso, e a entrega fica igual à de hoje;
  - com o índice cortado, sai só o aviso de hoje (a varredura), e não o novo;
  - a lição fora do índice vale pelo nome do arquivo, e não pelo `id:`;
  - uma pasta `x.md` em `docs/licoes/` não derruba o gancho.
- [x] **Quem muda, varre** (achado do revisor): as frases que diziam que a lição fora do índice
  nunca chega, na `licao` (`:11`, o título do passo 4 e o "Não é opcional"), na `diagnostico`
  (`:171-173`) e na docstring de um teste da régua.

## G2 — A régua confere as `refs:` e o tamanho do `AGENTS.md` (R2, R3)

- [x] `.claude/hooks/licoes_relevantes.py`: o `ler_gatilhos` recebe o nome do campo (o padrão
  continua `gatilhos`), para a régua ler as `refs:` com o mesmo leitor.
- [x] `.claude/golem.py`: a chave `agents_teto` (um inteiro de 1 em diante), com 3.000 nas três
  receitas, e a função que a lê para a régua, como o `teto_do_gancho`.
- [x] `docs/guia-configuracao.md`: a linha `agents_teto` na tabela das receitas, na lista das
  chaves e no exemplo de `golem.toml`.
- [x] `.claude/regua.py`:
  - a conferência das refs: quais itens se conferem, a âncora, a linha e a busca na pasta do kit no
    modo plugin, como na tabela do R2;
  - o teto do `AGENTS.md`, lido pelo `golem.py` (a chave `agents_teto`, com 3.000 se o
    `golem.toml` tiver erro ou o `golem.py` faltar);
  - os dois saem como `AVISO` no stderr, no `--gerar` e no `--conferir`, sem mudar o código de
    saída;
  - a docstring do arquivo, na lista do que a régua confere.
- [x] As lições do kit: as refs com linha ganham a âncora e a linha certa (as 10 do `requirements.md`,
  "Contexto"). O índice não guarda as `refs:` (`regua.py:266-293`): o `--conferir` tem de dar `ok`
  sem regerar.
- [x] Testes novos em `.claude/tests/test_regua.py`:
  - cada linha da tabela do R2, com uma lição descartável: o arquivo que não existe, a linha que
    não existe, a linha sem âncora, a âncora fora do arquivo e a âncora que mudou de linha (o aviso
    diz a linha nova);
  - o item em prosa e o caminho `game.…` não dão aviso;
  - no modo plugin, a ref a um arquivo que só existe no kit não dá aviso;
  - o código de saída do `--conferir` não muda com um aviso de ref;
  - as lições do próprio kit: zero avisos de ref;
  - o `AGENTS.md` acima do teto dá o aviso, e abaixo dele, não;
  - com `agents_teto` no `golem.toml`, vale o número dele; com o `golem.toml` com erro, os 3.000;
  - o `templates/AGENTS.md` está abaixo do teto padrão.
- [x] O cartão 5: a linha `origem: kit` nas 16 lições do kit e, nelas, o arquivo ausente sem
  aviso; o `--conferir` estrito no teste do kit, o teste da marca, o da cópia do kit e a linha no
  `docs/licoes/README.md`.
- [x] Testes novos em `.claude/tests/test_golem.py`: a `agents_teto` aceita um inteiro e recusa o
  texto e o zero, com o número da linha. O teste da tabela da economico (`test_sem_golem_toml_vale_a_economico`)
  ganha a chave nova.

## G3 — A regra de área, a frase do gatilho e o princípio do índice (R4, R5)

Só documentação: caminho rápido, só o revisor.

- [ ] `.claude/skills/licao/SKILL.md`:
  - o "Escreve:" e o passo 3, com os dois destinos da regra (o `AGENTS.md` e o
    `docs/regras-de-area.md`) e o formato da regra de área;
  - a frase "o gatilho casa com a ação, não com a ferramenta";
  - o formato das refs, com a âncora.
- [ ] `docs/licoes/README.md`:
  - a tabela "Onde cada coisa mora" e a frase de quando a lição vira regra;
  - a frase do gatilho;
  - o esqueleto das refs.
- [ ] A regra 7 no `AGENTS.md` e no `templates/AGENTS.md`, com o mesmo texto. O conciliador tem de
  passar sem entrada nova em `PERMITIDAS`.
- [ ] `docs/plano-produto.md`, seção 8: a decisão 13, o princípio do índice, com os campos do ADR e
  a tabela do R5. O PR do roteiro da GER (a fase 4b, decisão 14) entra antes e deixa na seção 8 o
  item "13. **Reservada:** …": o texto da 13 entra **no lugar dele**, entre a 12 e a 14, sem item
  novo. Antes do G3, a branch traz a `main` com esse PR (a GER, 2026-11-22).
- [ ] **Quem muda, varre:** buscar `regra no \`AGENTS.md\``, `acrescente aqui uma regra`, `refs:` e
  `não lê os arquivos de lição` em `.claude/`, `docs/`, `templates/`, `WORKFLOW.md` e `README.md`, e
  corrigir o que repete o texto velho.

## G4 — Verificação

- [ ] Os comandos do `validation.md`, com a linha de resumo lida, e a saída de cada critério
  colada nele.
- [ ] As verificações manuais do `validation.md`.
- [ ] O guardião sobre o diff inteiro do PR.
- [ ] A `validar-fase`: o roteiro marcado, o PR aberto e o PEDIDO à GER. A linha da fase 4 na
  seção 7 é a nova do PR da GER, que termina em "o acervo geral é da fase 4b (decisão 14)".

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|
| 2026-11-22 | O G1 corrige também a `licao` e a `diagnostico` (a lição fora do índice "nunca chega"), que estavam no G3 | O G1 tornou as frases falsas, e a varredura do G3 não as acharia (achado do revisor) | o agente: detalhe de implementação, dentro do R1 |
| 2026-11-22 | O gancho só lê arquivo em `docs/licoes/` (`is_file`) | Uma pasta `x.md` derrubava o gancho a cada ação, visto pelo validador; já caía na varredura de hoje | o agente: falha vista, dentro do R1 |
| 2026-11-22 | As lições do kit ganham `origem: kit`, e nelas o arquivo ausente não avisa | Na instalação por cópia o jogo nascia com 12 avisos de ref (achado do revisor do G2) | o autor do kit, pela EST: "D: só as do kit calam (Recomendado)" |
