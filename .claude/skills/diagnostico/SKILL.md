---
name: diagnostico
description: Faz o gancho das lições achar o Python da máquina. Pergunta ao usuário se ele tem Python e onde, procura nos lugares de costume do Windows, grava o caminho no golem.local.toml da pasta principal e testa o gancho. Use quando aparecer o aviso "Gancho das lições falhou (nenhum Python 3.8+ encontrado...)", quando o usuário disser "diagnóstico do Golem", "o gancho não acha o Python", "configurar o Python" ou invocar /diagnostico.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Diagnóstico do Golem: o Python do gancho

**Lê:** o `golem.local.toml` da pasta principal do repositório, se existir.
**Escreve:** a linha `python = '<caminho>'` do `golem.local.toml` da pasta principal e, com o ok do
usuário, a linha `golem.local.toml` no `.gitignore`, se faltar, e, com o sim ao modo sem Python, a
linha `gancho = "desligado"` no `golem.toml` da raiz da sessão (que viaja no git) e a linha do
gancho no bloco "Como o Golem trabalha aqui" do `AGENTS.md`. Não instala nada.
**Decide:** nada sozinha. Pergunta antes de procurar, e grava o que achou só depois do ok do
usuário. Esta é a versão mínima: o resto do diagnóstico (o `sh`, o git, o índice) fica para depois.

Por que existe: o gancho procura o Python na linha `python`, no `.venv`, no PATH e nos lugares do
instalador do Windows. Fora disso, ele não acha, e o aviso dele diz onde procurou, **não** que a
máquina não tem Python (lição `sem-python-no-path-nao-e-maquina-sem-python`).

## 1. Ver o que já existe

```bash
principal=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
grep -Hn '^[[:space:]]*python[[:space:]]*=' "$principal/golem.local.toml" 2>/dev/null
git -C "$principal" check-ignore -q golem.local.toml && echo ignorado || echo "NÃO ignorado"
```

- A pasta principal é a do repositório, e não a do worktree: o `golem.local.toml` não viaja para
  os worktrees, e o gancho o procura lá **se a raiz da sessão não tiver a linha**.
- Se já há uma linha `python` na pasta principal, ponha-a no texto da pergunta do passo 2, com o
  aviso de que ela será substituída no fim.
- Se o arquivo **não** está ignorado pelo git, diga isso no texto da pergunta do passo 2 e, no
  pedido de ok para gravar, proponha também a linha `golem.local.toml` no `.gitignore`. O caminho é
  desta máquina e traz o nome do usuário.

## 2. Perguntar

Pergunte com botões (no Claude Code, a ferramenta de pergunta), ou em texto numerado onde não
houver botões: **"Você tem Python instalado nesta máquina?"**

1. Sim, e sei onde
2. Sim, mas não sei onde
3. Não sei
4. Não

## 3. Agir conforme a resposta

| Resposta | O que fazer |
|---|---|
| Sim, e sei onde | Peça o caminho do `python.exe` (ou do `python`). Tire as aspas duplas, se ele colar com elas. Se o caminho tiver aspa simples (`'`), recuse e peça outro: a linha não a aceita. Teste (passo 4). Se rodar, grave (passo 5). Se não rodar, ofereça a busca numa pergunta que diz, no próprio texto, que o caminho não rodou. |
| Sim, mas não sei onde | Procure (passo 4). Peça o ok para gravar com o que achou no texto da pergunta, e grave depois do ok. Se não achar nada, dê o comando de instalação (passo 6). |
| Não sei | O mesmo que a anterior. |
| Não | Faça a mesma busca. Se achar, pergunte: "Achei um em `...`. Quer usar este?". Se não achar, dê o comando de instalação (passo 6). |

## 4. Procurar e testar

Um candidato só vale se rodar um Python 3.8+. O teste imprime o caminho completo do Python que
rodou, e **é esse caminho que se grava**, sempre: o gancho só aceita um arquivo que existe, e não um
nome solto (`python3`) nem um caminho relativo.

```bash
"<candidato>" -c 'import sys; sys.exit(1) if sys.version_info < (3, 8) else print(sys.executable)'
```

Para o `py.exe`, o lançador, ponha `-3` depois do caminho: a linha `python` não leva o `-3`, e por
isso se grava o Python que ele acha, e não o próprio `py.exe`.

A busca olha o PATH e os lugares do instalador oficial do Windows, que costumam ficar fora dele:

```bash
command -v python3 python py
ls "$LOCALAPPDATA"/Programs/Python/Python3*/python.exe \
   "$LOCALAPPDATA"/Programs/Python/Launcher/py.exe \
   "$PROGRAMFILES"/Python3*/python.exe 2>/dev/null
```

- Teste cada um. Um `python` em `WindowsApps` costuma ser o atalho da Microsoft Store, que não
  roda sem o Python da loja instalado: o teste decide.
- Fora do Windows, a busca é só o PATH.

## 5. Gravar

No `golem.local.toml` da pasta principal, troque a linha `python` que já houver. Se o arquivo
existe sem ela, acrescente-a. Se não existe, crie-o com:

```toml
# Gravado pela skill diagnostico do Golem. Fica fora do git: o caminho é desta máquina.
python = 'C:\Users\<usuario>\AppData\Local\Programs\Python\Python312\python.exe'
```

O caminho vai entre **aspas simples**: no TOML, elas guardam a barra invertida do Windows como
está. Aspas duplas tornam o `\U` inválido. Um caminho com aspa simples (`'`) não se grava, venha
ele do usuário ou da busca: o gancho o cortaria nela. Diga isso ao usuário e peça outro Python.

## 6. Nada achado: o comando de instalação

Mostre o comando e peça que o **usuário** o rode no terminal dele. Não o rode você.

```bash
winget install -e --id Python.Python.3.14 --scope user
```

- O número no id muda a cada versão do Python: `winget search Python.Python` lista as que existem.
- O `--scope user` instala só para este usuário, sem pedir administrador. Depois, o passo 4 acha o
  Python novo, onde quer que ele tenha ficado.
- Sem o `winget`, o instalador está em python.org. Fora do Windows, use o do sistema
  (`brew install python`, `sudo apt install python3`).

Depois da instalação, volte ao passo 4.

Se o usuário não quiser instalar agora, ofereça o **modo sem Python**: a linha
`gancho = "desligado"` no `golem.toml` da raiz desliga o gancho e o aviso, e as lições passam a
ser buscadas à mão em `docs/licoes/`. A mudança (a linha e o arquivo em que ela entra) vai no
texto da própria oferta. Com o sim, ponha a linha `gancho = "desligado"` no `golem.toml` da raiz
(crie o arquivo se não existir); o resto da
configuração fica como está (`docs/guia-configuracao.md`). Sem Python, o `aplicar` não roda: troque
à mão, no bloco "Como o Golem trabalha aqui" do `AGENTS.md`, só a linha do gancho por esta, que é
a que o `aplicar` gera:

```markdown
- **Gancho das lições:** desligado: antes de editar um arquivo ou rodar um comando, procure em `docs/licoes/` as lições que citam o nome dele.
```

Com o modo sem Python, **pule o passo 7**: o gancho desligado sai vazio sem procurar o Python, e
a saída vazia não diz nada sobre ele. Diga ao usuário que as lições ficam para buscar à mão em
`docs/licoes/`. Quando esta pergunta vem pela skill `configurar`, é ela quem oferece o modo sem
Python.

## 7. Testar o gancho

```bash
echo '{"tool_input":{"command":"pytest -q"}}' | sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"
```

- A entrada vai **sem** `session_id`: assim, o gancho não esconde a lição nem o aviso numa segunda
  rodada.
- Leia o motivo entre parênteses, e não só a palavra "falhou":
  - "nenhum Python 3.8+ encontrado": o gancho ainda não acha o Python. Volte ao passo 2,
    com o motivo no texto da pergunta.
  - "licoes_relevantes.py saiu com código N": o Python foi achado e rodou. Mostre o motivo ao
    usuário; ele fica para o diagnóstico completo.
  - "não achei .claude/hooks/licoes_relevantes.py": o gancho parou antes de procurar o Python, e o
    teste não diz nada sobre ele. Mostre o motivo ao usuário: falta o arquivo do kit.
- Se a saída traz uma lição, ou sai vazia, o Python rodou. Vazia quer dizer só que nenhuma lição
  casa com `pytest` neste projeto.
- Com o Python rodando, confira o índice das lições: `"<o Python gravado>" .claude/regua.py
  --conferir`. Lição escrita enquanto não havia Python fica fora do índice, e o gancho, que lê o
  índice, nunca a entrega. Se o `--conferir` acusar, rode o `--gerar` (com o `git add` das lições
  antes, como na skill `licao`) e diga ao usuário que o índice mudou e que o commit é dele.

Conte ao usuário o que foi gravado e onde, e o resultado do teste.
