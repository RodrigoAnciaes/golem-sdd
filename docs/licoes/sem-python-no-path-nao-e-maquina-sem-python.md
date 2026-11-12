---
id: sem-python-no-path-nao-e-maquina-sem-python
data: 2026-11-12
area: processo
tipo: erro-de-diagnostico
custo: "uma sessão inteira sem lições injetadas, um diagnóstico errado escrito em mensagens ao usuário e uma proposta de produto apoiada nele"
gatilho: "no Windows, o gancho avisou 'nenhum Python 3.8+ encontrado' em toda ação, e o agente concluiu que a máquina não tinha Python"
refs:
  - ".claude/hooks/gancho.sh:60 (achar_venv: só o .venv da raiz e o da pasta principal)"
  - ".claude/hooks/gancho.sh:74 (achar_no_path: python3, python e py -3, só pelo PATH)"
  - ".claude/hooks/gancho.sh:100 (o aviso 'nenhum Python 3.8+ encontrado')"
  - "instalador oficial do Python no Windows: %LOCALAPPDATA%\\Programs\\Python\\PythonXY\\python.exe e %LOCALAPPDATA%\\Programs\\Python\\Launcher\\py.exe"
gatilhos:
  - '\b(where(\.exe)?|which|type|command\s+-v|get-command)\s+(python3?|py)\b'
  - '(^|/)gancho-falhas\.log\b'
  - '\bwinget\s+install\b.*\bpython'
---

**O que se achava:** que o aviso do gancho, "nenhum Python 3.8+ encontrado (nem .venv na pasta da
sessão ou na principal, nem python3, python ou py -3 no PATH)", queria dizer que a máquina não tinha
Python. O agente repetiu isso ao usuário ("esta máquina não tem Python") e montou uma proposta em
cima. O usuário corrigiu: o Python existe e é usado por vários ambientes e conversas.

**O que é:** o gancho só procura no `.venv` da raiz, no da pasta principal e no PATH. O Python do
instalador oficial e o `py.exe` estavam fora do PATH (os caminhos estão nos `refs`). No PATH, só os
atalhos da Microsoft Store, que imprimem "Python não foi encontrado" e saem com erro (49 no Git
Bash, 9009 no PowerShell). O aviso diz onde o gancho procurou, não que o Python falta.

**Como perceber da próxima vez:**
1. Diante de "nenhum Python encontrado", leia a lista de onde o gancho procurou e escreva "não há
   Python **no PATH** nem num `.venv` daqui", nunca "a máquina não tem Python".
2. No Windows, antes de afirmar que falta: `ls "$LOCALAPPDATA"/Programs/Python/*/python.exe` e
   `ls "$LOCALAPPDATA"/Programs/Python/Launcher/py.exe`. Um `python` que aponta para
   `WindowsApps` é o atalho da loja, não um Python.
3. Se outras conversas ou outros projetos rodam Python na mesma máquina (um `.venv` de outro
   repositório, por exemplo), o Python existe: o que falta é o caminho até ele.
