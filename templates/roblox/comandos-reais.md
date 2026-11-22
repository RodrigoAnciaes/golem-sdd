## Comandos reais

Num jogo do Roblox sem Rojo, não há comando de terminal: tudo passa pelo Studio MCP (o servidor
`Roblox_Studio`), com o place aberto no Roblox Studio. Toda chamada leva o `studio_id`, que o
`list_roblox_studios` dá; ele também diz `"persistedToCloud": true` quando o place está salvo no
Roblox.

**Antes de começar cada fase:** chame o `save_place` e anote no `plan.md` (no formato curto, no
`requirements.md`) a hora e a versão que ele
devolveu (`"version": N`). Ela é o ponto de volta pelo histórico de versões. Se o place estiver
aberto de um arquivo local (`.rbxl`), o `save_place` grava por cima do arquivo e não cria versão:
pare e peça ao usuário que salve o place no Roblox (Arquivo ⟩ Salvar na Roblox) antes da fase.

**Os testes** (a linha de resumo tem de aparecer), em modo de jogo:

1. `start_stop_play` com `is_start: true`; confira no `get_studio_state` que o DataModel `Server`
   existe.
2. `execute_luau` com `datamodel_type` `Server` e o código
   `return require(game.ServerStorage.GolemTestes.Executor).rodar()`.
3. `get_console_output`: leia a linha `N passed, N failed, N skipped` e as linhas `FALHOU`.
4. `start_stop_play` com `is_start: false`.

Ligar o jogo roda também os scripts do jogo. Se eles usam `DataStore` e o acesso do Studio às APIs
está ligado ("Enable Studio Access to API Services", em Arquivo ⟩ Configurações de experiência;
desligado por padrão), o dado é o do jogo publicado.

**Ao chamar o revisor ou o validador:** sem diff no git, passe na chamada os caminhos dos scripts
que o grupo mexeu pelo `multi_edit` (por exemplo, `game.ServerStorage.Moedas`). É por eles que o
revisor lê o place.

**Lint e formatação:** não há.

**Stack:** Luau no Roblox Studio, sem Rojo; o detalhe vive em `specs/tech-stack.md`.

**Contagem esperada de testes:** no `validation.md` da fase.
