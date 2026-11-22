# Fase 4: lições e índices — Requisitos

Branch `fase-4-licoes-e-indices`, cortada de `746ebf7` (a `main` em 2026-11-22, com o PR 12 da
fase 3, conferida com `git fetch` e `git log -1 origin/main`). Os fatos do kit foram lidos em
`746ebf7`, salvo onde se diz outro commit.

## Objetivo

Uma lição que existe no projeto sempre chega a quem age, e as citações que sustentam as lições e as
regras não envelhecem sem aviso. São cinco itens da proposta da conversa de método (MET) sobre os
aprendizados de outro projeto que usa o método (`docs/plano-produto.md:615`):
- **A1:** o gancho percebe a lição que falta no índice e avisa uma vez por sessão;
- **D2:** a régua confere as `refs:` das lições;
- **D3:** a régua mede o tamanho do `AGENTS.md` e avisa;
- **C:** a `licao` manda a regra de área ao `docs/regras-de-area.md`;
- **D1:** o princípio do índice, registrado como decisão.

**O "pronto" do roteiro** está "a definir na spec da fase" (`docs/plano-produto.md:615`). Esta spec
o define assim:
- **A1:** num projeto com o índice em dia menos uma lição nova, a primeira ação que casa com o
  gatilho dela recebe a lição e o aviso "índice defasado", e a segunda ação da sessão não recebe o
  aviso de novo;
- **D2:** uma ref deslocada de propósito sai na régua com a linha nova;
- **D3:** um `AGENTS.md` acima do teto sai na régua com o aviso;
- **C e D1:** o texto novo está na `licao`, no `README` das lições, na regra 7 e na seção 8.

**Por quê.**
- **Hoje, a lição fora do índice não chega, e nada avisa.** Com o índice legível, o gancho só lê o
  índice (`licoes_relevantes.py:294-297`). Ele cai no Markdown só quando o índice está ilegível ou
  cortado (`:229-231`, `:266-267`). A lição escrita fora de fase, à mão ou sem Python fica fora do
  índice, e o gancho a cala.
- **As `refs:` envelhecem sem aviso.** A régua valida o `id`, a `area`, o `tipo` e os `gatilhos`
  (`regua.py:195-226`), e não as `refs:`. Nesta `main`, 10 refs das lições do kit têm número de
  linha, e 8 delas apontam para uma linha que ainda existe, mas não é mais a citada (Contexto, "As
  refs deslocadas hoje").
- **O `AGENTS.md` entra inteiro em toda conversa** (`CLAUDE.md:1`, `@AGENTS.md`), e nada mede o
  tamanho dele. O do outro projeto, que inspirou a proposta, foi de 7,5 mil a 25 mil palavras em
  cinco semanas (a leitura da EST, `leitura-produto-aprendizados-psi.md`, item D; esse número é a
  documentação inteira de lá).
- **A `licao` manda toda regra nova ao `AGENTS.md`** (`licao/SKILL.md:101-102`; regra 7,
  `AGENTS.md:170-171`). A regra que só importa a quem mexe numa área pesa em toda conversa, e o
  `docs/regras-de-area.md` existe para ela (`licoes_relevantes.py:312-315`).

## Escopo

### R1. O gancho percebe a lição que falta no índice (A1)

- **Quando o índice está legível**, o gancho também lista os `docs/licoes/*.md` da raiz do projeto,
  sem o `README.md` e sem a subpasta `arquivo/`. Lista os nomes, sem ler os arquivos. Cada lição
  cujo nome (sem o `.md`) não está entre os ids do índice entra no acervo pela leitura do Markdown,
  com as mesmas funções da varredura de hoje (`campo` e `ler_gatilhos`, `licoes_relevantes.py:273-284`).
  Daí em diante, ela é escolhida como as outras: pelo gatilho, senão pela área, dentro do mesmo teto.
- **O aviso, uma vez por sessão e por agente**, pela mesma marca das lições (`reivindicar`,
  `:409-424`), com um nome de marca próprio. O texto:
  - diz quantas lições estão fora do índice e os ids delas;
  - diz que elas chegam mesmo assim, lidas do Markdown;
  - diz como pôr o índice em dia: o `git add` da lição e a régua, pelo comando que a skill `licao`
    traz (passo 4).

  O aviso sai na primeira ação da sessão que chega ao gancho com um alvo (um caminho ou um
  comando), **mesmo que essa ação não tenha lição a receber**. Sem isso, o aviso só sairia por
  acaso, quando uma lição casasse.
- **O caso de hoje sem mudança:** com o índice ilegível, cortado ou ausente, o gancho continua
  varrendo o Markdown, com o aviso de hoje (`:563-568`), e o aviso novo não sai junto.
- **Custo:** uma listagem da pasta por ação, sem ler os arquivos. A lição que falta é lida, uma por
  ação, enquanto o índice não for regerado.
- **A lição ainda sem `git add`** também conta como fora do índice, porque o índice só vê o que o
  git rastreia (`regua.py:86-105`). É de propósito: no disco, ela já vale para o agente, e o aviso
  manda fazer o `git add`.
- **Os documentos:**
  - a docstring do gancho, na lista "Degradação" (`:38-42`);
  - o `docs/licoes/README.md`, onde diz que o gancho lê o índice e não os arquivos (`:108-111`).

### R2. A régua confere as `refs:` das lições (D2)

O formato, com a âncora, e o aviso em vez da falha são os cartões 2 e 3 ("Decisões").

- **A leitura:** a lista em bloco `refs:` do frontmatter, um item por linha. É o mesmo formato dos
  `gatilhos:`, lido pelo mesmo leitor do gancho (`ler_gatilhos`, `licoes_relevantes.py:168-205`),
  que passa a receber o nome do campo. Assim o formato não diverge entre os dois.
- **Qual item a régua confere:** o item que começa por um caminho com extensão (`.claude/regua.py`,
  `AGENTS.md`, `specs/…/plan.md`), seguido, se houver, de `:N` ou `:N-M`. Ela pula:
  - o item que não começa por um caminho, que é prosa ("a correção do usuário, 2026-11-21: …");
  - o caminho de um script no place do Roblox (`game.…`), que a régua não lê.
- **A âncora:** o primeiro trecho entre crases do item, depois do caminho. Exemplo:

  ```
  .claude/tests/test_codex.py:283 `def test_o_frontmatter_dos_agentes`
  ```

- **O que ela confere, por item:**

  | O item | O que a régua confere | O aviso, quando falha |
  |---|---|---|
  | caminho só | o arquivo existe | "o arquivo não existe" |
  | caminho e linha, sem âncora | o arquivo existe e tem a linha | "a linha não existe" ou "linha sem âncora: a régua não confere o que ela cita" |
  | caminho e âncora, sem linha | a âncora está no arquivo | "a âncora não está no arquivo" |
  | caminho, linha e âncora | a âncora está naquela linha, ou no intervalo `N-M` | "a âncora está agora na `:K`" ou "a âncora não está no arquivo" |

- **Onde o arquivo é procurado:** na raiz do projeto e, no modo plugin, também na pasta do kit. As
  lições do kit chegam ao jogo pela cópia da `iniciar-sdd` (`iniciar-sdd/SKILL.md:94`) e citam
  arquivos do kit (`.claude/tests/…`, as `specs/` do kit), que não existem no jogo.
- **A lição do kit, na instalação por cópia** (cartão 5): a cópia leva as lições do kit e não os
  testes nem as specs que elas citam (`README.md:178-184`), e aí a pasta do kit é a do jogo. As
  lições do kit trazem a linha `origem: kit` no frontmatter, e nelas o arquivo que não existe não
  dá aviso. A linha ou a âncora que mudou continua avisando em todas, e nas lições do jogo o
  arquivo ausente também. No kit, um teste exige a marca em toda lição e confere as refs sem a
  folga (todo arquivo citado existe). O índice não guarda o campo.
- **Aviso, e não erro.** A conferência roda no `--gerar` e no `--conferir`, com uma linha `AVISO`
  no stderr por ref, sem mudar o código de saída. É o mesmo comportamento do "não está no git" de
  hoje (`regua.py:126-134`). Uma ref velha nunca impede o índice de sair, nem a lição de chegar.
- **No kit, sem folga:** um teste da suíte exige zero avisos de ref nas lições do kit. Quem muda um
  arquivo citado no kit, varre (as convenções do `AGENTS.md`).
- **A migração:** as refs com linha das lições do kit ganham a âncora e a linha certa nesta fase,
  para o teste acima passar.

### R3. O teto do `AGENTS.md` (D3)

O teto configurável e o aviso em vez da falha são os cartões 4 e 3 ("Decisões").

- **A régua conta as palavras** do `AGENTS.md` da raiz do projeto como o `wc -w` conta: o que fica
  entre espaços. Acima do teto, sai um `AVISO` no `--gerar` e no `--conferir`, sem mudar o código
  de saída. O aviso diz:
  - o número de palavras e o teto;
  - que o arquivo entra inteiro em toda conversa;
  - a saída: o que só vale para quem mexe numa área vai ao `docs/regras-de-area.md` (regra 7);
  - onde mudar o teto: a linha `agents_teto` do `golem.toml`.
- **O teto é uma linha do `golem.toml`**, a chave nova `agents_teto`, com **3.000 palavras** por
  padrão:
  - o valor é um inteiro de 1 em diante, sem aspas, conferido pelo leitor de hoje
    (`golem.py:134-165`), que acusa a chave errada com o número da linha;
  - o padrão entra nas três receitas (`golem.py:105-121`), como o `gancho_teto`. Assim a tabela do
    `docs/guia-configuracao.md` (`:13-24`) ganha a linha, e o teste que a compara com o `golem.py`
    (`test_golem.py:216-231`) continua valendo;
  - a régua lê o valor pelo `golem.py`, como o gancho lê o `gancho_teto`
    (`licoes_relevantes.py:71-83`): o do projeto, e no modo plugin com o do central por baixo
    (`golem.py:172-190`);
  - com o `golem.toml` com erro, ou sem o `golem.py`, a régua usa os 3.000. Quem acusa o erro do
    `golem.toml` é o `aplicar`, como no `teto_do_gancho` (`golem.py:193-198`).
- **O `docs/guia-configuracao.md`** documenta a linha em três lugares: a tabela das receitas, a
  lista das chaves (`:56-57`) e o exemplo de `golem.toml` (`:101`).
- **Sem `AGENTS.md` na raiz**, a régua não diz nada.
- **O modelo cabe com folga:** um teste confere que o `templates/AGENTS.md` está abaixo do teto,
  para o jogo não nascer com o aviso.

### R4. A `licao` manda a regra de área ao `docs/regras-de-area.md` (C)

- **A `licao`, no passo 3** (`licao/SKILL.md:99-104`) e no "Escreve:" (`:9-12`), separa dois casos:
  - a regra que vale **para toda tarefa** vai ao `AGENTS.md`, curta e citando a lição, como hoje;
  - a regra que **só muda a decisão de quem mexe numa área** vai ao `docs/regras-de-area.md`. Ela
    leva o formato que o gancho lê: `## Regra N — Título`, com travessão, e a linha `areas:` logo
    abaixo (`licoes_relevantes.py:312-315`). Se o arquivo não existe, a `licao` o cria, com uma
    linha que diz o que ele é. A régua confere o formato (`regua.py:229-256`).
- **A frase do gatilho, nas palavras da EST:** "o gatilho casa com a ação, não com a ferramenta". Ela
  entra em dois lugares:
  - na `licao`, junto do "O gatilho descreve a ação em que o erro acontece" (`licao/SKILL.md:90-92`);
  - no `docs/licoes/README.md`, no mesmo ponto (`:143-145`).

  A frase completa diz que o gatilho casa com a ação em que o erro acontece, e não com a
  ferramenta que o revelou.
- **O formato das refs** (R2) vai à `licao`, nas regras de escrita (`:66`), e ao
  `docs/licoes/README.md`, no esqueleto (`:60-62`).
- **O `docs/licoes/README.md`** ganha o `docs/regras-de-area.md` em dois lugares: na tabela "Onde
  cada coisa mora" (`:9-15`) e na frase de quando a lição vira regra (`:17-19`).
- **A regra 7**, no `AGENTS.md` (`:170-171`) e no `templates/AGENTS.md` (`:159-160`), com o mesmo
  texto, pede a regra curta aqui só quando ela vale para toda tarefa. A de área vai ao
  `docs/regras-de-area.md`. O conciliador confere que os dois textos são iguais
  (`.claude/tests/test_conciliar.py`).

### R5. O princípio do índice, registrado como decisão (D1)

- **Onde:** a decisão 13 da seção 8 do `docs/plano-produto.md`, com os campos do modelo de ADR do
  kit (`templates/adr.md`):
  - o contexto;
  - as opções consideradas;
  - a decisão;
  - as consequências;
  - o gatilho de revisão;
  - a evidência de uso.

  A seção 8 é onde o kit registra as decisões técnicas, porque o kit não tem `docs/adr/` (`AGENTS.md`,
  "O projeto").
- **A decisão:** o índice gerado e versionado serve ao acervo que muda pouco e tem chave estável.
  Ele é conferido pela régua, e o gancho avisa quando falta algo nele (R1). O documento vivo usa o
  índice calculado na hora. **A consequência entra escrita assim:** "todo documento que cresce com
  o uso nasce com busca".
- **As consequências, documento por documento**, com o que já se aplica:

  | Documento | Como cresce | A busca |
  |---|---|---|
  | as lições | uma por armadilha | o índice gerado, e o gancho percebe a que falta nele (R1) |
  | as regras de área | uma por lição que vira regra de área | o gancho lê o arquivo na hora |
  | o registro dos jogos | um jogo por registro | a tabela, lida na hora (fase 3) |
  | o catálogo | uma peça por reaproveitamento | nasce com busca, na fase 6 |
  | as specs | uma pasta por fase | a ordem de leitura abre só a pasta da fase |
  | o `AGENTS.md` | regras e combinados | o teto medido (R3); a busca na hora, se o teto não bastar |

## Fora de escopo

- **O acervo geral, no central** (cartão 1, "Decisões"). O gancho lendo os dois acervos, a `licao` oferecendo subir a
  lição (com o ok e sem citar o projeto) e o projeto de cliente marcado, sem subir nada vão para uma
  fase própria, logo depois desta. Esta fase deixa a pasta das lições num só lugar no código, para
  a fase seguinte trocar. Hoje o gancho lê só o acervo do jogo (`licoes_relevantes.py:66`), e o
  central não tem pasta de lições (`golem.py:424-437`).
- **A lição que está no índice e cujo arquivo sumiu.** O gancho continua entregando só o id dela,
  sem o sinal (`licoes_relevantes.py:338-343`, `:588-589`). Nenhuma falha vista.
- **Conferir que a linha ainda diz o mesmo.** A âncora mostra que o trecho continua ali, e não que
  o sentido da citação continua.
- **A cópia das lições do kit no jogo envelhece** quando o kit muda depois do registro: a régua do
  jogo pode avisar de uma ref de lição do kit. O que o kit entrega, e como atualiza, é da fase 7
  (decisão 6) e da fase 9.
- **A `iniciar-conversa` e a `implementar-fase`** já buscam na pasta, e não no índice
  (`iniciar-conversa/SKILL.md:77`, `implementar-fase/SKILL.md:24-28`), e ficam como estão.
- **O Codex**, que usa a cópia, ganha o gancho novo pelas cópias geradas, como hoje. O repositório
  do kit não versiona as cópias (as convenções do `AGENTS.md`).
- **O roteiro (seção 7):** a `validar-fase` marca a fase, e o resto é da GER.

## Decisões

**Do autor do kit, pela EST, em 2026-11-22** (a resposta de cada cartão, nas palavras dele):
1. **O acervo geral fica para uma fase própria**, logo depois desta: "A: fase própria
   (Recomendado)". A GER recebeu o pedido de replanejar o roteiro. Descartado: os dois acervos
   nesta fase, que a levaria do tamanho M ao G.
2. **A ref leva o arquivo, a linha e a âncora:** "A: arquivo, linha e âncora (Recomendado)".
   Descartado: conferir só o arquivo e a linha, que passaria as refs deslocadas de hoje.
3. **A ref velha e o teto passado dão aviso, não falha:** "A: aviso (Recomendado)". No kit, um
   teste segura as refs em dia. Descartado: a falha, que pararia o índice de quem usa o kit por uma
   citação velha.
4. **O teto do `AGENTS.md` é configurável:** "C: configurável", uma linha no `golem.toml` com
   3.000 palavras por padrão. Ele não escolheu a recomendada (o teto fixo). A ressalva do cartão, a
   chave nova sem pedido (regra 10), deixa de valer, porque agora o pedido é dele. Descartado: o
   teto fixo de 3.000 na régua.

5. **Na instalação por cópia, só as refs das lições do kit calam o arquivo ausente:** "D: só as do
   kit calam (Recomendado)" (2026-11-22). O D é da EST; a recomendação desta conversa era a A (o
   arquivo ausente não avisa em lição nenhuma). Achado do revisor do G2: a cópia nascia com 12
   avisos. Descartados: a A, que calaria também o arquivo apagado ou renomeado nas lições do jogo;
   a B, o jogo nascendo com os avisos; a C, a cópia levando os arquivos citados, que poria as fases
   do kit na `specs/` do jogo. A marca é a linha `origem: kit` (detalhe do agente: uma lista na
   régua não separaria as lições na cópia, em que a pasta do kit é a do jogo).

A premissa dos "dois acervos" do pedido à fase estava errada: o gancho lê só o acervo do jogo. A EST
registrou que o erro estava no pedido dela à GER.

**A aprovação da spec:** à pergunta "Aprova a spec da fase 4, com um commit por grupo na branch?",
"Aprovo" (o autor do kit, 2026-11-22). Ela aprova junto o D1 como decisão 13 e o aviso do A1 mesmo
sem lição ("Do agente", abaixo).

**Já tomadas e que esta fase aplica:**
- a decisão 10: a fase própria de "lições e índices", com "Fase própria (Recomendado)", e o D1
  nela, com "Na fase lições e índices (Recommended)";
- a decisão 11: o Golem central, que pede a busca nas lições do kit pela pasta do kit (R2);
- o pedido do Rodrigo à EST, de 2026-11-22: "pede à GER para abrir a fase 4". À GER, ele disse
  "Sim, abre".

**Do agente, dentro destas:**
- **O D1 vai à seção 8, como decisão 13**, e não a um `docs/adr/` novo. O kit registra as decisões
  lá (`AGENTS.md`, "O projeto"). Descartado: criar o `docs/adr/` no kit.
- **O aviso do A1 sai mesmo sem lição para a ação.** Descartado: avisar só junto de uma entrega,
  porque aí o aviso dependeria de uma lição casar.
- **A lição fora do índice chega pelo Markdown, além do aviso.** Descartado: só avisar, porque
  calar a lição até alguém rodar a régua é o defeito que o A1 corrige.
- **As refs são lidas pelo leitor dos `gatilhos:`**, com o nome do campo como parâmetro. Descartado:
  um leitor novo, que divergiria do formato.
- **O teto vale para o `AGENTS.md` da raiz.** O do kit e o do jogo são conferidos cada um pela
  própria régua, e o modelo, por um teste. Descartado: medir também o `docs/operacao-das-conversas.md`
  (3.431 palavras). Ele não entra em toda conversa: só se abre quando a tarefa pede.

## Contexto

- **A suíte em `746ebf7`:** `166 passed in 71.92s`, sem puladas, com o comando dos "Comandos
  reais", rodado nesta conversa. O `regua.py --conferir` deu `ok       .claude/indice/licoes.yaml`.
- **As refs deslocadas hoje**, conferidas com `sed -n` e `grep -n` em `746ebf7`:
  - `frontmatter-invalido-some-com-o-agente-sem-aviso`: a ref `test_codex.py:276` cita
    `test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido`, que hoje está na `:283`;
  - `o-windows-muda-o-que-o-sh-recebe-do-python`: a `test_gancho.py:400` cita `_comando_do_lancador`,
    que está na `:402`, e a `test_codex.py:241` cita
    `test_lancador_sem_o_proprio_caminho_acha_a_raiz_pelo_git`, que está na `:248`;
  - `o-aviso-entre-duas-perguntas-fica-no-raciocinio`: a `configurar/SKILL.md:52-61` cita "o aviso,
    agora na descrição do botão Nunca", que está na `:78-81`, e a `:85-88` cita "o arquivo, agora
    no texto da pergunta de gravar", que está na `:111-112`;
  - `sem-python-no-path-nao-e-maquina-sem-python`: a `diagnostico/SKILL.md:37-46 e :82-95` cita "a
    pergunta onde está o Python", que está na `:62`;
  - `trocar-o-localappdata-nao-esconde-o-python-do-agente`: a `diagnostico/SKILL.md:69-76` cita "a
    busca, que lê o $LOCALAPPDATA", que está na `:95-96`, e a `:96-102` cita "o winget", que está
    na `:124`. Essas duas faltavam na primeira versão desta lista, que dizia 8 refs em 5 lições; a
    régua do G2 as achou (2026-11-22).

  As 10 refs com linha estão em 6 lições. As outras duas estão em dia: a
  `.claude/agents/revisor.md:3` (a `description`) e a `implementar-fase/SKILL.md:24-28`. Uma
  conferência só de "o arquivo e a linha existem" passaria as 8 deslocadas.
- **O formato das refs hoje é livre:**
  - uma parte é caminho com linha (as 10 acima);
  - uma parte é caminho e uma descrição entre parênteses
    (`docs/guia-roblox.md (seção 4, Voltar atrás)`);
  - uma parte é prosa, sem caminho (`conferir-e-agir-em-chamadas-separadas.md:12-14`,
    `num-produto-a-falha-vista-vem-do-uso.md:12-14`).
- **A marca da sessão** é um arquivo por lição, numa pasta por agente, criado de forma atômica
  (`licoes_relevantes.py:349-424`). O aviso do R1 usa a mesma marca, como as regras de área usam a
  `regra-N` (`:532-533`).
- **O tamanho do `AGENTS.md`** (`wc -w`, em `746ebf7`): o do kit tem 2.578 palavras, e o
  `templates/AGENTS.md`, 2.526.
- **O `docs/regras-de-area.md`** não existe no kit. O modelo do Roblox está em
  `templates/roblox/regras-de-area.md`, e o `docs/guia-roblox.md:51` manda copiá-lo para o jogo.
- **A `iniciar-sdd` copia todas as lições do kit para o jogo** (`iniciar-sdd/SKILL.md:94`,
  `cp -n "$KIT"/docs/licoes/*.md docs/licoes/`).

## Padrões a seguir

- **O aviso que não muda o código de saída** segue o `avisar_nao_rastreados` (`regua.py:126-134`):
  uma linha `  AVISO    …` no stderr.
- **A marca do aviso** segue a das regras de área (`licoes_relevantes.py:530-533`): um nome sem `:`,
  reivindicado antes da entrega e devolvido se a entrega falhar (`:550-558`).
- **Os testes do gancho e da régua** seguem os de hoje, sobre a árvore descartável `acervo`
  (`conftest.py`). O teste "o índice legível sem a lição nova" segue o de "o índice cortado".

## Notas do usuário

- "lembrando que a gente está desenvolvendo um produto para as outras pessoas usarem, então a gente
  não está esperando ver o caso real aqui, né?" (o autor do kit, 2026-11-21, sobre o item D; a
  leitura da EST). É por isso que o D3 e o R2 valem para o projeto de quem usa o kit, e não só para
  o kit.
- "trouxesse junto com a MET uma proposta de trazer essas novas alterações para cá. Principalmente
  a parte sobre indexação de documentação e sobre as lições passarem pela conversa de método." (o
  autor do kit, 2026-11-21).

## Perguntas em aberto

Nenhuma.
