---
name: iniciar-sdd
description: Prepara um jogo para o Golem e, no Golem central, registra o jogo e liga o kit nele. Pergunta o nome e se já existe uma pasta, copia o AGENTS.md, as lições e os modelos, liga o plugin no jogo e gera o índice. Use quando o usuário disser "registrar um jogo", "começar um jogo novo", "iniciar SDD neste projeto", "preparar o projeto para specs" ou invocar /iniciar-sdd.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Iniciar um jogo no Golem

**Lê:** o registro dos jogos (`jogos.md`, no Golem central) e a pasta do jogo, para ver o que já
existe.
**Escreve:** na pasta do jogo, **só o que falta**: o `AGENTS.md`, o `CLAUDE.md`, as lições, os
modelos, a `specs/`, o índice, o `.gitignore` e o "ligado" do plugin. No central, a linha do jogo
no `jogos.md`.
**Decide:** o que já existe e não deve ser recriado. Sobrescrever o `AGENTS.md` de um projeto vivo
apaga regra comprada com falha. **Não escreve a constituição**: isso é a skill `constituicao`,
chamada depois, já na pasta do jogo.

Os arquivos do kit (os modelos, a régua, o `golem.py`) moram na pasta do kit, e o caminho dela sai
da pasta desta skill: `${CLAUDE_SKILL_DIR}/../../..`. Nos comandos abaixo, `KIT` é essa pasta. O
Bash não guarda variáveis de uma chamada para a outra: cada bloco a define de novo. Se a primeira
linha disser `ERRO`, pare: sem o kit, nada abaixo funciona.

## 1. Ver o modo e o que existe

```bash
KIT=$(cd "${CLAUDE_SKILL_DIR}/../../.." && pwd)
[ -f "$KIT/.claude/golem.py" ] || echo "ERRO: não achei o kit em $KIT; use a pasta de 'Base directory for this skill', três níveis acima"
raiz=$(cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && pwd)
if [ -f "$KIT/.claude-plugin/plugin.json" ] && [ "$KIT" != "$raiz" ]; then
    echo "modo plugin; central: ${GOLEM_CENTRAL:-$HOME/Golem}"
    cat "${GOLEM_CENTRAL:-$HOME/Golem}/jogos.md" 2>/dev/null
else
    echo "modo cópia: o kit mora no próprio projeto"
fi
```

- **Modo plugin (o Golem central):** siga os passos 2 a 7. Esta conversa roda na pasta do central
  (`~/Golem`), que tem o plugin ligado; o jogo fica noutra pasta, e o trabalho nele é numa sessão
  nova, aberta lá.
- **Modo cópia** (o kit copiado dentro do projeto, como no Codex): vá direto ao passo 8.

## 2. Perguntar

Com botões (no Claude Code, a ferramenta de pergunta), ou em texto numerado onde não houver botões:

1. **"Qual é o nome do jogo?"** O nome entra numa linha da tabela do registro: sem `|` e sem
   quebra de linha.
2. **"Você já tem uma pasta para este jogo?"**
   - "Não: crie em `jogos/<nome>/`, no Golem central (Recomendado)": uma pasta por jogo, dentro do
     central;
   - "Sim, tenho": peça o caminho e confira que ele existe.

Se o jogo já está no registro (a lista do passo 1), diga isso e pergunte se é para conferir o que
falta nele, em vez de registrar de novo.

## 3. A pasta e o git

```bash
# "Não, crie": o caminho é "${GOLEM_CENTRAL:-$HOME/Golem}/jogos/<nome>", e o mkdir -p o cria.
# "Sim, tenho": tire o mkdir -p; a pasta tem de existir, e o comando diz ERRO se não existir.
pasta=$(mkdir -p "<caminho>" && cd "<caminho>" && { pwd -W 2>/dev/null || pwd; }) || echo "ERRO: a pasta <caminho> não existe"
echo "pasta: $pasta"
topo=$(t=$(git -C "$pasta" rev-parse --show-toplevel 2>/dev/null) && cd "$t" && { pwd -W 2>/dev/null || pwd; })
echo "raiz do git: ${topo:-não é um repositório git}"
```

Daqui em diante, `<pasta>` é o caminho **absoluto** que o primeiro `echo` imprimiu (no Windows, na
forma `C:/...`, a mesma que o `registrar` grava no `jogos.md`), escrito por extenso em
cada comando (um `~` entre aspas não se expande, e um caminho relativo muda com o `cd`).

A pasta do jogo precisa ser a raiz de um repositório git: é onde as specs e as lições ganham
histórico, e a régua só indexa o que o git conhece.
- Se não for um repositório, pergunte antes de rodar `git init`. Se o usuário recusar, pare aqui:
  sem git, a régua recusa o índice.
- Se o `--show-toplevel` der **outra** pasta (a do jogo está dentro de outro repositório), diga isso
  e pergunte se o jogo é aquela pasta de fora ou se a de dentro ganha um `git init` próprio.

## 4. Copiar o que viaja

Só o que falta: `cp -n` nunca sobrescreve. Se o jogo já tem algum destes arquivos, mostre a
diferença e proponha juntar à mão.

```bash
KIT=$(cd "${CLAUDE_SKILL_DIR}/../../.." && pwd)
cd "<pasta>"
cp -n "$KIT/templates/AGENTS.md" AGENTS.md
[ -f CLAUDE.md ] || printf '@AGENTS.md\n' > CLAUDE.md
cp -n "$KIT/WORKFLOW.md" WORKFLOW.md
mkdir -p docs/licoes docs/adr .github .claude specs
cp -n "$KIT/docs/operacao-das-conversas.md" docs/
cp -n "$KIT"/docs/licoes/*.md docs/licoes/
cp -n "$KIT/templates/adr.md" docs/adr/modelo.md
cp -n "$KIT/templates/CHANGELOG.md" CHANGELOG.md
cp -n "$KIT/templates/pull_request_template.md" .github/pull_request_template.md
cp -n "$KIT/.claude/LICENSE" .claude/LICENSE
```

- O `.claude/LICENSE` vai porque o `AGENTS.md` e as lições de exemplo são do kit, e a licença MIT
  pede o aviso junto.
- As lições de exemplo são as do kit, como hoje; a escolha das que o kit entrega é de uma fase
  futura.
- No `.gitignore` do jogo, acrescente as linhas que faltarem: `GERENTE.md`,
  `.claude/gancho-falhas.log` e `golem.local.toml`. O passo 5 põe a do "ligado".
- **Nada do kit além disso vai ao jogo:** nem a `.claude/tests/`, nem o `docs/plano-produto.md`,
  nem os scripts (a régua, o `golem.py`, o gancho), que rodam da pasta do kit.

## 5. Registrar e ligar

```bash
KIT=$(cd "${CLAUDE_SKILL_DIR}/../../.." && pwd)
python3 "$KIT/.claude/golem.py" registrar "<pasta>" --nome "<nome>"
```

No Windows, `python` ou `py -3` no lugar de `python3`. Ele põe o jogo no `jogos.md` do central, liga
o plugin no `.claude/settings.local.json` do jogo e tira esse arquivo do git dele. Rodado de novo,
não duplica nada. Se ele disser `ERRO`, mostre a mensagem ao usuário: nada foi escrito.

## 6. O índice das lições e a configuração

```bash
KIT=$(cd "${CLAUDE_SKILL_DIR}/../../.." && pwd)
cd "<pasta>"
git add docs/licoes                          # a régua só indexa as lições que o git conhece
python3 "$KIT/.claude/regua.py" --gerar      # escreve .claude/indice/licoes.yaml
python3 "$KIT/.claude/regua.py" --conferir
python3 "$KIT/.claude/golem.py" aplicar      # o bloco "Como o Golem trabalha aqui", do central
```

A última linha do índice é `total:` com o número de lições de `docs/licoes/` (fora o `README.md`).
Se o `--gerar` recusar porque nenhuma lição está no git, faltou o `git add`.

**Sem Python:** faça à mão o que o `registrar` faz:
- no `.claude/settings.local.json` do jogo, junte `"golem@golem": true` ao `enabledPlugins` (crie o
  arquivo, com `{"enabledPlugins": {"golem@golem": true}}`, se não existir; se existir, guarde o
  resto);
- acrescente `.claude/settings.local.json` ao `.gitignore` do jogo;
- no fim do `jogos.md` do central, uma linha `| <nome> | <pasta> | <data> |`, com a data no formato
  `AAAA-MM-DD`. Sem o `jogos.md`, crie-o antes com o cabeçalho `| Jogo | Pasta | Registrado em |` e
  a linha `|---|---|---|`.
Pule o índice e o `aplicar`, e diga ao usuário que pulou: o bloco do `AGENTS.md` fica com a receita
`economico` do modelo até o `aplicar` rodar.

## 7. Fechar

Mostre a árvore criada no jogo, o que foi preenchido e o que ficou como `<< a preencher >>`. Depois:

- **Abra uma sessão nova do Claude Code na pasta do jogo** (`<pasta>`). Na primeira vez, ele
  pergunta se você confia na pasta: aceite, e só então o Golem liga ali.
- Lá, o próximo passo é a skill `constituicao`.
- O commit no jogo é do usuário.

Termine com o fecho (Resumo, O que você faz agora, Worktree, Espera; formato em
`${CLAUDE_SKILL_DIR}/../../../docs/operacao-das-conversas.md`: o central não tem esse arquivo).

## 8. Na cópia (o kit dentro do projeto)

Com o kit copiado na `.claude/` do projeto (o caminho do Codex), o projeto é a própria raiz:

1. É repositório git? Se não, pergunte antes de rodar `git init`. Projeto que já tem código: a
   constituição descreve o que existe.
2. Crie só o que falta, como no passo 4, com o `KIT` sendo a pasta do kit de onde a `.claude/` veio
   (se a `templates/` não estiver no projeto, pergunte ao usuário o caminho do kit).
3. Rode a régua e o `aplicar` como no passo 6, na raiz do projeto, pelo `.claude/` dele.
4. Se o projeto usa o Codex, rode também `python3 "$KIT/.claude/instalar_codex.py"`: ele gera
   `.agents/skills/`, `.codex/agents/` e `.codex/hooks.json` (detalhe no `README.md` do kit, "Usando
   com o Codex").
5. Avise que skill nova só aparece numa sessão nova, e feche como no passo 7.

O `AGENTS.md` precisa conter a ordem de leitura das specs, os comandos reais do projeto, as
convenções e as regras. Preencha os comandos lendo `package.json`, `Makefile`, `pyproject.toml` ou
equivalente. Não invente comando: se não achar, pergunte.

## Restrições

- Nunca sobrescrever arquivo existente sem mostrar o diff e pedir confirmação.
- Nunca escrever um `CLAUDE.md` no central: a documentação diz que ele subiria para os jogos de
  `jogos/` (nas rodadas da fase 3 não subiu, mas sem ele não há dúvida).
- Não criar `specs/mission.md` vazio: documento vazio dá falsa sensação de spec pronta.
- Não commitar nada sem o usuário pedir.
