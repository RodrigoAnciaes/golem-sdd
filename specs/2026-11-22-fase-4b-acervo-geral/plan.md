# Fase 4b: o acervo geral de lições — Plano

O fluxo é o da receita `completo` do kit (`AGENTS.md`, "Como o Golem trabalha aqui"):
- o revisor e o validador rodam a cada grupo, no Opus, com o modelo passado na chamada;
- não há parada entre os grupos;
- o guardião lê o diff inteiro do PR antes do PEDIDO de merge.

O grupo só de documentação (G4) leva só o revisor, pelo caminho rápido da regra 11. Um commit por
grupo, na branch da fase, se o autor do kit o aprovar junto com a spec.

**Antes do G1:**
- a spec aprovada pelo autor do kit;
- a branch trazida para a `main` do momento, se ela tiver andado, e as linhas citadas reconferidas.

## G1 — O gancho lê os dois acervos (R1, R2)

- [x] `.claude/hooks/gancho.sh`: no modo plugin, exporta o `GOLEM_CENTRAL` com o central que já
  calcula (`:63-66`), junto do `CLAUDE_PROJECT_DIR` (`:321-322`); fora dele, quem não lê o geral
  é o `.py`, que confere o modo (tirar a variável no `sh` seria uma segunda conferência sem falha
  vista: a mutação dela não muda nada que se veja). O comentário do topo (passo 1) diz isso.
- [x] `.claude/hooks/licoes_relevantes.py`:
  - a leitura de um acervo (o índice, a lição fora dele, a varredura do Markdown) passa a receber a
    pasta, no lugar das constantes `LICOES` e `INDICE`;
  - o acervo geral: o `GOLEM_CENTRAL`, só no modo plugin (o `.claude-plugin/plugin.json` no kit e a
    raiz diferente do kit) e só se for uma pasta diferente da raiz;
  - a `candidatas` junta os dois: gatilho antes de área, e o jogo antes do geral dentro de cada
    grupo; o id que está no jogo não entra do geral;
  - o sinal sai da pasta de onde a lição veio;
  - a saída: as gerais num bloco próprio, com o título do acervo geral e a pasta;
  - a degradação e o aviso "índice defasado" por acervo, com uma marca própria para o do geral e o
    texto apontando a pasta e o comando certos;
  - a docstring (o topo e a "Degradação").
- [x] Testes novos em `.claude/tests/test_gancho.py`, sobre a árvore `Plugin` (o gancho pelo
  `gancho.sh`, com o `CLAUDE_PROJECT_DIR` no jogo e o `GOLEM_CENTRAL` no central):
  - a lição só do geral chega na ação que casa com o gatilho dela, no bloco do geral, com o sinal
    lido do Markdown do geral;
  - o mesmo id nos dois: chega só a do jogo, com o sinal do jogo;
  - com o teto 1 e uma lição de cada acervo casando por gatilho, chega a do jogo; a geral vem na
    ação seguinte;
  - a lição geral fora do índice do geral chega, com o aviso do geral uma vez por sessão;
  - o índice do geral cortado: a varredura do geral, com o aviso que aponta o geral, e o do jogo
    segue pelo índice;
  - sem a pasta do geral: a saída é igual à de hoje;
  - fora do modo plugin (o kit sem `.claude-plugin/`), com o `GOLEM_CENTRAL` no ambiente e lições
    no geral, nenhuma geral chega;
  - a sessão aberta no próprio central: um acervo só, sem bloco do geral;
  - da revisão do G1: a geral de mesmo id fica de fora mesmo quando só ela casa (e sem a marca da
    sessão); a geral por gatilho vem antes da do jogo pela área; os dois acervos defasados dão os
    dois avisos; sem o `GOLEM_CENTRAL` no ambiente, o central é o `$HOME/Golem`.
- [x] Um teste da régua (`test_regua.py`): rodada com a pasta corrente num central sem git, o
  `--gerar` indexa as lições do disco, e o `--conferir` passa.

## G2 — A marca de jogo para terceiros e o comando de subir (R3, R4)

- [x] `.claude/golem.py`:
  - o registro com a coluna `Para terceiros`: o `ler_registro` lê as linhas de três e de quatro
    células (a de três vale `não`); o cabeçalho novo; a primeira escrita passa o arquivo a quatro
    colunas;
  - o `registrar --terceiros`: marca, e no jogo já registrado troca a marca sem duplicar; sem o
    `--terceiros`, não desmarca;
  - a chave `jogos_para_terceiros` (`sim` ou `nao`), lida só do `golem.toml` do central, `nao`
    sem a linha; e a conferência de como ela entra no `onde` e no guia (a tabela das receitas,
    `test_golem.py:226`), com o que se decidir anotado no `requirements.md`, R3;
  - o `onde`, no modo plugin: a linha "para terceiros" (`sim`, `não` ou "fora do registro");
  - o `subir <arquivo> [--substituir]`, com as conferências do R4 antes de escrever, a escrita em
    `<central>/docs/licoes/<id>.md`, a régua do kit regerando o índice do geral (um subprocesso
    com a pasta corrente no central) e a linha da subida no `<central>/.claude/indice/subidas.txt`;
  - o `USO` (`:532-543`) com o comando novo e o `--terceiros`.
- [x] Testes novos em `.claude/tests/test_golem.py`:
  - o registro antigo, de três colunas, é lido, com `não`, e passa a quatro na primeira escrita;
  - o `registrar --terceiros` marca; rodado de novo sem ele, a marca fica; não duplica a linha;
  - a chave `jogos_para_terceiros`: aceita no central, `nao` sem a linha, e um valor fora de
    `sim`/`nao` sai com o erro da linha;
  - o `onde` diz o "para terceiros" nos três casos;
  - o `subir` recusa, sem escrever nada: fora do modo plugin; no projeto fora do registro; no
    projeto para terceiros; com o nome do jogo no texto (em maiúsculas diferentes); com a pasta do
    jogo; com uma ref a um arquivo do jogo; com uma ref `game.…`; com o frontmatter que a régua
    recusa; com o id que já está no geral, sem o `--substituir`;
  - o `subir` aceita a lição com ref a um arquivo do kit e a ref em prosa, escreve no geral, regera
    o índice dele e grava a linha da subida, e a lição do jogo fica igual; com o `--substituir`, a
    linha do mesmo id se troca, sem duplicar;
  - de ponta a ponta: a lição subida de um jogo chega pelo gancho num **segundo** jogo registrado.

## G3 — A régua avisa a divergência (R5)

- [x] `.claude/regua.py`: no modo plugin (pelo `golem.py`, que ela já carrega, `:348-359`), o
  `AVISO` de cada lição do jogo com id no `subidas.txt` do central e com a impressão do jogo ou a
  do geral diferente da gravada (ou o geral sumido), junto dos avisos das refs e do teto
  (`:377-387`). A impressão com as quebras de linha passadas a `\n`. A docstring do topo.
- [x] Testes novos em `.claude/tests/test_regua.py`, sobre a árvore `Plugin`:
  - logo depois do `subir`, o `--conferir` no jogo não avisa;
  - a lição do jogo mudada: o `AVISO` com as duas pastas, e a régua sai 0;
  - a versão geral mudada à mão, e a apagada: o `AVISO`;
  - só a troca de `\n` por `\r\n` na lição do jogo: nenhum aviso;
  - o `subir --substituir` depois da mudança: o aviso some;
  - fora do modo plugin, com o `subidas.txt` no central do ambiente: nenhum aviso;
  - da revisão do G3: a sessão aberta no próprio central, com uma versão geral reescrita (outro
    texto que o da lição do jogo), não avisa; e o repositório do kit, com o manifesto e a raiz
    nele, não avisa.

## G4 — As skills e os documentos (R3, R6, R7)

- [x] `.claude/skills/iniciar-sdd/SKILL.md`: no passo 2, a pergunta geral quando o `golem.toml` do
  central não tem a linha (e a escrita da linha), a pergunta por jogo com `sim`, a linha de aviso
  com `nao`; o `--terceiros` no passo 5; a coluna nova no caminho sem Python (`:135-142`).
- [x] `.claude/skills/licao/SKILL.md`: o passo 1 busca também no geral, no modo plugin; o passo
  novo "Oferecer o acervo geral", depois do fecho, com as condições (o "parece valer para qualquer
  jogo", e na dúvida pergunta), as duas perguntas (o texto reescrito dentro da segunda), o `subir`
  e a prova (o índice do geral e a régua do jogo); a pergunta do nome comum e o `--palavra-comum`; o `AVISO` da divergência
  no passo 4; o "Escreve:" do topo.
- [x] `docs/licoes/README.md`: a tabela "Onde cada coisa mora" e "Como o gancho entrega as lições".
- [x] `README.md`: o "Mapa das pastas" (as linhas do `jogos.md`, do `docs/licoes/` e do índice, e o
  `subidas.txt`).
- [x] `docs/guia-configuracao.md`: a chave `jogos_para_terceiros`, como o G2 decidiu.
- [x] **Quem muda, varre** (as buscas abaixo), e o que achar entra neste grupo:

  ```bash
  grep -rn "Registrado em" --include=*.md --include=*.py . | grep -v '^./specs/'
  grep -rn -i "neste projeto\|só as lições do jogo\|acervo do jogo\|acervo geral" --include=*.md . | grep -v '^./specs/'
  grep -rn "docs/licoes/" .claude/skills .claude/agents docs/operacao-das-conversas.md WORKFLOW.md
  grep -rn -i "cliente" .claude/skills .claude/golem.py .claude/regua.py README.md docs/licoes/README.md docs/guia-configuracao.md
  ```

  A última busca confere que a palavra "cliente" não chega à tela nos textos novos (os nomes
  internos do código podem ficar).

## G5 — A verificação e o registro

- [ ] Os comandos do `validation.md`, com a saída colada.
- [ ] As verificações manuais M1 a M4 (o `gancho.sh`, o `golem.py` e a régua numa árvore
  descartável, sem login) e, se o autor do kit topar, a rodada com login L1.
- [ ] O `validation.md` com a contagem final, e os itens marcados.
- [ ] O guardião sobre o diff inteiro, e as correções dele.

## Alterações de escopo durante a fase

| Data | O quê | Por quê | Quem aprovou |
|---|---|---|---|
| 2026-11-22 | A prova da `licao` (R6): o índice do geral e a régua do jogo, e não o gancho | No jogo de onde a lição subiu, o gancho entrega a do jogo (a de mesmo id vence, R2), sem o rótulo do geral | O agente, no G4 (detalhe de implementação) |
| 2026-11-22 | O `subir --palavra-comum` e a pergunta da `licao` sobre o nome comum (R4, R6) | A revisão do G2 mostrou a recusa pelo nome sem saída, com nomes comuns ("Obby", a pasta `jogo`) | O autor do kit, pela EST: "A: recusa com saída (Recomendado)" |
