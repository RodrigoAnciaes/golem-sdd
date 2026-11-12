# Plano de produto do Golem

Rascunho de 2026-11-12. As citações `arquivo:linha` se referem ao commit `c880a17`, o kit antes
deste plano. O commit `ccca28b`, do crédito, pôs uma linha no topo de vários arquivos e uma seção
no README. As linhas citadas desses arquivos que vêm depois da inserção andaram uma: o
`gancho.sh:99` é hoje o 100, e o `README.md:228`, o 229; o `README.md:74` e o `:83` não mudaram.

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
| 2 | **Gancho que acha o Python e falha uma vez só:** a configuração pergunta se ele tem Python e onde, e o gancho usa esse caminho ou procura também onde o instalador oficial põe o Python; quando falha, avisa uma vez, em palavras simples, cita a lição e dá o conserto em uma linha. Numa máquina sem Python nenhum, ele pode ser desligado: as skills passam a mandar buscar as lições em momentos fixos (o modo sem Python, de reserva) | fácil, custo | A | P |
| 3 | **Receitas prontas, escolha por etapa e configuração por conversa:** três receitas recomendadas (`so-eu`, `economico`, `completo`); cada etapa opcional responde `sempre`, `perguntar` ou `nunca`; ele configura pedindo "configurar o Golem" e respondendo a botões; e o "guia de configuração", de uma página, explica cada escolha | custo, fácil | A | M |
| 4 | **Pacote Roblox mínimo:** os comandos reais de um projeto Rojo, os gatilhos `.luau`/`rojo`/`selene`/`stylua`, um `tech-stack` modelo, critérios com playtest passo a passo e o uso do Studio MCP | Roblox | A | M |
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
# gancho_teto      = 2             # lições novas por ação (hoje fixo em 4)
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
o gancho injeta, um dos itens do critério "customizável", e é uma linha. O gancho continua
rodando antes de comandos em todas as receitas: as três lições do kit disparam por comando, e quem
roda os comandos do `validation.md` (a conversa, e o validador quando ele existe) precisa delas.

**Como a configuração chega ao agente, sem custo novo de leitura.** O `golem aplicar`
(`python .claude/golem.py aplicar`, no molde do `instalar_codex.py`) junta a receita e as linhas
do usuário e gera três coisas:
1. o `model:` e o `effort:` no frontmatter de `.claude/agents/*.md`, que o Claude Code respeita;
2. no `.claude/settings.json`, a chamada do gancho com o teto (o `licoes_relevantes.py` passa a
   ler o teto de uma variável, em vez do `TETO = 4` fixo) ou sem o gancho;
3. um bloco curto e **gerado** no `AGENTS.md`, "Como o Golem trabalha aqui", que as regras 1, 10
   e 11 passam a citar. Como o `AGENTS.md` já entra em todo turno, o agente sabe a configuração
   sem abrir arquivo novo, e sabe em que momento perguntar.

A skill de configurar escreve o `golem.toml` e roda o `aplicar` por ele. Mudou a configuração,
abre-se uma conversa nova. Com o plugin da fase 4, a skill vira `/golem:configurar`.

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
  skill de configurar (fase 1) e, com o plugin, no `comecar` e no `diagnostico` (fase 4);
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
| **Não** | faz mesmo assim uma busca rápida, porque quem acha que não tem pode ter (a lição acima). Se achar, pergunta: "Achei um em `...`. Quer usar este?" Se não achar, oferece o comando de instalação ou o modo sem Python |

A busca rápida é olhar se dois ou três arquivos existem. Na skill, ela custa uma chamada de
ferramenta, poucas centenas de tokens; no gancho, nenhum. Os lugares de costume, no Windows, são
os do instalador oficial: na instalação "só para mim",
`%LOCALAPPDATA%\Programs\Python\Python3*\python.exe` e o `py.exe` de `...\Python\Launcher`; na
"para todos os usuários", `%ProgramFiles%\Python3*` (a conferir).

**Depois, o gancho não pergunta nada:** procura nesta ordem:
1. (novo) o caminho da linha `python` do `golem.local.toml`, lida em `sh`. A leitura do
   `golem.toml` pelo `gancho.sh`, para o `gancho = "desligado"`, também é nova, da fase 1;
2. o `.venv` do projeto e o da pasta principal (como hoje);
3. o PATH (como hoje);
4. (novo) os lugares do instalador oficial.

Um caminho que não roda mais (o Python foi desinstalado) é tratado como os candidatos de hoje, que
só valem se rodarem um Python 3.8+: o gancho passa ao passo 2. Se nada mais for achado, o aviso
diz que a linha `python` não roda, sem citar o caminho (o `avisar` do `gancho.sh` encerra o gancho
sem entregar lição nenhuma e só aceita texto fixo, sem barra invertida, dentro do JSON). Avisar isso sem cortar as lições,
quando o passo 2 ou outro acha um Python, pediria uma peça nova (ver "Detalhes a conferir").

O aviso de falha diz onde procurou, cita a lição pelo id e manda rodar o diagnóstico, em vez de
dar a entender que o Python não existe. Isso importa porque o gancho não consegue entregar a lição
justamente quando não acha o Python.

**A linha `python` vai entre aspas simples** (`python = 'C:\...\python.exe'`). No TOML, as aspas
simples fazem uma string literal, sem escape. O `gancho.sh` lê com `read -r`, que não trata a
barra invertida (conferido no Git Bash em 2026-11-12: com `-r`, o caminho chega inteiro; sem ele,
as barras somem). Um caminho com aspa simples dentro não cabe nesse formato: a skill o recusa e
pede outro (a conferir).

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

**Detalhes a conferir na fase:**
- o `tomllib` só existe no Python 3.11+, e o kit pede 3.8+: ou se sobe o mínimo, ou o arquivo usa
  só `chave = valor`, que se lê com meia dúzia de linhas;
- se o formato de agente do Codex aceita modelo por agente;
- como o `golem.local.toml` chega a um worktree: ele fica fora do git, como o `.venv`, então o
  `gancho.sh` o procura também na pasta principal do repositório, do mesmo jeito que já procura o
  `.venv` (`gancho.sh`, `achar_venv` e o `--git-common-dir`);
- o aviso da linha `python` que não roda, quando outro Python é achado: ou nenhum aviso (o gancho
  segue com o Python achado), ou um aviso que não interrompe e deixa a lição seguir. E, se o aviso
  de falha for listar os lugares onde procurou, como pôr caminho com barra invertida no JSON do
  aviso, que hoje só aceita texto fixo (`gancho.sh`, o comentário do `avisar`);
- no `sh` do Git Bash, o `%ProgramFiles%` do Windows chega como `$PROGRAMFILES`, em maiúsculas
  (`$ProgramFiles` sai vazio); o `$LOCALAPPDATA` chega com esse nome (conferido em 2026-11-12).

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
do kit (o gancho, a régua e o instalador) é Python. A busca nas lições e nos documentos não
precisa dele: o Claude Code tem a própria busca. Sem Python, o que se perde é:
- a entrega automática das lições na hora certa (o gancho);
- a geração e a conferência do índice: a `licao` gera o índice, e o `regua.py --conferir` é
  critério na `validar-fase`, na `auditar-specs` e na `sessao-gerente`. Sem Python, o índice
  envelhece;
- o `aplicar` e o instalador do Codex.

Há quatro saídas, e elas não se excluem:
- **(a)** a configuração pergunta se ele tem Python e onde, e confere com uma busca rápida nos
  lugares do instalador oficial; o gancho usa o caminho registrado e, sem ele, procura nesses
  mesmos lugares (seção 3, "Primeiro perguntar, depois procurar"). Só se nada for achado, a
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
  `golem.toml` com a receita `economico`). Preenche as lacunas `<< >>` por entrevista ("como você
  roda o jogo?", "usa Rojo?", "onde estão seus módulos?"), passa pela configuração com botões (com
  a pergunta do Python) e termina testando o gancho.
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

Cada fase é uma branch, mergeável sozinha, com spec aprovada antes (regra 1). A ordem põe primeiro
o que o primeiro usuário sente no primeiro dia. A instalação vem depois porque, no começo, o autor
do kit pode instalar com ele. A ordem foi confirmada pelo autor do kit (seção 8, item 3).

| Fase | Entrega | Melhorias | Tamanho | Pronto quando |
|---|---|---|---|---|
| **1. Configuração e receita econômica** | as três receitas e o `golem.toml` com as linhas livres; o `sempre`/`perguntar`/`nunca` de cada etapa; a skill de configurar com botões (em texto onde não houver botões) e o guia de configuração; um `golem aplicar` mínimo, em `.claude/golem.py` (o bloco "Como o Golem trabalha aqui" no `AGENTS.md`, o `model:` dos agentes e o gancho ligado ou não, com o teto); as regras 1, 10 e 11, a `implementar-fase`, o fecho em `docs/operacao-das-conversas.md:156` e a descrição do `validador` obedecendo à configuração; o gancho que falha uma vez só; a pergunta do Python na skill de configurar e a linha `python` do `golem.local.toml` (que entra no `.gitignore`); o `gancho.sh` achando o Python fora do PATH (a linha `python`, depois os lugares do instalador oficial); e o modo sem Python (o `gancho.sh` lendo o `gancho = "desligado"`, a busca direto em `docs/licoes/`) | 1, 2, 3 | M | numa fase de teste com a receita `economico`, a conversa para a cada grupo, roda um revisor só, no Sonnet, e o aviso do gancho aparece uma vez; com `revisor = "perguntar"`, a pergunta aparece com botões no fim da fase; a skill de configurar, respondida de ponta a ponta, deixa o `golem.toml` e o que o `aplicar` gera de acordo com as respostas; numa máquina com o Python fora do PATH (só os atalhos da loja no PATH), o gancho o acha e entrega a lição; respondendo "Não" à pergunta do Python nessa máquina, a skill o acha e pergunta se usa; com a linha `python` apontando para um Python fora dos lugares de costume, o gancho entrega a lição; com ela apontando para um caminho que não roda e nenhum outro Python achado, o aviso diz que a linha `python` não roda; e, com `gancho = "desligado"` numa máquina sem Python, nenhum aviso do gancho aparece |
| **2. Roblox mínimo** | os modelos de tech-stack e de comandos para Rojo, os gatilhos, duas lições de exemplo e os testes pelo Studio MCP | 4 | M | num place Rojo de exemplo, uma fase pequena vai da spec ao validado, com o resumo dos testes lido no console |
| **3. Estilo e reaproveitamento** | a skill de estilo, o catálogo, a pergunta na entrevista e o revisor checando o estilo e o reaproveitamento | 5, 6 | M | com 3 programas do usuário, as regras saem com exemplos do código dele, e o revisor acusa um módulo duplicado de propósito |
| **4. Instalação fácil** | o plugin (com o gancho achando a raiz pelo projeto), o `comecar`, o `diagnostico` e o guia do primeiro dia | 7, 9 | M | uma pessoa sem o kit instala e começa a primeira spec seguindo só o guia do primeiro dia, num Windows sem Python instalado de antemão |
| **5. Configuração completa e medidor** | o esforço por papel, o `golem aplicar --conferir`, a página HTML de configuração (se a fase 1 mostrar que a conversa com botões não basta), o medidor e a busca uniforme no índice | 8, 10, 12 | M | trocar a `receita` e rodar o `aplicar` muda o que a fase 1 gera, o `--conferir` acusa a divergência, e o medidor mostra o gasto por papel antes e depois |
| **6. Produto** | versões, notas de versão, como atualizar, a página do kit, a paridade do Codex e a fonte dele depois do plugin | 11, 13 | M–G | um usuário atualiza de uma versão para a outra sem perder as lições nem a configuração |

**Perguntas ao primeiro usuário.**
- **Antes da fase 1:** qual modelo o Pro dele mostra no `/model` (as receitas fixam o Sonnet e o
  Opus, e o "pronto" da fase 1 pede o Sonnet) e se ele já tem Python instalado, e onde (o
  trabalho do Python é da fase 1).
- **Antes da fase 2:** se ele usa Rojo ou só o Studio e que framework de teste usa.

---

## 8. Decisões do autor do kit

**Tomadas:**
1. **A licença, em 2026-11-12.** O cartão recomendou manter a MIT. As palavras dele: "Ok, eu
   quero manter a MIT só que eu só quero pelo menos reforçar que me deem os créditos" e, sobre
   como reforçar, "MIT, com aviso por arquivo". Aplicado no commit `ccca28b`: o nome completo no
   `LICENSE`, a cópia em `.claude/LICENSE`, a linha de crédito em cada skill, agente e script, a
   seção "Licença e crédito" do README e o teste que acusa crédito ausente.
2. **A configuração, em 2026-11-12.** O pedido está na seção 3. As palavras dele sobre a
   recomendação: "sim, pode seguir sua recomendação". Entra na fase 1 (seções 3, 5 e 7). Os pontos
   aceitos:
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
   da seção 7 fica como está.
4. **Perguntar antes de procurar o Python, em 2026-11-12.** A proposta veio dele (as palavras
   estão na seção 3, "Primeiro perguntar, depois procurar"). As palavras dele sobre os ajustes do
   agente: "sim, pode atualizar o plano". Os ajustes aceitos:
   - a pergunta vem na configuração, porque o gancho não pode perguntar;
   - o botão "Não sei", ao lado do sim e do não;
   - com "Não", uma busca rápida antes de mandar instalar, por causa da lição
     `sem-python-no-path-nao-e-maquina-sem-python`;
   - a linha `python` de volta, entre aspas simples, para guardar o caminho que o usuário informar;
   - a ordem de procura do gancho: a linha `python`, o `.venv`, o PATH e os lugares do instalador.

   Mudança depois do ok, para a spec da fase 1 confirmar: a linha `python` foi para um
   `golem.local.toml`, fora do git, e não para o `golem.toml`. O caminho é desta máquina, está
   errado em qualquer outra e expõe o nome do usuário.

**Em aberto, uma de cada vez:**
1. **Uma fase 0 para o gancho achar o Python?** A busca do Python nos lugares do instalador não
   depende do `golem.toml` e conserta já a falha vista. Ela pode sair numa fase pequena antes da 1
   (só o `gancho.sh`, o aviso e um teste) ou ficar dentro da 1, que já é a maior do roteiro. O
   porém: a fase 0 traria só o passo 4 da ordem, a busca sem perguntar, que é o que o autor do kit
   quis evitar ("senão a gente vai buscar à toa"). A pergunta e a linha `python` ficariam na 1.
2. **O nome como marca:** há outros projetos de software chamados Golem. Vale buscar no INPI antes
   de investir em página e identidade (a conferir).
3. **O que é pago, se algo for:** com a MIT mantida, a parte paga, se houver, é serviço ou um
   repositório à parte (o núcleo aberto do cartão da licença).
