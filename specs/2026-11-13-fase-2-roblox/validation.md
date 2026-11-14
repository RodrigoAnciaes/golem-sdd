# Fase 2: Roblox mínimo, sem Rojo — Validação

O contrato de merge. Cada item se marca com a saída real, no head que vai ao PR. Os comandos usam
os caminhos desta máquina (sem Python no PATH):

- `PYT` = `"C:\Users\rodri\Documents\Rodrigo\Insper\ProjetoImportExport\agent_validation_env\.venv\Scripts\python.exe"`
- `PY` = `"C:\Users\rodri\AppData\Local\Programs\Python\Python312\python.exe"`

## Verificações automatizadas

1. **A suíte do ferramental:**
   `$PYT -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs`
   → `<N> passed`, 0 falhas, 0 puladas, em que `<N>` é o total da `main` depois do merge da fase 1
   (lido no G1 e escrito aqui: `____`) mais os 7 testes novos desta fase (5 do G3 e 2 do G5).
   Pulado é falha até prova em contrário (regra 8).
2. **Os testes novos, um por um**, com `-k`, cada um `1 passed`:
   `test_multi_edit_num_script_do_place_acende_codigo`,
   `test_execute_luau_chega_aos_gatilhos`,
   `test_matcher_do_studio_casa_so_com_edicao_e_execucao`,
   `test_settings_tem_a_entrada_do_studio_com_o_mesmo_comando`,
   `test_pasta_workspace_num_arquivo_nao_acende_codigo`,
   `test_licoes_de_exemplo_do_roblox_chegam_pelo_studio_mcp`,
   `test_riscos_do_roblox_chegam_num_multi_edit`.
3. **Os testes pegam o defeito** (o validador, numa cópia descartável): tirar a leitura do campo
   do `multi_edit` do `licoes_relevantes.py` faz o teste 1 falhar; tirar a entrada nova do
   `settings.json` faz o teste 4 falhar; tirar `game.ServerScriptService` do `POR_CAMINHO` faz o
   teste 1 falhar; trocar `game.Workspace` por `Workspace` no `POR_CAMINHO` faz o teste 5 falhar.
   Se o G2 mostrou que o campo já era `file_path` ou `command`, a primeira mutação não se aplica, e
   o registro diz isso.
4. **A régua:** `$PY .claude/regua.py --conferir` → sai com código 0, sem divergência. As lições de
   exemplo em `templates/roblox/licoes/` não entram no índice do kit
   (`grep -c roblox .claude/indice/licoes.yaml` → `0`, salvo lição real da regra 7 sobre Roblox).
5. **O Codex:** numa cópia do repositório, `$PY .claude/instalar_codex.py` e depois ler o
   `.codex/hooks.json` gerado → só os dois `matcher` de antes da fase, `Bash` e `apply_patch` (os
   `MATCHERS`, `.claude/instalar_codex.py:39`).
6. **O `aplicar` não apaga o `tools:`:** numa cópia do repositório, `$PY .claude/golem.py aplicar`
   e depois `git diff .claude/agents/` → nenhuma linha `tools:` mudou.
7. **Só os arquivos previstos:** `git diff --stat origin/main...HEAD` lista só a pasta da spec,
   `docs/plano-produto.md`, `docs/guia-roblox.md`, `templates/roblox/`, `.claude/settings.json`,
   `.claude/hooks/licoes_relevantes.py`, `.claude/agents/revisor.md`, `.claude/agents/validador.md`,
   `.claude/tests/`, `README.md`, o `CHANGELOG.md` se a `validar-fase` o pedir e, se a regra 7
   disparar, `docs/licoes/` e `.claude/indice/`.
8. **O registro do G2:** o `plan.md`, seção "Respostas do G2", tem as sete respostas do R2, cada
   uma com a saída colada (o JSON de entrada, a saída do `execute_luau`, do `get_console_output`,
   o print do Version History ou a lista do Explorer).
9. **Os modelos (R5):** `templates/roblox/tech-stack.md` tem as seções de
   `templates/constituicao/tech-stack.md` (`grep -c "^## " ` igual nos dois), nenhuma com o texto
   de modelo ("> Ex.:"); `templates/roblox/comandos-reais.md` cita a ferramenta que roda o
   executor, o `datamodel_type`, onde ler a linha de resumo e o `save_place` antes de cada fase
   (`grep -n -e execute_luau -e datamodel_type -e get_console_output -e save_place`, as quatro
   aparecem).
10. **A lista de riscos (R7):** `grep -c "^## Regra " templates/roblox/regras-de-area.md` → de 5 a
    8; cada bloco tem a linha `areas: codigo` e um link `https://create.roblox.com/` (conferido
    pelo revisor do G5, que abre cada link).
11. **O crédito:** `grep -c "templates/roblox/Executor.luau" .claude/tests/test_credito.py` → `1`, e
    a primeira linha do `Executor.luau` é `-- Golem SDD · …` (o `test_credito.py`, dentro da suíte,
    confere a linha).
12. **O guia (R8):** `docs/guia-roblox.md` cita as permissões de Open Cloud a desligar (MCP ⟩ MCP
    Permissions), o `DataStore` de verdade, o salvar no Roblox antes da primeira fase e o fechar a
    sessão antiga sem salvar depois da volta (`grep -n -e "MCP Permissions" -e DataStore -e "antes
    da primeira fase" -e "sem salvar"`, as quatro aparecem); e o Ctrl+Z só aparece se o R2.7 o
    confirmou.

## Verificações manuais

Antes de começar: o autor do kit diz onde o Studio vai rodar (decisão 4 da entrevista).

1. **O "pronto" (R9), num place de exemplo, sem Rojo:**
   1. No Studio, File ⟩ New ⟩ Baseplate, e salvar no Roblox (File ⟩ Save to Roblox). Ligar o
      Studio MCP seguindo só o `docs/guia-roblox.md`.
   2. Criar uma pasta de projeto fora do kit, com `git init`, e copiar para ela o kit e os modelos
      de `templates/roblox/` como o guia manda: as lições de exemplo em `docs/licoes/`, a lista de
      riscos em `docs/regras-de-area.md`, e rodar `regua.py --gerar`. Abrir o Claude Code nessa
      pasta.
   3. Pedir: "ponha o executor de testes no place". Ver, no Explorer do Studio, o ModuleScript do
      executor no lugar do R6.
   4. Pedir uma fase pequena pela `spec-de-fase`: um ModuleScript `Moedas` em `ServerStorage`, com
      `adicionar(jogador, n)` e `gastar(jogador, n)`, que nunca deixa o saldo negativo, e o teste
      com três casos. Aprovar a spec.
   5. Na `implementar-fase`, **ver o agente chamar o `save_place` antes de editar** e anotar a hora
      no `plan.md`; conferir em Window ⟩ Version History que a versão apareceu.
   6. Ver o agente criar o `Moedas` pelo `multi_edit`. **Ver a lição de exemplo e as regras de
      risco chegarem** nessa edição (a linha "Lendo as lições da área..." e o texto no contexto;
      pedir ao agente que diga qual lição e quais regras recebeu).
   7. Ver o agente rodar o executor pelo `execute_luau` e ler no console
      `3 passed, 0 failed, 0 skipped`.
   8. Pedir ao agente que quebre o `gastar` de propósito (deixe o saldo ficar negativo) e rode de
      novo: o console mostra `failed` maior que 0 e a linha da falha com o teste. Pedir que
      desfaça, e ver `3 passed` de novo.
   9. Na `validar-fase` do projeto de exemplo, ver o "validado" com a linha de resumo citada.
   10. Por último, voltar à versão do passo 5 seguindo só o guia (Window ⟩ Version History ⟩ ⋮ ⟩
       Open Local Copy ⟩ Save to Roblox As). Fechar a sessão antiga do Studio sem salvar,
       reabrir o place pelo Roblox e ver, nele, que o `Moedas` sumiu.

   Esperado: todos os "ver" acontecem. Anotar aqui a saída do console dos passos 7 e 8.
2. **O revisor lê o place:** com o Studio ligado, chamar o revisor sobre o `Moedas`. Ver, na
   resposta, um achado ou um "sem bloqueio" que cita o script pelo caminho
   (`game.ServerStorage.Moedas`), lido pelo `script_read`.
3. **O validador não muda o place:** chamar o validador sobre a mesma fase. Ver a linha de resumo
   citada e a frase de que a mutação foi pulada no place. Conferir, no Studio, que nenhum script
   mudou (o `Moedas` igual ao de antes, sem script novo).
4. **O aviso de risco** ("avisar e deixar"): no projeto de exemplo, pedir uma mudança que bate num
   risco da lista (por exemplo, um `RemoteEvent` que credita moedas com o valor que o cliente
   manda, sem validar). Ver o agente fazer o pedido e pôr, no resumo, uma linha de aviso com as
   três saídas (corrigir, deixar assim, me explica), sem bloquear.

## Casos de borda

- **Nenhum teste no place:** o executor imprime `0 passed, 0 failed, 0 skipped` e "nenhum teste
  encontrado" (G5, no Studio).
- **Um teste com `pular: `** conta como `skipped` (G5, no Studio).
- **Um projeto sem o Studio MCP:** o revisor ainda abre e lê arquivo (G4); o gancho segue com as
  duas entradas de hoje, e a terceira não dispara.
- **Outra ferramenta do Studio MCP** (o `script_read`): o `matcher` não casa (teste 3).
- **Uma pasta `Workspace` num caminho de arquivo:** não acende `codigo` (teste 5).
- **O Studio fechado no meio da fase:** o guia diz o que aparece e o que fazer; conferido no G5.
- **Lição copiada sem regerar o índice:** o guia manda rodar `regua.py --gerar` (R8).

## Requisitos da constituição

- Nenhuma dependência nova: o executor é modelo do kit, sem pacote; nada de Rojo, Wally, TestEZ ou
  Jest (regra 3). Conferir no `git diff --stat` e no `templates/roblox/tech-stack.md`.
- Nenhuma credencial: nada pede chave de API, e o guia manda desligar as permissões de Open Cloud,
  que começam no nível "Balanced" (regra 5).
- A linha de crédito no `Executor.luau` (item 11).
- Cada fato novo no `docs/plano-produto.md` com o link ou o `arquivo:linha` (regra 9), conferido
  pelo revisor no G1.
- As palavras do autor do kit na seção 8, com a data.

## Registro

- `docs/plano-produto.md`: a linha da fase 2 marcada como feita, com a data, a branch e a pasta da
  spec, como a da fase 0 (`:545` na `1f9f827`).
- O `CHANGELOG.md`, se a `validar-fase` o pedir.
- As perguntas em aberto da spec respondidas ou movidas, cada uma com o destino.
- As lições da regra 7, se o G2 refutar uma hipótese desta spec (por exemplo, o `require` em modo
  de edição ou o nome com ponto).

## Não exigido nesta fase

- A migração para o Rojo e tudo o que ela traz (a skill, o `rojo syncback`, o git do código, um
  framework de teste): fase própria.
- O antes e o depois de cada script no git.
- A mutação no place pelo validador.
- O estilo, o gosto × risco na skill de estilo, os combinados e os limites: fase 3.
- O Codex com o Studio MCP: fase 6.
- O `comecar` e o `iniciar-sdd` perguntando "usa Rojo?": fase 4.
- O `run-in-roblox` e a Open Cloud.
- O playtest automatizado pelas ferramentas de input do Studio MCP.
- A resposta do primeiro usuário às três perguntas (R1): o guia sai com a sugestão "uma pasta por
  jogo".
