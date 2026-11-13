---
id: trocar-o-localappdata-nao-esconde-o-python-do-agente
data: 2026-11-13
area: processo
tipo: premissa-falsa
custo: "três tentativas do usuário de abrir a sessão de teste, e o resultado esperado não apareceu"
gatilho: "um teste manual da skill diagnostico: abrir o Claude Code com o LOCALAPPDATA numa pasta vazia, para ver o caminho de uma máquina sem Python"
refs:
  - ".claude/skills/diagnostico/SKILL.md:70-77 (a busca, que lê o $LOCALAPPDATA)"
  - ".claude/skills/diagnostico/SKILL.md:97-103 (o winget, quando nada é achado)"
gatilhos:
  - '\bLOCALAPPDATA=\S'
  - '\$env:LOCALAPPDATA\s*='
  - '\bwinpty\b'
---

**O que se achava:** que abrir o Claude Code com o `LOCALAPPDATA` numa pasta vazia simula uma
máquina sem Python para a skill `diagnostico`, e que o `claude.exe` abre uma sessão no Git Bash.

**O que é:** na sessão de 2026-11-13, segundo a saída que o usuário colou, o agente notou a
pasta de teste ("Refaço com o caminho real") e achou o Python instalado; não chegou ao `winget`.
Por que notou fica a conferir: o nome da pasta (`golem-vazio-...`) entregava o teste. No Git
Bash, o `claude.exe` caiu no modo `--print`, e o `winpty` não resolveu; pelo PowerShell, abriu.

**Como perceber da próxima vez:**
1. Se a sessão de teste acha o Python mesmo com a variável trocada, ou diz que vai procurar no
   caminho real, o teste não simula a máquina sem Python. Rode a busca da skill num `sh`, com
   as pastas vazias e o PATH sem Python: o caminho do `winget` só se vê de verdade numa máquina
   sem Python.
2. Se o `claude.exe` sai no Git Bash com "Input must be provided either through stdin or as a
   prompt argument when using --print", abra-o pelo PowerShell:
   `$velho = $env:LOCALAPPDATA; $env:LOCALAPPDATA = <pasta>; & <claude.exe>; $env:LOCALAPPDATA = $velho`.
3. Uma saída colada sem a linha do prompt não diz em que terminal o usuário rodou, nem qual dos
   comandos sugeridos funcionou: pergunte antes de registrar.
4. O prompt `PS C:\...` é o PowerShell, onde `VAR=valor comando` e o caminho `/c/...` não
   existem. Diga para qual terminal é cada comando que você dá.
