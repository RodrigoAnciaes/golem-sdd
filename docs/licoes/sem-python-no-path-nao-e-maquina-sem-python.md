---
id: sem-python-no-path-nao-e-maquina-sem-python
data: 2026-11-12
area: processo
tipo: erro-de-diagnostico
custo: "uma sessão inteira sem lições injetadas, um diagnóstico errado escrito em mensagens ao usuário e uma proposta de produto apoiada nele"
gatilho: "no Windows, o gancho avisou 'nenhum Python 3.8+ encontrado' em toda ação, e o agente concluiu que a máquina não tinha Python"
refs:
  - ".claude/hooks/gancho.sh, achar_venv e achar_no_path (em f912da6, os únicos lugares de procura: o .venv da raiz, o da pasta principal e o PATH)"
  - ".claude/hooks/gancho.sh, o aviso 'nenhum Python 3.8+ encontrado'"
  - ".claude/hooks/gancho.sh, ler_linha_python e achar_no_instalador (o conserto da fase 0)"
  - ".claude/skills/diagnostico/SKILL.md:35-44 e :80-93 (pergunta onde está o Python e grava a linha python)"
  - "instalador oficial do Python no Windows: %LOCALAPPDATA%\\Programs\\Python\\PythonXY\\python.exe e %LOCALAPPDATA%\\Programs\\Python\\Launcher\\py.exe"
gatilhos:
  - '\b(where(\.exe)?|which|type|command\s+-v|get-command)\s+(python3?|py|claude)\b'
  - '(^|/)gancho-falhas\.log\b'
  - '\bwinget\s+install\b.*\bpython'
---

**O que se achava:** que o aviso do gancho, "nenhum Python 3.8+ encontrado (nem .venv na pasta da
sessão ou na principal, nem python3, python ou py -3 no PATH)", queria dizer que a máquina não tinha
Python. O agente repetiu isso ao usuário ("esta máquina não tem Python") e montou uma proposta em
cima. O usuário corrigiu: o Python existe e é usado por vários ambientes e conversas.

**O que é:** em `f912da6`, o gancho só procurava no `.venv` da raiz, no da pasta principal e no
PATH. O Python do instalador oficial e o `py.exe` estavam fora do PATH (os caminhos estão nos
`refs`). No PATH, só os atalhos da Microsoft Store, que imprimem "Python não foi encontrado" e
saem com erro (49 no Git Bash, 9009 no PowerShell). O aviso diz onde o gancho procurou, não que o Python falta.

Desde a fase 0 (2026-11-12), o gancho também procura na linha `python` do `golem.local.toml` e nos
lugares do instalador do Windows, e a skill `diagnostico` grava essa linha. O sinal abaixo continua
valendo para o Python que fica fora até desses lugares.

Em 2026-11-13, o mesmo erro se repetiu com outro programa. O agente escreveu que o CLI `claude`
"não está instalado", porque ele não estava no PATH. O revisor achou o `claude.exe` que o app
desktop traz numa pasta própria, dentro do `%LOCALAPPDATA%` (o item 4 abaixo).

**Como perceber da próxima vez:**
1. Diante de "nenhum Python encontrado", leia a lista de onde o gancho procurou e escreva "não há
   Python **no PATH** nem num `.venv` daqui", nunca "a máquina não tem Python".
2. No Windows, antes de afirmar que falta: `ls "$LOCALAPPDATA"/Programs/Python/*/python.exe` e
   `ls "$LOCALAPPDATA"/Programs/Python/Launcher/py.exe`. Um `python` que aponta para
   `WindowsApps` é o atalho da loja, não um Python.
3. Se outras conversas ou outros projetos rodam Python na mesma máquina (um `.venv` de outro
   repositório, por exemplo), o Python existe: o que falta é o caminho até ele. Peça ao usuário o
   diagnóstico do Golem, que pergunta onde ele está.
4. Vale para qualquer programa: "não está no PATH" não é "não está instalado". Antes de afirmar
   que falta, procure na pasta do app que o traz. O `claude.exe` do app desktop fica em
   `%LOCALAPPDATA%\Claude-Data\<id>\claude-code\<versão>\<hash>\`.
