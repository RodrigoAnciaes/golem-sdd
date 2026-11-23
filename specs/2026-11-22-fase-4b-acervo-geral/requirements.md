# Fase 4b: o acervo geral de lições — Requisitos

Branch `fase-4b-acervo-geral`, cortada de `53625f6` (a `main` em 2026-11-22, com o PR 14 da fase
4). Os fatos do kit foram lidos em `53625f6`, salvo onde se diz outro commit.

**Aprovada** pelo autor do kit: "Aprovo" (2026-11-22), com um commit por grupo na branch da fase.

## Objetivo

No Golem central, um acervo geral de lições, ao lado do acervo de cada jogo
(`docs/plano-produto.md:621`; seção 8, decisões 11 e 14):
- o gancho lê os dois acervos, com a raiz do gancho valendo para os dois;
- a `licao` oferece subir a lição ao acervo geral, só com o ok do usuário e sem citar o projeto;
- o projeto de cliente fica marcado e não sobe nada.

**A palavra na tela.** O usuário não lê "cliente". Ele lê "jogo para terceiros" (um estúdio ou
outra pessoa), na pergunta, no registro, no `onde` e nas mensagens. No código, os nomes internos
podem continuar `cliente` (o autor do kit, pela EST, 2026-11-22; "Decisões").

**O "pronto" do roteiro** está "a definir na spec da fase" (`docs/plano-produto.md:621`). Esta spec
o define assim:
- num jogo do Golem central, uma lição que só existe no acervo geral chega pelo gancho na ação que
  casa com ela, com o rótulo do acervo geral; a lição de mesmo id no jogo vence a geral;
- fora do modo plugin (o repositório do kit e a instalação por cópia), o gancho não lê o acervo
  geral, mesmo com lições nele;
- num jogo marcado como para terceiros, o comando de subir recusa, e a `licao` não oferece a subida;
- a lição que cita o nome ou a pasta do jogo, ou um arquivo dele, é recusada na subida;
- a lição subida chega pelo gancho em **outro** jogo registrado;
- a lição do jogo mudada depois da subida sai num `AVISO` da régua, no jogo.

**Por quê.** Hoje cada jogo começa sem o que os outros ensinaram: o gancho lê só as lições do
projeto aberto (`.claude/hooks/licoes_relevantes.py:66-70`), e o central não tem pasta de lições
(`.claude/golem.py:443-456`, `criar_central`). O pedido do autor do kit, na decisão 11: "guarda as
lições", com "lições e estilo ficam em dois níveis, e o geral só sobe com o ok dele e sem citar o
projeto" (`docs/plano-produto.md:776-790`).

**O usuário padrão primeiro.** A lente do autor do kit para esta fase (pela EST, 2026-11-22): "A
maioria das vezes, jogos com estúdio vão ser exceção. A maioria das pessoas desenvolve sozinha.
[...] a gente não pode prejudicar o usuário padrão." Quem faz jogos só para si responde uma
pergunta a mais, uma vez (R3), e nada muda no resto do fluxo dele.

## Escopo

### R1. O acervo geral mora no central

- **Onde:** `~/Golem/docs/licoes/`, com o índice em `~/Golem/.claude/indice/licoes.yaml`. É o
  mesmo desenho do jogo, de propósito: a régua e o gancho já sabem ler uma pasta assim, e o
  `~/Golem/.claude/` já existe (o "ligado" do central, `golem.py:455`). O formato da lição é o do
  `docs/licoes/README.md`, com a mesma régua.
- **Quem cria a pasta:** o comando de subir (R4), na primeira lição. O `central` não a cria antes
  (nada vazio no central sem uso).
- **O índice do geral** sai da régua do kit rodada com a raiz no central. O central não é um
  repositório git (`criar_central` não roda `git init`, `golem.py:443-456`), e sem git a régua não
  filtra pelo que o git rastreia: indexa o disco (`regua.py:100-129`, `:424-434`). Se o usuário
  puser o central no git, vale o que vale num jogo (o `git add` antes do `--gerar`).

### R2. O gancho lê os dois acervos

- **A raiz do gancho vale para os dois.** O `gancho.sh` já decide a raiz do jogo e, no modo plugin,
  o central (`gancho.sh:56-66`). Ele passa a exportar o central ao `.py` no `GOLEM_CENTRAL`, como
  já passa a raiz no `CLAUDE_PROJECT_DIR` (`gancho.sh:321-322`). Fora do modo plugin, ele não
  calcula central nenhum, e o `.py` não lê o geral (abaixo).
- **O `.py` lê o acervo geral só no modo plugin:** a pasta do kit tem o
  `.claude-plugin/plugin.json`, a raiz do jogo é outra, e o `GOLEM_CENTRAL` aponta uma pasta que
  não é a raiz do jogo. A sessão aberta no próprio central lê só um acervo, o dele.
- **A escolha**, sobre os dois acervos juntos, dentro do mesmo teto (`teto_do_gancho`):
  - a regra de hoje fica: a que casou por gatilho vem antes da que veio só pela área
    (`licoes_relevantes.py:320-347`);
  - dentro de cada grupo, as do jogo vêm antes das gerais (o estudo do central, pergunta 2:
    "primeiro as do jogo, depois as gerais, dentro do mesmo teto");
  - **o mesmo id nos dois acervos:** vale a do jogo, e a geral não entra. É o caso da lição que
    subiu daquele jogo (R4: a subida copia).
- **O sinal** (o "Como perceber da próxima vez") sai do Markdown do acervo de onde a lição veio.
  Hoje ele sai sempre da pasta do jogo (`sinal_de`, `licoes_relevantes.py:378-383`).
- **O rótulo:** as gerais saem num bloco próprio, depois das do jogo, com o título que diz de onde
  vêm (o acervo geral, com a pasta) e que valem para todo jogo. Hoje o título diz "armadilhas
  registradas neste projeto" (`:641-646`), o que é falso para a geral.
- **A marca da sessão** é a de hoje, pelo id (`reivindicar`, `:452-467`): como o mesmo id não entra
  duas vezes, um id só basta.
- **A degradação vale por acervo**, com o texto de hoje apontando a pasta certa:
  - o índice do geral ilegível, cortado ou ausente → a varredura do Markdown do geral, com o aviso
    (`:617-622`) dizendo que é o índice do acervo geral e o comando para regerá-lo;
  - a lição do geral fora do índice dele → lida do Markdown, com o aviso "índice defasado" do
    geral, uma vez por sessão e por agente, por uma marca própria (a do jogo é
    `aviso-indice-defasado`, `:388-389`);
  - sem a pasta do geral (o caso de todo central até a primeira subida), nada muda e nada se avisa.
- **Os documentos:** a docstring do gancho (o topo e a "Degradação", `:2-46`) e o
  `docs/licoes/README.md`, "Como o gancho entrega as lições" (`:115-135`).

### R3. O jogo para terceiros fica marcado, em dois níveis

A marca é por jogo, mas a pergunta por jogo só aparece para quem faz jogos para terceiros.

- **A pergunta geral, uma vez:** "Você costuma fazer jogos para estúdios ou outras pessoas?" (o
  texto da EST, aceito pelo autor do kit em 2026-11-22). A resposta vai a uma linha nova do
  `golem.toml` do central, `jogos_para_terceiros = "sim" | "nao"`. É a configuração do central,
  que vale em todos os jogos (a da fase 3, `docs/plano-produto.md:619`; a mesma em que a fase 5
  grava a preferência dos emojis, decisão 12, `:813-816`).
  - **Quem pergunta:** a `iniciar-sdd`, no primeiro registro de um jogo em que o `golem.toml` do
    central ainda não tem a linha. O central não tem hoje uma configuração com perguntas: o
    `golem.py central` só cria os arquivos (`README.md:122-130`, `golem.py:443-456`), e a
    `configurar` é opcional (`README.md:134-138`) e só pergunta a receita, o revisor e o "parar a
    cada parte" (`configurar/SKILL.md:52-53`). O primeiro registro é a primeira vez que a resposta
    serve. O `/golem:comecar` da fase 7 pode trazê-la para a configuração inicial: isso é da fase 7.
  - **Sem a linha** (nunca respondida, o caminho sem Python, o central de antes desta fase): vale
    `nao` (a sugestão da EST, aceita pelo autor do kit).
  - **A leitura:** pela leitura de hoje do `golem.toml`, que recusa chave desconhecida
    (`golem.py:155-157`), com a chave nova entre as que valem (`VALORES`, `:94-107`). A linha só
    vale no `golem.toml` do central. Ela não depende da receita, e o guia ganha uma linha para ela
    (R7). **Conferido no G2:** ela fica fora das `RECEITAS`, num `FORA_DAS_RECEITAS` com o `nao`
    sem a linha, que a `configuracao` põe por baixo da receita. O `onde` a mostra só no modo
    plugin, com "(o padrão)" sem a linha. No guia, ela não entra na tabela das receitas, que o
    `test_golem.py:226` confere célula por célula contra as `RECEITAS`: entra na lista "O que cada
    chave faz", em prosa. A linha num `golem.toml` que não é o do central é erro, que diz a chave
    e onde ela vale (da revisão do G2: senão a do jogo, que vai ao git dele, venceria a do central).
  - **Mudar a resposta:** à mão, na linha do `golem.toml` do central, como as outras chaves
    (`docs/guia-configuracao.md:72`).
- **Com `sim`, a pergunta por jogo, ao registrar:** "Você faz este jogo para você mesmo, nos seus
  próprios repositórios, ou para um estúdio ou outra pessoa? Se for para outra pessoa, o Golem não
  leva nada deste jogo para o acervo geral, que todos os seus jogos leem, porque o que se aprende
  nele pertence a quem encomendou." (o texto da EST, aceito pelo autor do kit em 2026-11-22). Com
  "para outra pessoa", a skill passa o `--terceiros` ao `registrar`.
- **Com `nao`, nenhuma pergunta por jogo:** só uma linha no relato do registro, "se este jogo for
  de um estúdio ou de outra pessoa, me diga". Se o usuário disser, a skill roda o `registrar` de
  novo com o `--terceiros`.
- **A marca:** uma coluna `Para terceiros` (`sim` ou `não`) no registro, o `~/Golem/jogos.md`. Hoje
  a tabela tem `Jogo | Pasta | Registrado em` (`golem.py:363-368`). A marca não leva o nome de
  quem encomendou: nesta fase, o nome não tem uso.
- **O `registrar <pasta> --terceiros`** marca o jogo. Rodado num jogo já registrado, troca a marca
  para `sim` sem duplicar a linha. Rodado de novo **sem** o `--terceiros`, não desmarca: desmarcar
  é à mão, no `jogos.md`, como apagar uma linha hoje (`golem.py:364-366`). Assim, nenhum comando
  repetido tira a proteção sem querer. Pela mesma razão, só `não` (ou `nao`) desmarca: outro valor
  escrito à mão na coluna vale `sim` (da revisão do G2).
- **O registro antigo** (três colunas, da fase 3) continua sendo lido, com `não` em todo jogo. A
  primeira escrita do `registrar` o passa a quatro colunas, com `não` nas linhas que já existiam,
  para a tabela não ficar com linhas de tamanhos diferentes.
- **A `iniciar-sdd`**: as perguntas acima no passo 2 (`iniciar-sdd/SKILL.md:42-55`), depois da
  pasta; o `--terceiros` no `registrar` (`:111-115`); e a coluna nova no caminho sem Python
  (`:135-142`), sempre com `não` ali, salvo se o usuário disser que o jogo é para terceiros.
- **O `onde`** (`golem.py:506-530`) diz, no modo plugin, se o projeto é para terceiros (`sim`,
  `não` ou "fora do registro"). É por ele que a `licao` sabe se oferece a subida (R6).
- **O jogo para terceiros lê o acervo geral:** sim (P3). A marca só bloqueia a subida.

### R4. O comando de subir

Novo comando do `golem.py`: **`subir <arquivo> [--substituir]`**. O `<arquivo>` é a versão da
lição que vai ao geral, já reescrita sem o projeto e lida pelo usuário (R6). Ele confere tudo antes
de escrever e, se recusar, diz por quê e não escreve nada:

- **só no modo plugin** (`modo_plugin`, `golem.py:77-79`): fora dele, não há central;
- **só num jogo do registro e que não é para terceiros:** o projeto fora do registro também recusa,
  porque aí não se sabe para quem ele é;
- **só uma lição do jogo:** um `<id>.md` (não o `README.md`), em UTF-8, com a lição de mesmo nome
  no `docs/licoes/` do jogo ("toda lição nasce no jogo", o estudo; e é a impressão dela que o R5
  compara). Da revisão do G2;
- **o texto não cita o projeto.** Recusa se o arquivo traz, sem diferenciar maiúsculas:
  - o nome do jogo no registro, ou o nome da pasta dele;
  - o caminho da pasta do jogo;
  - uma ref (`refs:`) a um arquivo que existe no jogo e não no kit, ou a um script do place
    (`game.…`);

  A lição do kit e a ref em prosa passam. A conferência é mecânica e não substitui a leitura do
  usuário: ela pega o caso grosseiro (o nome, a pasta, o arquivo), e a releitura pega o resto (a
  chave do save, o nome de um NPC).

  **O nome que é palavra comum** (o jogo "Obby" e a lição sobre obbies; a pasta `jogo`): a
  recusa pelo nome diz a saída, o `--palavra-comum`, que pula só a conferência do nome do jogo e
  do da pasta. O caminho da pasta e as refs continuam conferidos. Quem o passa é a `licao`, depois
  de perguntar (R6). Da revisão do G2, decidido pelo autor do kit ("Decisões");
- **o frontmatter passa na régua** (o `id` igual ao nome do arquivo, a `area`, o `tipo`, os
  `gatilhos`): a régua do kit roda numa cópia do acervo geral com a lição nova, antes de escrever
  no central;
- **o id ainda não está no geral**, salvo com o `--substituir` (a lição geral atualizada com
  evidência nova, como manda o passo 1 da `licao`).

Depois de escrever `~/Golem/docs/licoes/<id>.md`, ele:
- regera o índice do geral (a régua do kit, com a raiz no central). Se a régua falhar ali (o
  central posto no git sem lição rastreada), desfaz a escrita (e a pasta que ela criou) e sai com o
  `ERRO`, que diz a saída: copiar a lição à mão ao central, o `git add` dela e o subir de novo com
  o `--substituir`. Os `AVISO` dela
  (a lição fora do git do central, que fica fora do índice) saem no relato;
- grava a subida em `~/Golem/.claude/indice/subidas.txt`, uma linha por id: o id, a impressão
  (sha256) da lição do jogo e a da versão geral, como estavam na subida (R5). A linha do mesmo id
  se troca;
- diz o que escreveu, uma linha por arquivo, como o `aplicar` (`golem.py:483-487`).

A lição do jogo não muda: a subida copia (P2).

### R5. A régua avisa a divergência

A subida copia (P2), e a cópia pode envelhecer. O `regua.py --conferir` (e o `--gerar`), rodado num
jogo no modo plugin, dá um `AVISO` para cada lição do jogo cujo id está no `subidas.txt` do central
e que:
- mudou desde a subida (a impressão da lição do jogo não é a gravada), ou
- tem a versão geral mudada desde a subida (a impressão do arquivo geral não é a gravada, ou o
  arquivo sumiu).

O aviso diz as duas pastas e o caminho de volta: conferir a versão geral e subir de novo com o
`--substituir` (o que renova a impressão); se a diferença é de propósito, subir a própria versão
geral de novo também renova. É `AVISO`, não erro: a régua não falha por isso, como nos avisos das
refs e do teto (`regua.py:377-387`).

- **A impressão** é a do texto com as quebras de linha passadas a `\n`, para o `core.autocrlf` do
  Git for Windows não dar divergência falsa.
- **Por quê no `subidas.txt`, e não no frontmatter da lição geral:** a lição geral fica no formato
  de toda lição, sem campo novo na régua e no índice, e a impressão da própria versão geral não
  cabe dentro dela.
- **A régua acha o central** pelo `golem.py`, que ela já carrega para o teto (`regua.py:348-359`):
  o `modo_plugin` e o `central()` (`golem.py:64-79`). Fora do modo plugin, nada muda.
- **O caso aceito:** um segundo jogo com uma lição própria de mesmo id que uma geral subida de
  outro jogo também sai no aviso. É raro, e o aviso tem uso aí: o gancho dele entrega a do jogo, e
  não a geral (R2).

### R6. A `licao` oferece a subida

Um passo novo na `licao` (`licao/SKILL.md`), depois do fecho (`:186-192`), só no Golem central:
- **quando aparece:** no modo plugin, com o `onde` dizendo que o projeto não é para terceiros, e só
  quando a lição **parece valer para qualquer jogo** (a recomendação da EST, aceita pelo autor do
  kit em 2026-11-22). O agente julga pelo que a lição ensina: a armadilha da plataforma, da API ou
  da ferramenta (o exemplo do estudo: "DataStore sem `pcall`") parece valer; a que só existe por
  causa deste jogo ("o save deste jogo usa a chave X") não parece, e aí o passo diz em uma linha que
  a lição fica só no jogo, e por quê. **Na dúvida, pergunta**: "algumas perguntas a mais do usuário
  não tem problema. Ela só tem que deixar mais óbvia" (o autor do kit, 2026-11-22);
- **onde não aparece:** no jogo para terceiros (a skill diz em uma linha que nada deste jogo vai ao
  acervo geral, porque ele é para outra pessoa), fora do registro, na cópia (o Codex) e no kit;
- **a pergunta**, com botões (texto numerado onde não houver), deixa óbvio o que é o acervo geral:
  que todos os seus jogos o leem, que vai uma cópia, sem nada deste projeto, e que a lição deste
  jogo fica como está. As duas opções: "copiar ao acervo geral" e "fica só neste jogo";
- **com o sim**, o agente reescreve a lição sem nada do projeto (o nome, as pastas, os arquivos do
  jogo, o place, as chaves) e mostra o texto **dentro da pergunta** "Gravo no acervo geral assim?"
  (lição `o-aviso-entre-duas-perguntas-fica-no-raciocinio`: o texto entre duas perguntas fica no
  raciocínio). Só com o segundo sim ele grava a versão numa pasta temporária e roda o `subir`;
- **o nome comum:** se o `subir` recusar pelo nome do jogo, a skill pergunta com botões: "O texto
  cita '<nome>', o nome deste jogo. Aqui é a palavra comum, e não o seu jogo?". Com o sim, roda o
  `subir` de novo com o `--palavra-comum`; com o não, reescreve o trecho e volta à segunda
  pergunta;
- **a prova:** o gancho rodado com a ação que deve receber a lição, como no passo 5
  (`:161-178`), mostra o id com o rótulo do geral;
- **o passo 1** ("Conferir se já existe", `:32-39`) passa a buscar também no geral, no modo plugin:
  a lição geral próxima se atualiza (com o `--substituir`), em vez de nascer outra;
- **o `AVISO` da divergência** (R5), quando a régua do passo 4 o der depois de a lição do jogo
  mudar: a skill o mostra e pergunta se sobe a versão nova, pelo mesmo caminho das duas perguntas.

### R7. Os documentos que mudam

- **O `README.md`**, no "Mapa das pastas" (`:343-372`): o `docs/licoes/` (`:363`) e o
  `.claude/indice/licoes.yaml` (`:368`) passam a morar no jogo e, os do acervo geral, no central,
  com o `subidas.txt`; o `jogos.md` (`:357`) ganha a marca de jogo para terceiros.
- **O `docs/licoes/README.md`**: a tabela "Onde cada coisa mora" (`:8-17`) ganha o acervo geral, e
  "Como o gancho entrega as lições" (`:115-135`), os dois acervos.
- **O `docs/guia-configuracao.md`**: a chave `jogos_para_terceiros`, que só vale no central e não
  depende da receita.
- **Quem muda, varre:** os documentos e as skills que dizem que o gancho lê só o acervo do jogo, ou
  que o registro tem três colunas (as buscas estão no `plan.md`, G4).

## Fora de escopo

- **As regras de área gerais** (o estudo, tabela do T1: "no jogo, e as gerais no central"). O pedido
  da fase são as lições, e nenhuma regra de área geral foi pedida.
- **O estilo em dois níveis:** fase 6.
- **O "onde está tudo?" (T1)** e esconder os outros jogos no jogo para terceiros (o estudo,
  pergunta 3): fase 7. Também da fase 7: levar a pergunta geral (R3) ao `/golem:comecar`.
- **As lições do kit no acervo geral**, no lugar da cópia em cada jogo
  (`iniciar-sdd/SKILL.md:94`): a escolha das lições que o kit entrega é da fase 7 (decisão 6).
- **O histórico do acervo geral.** O central não é um repositório git (R1), e a lição geral não tem
  commit. A lição continua no git do jogo de onde subiu. Pôr o central no git é escolha do usuário,
  e a régua já a trata (R1).
- **Descer uma lição geral para um jogo, ou apagar uma geral:** à mão, apagando o arquivo e rodando
  a régua no central. Nenhuma falha vista.
- **Mudar a resposta geral (R3) por uma skill:** à mão, na linha do `golem.toml`. Nenhuma falha
  vista.
- **O Codex:** fica na instalação por cópia (decisão 11), sem central; o passo novo da `licao` não
  aparece lá.
- **O roteiro (seção 7):** a `validar-fase` marca a fase; o resto é da GER.

## Decisões

**Já tomadas e que esta fase aplica:**
- a decisão 11: as lições em dois níveis, o geral só sobe com o ok dele e sem citar o projeto, o
  gancho achando o jogo pelo `CLAUDE_PROJECT_DIR`;
- a decisão 14: o acervo geral numa fase própria, numerada 4b ("A: fase própria (Recomendado)" e
  "4b, sem mudar o resto (Recomendado)", 2026-11-22);
- a decisão 13: o índice gerado para o acervo que muda pouco e tem chave estável (as lições), com o
  gancho percebendo a que falta. O acervo geral é um acervo de lições: ganha o índice.

**Do autor do kit, pela EST, em 2026-11-22** (os cartões P1 a P3, depois de uma segunda passada com
a lente do usuário padrão, no "Objetivo"). As palavras finais dele: "Ok. Quanto à divergência, pode
ser da sua recomendação. E eu gostei da sua ideia da pergunta como ficou. Aí vamos seguir todas as
suas recomendações, então." O que ele aceitou:
- **P1, a marca:** no `~/Golem/jogos.md`, e não no `golem.toml` do jogo, que iria ao git do estúdio.
  Duas mudanças pedidas por ele:
  - **a palavra:** "ao invés de cliente, você poderia tentar usar as palavras mais óbvias para a
    pessoa, como você está desenvolvendo esse projeto por si mesmo, usando os próprios
    repositórios, ou você está desenvolvendo para um estúdio, para um terceiro. Aí tem que explicar
    direito." O texto da pergunta por jogo, no R3;
  - **os dois níveis:** "talvez isso fosse uma vez só na configuração geral do golem". A pergunta
    geral, a por jogo só com `sim`, e a linha de aviso com `não` (R3). Sem resposta, vale `não`.
- **P2, copiar ou mover:** copiar. A ressalva dele era a divergência: a régua avisa quando a lição
  do jogo e a versão geral ficam diferentes (R5), a "conferência automática", em vez de só um
  lembrete na `licao`, porque pega também a edição feita à mão. O fato que pesou: o central não é
  repositório git (`golem.py:443-456`); mover tiraria o texto da lição do git, e copiar deixa o
  backup no jogo.
- **P3, o jogo para terceiros lê o acervo geral:** sim. Só não sobe nada.
- **A oferta só quando a lição parece geral** (R6), e não ao fim de toda lição, com a nuance dele:
  "algumas perguntas a mais do usuário não tem problema. Ela só tem que deixar mais óbvia."
- **O nome do jogo que é palavra comum** (cartão da EST, depois da revisão do G2, que mostrou a
  recusa sem saída com nomes como "Obby", "Moedas" ou a pasta `jogo`): "A: recusa com saída
  (Recomendado)" (2026-11-22). As outras opções eram tirar a conferência do nome (B) e não mudar
  nada (C). O R4 e o R6 trazem o que muda.

**Do agente, dentro destas:**
- **O geral em `~/Golem/docs/licoes/`**, com o índice em `~/Golem/.claude/indice/`, e não numa
  `~/Golem/licoes/` (o estudo): o mesmo desenho do jogo deixa a régua e o gancho como estão, só com
  outra raiz. Descartado: uma pasta de outro formato, que pediria caminhos novos na régua.
- **O central passa ao `.py` pelo `GOLEM_CENTRAL`**, que o `gancho.sh` já calcula, e não por uma
  conta nova no `.py`: uma regra só, a do `sh` e do `golem.py` (`golem.py:64-74`). O `.py` confere
  o modo plugin, para não ler o geral se a variável vier do ambiente fora dele.
- **A conferência de "não cita o projeto" fica no `subir`**, mecânica e testável, e não só na
  leitura do agente. Ela pega o grosseiro; a releitura do usuário pega o resto. Descartado: só a
  leitura, que não se testa.
- **O `subir` regera o índice do geral**, para a lição chegar já na ação seguinte, sem um segundo
  comando. Descartado: deixar à `licao` o `cd` ao central e a régua, um passo a mais a esquecer.
- **O mesmo id: vale a do jogo.** A do jogo tem as refs dele e é a de origem. Descartado: entregar
  as duas, que repetiria o sinal.
- **Desmarcar é à mão.** Descartado: um `--nao-terceiros`, sem caso real.
- **A pergunta geral na `iniciar-sdd`, no primeiro registro** (R3), e não na `configurar`: a
  `configurar` é opcional, e quem nunca a roda nunca seria perguntado. Descartado: perguntar nas
  duas, que repete a pergunta.
- **O `--terceiros`, a coluna `Para terceiros` e a chave `jogos_para_terceiros`**: o usuário lê
  esses nomes (o registro, o comando no relato, o `golem.toml`), e a palavra "cliente" não aparece
  na tela. Os nomes internos do código podem ficar `cliente`.
- **A impressão da subida no `subidas.txt`** (R5), e não no frontmatter: ver o R5.

## Contexto

- **A suíte em `53625f6`:** `209 passed in 80.07s (0:01:20)`, sem puladas, com o comando dos
  "Comandos reais", rodado nesta conversa. O `regua.py --conferir` deu
  `ok       .claude/indice/licoes.yaml`.
- **A pasta das lições num lugar só:** no gancho, `LICOES` e `INDICE` saem da `RAIZ`
  (`licoes_relevantes.py:66-70`), e todo o resto as usa: `do_indice` (`:228-276`),
  `arquivos_de_licao` (`:279-288`), `sinal_de` (`:378-383`). Na régua, o mesmo
  (`regua.py:69-73`). É o que a fase 4 deixou para esta trocar (decisão 14).
- **A raiz da régua no plugin** é o git da pasta corrente, ou a pasta corrente
  (`regua.py:53-66`): rodada com a pasta corrente no central, que não é git, a raiz é o central.
- **A suíte não lê o central da máquina:** o `conftest.py:30-34` aponta o `GOLEM_CENTRAL` para uma
  pasta que não existe e tira o `CLAUDE_PROJECT_DIR`. A árvore `Plugin` (`conftest.py:182-222`) já
  monta o kit como plugin, um jogo com lição própria e o central: os testes novos a reusam.
- **O `registrar` não duplica** (`golem.py:459-480`), e o `ler_registro` só aceita linhas de três
  células (`golem.py:420-436`).
- **O `golem.toml` do central** nasce só com o comentário do topo (`golem.py:370-373`, `:448-449`).
- **O estudo do central** (na pasta de notas da GER, `estudo-golem-central.md`, perguntas 2 e 3):
  o geral em `licoes/` no central, "no mesmo formato e com a mesma régua"; "toda lição nasce no
  jogo"; o registro marca o cliente com `cliente = "<nome>"`, e "nele, nada sobe ao central".

## Padrões a seguir

- **A leitura de um acervo** segue a de hoje: o índice, a conferência da lição fora dele e a
  degradação para o Markdown (`licoes_relevantes.py:228-347`), agora com a pasta como parâmetro.
- **O comando novo do `golem.py`** segue o `registrar`: confere tudo antes de escrever, sai com
  `ERRO` e nada escrito, e relata uma linha por arquivo (`golem.py:459-487`).
- **O aviso novo da régua** segue os das refs e do teto (`regua.py:377-387`).
- **Os testes** seguem os do central da fase 3 (`test_golem.py`, `test_gancho.py`, sobre a árvore
  `Plugin` do `conftest.py`) e os do índice defasado da fase 4.

## Notas do usuário

- "é configurado uma só vez, é fácil de usar, guarda as lições, guarda o estilo do usuário [...]"
  (o autor do kit, 2026-11-21, decisão 11).
- O exemplo do estudo, sobre o que sobe: "DataStore sem `pcall`" sobe; "o save deste jogo usa a
  chave X" fica (o autor do kit, no estudo do central; `estudo-golem-central.md`, pergunta 2).
- As palavras de 2026-11-22, pela EST, estão em "Objetivo" e em "Decisões".

## Perguntas em aberto

- **A rodada com login** (validation.md, L1), para ver a `iniciar-sdd` e a `licao` numa sessão de
  verdade: pergunta-se na hora do G5, como na fase 3.
- ~~A conferir no G2: como a chave `jogos_para_terceiros` entra no `onde` e no guia (R3).~~
  Conferido no G2: ver o R3, "A leitura".
