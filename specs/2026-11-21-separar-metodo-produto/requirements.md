# Separar o método que usamos do produto que entregamos — Requisitos

Branch `fase-separar-metodo-produto`, cortada de `30b87db` (a `main` em 2026-11-21, com o PR 2 da
MET já mergeado, conferida com `git ls-remote origin refs/heads/main`). Os fatos foram lidos em
`30b87db`, salvo onde se diz outro commit. O nome, a pasta e a branch foram combinados com a GER
(2026-11-21). A fase fica sem número até o autor do kit decidir a ordem, no replanejamento depois
do merge da fase 2.

## Objetivo

O repositório do kit deixa de usar como regra própria o modelo que o usuário copia. O modelo do
`AGENTS.md` vai para `templates/AGENTS.md`, na receita `economico` e com as lacunas `<< >>`. A raiz
do kit ganha o `AGENTS.md` próprio, com as lacunas preenchidas, a receita `completo` num
`golem.toml` do kit e os comandos reais. Uma conferência automática, o conciliador, acusa toda
diferença entre os dois que não esteja numa lista de diferenças permitidas. A instalação passa a
copiar o modelo e a rodar o `aplicar`. O resto do que viaja ao usuário espera a decisão entre o kit
dentro de cada projeto (M1) e o Golem central por plugin (M2) (decisão 5).

**Por quê.** Hoje o mesmo `AGENTS.md` da raiz é a regra do desenvolvimento do kit e o modelo que
o usuário copia. Daí saem três problemas:

- **O kit roda na `economico`.** É a decisão 7, "Econômica no kit" (`docs/plano-produto.md:639-641`).
  O modo completo do desenvolvimento só vale quando vem no prompt de cada fase ("Completo pelo
  prompt"). Uma fase aberta sem essa linha cai na `economico` sem aviso.
- **As lacunas que o kit precisa estão abertas.** São os "Comandos reais" (`AGENTS.md:38-55`) e a
  "Contagem esperada de testes" (`:59`). O próprio arquivo avisa que, sem eles, "as regras 4 e 8
  ficam no ar" (`:40-41`). O comando da suíte do kit vive na memória e nos prompts.
- **A instalação leva o que é só do kit.** Ela manda copiar a `.claude/` inteira, "testes"
  inclusive, e a pasta `docs/` (`README.md:94-99`). A `docs/` tem o `plano-produto.md` do kit.
  Este terceiro problema espera a decisão M1 × M2. A fase só impede que ele piore: sem o R5, a
  instalação levaria também o `AGENTS.md` do kit.

## Escopo

- **R1. O modelo do usuário em `templates/AGENTS.md`.**
  - O conteúdo é o `AGENTS.md` da `main` na hora da implementação (em `30b87db`, já com a regra 10
    do PR 2 da MET), com as lacunas `<< >>` como estão.
  - O bloco "Como o Golem trabalha aqui" é o da `economico`, o mesmo que
    `golem.bloco(golem.configuracao(<pasta sem golem.toml>))` gera.
  - Sai do modelo só a frase que fala do repositório do kit: "O repositório do próprio kit não
    versiona as cópias: quem instala o kit as gera no projeto dele (`README.md` do kit, 'Usando
    com o Codex')." (`AGENTS.md:108-109`). Ela fica na raiz, como diferença permitida (R3).
- **R2. A raiz do kit com a configuração e os comandos dele.**
  - O `golem.toml` na raiz tem a linha `receita = "completo"` e um comentário de uma linha que diz
    que ele é do kit e não viaja.
  - O `golem.py aplicar`, rodado no kit, escreve o bloco da `completo` no `AGENTS.md` da raiz e
    `model: opus` nos dois agentes (`.claude/golem.py:218-235`; a `completo` em `:64-68`).
  - O `AGENTS.md` da raiz fica com as lacunas preenchidas e com o que aponta para algo que o kit
    não tem trocado pelo que ele tem. O texto proposto, aprovado junto com esta spec:
    - **A frase de abertura** (`:4`, "Os trechos entre `<< >>` são do projeto: preencha antes de
      usar."): no kit, "Este é o `AGENTS.md` do kit. O modelo que o usuário copia é o
      `templates/AGENTS.md`, com as lacunas; as diferenças entre os dois estão no conciliador
      (`.claude/tests/test_conciliar.py`)."
    - **O projeto** (`:10`): "Golem SDD: kit de spec-driven development para Claude Code e Codex,
      pensado para desenvolvedores de Roblox iniciantes."
    - **A tabela** (`:14-20`):
      - o código é `.claude/` (skills, agentes, gancho, régua, `golem.py`, instalador do Codex) e
        `templates/`;
      - as specs ficam em `specs/`, com uma pasta por fase;
      - as decisões técnicas, sem `docs/adr/` no kit, estão na seção 8 do `docs/plano-produto.md`;
      - a linha "Cópias para o Codex" (`:20`) fica como está: o kit não versiona as cópias, e a
        frase da `:108-109`, que fica na raiz, já diz isso.
    - **A ordem de leitura** (`:28-32`): o kit não tem `specs/mission.md`, `tech-stack.md` nem
      `roadmap.md`, nem `docs/adr/`. No item 3, a constituição é o `docs/plano-produto.md` (o
      roteiro na seção 7). No item 5, as decisões estão na seção 8 dele.
    - **Os comandos reais** (`:40-54`):
      - setup: nenhum (só a biblioteca padrão; a suíte pede pytest);
      - testes: `python -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs`;
      - a régua: `python .claude/regua.py --conferir`;
      - lint: "não instalado";
      - subir local: "não há: o kit é texto e scripts".
    - **A stack** (`:57`): Python 3.8+ só com a biblioteca padrão (scripts e gancho), `sh` POSIX no
      gancho, Markdown nas skills, e pytest só na suíte do kit.
    - **A contagem esperada de testes** (`:59`): vive no `validation.md` de cada fase (a contagem
      da fase anterior mais os testes novos).
    - **As convenções:**
      - `:84`: commits e PRs em português; merge por merge commit (`git log --merges`: todo PR
        entrou assim, do `9f6e33b` ao `30b87db`);
      - `:92`: "nenhum além dos três acima". O `docs/operacao-das-conversas.md:101` continua com a
        lacuna, porque é uma cópia só e serve ao modelo; a frase "mudou aqui, muda lá"
        (`AGENTS.md:94-95`) vale para o modelo;
      - `:110`: nenhum nome de cliente, de outro projeto ou de pessoa entra no kit, fora do
        crédito (a linha de crédito, o `LICENSE` e a seção "Licença e crédito" do `README.md`).
    - **Os segredos** (`:143`): o kit não tem segredo. O `golem.local.toml`, com o caminho do
      Python da máquina, fica fora do git (`.gitignore`).
    - **A regra 3** ("algo fora de `specs/tech-stack.md`"): no kit, "algo fora da linha **Stack**
      dos 'Comandos reais'". O agente `revisor`, que é do produto, continua citando o
      `specs/tech-stack.md` (`.claude/agents/revisor.md:31`). No kit, ele não acha o arquivo e cai
      na regra 3 do `AGENTS.md`, que aponta a linha **Stack**. É uma diferença conhecida, e o
      agente não muda.
    - **As regras do projeto** (`:230`): nenhuma por ora.
- **R3. O conciliador, um teste da suíte do kit.**
  - Fica em `.claude/tests/test_conciliar.py`, com a linha de crédito (`test_credito.py:22-38`, a
    lista fechada). A lista de diferenças permitidas fica no mesmo arquivo, numa constante
    `PERMITIDAS` de trios (o trecho do modelo, o trecho do kit, o motivo).
  - Ele lê os dois arquivos em LF, como o `golem._ler` (`.claude/golem.py:211-215`). Tira dos
    dois lados o bloco entre `<!-- golem:inicio -->` e `<!-- golem:fim -->`, porque o bloco é
    gerado pelo `aplicar` de cada configuração e conferido pelo `test_golem.py`. Depois troca no
    modelo cada trecho permitido pelo do kit e compara o resultado com o `AGENTS.md` da raiz.
  - Ele falha quando:
    - sobra diferença: a mensagem traz o diff unificado (`difflib`, biblioteca padrão) e diz o que
      fazer. A MET decide: leva a mudança ao modelo (`templates/AGENTS.md`) ou a acrescenta a
      `PERMITIDAS`, com o motivo;
    - um trecho permitido não aparece exatamente uma vez no modelo, porque a permissão envelheceu
      ou ficou ambígua;
    - uma permitida não tem motivo.
  - Outro teste, no mesmo arquivo, confere que o bloco do modelo é o da `economico`, gerado pelo
    `golem.bloco`.
  - A conferência roda em toda suíte. A suíte está nos comandos reais do kit (R2) e no
    `validation.md` de cada fase. A skill `validar-fase`, que é do produto, não muda.
  - **Fora do kit, ele se pula.** Até a decisão M1 × M2, o `test_conciliar.py` viaja na
    `.claude/tests/`, e o `README.md` oferece a suíte ao usuário (`:83`, `:268`). O teste que
    falhasse no projeto dele seria lido como "o kit está quebrado" (sugestão da EST, pela GER,
    2026-11-21). A condição é exata:
    - o módulo inteiro se pula (`pytest.skip(..., allow_module_level=True)`) quando o `AGENTS.md`
      da raiz não traz a frase de abertura do kit (R2, "Este é o `AGENTS.md` do kit."). O motivo
      diz: "não é o repositório do kit: o conciliador só roda lá";
    - no kit, a frase existe, e ele nunca se pula. Se alguém apagar a frase no kit, os 3 pulados
      aparecem no `-rs`, e a contagem do `validation.md` ("0 pulados") acusa (regra 8).
- **R4. A instalação roda o `aplicar`.**
  - O passo 4 de "Instalar num projeto" (`README.md:125-137`) ganha, junto dos comandos da régua,
    o `python3 .claude/golem.py aplicar`. Ele volta os agentes ao modelo da receita do usuário:
    sem `golem.toml`, a `economico`, com `model: sonnet` no revisor (`.claude/golem.py:59-63`). O
    passo entra no 4, e não num número novo, para não mudar as referências aos passos
    (`README.md:135`, "faltou o passo 3"; `:175`, "os passos 1 a 5").
  - **Sem Python**, o `aplicar` não roda (`configurar/SKILL.md:112-119`). Nesse caso, o mesmo passo
    diz para trocar à mão a linha `model:` do `.claude/agents/revisor.md` para `model: sonnet`, a
    linha que o `aplicar` escreveria na `economico`.
  - **Depois do `aplicar`, o `git add .claude/agents`.** O passo 3 já fez o `git add .claude`
    (`README.md:115`). Sem o segundo `add`, a troca para `sonnet` fica fora do stage, e um commit
    comum grava o revisor em `opus`. O passo 4 já faz o mesmo com o índice (`:136-137`).
  - O passo 7 ("Opcional: configure o Golem", `:151-154`) continua opcional, para quem quer mudar
    a receita.
- **R5. A instalação copia o modelo, e não o `AGENTS.md` do kit (mínimo).** No passo 1 do
  `README.md` (`:99`), o `AGENTS.md` passa a ser "o `templates/AGENTS.md`, copiado como
  `AGENTS.md`". Sem isso, quem instala leva o `AGENTS.md` do kit, com a `completo` e as lacunas
  preenchidas para o kit. É a única mudança na lista do que se copia. O resto da lista continua
  como hoje até a decisão M1 × M2 (ver "Decisões" e "Fora de escopo"). Os arquivos que já viajam
  mudam também: o revisor em `opus` (R2), o `test_conciliar.py` (R3) e o `test_credito.py`.
- **R6. Quem muda, varre.**
  - O `copia_do_kit` passa a copiar o `templates/AGENTS.md` como `AGENTS.md`, o que o usuário
    recebe (`conftest.py:156`, e a docstring em `:150-151`). Se a `templates/AGENTS.md` não
    existir, ele copia o `AGENTS.md` da raiz, como hoje. É o caso do projeto do usuário, em que a
    `templates/` é opcional (`README.md:158`) e o `AGENTS.md` da raiz já é o modelo. Sem esse
    recuo, 9 testes que viajam e usam o `copia_do_kit` quebrariam lá com `FileNotFoundError`:
    5 do `test_golem.py`, 2 do `test_codex.py` e 2 do `test_regua.py` (o revisor, na terceira
    rodada). Isso vai no G1: sem a troca, o `test_segunda_rodada_do_aplicar_nao_muda_nada`
    (`test_golem.py:170-173`) quebra assim que a raiz ganha o bloco da `completo`.
  - Os textos que dizem que o `AGENTS.md` do kit é o que o usuário copia: `test_golem.py:202-203`
    (o "No kit, sem golem.toml, é a economico"). O `test_credito.py:4-5` ("A instalação copia a
    pasta `.claude/` inteira") continua certo até a decisão M1 × M2 e não muda.
  - Uma busca nos `.md` e `.py` do kit, na implementação, acha o resto (o comando está no
    `plan.md`, G3). Fica como está, porque é parte do mapa, que espera a decisão M1 × M2: a linha da
    `templates/` no "Mapa das pastas" (`README.md:269`), sem o `AGENTS.md` novo.
  - O roteiro de teste da GER (`roteiro-teste-golem.md`, passo 3) está fora do repositório. A GER
    o refaz depois do merge desta fase (o recado dela, 2026-11-21).
- **R7. As decisões no `docs/plano-produto.md`.** A seção 8 ganha uma decisão, numerada depois
  das que existirem na hora, com as palavras do autor do kit desta fase. Ela diz que a decisão 7,
  "Econômica no kit", e a exceção "Completo pelo prompt" (a decisão 8, na branch da fase 2) deixam
  de valer: o kit passa a rodar na `completo` pelo próprio `golem.toml`. **Só depois do merge da
  fase 2**, que é dona do arquivo até lá. A linha desta fase no roteiro (seção 7) entra quando a
  GER refizer o roteiro.

## Fora de escopo

- **O que mais viaja ao usuário, até a decisão M1 × M2** (o kit dentro de cada projeto, ou o Golem
  central por plugin). Espera a decisão, para não ser refeito:
  - a lista completa do que viaja: a `.claude/` sem os testes; da `docs/`, só a operação, o guia
    de configuração, os guias de área e as lições; a `templates/` deixando de ser opcional;
  - o "Mapa das pastas" e os "Requisitos" do `README.md`;
  - a `iniciar-sdd` copiando o `templates/AGENTS.md` e rodando o `aplicar`.

  Até lá, a instalação copia a `.claude/` inteira e a `docs/` como hoje, inclusive o
  `test_conciliar.py` e o `docs/plano-produto.md`. Quem rodar a suíte do kit no próprio projeto vê
  os 3 testes do conciliador pulados, com o motivo (R3), e os do `copia_do_kit` passando pelo recuo
  ao `AGENTS.md` da raiz (R6). Nenhum falha por causa da separação.
- **O zip e o plugin.** Não existem ainda: a primeira release é ideia para o fim da fase 4, na
  ideação da EST (fora do repositório). A lista do que viaja espera a decisão M1 × M2 (acima).
- **A escolha fina das lições que o kit entrega.** Continua na fase 4 (decisão 6,
  `docs/plano-produto.md:629-633`). As lições de hoje viajam como exemplo (o índice tem
  `total: 9`), inclusive a do PR 2 da MET, `num-produto-a-falha-vista-vem-do-uso`, embora seja do
  kit. O índice viaja como hoje, e o passo 4 do `README.md` o regera com as lições do projeto.
- **As lacunas do `docs/operacao-das-conversas.md`** (`:76`, `:101`, `:220`, `:313`, `:328`). O
  arquivo tem uma cópia só: o kit o usa com as lacunas abertas, e o conciliador não o compara.
- **A `validar-fase`.** É do produto e não ganha passo do kit (R3).
- **Mudar o `golem.py` ou as receitas.** O `aplicar` de hoje já faz o que a fase precisa.
- **O roteiro (seção 7) e o número da fase nele.** São da GER e do `replanejar-roadmap`, depois do
  merge da fase 2.

## Decisões

Todas são do autor do kit, de 2026-11-21. As cinco numeradas vieram por caixa de pergunta nesta
conversa, com a recomendada primeiro.

- **Separar já.** À pergunta "Como separar o método que usamos do produto que entregamos?"
  (separar já × separar na fase 4 × estudar com o central): "Separar já (Recomendado)". Depois da
  correção da EST e dos dois casos novos: "Ok, mantém a separação". As duas falas estão na ideação
  da EST, na seção "Separar o método" (fora do repositório).
- **Conferência automática.** À pergunta "O conciliador vira uma conferência automática ou um
  agente novo?": "Conferência automática". Descartado: um agente novo, que custa uma conversa por
  rodada e só lê.
- **1. "Fonte só, raiz à mão (Recomendado)".** O modelo é a fonte, e a raiz se edita à mão. O
  conciliador só confere e não escreve. Descartado: a raiz gerada do modelo por um `--gerar`, que
  é mais rígida e maior, e em que a edição à mão na raiz se perde na rodada seguinte.
- **2. "Teste da suíte do kit (Recomendado)".** O conciliador é o
  `.claude/tests/test_conciliar.py`, com a lista no mesmo arquivo. Descartado: um script
  `conciliar --conferir` numa pasta nova, só do kit, que pede um arquivo e uma pasta a mais e uma
  linha a mais em cada `validation.md`.
  - **Correção do cartão:** ele disse "hoje toda a `.claude/` viaja, menos os testes". Está
    errado: hoje os testes viajam também (`README.md:95-96`). A decisão 4 os tiraria, mas a 5 a
    suspendeu. Por isso o `test_conciliar.py` viaja até a decisão M1 × M2 e se pula fora do kit
    (R3). A escolha continua de pé.
- **3. "Instalar roda o aplicar (Recomendado)".** Descartado: os agentes do kit em `sonnet` e o
  Opus pelo prompt, que mantém parte da exceção que esta fase quer tirar. O risco aceito: quem
  pular o passo fica com o revisor no Opus até rodar o `aplicar` ou o `configurar`. Quem não tem
  Python troca a linha à mão (R4).
- **4. "Lista no README (Recomendado)".** Descartado: separar as lições já (as de exemplo em
  `templates/licoes/`), que faz a fase crescer e tira da fase 4 a escolha das lições. A decisão 6
  continua na fase 4.
- **5. "Mínimas agora (Recomendado)".** A GER avisou que o autor do kit vai escolher entre o Golem
  central por plugin (M2) e o kit dentro de cada projeto (M1), e que as decisões 3 e 4 dizem o que
  viaja ao usuário. À pergunta sobre o que essas duas partes fazem: "Mínimas agora (Recomendado)".
  Entram só as duas mudanças que a separação obriga no `README.md`: copiar o `templates/AGENTS.md`
  (R5) e rodar o `aplicar` no passo 4 (R4). O resto espera a decisão M1 × M2. Descartado: esperar
  a decisão com a fase inteira. Como a separação, sem essas linhas, quebra a instalação de hoje,
  isso pararia a implementação toda.
  - **O que muda nas decisões de antes:** a decisão 3 fica só no `README.md`, e a `iniciar-sdd`
    espera. A decisão 4 fica suspensa: a lista do que viaja não entra agora.
- **Decisões do agente, dentro destas:**
  - o modelo em `templates/AGENTS.md`, ao lado dos outros modelos, fora de `templates/roblox/`
    (que é da fase 2);
  - a `PERMITIDAS` como trios de trechos, e não como seções inteiras, para acusar também a
    mudança dentro de uma seção que tem lacuna;
  - o comando do `aplicar` dentro do passo 4 do `README.md`, e não num passo novo (R4);
  - o conciliador se pula fora do kit, e o `copia_do_kit` recua ao `AGENTS.md` da raiz sem
    `templates/` (R3, R6). A sugestão da primeira parte veio da EST, pela GER, como detalhe de
    implementação.

## Contexto

- **O `aplicar` escreve nos agentes que viajam.** O `golem.esperado` escreve o `model:` em
  `.claude/agents/revisor.md` e `validador.md` (`.claude/golem.py:221-230`). Hoje eles estão em
  `sonnet` e `opus` (`revisor.md:5`, `validador.md:5`). O teste
  `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml` (`test_golem.py:201-206`) confere o disco
  contra o `golem.toml` da raiz. Com o `golem.toml` do kit, ele passa a conferir a `completo`.
- **A `completo` muda também o desenvolvimento do kit** (`.claude/golem.py:64-68`):
  - o gancho entrega até 4 lições novas por ação, e não 2;
  - o "parar a cada parte" passa a `nunca`;
  - as conversas passam a "papéis".

  Os testes do gancho não mudam com o teto. Os do `acervo` usam uma árvore própria, e os do teto
  escrevem o `golem.toml` deles (`test_gancho.py:66`, `:93`). O
  `test_licoes_de_exemplo_chegam_na_acao_certa` (`test_gancho.py:294-310`) roda sobre a raiz do kit
  e passa a ler o teto 4, mas só uma lição casa com cada ação, porque a seleção é por gatilho
  (`licoes_relevantes.py:274-281`). Isso se reconfere quando a fase 2 somar a lição dela.
- **Os testes que copiam o kit.** O `copia_do_kit` (`conftest.py:148-157`) copia a `.claude/` sem
  os testes, as lições e o `AGENTS.md` da raiz, sem o `golem.toml`. Os testes do `aplicar` que o
  usam escrevem o `golem.toml` deles (`test_golem.py:113-177`). O
  `test_segunda_rodada_do_aplicar_nao_muda_nada` (`:170-173`) espera que a primeira rodada com a
  `completo` escreva o `AGENTS.md`. Por isso a cópia tem de partir do modelo, na `economico` (R6).
- **O crédito é uma lista fechada.** Arquivo novo do kit entra na `ARQUIVOS_DO_KIT`
  (`test_credito.py:7-10`, `:22-38`).
- **O que o `<<` acha no `AGENTS.md`** (`grep -n "<<" AGENTS.md`): a frase de abertura (`:4`) e as
  lacunas em `:10`, `:14`, `:40`, `:45`, `:48`, `:51`, `:54`, `:57`, `:59`, `:84`, `:92`, `:110`,
  `:143` e `:230`.
- **A suíte na `30b87db`:** `123 passed in 61.45s`, sem pulados, com o comando dos comandos reais
  (R2), rodado nesta conversa. O índice tem `total: 9`.
- **Os outros que tocam os mesmos arquivos:**
  - o PR 2 da MET (PR 5) já está na `main` (`30b87db`). Ele mudou a regra 10 do `AGENTS.md`, a
    `licao`, a `iniciar-conversa`, a `diagnostico`, a `adr`, o `templates/adr.md` e o índice
    (`git diff --stat ee0e661 30b87db`). Não tocou a `validar-fase` nem a `iniciar-sdd`;
  - a fase 2 (`origin/fase-2-roblox`, `d9780a2`) muda o `docs/plano-produto.md`, o gancho e o
    `test_gancho.py`. No G5, ela cria `templates/roblox/` e `docs/guia-roblox.md`, varre o
    `README.md` (`specs/2026-11-13-fase-2-roblox/plan.md:187-204`, na branch dela) e soma uma
    lição ao índice.

## Padrões a seguir

- **O conciliador** segue o `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml`
  (`test_golem.py:201-206`): compara o que se espera com o disco e diz na mensagem o que fazer. A
  saída de diferença segue o `--conferir` da régua: dizer o que diverge e o que corrige
  (`.claude/regua.py:325-336`).
- **A leitura em LF** segue o `golem._ler` (`.claude/golem.py:211-215`).
- **A linha de crédito** segue o `test_golem.py:1`.

## Notas do usuário

- "nós estamos usando a ferramenta para desenvolver a ferramenta. Talvez seja muito importante nós
  criarmos essa separação, porque se nós misturarmos o método que nós estamos utilizando agora com
  o método que estamos desenvolvendo, vira essa confusão que você está mostrando." (o autor do
  kit, 2026-11-21, na EST).
- "vale a criação de um agente de desenvolvimento especial para a gente, que seria o conciliador
  ou algo desse tipo, [...] que prestaria atenção nessa correspondência entre os dois projetos
  separados" (o autor do kit, 2026-11-21, na EST). O "agente" virou conferência automática por
  decisão dele (acima).

## Perguntas em aberto

- **A ordem:** a implementação parte da `main` com o PR 2 da MET (condição cumprida em `30b87db`)
  e espera a ordem do autor do kit nesta conversa. O R7 espera o merge da fase 2. Se a fase 2 não
  tiver mergeado quando o resto estiver pronto, a GER decide se o R7 vai num PR à parte.
- **O `README.md`:** a fase 2 varre o mesmo arquivo no G5. Quem mergear depois resolve o conflito,
  com a GER avisada.
- **Os agentes e o `test_golem.py`:** o G4 da fase 2 (`origin/fase-2-roblox`, `8e032bd`, pela GER)
  mudou a linha `tools:` do `revisor.md` e do `validador.md` e fez o `test_golem.py` ler o
  `tools:` do próprio arquivo. O G1 desta fase mexe nos mesmos três arquivos (o `model:` e o
  `copia_do_kit`). Se a fase 2 mergear antes, a implementação traz a `main` antes do G1. Se mergear
  depois, quem mergear por último traz a `main`, resolve o conflito e refaz a prova inteira.
- **O número da fase:** entra quando o autor do kit decidir a ordem, no replanejamento.
