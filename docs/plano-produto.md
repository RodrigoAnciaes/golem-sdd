# Plano de produto do Golem

Rascunho de 2026-11-12, base `c880a17`. É um plano: nada aqui mudou o kit. Cada decisão volta ao
autor do kit num cartão, uma de cada vez.

**Para quem é a primeira versão.** O primeiro usuário programa em Luau no Roblox Studio e usa pouco
a IA, só para ajudar no código. Ele quer reaproveitar o que já escreveu e manter o próprio estilo.
Não quer que a IA faça coisas grandes por ele. Gostou de quatro peças: a spec com entrevista, as
lições que voltam, os índices em que se busca e os papéis (gerente, revisor, validador). Ele usa o
**plano Pro**, então o padrão tem de ser barato e ter espaço para crescer.

**Os três critérios, nesta ordem:** fácil para quem não está acostumado com IA; customizável,
sobretudo no gasto de tokens; integração fácil com o Roblox Studio.

**Como ler os números.** Os tamanhos estão em **bytes** (`wc -c`); em caracteres, ficam de 2% a
3% abaixo, por causa dos acentos. Os tokens são estimados a cerca de 3,8 bytes por token (uns 3,7
caracteres) em português; o número exato depende do tokenizador. O custo do revisor e do validador
foi **medido**, não estimado (seção 1.2).

---

## 1. Diagnóstico: o kit hoje

### 1.1 O que ele oferece

| Peça | O que faz | Onde |
|---|---|---|
| **Spec com entrevista** | antes de escrever, uma rodada de perguntas sobre escopo, decisões e contexto; depois `requirements.md`, `plan.md` e `validation.md`, aprovados pelo usuário. Há também um formato curto para fase pequena | `spec-de-fase`, `references/entrevista.md`, regra 1 do `AGENTS.md` |
| **Lições que voltam** | cada armadilha vira um arquivo em `docs/licoes/`. Um gancho roda antes de cada edição e de cada comando (`.claude/settings.json:6` e `:17`) e injeta o "Como perceber" das lições daquela ação. Entrega no máximo 4 lições novas por ação (`TETO = 4`, `.claude/hooks/licoes_relevantes.py:59`), cada uma uma vez por agente, por sessão | `.claude/hooks/` |
| **Índice em que se busca** | `.claude/indice/licoes.yaml`, gerado pela régua a partir do frontmatter das lições e conferido por ela (`--conferir`). É o único índice. A `iniciar-conversa` o busca por `grep` (`iniciar-conversa/SKILL.md:71-72`); a `implementar-fase` manda procurar nele sem dizer como (`implementar-fase/SKILL.md:23`) | `.claude/regua.py` |
| **Revisor e validador** | dois subagentes que só leem. O revisor confere o diff contra a spec e as regras; o validador roda os critérios e faz mutação numa cópia descartável. Os dois rodam **a cada grupo** do plano (regra 11, `AGENTS.md:176`) | `.claude/agents/` |
| **Guardião** | o revisor de novo, sobre o diff inteiro do PR | regra 11 |
| **Papéis de conversa** | gerente (GER), estratégia (EST), método (MET), guardião e frentes, com PEDIDO → LIBERADO, níveis de autonomia, o fecho de quatro linhas e o cartão de decisão | `docs/operacao-das-conversas.md`, `sessao-gerente` |
| **Codex** | um instalador gera as cópias que o Codex lê (`.agents/skills/`, `.codex/`) a partir de `.claude/` | `.claude/instalar_codex.py` |

### 1.2 Quanto cada peça custa

**O que entra em toda conversa, a cada turno** (vai para o cache depois do primeiro turno):

| Peça | Tamanho | Tokens (estim.) |
|---|---|---|
| `AGENTS.md` (o `CLAUDE.md` o importa inteiro) | 12.987 bytes | ~3,4 mil |
| descrições das 12 skills (só o `description` entra antes de a skill ser chamada) | 4.520 bytes | ~1,2 mil |
| **total fixo** | | **~4,6 mil** |

**O que entra quando se usa:**

| Peça | Tamanho | Tokens (estim.) |
|---|---|---|
| `spec-de-fase` + entrevista + validação | 8.711 bytes | ~2,3 mil, uma vez por fase |
| `implementar-fase` | 5.119 bytes | ~1,3 mil |
| `docs/operacao-das-conversas.md` (o fecho e o cartão moram nele, e seis skills mandam abri-lo) | 17.765 bytes | ~4,7 mil |
| `sessao-gerente` + referência | 13.704 bytes | ~3,6 mil, mais a leitura do git e do GitHub a cada rodada |
| gancho, por ação | até 4 lições × ~550 bytes | até ~600, só com lição nova |
| gancho **quebrado**, por ação | aviso de 340 bytes | ~90 **em toda ação** |
| suporte ao Codex | nada em tempo de uso | custa manutenção (o instalador e 12 mil caracteres de teste) |

**O revisor e o validador são o maior custo medido.** Medi todas as transcrições de subagente
guardadas nesta máquina (`~/.claude/projects/*/*/subagents/`). 91% das rodadas vêm de um mesmo
grupo de pastas (o mesmo prefixo de caminho), que é um projeto grande. Os subagentes de tipo próprio entram pelo tipo; os `general-purpose` entram pela
descrição ("revis" ou "guardi" para o revisor, "valida" para o validador). As 48 descrições com
as duas palavras ficaram de fora. Todos os números são medianas por rodada:

| Subagente | Rodadas (no Opus) | Chamadas | Entrada nova | Cache relido | Saída | Pico de contexto |
|---|---|---|---|---|---|---|
| revisor | 500 (482) | 26 | ~127 mil | ~2,8 milhões | ~7 mil | ~140 mil |
| validador | 448 (427) | 26 | ~107 mil | ~2,6 milhões | ~7 mil | ~132 mil |

Somando as duas medianas, cada grupo do plano gasta da ordem de **230 mil tokens de entrada nova
e 5,4 milhões de cache relido** só com os dois subagentes. Uma fase de 3 grupos, com o guardião,
roda 7 subagentes.

**As ressalvas:**
- O projeto medido é grande, com specs longas. Num projeto Roblox pequeno, o contexto deve ser
  menor.
- A conversa principal não foi medida. Ela também relê o cache a cada turno, então "o maior"
  vale entre as peças medidas.
- A Anthropic não publica quanto o cache relido pesa no limite do plano (a conferir).

**Várias conversas multiplicam o custo fixo.** Cada papel é uma sessão inteira, com o próprio
histórico. Para uma pessoa no Pro, o natural é uma conversa só, e o próprio README já diz que ela
basta (`README.md:228`).

**O que o plano Pro impõe.** O Pro tem um limite por janela de cinco horas e um limite semanal, e
o Claude e o Claude Code dividem os dois ([artigo de ajuda](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)).
O limite não é publicado em tokens. A conferir: quais modelos o Pro libera no Claude Code e quanto
cada um pesa.

### 1.3 O que atrapalha os três critérios

**Fácil para quem não está acostumado com IA:**
- **A instalação tem 6 passos à mão** (copiar pastas, juntar o `settings.json`, o `.gitattributes`
  e o `.gitignore`, gerar o índice e testar o gancho), mais 3 passos para o Codex. Ela exige
  **Python 3.8+ e o Git Bash no Windows** (`README.md:74` e `:83`). Quem programa Roblox
  costuma não ter Python.
- **A prova veio na sessão de análise de 2026-11-12.** A máquina não tinha Python no PATH, e o
  gancho falhou em **todas** as ações (`gancho.sh:99`). Cada falha mostrou um aviso ao usuário e
  pôs ~90 tokens no contexto. O aviso está certo; o problema é repeti-lo a cada ação, sem dizer
  como resolver em uma linha.
- **O vocabulário é o de uma equipe de conversas:** GER, EST, MET, frentes, PEDIDO/LIBERADO,
  níveis 1 a 3, decisões P/M/G (a G confirmada num segundo turno), o fecho de quatro itens. Tudo
  isso vale para quem toca várias entregas ao mesmo tempo. Para uma pessoa, é ruído.
- **O `AGENTS.md` chega com lacunas `<< >>`** (o projeto, os comandos reais, a stack). Sem os
  comandos reais, as regras 4 e 8 ficam no ar, e nada conduz o usuário a preenchê-las.
- **O fluxo supõe GitHub e PR** (`gh`, merge por PR). Para um projeto local, ele funciona, mas o
  caminho não está descrito para o iniciante.

**Customizável e barato:**
- **Não existe um botão de custo.** Revisor e validador por grupo, mutação, guardião, teto do
  gancho e modelos são fixos no texto das regras, das skills e do script do gancho. Mudar exige
  editar vários arquivos.
- **Os agentes não fixam modelo.** Não têm `model:` no frontmatter, então herdam o da conversa. O
  Claude Code aceita `model:` (sonnet, opus, haiku, `inherit` ou o id) e `effort:` por agente, e
  a ordem de precedência é: a chamada, depois o frontmatter, depois `CLAUDE_CODE_SUBAGENT_MODEL`,
  depois o modelo principal ([subagentes](https://code.claude.com/docs/en/sub-agents.md)).
- **A busca no índice não é uniforme.** A `implementar-fase` não diz como procurar, e o agente
  pode ler o índice inteiro. Com 2 lições, isso não pesa; com 100, são ~14 mil tokens por leitura.

**O estilo dele e passos pequenos:**
- **O kit hoje empurra para o contrário do que o primeiro usuário quer.** "O agente segue grupo a
  grupo sem pedir licença" (`AGENTS.md:169`) e "Fim de grupo não é fim de turno"
  (`implementar-fase/SKILL.md:39` e `docs/operacao-das-conversas.md:156`). Para quem quer aprovar
  passos pequenos, isso tem de virar opção.
- **O reaproveitamento existe só como frase.** Há a regra "Reuse o que existe antes de criar"
  (`AGENTS.md:162`), os "padrões a seguir" da spec (`spec-de-fase/SKILL.md:74`) e a pergunta
  "reaproveita algo existente?" da entrevista (`entrevista.md:17`). Nada **aprende** o estilo do
  código que já existe, e nada **lista** o que pode ser reaproveitado.

**Roblox:**
- Os exemplos, os gatilhos das lições e os comandos são de pytest e npm. O gancho conhece
  `src/`, `docker` e `curl`, e não conhece `rojo`, `.luau` nem as ferramentas do Studio.
- Sem Rojo ou Argon, o código vive dentro do place, fora do git. Aí o revisor não tem diff, e o
  gancho não vê a edição, que passa por outra ferramenta, com outra entrada.

---

## 2. As melhorias, em ordem de valor e de custo

Valor para o primeiro usuário: **A** (alto), **M** (médio), **B** (baixo). Custo de fazer:
**P** (cabe num dia), **M** (alguns dias), **G** (uma semana ou mais). A ordem é por valor e,
dentro do mesmo valor, pelo menor custo.

| # | Melhoria | Critério | Valor | Custo |
|---|---|---|---|---|
| 1 | **Aprovação passo a passo:** a implementação para ao fim de cada grupo e mostra o que mudou; os grupos são pequenos (um arquivo ou uma função) | estilo | A | P |
| 2 | **Gancho que falha uma vez só**, em palavras simples, com o conserto em uma linha; ele também pode ser desligado, e aí as lições se buscam sob demanda | fácil, custo | A | P |
| 3 | **Modo econômico com um interruptor** (`modo = "economico"`): uma conversa, revisor uma vez por fase e no Sonnet, validador só com os comandos do `validation.md`, sem mutação nem guardião | custo | A | M |
| 4 | **Pacote Roblox mínimo:** os comandos reais de um projeto Rojo, os gatilhos `.luau`/`rojo`/`selene`/`stylua`, um `tech-stack` modelo, critérios com playtest passo a passo e o uso do Studio MCP | Roblox | A | M |
| 5 | **Aprender o estilo:** uma skill lê os programas que **ele escolher** e propõe as regras do estilo dele, cada uma com um exemplo `arquivo:linha` do próprio código; ele aprova uma a uma | estilo | A | M |
| 6 | **Catálogo do que reaproveitar:** uma linha por módulo dele (o nome, o caminho, o que faz, a interface). A entrevista e o plano consultam o catálogo antes de criar algo novo | estilo | A | M |
| 7 | **Instalação como plugin do Claude Code**, com uma skill de diagnóstico e o `AGENTS.md` preenchido por entrevista | fácil | A | M |
| 8 | **Medidor de custo:** um script local que lê as transcrições e diz quanto cada papel gastou na semana (o desta análise, arrumado) | custo | M | P |
| 9 | **Modo simples de documentação:** um guia "primeiro dia" de uma página; os papéis de várias conversas e o vocabulário de equipe só no modo completo | fácil, custo | M | M |
| 10 | **Configuração completa:** o modelo e o esforço de cada papel, quais papéis rodam e o teto do gancho | custo | M | M |
| 11 | **Infraestrutura de produto:** versões, notas de versão, o comando de atualizar, a página e a licença decidida | produto | M | M |
| 12 | **Busca uniforme no índice:** a `implementar-fase` usa o mesmo `grep` da `iniciar-conversa` | custo | B agora, M com o acervo maior | P |
| 13 | **Configuração também no Codex** (o instalador passa a ler o mesmo arquivo) | custo | B | M |

**O que fica de fora de propósito:** reescrever o kit em inglês, uma interface gráfica, um
servidor próprio e cobrança. Nada disso ajuda o primeiro usuário.

---

## 3. Esboço da configuração de custo

**Um arquivo, um interruptor.** A configuração mora num `golem.toml` na raiz do projeto. Para
trocar de modo, ele muda uma linha, roda `golem aplicar` e abre uma conversa nova. Na fase 1,
isso é um script (`python .claude/golem.py aplicar`) e uma skill `modo` ("mude para o modo
econômico"), que faz as duas primeiras coisas por ele. Com o plugin da fase 4, a skill vira
`/golem:modo`.

```toml
# golem.toml: quanto o Golem gasta.
# Mude "modo", rode "golem aplicar" (ou peça à skill modo) e abra uma conversa nova.
modo = "economico"            # economico | completo

[economico]                   # o padrão, pensado para o plano Pro
conversas  = "uma"            # uma | papeis (GER, EST, MET)
aprovacao  = "por_grupo"      # por_grupo: para ao fim de cada grupo | por_fase: segue sozinho
revisor    = "por_fase"       # por_grupo | por_fase
validador  = "comandos"       # mutacao: o subagente | comandos: a conversa roda o validation.md
guardiao   = false
modelo_revisor   = "sonnet"   # sonnet | opus | haiku | inherit
modelo_validador = "inherit"
gancho_ligado    = true
gancho_teto      = 2          # lições novas por ação (hoje fixo em 4)

[completo]                    # o fluxo de hoje, para planos maiores
conversas  = "papeis"
aprovacao  = "por_fase"
revisor    = "por_grupo"
validador  = "mutacao"
guardiao   = true
modelo_revisor   = "opus"
modelo_validador = "opus"
gancho_ligado    = true
gancho_teto      = 4
```

**Por que cada chave existe.** As de revisor, validador, guardião, conversas e modelos atacam o
maior custo medido (seção 1.2). A de aprovação é o pedido do primeiro usuário. O `gancho_ligado`
resolve a máquina sem Python. O `gancho_teto` custa pouco (o gancho injeta no máximo ~600 tokens
por ação), mas é o que controla quanto contexto o gancho injeta, um dos itens do critério
"customizável", e é uma linha. O gancho continua
rodando antes de comandos nos dois modos: as duas lições do kit disparam por comando, e é a
conversa que roda os comandos do `validation.md` no modo econômico.

**Como a configuração chega ao agente, sem custo novo de leitura.** O `golem aplicar`, no molde do
`instalar_codex.py`, lê o arquivo e gera três coisas:
1. o `model:` e o `effort:` no frontmatter de `.claude/agents/*.md`, que o Claude Code respeita;
2. no `.claude/settings.json`, a chamada do gancho com o teto (o `licoes_relevantes.py` passa a
   ler o teto de uma variável, em vez do `TETO = 4` fixo) ou sem o gancho;
3. um bloco curto e **gerado** no `AGENTS.md`, "Modo atual", que as regras 1, 10 e 11 passam a
   citar. Como o `AGENTS.md` já entra em todo turno, o agente sabe o modo sem abrir arquivo novo.

Um `--conferir`, como o da régua, acusa quando o `golem.toml` e o que foi gerado divergem.

**A diferença esperada, em ordem de grandeza.** Numa fase de 3 grupos, o modo completo roda 7
subagentes (3 revisores, 3 validadores e o guardião). O econômico roda 1: um revisor no Sonnet
sobre o diff da fase. O validador vira os comandos do `validation.md`, rodados pela própria
conversa com a linha de resumo lida.
- **Se os 7 tivessem o tamanho mediano medido**, o corte no que os subagentes gastam seria de uns
  85%.
- **Mas o revisor do econômico lê o diff da fase inteira.** Com o dobro do tamanho de uma rodada
  mediana, o corte cai para uns 70%.
- **A conta não inclui** os comandos que passam a rodar na conversa principal, nem a diferença de
  preço entre o Opus e o Sonnet.

O número real se mede com o medidor (melhoria 8) no primeiro projeto Roblox.

**O que o modo econômico não corta:** a spec com entrevista, a aprovação do usuário, os critérios
como comando, as lições e a regra de simplicidade. Elas custam pouco e são o que o primeiro
usuário gostou.

**Detalhes a conferir na fase:**
- o `tomllib` só existe no Python 3.11+, e o kit pede 3.8+: ou se sobe o mínimo, ou o arquivo usa
  só `chave = valor`, que se lê com meia dúzia de linhas;
- se o formato de agente do Codex aceita modelo por agente.

---

## 4. Estilo, reaproveitamento e passos pequenos

**Aprender o estilo a partir do código que ele já tem** (melhoria 5):
1. Ele escolhe de 3 a 5 programas que representam o jeito dele. Quem escolhe é ele, não a IA.
2. A skill lê só esses arquivos e propõe regras curtas. Cada regra traz um exemplo `arquivo:linha`
   do código dele, por exemplo: como nomeia, como organiza um ModuleScript, como trata erro, se
   usa `--!strict` e anotação de tipo, a língua dos comentários e o tamanho das funções.
3. Ele aprova, corrige ou recusa **uma regra por vez**. O que for formatação pura vai para o
   `stylua.toml` (o StyLua aplica sem gastar token); o que for lint, para o `selene.toml`.
4. As regras aprovadas vão para o `docs/regras-de-area.md`, no formato que o gancho já entende:
   um bloco `## Regra N — Título` com a linha `areas: codigo`. O gancho entrega cada bloco inteiro,
   uma vez por agente, a quem toca a área (`licoes_relevantes.py`, `regras_para`). Não há peça
   nova.
5. O revisor passa a tratar como achado "importante" o código fora do estilo aprovado.

**Preferir o que já existe** (melhoria 6):
- Um `docs/catalogo.md`: uma linha por módulo reaproveitável, com o caminho no projeto ou na
  pasta de biblioteca pessoal dele, o que faz e a interface.
- Ele se monta com uma skill que lê o cabeçalho dos módulos e propõe as linhas, e ele aprova.
- A entrevista ganha a pergunta "qual programa seu já resolve parte disso?", e cada grupo do
  `plan.md` diz o que reaproveita.
- Criar um módulo novo quando o catálogo tem um parecido exige uma linha de justificativa na spec.
  Sem ela, o revisor acusa.

**Passos pequenos que ele aprova** (melhoria 1):
- `aprovacao = "por_grupo"` faz a implementação parar ao fim de cada grupo, com o diff e uma linha
  do que mudou. O próximo grupo só começa com o ok dele.
- A `spec-de-fase` passa a propor grupos do tamanho de um arquivo ou de uma função.
- O guia recomenda o modo de permissão padrão do Claude Code, que pede licença antes de cada
  edição, e desaconselha o modo automático para ele.

---

## 5. Roblox Studio

**O caminho recomendado: Rojo (ou Argon) e git, com o Studio MCP para jogar e ver o console.**
- **Os arquivos:** o código fica em `src/` como `.luau` (`.server.luau` e `.client.luau` para
  Script e LocalScript), e o `default.project.json` mapeia as pastas para os serviços do place
  (ReplicatedStorage, ServerScriptService, StarterPlayer). Assim, o git, o diff, o revisor e o
  gancho funcionam como num projeto de qualquer linguagem.
- **As ferramentas:** o Rojo ou o Argon para sincronizar, o StyLua para formatar, o Selene para o
  lint e o Wally para pacotes, com as versões fixadas por um gerenciador de ferramentas (Rokit ou
  Aftman). Elas vão para o `tech-stack.md` com a versão; as versões atuais ficam a conferir na
  fase.
- **O Studio MCP oficial**, segundo a [documentação](https://create.roblox.com/docs/studio/mcp):
  - vem embutido no Studio e se liga em Assistant → Manage MCP Servers;
  - conecta, entre outros, o Claude Code e o Codex;
  - traz ferramentas para ler e buscar scripts (`script_read`, `script_grep`), editar
    (`multi_edit`), rodar Luau (`execute_luau`), jogar e parar (`start_stop_play`) e ler o
    console (`get_console_output`);
  - avisa que o cliente pode mudar o place.

**O caminho sem Rojo** (para começar, ou para quem não quer sair do Studio): o código fica no
place, e as specs e as lições ficam numa pasta com git ao lado. O agente edita pelo MCP.
- O revisor perde o diff do git.
- Os dois agentes hoje só têm `Read, Grep, Glob, Bash` no `tools:`, então nem leem o place. Ou
  ganham as ferramentas de leitura do MCP (e o validador, o `execute_luau` e o console), ou, sem
  Rojo, quem revisa e valida é a própria conversa.
- O gancho só lê `file_path` e `command` da entrada da ferramenta. Para ver uma edição pelo MCP,
  o `matcher` tem de incluir o `multi_edit`, e o `licoes_relevantes.py` tem de ler a entrada dele
  (o nome do campo fica a conferir).

Isso funciona, mas é mais fraco. O guia sugere migrar para o Rojo quando o projeto crescer.

**Os testes:**
- **Framework:** o TestEZ, o clássico, ou o Jest Lua, que tem um guia de migração do TestEZ
  ([documentação](https://jsdotlua.github.io/jest-lua)). Qual dos dois ele usa entra no
  `tech-stack.md`.
- **Como rodar, do mais simples ao mais automático:**
  1. **pelo Studio MCP:** o `execute_luau` roda Luau, e o `get_console_output` traz o resumo, sem
     credencial nenhuma. A conferir: se os testes rodam em modo de edição ou precisam de play
     (`start_stop_play`). O "pronto" da fase 2 depende disso;
  2. **pelo `run-in-roblox`, na linha de comando:** a documentação do Jest Lua diz que ele precisa
     do `run-in-roblox` para isso. Se o `run-in-roblox` segue mantido fica a conferir;
  3. **pela API Open Cloud de execução de Luau, sem abrir o Studio** ([documentação](https://create.roblox.com/docs/cloud/reference/features/luau-execution)):
     - pede uma chave de API, que é credencial (regra 5), e quem decide é o usuário;
     - aceita 5 criações de tarefa por minuto;
     - roda tarefas de até 5 minutos.
- **A lição da linha de resumo vale igual:** sem o total de testes, as falhas e os pulados lidos no
  console, não há resultado. O formato exato do resumo do TestEZ e do Jest Lua fica a conferir
  para o gatilho.
- **O que não tem teste automático** (a física, a sensação de um pulo, a interface) entra no
  `validation.md` como passo a passo de playtest, que a regra 4 já aceita.

**O que muda no kit:**
- um modelo de `tech-stack` e de "Comandos reais" para Roblox;
- `.luau` e `default.project.json` no `POR_CAMINHO`;
- `rojo`, `argon`, `selene`, `stylua`, `wally` e `run-in-roblox` no `POR_COMANDO`;
- as ferramentas do MCP no `tools:` do revisor e do validador (só se o caminho sem Rojo ficar);
- duas lições de exemplo do mundo Roblox no lugar das de pytest.

**O kit fora de um repositório JS ou Python.** O método não depende da linguagem. Só o ferramental
do kit (o gancho, a régua e o instalador) é Python. Há três saídas, e não se excluem:
- **(a)** o diagnóstico confere o Python e diz como instalar (no Windows, um comando do `winget`;
  o id exato fica a conferir);
- **(b)** o gancho pode ser desligado (`gancho_ligado = false`), e as lições se buscam sob
  demanda;
- **(c)** a estudar: o Claude Code aceita ganchos escritos em JavaScript num plugin (os "hooks
  modules"), o que tiraria o Python do caminho. Isso só vale para o Claude, e falta conferir se
  esse tipo de gancho pode injetar contexto.

---

## 6. Instalação e primeiro uso

- **Um plugin do Claude Code.** Um plugin junta skills, agentes e ganchos e se instala pelo
  `/plugin`, a partir de um marketplace que pode ser o próprio repositório
  ([plugins](https://code.claude.com/docs/en/plugins.md)). Os comandos exatos ficam a conferir na
  página de instalação.
  - **Custo:** as descrições das skills de um plugin ligado entram em todo turno, **em todo projeto
    em que ele estiver ligado**. Por isso, o guia manda instalar no escopo do projeto.
  - **Nome:** as skills ganham prefixo (`/golem:spec-de-fase`).
  - **O gancho muda o jeito de achar o projeto.** Hoje a raiz sai da posição do próprio arquivo
    (`licoes_relevantes.py:55`, `RAIZ = Path(__file__).resolve().parents[2]`). Dentro de um
    plugin, isso daria a pasta do plugin. Ele passa a achar a raiz pelo `CLAUDE_PROJECT_DIR` ou
    pelo git.
  - **O Codex perde a fonte.** O `instalar_codex.py` lê `.claude/skills/`, que deixa de existir no
    projeto. Falta decidir de onde ele tira as cópias.
- **`/golem:comecar`:** cria o que o projeto precisa (o `AGENTS.md`, `docs/licoes/`, `specs/` e o
  `golem.toml` no modo econômico). Preenche as lacunas `<< >>` por entrevista ("como você roda o
  jogo?", "usa Rojo?", "onde estão seus módulos?") e termina testando o gancho.
- **`/golem:diagnostico`:** confere o Python, o `sh`, o git, o índice, o gancho, o modo e o Studio
  MCP, e diz em uma linha o que fazer em cada falha.
- **O guia "primeiro dia":** uma página com um fluxo só (spec → implementar → validar), numa
  conversa só, sem GER, EST nem MET. O `docs/operacao-das-conversas.md` fica para o modo completo.
- **As mensagens:** a falha do gancho aparece uma vez por sessão, diz o que deixou de funcionar e
  como consertar. Nenhuma mensagem usa sigla sem dizer o que é.

---

## 7. Roteiro em fases

Cada fase é uma branch, mergeável sozinha, com spec aprovada antes (regra 1). A ordem põe primeiro
o que o primeiro usuário sente no primeiro dia. A instalação vem depois porque, no começo, o autor
do kit pode instalar com ele.

| Fase | Entrega | Melhorias | Tamanho | Pronto quando |
|---|---|---|---|---|
| **1. Econômico e passo a passo** | o `golem.toml` com os dois modos; a skill `modo`; um `golem aplicar` mínimo, em `.claude/golem.py` (o bloco "Modo atual" no `AGENTS.md`, o `model:` dos agentes e o gancho ligado ou não, com o teto); as regras 1, 10 e 11, a `implementar-fase`, o fecho em `docs/operacao-das-conversas.md:156` e a descrição do `validador` obedecendo ao modo; o gancho que falha uma vez só | 1, 2, 3 | M | numa fase de teste em modo econômico, a conversa para a cada grupo, roda um revisor só, no Sonnet, e o aviso do gancho aparece uma vez |
| **2. Roblox mínimo** | os modelos de tech-stack e de comandos para Rojo, os gatilhos, duas lições de exemplo e os testes pelo Studio MCP | 4 | M | num place Rojo de exemplo, uma fase pequena vai da spec ao validado, com o resumo dos testes lido no console |
| **3. Estilo e reaproveitamento** | a skill de estilo, o catálogo, a pergunta na entrevista e o revisor checando o estilo e o reaproveitamento | 5, 6 | M | com 3 programas do usuário, as regras saem com exemplos do código dele, e o revisor acusa um módulo duplicado de propósito |
| **4. Instalação fácil** | o plugin (com o gancho achando a raiz pelo projeto), o `comecar`, o `diagnostico` e o guia "primeiro dia" | 7, 9 | M | uma pessoa sem o kit instala e começa a primeira spec seguindo só o guia, num Windows sem Python instalado de antemão |
| **5. Configuração completa e medidor** | o esforço por papel, quais papéis rodam, o `golem aplicar --conferir`, o medidor e a busca uniforme no índice | 8, 10, 12 | M | trocar `modo` e rodar `aplicar` muda o que a fase 1 gera, o `--conferir` acusa a divergência, e o medidor mostra o gasto por papel antes e depois |
| **6. Produto** | versões, notas de versão, como atualizar, a página, a licença decidida, a paridade do Codex e a fonte dele depois do plugin | 11, 13 | M–G | um usuário atualiza de uma versão para a outra sem perder as lições nem a configuração |

**Antes da fase 1:** a decisão da licença (cartão à parte) e uma conversa com o primeiro usuário
para confirmar três coisas: se ele usa Rojo ou só o Studio, que framework de teste usa e qual
modelo o Pro dele mostra no `/model`.

---

## 8. Decisões que ficam com o autor do kit, uma de cada vez

1. **A licença:** cartão enviado em 2026-11-12, junto com este plano.
2. **A ordem do roteiro:** se a fase 2 (Roblox) vem antes da 1 (econômico).
3. **O nome como marca:** há outros projetos de software chamados Golem. Vale buscar no INPI antes
   de investir em página e identidade (a conferir).
4. **O que é pago, se algo for:** depende da licença.
