# Fase 2: Roblox mínimo, sem Rojo — Validação

O contrato de merge. Cada item se marca com a saída real, no head que vai ao PR. A máquina da fase
não tem Python no PATH; os comandos usam dois caminhos, ditos aqui pelo papel, e não pelo caminho,
que traz o nome do usuário:

- `PYT` = o `python.exe` do venv de testes do ferramental (com o pytest), fora do repositório;
- `PY` = o Python 3.12 do instalador oficial, em `%LOCALAPPDATA%\Programs\Python\Python312\`.

## Verificações automatizadas

1. **A suíte do ferramental:**
   `$PYT -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs`
   → `134 passed`, 0 falhas, 0 puladas: o total da `main` depois do merge da fase 1 (lido no G1,
   em `7671fc1`: `123 passed in 60.16s`), mais os 8 testes novos desta fase (5 do G3, 2 do G5 e 1
   do G6), mais os 3 do `test_conciliar.py`, que entraram com o PR 9 (`d637f52`, trazido no merge
   `52a9478`). Lido em 2026-11-21: `133 passed in 63.17s` antes do teste do G6 e
   `134 passed in 62.45s` com ele.
   Pulado é falha até prova em contrário (regra 8).
2. **Os testes novos, um por um**, com `-k`, cada um `1 passed`:
   `test_multi_edit_num_script_do_place_acende_codigo`,
   `test_execute_luau_chega_aos_gatilhos`,
   `test_matcher_do_studio_casa_so_com_edicao_e_execucao`,
   `test_settings_tem_a_entrada_do_studio_com_o_mesmo_comando`,
   `test_pasta_workspace_num_arquivo_nao_acende_codigo`,
   `test_licoes_de_exemplo_do_roblox_chegam_pelo_studio_mcp`,
   `test_riscos_do_roblox_chegam_num_multi_edit`,
   `test_execute_luau_que_cria_script_acende_codigo` (G6).
3. **Os testes pegam o defeito** (o validador, numa cópia descartável): tirar a leitura do
   `tool_input.code` do `licoes_relevantes.py` faz o teste 2 falhar; tirar a entrada nova do
   `settings.json` faz o teste 4 falhar; tirar `game.ServerScriptService` do `POR_CAMINHO` faz o
   teste 1 falhar; trocar `game.Workspace` por `Workspace` no `POR_CAMINHO` faz o teste 5 falhar;
   tirar a entrada do `Instance.new` do `POR_COMANDO` faz o teste do G6 falhar, e também tirar as
   maiúsculas exatas (`(?-i:...)`) ou o `(?!=)` dela (ver o resultado abaixo).
   O `file_path` do `multi_edit` o gancho já lia antes da fase (G2, resposta 2).
4. **A régua:** `$PY .claude/regua.py --conferir` → sai com código 0, sem divergência. As lições de
   exemplo em `templates/roblox/licoes/` não entram no índice do kit
   (`grep -c "templates/roblox/licoes" .claude/indice/licoes.yaml` → `0`; o G6 trocou o
   `templates/roblox` por `templates/roblox/licoes`, porque uma lição real da regra 7 cita no
   `gatilho:` o modelo `templates/roblox/regras-de-area.md`).
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
   de modelo ("> Ex.:"); `templates/roblox/comandos-reais.md` cita o modo de jogo (o
   `start_stop_play`), a ferramenta que roda o executor, o `datamodel_type`, onde ler a linha de
   resumo e o `save_place` antes de cada fase (`grep -n -e start_stop_play -e execute_luau -e
   datamodel_type -e get_console_output -e save_place`, as cinco aparecem).
10. **A lista de riscos (R7):** `grep -c "^## Regra " templates/roblox/regras-de-area.md` → de 5 a
    8; cada bloco tem a linha `areas: codigo` e um link `https://create.roblox.com/` (conferido
    pelo revisor do G5, que abre cada link).
11. **O crédito:** `grep -c "templates/roblox/Executor.luau" .claude/tests/test_credito.py` → `1`, e
    a primeira linha do `Executor.luau` é `-- Golem SDD · …` (o `test_credito.py`, dentro da suíte,
    confere a linha).
12. **O guia (R8):** `docs/guia-roblox.md` cita as permissões de Open Cloud a desligar (Configurações do
    Assistente ⟩ Permissões MCP), o acesso do Studio ao `DataStore`, desligado por padrão, o salvar
    no Roblox antes da primeira fase e o fechar a janela antiga sem salvar antes de salvar a cópia,
    na volta (`grep -n -e "Permissões MCP" -e "API Services" -e "antes da primeira fase" -e
    "sem salvar"`, as quatro aparecem); e diz que o Ctrl+Z não desfaz o
    que o agente escreve e que os testes rodam os scripts do jogo (`grep -n -e "Ctrl+Z" -e
    "scripts do jogo"`, os dois aparecem; G2, respostas 3 e 7); e oferece a configuração do
    Studio pelo controle da tela (`grep -n "controle da tela"` → aparece, e a frase cita o link
    da documentação que diz onde ele existe).

### Resultado das verificações automatizadas (2026-11-21, G6)

Rodadas pelo validador do G6 sobre o stage, com o HEAD em `52a9478` e o G6 sem commit, e
refeitas pela conversa depois dos últimos ajustes:

| Item | Resultado |
|---|---|
| 1 | Validador: `134 passed in 62.44s`. Conversa, no fim: ver a linha abaixo da tabela |
| 2 | Os 8 testes, um por um com `-k`: cada um `1 passed, 133 deselected` |
| 3 | Mutações, cada uma numa cópia: tirar o `Instance.new` → `1 failed, 73 passed`; tirar o `or entrada.get("code")` → `3 failed`; tirar `game.ServerScriptService` → `2 failed`; `Workspace` sem `game.` → `1 failed`; o `matcher` trocado → `2 failed`. Pela conversa, o `test_gancho.py` (74 testes) numa árvore inteira com git (`mutacoes-g6.txt` em `fase-2-g6-pronto/`): tirar o `(?!=)` → `1 failed, 73 passed`; tirar a entrada do Studio do `settings.json` → `2 failed, 72 passed` (os testes 3 e 4); tirar as maiúsculas exatas → `1 failed, 73 passed`; a cópia sem mutação → `74 passed` |
| 4 | `regua.py --conferir` → `ok`; `grep -c "templates/roblox/licoes"` → `0` |
| 5 | `.codex/hooks.json` gerado só com `"Bash"` e `"apply_patch"` |
| 6 | `aplicar` → "nada mudou", nenhuma linha `tools:` mudou |
| 7 | Só caminhos da lista |
| 9 | As cinco palavras no `comandos-reais.md` |
| 10 | 7 regras, 7 `areas: codigo`, 9 links, 7 "corrigir, deixar assim, me explica" |
| 11 | Crédito: `1`, e a primeira linha do `Executor.luau` |
| 12 | Os greps casam no guia |

A suíte rodada pela conversa no head final do G6: `134 passed in 55.75s`, sem falhas nem pulados;
a régua `ok`, e o índice com total 15.

## Verificações manuais

Antes de começar: o Studio roda nesta máquina (respondido no G2, 2026-11-21), com o place de
teste salvo no Roblox.

1. **O "pronto" (R9), num place de exemplo, sem Rojo:**
   1. No Studio, File ⟩ New ⟩ Baseplate, e salvar no Roblox (File ⟩ Save to Roblox). Ligar o
      Studio MCP seguindo só o `docs/guia-roblox.md`.
   2. Criar uma pasta de projeto fora do kit, com `git init`, e copiar para ela o kit e os modelos
      de `templates/roblox/` como o guia manda: as lições de exemplo em `docs/licoes/`, a lista de
      riscos em `docs/regras-de-area.md`, o `git add` deles e o `regua.py --gerar`. Abrir o Claude
      Code nessa pasta. Este passo muda quando o kit virar plugin (fase de instalação).
   3. Pedir: "ponha o executor de testes no place". Ver, no Explorer do Studio, o ModuleScript do
      executor no lugar do R6.
   4. Pedir uma fase pequena pela `spec-de-fase`: um ModuleScript `Moedas` em `ServerStorage`, com
      `adicionar(jogador, n)` e `gastar(jogador, n)`, que nunca deixa o saldo negativo, e o teste
      com três casos. Aprovar a spec.
   5. Na `implementar-fase`, **ver o agente chamar o `save_place` antes de editar** e anotar a hora
      no `plan.md`; conferir em Janela ⟩ Histórico da versão (Window ⟩ Version History,
      em inglês) que a versão apareceu.
   6. Ver o agente criar o `Moedas` pelo `multi_edit`. **Ver a lição de exemplo e as regras de
      risco chegarem** nessa edição (a linha "Lendo as lições da área..." e o texto no contexto;
      pedir ao agente que diga qual lição e quais regras recebeu).
   7. Ver o agente rodar o executor em modo de jogo (liga o jogo pelo `start_stop_play`, roda o
      executor pelo `execute_luau` no `Server`, desliga) e ler no console
      `3 passed, 0 failed, 0 skipped`.
   8. Pedir ao agente que quebre o `gastar` de propósito (deixe o saldo ficar negativo) e rode de
      novo: o console mostra `failed` maior que 0 e a linha da falha com o teste. Pedir que
      desfaça, e ver `3 passed` de novo.
   9. Na `validar-fase` do projeto de exemplo, ver o "validado" com a linha de resumo citada.
   10. Por último, voltar à versão do passo 5 seguindo só o guia (Janela ⟩ Histórico da versão ⟩ ⋮
       ⟩ Abrir cópia local; fechar a sessão antiga do Studio sem salvar; na cópia, Arquivo ⟩ Salvar
       na Roblox como), reabrir o place pelo Roblox e ver, nele, que o `Moedas` sumiu.

   Esperado: todos os "ver" acontecem. Anotar aqui a saída do console dos passos 7 e 8.
2. **O revisor lê o place:** com o Studio ligado, chamar o revisor sobre o `Moedas`. Ver, na
   resposta, um achado ou um "sem bloqueio" que cita o script pelo caminho
   (`game.ServerStorage.Moedas`), lido pelo `script_read`.
3. **O validador não muda o place** (a regra do R4 depois da decisão "Liberar sem DataStore"):
   chamar o validador sobre a mesma fase. Ver a busca por `DataStore` citada antes de ligar o jogo,
   a linha de resumo citada e, num place sem `DataStore`, a mutação em memória pega e restaurada;
   num place com `DataStore`, a frase de que a mutação foi pulada. Conferir, no Studio, que nenhum
   script mudou (o `Moedas` com o mesmo hash, sem script novo).
4. **O aviso de risco** ("avisar e deixar"): no projeto de exemplo, pedir uma mudança que bate num
   risco da lista (por exemplo, um `RemoteEvent` que credita moedas com o valor que o cliente
   manda, sem validar). Ver o agente fazer o pedido e pôr, no resumo, uma linha de aviso com as
   três saídas (corrigir, deixar assim, me explica), sem bloquear.

### Resultado das verificações manuais (2026-11-21, G6)

Rodadas no place novo "Golem pronto" (`placeId 114624124893726`) e numa pasta de projeto
descartável fora do kit, cada pedido por `claude -p` no terminal (Claude Code 2.1.323), com as
permissões de Open Cloud em Negar, salvas antes do passo 3. A transcrição de cada passo
(`passoN.jsonl`, `confN.jsonl`) e os prints estão em `fase-2-g6-pronto/`, nas notas da conversa da
fase 2, fora do repositório.

- [x] **1.1 e 1.2:** o place salvo no Roblox; a pasta com o kit e `templates/roblox/`, as lições e
  as regras copiadas, o `git add` e o `--gerar` (índice do projeto: total 12, lido na saída do
  `--gerar` na sessão, sem arquivo guardado; o Negar salvo e o `Connected` também foram vistos na
  sessão, sem arquivo: o Negar na tela de permissões reaberta, com "Personalizado" e o Salvar
  apagado; o `Connected` na saída do comando); o servidor
  registrado pelo PowerShell, `claude mcp get Roblox_Studio` → `Status: √ Connected`. Achado: o
  guia não mandava copiar a `templates/roblox/`, que o README chama de opcional e de onde o agente
  tira o `Executor.luau`; o guia passou a mandar.
- [x] **1.3:** `ServerStorage.GolemTestes.Executor` criado (117 linhas, igual ao modelo), visto no
  Explorer.
- [x] **1.4:** a spec `specs/2026-11-21-moedas/` no formato curto, aprovada, com o "ponto de volta"
  e a contagem `3 passed, 0 failed, 0 skipped`.
- [x] **1.5:** o `save_place` antes da primeira edição devolveu `"version":4`, `"status":"Saved"`,
  às 19:15 (-03:00), anotado pelo agente na spec da fase. No Histórico da versão, a v4 apareceu às
  19:15, com o rótulo "Salvamento automático" (`passo5-historico-v4-v5.jpg`); o guia passou a
  avisar disso.
- [x] **1.6:** o `Moedas` e o `Moedas_spec` criados pelo `multi_edit` (`passo6-explorer-moedas.jpg`).
  No `multi_edit` do `Moedas`, o agente relatou ter recebido "Regras de área para codigo" com as
  regras 1 a 7 e "Lições registradas para codigo" com `o-ctrl-z-nao-desfaz-o-texto-que-o-agente-escreveu`;
  no do `Moedas_spec`, nada (cada lição e regra chega uma vez por sessão).
- [x] **1.7:** `start_stop_play`, `execute_luau` no `Server`, `get_console_output`:
  `3 passed, 0 failed, 0 skipped`.
- [x] **1.8:** com a checagem de saldo tirada do `gastar`, o console mostrou
  `FALHOU ServerStorage.Moedas_spec > gastar sem saldo não deixa negativo: ServerStorage.Moedas_spec:27: gastar 5 de 2 deveria devolver false`
  e `2 passed, 1 failed, 0 skipped`; desfeito pelo `multi_edit`, `3 passed, 0 failed, 0 skipped`, e o
  `Source` com o mesmo tamanho e hash de antes (847 bytes, `481808074`). É o caminho da falha com o
  executor final, que o guardião pediu.
- [x] **1.9:** a `validar-fase` deu "validado", citando `3 passed, 0 failed, 0 skipped`. Achado do
  projeto de teste, e não do kit: a spec que o agente escreveu pedia "os três testes nomeados na
  saída", e o executor só nomeia quem falha (nenhum modelo do kit diz o contrário).
- [x] **1.10:** a volta à v4 deu certo, mas **na ordem que o guia dizia o Studio recusa**: com a
  sessão antiga aberta, o "Salvar na Roblox como" avisou da sessão de Criação em equipe e deu
  "Falha no salvamento". Fechada a sessão antiga, "Salvo com sucesso!". Reaberto pelo Roblox, o
  place tem só o `ServerStorage.GolemTestes.Executor` (`passo10-depois.txt`): o `Moedas`, o
  `Moedas_spec` e o que a conferência 4 criou sumiram. O guia e o passo 10 foram corrigidos, e a
  lição `o-studio-recusa-salvar-a-copia-com-a-sessao-antiga-aberta` registrada.
- [x] **2:** o revisor (do projeto de teste, no passo 5) leu `game.ServerStorage.Moedas` e
  `game.ServerStorage.Moedas_spec` pelo `script_read` e deu "sem bloqueio", citando os scripts pelo
  caminho.
- [x] **3**, pela rodada 3, a única com a regra de hoje (as rodadas 1 e 2 contam o caminho até ela).
  O ramo "com `DataStore`" não foi conferido: o place de teste não usa `DataStore`.
  - **Rodada 1 (`conf3.jsonl`):** o validador deu "valida" e citou `3 passed, 0 failed, 0 skipped`,
    e o place não mudou (o `Moedas` com o mesmo hash e nenhum `Script` ou `LocalScript`,
    `total BaseScript=0`: `conf3-hash.txt`). Mas **ele não pulou a mutação**: com o jogo ligado,
    trocou em memória as funções do `Moedas` e rodou o executor numa rodada de controle e em três
    mutações, todas pegas. Decisão do autor do kit, nesta conversa, em 2026-11-21: proibir também
    esse caminho ("Ok, vamos seguir sua proposta."). O `validador.md` e o R4 passaram a dizer "nem
    em memória, com o jogo ligado", e a lição
    `proibir-pelo-efeito-deixa-a-brecha-do-que-nao-tem-o-efeito` foi registrada.
  - **Rodada 2 (`conf3b.jsonl`):** numa sessão nova, com o `validador.md` novo copiado para o
    projeto de teste (antes da troca de "ela" por "a mutação" na frase seguinte, só redação) e o
    `Moedas` e o `Moedas_spec` recriados com o mesmo código
    (`recriar.jsonl`: 847 bytes, hash `481808074`), o validador deu "valida", citou
    `3 passed, 0 failed, 0 skipped` e disse: "Pulada, porque o código vive no place: não existe
    cópia descartável". Depois dele, o place tinha os mesmos três scripts (`Executor`, `Moedas`,
    `Moedas_spec`) e o `Moedas` com o mesmo hash (`conf3b-hash.txt`).
  - **Rodada 3 (`conf3c.jsonl`, regra nova).** O usuário decidiu "Liberar sem DataStore" (R4). Numa
    sessão nova, com o `validador.md` dessa decisão copiado para o projeto de teste, o validador
    fez o seguinte:
    - procurou `DataStore` pelo `script_grep` e não achou nada;
    - citou `3 passed, 0 failed, 0 skipped`;
    - fez duas mutações em memória, cada uma num jogo novo, e restaurou depois de cada uma. O
      `gastar` sem a checagem de saldo deu `2 passed, 1 failed, 0 skipped`, e o `adicionar` que
      sobrescreve deu `2 passed, 1 failed, 0 skipped`. As duas foram pegas.

    O place ficou igual: antes e depois, os mesmos 8 `LuaSourceContainer`, e o `Moedas` com 847
    bytes e hash `481808074` (`conf3c-hash-antes.txt`, `conf3c-hash-depois.txt`).

    O veredito dele foi "não valida", por um achado do projeto de teste, e não do kit. Os cinco
    `CreditarMoedas*` que as rodadas da conferência 4 deixaram no place repassam ao `Moedas` o
    valor do cliente, contra o "fora de escopo" da spec do projeto. Ele acertou ao acusá-los.
- [x] **4**, nas rodadas E e F, depois de dois consertos. Pedido o `RemoteEvent` que credita o
  valor do cliente sem validar (uma sessão nova por rodada, com nomes diferentes para as peças):
  - **A e B, antes dos consertos** (`conf4.jsonl`, `conf4b.jsonl`): o agente fez o pedido e
    avisou do risco, sem bloquear, mas com saídas inventadas, sem o "me explica". A A criou o
    Script pelo `multi_edit` (o gancho disparou: a resposta cita a lição do Ctrl+Z); a B criou tudo
    num `execute_luau` só, sem `multi_edit`.
  - **Conserto 1:** cada regra do `templates/roblox/regras-de-area.md` passou a nomear as três
    saídas, porque a introdução do arquivo não chega com a regra (lição
    `a-regra-de-area-chega-sem-a-introducao-do-arquivo`).
  - **C e D, depois do conserto 1 e antes do 2** (`conf4c.jsonl`, `conf4d.jsonl`): a C criou o
    Script num `execute_luau` só, sem aviso com as saídas, e a sessão disse que nenhum texto de
    gancho lhe chegou (`conf4c-gancho.txt`); a D leu o `docs/regras-de-area.md` por conta própria
    e trouxe as três saídas.
  - **Conserto 2:** o gancho passou a dar `codigo` ao Luau com `Instance.new` ou `.Source =`
    (teste novo no item 2; lição `o-agente-cria-script-pelo-execute-luau-sem-caminho`).
  - **E e F, depois dos dois** (`conf4e.jsonl`, `conf4f.jsonl`; o que cada sessão disse do
    gancho, perguntado pelo `--resume`, está em `conf4ef-saida-e-gancho.txt`): as duas sessões
    disseram ter
    recebido "Regras de área para codigo", com as regras 1 a 7, já no `execute_luau` que criou o
    `RemoteEvent` (com `Instance.new`); o Script elas criaram pelo `multi_edit`. As duas fizeram o
    pedido, avisaram citando a regra 1, sem bloquear, e ofereceram "Corrigir", "Deixar assim" e
    "Me explica". O Script criado pelo `execute_luau` com `.Source =`, como na B e na C, só foi
    provado pelo teste unitário, e não de ponta a ponta.
  - O `-p` lê o `CLAUDE.md` global do autor do kit (o formato das respostas, com marcadores, vem
    dele).
- Não conferido: a conversa nova pelo app desktop. Todos os pedidos foram pelo terminal.

## Casos de borda

- **Nenhum teste no place:** o executor imprime `0 passed, 0 failed, 0 skipped` e "nenhum teste
  encontrado" (G5, no Studio).
- **Um teste com `pular: `** conta como `skipped` (G5, no Studio).
- **Um projeto sem o Studio MCP:** o revisor ainda abre e lê arquivo (G4); o gancho segue com as
  duas entradas de hoje, e a terceira não dispara.
- **Outra ferramenta do Studio MCP** (o `script_read`): o `matcher` não casa (teste 3).
- **Uma pasta `Workspace` num caminho de arquivo:** não acende `codigo` (teste 5).
- **O Studio fechado no meio da fase:** o guia diz o que aparece e o que fazer; conferido no G5.
- **Lição copiada sem regerar o índice:** o guia manda o `git add` e o `regua.py --gerar` (R8).
- **Um `_spec` vazio** (o texto padrão de um ModuleScript novo): o executor imprime "nenhum teste
  encontrado" (G5, no Studio).

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
  spec, como a da fase 0 (`:562` na `7671fc1`).
- O `CHANGELOG.md`, se a `validar-fase` o pedir.
- As perguntas em aberto da spec respondidas ou movidas, cada uma com o destino.
- As lições da regra 7, se o G2 refutar uma hipótese desta spec (por exemplo, o `require` em modo
  de edição ou o nome com ponto).

## Não exigido nesta fase

- A migração para o Rojo e tudo o que ela traz (a skill, o `rojo syncback`, o git do código, um
  framework de teste): fase própria.
- O antes e o depois de cada script no git.
- A mutação que muda o place (o `Source` ou um script novo) pelo validador.
- O estilo, o gosto × risco na skill de estilo, os combinados e os limites: fase 3.
- O Codex com o Studio MCP: fase 6.
- O `comecar` e o `iniciar-sdd` perguntando "usa Rojo?": fase 4.
- O `run-in-roblox` e a Open Cloud.
- O playtest automatizado pelas ferramentas de input do Studio MCP.
- A resposta do primeiro usuário às três perguntas (R1): o guia sai com a sugestão "uma pasta por
  jogo".
