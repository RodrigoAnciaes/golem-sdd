# Fase 2: Roblox mínimo, sem Rojo — Plano

A implementação começa depois do merge da fase 1: antes do G1, a branch traz a `main` nova
(`git fetch origin` e o rebase ou o merge da `origin/main`, com o ok do autor do kit se houver
conflito) e reconfere as linhas citadas na spec (regra 9).

Fluxo completo (decisão "Completo pelo prompt", 2026-11-13): cada grupo fecha com a suíte do
ferramental (a linha de resumo lida) e com o revisor e o validador, chamados com o modelo `opus`
na chamada. O G1, só de documentação, vai pelo caminho rápido (um revisor). O guardião roda sobre
o diff inteiro do PR. Um commit por grupo na branch da fase, se o autor do kit aprovar assim.

## G1 — O registro e o roteiro (R1)

- [ ] Trazer a `main` com a fase 1 e reconferir: a suíte (o total novo, escrito no
  `validation.md`, item 1), a régua, e as linhas citadas no `requirements.md`. Linha que andou se
  corrige na spec, no mesmo commit.
- [ ] Reler as páginas do Studio MCP e do histórico de versões: o que mudou desde a versão citada
  no "Contexto" se corrige na spec antes de ir ao plano.
- [ ] Recado à GER antes de tocar o `docs/plano-produto.md` (arquivo comum).
- [ ] `docs/plano-produto.md`, seção 8: a decisão "Sem Rojo, migrar depois", as seis respostas da
  entrevista e a exceção do fluxo completo à decisão 1 da fase 1, com as palavras e a data.
- [ ] `docs/plano-produto.md`, seção 5: o caminho sem Rojo como o de entrada; o Rojo como destino
  da migração; os fatos do "Contexto" com o link. Os itens "a conferir" de hoje que a spec
  resolveu deixam de dizer "a conferir"; os que ficam para o G2 dizem "a conferir na fase 2".
- [ ] `docs/plano-produto.md`, seção 7: a linha da fase 2 com a entrega e o "pronto" do R9; a linha
  nova "Migração para o Rojo", no fim, "ordem a decidir"; as perguntas "Antes da fase 2".
- [ ] Caminho rápido: o revisor confere cada fato contra a fonte.

## G2 — As conferências no Studio (R2)

- [ ] Perguntar ao autor do kit onde o Studio vai rodar (decisão 4 da entrevista) e esperar a
  resposta.
- [ ] Ligar o Studio MCP ao Claude Code pelo quick connect; anotar o nome do servidor (a lista de
  ferramentas da sessão).
- [ ] Num place de teste (Baseplate novo, salvo no Roblox), com um gancho de registro temporário
  **fora do repositório do kit** (um `.claude/settings.local.json` numa pasta de teste, que grava o
  JSON de entrada num arquivo), anotar os campos do `multi_edit` e do `execute_luau` (R2.2).
- [ ] O `require` em modo de edição (R2.3): criar um ModuleScript que devolve `1`, ler pelo
  `execute_luau`, mudar para `2` pelo `multi_edit`, ler de novo. Anotar o que voltou.
- [ ] O `get_console_output` (R2.4): dois `print` em duas chamadas do `execute_luau`; anotar se o
  segundo `get_console_output` traz os dois ou só o novo.
- [ ] O `save_place` (R2.5): chamar e ver no Window ⟩ Version History se apareceu uma versão.
- [ ] O nome com ponto (R2.6): `multi_edit` em `game.ServerStorage.Moedas.spec` e ver no Explorer
  se nasceu um script `Moedas.spec` ou um `spec` dentro de `Moedas`; e o `script_read` do mesmo
  caminho.
- [ ] O Ctrl+Z (R2.7): editar um script pelo `multi_edit`, apertar Ctrl+Z no Studio e ver se a
  edição sumiu.
- [ ] Anotar as sete respostas abaixo, com a saída colada, e na tabela de alterações o que mudou no
  desenho. Anotar também se os campos do R2.2 já se chamam `file_path` ou `command`: nesse caso, o
  gancho já os lê: o teste 1 do G3 passa a provar só o `POR_CAMINHO`, e o teste 2 não prova código
  novo. O que mudar o R3 ao R8 volta ao autor do kit antes do G3.
- [ ] Revisor e validador sobre as anotações: o validador confere que cada uma tem a saída e que
  as conclusões seguem dela (ele não tem o `multi_edit` e não repete as edições).

### Respostas do G2

(a preencher no G2)

## G3 — O gancho vê o Studio MCP (R3)

- [ ] `.claude/settings.json`: a terceira entrada `PreToolUse`, com o `matcher` das duas
  ferramentas (com o nome do servidor do G2 ou um padrão que não dependa dele) e o mesmo conteúdo
  de `hooks` (`command`, `timeout`, `statusMessage`).
- [ ] `.claude/hooks/licoes_relevantes.py`: ler os campos do G2 como caminho e como comando; o
  `POR_CAMINHO` com os serviços na forma `game.<Serviço>`; a docstring `:9-13`.
- [ ] Testes em `.claude/tests/test_gancho.py`:
  1. `test_multi_edit_num_script_do_place_acende_codigo`;
  2. `test_execute_luau_chega_aos_gatilhos`;
  3. `test_matcher_do_studio_casa_so_com_edicao_e_execucao`;
  4. `test_settings_tem_a_entrada_do_studio_com_o_mesmo_comando`;
  5. `test_pasta_workspace_num_arquivo_nao_acende_codigo`.
- [ ] O instalador do Codex numa cópia: o `.codex/hooks.json` gerado tem os mesmos dois `matcher`.
- [ ] Suíte, revisor e validador.

## G4 — O revisor e o validador leem o place (R4)

- [ ] `.claude/agents/revisor.md`: as sete ferramentas de leitura no `tools:` (com o
  `list_roblox_studios`); o parágrafo do
  caminho sem Rojo (a lista de scripts recebida da conversa, o `script_read`).
- [ ] `.claude/agents/validador.md`: as mesmas, mais o `execute_luau` (e o `start_stop_play` e o
  `get_studio_state`, se o G2 mandar rodar em modo de jogo); o parágrafo do caminho sem Rojo (o
  executor, a linha de resumo, a mutação pulada no place e por quê).
- [ ] Conferir, com o Studio ligado, que um revisor chamado tem o `script_read` e consegue ler um
  script, e não tem o `multi_edit`.
- [ ] Conferir, numa pasta sem o Studio MCP, que o revisor ainda abre e lê um arquivo.
- [ ] Rodar o `aplicar` da fase 1 numa cópia e conferir que o `tools:` novo continua, e o `model:`
  também.
- [ ] Varredura: a description dos dois agentes, se mencionar o que mudou; o instalador do Codex
  regera as cópias dos agentes sem erro, numa cópia.
- [ ] Suíte, revisor e validador.

## G5 — O executor, os modelos, os exemplos e o guia (R5 a R8, R10)

- [ ] `templates/roblox/Executor.luau` (R6), com a linha de crédito, e um exemplo de teste com um
  que passa, um que se pula e nenhum que falha (o nome conforme o R2.6).
- [ ] No Studio: pôr o executor e o exemplo pelo `multi_edit`, rodar pelo `execute_luau` e ler no
  console `1 passed, 0 failed, 1 skipped`; sem teste, `0 passed, 0 failed, 0 skipped` e
  "nenhum teste encontrado"; com um teste que falha, `failed` e a linha da falha. Colar as saídas
  aqui.
- [ ] `templates/roblox/tech-stack.md` e `templates/roblox/comandos-reais.md` (R5).
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
| | | | |
