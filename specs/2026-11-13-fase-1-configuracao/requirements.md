# Fase 1: configuração e receita econômica — Requisitos

Branch `fase-1-configuracao`, criada de `1f9f827` (a `main` em 2026-11-13, conferida com
`git ls-remote origin refs/heads/main`). Fatos lidos em `1f9f827`, salvo onde se diz outro commit.

## Objetivo

Quem usa o kit escolhe quanto ele gasta: uma receita pronta (`so-eu`, `economico`, que é o padrão,
ou `completo`) e, por cima dela, linhas livres no `golem.toml`. Cada etapa opcional (revisor,
validador, guardião) responde `sempre`, `perguntar` ou `nunca`, e a implementação pode parar a
cada parte para o ok do usuário. Ele configura pedindo "configurar o Golem" e respondendo a
botões. Numa máquina sem Python, o gancho pode ser desligado sem aviso a cada ação
(`docs/plano-produto.md:546`, a linha da fase 1; seção 3, `:182-379`).

Pensado para o primeiro usuário: programa Luau no Roblox Studio, usa pouco IA e está no plano Pro.
O padrão tem de ser barato (`docs/plano-produto.md:12-16`).

## Escopo

- **R1. As decisões de 2026-11-13, registradas e aplicadas.**
  - A seção 8 do `docs/plano-produto.md` ganha as duas decisões, com as palavras do autor do kit
    (ver "Decisões"):
    - as lições `o-windows-muda-o-que-o-sh-recebe-do-python` e
      `trocar-o-localappdata-nao-esconde-o-python-do-agente` ficam em `docs/licoes/` por ora; a
      fase 4 (o plugin) decide o que o kit entrega. Os "Detalhes a conferir na fase"
      (`docs/plano-produto.md:360-379`) ganham esse item, marcado (fase 4);
    - da skill `diagnostico`, fica a conferência do `.gitignore`
      (`specs/2026-11-12-fase-0-python/plan.md:175`) e sai o aviso da linha `python` própria do
      worktree (`plan.md:178`).
  - A skill `.claude/skills/diagnostico/SKILL.md` perde esse aviso: o "Lê" e o "Escreve"
    (`:9-12`), a variável `raiz` (`:24`), que só o `grep` seguinte usa, o `grep` da raiz da sessão
    (`:26`) e o item do passo 1 (`:33-34`). O resto do passo 1 fica, inclusive a `:31`, que diz a
    precedência do gancho. Conferido em `1f9f827`: nenhum teste cita o aviso (`grep` por "raiz da
    sessão", "linha `python` própria", "worktree tiver" e "vence a da pasta" só acha a skill e o
    `plan.md` da fase 0).
  - O gancho continua preferindo a linha da raiz da sessão (`.claude/hooks/gancho.sh`, o
    `ler_linha_python` chamado para a raiz antes da pasta principal). Uma linha `python` escrita à
    mão num worktree passa a vencer sem aviso. Foi o que o autor do kit aceitou: a skill nunca
    grava na raiz, então o caso só nasce de uma linha escrita à mão.
- **R2. O `golem.toml` e o leitor.**
  - O arquivo fica na raiz do projeto, **versionado** (é a escolha do projeto, e não da máquina;
    o caminho do Python continua no `golem.local.toml`, fora do git). Sem `golem.toml`, vale a
    receita `economico`.
  - **O formato** é um subconjunto do TOML, lido por um leitor próprio, em Python 3.8+ (decisão
    2, abaixo). Cada linha é vazia, um comentário (`#` até o fim da linha) ou `chave = valor`. O
    valor é um texto entre aspas duplas ou simples, sem escape, ou um inteiro. Pode haver
    comentário depois do valor. O fim de linha CRLF vale.
  - **As chaves e os valores aceitos** (`docs/plano-produto.md:229-245`):

    | Chave | Valores |
    |---|---|
    | `receita` | `so-eu`, `economico`, `completo` |
    | `revisor`, `validador`, `guardiao` | `sempre`, `perguntar`, `nunca` |
    | `revisor_quando` | `por_fase`, `por_grupo` |
    | `modelo_revisor`, `modelo_validador` | `sonnet`, `opus`, `haiku`, `inherit` |
    | `parar_a_cada_parte` | `sempre`, `nunca` |
    | `conversas` | `uma`, `papeis` |
    | `gancho` | `ligado`, `desligado` |
    | `gancho_teto` | um inteiro de 1 a 10 |

  - **A precedência:** cada linha escrita vale mais que a receita. A chave repetida vale pela
    última linha, no Python e no `sh` (R5).
  - **O validador segue o `revisor_quando`:** com `por_fase`, o validador, quando roda, também roda
    uma vez, sobre a fase inteira; com `por_grupo`, a cada grupo. Não há `validador_quando`.
  - **O erro:** uma chave desconhecida, um valor fora da tabela, uma linha que não é nem
    comentário nem `chave = valor` faz o leitor falhar com o número da linha, a chave e os valores
    aceitos. Quem falha alto é o `aplicar` (R4). O gancho não falha por isso (R5).
- **R3. As três receitas** (`docs/plano-produto.md:216-223`, sem a `equilibrado`, que saiu do
  esboço por falta de quem a peça; `:579-580`). Elas moram no `.claude/golem.py`, que é a fonte, e
  o guia (R8) as mostra:

  | Etapa | `so-eu` | `economico` (o padrão) | `completo` (o fluxo de hoje) |
  |---|---|---|---|
  | `revisor` | `nunca` | `sempre` | `sempre` |
  | `revisor_quando` | `por_fase` | `por_fase` | `por_grupo` |
  | `modelo_revisor` | `sonnet` | `sonnet` | `opus` |
  | `validador` | `nunca` | `nunca` | `sempre` |
  | `modelo_validador` | `opus` | `opus` | `opus` |
  | `guardiao` | `nunca` | `nunca` | `sempre` |
  | `parar_a_cada_parte` | `sempre` | `sempre` | `nunca` |
  | `conversas` | `uma` | `uma` | `papeis` |
  | `gancho` | `ligado` | `ligado` | `ligado` |
  | `gancho_teto` | 2 | 2 | 4 |

  - **A conferir: se o Pro mostra o Sonnet e o Opus** no `/model`. O autor do kit vai perguntar
    ao primeiro usuário. Até a resposta, as receitas ficam como acima, e a spec não depende disso
    para ser aprovada. Quando a resposta vier, ajustam-se as receitas e o critério que pede o
    Sonnet (`validation.md`, verificação manual 1). Segundo a conversa gerente (GER), que o
    conferiu em 2026-11-13 (não reconferido aqui): no app desktop, numa conta que não é Pro, o `/model` mostra "Opus",
    "Fable", "Sonnet" e "Haiku", mais o submenu "Mais modelos"; no terminal, as linhas trazem a
    descrição e podem vir cinza ou com " · Requires usage credits".
- **R4. O `golem aplicar`** (`python3 .claude/golem.py aplicar`, no molde do
  `.claude/instalar_codex.py`, só biblioteca padrão). Ele lê o `golem.toml` (ou a `economico`, sem
  ele), junta a receita e as linhas, e escreve duas coisas:
  1. **o `model:` no frontmatter** de `.claude/agents/revisor.md` (o `modelo_revisor`) e de
     `.claude/agents/validador.md` (o `modelo_validador`). Troca a linha `model:` que houver, ou
     a acrescenta depois do `tools:`. O guardião é o próprio `revisor` (regra 11), com o mesmo
     modelo. Os outros agentes do projeto não mudam;
  2. **o bloco "Como o Golem trabalha aqui" no `AGENTS.md`**, entre as marcas
     `<!-- golem:inicio -->` e `<!-- golem:fim -->`. Troca só o que está entre as marcas. Sem as
     marcas (um `AGENTS.md` juntado à mão), acrescenta o bloco com as marcas no fim do arquivo. No
     `AGENTS.md` do kit, as duas marcas entram à mão, vazias, numa seção "Como o Golem trabalha
     aqui" depois de "Comandos reais", e o conteúdo vem do `aplicar`. O bloco diz, em uma linha por
     etapa: a receita; o revisor (quando, por fase ou por grupo, e o modelo); o validador (que
     segue o mesmo quando); o guardião; o parar a cada parte; as conversas; o gancho e o teto; e
     como agir no `perguntar`. Fica curto, porque o `AGENTS.md` entra em todo turno: até uns 1.200
     bytes.
  - É idempotente: a segunda rodada não muda nada e diz isso.
  - Com o `golem.toml` com erro, falha antes de escrever qualquer arquivo, com a mensagem do R2.
  - **O `aplicar` não mexe no `.claude/settings.json`.** O plano previa gerar ali a chamada do
    gancho com o teto, ou sem o gancho (`docs/plano-produto.md:268-269`). Esta spec troca isso
    pelo R5, em que o próprio gancho lê o `golem.toml` (leitura do agente, ver "Decisões").
  - O `--conferir` do `aplicar` fica para a fase 5 (`docs/plano-produto.md:550`).
- **R5. O gancho obedece ao `golem.toml`.**
  - **Desligado, em `sh`:** o `.claude/hooks/gancho.sh` lê a linha `gancho` do `golem.toml` da
    raiz, antes de procurar o Python. Com o valor `desligado` (entre aspas duplas ou simples), sai
    calado: código 0, sem saída, sem linha no `gancho-falhas.log` e sem rodar o Python. A leitura
    segue a do `ler_linha_python` (`gancho.sh:145-166`: o `read -r`; a chave só vale seguida de
    espaços opcionais e `=`, o que tira o `gancho_teto`; o resto da linha ignorado; o CRLF
    tolerado), com uma diferença: vale a **última** linha `gancho`, como no Python (R2).
    Qualquer outro valor, ou o arquivo ausente, segue como hoje.
  - **O teto, em Python:** o `.claude/hooks/licoes_relevantes.py` lê o teto do `golem.toml` da
    raiz pelo leitor do `golem.py` (a linha `gancho_teto`, ou o da receita), em vez do `TETO = 4`
    fixo (`licoes_relevantes.py:60`). Sem `golem.toml`, o teto é o da `economico`, 2.
  - **Com o `golem.toml` com erro**, o gancho usa o teto da `economico` e segue, sem aviso. Quem
    acusa o erro é o `aplicar` (R4), que a skill de configurar roda.
  - **Sem o `golem.py`** (uma instalação que não copiou a `.claude/` inteira, contra o
    `README.md:95`), o `licoes_relevantes.py` sai com erro, e o lançador avisa como hoje
    ("licoes_relevantes.py saiu com código N"). Não há caminho de reserva: seria peça sem caso
    real (regra 10).
- **R6. As regras e as skills obedecem à configuração.** O bloco do R4 é a fonte; os textos o
  citam, em vez de fixar a etapa:
  - `AGENTS.md`, regra 10 (`:168-171`, "o agente segue grupo a grupo sem pedir licença"): segue
    grupo a grupo, salvo com o parar a cada parte, em que para ao fim de cada grupo e espera o ok;
  - `AGENTS.md`, regra 11 (`:176-196`): o revisor, o validador e o guardião rodam conforme o
    bloco. Com `perguntar`, a etapa vira uma pergunta com botões na hora em que chega, com o custo
    ("abre 1 conversa extra"); em texto numerado onde não houver botões. O caminho rápido e o
    guardião continuam valendo quando a etapa roda. Os comandos do `validation.md` rodam sempre,
    pela conversa, com a linha de resumo lida (regras 4 e 8). A regra 1 não muda: nada nela
    depende da configuração;
  - `.claude/skills/implementar-fase/SKILL.md`: a description (`:3`, "com revisor e validador
    independentes a cada grupo"), o fechamento de grupo (`:29-39`) e o "Fim de grupo não é fim de
    turno" (`:40-46`) seguem o bloco. Com `revisor_quando = "por_fase"`, o revisor (e o
    validador, se rodar) roda uma vez, ao fim do último grupo, sobre o diff da fase inteira. Com o
    parar a cada parte, o grupo termina mostrando o diff e uma linha do que mudou, e o turno acaba
    esperando o ok;
  - `.claude/skills/validar-fase/SKILL.md:51-54`: o revisor, o validador e o guardião do
    fechamento seguem o bloco. Esta skill não estava na linha da fase 1 do plano, mas sem ela a
    `economico` rodaria o guardião no fechamento;
  - `.claude/skills/spec-de-fase/SKILL.md:78-79`: com o parar a cada parte, os grupos do
    `plan.md` têm o tamanho de um arquivo ou de uma função (`docs/plano-produto.md:410`);
  - `docs/operacao-das-conversas.md:156-159`, "Uma mensagem por marco": vale salvo com o parar a
    cada parte;
  - as descrições dos agentes: a do `.claude/agents/validador.md` (`:3`, "Use junto com o revisor,
    antes de marcar um grupo como feito") e a do `revisor.md` (`:3`, "Use antes de marcar um grupo
    como feito") passam a dizer "quando a configuração do projeto pedir";
  - a varredura: o que o `README.md` (`:42`, `:45`) e o `WORKFLOW.md` (`:9`, `:79`, "sem pedir
    licença entre os grupos"; `:84`; `:88`, "Fim de grupo não é fim de turno"; `:106`, o título
    "a cada grupo"; `:110-121`; `:138`) dizem do revisor, do validador e do seguir sem parar passa
    a dizer que depende da receita. O `grep` que acha esses trechos, a rodar de novo no G4:
    `git grep -n -i -e 'a cada grupo' -e 'sem pedir licença' -e 'fim de turno' -e 'marcar um grupo'`;
  - de menor peso, também no G4: a linha "O que é **gerado**" das "Convenções" do `AGENTS.md`
    passa a citar o bloco e o `model:` dos agentes (gerados pelo `aplicar`); o
    `docs/plano-produto.md:244` ("hoje fixo em 4") e a docstring do `.claude/tests/conftest.py:89`
    ("o teto de 4") deixam de dizer que o teto é fixo.
- **R7. O modo sem Python, mínimo** (decisão 3, abaixo):
  - a `implementar-fase` busca as lições com `grep` em `docs/licoes/` no começo da fase e antes de
    rodar os testes, **sempre**, com ou sem gancho (`docs/plano-produto.md:489-493`). Hoje ela
    manda procurar no índice (`implementar-fase/SKILL.md:24-25`), que sem Python envelhece;
  - a skill `licao` diz que pulou a régua quando não há Python (`licao/SKILL.md:105-113`), em vez
    de falhar, e avisa que o índice fica para depois;
  - o bloco do R4, com `gancho = "desligado"`, diz para buscar as lições à mão em `docs/licoes/`
    antes de editar e de rodar os testes.
- **R8. A skill `configurar` e o guia.**
  - `.claude/skills/configurar/SKILL.md`, pedida por "configurar o Golem". Ela faz as perguntas
    com botões (decisão 4), em texto numerado onde não houver botões:
    1. a receita (`so-eu`, `economico`, `completo`), cada opção com o custo numa linha ("1
       revisor por fase, no Sonnet", "nenhuma conversa extra", "até 7 conversas extras numa fase
       de 3 grupos");
    2. o revisor: `sempre`, `perguntar` ou `nunca`;
    3. o parar a cada parte: sim ou não.

    Quem escolhe `so-eu`, ou o revisor `nunca`, ouve numa linha que fica sem a leitura
    independente, e que os comandos do `validation.md` continuam rodando
    (`docs/plano-produto.md:354-358`).
  - Ela escreve o `golem.toml` com a `receita` e as linhas das duas etapas que diferem dela, mais o
    cabeçalho do esboço (`docs/plano-produto.md:230-231`). Se o arquivo já existe, mostra o atual,
    mantém as linhas das chaves que ela não pergunta (`gancho_teto`, `modelo_revisor`, `gancho` e
    as outras) e substitui o resto depois do ok.
  - Ela acha o Python na ordem do gancho (`gancho.sh:177-190`: a linha `python`, o `.venv` da raiz
    e o da pasta principal, o PATH, os lugares do instalador). Sem Python, faz a pergunta da skill
    `diagnostico` (passos 2 a 6). Sem Python nenhum depois disso, deixa o `golem.toml` escrito, diz que o `aplicar` fica
    pendente e que o bloco do `AGENTS.md` continua com a configuração anterior, e oferece o
    `gancho = "desligado"`.
  - Ela roda `"$PY" .claude/golem.py aplicar`, mostra a saída e diz que a configuração nova vale
    numa conversa nova (`docs/plano-produto.md:274-275`).
  - O passo 6 da `diagnostico` (nada achado) passa a oferecer também o modo sem Python, como o
    plano previa "a partir da fase 1" (`docs/plano-produto.md:309`).
  - **O guia**, `docs/guia-configuracao.md`, de uma página: as três receitas (a tabela do R3), cada
    chave com o que faz e o que custa, o que nenhuma receita corta
    (`docs/plano-produto.md:354-358`), como mudar à mão e como fica sem Python.
- **R9. Os testes.** A suíte do ferramental ganha os testes listados no `plan.md` (G2, G3 e G5).
  - Os dois testes de hoje que contam com o teto 4 (`.claude/tests/test_gancho.py:68` e `:91`)
    passam a pôr um `golem.toml` com `gancho_teto = 4` na cópia, e o `Acervo`
    (`.claude/tests/conftest.py:86-102`) copia também o `golem.py`.
  - A `copia_do_kit` (`conftest.py:147-152`) passa a copiar também o `AGENTS.md`, de que os testes
    do `aplicar` precisam.
  - A lista `ARQUIVOS_DO_KIT` do `test_credito.py` (`:25-35`) ganha o `.claude/golem.py` e o
    `.claude/tests/test_golem.py`.
- **R10. O repositório do kit roda na `economico`** (decisão 1). Ele fica sem `golem.toml`, e o
  `aplicar` rodado nele gera o bloco da `economico` no `AGENTS.md` e o `model:` dos dois agentes.
  Um teste confere que o bloco do `AGENTS.md` e o `model:` dos agentes são o que o `aplicar` gera
  a partir do `golem.toml` do próprio projeto. No kit, que não tem `golem.toml`, isso prova que o
  usuário copia a `economico` até a fase 4. No projeto de um usuário que configurou outra receita,
  o teste continua passando. Não é o `--conferir` da fase 5, que é uma opção de linha de comando. Esta fase continua no fluxo de hoje até o merge (revisor e validador a cada grupo,
  guardião no PR, chamados com o modelo `opus` na própria chamada, que vence o frontmatter).
- **R11. A varredura.**
  - a lista de skills esperadas da `iniciar-sdd` (`.claude/skills/iniciar-sdd/SKILL.md:85-87`),
    a tabela "Em volta de tudo" do `WORKFLOW.md` (`:159-169`) e a lista `SKILLS` do
    `.claude/tests/test_credito.py:19` citam a `configurar`, e a skill traz a linha de crédito;
  - o `README.md` ganha, na instalação, o passo opcional de configurar ("peça configurar o
    Golem"), e o mapa das pastas cita o `golem.py` e o `golem.toml`;
  - o `docs/plano-produto.md`, seção 3, passa a dizer que o gancho lê o `golem.toml` (R5), e não
    que o `aplicar` gera a chamada no `settings.json` (`:264-272`); os "Detalhes a conferir" ficam
    como em "Perguntas em aberto";
  - o instalador do Codex, rodado numa cópia, leva a skill nova (`--conferir` ok). O repositório
    do kit não versiona as cópias do Codex (`.agents/` e `.codex/` não estão no `git ls-files` de
    `1f9f827`), como na fase 0.

## Fora de escopo

- **O `effort:` por agente, o `--conferir` do `aplicar`, a página HTML e o medidor:** fase 5
  (`docs/plano-produto.md:550`).
- **O modelo por agente no Codex:** o `instalar_codex.py` leva só o `name` e o `description` do
  frontmatter (`.claude/instalar_codex.py:59-62`), e os nomes de modelo do Codex são outros. As
  cópias do Codex seguem o bloco do `AGENTS.md`, que o Codex lê, mas sem o modelo. Fica para a
  fase 6, a paridade do Codex (melhoria 13).
- **O "pulado sem Python" nas outras skills que rodam a régua** (`validar-fase/SKILL.md:46`,
  `auditar-specs/SKILL.md:50`, `sessao-gerente/SKILL.md:97`): fase 4 (decisão 3). O G1 o
  registra nos "Detalhes a conferir" do `docs/plano-produto.md`, marcado (fase 4), para que não
  suma: a seção 5(b) (`:493`) diz que os passos de régua das skills dizem que foram pulados.
- **Uma receita intermediária**, como a `equilibrado`: entra quando aparecer quem a use.
- **O vocabulário de equipe só na `completo`** (o guia do primeiro dia, melhoria 9): fase 4. A
  linha `conversas` desta fase só diz, no bloco, se os papéis de `docs/operacao-das-conversas.md`
  são o fluxo ou são opcionais.
- **Avisar que um `golem.toml` com erro foi ignorado pelo gancho:** fora. O `aplicar` acusa o
  erro. Um aviso do gancho a cada ação seria a peça que a fase 0 tirou.
- **Ler o `golem.toml` da pasta principal num worktree:** fora. O `golem.toml` é versionado e
  viaja com a branch.

## Decisões

- **A spec aprovada, com um commit por grupo.** As palavras dele: "Aprovo", à pergunta "Aprova a
  spec da fase 1, com um commit por grupo na branch?" (2026-11-13). Com ela, ficam aprovadas as
  leituras do agente listadas abaixo.
- **As respostas da entrevista desta spec** (2026-11-13). O autor do kit escolheu a opção
  recomendada nas quatro perguntas:
  1. **"Econômica no kit"**: o repositório do kit roda na `economico` depois desta fase, porque o
     `AGENTS.md` dele é o que o usuário copia até a fase 4. As fases 2 em diante do kit rodam com
     um revisor só, no Sonnet, uma vez por fase, e servem de teste real da receita. Descartado: o
     kit na `completo`, que faria o usuário receber o bloco da `completo` e precisar de um passo a
     mais na instalação, e de Python para sair dele.
  2. **"Leitor próprio, 3.8+"**: o `golem.toml` aceita só `chave = valor` e comentários, e o
     mínimo continua 3.8. Descartado: subir para 3.11 e usar o `tomllib`, que deixaria sem gancho
     quem tem Python 3.8 a 3.10. Resolve o item do `tomllib` (`docs/plano-produto.md:361-362`).
  3. **"Mínimo"** para o modo sem Python: a `implementar-fase` e a `licao` (R7). Descartado: as
     cinco skills com régua agora.
  4. **"Receita + duas etapas"** na skill de configurar (R8). Descartado: só a receita.
- **As decisões de 2026-11-13, da conversa gerente.** As palavras do autor do kit: "Sim, as
  quatro", aceitando as quatro recomendações da GER (as duas lições ficam em `docs/` por ora; da
  `diagnostico`, fica a conferência do `.gitignore` e sai o aviso do worktree). Entram no R1.
- **Leituras do agente, para aprovar com a spec:**
  - **O gancho lê o `golem.toml`; o `aplicar` não mexe no `settings.json`** (R4 e R5). O plano
    previa gerar a chamada do gancho com o teto no `settings.json`. Lido direto, há uma peça
    gerada a menos, e o `instalar_codex.py`, que lê o comando do gancho no `settings.json` para
    fazer o `hooks.json` do Codex (`.claude/instalar_codex.py:77-84`), não muda. O custo é o
    gancho abrir um arquivo pequeno a cada ação, sem token nenhum.
  - **A `validar-fase` entra no R6**, embora a linha da fase 1 não a cite: sem ela, a
    `economico` rodaria o guardião e o validador no fechamento.
  - **A regra 1 não muda.** O plano diz que as regras 1, 10 e 11 citam o bloco
    (`docs/plano-produto.md:270-271`), mas a regra 1 não tem nada que dependa da configuração. Os
    grupos pequenos do parar a cada parte vão para a `spec-de-fase`.
  - **O revisor por fase roda no fim do último grupo**, sobre o diff da fase inteira, dentro da
    `implementar-fase`, antes da `validar-fase`.
  - **A branch se chama `fase-1-configuracao`**, no padrão da fase 0, renomeada da que o app criou
    para o worktree.

## Contexto

- **Os agentes não fixam modelo hoje:** o frontmatter de `.claude/agents/revisor.md:1-5` e de
  `validador.md:1-5` tem só `name`, `description` e `tools`. O Claude Code aceita `model:` no
  frontmatter, e a precedência é a chamada, o frontmatter, a variável
  `CLAUDE_CODE_SUBAGENT_MODEL` e o modelo da conversa (`docs/plano-produto.md:125-128`).
- **O teto do gancho** é o `TETO = 4` (`.claude/hooks/licoes_relevantes.py:60`), usado no laço da
  entrega (`:497`). A raiz do projeto é `Path(__file__).resolve().parents[2]` (`:56`).
- **O lançador** acha a raiz pelo próprio caminho (`gancho.sh:37`) ou pelo git, e lê a linha
  `python` com o `ler_linha_python` (`gancho.sh:139-166`), cujo padrão o R5 repete.
- **O que já fixa o fluxo de hoje:** a regra 11 (`AGENTS.md:176-196`), a regra 10 (`:168-171`), a
  `implementar-fase` (`SKILL.md:29-46`), a `validar-fase` (`SKILL.md:51-54`) e o fecho
  (`docs/operacao-das-conversas.md:156-159`).
- **O custo medido** que a configuração ataca: o revisor e o validador, com medianas de ~127 mil e
  ~107 mil tokens de entrada nova por rodada (`docs/plano-produto.md:71-74`). Numa fase de 3
  grupos, a `completo` roda 7 subagentes e a `economico`, 1 (`:341-352`).
- **A suíte do ferramental** dá hoje `96 passed` em `1f9f827` (mensagem da GER, a reconferir no G2
  antes do primeiro teste novo).

## Padrões a seguir

- **O `golem.py`** segue o `.claude/instalar_codex.py`: o cabeçalho com a linha de crédito e o
  uso, `RAIZ` pelo caminho do arquivo, as funções puras que dizem o que deve ser escrito, o
  `main(args)` com a mensagem de uso e só biblioteca padrão.
- **Os testes do `golem.py`** seguem o `.claude/tests/test_codex.py` (a `copia_do_kit`, a
  segunda rodada que não muda nada).
- **Os testes do lançador** seguem `.claude/tests/test_gancho.py` (o `_path_sem_python`, o
  `_repassador` e o `_rodar_lancador`, da fase 0).
- **A skill `configurar`** segue a `.claude/skills/diagnostico/SKILL.md`: o frontmatter com
  `name`, `description` e `license`; o "Lê", "Escreve" e "Decide"; as perguntas com botões e a
  versão em texto numerado.

## Notas do usuário

- "tinha que ser fácil de customizar para ele"; "imagina que ele nem quer usar o revisor no final
  do código, o ideal seria aparecer para ele, tipo, você quer usar o revisor?"; "a gente manteria
  os nossos recomendados, com várias configurações diferentes já prontas, mas é livre para ele
  configurar como ele quiser" (2026-11-12, `docs/plano-produto.md:184-188`).
- "Sim, as quatro" (2026-11-13, às recomendações da GER sobre as lições e a `diagnostico`).

## Teto de gasto

Nenhum: a fase não gasta dinheiro. A fase de teste da verificação manual roda no plano do autor do
kit.

## Perguntas em aberto

- **Se o Pro mostra o Sonnet e o Opus no `/model`:** a conferir, com o primeiro usuário (R3). Não
  bloqueia a aprovação.
- **Se o `systemMessage` do gancho de um subagente aparece ao usuário**
  (`docs/plano-produto.md:375-376`, marcado fase 1): esta fase não depende disso, porque o
  `gancho = "desligado"` sai calado e o resto não muda o aviso. Proposta: movê-lo para a fase 4
  (o diagnóstico completo), no G1.
- **Se o formato de agente do Codex aceita modelo por agente** (`docs/plano-produto.md:363`):
  fica para a fase 6 (ver "Fora de escopo"), movido no G1.
