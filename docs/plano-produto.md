# Plano de produto do Golem

Rascunho de 2026-11-12. As citações `arquivo:linha` se referem ao commit `c880a17`, o kit antes
deste plano. O commit `ccca28b`, do crédito, pôs uma linha no topo de vários arquivos e uma seção
no README. As linhas citadas desses arquivos que vêm depois da inserção andaram uma: em `f912da6`,
o `gancho.sh:99` era o 100, e o `README.md:228`, o 229; o `README.md:74` e o `:83` não mudaram.
A fase 0 mudou de novo o `gancho.sh` e o `README.md`: no head dela, as linhas são outras.

É um plano: ele não muda o kit sozinho. Cada decisão volta ao autor do kit num cartão, uma de cada
vez, e as que já foram tomadas estão na seção 8, com as palavras dele.

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
| **Lições que voltam** | cada armadilha vira um arquivo em `docs/licoes/`. Um gancho roda antes de cada edição e de cada comando (`.claude/settings.json:6` e `:17`) e injeta o "Como perceber" das lições daquela ação. Entrega no máximo 4 lições novas por ação (`TETO = 4`, `.claude/hooks/licoes_relevantes.py:60` em `c880a17`; desde a fase 1, o teto vem do `golem.toml`), cada uma uma vez por agente, por sessão | `.claude/hooks/` |
| **Índice em que se busca** | `.claude/indice/licoes.yaml`, gerado pela régua a partir do frontmatter das lições e conferido por ela (`--conferir`). É o único índice. A `iniciar-conversa` o busca por `grep` (`iniciar-conversa/SKILL.md:71-72`); a `implementar-fase` manda procurar nele sem dizer como (`implementar-fase/SKILL.md:23`; desde a fase 1, ela busca direto em `docs/licoes/`) | `.claude/regua.py` |
| **Revisor e validador** | dois subagentes que só leem. O revisor confere o diff contra a spec e as regras; o validador roda os critérios e faz mutação numa cópia descartável. Os dois rodam **a cada grupo** do plano (regra 11, `AGENTS.md:176`; desde a fase 1, conforme o bloco "Como o Golem trabalha aqui") | `.claude/agents/` |
| **Guardião** | o revisor de novo, sobre o diff inteiro do PR | regra 11 |
| **Papéis de conversa** | gerente (GER), estratégia (EST), método (MET), guardião e frentes, com PEDIDO → LIBERADO, níveis de autonomia, o fecho de quatro linhas e o cartão de decisão | `docs/operacao-das-conversas.md`, `sessao-gerente` |
| **Codex** | um instalador gera as cópias que o Codex lê (`.agents/skills/`, `.codex/`) a partir de `.claude/` | `.claude/instalar_codex.py` |

### 1.2 Quanto cada peça custa

**O que entra em toda conversa, a cada turno** (vai para o cache depois do primeiro turno):

| Peça | Tamanho | Tokens (estim.) |
|---|---|---|
| `AGENTS.md` (o `CLAUDE.md` o importa inteiro) | 12.987 bytes | ~3,4 mil |
| descrições das 12 skills (só o `description` entra antes de a skill ser chamada; medido antes da fase 0, que acrescenta a `diagnostico`, com 437 bytes, e da fase 1, que acrescenta a `configurar`, com 386) | 4.520 bytes | ~1,2 mil |
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
grupo de pastas (o mesmo prefixo de caminho), que é um projeto grande. Os subagentes de tipo
próprio entram pelo tipo; os `general-purpose` entram pela descrição ("revis" ou "guardi" para o
revisor, "valida" para o validador). As 48 descrições com as duas palavras ficaram de fora. Todos
os números são medianas por rodada:

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
- **A prova veio na sessão de análise de 2026-11-12.** O gancho falhou em **todas** as ações
  (`gancho.sh:99`), com "nenhum Python 3.8+ encontrado". Cada falha mostrou um aviso ao usuário e
  pôs ~90 tokens no contexto.
  - **O Python existia.** O do instalador oficial estava em
    `%LOCALAPPDATA%\Programs\Python\Python312`, e o lançador `py.exe` em `...\Python\Launcher`,
    os dois fora do PATH. No PATH só estavam os atalhos da Microsoft Store, que não rodam nada.
  - **O gancho só procura no `.venv` e no PATH.** O agente leu o aviso como "a máquina não tem
    Python", e o autor do kit corrigiu. Virou a lição `sem-python-no-path-nao-e-maquina-sem-python`.
  - **O problema, então, é triplo:** repetir o aviso a cada ação; não procurar o Python onde o
    instalador o põe; e um aviso que leva a concluir que o Python falta.
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
| 2 | **Gancho que acha o Python e falha uma vez só:** o diagnóstico mínimo (fase 0) e depois a configuração perguntam se ele tem Python e onde, e o gancho usa esse caminho ou procura também onde o instalador oficial põe o Python; quando falha, avisa uma vez, em palavras simples, cita a lição e dá o conserto em uma linha. Numa máquina sem Python nenhum, ele pode ser desligado: as skills passam a mandar buscar as lições em momentos fixos (o modo sem Python, de reserva) | fácil, custo | A | P |
| 3 | **Receitas prontas, escolha por etapa e configuração por conversa:** três receitas recomendadas (`so-eu`, `economico`, `completo`); cada etapa opcional responde `sempre`, `perguntar` ou `nunca`; ele configura pedindo "configurar o Golem" e respondendo a botões; e o "guia de configuração", de uma página, explica cada escolha | custo, fácil | A | M |
| 4 | **Pacote Roblox mínimo:** primeiro sem Rojo (decisão 8, seção 8): os comandos reais com o Studio MCP, o gancho lendo a edição pelo Studio MCP, um `tech-stack` modelo, critérios com playtest passo a passo; o Rojo e as áreas `.luau`/`rojo`/`selene`/`stylua` vêm na migração | Roblox | A | M |
| 5 | **Aprender o estilo:** uma skill lê os programas que **ele escolher** e propõe as regras do estilo dele, cada uma com um exemplo `arquivo:linha` do próprio código; ele aprova uma a uma | estilo | A | M |
| 6 | **Catálogo do que reaproveitar:** uma linha por módulo dele (o nome, o caminho, o que faz, a interface). A entrevista e o plano consultam o catálogo antes de criar algo novo | estilo | A | M |
| 7 | **Instalação como plugin do Claude Code**, com uma skill de diagnóstico e o `AGENTS.md` preenchido por entrevista | fácil | A | M |
| 8 | **Medidor de custo:** um script local que lê as transcrições e diz quanto cada papel gastou na semana (o desta análise, arrumado) | custo | M | P |
| 9 | **Modo simples de documentação:** o "guia do primeiro dia", de uma página; os papéis de várias conversas e o vocabulário de equipe só na receita `completo` | fácil, custo | M | M |
| 10 | **Configuração completa:** o esforço de cada papel, o `--conferir` do `aplicar` e, se a configuração por conversa não bastar, a página HTML que gera o `golem.toml` | custo, fácil | M | M |
| 11 | **Infraestrutura de produto:** versões, notas de versão, o comando de atualizar e a página do kit | produto | M | M |
| 12 | **Busca uniforme no índice:** a `implementar-fase` usa o mesmo `grep` da `iniciar-conversa` | custo | B agora, M com o acervo maior | P |
| 13 | **Configuração também no Codex** (o instalador passa a ler o mesmo arquivo) | custo | B | M |

**O que fica de fora de propósito:** reescrever o kit em inglês, um servidor próprio e cobrança.
Nada disso ajuda o primeiro usuário.

**O que fica para depois: a interface gráfica de configuração.** O autor do kit a vê como "uma
demanda que eu vejo nesses tipos de pessoa" e "difícil da gente fazer". Primeiro vem a configuração
com botões (melhoria 3). Se ela não bastar, vem a página HTML que gera o arquivo (melhoria 10) e,
depois, a estudar, um painel dentro do Claude Code por plugin.

---

## 3. Esboço da configuração

**O pedido (2026-11-12, nas palavras do autor do kit):** "tinha que ser fácil de customizar para
ele"; "imagina que ele nem quer usar o revisor no final do código, o ideal seria aparecer para
ele, tipo, você quer usar o revisor?"; "a gente manteria os nossos recomendados, com várias
configurações diferentes já prontas, mas é livre para ele configurar como ele quiser"; e "uma
interface gráfica para configuração. Ou um guia muito bom".

**Três camadas, do mais fácil ao mais livre:**
1. **Configurar conversando.** Ele pede "configurar o Golem". O agente faz de 3 a 4 perguntas com
   botões, e cada opção diz o que custa ("1 conversa extra por pedido", "nenhuma"). No fim, ele
   escreve o `golem.toml` e o aplica. Os botões vêm da ferramenta de pergunta do Claude Code
   (`AskUserQuestion`).
   - No app desktop ela aparece com botões.
   - No terminal, fica a conferir: o `docs/operacao-das-conversas.md` diz que a caixa com botões é
     só do app.
   - No Codex, também a conferir. Onde não houver botões, as mesmas perguntas saem em texto,
     numeradas.
2. **Escolher uma receita.** As receitas são os recomendados do kit e vêm prontas com ele (num
   arquivo do kit, não no do projeto).
3. **Mudar qualquer peça.** Cada linha escrita no `golem.toml` vale mais que a receita.

**Cada etapa opcional responde `sempre`, `perguntar` ou `nunca`.** Com `perguntar`, a etapa vira
uma pergunta com botões na hora em que chega, por exemplo "Quer que o revisor olhe o que foi feito?
(abre 1 conversa extra)". O exemplo dele ("o ideal seria aparecer para ele, tipo, você quer usar o
revisor?") é o caso do `perguntar`; quem já sabe que não quer usa o `nunca`.

**Os comandos do `validation.md` rodam sempre.** Em toda receita, a própria conversa roda os
critérios e lê a linha de resumo antes de dar uma parte por pronta (regras 4 e 8). O "validador"
das receitas é só o subagente a mais, que roda tudo de novo e tenta quebrar o código numa cópia (a
mutação).

**As receitas** (os valores são a proposta para a spec da fase 1):

| Etapa | `so-eu` | `economico` (o padrão) | `completo` (o fluxo de hoje) |
|---|---|---|---|
| revisor | nunca | sempre, uma vez por fase, no Sonnet | sempre, a cada grupo, no Opus |
| validador (o subagente) | nunca | nunca | sempre, a cada grupo, no Opus |
| guardião | nunca | nunca | sempre |
| parar a cada parte | sempre | sempre | nunca |
| conversas | uma | uma | papéis (GER, EST, MET) |
| teto do gancho | 2 | 2 | 4 |

Três receitas cobrem os casos que existem hoje: o usuário que não quer revisor (`so-eu`), o plano
Pro (`economico`) e o fluxo do projeto de origem (`completo`). Uma receita intermediária entra
quando aparecer quem a use.

```toml
# golem.toml: como o Golem trabalha neste projeto.
# O jeito mais fácil de mudar: peça "configurar o Golem" e responda aos botões.
receita = "economico"            # so-eu | economico | completo

# Opcional. Cada linha abaixo vale mais que a receita; tire o # da que quiser mudar.
# revisor          = "perguntar"   # sempre | perguntar | nunca
# revisor_quando   = "por_fase"    # por_fase | por_grupo
# modelo_revisor   = "sonnet"      # sonnet | opus | haiku | inherit
# validador        = "nunca"       # sempre | perguntar | nunca (o subagente; os comandos rodam sempre)
# modelo_validador = "opus"
# guardiao         = "nunca"       # sempre | perguntar | nunca
# parar_a_cada_parte = "sempre"    # sempre | nunca
# conversas        = "uma"         # uma | papeis
# gancho           = "ligado"      # ligado | desligado (máquina sem Python)
# gancho_teto      = 2             # lições novas por ação (antes da fase 1, fixo em 4)
# agents_teto      = 3000          # palavras do AGENTS.md antes do aviso da régua (fase 4)
```

```toml
# golem.local.toml: o que é desta máquina. Fica fora do git.
python = 'C:\...\python.exe'       # o Python que o usuário informou ou confirmou (aspas simples)
```

**Por que cada chave existe.** As de revisor, validador, guardião, conversas e modelos atacam o
maior custo medido (seção 1.2). O `revisor_quando` é o que expressa o "uma vez por fase" contra o
"a cada grupo". A de parar a cada parte é o pedido do primeiro usuário. O `gancho = "desligado"`
resolve a máquina sem Python nenhum. O `python`, no `golem.local.toml`, guarda o caminho que o
usuário informou ou confirmou (o pedido do autor do kit, abaixo, em "Primeiro perguntar, depois
procurar"). Ele mora num arquivo à parte porque é desta máquina: um caminho como
`C:\Users\<nome>\...` está errado em qualquer outra e expõe o nome do usuário. O `gancho_teto`
custa pouco (o gancho injeta no máximo ~600 tokens por ação), mas é o que controla quanto contexto
o gancho injeta, um dos itens do critério "customizável", e é uma linha. O `agents_teto` (fase
4, decisão 13) é o teto de palavras do `AGENTS.md`, que entra inteiro em toda conversa; ele é
configurável a pedido do autor do kit ("C: configurável"). O gancho continua
rodando antes de comandos em todas as receitas: as lições do kit disparam por comando, e quem
roda os comandos do `validation.md` (a conversa, e o validador quando ele existe) precisa delas.

**Como a configuração chega ao agente, sem custo novo de leitura.** O `golem aplicar`
(`python .claude/golem.py aplicar`, no molde do `instalar_codex.py`) junta a receita e as linhas
do usuário e gera duas coisas:
1. o `model:` no frontmatter de `.claude/agents/*.md`, que o Claude Code respeita (o `effort:` fica
   para a fase 8);
2. um bloco curto e **gerado** no `AGENTS.md`, "Como o Golem trabalha aqui", que as regras 10 e
   11 passam a citar.

O gancho não passa pelo `aplicar`: o `licoes_relevantes.py` lê o teto do `golem.toml` pelo
`golem.py`, em vez do `TETO = 4` fixo, e o `gancho.sh` lê a linha `gancho` (abaixo). Assim, o
`settings.json` não muda. A fase 1 trocou por isso o plano de gerar ali a chamada do gancho
(`specs/2026-11-13-fase-1-configuracao/requirements.md`, R4 e R5).

Como o `AGENTS.md` já entra em todo turno, o agente sabe a configuração sem abrir arquivo novo, e
sabe em que momento perguntar.

A skill de configurar escreve o `golem.toml` e roda o `aplicar` por ele. Mudou a configuração,
abre-se uma conversa nova. Com o plugin (fase 3), a skill vira `/golem:configurar`.

**Sem Python.** Escrever o `golem.toml` não precisa de Python; aplicá-lo, sim, menos o desligar do
gancho. Para o `gancho = "desligado"` valer numa máquina sem Python, quem o lê é o próprio
`gancho.sh`, que roda em `sh`: ele acha a linha no `golem.toml` e sai calado, antes de procurar o
Python. Assim, a máquina sem Python para de mostrar o aviso a cada ação, e o resto da configuração
fica escrito, esperando o Python para ser aplicado.

**Python fora do PATH.** O caso visto (uma máquina, em 2026-11-12) não foi a falta de Python, e
sim o Python instalado fora do PATH (lição `sem-python-no-path-nao-e-maquina-sem-python`). A
pergunta ao primeiro usuário sobre o Python (seção 7) diz se o caso dele é o mesmo.

**Primeiro perguntar, depois procurar.** O pedido do autor do kit (2026-11-12): "Antes de fazer a
busca, é importante perguntar para o usuário se ele tem ou não. Senão a gente vai buscar à toa,
né? E também tem que dar a possibilidade dele de falar onde, se ele souber."

**Os ajustes do agente, aceitos com o plano (seção 8, decisão 4):**
- a pergunta vem uma vez, na configuração, porque o gancho roda sozinho e não pode perguntar: na
  skill de configurar (fase 1) e, com o plugin, no `comecar` e no `diagnostico` (fase 7). Com a
  decisão 5 da seção 8, ela nasce antes, na fase 0, numa versão mínima da skill de diagnóstico, e
  a skill de configurar a reaproveita;
- o botão "Não sei", ao lado do sim e do não;
- com "Não", uma busca rápida mesmo assim;
- o caminho guardado na linha `python`, entre aspas simples. O arquivo, `golem.local.toml`, foi
  mudança depois do ok (seção 8, decisão 4);
- a ordem de procura do gancho, abaixo.

A pergunta vem com botões:

| Resposta | O que o agente faz |
|---|---|
| **Sim, e sei onde** | o usuário cola o caminho; o agente testa se aquele Python roda (3.8 ou mais novo) e grava o caminho na linha `python` do `golem.local.toml` |
| **Sim, mas não sei onde** | procura nos lugares de costume, mostra o que achou, e o usuário confirma antes de gravar |
| **Não sei** | o mesmo que "sim, mas não sei onde" |
| **Não** | faz mesmo assim uma busca rápida, porque quem acha que não tem pode ter (a lição acima). Se achar, pergunta: "Achei um em `...`. Quer usar este?" Se não achar, oferece o comando de instalação e, a partir da fase 1, também o modo sem Python |

A busca rápida é olhar se dois ou três arquivos existem. Na skill, ela custa uma chamada de
ferramenta, poucas centenas de tokens; no gancho, nenhum. Os lugares de costume, no Windows, são
os do instalador oficial: na instalação "só para mim",
`%LOCALAPPDATA%\Programs\Python\Python3*\python.exe` e o `py.exe` de `...\Python\Launcher`; na
"para todos os usuários", `%ProgramFiles%\Python3*` (a conferir).

**Depois, o gancho não pergunta nada:** procura nesta ordem:
1. (novo, fase 0) o caminho da linha `python` do `golem.local.toml`, lida em `sh`. A leitura do
   `golem.toml` pelo `gancho.sh`, para o `gancho = "desligado"`, também é nova, da fase 1;
2. o `.venv` do projeto e o da pasta principal (como hoje);
3. o PATH (como hoje);
4. (novo, fase 0) os lugares do instalador oficial.

Um caminho que não roda mais (o Python foi desinstalado) é tratado como os candidatos de hoje, que
só valem se rodarem um Python 3.8+: o gancho passa ao passo 2. Se nada mais for achado, o aviso
diz que a linha `python` não roda, sem citar o caminho (o `avisar` do `gancho.sh` encerra o gancho
sem entregar lição nenhuma e só aceita texto fixo, sem barra invertida, dentro do JSON). Avisar
isso sem cortar as lições, quando o passo 2 ou outro acha um Python, pediria uma peça nova (ver
"Detalhes a conferir").

O aviso de falha diz onde procurou, cita a lição pelo id e manda rodar o diagnóstico, em vez de
dar a entender que o Python não existe. Isso importa porque o gancho não consegue entregar a lição
justamente quando não acha o Python.

**A linha `python` vai entre aspas simples** (`python = 'C:\...\python.exe'`). No TOML, as aspas
simples fazem uma string literal, sem escape. O `gancho.sh` lê com `read -r`, que não trata a
barra invertida (conferido no Git Bash em 2026-11-12: com `-r`, o caminho chega inteiro; sem ele,
as barras somem). Um caminho com aspa simples dentro não cabe nesse formato: a skill o recusa e
pede outro (na skill, `SKILL.md:49` e `:91-92`; não exercitado na fase 0).

**A diferença esperada, em ordem de grandeza.** Numa fase de 3 grupos, a receita `completo` roda
7 subagentes (3 revisores, 3 validadores e o guardião). A `economico` roda 1: um revisor no Sonnet
sobre o diff da fase. Os comandos do `validation.md` ficam com a própria conversa, que lê a linha
de resumo.
- **Se os 7 tivessem o tamanho mediano medido**, o corte no que os subagentes gastam seria de uns
  85%.
- **Mas o revisor do econômico lê o diff da fase inteira.** Com o dobro do tamanho de uma rodada
  mediana, o corte cai para uns 70%.
- **A conta não inclui** os comandos que passam a rodar na conversa principal, nem a diferença de
  preço entre o Opus e o Sonnet.

O número real se mede com o medidor (melhoria 8) no primeiro projeto Roblox.

**O que nenhuma receita corta:** a spec com entrevista, a aprovação do usuário, os critérios como
comando, as lições e a regra de simplicidade. Elas custam pouco e são o que o primeiro usuário
gostou. Quem desliga o revisor e o validador (a `so-eu`, ou um `nunca`) fica sem a leitura e a
prova independentes; os comandos do `validation.md` continuam rodando. A skill de configurar diz
isso numa linha, e a escolha é dele.

**Detalhes a conferir na fase** (a fase de cada item entre parênteses):
- (fase 1, resolvido) o `tomllib` só existe no Python 3.11+, e o kit pede 3.8+: o `golem.toml`
  usa só `chave = valor`, lido por um leitor próprio, e o mínimo continua 3.8 (seção 8, decisão 7);
- (fase 9, a paridade do Codex) se o formato de agente do Codex aceita modelo por agente. O
  `instalar_codex.py` leva só o `name` e o `description` do frontmatter, e os nomes de modelo do
  Codex são outros. Movido da fase 1 em 2026-11-13;
- (fase 0, resolvido) como o `golem.local.toml` chega a um worktree: o `gancho.sh` o procura
  também na pasta principal, pelo `--git-common-dir`, como o `.venv` (`ler_linha_python`);
- (fase 0, resolvido) o aviso da linha `python` que não roda, quando outro Python é achado: fica
  em silêncio, e o gancho segue com o Python achado. O aviso de falha lista os lugares em texto
  fixo, sem caminho;
- (fase 0, resolvido) no `sh` do Git Bash, o `%ProgramFiles%` do Windows chega como
  `$PROGRAMFILES`, em maiúsculas, e o `$LOCALAPPDATA` com esse nome (conferido em 2026-11-12). O
  Windows reescreve o `PROGRAMFILES` de todo processo criado fora do `sh` (lição
  `o-windows-muda-o-que-o-sh-recebe-do-python`);
- (fase 9, a paridade do Codex) se a entrada de gancho do Codex traz `session_id`. Sem ele, o
  aviso de falha sai em toda ação, como antes da fase 0;
- (fase 7, o diagnóstico completo) se o `systemMessage` do gancho de um subagente aparece ao
  usuário. A fase 0 não depende disso: só a conversa principal põe o `systemMessage`. A fase 1
  também não: o `gancho = "desligado"` sai calado. Movido da fase 1 em 2026-11-13;
- (fase 7, a instalação) o que o kit entrega das lições `o-windows-muda-o-que-o-sh-recebe-do-python` e
  `trocar-o-localappdata-nao-esconde-o-python-do-agente`, que ficam em `docs/licoes/` por ora
  (seção 8, decisão 6), e das duas que a fase 1 acrescentou pelo mesmo caminho,
  `frontmatter-invalido-some-com-o-agente-sem-aviso` e
  `o-grep-do-git-for-windows-aborta-com-i-e-varios-e`;
- (fase 7) o "pulado sem Python" na `validar-fase`, na `auditar-specs` e na `sessao-gerente`, que
  rodam a régua: a fase 1 o faz só na `implementar-fase` e na `licao` (seção 8, decisão 7), e a
  seção 5(b) o pede em todas;
- (fase 3, a fundação do Golem central) por que uma sessão do app desktop aberta num worktree criado pelo app roda o
  `gancho.sh` da pasta principal, e não o do worktree. A hipótese é o `CLAUDE_PROJECT_DIR`, que
  `.claude/settings.json:10` e `:21` usam. Visto na fase 0, a conferir.

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
- `parar_a_cada_parte = "sempre"` faz a implementação parar ao fim de cada grupo, com o diff e
  uma linha do que mudou. O próximo grupo só começa com o ok dele.
- A `spec-de-fase` passa a propor grupos do tamanho de um arquivo ou de uma função.
- O guia recomenda o modo de permissão padrão do Claude Code, que pede licença antes de cada
  edição, e desaconselha o modo automático para ele.

---

## 5. Roblox Studio

**O caminho de entrada é sem Rojo** (decisão 8, seção 8). O código fica no place; as specs, as
lições e o `AGENTS.md` ficam numa pasta ao lado, com git local (o kit não exige GitHub). O agente
edita os scripts pelo Studio MCP. A fase 2 entrega esse caminho
(`specs/2026-11-13-fase-2-roblox/`); os fatos abaixo foram lidos na fonte em 2026-11-13 e
reconferidos em 2026-11-15.

- **O Studio MCP oficial**, segundo a [documentação](https://create.roblox.com/docs/studio/mcp):
  - vem embutido no Studio e se liga em Assistant ⟩ … ⟩ Manage MCP Servers ⟩ "Enable Studio as MCP
    server"; o quick connect tem, entre outros, o Claude Code e o Codex, e para o Claude Code ele
    mostra um comando `claude mcp add` a rodar na pasta do projeto (fase 2, G2, resposta 1). Na
    configuração por JSON, o servidor se chama `Roblox_Studio`;
  - os scripts: o `script_read` lê pelo caminho com pontos (`game.ServerScriptService.MyScript`);
    o `script_search` busca pelo nome, e o `script_grep`, por um texto em todos os scripts; o
    `multi_edit` edita, e cria o script se o caminho não existe;
  - o `execute_luau` roda Luau num `datamodel_type` (Edit, Client ou Server); o `start_stop_play`
    e o `get_studio_state` controlam o jogo; o `get_console_output` lê o console;
  - o `save_place` salva como File ⟩ Save: uma versão nova, num place aberto do Roblox; por cima
    do arquivo, num place local (a página escreve "`.rbx` and `.rbxlx`");
  - toda chamada leva um `studio_id`, que o `list_roblox_studios` lista;
  - avisa: "MCP clients can read and modify content in your open Roblox places."
- **A Open Cloud pelo Studio MCP**
  ([documentação](https://create.roblox.com/docs/studio/mcp-open-cloud)): o `open_cloud_invoke`
  chama as APIs sem chave, com as permissões ligadas por jogo em MCP ⟩ MCP Permissions. Cada jogo
  começa no nível "Balanced"; o "Full access" pode publicar no jogo ao vivo; e, para os scripts
  no Studio com o acesso às APIs ligado, o `DataStore` é o do jogo publicado (a opção vem
  desligada: [data stores](https://create.roblox.com/docs/cloud-services/data-stores); fase 2,
  G6). O kit não usa a Open Cloud, e o guia de Roblox manda desligar as
  permissões.
- **O que fica mais fraco sem Rojo, e como a fase 2 cobre:**
  - não há diff do git: o revisor lê o script atual pelo Studio MCP, com a lista dos scripts que o
    grupo mexeu;
  - os dois agentes ganham as ferramentas de leitura do Studio MCP no `tools:`; o validador ganha
    também o `execute_luau`, o `start_stop_play` e o `get_studio_state`, para rodar os testes em
    modo de jogo; ele nunca muda o place, porque não há cópia descartável, e a mutação é em
    memória, com o jogo ligado, e só num place sem `DataStore` (fase 2, G6);
  - o gancho ganha uma entrada para o `multi_edit` e o `execute_luau`: o caminho do script chega
    em `file_path`, que ele já lia, e o código em `code`, que ele passou a ler (fase 2, G2,
    resposta 2);
  - o desfazer: o agente salva uma versão (`save_place`) antes de cada fase, e volta-se pelo
    [histórico de versões](https://create.roblox.com/docs/projects/version-history) (Window ⟩
    Version History ⟩ ⋮ ⟩ Open Local Copy ⟩ Save to Roblox As, ou Creator Dashboard ⟩ Restore).
    Restaurar cria uma versão nova e não publica.

**O destino é o Rojo (ou o Argon) e o git, numa fase própria de migração** (seção 7, a fase 10):
- **Os arquivos:** o código fica em `src/` como `.luau` (`.server.luau` e `.client.luau` para
  Script e LocalScript), e o `default.project.json` mapeia as pastas para os serviços do place
  (ReplicatedStorage, ServerScriptService, StarterPlayer). Assim, o git, o diff, o revisor e o
  gancho funcionam como num projeto de qualquer linguagem.
- **As ferramentas:** o Rojo ou o Argon para sincronizar, o StyLua para formatar, o Selene para o
  lint e o Wally para pacotes, com as versões fixadas por um gerenciador de ferramentas (Rokit ou
  Aftman). As versões atuais ficam a conferir na fase da migração.
- **O `rojo syncback`:** a versão 7.7.0 do Rojo, estável desde 2026-07-02 (a mais nova é a 7.7.1,
  de 2026-10-02), traz o `rojo syncback path/to/project --input path/to/file.rbxl`, que converte
  um place existente em projeto Rojo. Só vem o que descende de um nó do arquivo de projeto, e as
  regras ficam no campo `syncbackRules`. As notas da release dizem que a documentação ainda vai
  sair ("Documentation is forthcoming").

**Os testes:**
- **Framework** (API do GitHub, 2026-11-13): o `Roblox/testez` está arquivado (último push em
  2024-03-05); o `TestEZ.rbxm` vem nas releases v0.2.0 a v0.3.2, e a última, v0.4.2 (2022), não o
  traz. O resumo sai como `"%d passed, %d failed, %d skipped"` (`Roblox/testez`,
  `src/Reporters/TextReporter.lua:80`). O Jest
  ativo é o `Roblox/jest-roblox` (MIT), sem release publicada; o `jsdotlua/jest-lua` é um fork dele,
  parado em 2024-12 (v3.10.0), com `.rbxm` só nas rc da 3.6.1. **Sem Rojo, a fase 2 usa um executor
  mínimo**, modelo do kit, que imprime no formato do TestEZ; o framework entra na migração.
- **Como rodar:**
  1. **pelo Studio MCP**, o caminho da fase 2: o `execute_luau` roda o executor, e o
     `get_console_output` traz o resumo, sem credencial nenhuma. Os testes rodam com o jogo
     ligado: em modo de edição, o `require` devolve a versão guardada de um módulo, mesmo
     depois de editado (fase 2, G2, resposta 3);
  2. **o `run-in-roblox`**, fora: o último commit é de 2020-07-20 (a v0.3.0);
  3. **a API Open Cloud de execução de Luau, sem abrir o Studio** ([documentação](https://create.roblox.com/docs/cloud/reference/features/luau-execution)),
     fora da fase 2:
     - pede uma chave de API, que é credencial (regra 5), e quem decide é o usuário;
     - aceita 5 criações de tarefa por minuto;
     - roda tarefas de até 5 minutos.
- **A lição da linha de resumo vale igual:** sem o total de testes, as falhas e os pulados lidos no
  console, não há resultado. O executor imprime a linha no formato do TestEZ e diz "nenhum teste
  encontrado" quando não acha teste.
- **O que não tem teste automático** (a física, a sensação de um pulo, a interface) entra no
  `validation.md` como passo a passo de playtest, que a regra 4 já aceita.

**O que muda no kit:**
- **na fase 2:** os modelos em `templates/roblox/` (o `tech-stack`, os "Comandos reais", o
  executor, duas lições e uma lista de riscos de exemplo, como regras de área); o gancho lendo o
  Studio MCP, com os serviços do place (`game.ServerScriptService` e os outros) no `POR_CAMINHO`;
  as ferramentas de leitura do Studio MCP no `tools:` do revisor e do validador; e o guia
  `docs/guia-roblox.md`;
- **na migração:** `.luau` e `default.project.json` no `POR_CAMINHO`; `rojo`, `argon`, `selene`,
  `stylua` e `wally` no `POR_COMANDO`; o framework de teste no lugar do executor.

**O kit fora de um repositório JS ou Python.** O método não depende da linguagem. Só o ferramental
do kit (o gancho, a régua e o instalador) é Python. A busca nas lições e nos documentos não
precisa dele: o Claude Code tem a própria busca. Sem Python, o que se perde é:
- a entrega automática das lições na hora certa (o gancho);
- a geração e a conferência do índice: a `licao` gera o índice, e o `regua.py --conferir` é
  critério na `validar-fase`, na `auditar-specs` e na `sessao-gerente`. Sem Python, o índice
  envelhece;
- o `aplicar` e o instalador do Codex.

Há quatro saídas, e elas não se excluem:
- **(a)** o diagnóstico mínimo (fase 0) e a configuração perguntam se ele tem Python e onde, e
  conferem com uma busca rápida nos lugares do instalador oficial; o gancho usa o caminho
  registrado e, sem ele, procura nesses mesmos lugares (seção 3, "Primeiro perguntar, depois procurar"). Só se nada for achado, a
  configuração e o diagnóstico dizem como instalar (no Windows, um comando do `winget`; o id exato
  fica a conferir);
- **(b)** o modo sem Python, de reserva: `gancho = "desligado"` (lido pelo `gancho.sh`, seção 3).
  As skills buscam as lições em momentos fixos (no começo da fase e antes de rodar os testes)
  **sempre**, com ou sem gancho: a busca é barata, e assim não depende do `aplicar` para saber que
  o gancho está desligado. Sem Python, a busca vai direto a `docs/licoes/`, e não ao índice, que
  pode estar velho. Os passos de régua das skills dizem que foram pulados, em vez de falhar;
- **(c)** a estudar: o Claude Code aceita ganchos escritos em JavaScript num plugin (os "hooks
  modules"), o que tiraria o Python do caminho. Isso só vale para o Claude, e falta conferir se
  esse tipo de gancho pode injetar contexto;
- **(d)** a estudar: reescrever em Luau, rodando no Lune, se o usuário já tiver o Lune.

**Decidido em 2026-11-12:** a (a), com a (b) de reserva. A (a) foi ampliada no mesmo dia pela
decisão 4 da seção 8 (perguntar antes de procurar). A (c) e a (d) só se, depois, mais gente
travar na instalação do Python. A skill de configurar escreve o `golem.toml` sem Python; aplicá-lo
pede Python, menos o desligar do gancho.

---

## 6. Instalação e primeiro uso

**Mudou com o Golem central (seção 8, decisão 11).** O kit é instalado uma vez, como plugin, e
ligado só nos jogos. A base, com o plugin, o "ligar" e o registro dos jogos, é da fase 3 (a
fundação). O acabamento abaixo, com o `comecar`, o `diagnostico` e o guia, é da fase 7.

- **Um plugin do Claude Code.** Um plugin junta skills, agentes e ganchos e se instala pelo
  `/plugin`, a partir de um marketplace que pode ser o próprio repositório ou uma pasta local (o caminho
  da release com zip, decisão 12) ([plugins](https://code.claude.com/docs/en/plugins.md)). Os comandos, conferidos na fase 3, estão
  no `README.md`, "Instalar o Golem (uma vez)".
  - **Custo:** as descrições das skills de um plugin ligado entram em todo turno, **em todo projeto
    em que ele estiver ligado**. Por isso, com o Golem central (seção 8, decisão 11), ele fica
    desligado por padrão no usuário e ligado só nos jogos, por uma linha `true` no projeto.
  - **Nome:** as skills ganham prefixo (`/golem:spec-de-fase`).
  - **O gancho muda o jeito de achar o projeto.** Antes, a raiz saía da posição do próprio
    arquivo, o que dentro de um plugin daria a pasta do plugin. Desde a fase 3, ele acha a raiz
    pelo `CLAUDE_PROJECT_DIR` ou pelo git.
  - **O Codex fica na cópia.** Ele não usa o plugin: o kit vai copiado ao projeto, e o
    `instalar_codex.py` continua lendo a `.claude/skills/` dele (decisão 11; `README.md`, "Usando
    com o Codex"). O Codex como plugin é da fase 9.
- **`/golem:comecar`:** cria o que o projeto precisa (o `AGENTS.md`, `docs/licoes/`, `specs/` e o
  `golem.toml` com a receita `economico`). Preenche as lacunas `<< >>` por entrevista ("como você
  roda o jogo?", "usa Rojo?", "onde estão seus módulos?"), passa pela configuração com botões (com
  a pergunta do Python) e termina testando o gancho. No Golem central, o que se configura uma vez
  e o que fica no jogo se decide na fase 3.
- **`/golem:diagnostico`:** confere o Python, o `sh`, o git, o índice, o gancho, a configuração e
  o Studio MCP, e diz em uma linha o que fazer em cada falha. Quando o gancho não acha o Python,
  faz a mesma pergunta com botões da configuração (seção 3) e grava a resposta. Sem Python
  nenhum, diz o comando que o instala e oferece o modo sem Python enquanto isso.
- **O guia do primeiro dia:** uma página com um fluxo só (spec → implementar → validar), numa
  conversa só, sem GER, EST nem MET. O `docs/operacao-das-conversas.md` fica para a receita
  `completo`.
- **As mensagens:** a falha do gancho aparece uma vez por sessão, diz o que deixou de funcionar e
  como consertar. Nenhuma mensagem usa sigla sem dizer o que é.

---

## 7. Roteiro em fases

Cada fase é uma branch, mergeável sozinha, com spec aprovada antes (regra 1). A ordem das fases 0
a 2 pôs primeiro o que o primeiro usuário sente no primeiro dia. A instalação vem depois porque, no
começo, o autor do kit pode instalar com ele. A ordem foi confirmada pelo autor do kit (seção 8,
decisões 3 e 5) e refeita em 2026-11-21 pelas decisões 10 e 11: o Golem central e as fases novas.
A exceção aceita: a base (a fundação, as lições e a fala) vem antes do estilo, que é o que o
primeiro usuário mais quer.

**Os números mudaram em 2026-11-21.** As fases 0 a 2 guardam o número. As pendentes foram
renumeradas, e o número antigo vem entre parênteses ("antes: 3"). As specs das fases 0 a 2 e a da
separação, e as decisões 1 a 8 da seção 8, citam os números antigos: leia-os por esses parênteses.
Em 2026-11-22, a fase 4b entrou entre a 4 e a 5, sem renumerar as outras (decisão 14). Na spec da
fase 3, a "fase 4" dos dois acervos, da raiz do gancho e do cliente marcado é a 4b.

| Fase | Entrega | Melhorias | Tamanho | Pronto quando |
|---|---|---|---|---|
| **0. O gancho acha o Python** (feita: validada em 2026-11-13, branch `fase-0-python`, spec em `specs/2026-11-12-fase-0-python/`) | a pergunta do Python com botões ("Você tem Python? Onde?"), numa versão mínima da skill de diagnóstico (em texto onde não houver botões); o `golem.local.toml` com a linha `python` (que entra no `.gitignore`), procurado também na pasta principal; o `gancho.sh` com a ordem nova (a linha `python`, o `.venv`, o PATH, os lugares do instalador oficial); o aviso de falha que sai uma vez, diz onde procurou, cita a lição e manda rodar o diagnóstico; e, quando nada é achado, o comando de instalação | 2 (o Python e o aviso) | P–M | numa máquina com o Python fora do PATH (só os atalhos da loja no PATH), o gancho o acha e entrega a lição; respondendo "Não" à pergunta do Python nessa máquina, a skill o acha e pergunta se usa; respondendo "Sim, e sei onde" com um caminho fora dos lugares de costume, a skill o grava e o gancho entrega a lição; com um `.venv` presente e a linha `python` apontando para outro Python, o gancho usa o da linha (a ordem); num worktree, o gancho acha o `golem.local.toml` da pasta principal; `git check-ignore golem.local.toml` confirma que ele fica fora do git; com a linha `python` apontando para um caminho que não roda e nenhum outro Python achado, o aviso diz que a linha `python` não roda; e o aviso de falha aparece uma vez por sessão, não a cada ação, citando a lição pelo id |
| **1. Configuração e receita econômica** (feita: validada em 2026-11-15, branch `fase-1-configuracao`, spec em `specs/2026-11-13-fase-1-configuracao/`) | as três receitas e o `golem.toml` com as linhas livres; o `sempre`/`perguntar`/`nunca` de cada etapa; a skill de configurar com botões (em texto onde não houver botões), que reaproveita a pergunta do Python da fase 0, e o guia de configuração; um `golem aplicar` mínimo, em `.claude/golem.py` (o bloco "Como o Golem trabalha aqui" no `AGENTS.md` e o `model:` dos agentes; o gancho lê o `golem.toml` direto, o desligado e o teto, sem passar pelo `aplicar`); as regras 10 e 11 (a 1 não mudou), a `validar-fase`, a `implementar-fase`, o fecho em `docs/operacao-das-conversas.md:156` e a descrição do `validador` obedecendo à configuração; e o modo sem Python (o `gancho.sh` lendo o `gancho = "desligado"`, a busca direto em `docs/licoes/`) | 1, 2 (o modo sem Python), 3 | M | numa fase de teste com a receita `economico`, a conversa para a cada grupo e roda um revisor só, no Sonnet; com `revisor = "perguntar"`, a pergunta aparece com botões no fim da fase; a skill de configurar, respondida de ponta a ponta, deixa o `golem.toml` e o que o `aplicar` gera de acordo com as respostas; e, com `gancho = "desligado"` numa máquina sem Python, nenhum aviso do gancho aparece |
| **2. Roblox mínimo, sem Rojo** (feita: validada em 2026-11-21, branch `fase-2-roblox`, spec em `specs/2026-11-13-fase-2-roblox/`) | o caminho sem Rojo: o gancho lendo a edição pelo Studio MCP; o revisor e o validador lendo o place (o validador com a mutação só em memória, num place sem `DataStore`); um executor mínimo de testes; os modelos de tech-stack e de comandos, duas lições e uma lista de riscos de exemplo em `templates/roblox/`; e o guia `docs/guia-roblox.md` | 4 | M | num place de exemplo, sem Rojo, com o Studio MCP ligado, uma fase pequena vai da spec ao validado: o agente salva a versão antes da fase; edita um ModuleScript pelo `multi_edit`; o gancho entrega uma lição e uma regra de área de exemplo nessa edição; os testes rodam pelo executor, e a linha `N passed, N failed, N skipped` é lida no console; um teste quebrado de propósito aparece como `failed`; e, no fim, uma volta pelo histórico de versões é feita seguindo só o guia |
| **Separar o método do produto** (sem número; feita: validada em 2026-11-21, PR 9, merge `d637f52`, spec em `specs/2026-11-21-separar-metodo-produto/`) | o modelo do usuário em `templates/AGENTS.md`; o `AGENTS.md` da raiz e o `golem.toml` do próprio kit, na receita `completo`; o conciliador (`.claude/tests/test_conciliar.py`); e a instalação copiando o modelo e rodando o `golem.py aplicar` | — (decisão 9) | P–M | feita; o "pronto" está no `validation.md` da fase |
| **3. Fundação do Golem central** (feita: validada em 2026-11-22, branch `fase-3-fundacao-central`, spec em `specs/2026-11-21-fase-3-fundacao-central/`; decisões 9, 11 e 12) | o esqueleto do plugin; a configuração do central, feita uma vez e válida em todos os jogos (onde a fase 5 grava a preferência dos emojis); o plugin desligado por padrão no usuário e ligado só nos jogos, pela linha `true` que o kit escreve no projeto ao registrar o jogo; o registro dos jogos; o gancho achando o jogo pelo `CLAUDE_PROJECT_DIR`; os itens a conferir da decisão 11 (o modo interativo, o gancho fora do Golem, o arquivo do "ligado", o `CLAUDE_PLUGIN_ROOT` e a subida do `CLAUDE.md`); e as três partes adiadas da separação: a lista do que viaja, o mapa das pastas e a `iniciar-sdd` | 7 (a base) | M–G | feita; o "pronto" está no `validation.md` da fase (num jogo registrado, as skills e os agentes `golem:*` aparecem e o gancho entrega a lição, provado com login; num projeto fora do registro, nenhum aparece) |
| **4. Lições e índices** (feita: validada em 2026-11-22, branch `fase-4-licoes-e-indices`, spec em `specs/2026-11-22-fase-4-licoes-e-indices/`; seção 8, decisões 10, 13 e 14) | cinco itens da proposta da conversa de método sobre os aprendizados de outro projeto: o gancho percebe a lição que falta no índice e avisa uma vez por sessão (A1); a régua confere as `refs:` das lições (D2); a régua mede o tamanho do `AGENTS.md` e avisa (D3); a `licao` manda a regra de área ao `docs/regras-de-area.md`, e não ao `AGENTS.md` (C); e o princípio "índice gerado para o acervo estável, calculado na hora para o documento vivo", na decisão 13 (D1). Tudo sobre o acervo do jogo, com a pasta das lições num só lugar no código, para a 4b trocar; o acervo geral é da fase 4b (decisão 14) | — | M | feita; o "pronto" está no `validation.md` da fase (a lição fora do índice chega com o aviso uma vez por sessão; a ref deslocada sai na régua com a linha nova; o `AGENTS.md` acima do teto sai na régua com o aviso; o texto novo está na `licao`, no README das lições, na regra 7 e na decisão 13) |
| **4b. O acervo geral de lições** (nova; decisão 14) | no Golem central, o acervo geral de lições, ao lado do acervo do jogo: o gancho lê os dois, com a raiz do gancho para os dois; a `licao` oferece subir a lição ao acervo geral, com o ok do usuário e sem citar o projeto; e o projeto de cliente fica marcado e não sobe nada | — | a conferir | a definir na spec da fase |
| **5. Como o kit fala com o usuário** (nova; decisões 10 e 12) | a pergunta das respostas com emojis, gravada na configuração do Golem central, que vale em todos os jogos (decisão 12); os links de todo documento criado ou mudado; toda mudança se explica (T2); o resumo antes de gravar (T3); a linha da etapa (P1) e reler a etapa (P2) | — | a conferir | a definir na spec da fase |
| **6. Estilo e reaproveitamento** (antes: 3) | a skill de estilo, o catálogo (gerado e conferido, como a régua faz com as lições), a pergunta na entrevista e o revisor checando o estilo e o reaproveitamento; o gosto × risco com `riscos = "avisar" \| "perguntar"`, os combinados (o `deny` de permissão a avaliar) e a lição contada ao usuário; no Golem central, o estilo em dois níveis | 5, 6 | M | com 3 programas do usuário, as regras saem com exemplos do código dele, e o revisor acusa um módulo duplicado de propósito |
| **7. Instalação fácil** (antes: 4; só o acabamento, porque a base do plugin vai para a fase 3) | o `/golem:comecar`, o `diagnostico` completo (a fase 0 entrega só a parte do Python), o guia do primeiro dia, o "onde está tudo?" (T1), a escolha das lições que o kit entrega (decisão 6) e, no fim da fase, a primeira release: um zip com o plugin, que se instala de uma pasta local, sem GitHub (decisão 12) | 7, 9 | M | uma pessoa sem o kit instala e começa a primeira spec seguindo só o guia do primeiro dia, num Windows sem Python instalado de antemão; o critério da release com zip fica para a spec da fase 7 (decisão 12) |
| **8. Configuração completa e medidor** (antes: 5) | o esforço por papel, o `golem aplicar --conferir`, a página HTML de configuração (se a fase 1 mostrar que a conversa com botões não basta), o medidor e a busca uniforme no índice; a retrospectiva de três perguntas no fim da fase (decidida para esta fase em 2026-11-13: "Fase 5", o número antigo); e, candidatos, os cartões da conversa gerente para abrir as conversas de estratégia e de método | 8, 10, 12 | M | trocar a `receita` e rodar o `aplicar` muda o que a fase 1 gera, o `--conferir` acusa a divergência, e o medidor mostra o gasto por papel antes e depois |
| **9. Produto** (antes: 6) | o formato das versões, as notas de versão (a primeira release, com o zip, sai no fim da fase 7; decisão 12), como atualizar, a página do kit, a paridade do Codex e a fonte dele depois do plugin | 11, 13 | M–G | um usuário atualiza de uma versão para a outra sem perder as lições nem a configuração |
| **10. Migração para o Rojo** (antes: 7; depois da instalação, na posição que o retorno do primeiro usuário indicar; decisões 8 e 10) | a skill que guia a migração pelo `rojo syncback`; o `default.project.json`; o código no git; as áreas `.luau`, `default.project.json`, `rojo`, `argon`, `selene`, `stylua` e `wally` no gancho; e a troca do executor mínimo por um framework de teste | 4 | a conferir | a definir na spec da fase |

**Perguntas ao primeiro usuário.**
- **Antes da fase 0:** se ele já tem Python instalado, e onde (o trabalho do Python é da fase 0).
- **Antes da fase 1:** qual modelo o Pro dele mostra no `/model` (as receitas fixam o Sonnet e o
  Opus, e o "pronto" da fase 1 pede o Sonnet).
- **Antes da fase 2** (não travam a fase; sem resposta, o guia de Roblox sugere uma pasta por
  jogo): se ele toparia migrar para o Rojo um dia; como organiza os jogos (uma pasta por jogo?);
  e como volta a uma versão anterior hoje.

---

## 8. Decisões do autor do kit

**Tomadas:**
1. **A licença, em 2026-11-12.** O cartão recomendou manter a MIT. As palavras dele: "Ok, eu
   quero manter a MIT só que eu só quero pelo menos reforçar que me deem os créditos" e, sobre
   como reforçar, "MIT, com aviso por arquivo". Aplicado no commit `ccca28b`: o nome completo no
   `LICENSE`, a cópia em `.claude/LICENSE`, a linha de crédito em cada skill, agente e script, a
   seção "Licença e crédito" do README e o teste que acusa crédito ausente.
2. **A configuração, em 2026-11-12.** O pedido está na seção 3. As palavras dele sobre a
   recomendação: "sim, pode seguir sua recomendação". Entra na fase 1 (seções 3, 5 e 7); a parte
   do Python foi depois para a fase 0 (decisão 5). Os pontos aceitos:
   - configurar conversando, com botões, mais um guia de uma página;
   - receitas prontas, com linhas livres que valem mais que elas;
   - cada etapa opcional com `sempre`, `perguntar` ou `nunca`;
   - a página HTML e um painel de plugin ficam para depois;
   - o Python como requisito, com o diagnóstico guiando a instalação e o modo sem Python de
     reserva; reescrever o gancho em JavaScript ou em Luau, só se mais gente travar no Python.

   Mudança depois do ok, para a spec da fase 1 confirmar: a receita `equilibrado`, que estava na
   recomendação, saiu do esboço por não ter um usuário que a peça (regra 10).
3. **A ordem do roteiro, em 2026-11-12.** O cartão recomendou a fase 1 (configuração e receita
   econômica) antes da fase 2 (Roblox mínimo). As palavras dele: "Configuração primeiro". A ordem
   da seção 7 fica como está; depois, a decisão 5 pôs uma fase 0 antes da 1.
4. **Perguntar antes de procurar o Python, em 2026-11-12.** A proposta veio dele (as palavras
   estão na seção 3, "Primeiro perguntar, depois procurar"). As palavras dele sobre os ajustes do
   agente: "sim, pode atualizar o plano". Os ajustes aceitos:
   - a pergunta vem na configuração, porque o gancho não pode perguntar (a decisão 5 a pôs na
     fase 0, no diagnóstico mínimo);
   - o botão "Não sei", ao lado do sim e do não;
   - com "Não", uma busca rápida antes de mandar instalar, por causa da lição
     `sem-python-no-path-nao-e-maquina-sem-python`;
   - a linha `python` de volta, entre aspas simples, para guardar o caminho que o usuário informar;
   - a ordem de procura do gancho: a linha `python`, o `.venv`, o PATH e os lugares do instalador.

   Mudança depois do ok, para a spec da fase 0 confirmar: a linha `python` foi para um
   `golem.local.toml`, fora do git, e não para o `golem.toml`. O caminho é desta máquina, está
   errado em qualquer outra e expõe o nome do usuário.
5. **A fase 0, em 2026-11-12.** O cartão trouxe três opções:
   - (A) uma fase 0 com todo o fluxo do Python;
   - (B) uma fase 0 só com a busca e o aviso, sem a pergunta;
   - (C) sem fase 0, com tudo na fase 1.

   O cartão recomendou a (A). As palavras dele: "Opção A, a fase 0 com todo o fluxo do Python". A
   fase 0 leva a pergunta com botões numa versão mínima da skill de diagnóstico, o
   `golem.local.toml` com a linha `python`, a busca nos lugares do instalador e o aviso que sai uma
   vez e cita a lição. A ordem passa a ser: fase 0, depois a 1 (configuração), depois a 2 (Roblox).

   Leitura do agente, para a spec da fase 0 confirmar: o cartão não listava o modo sem Python
   (`gancho = "desligado"`) em nenhuma das fases. Ele fica na 1, porque o `gancho = "desligado"` é
   uma linha do `golem.toml` e o modo mexe nas skills (buscar as lições em momentos fixos). Na fase
   0, quando nada é achado, a pergunta oferece só o comando de instalação.
6. **O que sobrou da fase 0, em 2026-11-13.** A conversa gerente (GER) trouxe quatro
   recomendações. As palavras dele: "Sim, as quatro". As quatro, em dois itens:
   - as lições `o-windows-muda-o-que-o-sh-recebe-do-python` e
     `trocar-o-localappdata-nao-esconde-o-python-do-agente` ficam em `docs/licoes/` por ora; a fase
     4 (o plugin) decide o que o kit entrega (ver "Detalhes a conferir na fase", seção 3);
   - da skill `diagnostico`, fica a conferência do `.gitignore` e sai o aviso da linha `python`
     própria do worktree. Uma linha `python` escrita à mão num worktree passa a vencer a da pasta
     principal sem aviso: a skill nunca grava ali. Aplicado na fase 1.
7. **A spec da fase 1, em 2026-11-13.** Ele escolheu a opção recomendada nas quatro perguntas da
   entrevista (`specs/2026-11-13-fase-1-configuracao/requirements.md`, "Decisões"):
   - **"Econômica no kit":** depois da fase 1, o repositório do kit roda na receita `economico`,
     porque o `AGENTS.md` dele é o que o usuário copia até a fase 4. As fases 2 em diante do kit
     rodam com um revisor só, no Sonnet, uma vez por fase;
   - **"Leitor próprio, 3.8+":** o `golem.toml` aceita só `chave = valor` e comentários, e o
     mínimo continua o Python 3.8;
   - **"Mínimo"** para o modo sem Python: só a `implementar-fase` e a `licao` mudam na fase 1; o
     resto vai para a fase 4;
   - **"Receita + duas etapas":** a skill de configurar pergunta a receita, o revisor e o parar a
     cada parte.

   **A "Econômica no kit" deixou de valer: ver decisão 9.**

8. **O caminho sem Rojo e a spec da fase 2, em 2026-11-13.** As palavras dele sobre o caminho:
   "Sem Rojo, migrar depois". O caminho de entrada é sem Rojo (seção 5): o código fica no place, e
   as specs e as lições ficam numa pasta ao lado com git local; uma skill guia a migração para o
   Rojo quando ele quiser ou o projeto crescer (a fase 7). Os fatos dele sobre o primeiro usuário:
   não usa Rojo, e "Não parece ter muita experiência com controle de versões ainda". Na entrevista
   da spec da fase 2 (`specs/2026-11-13-fase-2-roblox/requirements.md`, "Decisões"), ele escolheu
   a opção recomendada em cinco das seis perguntas e respondeu a do Studio com texto livre:
   - **"Só salvar o place"** para desfazer (primeiro "Sem espelho"; reconfirmado depois que a
     conversa de estratégia trouxe o "Os dois, como ideia" dele): o agente salva uma versão antes
     de cada fase. Descartado: guardar o antes e o depois de cada script no git;
   - **"Executor mínimo do kit"**, reconfirmado como **"Mantém o executor"** com os fatos dos
     frameworks corrigidos (seção 5). Descartados: o TestEZ e o Jest, dependência nova (regra 3);
   - **"Fase própria depois"** para a migração (a fase 7);
   - sobre o teste no Studio, que não está instalado na máquina do autor do kit: "Me pergunte
     novamente quando chegarmos nesta etapa em que ele é necessário.";
   - **"Fica na fase 2"**: o gancho lê a edição pelo Studio MCP (pedido da conversa de
     estratégia);
   - **"Nesta fase, como modelo"**: a lista de riscos do Roblox, em `templates/roblox/`.

   Sobre o fluxo da própria fase 2: "Completo pelo prompt" (revisor e validador a cada grupo, no
   Opus, e guardião no PR). **É uma exceção à decisão 7**, a "Econômica no kit": a fase 2 não serve
   de teste da receita `economico`. A spec foi aprovada com "Aprovo" (2026-11-13), com um commit
   por grupo. **O "Completo pelo prompt" deixou de valer: ver decisão 9.**
9. **Separar o método do produto, em 2026-11-21.** As palavras dele: "nós estamos usando a
   ferramenta para desenvolver a ferramenta. Talvez seja muito importante nós criarmos essa
   separação [...]". As respostas:
   - "Separar já (Recomendado)" e, depois da correção da conversa de estratégia, "Ok, mantém a
     separação";
   - "Conferência automática" para o conciliador (e não um agente).

   As cinco da spec da fase (`specs/2026-11-21-separar-metodo-produto/requirements.md`,
   "Decisões"):
   - "Fonte só, raiz à mão": o modelo do `AGENTS.md` mora em `templates/AGENTS.md`, na
     `economico` e com as lacunas, e a raiz do kit se edita à mão;
   - "Teste da suíte do kit": o conciliador é o `.claude/tests/test_conciliar.py`, que acusa a
     diferença fora da lista de permitidas, e quando ele acusa a conversa de método decide;
   - "Instalar roda o aplicar": o passo 4 do `README.md` roda o `golem.py aplicar`, com a troca
     à mão quando não há Python;
   - "Lista no README";
   - "Mínimas agora": da lista no README, só a cópia do modelo e o `aplicar`.

   Depois, com o Golem central decidido (decisão 11): "Ficam para depois (Recomendado)" e "Sim,
   fundação antes (Recomendado)". A lista do que viaja, o mapa das pastas e a `iniciar-sdd` vão
   para a fase 3, a fundação do Golem central.

   **Consequência:** o repositório do kit passa a rodar na receita `completo`, pelo próprio
   `golem.toml` (`.claude/golem.py`, a receita `completo`). Isso traz revisor e validador no Opus
   a cada grupo, o guardião antes do merge, nenhuma parada entre os grupos e até 4 lições por
   ação. **A decisão 7 ("Econômica no kit") e o "Completo pelo prompt" da decisão 8 deixam de
   valer.**
10. **A ordem das fases novas, em 2026-11-21.** Três fases novas entraram, cada uma por cartão:
    - "lições e índices", com o A1, o D2, o D3 e o C: "Fase própria (Recomendado)"; o D1 veio
      depois, na conversa de método: "Na fase lições e índices (Recommended)";
    - "como o kit fala com o usuário", com as ideias 5 e 6, o T2, o T3, o P1 e o P2: "Fase própria
      (Recomendado)";
    - a separação (decisão 9).

    À pergunta dele, "Essas fases, se houver no roteiro, têm que ser encaixadas em algum lugar.
    Onde você sugere?", o cartão trouxe três ordens. As palavras dele: "Base antes do estilo
    (Recomendado)". A ordem: lições e índices, como o kit fala com o usuário, estilo e
    reaproveitamento, instalação, as fases de configuração e de produto. A migração para o Rojo vem
    depois da instalação, na posição que o retorno do primeiro usuário indicar. O custo aceito: o
    estilo, que é o que o primeiro usuário mais quer, chega mais tarde. A decisão 11 pôs a fundação
    antes de todas.
11. **O Golem central, em 2026-11-21.** Ao primeiro cartão (o kit dentro de cada projeto, um Golem
    central ou estudar antes), ele respondeu "Estudar antes". Para o estudo, as palavras dele: "é
    configurado uma só vez, é fácil de usar, guarda as lições, guarda o estilo do usuário [...] a
    gente só teria que ter um documento, que seria um banco de dados, né, dos projetos que ele
    tem". Depois do estudo da conversa de método e do teste "ligado só nos
    jogos" (o plugin, desligado no usuário e com `true` no projeto, aparece só no jogo), as
    respostas foram:
    - no primeiro turno, "Golem central (Recomendado)";
    - no segundo, à pergunta "Confirma o Golem central, instalado uma vez e ligado só nos
      jogos?", "Confirmo".

    **O que decide:**
    - o kit é instalado uma vez, como plugin, desligado por padrão no usuário e ligado só nos
      jogos (o kit escreve o "ligado" ao registrar o jogo);
    - configurar e atualizar se fazem uma vez;
    - lições e estilo ficam em dois níveis, e o geral só sobe com o ok dele e sem citar o projeto;
    - há um registro dos jogos;
    - o jogo sem Rojo fica numa subpasta do central ou na pasta que ele já tiver.

    **O que continua:** as regras (`AGENTS.md`) ficam em cada jogo, porque o plugin não leva o
    `CLAUDE.md`. O gancho acha o jogo pelo `CLAUDE_PROJECT_DIR`. O Codex fica no modelo de hoje até
    se conferir.

    **A conferir na fase 3:**
    - o modo interativo (o diálogo de confiança);
    - o gancho fora do Golem;
    - o arquivo do "ligado": o `settings.json`, que vai ao git e valeria num repositório de
      cliente, ou o `settings.local.json`, não testado;
    - o `CLAUDE_PLUGIN_ROOT` e a subida do `CLAUDE.md` (as rodadas com login, se precisar).

    Depois, à pergunta "Ponho uma fase 'fundação do Golem central' logo depois da separação?",
    ele respondeu "Sim, fundação antes (Recomendado)". **Consequência no roteiro (seção 7):** a
    fundação é a fase 3. A instalação fica só com o acabamento. As fases de lições, da fala, do
    estilo e da instalação passam a ser desenhadas para o central.
12. **Os dois pontos do roteiro novo, em 2026-11-21.** O PR do roteiro novo deixou dois "a
    conferir", e a conversa de estratégia levou cada um a ele num cartão:
    - "[...] a pergunta 'respostas com emojis?' é da fase 5 [...] Onde ela se grava?" (na configuração
      do central, recomendada × junto dos combinados). As palavras dele: "Na config do central
      (Recomendado)". A preferência vai para a configuração do Golem central, que a fase 3 cria,
      e vale em todos os jogos. A fase 5 não depende da 6;
    - "[...] em que fase sai a primeira release com zip? [...]" (no fim da 7, recomendada × só na 9). As
      palavras dele: "No fim da 7 (Recomendado)". A ideia do zip é dele, de 2026-11-17. O zip leva o plugin, que se instala de uma pasta
      local, sem GitHub (o teste do plugin usou um marketplace numa pasta local). O git local
      continua necessário. O formato das versões, as notas e o "atualizar sem perder nada" ficam
      na fase 9.
13. **O princípio do índice, em 2026-11-22.** É o D1 da fase 4, que ele aprovou com a spec dela
    ("Aprovo", 2026-11-22), com o teto do `AGENTS.md` que ele escolheu configurável ("C:
    configurável").
    - **Contexto:** o acervo cresce com o uso, e o agente não relê tudo antes de cada ação. Até a
      fase 3, três coisas cresciam sem aviso:
      - a lição escrita fora do índice gerado não chegava pelo gancho, e nada avisava;
      - as `refs:` das lições envelheciam (8 das 10 refs com linha do kit apontavam a linha
        errada);
      - o `AGENTS.md`, que entra inteiro em toda conversa, crescia sem medida.
    - **Opções consideradas** (as opções, o gatilho e a evidência abaixo são da conversa da fase,
      dentro do D1 aprovado, e não decisão dele):
      - o índice gerado para tudo: barato a cada ação, mas o documento vivo envelhece entre uma
        regeração e outra;
      - a busca na hora para tudo, sem índice: sempre em dia, mas lê o acervo inteiro a cada ação,
        e cada lição nova deixa o gancho mais lento;
      - o índice gerado para o que muda pouco e a busca na hora para o documento vivo: cada um no
        custo que lhe cabe, com a régua e o aviso do gancho para o índice não envelhecer calado.
    - **Decisão:** a terceira opção. O índice gerado e versionado serve ao acervo que muda pouco e
      tem chave estável, como as lições: a régua o confere, e o gancho percebe a lição que falta
      nele. O documento vivo usa o índice calculado na hora. **Todo documento que cresce com o uso
      nasce com busca.**
    - **Consequências, documento por documento:**

      | Documento | Como cresce | A busca |
      |---|---|---|
      | as lições | uma por armadilha | o índice gerado, e o gancho percebe a que falta nele |
      | as regras de área | uma por lição que vira regra de área | o gancho lê o arquivo na hora |
      | o registro dos jogos | um jogo por registro | a tabela, lida na hora (fase 3) |
      | o catálogo | uma peça por reaproveitamento | nasce com busca, na fase 6 |
      | as specs | uma pasta por fase | a ordem de leitura abre só a pasta da fase |
      | o `AGENTS.md` | regras e combinados | o teto medido (a linha `agents_teto`); a busca na hora, se o teto não bastar |

    - **Gatilho de revisão:** qualquer um destes:
      - um documento que cresce com o uso entra no kit sem busca;
      - o gancho leva mais de 1 s numa ação, medido, por causa da listagem de `docs/licoes/`;
      - o `AGENTS.md` de um jogo passa do teto mesmo depois de as regras de área irem ao
        `docs/regras-de-area.md`.
    - **Evidência de uso:** o que vai mostrar que funciona, a conferir no primeiro jogo que usar a
      fase 4:
      - o aviso "índice defasado" aparece depois de uma lição escrita sem regerar e some depois do
        `--gerar`;
      - a régua avisa a linha nova de uma ref deslocada, em vez de a lição seguir citando a linha
        errada;
      - o `AGENTS.md` do jogo fica abaixo do teto.
14. **O acervo geral numa fase própria, em 2026-11-22.** Na spec da fase 4, a conversa de estratégia
    levou a ele o cartão sobre levar o acervo geral a esta fase ou a uma fase própria. As palavras
    dele: "A: fase própria (Recomendado)". O motivo: com os dois acervos, a fase 4 passaria a G, e a
    regra 2 pede dividir o roteiro em vez de inchar a fase. A fase 4 faz o A1, o D2, o D3, o C e o
    D1 sobre o acervo do jogo, com a pasta das lições num só lugar no código, para a 4b trocar. A
    fase nova, logo depois, faz o acervo geral no central: o gancho lê os dois acervos, a `licao`
    oferece subir a lição com o ok dele e sem citar o projeto, e o projeto de cliente fica marcado e
    não sobe nada.

    Ao cartão do número da fase nova ("4b, sem mudar o resto", recomendada × "5, e o resto sobe um",
    com as fases 5 a 10 passando a 6 a 11), as palavras dele: "4b, sem mudar o resto (Recomendado)"
    (2026-11-22). As citações das fases 5 a 10 não mudam: as do plano e da spec da fase 3 seguem o
    número novo, e as das specs das fases 0 a 2 e da separação, o antigo (os parênteses da seção 7).

**Em aberto, uma de cada vez:**
1. **O nome como marca:** há outros projetos de software chamados Golem. Vale buscar no INPI antes
   de investir em página e identidade (a conferir).
2. **O que é pago, se algo for:** com a MIT mantida, a parte paga, se houver, é serviço ou um
   repositório à parte (o núcleo aberto do cartão da licença).
