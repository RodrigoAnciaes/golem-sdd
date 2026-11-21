# Fase 2: Roblox mínimo, sem Rojo — Plano

A implementação começa depois do merge da fase 1: antes do G1, a branch traz a `main` nova
(`git fetch origin` e o rebase ou o merge da `origin/main`, com o ok do autor do kit se houver
conflito) e reconfere as linhas citadas na spec (regra 9).

Fluxo completo (decisão "Completo pelo prompt", 2026-11-13): cada grupo fecha com a suíte do
ferramental (a linha de resumo lida) e com o revisor e o validador, chamados com o modelo `opus`
na chamada. O G1, só de documentação, vai pelo caminho rápido (um revisor). O guardião roda sobre
o diff inteiro do PR. Um commit por grupo na branch da fase, se o autor do kit aprovar assim.

## G1 — O registro e o roteiro (R1)

- [x] Trazer a `main` com a fase 1 e reconferir: a suíte (o total novo, escrito no
  `validation.md`, item 1), a régua, e as linhas citadas no `requirements.md`. Linha que andou se
  corrige na spec, no mesmo commit.
- [x] Reler as páginas do Studio MCP e do histórico de versões: o que mudou desde a versão citada
  no "Contexto" se corrige na spec antes de ir ao plano.
- [x] Recado à GER antes de tocar o `docs/plano-produto.md` (arquivo comum).
- [x] `docs/plano-produto.md`, seção 8: a decisão "Sem Rojo, migrar depois", as seis respostas da
  entrevista e a exceção do fluxo completo à decisão 1 da fase 1, com as palavras e a data.
- [x] `docs/plano-produto.md`, seção 5: o caminho sem Rojo como o de entrada; o Rojo como destino
  da migração; os fatos do "Contexto" com o link. Os itens "a conferir" de hoje que a spec
  resolveu deixam de dizer "a conferir"; os que ficam para o G2 dizem "a conferir na fase 2".
- [x] `docs/plano-produto.md`, seção 7: a linha da fase 2 com a entrega e o "pronto" do R9; a linha
  nova "Migração para o Rojo", no fim, "ordem a decidir"; as perguntas "Antes da fase 2".
- [x] Caminho rápido: o revisor confere cada fato contra a fonte (sem bloqueio em duas rodadas;
  os 7 achados da primeira, corrigidos).

## G2 — As conferências no Studio (R2)

- [x] Perguntar ao autor do kit onde o Studio vai rodar (decisão 4 da entrevista) e esperar a
  resposta.
- [x] Ligar o Studio MCP ao Claude Code pelo quick connect; anotar o nome do servidor (a lista de
  ferramentas da sessão).
- [x] Num place de teste (Baseplate novo, salvo no Roblox), com um gancho de registro temporário
  **fora do repositório do kit** (um `.claude/settings.local.json` numa pasta de teste, que grava o
  JSON de entrada num arquivo), anotar os campos do `multi_edit` e do `execute_luau` (R2.2).
- [x] O `require` em modo de edição (R2.3): criar um ModuleScript que devolve `1`, ler pelo
  `execute_luau`, mudar para `2` pelo `multi_edit`, ler de novo. Anotar o que voltou.
- [x] O `get_console_output` (R2.4): dois `print` em duas chamadas do `execute_luau`; anotar se o
  segundo `get_console_output` traz os dois ou só o novo.
- [x] O `save_place` (R2.5): chamar e ver no Window ⟩ Version History se apareceu uma versão.
- [x] O nome com ponto (R2.6): `multi_edit` em `game.ServerStorage.Moedas.spec` e ver no Explorer
  se nasceu um script `Moedas.spec` ou um `spec` dentro de `Moedas`; e o `script_read` do mesmo
  caminho.
- [x] O Ctrl+Z (R2.7): editar um script pelo `multi_edit`, apertar Ctrl+Z no Studio e ver se a
  edição sumiu.
- [x] Anotar as sete respostas abaixo, com a saída colada, e na tabela de alterações o que mudou no
  desenho. Anotar também se os campos do R2.2 já se chamam `file_path` ou `command`: nesse caso, o
  gancho já os lê: o teste 1 do G3 passa a provar só o `POR_CAMINHO`, e o teste 2 não prova código
  novo. O que mudar o R3 ao R8 volta ao autor do kit antes do G3.
- [x] Revisor e validador sobre as anotações: o validador confere que cada uma tem a saída e que
  as conclusões seguem dela (ele não tem o `multi_edit` e não repete as edições). Feito (2026-11-21): revisor sem bloqueio
  na segunda rodada; validador "valida" (123 passed, a régua ok).

### Respostas do G2

Feitas em 2026-11-21, nesta máquina, com o Roblox Studio instalado pelo autor do kit, num place
novo (Baseplate) salvo no Roblox com a "Criação em equipe" ligada, como vem por padrão. O Studio foi
operado pela conversa, com o controle da tela que ele ofereceu ("Se você achar necessário, eu posso
dar permissão para controlar minha tela", 2026-11-21). As chamadas ao Studio MCP rodaram pelo
`claude -p` (decisão do autor do kit, pela EST, 2026-11-13): as rodadas 1 a 3 numa pasta descartável
fora do repositório, com `--strict-mcp-config`, `--mcp-config` só com o servidor do Studio e
`--settings` com um gancho `PreToolUse` que gravava o JSON de entrada de cada chamada; a rodada 5
na mesma pasta, sem o gancho; a rodada 4 na pasta do worktree, sem configuração extra (uma conversa nova, como a de um usuário).
Rodadas: 1 (11 passos), 2 (8), 3 (9), 4 e 5 (só leitura), todas `success`. Os nomes da conta do
Roblox foram trocados por `<usuário>` abaixo. **A prova** (os prompts das rodadas 1 a 5, as transcrições
`saida*.jsonl`, o `entradas.jsonl` e o print do histórico) está fora do repositório, na pasta de
notas da GER, `fase-2-g2-prova/`; o que sustenta cada resposta está colado aqui.

1. **O servidor (R2.1): `Roblox_Studio`.**
   - O quick connect do Studio (Configurações do Assistente ⟩ Servidores MCP ⟩ Conexão rápida ⟩
     Claude Code CLI) não liga sozinho: mostra o comando `claude mcp add --transport stdio
     Roblox_Studio -- "cmd.exe" "/c" ...` e "Execute este comando no diretório do seu projeto"
     (visto na tela, sem arquivo).
   - Rodado pela ferramenta Bash (Git Bash), o comando gravou
     `Args: C:/ %LOCALAPPDATA%\Roblox\mcp.bat` e não conectou ("connection timed out after
     30000ms"); pelo PowerShell, gravou `Args: /c %LOCALAPPDATA%\Roblox\mcp.bat`, e o
     `claude mcp get Roblox_Studio` deu `Status: √ Connected` (a lição
     `o-git-bash-troca-o-barra-c-do-cmd-por-c`). Rodado no worktree, o `claude mcp add` gravou o
     registro sob a pasta principal do projeto ("File modified: ...\.claude.json [project: <pasta
     principal>]").
   - Esta conversa, já aberta, não viu o servidor: a `ToolSearch` por "Roblox_Studio" respondeu "No
     matching deferred tools found".
   - Uma conversa nova (rodada 4), aberta no worktree, viu: no `init`, `{'name': 'Roblox_Studio',
     'status': 'connected', 'source': 'local'}`, com 37 ferramentas `mcp__Roblox_Studio__*`, e o
     `script_read` funcionou.
   - Na mesma tela, o "Data access" estava ligado ("To help improve the Studio experience,
     provide Roblox with access to prompt information."). Ele foi desligado, porque o kit não
     precisa dele e ele manda os prompts à Roblox (leitura do agente, a levar ao guia).
2. **Os campos (R2.2)**, como o gancho os recebeu no `tool_input`:
   - `multi_edit`: `{"file_path": "game.ServerStorage.G2Modulo", "edits": [{"old_string": "",
     "new_string": "return 1"}], "className": "ModuleScript", "datamodel_type": "Edit",
     "studio_id": "..."}`. **O caminho chega em `file_path`**, que o gancho já lê
     (`licoes_relevantes.py:470`);
   - `execute_luau`: `{"code": "print(\"G2-A\", ...) return ...", "datamodel_type": "Edit",
     "studio_id": "..."}`. **O código chega em `code`**, que o gancho ainda não lê;
   - `script_read`: `{"target_file": "game.ServerStorage.Moedas.spec", "studio_id": "..."}`;
   - `start_stop_play`: `{"is_start": true, "studio_id": "..."}`.

   O gancho lê só `file_path` e `command` (`licoes_relevantes.py:470-472`), nunca `code`. O
   validador do G2 o rodou com essas entradas e duas lições de teste (uma com gatilho
   `game\.ServerStorage`, outra com gatilho no texto do `code`): o `multi_edit` entregou a
   primeira; o `execute_luau` não entregou nada; o mesmo texto do `code` posto em `command`
   entregou as duas. Por isso, o teste 1 do G3 prova só o `POR_CAMINHO`, e a leitura
   nova do G3 é só a do `code`.
3. **O `require` em modo de edição (R2.3): devolve o módulo guardado.**
   - O `G2Modulo` com `return 1`: o `execute_luau` (Edit) devolveu `1`. Trocado para `return 2`
     pelo `multi_edit` ("Modified G2Modulo (ModuleScript) with 1 edits applied"), a mesma leitura
     devolveu `1`. Na rodada 2, o `script_read` mostrou `return 2`, e o `require` (Edit) ainda
     devolveu `1`.
   - **O clone:** `require(game.ServerStorage.G2Modulo:Clone())` (Edit) devolveu `2`. Na rodada 3,
     um `G2Chamador` com `return require(game.ServerStorage.G2Modulo)`, clonado e chamado
     (`require(game.ServerStorage.G2Chamador:Clone())`), devolveu `1`: o clone refresca o próprio
     módulo, e o que ele chama por `require` continua o guardado.
   - **O modo de jogo:** `start_stop_play` com `is_start: true` ("Game Started"; o
     `get_studio_state` disse "Current Studio Mode: Play", "Available DataModels: Client,
     Server"), o `execute_luau` com `datamodel_type` `Server` devolveu `2`, e o `start_stop_play`
     com `is_start: false` voltou ao modo de edição ("Game Stopped").
   - **Os scripts do jogo rodam no modo de jogo:** na rodada 3, um Script
     `game.ServerScriptService.G2Script` com `print("G2-SCRIPT rodou")`; ligado o jogo, o
     `get_console_output` trouxe "G2-SCRIPT rodou".
4. **O console (R2.4): o `print` do `execute_luau` chega nele; na sessão de edição, o log é
   cumulativo.** O primeiro `get_console_output` trouxe "DataModel Loading ... | `<usuário>` joined
   live editing session. | G2-A 1"; o segundo, o mesmo e mais "G2-B 1". Nas duas jogadas (rodadas 2
   e 3), o `get_console_output` trouxe só o daquela jogada ("G2-C 2"; "G2-SCRIPT rodou"). O
   `execute_luau` também devolve o valor do `return`.
5. **O `save_place` (R2.5): grava uma versão.** A resposta: `{"location":"TeamCreate",
   "status":"Saved","version":3,"message":"Saved to Roblox."}`. Em Janela ⟩ Histórico da versão
   apareceu a v3 (a do `version: 3`), às 16:42; a chamada foi às 16:41:27. A v1 e a v2 são do
   "Salvar na Roblox" que criou o place, às 16:38. Na interface em português, o menu é "Janela ⟩
   Histórico da versão".
6. **O nome com ponto (R2.6): o ponto separa.** O `multi_edit` em `game.ServerStorage.Moedas.spec`
   respondeu "Created spec (ModuleScript)", e os descendentes do `ServerStorage` passaram a ser
   `ServerStorage.Moedas [Folder]` e `ServerStorage.Moedas.spec [ModuleScript]`: ele criou uma pasta
   `Moedas` e um ModuleScript `spec` dentro dela (visto também no Explorer). A convenção do R6
   passa a ser o sufixo `_spec`.
7. **O Ctrl+Z (R2.7): desfaz a criação de um script, e não a troca de texto.**
   - Depois da rodada 1, Editar ⟩ Desfazer (Ctrl+Z) apagou de uma vez a pasta `Moedas` e o `spec`, a
     última criação (no Explorer: antes, `Moedas` ⟩ `spec` e `G2Modulo`; depois, só `G2Modulo`).
   - Na rodada 3, a última chamada foi a troca de texto do `G2Modulo` (`return 2` → `return 3`),
     depois da criação do `G2Script`. O Ctrl+Z no Studio deixou o `G2Modulo` com `return 3` (rodadas
     4 e 5, `script_read`) e apagou o `G2Script` ("Script not found at path:
     game.ServerScriptService.G2Script", rodada 5). A troca de texto pelo `multi_edit` não entrou
     no desfazer do Studio. Foi uma tentativa só, com o Ctrl+Z apertado com o foco na janela 3D.

**O que muda no desenho** (na tabela abaixo): o executor roda em modo de jogo, e rodar os testes
roda também os scripts do jogo (R2.3, R6, R8); a convenção é `_spec` (R2.6); o G3 lê o `code` do
`execute_luau`, e o `file_path` do `multi_edit` já é lido (R2.2); o guia não oferece o Ctrl+Z como
desfazer do que o agente escreveu, só o histórico de versões, e explica o registro do servidor, a
conversa nova e o "Data access" (R2.1, R2.7, R8).

## G3 — O gancho vê o Studio MCP (R3)

- [x] `.claude/settings.json`: a terceira entrada `PreToolUse`, com o `matcher` das duas
  ferramentas (com o nome do servidor do G2 ou um padrão que não dependa dele) e o mesmo conteúdo
  de `hooks` (`command`, `timeout`, `statusMessage`).
- [x] `.claude/hooks/licoes_relevantes.py`: ler o `tool_input.code` do `execute_luau` como comando; o
  `POR_CAMINHO` com os serviços na forma `game.<Serviço>`; a docstring `:9-13`.
- [x] Testes em `.claude/tests/test_gancho.py`:
  1. `test_multi_edit_num_script_do_place_acende_codigo`;
  2. `test_execute_luau_chega_aos_gatilhos`;
  3. `test_matcher_do_studio_casa_so_com_edicao_e_execucao`;
  4. `test_settings_tem_a_entrada_do_studio_com_o_mesmo_comando`;
  5. `test_pasta_workspace_num_arquivo_nao_acende_codigo`.
- [x] O instalador do Codex numa cópia: o `.codex/hooks.json` gerado tem os mesmos dois `matcher`.
- [x] Suíte, revisor e validador: `128 passed`; revisor sem bloqueio (com o `game.ReplicatedFirst`
  acrescentado, achado dele); validador "valida", com as quatro mutações pegas (2026-11-21).

## G4 — O revisor e o validador leem o place (R4)

- [x] `.claude/agents/revisor.md`: as sete ferramentas de leitura no `tools:` (com o
  `list_roblox_studios`); o parágrafo do
  caminho sem Rojo (a lista de scripts recebida da conversa, o `script_read`).
- [x] `.claude/agents/validador.md`: as mesmas, mais o `execute_luau`, o `start_stop_play` e o
  `get_studio_state` (o executor roda em modo de jogo); o parágrafo do caminho sem Rojo (o
  executor, a linha de resumo, a mutação pulada no place e por quê).
- [x] Conferir, com o Studio ligado, que um revisor chamado tem o `script_read` e consegue ler um
  script, e não tem o `multi_edit`.
- [x] Conferir, numa pasta sem o Studio MCP, que o revisor ainda abre e lê um arquivo.
- [x] Rodar o `aplicar` da fase 1 numa cópia e conferir que o `tools:` novo continua, e o `model:`
  também.
- [x] Varredura: a description dos dois agentes, se mencionar o que mudou; o instalador do Codex
  regera as cópias dos agentes sem erro, numa cópia.
- [x] Suíte, revisor e validador: `128 passed`; revisor sem bloqueio na segunda rodada (o bloqueio
  da primeira, o veredito do validador no place, corrigido); validador "valida", com as três
  mutações pegas (2026-11-21).

### O que o G4 conferiu (2026-11-21)

Pelo `claude -p`, no worktree, com a prova (os prompts e as transcrições `saida-g4a.jsonl`,
`saida-g4b.jsonl` e `saida-g4c.jsonl`) em `fase-2-g4-prova/`, na pasta de notas da GER. O `aplicar` e
o Codex rodaram numa cópia sem transcrição guardada; o validador do G4 os refez e deu o mesmo:

- **Com o Studio ligado** (`saida-g4a.jsonl`): o `init` lista o `revisor` entre os agentes (o
  frontmatter é YAML válido). Chamado pela ferramenta Agent, ele disse ter só as sete ferramentas
  de leitura do Studio e "`mcp__Roblox_Studio__multi_edit`: não tenho"; o `script_read` em
  `game.ServerStorage.G2Modulo` devolveu `1→return 3`.
- **Sem o servidor do Studio** (`--strict-mcp-config` com `{"mcpServers": {}}`, `saida-g4b.jsonl`):
  o `revisor` aparece entre os agentes, disse ter só `Read`, `Grep`, `Glob` e `Bash`, avisa que não tem
  as ferramentas do Studio e lê as três primeiras linhas do `AGENTS.md`.
- **O `aplicar`**, numa cópia com os agentes novos: "nada mudou: o AGENTS.md e os agentes já seguem
  o golem.toml"; o `tools:` e o `model:` dos dois continuam. O `test_aplicar_escreve_o_model_dos_dois_agentes`
  prova o mesmo com o `model:` trocado.
- **O Codex**, na mesma cópia: o instalador gerou 24 arquivos, e o `--conferir` deu ok.
- **O validador com o Studio ligado** (`saida-g4c.jsonl`, rodado pelo validador do G4): disse ter
  as 10 ferramentas do Studio do `tools:` e não ter o `multi_edit`; chamou só o
  `list_roblox_studios` e o `get_studio_state` ("Current Studio Mode: Edit"), sem ligar o jogo.

## G5 — O executor, os modelos, os exemplos e o guia (R5 a R8, R10)

- [ ] `templates/roblox/Executor.luau` (R6), com a linha de crédito, e um exemplo de teste com um
  que passa, um que se pula e nenhum que falha (o nome conforme o R2.6).
- [ ] No Studio: pôr o executor e o exemplo pelo `multi_edit`, rodar em modo de jogo (R6) e ler no
  console `1 passed, 0 failed, 1 skipped`; sem teste, `0 passed, 0 failed, 0 skipped` e
  "nenhum teste encontrado"; com um teste que falha, `failed` e a linha da falha. Colar as saídas
  aqui.
- [ ] `templates/roblox/tech-stack.md` e `templates/roblox/comandos-reais.md` (R5). O
  `comandos-reais.md` diz também que, ao chamar o revisor ou o validador, a conversa passa os
  caminhos dos scripts que o `multi_edit` tocou no grupo: sem diff no git, é a entrada de que o
  revisor precisa (`revisor.md`, "Código num place do Roblox Studio"; achado do revisor do G4).
- [ ] `templates/roblox/licoes/`: as duas lições de exemplo (R7), com a fonte de cada fato.
- [ ] `templates/roblox/regras-de-area.md`: a lista de riscos (R7). Cada candidata conferida na
  documentação do Roblox, com o link; a que não tiver fonte sai. De 5 a 8 regras.
- [ ] Testes:
  6. `test_licoes_de_exemplo_do_roblox_chegam_pelo_studio_mcp`;
  7. `test_riscos_do_roblox_chegam_num_multi_edit`.
- [ ] `docs/guia-roblox.md` (R8). Fechar o Studio e pedir um `script_read`: anotar o que aparece,
  para o guia.
- [ ] A varredura do R10: `test_credito.py`, `README.md`.
- [ ] Suíte, revisor e validador.

## G6 — Verificação

- [ ] Percorrer o `validation.md` inteiro, com a saída real de cada comando.
- [ ] A verificação manual 1 (o "pronto"), com o autor do kit, onde ele disse no G2.
- [ ] O guardião sobre o diff inteiro do PR.

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Quem aprovou |
|---|---|---|---|
| 2026-11-21 | As verificações manuais e as conferências que não precisam dos olhos do autor do kit rodam pelo `claude -p`, numa pasta descartável fora do kit, com a transcrição como prova | decisão do autor do kit na ideação da EST: "Ok, vamos seguir sua recomendação." (2026-11-13), repassada pela GER | o autor do kit, na EST |
| 2026-11-21 | O executor roda em modo de jogo (R6), e o validador ganha o `start_stop_play` e o `get_studio_state` (R4) | o `require` em modo de edição devolve o módulo guardado (G2, resposta 3) | "Modo de jogo (Recomendado)" (2026-11-21) |
| 2026-11-21 | A convenção de nome dos testes é `_spec`, e não `.spec` (R6) | o ponto separa no caminho do Studio MCP (G2, resposta 6) | previsto no R2.6 da spec aprovada |
| 2026-11-21 | A leitura nova do gancho é só a do `code` do `execute_luau` (R3) | o `multi_edit` já manda o caminho em `file_path` (G2, resposta 2) | previsto no `plan.md`, G2 ("nesse caso, o gancho já os lê") |
| 2026-11-21 | O guia (R8): o Ctrl+Z sai como desfazer do que o agente escreve, e o desfazer é o histórico de versões; o guia explica o registro do servidor pelo PowerShell, a conversa nova e o "Data access" desligado; e avisa que rodar os testes roda os scripts do jogo | G2, respostas 1, 3 e 7 | "Essas mudanças estão ok ok" (2026-11-21) |
| 2026-11-21 | O guia (R8) oferece que o agente faça a configuração do Studio pelo controle da tela, com o que a documentação disser de onde ele existe (a conferir no G5) | o G2 configurou o Studio assim | "você poderia oferecer isso para o usuário" (2026-11-21) |
| 2026-11-21 | O `test_aplicar_escreve_o_model_dos_dois_agentes` (`.claude/tests/test_golem.py`, da fase 1) lê a linha `tools:` do próprio revisor, em vez de fixar `Read, Grep, Glob, Bash`; assim ele prova também que o `aplicar` mantém o `tools:` novo | o teste fixava a lista antiga e falhou com o G4 | detalhe de implementação (o R4 pede que o `aplicar` não colida com o `tools:`) |
