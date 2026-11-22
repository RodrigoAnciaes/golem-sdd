---
id: o-git-bash-troca-o-barra-c-do-cmd-por-c
data: 2026-11-21
area: processo
tipo: armadilha
custo: "uma rodada do G2 da fase 2: o servidor do Studio MCP registrado pelo Git Bash não conectava (timeout de 30 s)"
gatilho: "registrar o servidor MCP do Roblox Studio no Claude Code com o comando que o quick connect do Studio mostra, rodado pela ferramenta Bash (Git Bash) no Windows"
refs:
  - "specs/2026-11-13-fase-2-roblox/plan.md (Respostas do G2, resposta 1)"
gatilhos:
  - '\bmcp\s+add\b'
  - '\bcmd(\.exe)?"?\s+"?/c\b'
---

**O que se achava:** que o comando que o Studio mostra para conectar o Claude Code
(`claude mcp add --transport stdio Roblox_Studio -- cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat`)
registra o mesmo servidor em qualquer terminal da máquina, inclusive no Git Bash, o shell da
ferramenta Bash do agente no Windows.

**O que é:** o Git Bash converte o argumento que começa com `/` num caminho do Windows antes de
passá-lo a um programa nativo. Rodado nele, o `claude mcp add` respondeu "Added stdio MCP server
Roblox_Studio with command: cmd.exe C:/ %LOCALAPPDATA%\Roblox\mcp.bat", e o `claude mcp get
Roblox_Studio` mostrou `Args: C:/ %LOCALAPPDATA%\Roblox\mcp.bat` e "Failed to connect", "connection
timed out after 30000ms". O mesmo comando no PowerShell gravou `Args: /c %LOCALAPPDATA%\Roblox\mcp.bat`
e deu `Status: √ Connected` (2026-11-21, Claude Code 2.1.323; visto na sessão do G2, sem
arquivo próprio).

**Como perceber da próxima vez:**
1. Um `claude mcp get <servidor>` que mostra `C:/` no lugar do `/c` nos `Args`, ou um servidor que
   só dá timeout ao conectar, depois de um `mcp add` rodado pela ferramenta Bash: o `/c` foi
   convertido. Remova (`claude mcp remove <servidor> -s local`) e registre de novo pela ferramenta
   PowerShell.
2. Antes de rodar no Git Bash um comando com argumento que começa com `/` (`/c`, `/k`, `/s`) para
   um programa do Windows, leia o eco do que foi gravado: a conversão não dá erro nenhum.
