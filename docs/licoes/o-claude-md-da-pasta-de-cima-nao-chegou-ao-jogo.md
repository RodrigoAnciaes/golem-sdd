---
id: o-claude-md-da-pasta-de-cima-nao-chegou-ao-jogo
data: 2026-11-22
area: processo
tipo: premissa-falsa
custo: "uma decisão da spec da fase 3 apoiada na documentação, desfeita por 4 rodadas com login"
gatilho: "a spec da fase 3 leu na documentação que o CLAUDE.md sobe a toda pasta acima e tirou disso que o do Golem central chegaria a cada jogo de ~/Golem/jogos/"
refs:
  - "specs/2026-11-21-fase-3-fundacao-central/validation.md (L4 e L5)"
  - "specs/2026-11-21-fase-3-fundacao-central/requirements.md (R3, o central sem CLAUDE.md)"
gatilhos:
  - '(^|/)CLAUDE\.md$'
  - '\.claude-plugin/'
---

**O que se achava:** que um `CLAUDE.md` posto numa pasta acima de um projeto entra em toda sessão
aberta nele, porque a documentação do Claude Code diz que ele lê o `CLAUDE.md` "from your current
working directory and every directory above it".

**O que é:** no Claude Code 2.1.330, com um `CLAUDE.md` com uma marca no Golem central, a marca não
chegou a nenhuma sessão aberta num jogo de `~/Golem/jogos/`: nem num jogo com git, nem numa pasta
sem git, nem no `-p`, nem no modo interativo depois de aceitar a confiança na pasta (4 rodadas). Ela
também não aparece no texto que foi ao modelo, gravado na transcrição. O motivo não se conferiu.

**Como perceber da próxima vez:**
1. Antes de desenhar em cima de como o Claude Code carrega um arquivo (o `CLAUDE.md`, uma skill, um
   settings), prove com uma marca: um texto único no arquivo, uma rodada que pergunta por ele sem
   ferramentas, e a busca da marca na transcrição da sessão (`<config>/projects/<pasta>/*.jsonl`).
2. A leitura da documentação entra na spec como "a conferir" até essa rodada. Uma frase genérica
   ("every directory above it") não diz o que acontece com uma pasta não confiável, um repositório
   git ou o `-p`.
