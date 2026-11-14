# Fase 2: Roblox mínimo, sem Rojo — Requisitos

Branch `fase-2-roblox`, criada de `1f9f827` (a `main` em 2026-11-13, conferida com
`git ls-remote origin refs/heads/main`). Fatos do repositório lidos em `1f9f827`; os da fase 1, em
`origin/fase-1-configuracao` no `7435d83` (só a spec dela existia na branch nesse commit). Fatos de
fora lidos em 2026-11-13, com o link. **As páginas do Studio MCP mudaram nesse mesmo dia**
(`last_updated: 2026-11-14T01:38:48Z`, em UTC, no `.md` de cada uma): a leitura que vale é a
dessa versão, e o G1 relê antes de levar os fatos ao `docs/plano-produto.md`.

**Esta spec é escrita antes do merge da fase 1** e conta com o que ela entrega: o `golem.toml`, as
receitas, o `golem aplicar` e o bloco "Como o Golem trabalha aqui" no `AGENTS.md`
(`specs/2026-11-13-fase-1-configuracao/requirements.md`, R2 a R6, no `7435d83`). A implementação
começa depois desse merge, com a `main` nova; os números de linha citados aqui se reconferem no G1
(regra 9).

## Objetivo

Quem programa Luau no Roblox Studio, sem Rojo, usa o kit: o código continua no place, e as specs,
as lições e o `AGENTS.md` ficam numa pasta com git ao lado, que o agente opera. O agente edita os
scripts pelo Studio MCP; o gancho entrega as lições e as regras de área nessa edição; os testes
rodam no Studio, e o resumo é lido no console. O agente salva uma versão do place antes de cada
fase, e volta-se atrás pelo histórico de versões do Roblox. A migração para o Rojo fica para uma
fase própria (`docs/plano-produto.md:547`, a linha da fase 2; seção 5, `:416-505`).

Pensado para o primeiro usuário: programa Luau no Studio, usa pouco IA, não usa Rojo e "Não parece
ter muita experiência com controle de versões ainda" (palavras do autor do kit, 2026-11-13).

## Escopo

- **R1. As decisões registradas e o roteiro reescrito** (`docs/plano-produto.md`):
  - a seção 8 ganha a decisão "Sem Rojo, migrar depois", as respostas da entrevista desta spec e o
    fluxo completo desta fase como exceção à decisão 1 da fase 1, com as palavras do autor do kit e
    a data (ver "Decisões");
  - a seção 5 (`:416-505`) passa a ter o caminho sem Rojo como o de entrada, e o Rojo como o
    destino da migração. Os fatos conferidos desta spec entram com o link (ver "Contexto"): as
    ferramentas do Studio MCP, o `execute_luau` com o modo de edição, o `save_place`, o
    `open_cloud_invoke`, o histórico de versões, o `rojo syncback` e o estado do TestEZ, do Jest
    (o `Roblox/jest-roblox` e o fork `jsdotlua/jest-lua`) e do `run-in-roblox`;
  - a linha da fase 2 (`:547`) ganha a entrega e o "pronto" desta spec (R9). O "pronto" de hoje
    ("num place Rojo de exemplo") sai;
  - o roteiro (seção 7) ganha uma linha nova, **Migração para o Rojo**, com a skill que guia a
    migração pelo `rojo syncback`, o `default.project.json`, o código no git, as áreas do
    `POR_CAMINHO` e do `POR_COMANDO` de `:469-470` (`.luau`, `default.project.json`, `rojo`,
    `argon`, `selene`, `stylua`, `wally`) e a troca do executor mínimo por um framework. O
    `run-in-roblox` sai da lista: o último commit é de 2020-07-20, a v0.3.0 (ver "Contexto"). A
    ordem entre essa fase e as fases 3 a 6 fica para o autor do kit decidir; a linha entra no fim
    da tabela, marcada "ordem a decidir";
  - as "Perguntas ao primeiro usuário" (`:553-557`): a linha "Antes da fase 2" passa a pedir se ele
    toparia migrar para o Rojo um dia, como organiza os jogos (uma pasta por jogo?) e como volta a
    uma versão anterior hoje. Essas perguntas não travam a fase (ver "Perguntas em aberto").
- **R2. As conferências no Studio**, antes do código que depende delas. Com o Studio aberto e o
  Studio MCP ligado ao Claude Code, o agente confere e anota no `plan.md` (G2), com a saída:
  1. o nome do servidor que o quick connect registra no Claude Code. A documentação dá
     `Roblox_Studio` na configuração por JSON; o do quick connect fica a conferir;
  2. os nomes dos campos da entrada do `multi_edit` (o caminho do script, o texto e o
     `datamodel_type`) e do `execute_luau` (o código e o `datamodel_type`), como chegam ao gancho
     no `tool_input`;
  3. se o `require` de um ModuleScript, rodado pelo `execute_luau` em modo de edição, enxerga a
     edição feita pelo `multi_edit` logo antes, ou devolve o módulo guardado da rodada anterior.
     Se devolver o velho, o executor (R6) roda em modo de jogo (`start_stop_play` e o
     `datamodel_type` `Server`), e a spec registra a troca na tabela de alterações;
  4. o que o `get_console_output` devolve: o log inteiro da sessão ou só o novo, e se o `print`
     do `execute_luau` chega nele;
  5. que o `save_place`, num place aberto do Roblox, faz aparecer uma versão em Window ⟩ Version
     History, como a documentação diz (ver "Contexto");
  6. como o `multi_edit` e o `script_read` tratam um nome com ponto, como `Moedas.spec`, no caminho
     com pontos (`game.ServerStorage.Moedas.spec`): se acham o script com esse nome ou leem `spec`
     como filho de `Moedas`. No segundo caso, a convenção do R6 passa a ser o sufixo `_spec`;
  7. se o Ctrl+Z do Studio desfaz uma edição feita pelo `multi_edit`. Sem essa conferência, o guia
     (R8) não cita o Ctrl+Z.

  Cada conferência que mudar o desenho do R3 ao R8 volta ao autor do kit antes do grupo que
  depende dela.
- **R3. O gancho vê a edição pelo Studio MCP** (pedido da conversa de estratégia, confirmado pelo
  autor do kit, ver "Decisões").
  - **O `matcher`:** o `.claude/settings.json` ganha uma terceira entrada `PreToolUse`, com o
    `matcher` do `multi_edit` e do `execute_luau` do Studio MCP e o mesmo conteúdo de `hooks` das
    outras duas (`command`, `timeout` e `statusMessage`, `.claude/settings.json:7-14`).
    As duas entradas de hoje não mudam: o `instalar_codex.py` lê o comando da primeira
    (`.claude/instalar_codex.py:77-84`) e usa os `MATCHERS` dele (`:39`) para o Codex, e o Codex
    fica fora desta fase.
  - **A leitura:** o `.claude/hooks/licoes_relevantes.py` lê o caminho do script do `multi_edit`
    como caminho (hoje só `tool_input.file_path`, `:456`) e o código do `execute_luau` como
    comando (hoje só `tool_input.command`, `:458`), pelos campos do R2. A docstring "As entradas
    que ele entende" (`:9-13`) ganha as duas.
  - **As áreas:** o `POR_CAMINHO` (`:64-78`) ganha os serviços do place em que mora código, na
    forma do caminho do Studio MCP (`game.ServerScriptService`, `game.ServerStorage`,
    `game.ReplicatedStorage`, `game.StarterPlayer`, `game.StarterGui`, `game.Workspace`), na área
    `codigo`. Na forma com `game.`, uma pasta comum chamada `Workspace` num caminho de arquivo não
    acende `codigo`. O `POR_COMANDO` não muda: uma lição com `gatilhos:` só chega quando um gatilho
    casa, e não pela área (`licoes_relevantes.py:20-24`, `:260-266`); a lição do resumo dos testes
    no place é a lição de exemplo do R7, com o gatilho na chamada do executor.
  - **Os testes** na suíte do ferramental, no padrão de `.claude/tests/test_gancho.py`:
    1. um `tool_input` de `multi_edit` num script de `game.ServerScriptService` entrega uma lição
       da área `codigo`;
    2. o código de um `execute_luau` chega aos gatilhos: uma lição com gatilho no nome do executor
       é entregue;
    3. o `matcher` da entrada nova casa com `mcp__<servidor>__multi_edit` e
       `mcp__<servidor>__execute_luau`, e não com `mcp__<servidor>__script_read`. O teste aplica a
       regra do Claude Code (ver "Contexto"): só letras, dígitos, `_`, `-`, espaço, `,` e `|` fazem
       uma lista de nomes exatos; qualquer outro caractere faz uma expressão regular de JavaScript
       sem âncora;
    4. a entrada nova tem o mesmo `command`, `timeout` e `statusMessage` das outras duas;
    5. um `Edit` de `C:/x/Workspace/notas.md` não acende `codigo`.
- **R4. O revisor e o validador leem o place.**
  - **O revisor** ganha no `tools:` as ferramentas de leitura do Studio MCP: `script_read`,
    `script_grep`, `script_search`, `search_game_tree`, `inspect_instance`, `get_console_output`
    e `list_roblox_studios` (toda chamada leva o `studio_id`, que só ela lista), com o nome do
    servidor do R2 (`mcp__<servidor>__<ferramenta>`). Nenhuma
    que escreve (`multi_edit`, `execute_luau`, `save_place`, `start_stop_play`,
    `open_cloud_invoke`).
  - **O validador** ganha as mesmas, mais o `execute_luau`, para rodar o executor, e, se o R2
    mandar rodar em modo de jogo, o `start_stop_play` e o `get_studio_state`.
  - **O texto dos dois** ganha o caminho sem Rojo, curto: sem diff no git, o revisor recebe da
    conversa a lista dos scripts que o grupo mexeu e os lê pelo `script_read`; o validador roda o
    executor e lê a linha de resumo no console. **No place, o validador não faz mutação**: não há
    cópia descartável, e o `execute_luau` mudaria o place do usuário. Ele diz numa linha que a
    mutação foi pulada por isso. O `execute_luau` do validador só roda o executor e leituras.
  - Num projeto sem o Studio MCP, as entradas `mcp__` não resolvem e o resto do `tools:` continua
    valendo (a documentação dos subagentes diz que o agente só falha se **nenhuma** entrada
    resolver, ver "Contexto"). O G4 confere isso numa pasta sem o servidor.
  - O `aplicar` da fase 1 troca só a linha `model:` do frontmatter (fase 1, R4): o `tools:` novo
    não colide com ele. O G4 confere com o `aplicar` rodado depois da mudança.
- **R5. Os modelos para Roblox**, numa pasta nova `templates/roblox/`, que o guia (R8) manda copiar
  para o projeto do usuário:
  - `tech-stack.md`: o modelo de `templates/constituicao/tech-stack.md` preenchido, seção por
    seção, para o caminho sem Rojo (Luau no Studio; o código no place; o Studio MCP; o executor
    mínimo; o git local só para specs e lições; nenhum segredo, porque nada usa chave);
  - `comandos-reais.md`: o bloco "Comandos reais" do `AGENTS.md` para Roblox. Não há comando de
    terminal para os testes: o bloco diz qual ferramenta do Studio MCP roda o executor, com que
    `datamodel_type`, e onde ler a linha de resumo; e diz que, **antes de começar cada fase**, o
    agente chama o `save_place` e anota no `plan.md` a hora da versão salva. Num place aberto de
    um arquivo local (`.rbxl`), o `save_place` grava por cima do arquivo e não cria versão
    (ver "Contexto"): o agente para e pede ao usuário que salve o place no Roblox (File ⟩ Save to
    Roblox) antes da fase. A "Contagem esperada
    de testes" vive no `validation.md` da fase, como hoje (`AGENTS.md:59`);
  - `Executor.luau` e um exemplo de teste (R6).
- **R6. O executor mínimo de testes.** Um ModuleScript curto, em Luau, que o agente põe no place
  pelo `multi_edit` (o lugar, um ModuleScript `GolemTestes.Executor` em `ServerStorage`, se
  confirma no G2):
  - um teste é uma função num ModuleScript cujo nome termina em `.spec` (ou `_spec`, conforme o
    R2.6), que devolve uma tabela `{ ["nome do teste"] = função }`. O sufixo `.spec` é o do nome
    dos arquivos de teste do TestEZ e do Jest; o conteúdo não é o `describe`/`it` deles;
  - o executor acha os testes nos serviços do R3, roda cada função com `pcall` e imprime, no fim,
    uma linha `N passed, N failed, N skipped` (o formato do TestEZ, `TextReporter.lua:80`), e uma
    linha por falha com o módulo, o teste e o erro;
  - um teste se pula com o nome começando por `pular: `, e conta como `skipped`;
  - sem nenhum teste, a linha sai `0 passed, 0 failed, 0 skipped` e mais uma linha
    "nenhum teste encontrado", para que zero coletado não pareça verde (regra 8);
  - o executor e o exemplo não chamam o `DataStore`: no Studio, ele é o de verdade, e escrever nele
    muda o dado dos jogadores (ver "Contexto");
  - o executor é **modelo do kit**, não dependência: o código fica em `templates/roblox/`, com a
    linha de crédito (`-- Golem SDD · ...`), e o usuário pode trocá-lo por um framework na
    migração.
- **R7. As lições e as regras de área de exemplo**, em `templates/roblox/`. São do projeto do
  usuário, não do kit: ficam fora de `docs/licoes/` e do índice do kit.
  - **Duas lições de exemplo** em `templates/roblox/licoes/`, no formato de
    `docs/licoes/README.md`. Uma tem gatilho na chamada do executor e conta a linha de resumo no
    console (o que o R2.4 mostrar). A outra conta um fato conferido na fonte ou no G2 (regra 9).
    Candidatas: "restaurar uma versão não publica"
    ([histórico de versões](https://create.roblox.com/docs/projects/version-history)); o `require`
    guardado em modo de edição, se o R2.3 o confirmar.
  - **A lista de riscos do Roblox** (pedido da conversa de estratégia, confirmado pelo autor do
    kit): `templates/roblox/regras-de-area.md`, de 5 a 8 regras no formato que o gancho entende
    (`## Regra N — Título`, a linha `areas: codigo`, o corpo; `licoes_relevantes.py:31-33`,
    `:270-296`). Cada regra diz o risco e o porquê em uma linha, com o link da documentação do
    Roblox que o sustenta, e o comportamento **"avisar e deixar"**: o agente faz o que o usuário
    pediu, e põe uma linha de aviso no resumo da parte (ou no fim do grupo), com três saídas:
    corrigir, deixar assim, me explica. Não bloqueia. O que o agente escreve por conta própria já
    sai do jeito seguro. Candidatas, cada uma **a conferir** na documentação no G5; a que não
    tiver fonte sai:
    1. o servidor não confia no que o cliente manda por um `RemoteEvent` ou `RemoteFunction`
       (valida os argumentos);
    2. a chamada de `DataStore` pode falhar e vai dentro de `pcall`;
    3. o `DataStore` tem limite de pedidos;
    4. o que o cliente não pode ver fica em `ServerStorage` ou `ServerScriptService`, e não em
       `ReplicatedStorage`;
    5. um laço sem pausa trava o script;
    6. o dado do jogador se salva também no `game:BindToClose`, além do `PlayerRemoving`;
    7. a conexão de evento que não serve mais se desconecta;
    8. o `task.wait` no lugar do `wait`.
  - **Os testes:** um teste copia as duas lições de exemplo para o `docs/licoes/` de uma cópia do
    kit, regera o índice e confere que o gancho as entrega a um `tool_input` do Studio MCP (a do
    executor num `execute_luau`); outro copia a lista de riscos para o `docs/regras-de-area.md` da
    cópia e confere que um `multi_edit` em `game.ServerScriptService` a entrega.
- **R8. O guia.** `docs/guia-roblox.md`, de uma página:
  - ligar o Studio MCP (Assistant ⟩ … ⟩ Manage MCP Servers ⟩ Enable Studio as MCP server, e o quick
    connect do Claude Code), com o aviso da documentação de que o cliente MCP lê e muda o place;
  - **desligar as permissões de Open Cloud do Studio MCP** (MCP ⟩ MCP Permissions), seção por
    seção: cada jogo começa no nível "Balanced", com os escopos de risco baixo e moderado ligados,
    e o "Safe" ainda deixa algumas ligadas; o kit não usa o `open_cloud_invoke` (ver "Contexto");
  - o aviso de que, no Studio, o `DataStore` é o de verdade: um teste que escreve nele muda o dado
    dos jogadores;
  - **salvar o place no Roblox antes da primeira fase** (File ⟩ Save to Roblox): num place local,
    não há histórico de versões;
  - a pasta do projeto com git ao lado do place (uma pasta por jogo, como sugestão); copiar os
    modelos do R5 e do R7 (as lições para `docs/licoes/`, a lista de riscos para
    `docs/regras-de-area.md`) e rodar `regua.py --gerar`, porque o gancho lê o índice e só cai no
    Markdown sem ele (`licoes_relevantes.py:183-196`, `:255-258`);
  - pedir ao agente que ponha o executor; rodar os testes;
  - o desfazer: o agente salva uma versão (`save_place`) antes de cada fase; o Ctrl+Z, só se o
    R2.7 o confirmar; e voltar à versão salva pelo histórico, com os passos do Studio e do Creator
    Dashboard, o aviso de que restaurar não publica, e o de que, depois do "Open Local Copy" e do
    "Save to Roblox As", a sessão antiga se fecha sem salvar, para não gravar por cima da volta;
  - o que fica mais fraco sem Rojo (sem diff, sem mutação, sem git do código), com o caminho para
    migrar depois;
  - o que aparece quando o Studio está fechado (a ferramenta do MCP falha) e o que fazer.
- **R9. O "pronto" da fase** (a linha `:547` reescrita): num place de exemplo, sem Rojo, com o
  Studio MCP ligado, uma fase pequena vai da spec ao validado: o agente salva a versão antes da
  fase; edita um ModuleScript pelo `multi_edit`; o gancho entrega uma lição e uma regra de área de
  exemplo nessa edição; os testes rodam pelo executor, e a linha `N passed, N failed, N skipped` é
  lida no console; um teste quebrado de propósito aparece como `failed`; e, no fim, uma volta pelo
  histórico de versões é feita seguindo só o guia. O passo a passo está no `validation.md`,
  verificação manual 1.
- **R10. A varredura.** A lista `ARQUIVOS_DO_KIT` do `test_credito.py` (`:25-35`) ganha o
  `templates/roblox/Executor.luau`, com a linha `-- Golem SDD · …` (o teste compara a linha exata
  em qualquer linguagem, `test_credito.py:49-57`). Os outros arquivos novos (`.md` em
  `templates/` e `docs/`) seguem como os de hoje, que não trazem a linha; os testes novos entram
  em `test_gancho.py`, que já está na lista. O `README.md` ganha uma linha no mapa das pastas
  para `templates/roblox/` e o `docs/guia-roblox.md`. O `.codex/hooks.json` gerado pelo instalador
  continua com os mesmos dois `matcher`.

## Fora de escopo

- **A migração para o Rojo** (a skill, o `rojo syncback`, o `default.project.json`, o código no
  git, as áreas `.luau`/`rojo`/`argon`/`selene`/`stylua`/`wally`, um framework de teste): fase
  própria, registrada no roteiro pelo R1.
- **Guardar o antes e o depois de cada script no git** (o espelho): descartado ("Só salvar o
  place", 2026-11-13).
- **Estilo, gosto × risco na skill de estilo, combinados e limites**: estão na ideação da conversa
  de estratégia (EST) e vão para a fase 3. Daqui, só a lista de riscos (R7).
- **O Codex com o Studio MCP:** o gancho do Codex continua com os `MATCHERS` de hoje; a paridade é
  da fase 6.
- **O `iniciar-sdd` e o `comecar` perguntando "usa Rojo?"**: fase 4 (`docs/plano-produto.md:521-524`).
- **O `run-in-roblox` e a Open Cloud:** o último commit do primeiro é de 2020-07-20. A Open Cloud,
  pelo `open_cloud_invoke` do Studio MCP, dispensa a chave de API, mas não ajuda a rodar os testes
  (o `execute_luau` já roda), e o nível "Full access" pode publicar no jogo ao vivo.
- **Playtest automatizado** (`character_navigation`, `user_keyboard_input`, `screen_capture`): o
  que não tem teste automático continua como passo a passo de playtest no `validation.md` da fase
  do usuário (`docs/plano-produto.md:464-465`).

## Decisões

- **A spec aprovada, com um commit por grupo.** As palavras dele: "Aprovo", à pergunta "Aprova a
  spec da fase 2 (Roblox sem Rojo), com um commit por grupo na branch quando a implementação
  começar?", que também listava a exceção "Completo pelo prompt" (2026-11-13). Com ela, ficam
  aprovadas as leituras do agente listadas abaixo.
- **"Sem Rojo, migrar depois"** (palavras do autor do kit, 2026-11-13, repassadas pela conversa
  gerente). O caminho de entrada é sem Rojo: o código fica no place, e as specs e as lições ficam
  numa pasta ao lado com git, que o agente opera. O kit não exige GitHub; git local basta. Uma
  skill guia a migração para o Rojo quando o usuário quiser ou o projeto crescer. Descartado: o
  Rojo como caminho de entrada, que a seção 5 recomendava (`:418`), porque o primeiro usuário não
  usa Rojo.
- **As respostas da entrevista desta spec** (2026-11-13), todas na opção recomendada:
  1. **"Sem espelho"**, confirmada depois como **"Só salvar o place"** (à pergunta que trouxe o
     "Os dois, como ideia" da conversa de estratégia e o fato de que o `save_place` grava uma
     versão): o agente salva uma versão antes de cada fase; o revisor lê os scripts pelo Studio
     MCP. Descartado: guardar o antes e o depois de cada script no git, que daria diff e o
     desfazer de um script só, mas é uma peça de custo M que envelhece quando ele edita direto no
     Studio.
  2. **"Executor mínimo do kit"** (R6), confirmada como **"Mantém o executor"** depois de os fatos
     dos frameworks serem corrigidos (ver "Contexto"). Descartados: o TestEZ, arquivado (o
     `TestEZ.rbxm` existe até a v0.3.2); e o Jest, cujo repositório ativo (`Roblox/jest-roblox`)
     não tem release com pacote para o place. Os dois seriam dependência nova (regra 3).
  3. **"Fase própria depois"** para a migração (R1). Descartado: a migração nesta fase, que a
     levaria de M a M-G.
  4. **O teste no Studio**, que não está instalado nesta máquina: "Me pergunte novamente quando
     chegarmos nesta etapa em que ele é necessário." O G2 e a verificação manual 1 começam por
     essa pergunta.
  5. **"Fica na fase 2"**: o gancho lê a edição pelo Studio MCP (R3). Pedido da conversa de
     estratégia; a linha da fase 2 no roteiro não o citava. Descartado: tirá-lo, o que deixaria o
     caminho sem Rojo sem lição nenhuma na hora da edição.
  6. **"Nesta fase, como modelo"**: a lista de riscos do Roblox (R7), em `templates/roblox/`.
     Descartado: deixá-la para a fase 3, com o estilo.
- **O fluxo completo nesta fase** ("Completo pelo prompt", do autor do kit, 2026-11-13, repassado
  pela conversa gerente; vale com a aprovação desta spec): revisor e validador a cada grupo, no
  Opus, e guardião no PR. **É uma exceção à decisão 1 da fase 1** ("As fases 2 em diante do kit
  rodam com um revisor só, no Sonnet, uma vez por fase, e servem de teste real da receita",
  `specs/2026-11-13-fase-1-configuracao/requirements.md`, no `7435d83`): esta fase não serve de
  teste da `economico`. O caminho rápido da regra 11 vale para o grupo só de documentação. O G1
  leva a exceção à seção 8.
- **Leituras do agente, para aprovar com a spec:**
  - **O validador não faz mutação no place** (R4): sem cópia descartável, a mutação mudaria o
    place do usuário. Na receita `economico`, o validador já não roda (fase 1, R3).
  - **O executor imprime no formato do TestEZ** (`N passed, N failed, N skipped`): a lição da
    linha de resumo e o hábito de quem migrar continuam valendo.
  - **A linha nova do `settings.json` entra como terceira entrada**, sem mexer nas duas de hoje,
    para o instalador do Codex não mudar.
  - **Os modelos, as lições e a lista de riscos ficam em `templates/roblox/`**, e não em
    `docs/`: são do projeto do usuário; o kit não é um projeto Roblox.
  - **O `POR_COMANDO` não muda** (R3): a área não traz lição com gatilho, e a lição do resumo no
    place vem pelo gatilho dela.
  - **A branch se chama `fase-2-roblox`**, no padrão das fases 0 e 1, renomeada da que o app criou
    para o worktree.

## Contexto

- **O Studio MCP oficial** ([documentação](https://create.roblox.com/docs/studio/mcp), versão de
  `2026-11-14T01:38:48Z`):
  - liga-se em Assistant ⟩ … ⟩ Manage MCP Servers ⟩ "Enable Studio as MCP server"; o quick
    connect liga o Claude Code;
  - na configuração por JSON, o servidor se chama `Roblox_Studio` e roda
    `cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`;
  - as ferramentas de scripts: `script_read` (pelo caminho com pontos, como
    `game.ServerScriptService.MyScript`), `multi_edit` (várias edições num script; cria o script
    se o caminho não existe; "Requires specifying a `datamodel_type` (Edit)"), `script_search` e
    `script_grep`;
  - o `execute_luau` "Requires specifying a datamodel_type (Edit, Client, or Server)"; o
    `get_console_output` lê o log de saída do Studio; o `start_stop_play` e o `get_studio_state`
    controlam o modo de jogo;
  - o `save_place` "Saves the open place the same way as File ⟩ Save: as a new place version for
    places opened from Roblox, or back to the file for local `.rbx` and `.rbxlx` places";
  - toda chamada leva um `studio_id` (o `list_roblox_studios` lista os abertos);
  - o aviso: "MCP clients can read and modify content in your open Roblox places."
  - os nomes dos campos de cada ferramenta não estão na página: a conferir no G2.
- **A Open Cloud pelo Studio MCP** ([documentação](https://create.roblox.com/docs/studio/mcp-open-cloud),
  mesma versão): a ferramenta `open_cloud_invoke` chama as APIs "without creating or pasting an API
  key", só com as permissões ligadas para o jogo, em MCP ⟩ MCP Permissions; "Each game starts at
  Balanced" (escopos de risco baixo e moderado); o nível "Full access" inclui o que pode "publish
  to your live game"; e o aviso: "Studio uses your live data stores. Writes from your client change
  real player data".
- **O `matcher` dos ganchos** ([documentação](https://code.claude.com/docs/en/hooks.md), "Matcher
  patterns", lida em 2026-11-13): só com letras, dígitos, `_`, `-`, espaço, `,` e `|`, é "Exact
  string, or list of exact strings"; com qualquer outro caractere, "JavaScript regular expression,
  unanchored". Por isso `mcp__memory` não casa com nada, e `mcp__memory__.*` casa com o servidor
  inteiro.
- **O histórico de versões** ([documentação](https://create.roblox.com/docs/projects/version-history),
  lida em 2026-11-13): cria versão o "Save to Roblox with Notes" e o "Publish"; a lista se filtra
  por tipo de salvamento ("auto or manual"); restaurar pelo Studio é Window ⟩ Version History ⟩ ⋮ ⟩
  Open Local Copy ⟩ Save to Roblox As; pelo Creator Dashboard é Creations ⟩ o jogo ⟩
  Configurations ⟩ Places ⟩ Version History ⟩ Restore; restaurar cria uma versão nova e "does not
  automatically publish the changes". A página não fala de histórico por script.
- **O Rojo e o `rojo syncback`:** a 7.7.0 é estável, de 2026-07-02, e a mais nova é a 7.7.1, de
  2026-10-02 (API de releases do GitHub, `rojo-rbx/rojo`, lida em 2026-11-13). As notas da 7.7.0:
  o `rojo syncback path/to/project --input path/to/file.rbxl` converte um place existente em
  projeto Rojo; só vem o que descende de um nó do arquivo de projeto; a regra fica no campo
  `syncbackRules`; "Documentation is forthcoming". Pede o place como arquivo `.rbxl`. Isso é da
  fase da migração.
- **Os frameworks de teste** (API do GitHub, lida em 2026-11-13):
  - o `Roblox/testez` está arquivado (último push em 2024-03-05). A última release, v0.4.2, é de
    2022-01-05 e não traz `.rbxm`; as v0.2.0 a v0.3.2 trazem o `TestEZ.rbxm`. O resumo sai como
    `"%d passed, %d failed, %d skipped"` (`src/Reporters/TextReporter.lua:80`);
  - o `Roblox/jest-roblox` (MIT) segue ativo (push em 2026-11-10), sem release publicada;
  - o `jsdotlua/jest-lua` é um fork dele, com o último push em 2024-12-23 (v3.10.0); o `.rbxm`
    aparece só nas releases `v3.6.1-rc.1` e `v3.6.1-rc.2`;
  - o `rojo-rbx/run-in-roblox` teve o último push em 2024-03-06, mas o último commit da `master`
    (a única branch) é o `40fb70c`, "Release 0.3.0", de 2020-07-20.
- **Os subagentes e o MCP** ([documentação](https://code.claude.com/docs/en/sub-agents.md), lida em
  2026-11-13): o `tools:` aceita ferramentas de MCP (`mcp__<servidor>__*` nos exemplos); o
  `disallowedTools` tem o "Same format as `tools`" e mostra o nome exato
  `mcp__reports__run_query`; omitido o `tools:`, o agente herda todas, inclusive as que escrevem;
  "If no entry in the list resolves to a tool, the subagent usually fails to launch"; um
  subagente em segundo plano mantém todas as ferramentas de MCP.
- **O gancho hoje:** o `matcher` é `Edit|Write` e `Bash|PowerShell` (`.claude/settings.json:6` e
  `:17`); o `licoes_relevantes.py` lê só `tool_input.file_path` e `tool_input.command`
  (`:456-458`); o `POR_CAMINHO` casa por trecho contido no caminho (`:462-465`); lição com
  gatilho só entra pelo gatilho (`:260-266`); sem índice, ele lê o Markdown (`:183-196`); as
  regras de área vêm de `docs/regras-de-area.md`, sem teto, uma vez por sessão (`:31-33`).
- **Os agentes hoje** só têm `Read, Grep, Glob, Bash` no `tools:` (`.claude/agents/revisor.md:4`,
  `validador.md:4`); o validador faz a mutação numa cópia descartável (`validador.md:14` e `:37-43`).
- **Esta máquina não tem o Roblox Studio** (`%LOCALAPPDATA%\Roblox` e `Program Files\Roblox`
  ausentes, 2026-11-13). Nem um runtime de Luau: o executor só se testa no Studio.
- **A suíte do ferramental** dá `96 passed` em `1f9f827` (rodada pelo revisor desta spec,
  2026-11-13), sem puladas. A fase 1 acrescenta testes: o total se relê no G1.
- **A ideação da conversa de estratégia** ("o fluxo que aprende", 2026-11-13, fora do git, nas
  notas da sessão de estratégia): dela vêm o R3 como pedido, a lista de riscos com o "avisar e
  deixar" (ideia 1) e os dois jeitos de desfazer (ideia 3b).

## Padrões a seguir

- **Os testes do gancho** seguem `.claude/tests/test_gancho.py` (o JSON de entrada montado no
  teste, o `Acervo` do `conftest.py`).
- **O `tech-stack.md` de Roblox** segue `templates/constituicao/tech-stack.md`, seção por seção.
- **As lições de exemplo** seguem o formato de `docs/licoes/README.md` e uma lição real, como
  `docs/licoes/suite-verde-so-vale-com-a-linha-de-resumo.md`.
- **A lista de riscos** segue o formato que o `regras_para` lê (`licoes_relevantes.py:270-296`).
- **O guia** segue o `docs/guia-configuracao.md` da fase 1: uma página, palavras simples, nenhuma
  sigla sem dizer o que é (`docs/plano-produto.md:532-533`).

## Notas do usuário

- "Sem Rojo, migrar depois" (2026-11-13).
- Sobre o primeiro usuário: não usa Rojo, e "Não parece ter muita experiência com controle de
  versões ainda" (2026-11-13).
- "Completo pelo prompt" (2026-11-13, o fluxo desta fase).
- "Me pergunte novamente quando chegarmos nesta etapa em que ele é necessário." (2026-11-13, sobre
  o Studio para o teste real).
- À conversa de estratégia, sobre o desfazer: "Os dois, como ideia" (2026-11-13); aqui, depois:
  "Só salvar o place".

## Teto de gasto

Nenhum: a fase não gasta dinheiro. O Studio e o Studio MCP são gratuitos; a Open Cloud fica fora.

## Perguntas em aberto

- **As três perguntas ao primeiro usuário** (R1): se toparia migrar para o Rojo, como organiza os
  jogos, como volta a uma versão hoje. Não bloqueiam: o guia diz "uma pasta por jogo" como
  sugestão, e a resposta pode mudar o guia antes do merge.
- **Onde rodar o teste no Studio:** perguntar ao autor do kit no começo do G2 (decisão 4).
- **As sete conferências do R2:** a conferir no G2; cada uma que mudar o desenho volta ao autor do
  kit.
- **Se o nome exato de uma ferramenta de MCP vale no `tools:`** do agente (a documentação só o
  mostra no `disallowedTools`): a conferir no G4.
- **As fontes da lista de riscos** (R7): a conferir no G5, item por item.
