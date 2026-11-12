# Fase 0: o gancho acha o Python — Requisitos

Branch `fase-0-python`, criada de `f912da6` (a branch do plano). Fatos lidos em `f912da6`.

**A ordem dos merges.** Esta branch nasceu da branch do plano, que ainda não está na `main`
(decisão 3A). O PR do plano entra antes, ou os dois entram juntos. A ordem e o merge são do autor
do kit. Para o guardião, o diff desta fase se lê contra `f912da6`, não contra a `main`.

## Objetivo

O gancho das lições acha o Python que já existe na máquina, mesmo fora do PATH. Antes de
procurar, pergunta ao usuário se ele tem Python e onde. Quando falha, avisa uma vez, diz onde
procurou e cita a lição (`docs/plano-produto.md`, seção 7, linha da fase 0).

## Escopo

- **R1. O arquivo local.**
  - É um `golem.local.toml` opcional, fora do git: o `.gitignore` do kit ganha a linha
    `golem.local.toml`.
  - Ele tem uma linha `python = '<caminho>'`.
  - O `gancho.sh` o procura na raiz e, se não achar, na pasta principal do repositório (o mesmo
    `--git-common-dir` do `.venv`).
  - **A regra de leitura**, em `sh` e com `read -r`: a primeira linha que começa com `python`
    (com espaços opcionais antes do `=`). Antes de tudo, tira-se o `\r` do fim. O valor vai da
    primeira aspa simples até a seguinte, e o resto da linha (um comentário, por exemplo) é
    ignorado. Linha sem as duas aspas não vale.
- **R2. A ordem de procura.** O `gancho.sh` tenta, nesta ordem:
  1. o caminho da linha `python`;
  2. o `.venv` da raiz;
  3. o `.venv` da pasta principal;
  4. o PATH (`python3`, `python`, `py -3`);
  5. os lugares do instalador oficial do Windows: `$LOCALAPPDATA/Programs/Python/Python3*/python.exe`,
     `$LOCALAPPDATA/Programs/Python/Launcher/py.exe` (com `-3`) e `$PROGRAMFILES/Python3*/python.exe`.

  Cada candidato só vale se existir e rodar um Python 3.8+ (o `roda_py38` de hoje). Um candidato
  que não roda, ou um glob que não casa, passa ao seguinte em silêncio.
- **R3. O aviso de falha.** Quando nenhum candidato roda:
  - **Os ids.** Os ids vêm do stdin: o `session_id` e o `agent_id`. Sem `agent_id`, o agente é
    `principal`, como no `pasta_de_marca`. Um id só vale se casar com `[A-Za-z0-9_-]`, até 128
    caracteres; fora disso, o id é tratado como ausente. Sem `session_id` válido, o aviso sai em
    toda ação, como hoje.
  - **Duas marcas por sessão** (a leitura do agente para a decisão 2A, aprovada com a spec):
    - o aviso ao **usuário** (o `systemMessage`) sai uma vez por sessão, e **só pela conversa
      principal**. A primeira ação com gancho pode ser de um subagente, e não se sabe se o
      `systemMessage` de um subagente chega ao usuário;
    - o aviso ao **agente** (o `additionalContext`) sai uma vez por agente, porque um subagente
      começa com o contexto zerado.

    Quando as marcas que cabem ao agente da ação já existem, o gancho sai calado (exit 0, sem
    saída).
  - **O texto**, fixo, sem caminho:
    - onde procurou;
    - a lição `sem-python-no-path-nao-e-maquina-sem-python`, pelo id;
    - "peça o diagnóstico do Golem";
    - se a linha `python` existe e não roda, uma frase dizendo isso.
  - **O registro.** O `gancho-falhas.log` recebe uma linha por falha, inclusive nas ações em que o
    aviso não sai.
  - As outras falhas (o `licoes_relevantes.py` ausente ou saindo com erro) continuam como hoje.
- **R4. A skill `diagnostico`, versão mínima.**
  - Ela faz a pergunta do Python com botões, em texto numerado onde não houver botões.
  - Ela grava sempre o `golem.local.toml` na **pasta principal** do repositório, para que os
    worktrees o achem (o R1). Se o arquivo já tem uma linha `python`, ela mostra a atual e a
    substitui.
  - Ela age conforme a resposta:

  | Resposta | O que a skill faz |
  |---|---|
  | Sim, e sei onde | recebe o caminho; se tiver aspa simples, recusa e pede outro; testa se roda um Python 3.8+; se rodar, grava a linha `python`; se não rodar, diz isso e oferece a busca |
  | Sim, mas não sei onde | procura nos passos 4 e 5 do R2; mostra o que achou e grava depois do ok; se não achar nada, dá o comando de instalação |
  | Não sei | o mesmo que a anterior |
  | Não | faz a mesma busca; se achar, pergunta "Achei um em `...`. Quer usar este?"; se não achar, dá o comando de instalação |

  - Ao fim, ela roda o gancho com uma entrada de teste **sem `session_id`**
    (`{"tool_input":{"command":"pytest -q"}}`, como no `README.md:139`) e mostra se a lição chegou.
    Sem `session_id`, a deduplicação das lições não esconde a lição numa segunda rodada.
  - Ela não faz o resto do diagnóstico, que fica para a fase 4.
- **R5. Os testes.** A suíte do ferramental ganha os testes listados no `plan.md` (G1 e G2).
  - O `_path_sem_python` (`test_gancho.py:382`) passa a isolar também o `LOCALAPPDATA` e o
    `PROGRAMFILES`, em pastas vazias, e o `TMPDIR`, num `tmp_path`.
  - Sem isso, os testes que contam com ele (`test_lancador_usa_py_menos_3` e o do worktree)
    passariam com defeito: o passo 5 acharia o Python real da máquina. E os que chegam ao caminho
    do aviso quebrariam na segunda rodada, porque as marcas ficariam na pasta temporária real.
- **R6. A varredura.**
  - O `README.md`:
    - os Requisitos (linhas 74-76, "o gancho procura o `.venv` primeiro") passam a dar a ordem
      nova;
    - o passo 2 da instalação cita a linha `golem.local.toml` do `.gitignore`.
  - A lista de skills esperadas da `iniciar-sdd` (`.claude/skills/iniciar-sdd/SKILL.md:85`) e a
    tabela "Em volta de tudo" do `WORKFLOW.md` (linha 159) citam a `diagnostico`.
  - A lista `SKILLS` do `test_credito.py` inclui a `diagnostico`, e a skill traz a linha de
    crédito.
  - Os `refs` da lição `sem-python-no-path-nao-e-maquina-sem-python` passam a citar as funções
    (`achar_venv`, `achar_no_path`, o aviso "nenhum Python") em vez de números de linha, que esta
    fase muda. Depois, o índice é regerado.

## Fora de escopo

- **O modo sem Python** (`gancho = "desligado"` e a busca de lições em momentos fixos): fase 1,
  com a configuração (`docs/plano-produto.md`, seção 8, decisão 5, leitura do agente).
- **O `golem.toml` e as receitas:** fase 1.
- **Os lugares de costume do macOS e do Linux:** fora (decisão 1A). Lá, o `python3` costuma estar
  no PATH, e o passo 4 já o acha.
- **Conferir se o arquivo da lição existe antes de citá-lo:** fora (decisão 5A).
- **Avisar quando a linha `python` não roda mas outro Python é achado:** fora. O gancho segue com o
  Python achado, em silêncio, e o diagnóstico mostra a linha quebrada. Um aviso que não interrompe
  seria peça nova sem caso visto (regra 10).
- **Limpar as marcas velhas do aviso:** fora. São arquivos vazios, um por sessão com falha mais um por
  agente, na pasta temporária do sistema.
- **Um limite conhecido, sem conserto nesta fase:** o `read` embutido lê o stdin byte a byte. Uma
  entrada de 2 MB levou 4,6 s no `sh` do Git Bash (medido pelo revisor em 2026-11-12), e o gancho
  tem `timeout: 10` no `settings.json`. Um `Write` de vários MB, no caminho da falha, pode estourar
  o tempo. É raro, e o caminho da falha só existe sem Python.
- **O diagnóstico completo, o plugin e o `comecar`:** fase 4.

## Decisões

- **A spec aprovada, com um commit por grupo.** As palavras dele: "Aprovo", à pergunta "Aprova a
  spec da fase 0, com um commit por grupo?" (2026-11-12). Com ela, ficam aprovadas as duas
  leituras do agente levadas junto: as duas marcas do R3 e a linha `python` no arquivo local.
- **Uma fase 0 com todo o fluxo do Python.** As palavras dele: "Opção A, a fase 0 com todo o fluxo
  do Python" (2026-11-12). Descartadas: a fase 0 só com a busca (buscaria sem perguntar) e tudo
  dentro da fase 1 (a fase ficaria grande).
- **Perguntar antes de procurar.** As palavras dele: "Antes de fazer a busca, é importante
  perguntar para o usuário se ele tem ou não. […] E também tem que dar a possibilidade dele de
  falar onde, se ele souber." (2026-11-12). Os ajustes que ele aceitou ("sim, pode atualizar o
  plano"): a pergunta na configuração, porque o gancho não pode perguntar; o botão "Não sei"; com
  "Não", uma busca rápida antes de mandar instalar; a linha `python` entre aspas simples; a ordem
  de procura.
- **A linha `python` num arquivo local, fora do git.** Mudança do agente depois do ok, aprovada com esta
  spec (`docs/plano-produto.md`, seção 8, decisão 4). O caminho é desta máquina, está
  errado em qualquer outra e expõe o nome do usuário. Descartado: a linha no `golem.toml`
  versionado.
- **As respostas da entrevista desta spec** (2026-11-12), com as palavras dele: "1A 2A 3A 4A 5A".
  - 1A: os lugares de costume só do Windows. Descartado: macOS e Linux também.
  - 2A: o aviso uma vez para o usuário e para o agente. Descartado: uma linha curta ao agente em
    toda ação. Como o agente leu isso, com duas marcas, está no R3, aprovado com a spec.
  - 3A: a branch a partir da branch do plano, que tem a lição e o plano. Descartado: a partir da
    `origin/main`, que está em `c880a17`, sem eles.
  - 4A: seguir sem a resposta do primeiro usuário sobre o Python. O desenho cobre as quatro
    respostas.
  - 5A: o aviso cita o id da lição sem conferir se o arquivo existe.
- **A marca do aviso é um arquivo vazio criado de forma atômica em `sh`** (`set -C` e o
  redirecionamento `>`), na pasta temporária do sistema (`$TMPDIR`, ou `$TEMP`, ou `/tmp`, nessa
  ordem). Isso usa só recursos embutidos do `sh`. Descartada a pasta por sessão do
  `pasta_de_marca`, porque o `mkdir` seria um utilitário novo no lançador. O Claude Code roda
  ferramentas em paralelo, e o par "conferir, depois criar" avisaria duas vezes.
- **O stdin é lido em `sh` só no caminho da falha**, com `read` embutido. Ali o Python não vai
  rodar, então ler o stdin não tira nada dele. Os ids saem por expansão de parâmetro, e espaços
  depois dos dois-pontos são tolerados.

## Contexto

- **O lançador de hoje** (`.claude/hooks/gancho.sh` em `f912da6`):
  - o `avisar` está nas linhas 42-50. O comentário da linha 43 pede texto fixo, sem aspas nem barra
    invertida, porque o texto vai dentro de uma string JSON. Ele sai com 0, sem lição (linha 49);
  - o `roda_py38` está nas linhas 56-58;
  - o `achar_venv` está nas linhas 60-68, e o `achar_no_path` nas linhas 74-87;
  - a ordem de hoje está nas linhas 89-99: o `.venv` da raiz, o da pasta principal pelo
    `--git-common-dir` e o PATH;
  - o aviso "nenhum Python" está na linha 100. O stdin passa direto ao Python (linhas 102-105), e
    o lançador não lê o `session_id`;
  - os utilitários externos que ele usa são o `dirname`, o `date`, o `git` e o `printf`.
- **O `pasta_de_marca`** (`.claude/hooks/licoes_relevantes.py`) já define o que a fase reusa:
  - o agente ausente vira `principal`;
  - os ids valem só se casarem com `[\w-]{1,128}`;
  - o teste do id hostil está em `.claude/tests/test_gancho.py:205`.
- **A máquina em que o defeito apareceu:**
  - o Python 3.12.4 está em `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`, e o lançador
    em `...\Launcher\py.exe`, os dois fora do PATH;
  - no PATH, só os atalhos da Microsoft Store, que saem com 49 no Git Bash;
  - no Git Bash, a variável é `$PROGRAMFILES`, e `$ProgramFiles` sai vazio;
  - o `read -r` traz o caminho com as barras, e sem o `-r` elas somem;
  - um glob que não casa devolve o padrão literal.

  Tudo isso foi conferido em 2026-11-12 (lição `sem-python-no-path-nao-e-maquina-sem-python`;
  `docs/plano-produto.md`, seção 3).
- **No TOML**, a string entre aspas simples é literal: o `tomllib` lê o caminho do Windows inteiro.
  Com aspas duplas, o `\U` o torna inválido. Uma aspa simples dentro da string também o torna
  inválido. Conferido em 2026-11-12.
- **A suíte do ferramental** dá hoje 76 passed, 0 skipped (`python -m pytest .claude/tests -o
  addopts= -q -p no:cacheprovider -rs`, em `ae037b4`, que tem o mesmo `.claude/` de `f912da6`).
  O `AMBIENTE` dos testes (`.claude/tests/conftest.py:32`) herda o ambiente real, inclusive o
  `LOCALAPPDATA`.

## Padrões a seguir

- **Os testes do lançador** seguem `.claude/tests/test_gancho.py:314-454`:
  - o `_sh`, o `_repassador` (um `sh` que repassa ao Python da suíte), o `_path_sem_python` (o
    PATH com Pythons quebrados na frente) e o `_rodar_lancador`;
  - o `py` que só repassa se receber `-3` (`test_lancador_usa_py_menos_3`);
  - o teste do worktree, que acha o `.venv` da pasta principal.
- **Os ids e o agente `principal`** seguem o `pasta_de_marca` de `.claude/hooks/licoes_relevantes.py`.
- **O aviso** segue o formato do `avisar` de hoje: o `systemMessage` para o usuário e o
  `additionalContext` para o agente.
- **A skill** segue o formato das skills de `.claude/skills/`: o frontmatter com `name`,
  `description` e `license`; os blocos "Lê", "Escreve" e "Decide".

## Notas do usuário

- "Antes de fazer a busca, é importante perguntar para o usuário se ele tem ou não. Senão a gente
  vai buscar à toa, né? E também tem que dar a possibilidade dele de falar onde, se ele souber."
  (2026-11-12)
- "Que essa máquina tem Python. Você não encontrou, mas ele existe. Tanto que está sendo utilizado
  pelas várias envs que tem e várias conversas." (2026-11-12)

## Teto de gasto

Nenhum: a fase não gasta dinheiro.

## Perguntas em aberto

- **O id do `winget` para o Python 3** (por exemplo, `Python.Python.3.12`): a conferir no G3, com
  a saída de `winget search`, antes de a skill citá-lo.
- **Se a entrada de gancho do Codex traz `session_id`:** a conferir. Sem ele, o aviso sai em toda
  ação, como hoje (R3).
- **Se o `systemMessage` do gancho de um subagente aparece ao usuário:** a conferir no G2. O
  desenho não depende da resposta: só a conversa principal põe o `systemMessage`.
- **Se o `sh` do Git Bash executa o `_repassador` com o nome `python.exe`** num lugar de costume
  falso: a conferir no G1. Se não executar, o teste do passo 5 usa outra forma de Python falso, e
  isso entra na tabela de alterações do `plan.md`.
