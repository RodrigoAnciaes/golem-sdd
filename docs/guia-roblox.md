# Guia: o Golem num jogo do Roblox, sem Rojo

Para quem programa em Luau no Roblox Studio e não usa Rojo. O código do jogo continua no place,
dentro do Studio. Ao lado dele fica uma pasta do projeto, com git, que guarda as specs, as lições e o
`AGENTS.md`. O agente (o Claude Code) lê e edita o place pelo **Studio MCP**, um servidor que já vem
no Studio e deixa um programa de fora conversar com ele.

## 1. Preparar o Studio (uma vez)

> **Prefere que o agente faça isto por você?** No app desktop do Claude (aba Code), no Windows ou no
> macOS, nos planos Pro, Max ou Ultra, o agente pode controlar a tela e fazer sozinho os passos 1, 2, 4 e 5 (o 3, abrir a conversa
> nova, é seu).
> O controle da tela fica desligado até você ligá-lo nas configurações do app, e você aprova cada
> app que ele for usar. No Claude Code de terminal, o controle da tela só existe no macOS, como
> prévia. Fonte: a documentação do Claude Code,
> [no app desktop](https://code.claude.com/docs/en/desktop.md) ("Let Claude use your computer") e
> [no terminal](https://code.claude.com/docs/en/computer-use.md).

1. **Ligue o servidor MCP.** No Studio, abra as Configurações do Assistente ⟩ Servidores MCP e ligue
   "Ativar o Studio como servidor MCP". Na mesma tela, deixe **desligado** o "Data access": ele
   manda os seus prompts para a Roblox, e o kit não precisa dele. A documentação da Roblox avisa que
   um programa ligado ao MCP lê e muda o seu place: ligue só programas em que você confia.
2. **Conecte o Claude Code.** Na mesma tela, em Conexão rápida ⟩ Claude Code CLI, o Studio mostra um
   comando `claude mcp add ... Roblox_Studio ...`. Rode esse comando **no PowerShell**, dentro da
   pasta do projeto. No Git Bash ele grava o `/c` como `C:/`, e o servidor não conecta. Confira com
   `claude mcp get Roblox_Studio`: deve aparecer `Connected`.
3. **Abra uma conversa nova** do Claude Code: uma conversa que já estava aberta não vê o servidor
   novo.
4. **Salve o place no Roblox** antes da primeira fase (Arquivo ⟩ Salvar na Roblox). Um place que
   é só um arquivo no computador (`.rbxl`) não tem histórico de versões, e é pelo histórico que se
   volta atrás.
5. **Desligue as permissões de Open Cloud do MCP:** no Studio, Configurações do Assistente ⟩
   Permissões MCP, escolha
   **Negar** em cada seção e salve. Cada jogo começa no nível "Equilibrado", com algumas ligadas, e
   até o "Seguro" deixa algumas ligadas. O kit não usa nenhuma.

## 2. Preparar a pasta do projeto (uma vez)

Uma pasta por jogo, com `git init`. Dentro dela, o kit e os modelos de Roblox. Hoje, o kit se copia
para a pasta; isto muda quando o kit virar plugin (a fundação do Golem central). Com o kit copiado:

- copie também a pasta `templates/roblox/` do kit para `templates/roblox/` no projeto: o README
  chama a `templates/` de opcional, mas para um jogo ela não é, porque o agente tira dela o
  `Executor.luau` quando você pede o executor de testes;
- troque o bloco "Comandos reais" do `AGENTS.md` pelo `templates/roblox/comandos-reais.md`;
- copie `templates/roblox/tech-stack.md` para `specs/tech-stack.md` e ajuste ao seu jogo;
- copie as lições de `templates/roblox/licoes/` para `docs/licoes/`, e o
  `templates/roblox/regras-de-area.md` para `docs/regras-de-area.md` (os riscos do Roblox, que o
  agente avisa quando o seu pedido bate num deles);
- rode `git add docs/licoes docs/regras-de-area.md` e depois `python .claude/regua.py --gerar`: o
  gancho lê as lições pelo índice, a régua só indexa o que o git conhece, e uma lição copiada sem
  esses dois passos não chega.

## 3. No dia a dia

- **Os testes.** Peça ao agente: "ponha o executor de testes no place". Ele cria o `Executor` numa
  pasta `GolemTestes` do `ServerStorage`. Um teste é um ModuleScript com o nome terminado em `_spec`
  (o `templates/roblox/Exemplo_spec.luau` mostra como). O agente roda os testes **com o jogo
  ligado**, porque com o jogo parado o Studio usa a versão antiga de um script editado. A linha
  `N passed, N failed, N skipped` no console é o resultado; "nenhum teste encontrado" quer dizer
  zero testes, e não verde.
- **Rodar os testes liga o jogo, e os scripts do jogo rodam junto.** Por padrão, o Studio não
  acessa o `DataStore`: a gravação dá erro. Se você ligar "Enable Studio Access to API Services"
  (em Arquivo ⟩ Configurações de experiência, na parte de segurança; o rótulo em português fica a
  conferir), o Studio grava nos mesmos dados do jogo publicado, porque os dados são da experiência,
  e não do place. A Roblox recomenda ligar isso só numa versão de teste do jogo, e não no jogo ao
  vivo. Fonte: [data stores](https://create.roblox.com/docs/cloud-services/data-stores).
  Os testes do kit não usam `DataStore`. Num place que usa `DataStore`, o validador não chama as
  funções do código nem quebra nada de propósito com o jogo ligado.
- **Antes de cada fase**, o agente salva uma versão do place no Roblox e anota qual foi.

## 4. Voltar atrás

- **O Ctrl+Z não desfaz o que o agente escreveu.** Ele desfaz a criação de um script pelo agente,
  mas não a troca de texto dentro de um script (a criação, vista pelo menu Editar ⟩ Desfazer; a
  troca de texto, uma vez, pelo Ctrl+Z com o foco na janela 3D).
- **Para voltar a uma versão:** no Studio, Janela ⟩ Histórico da versão ⟩ ⋮ ao lado da versão ⟩
  Abrir cópia local. Com a Criação em equipe ligada, o histórico também mostra os salvamentos
  automáticos; a versão do agente é a do número que ele anotou na spec da fase (o `vN` da lista), e
  ela mesma pode aparecer com o rótulo "Salvamento automático". A cópia abre numa janela nova.
  **Antes de salvar a cópia, feche a janela antiga do place, sem salvar:** com ela aberta, o Studio
  avisa de uma sessão de Criação em equipe aberta (a sua) e recusa o salvamento ("Falha no
  salvamento"). Depois, na cópia, Arquivo ⟩ Salvar na Roblox como ⟩ o jogo ⟩ o place que já
  existe ⟩ Substituir, e reabra o place pelo Roblox (Arquivo ⟩ Abrir da Roblox). Pelo site:
  Creator Dashboard ⟩ Creations ⟩ o jogo ⟩ Configurations ⟩ Places ⟩ Version History ⟩ Restore.
  Restaurar cria uma versão nova e **não publica**: para o jogo ao vivo mudar,
  publique depois. Fonte: [histórico de versões](https://create.roblox.com/docs/projects/version-history).

## 5. Quando algo não responde

- **Studio fechado:** o agente recebe "No Roblox Studio instances are connected". Abra o Studio com o
  place e peça de novo; se ainda não responder, abra uma conversa nova.
- **Studio aberto sem place:** o agente recebe "Place is not open". Abra o place e peça de novo.

## 6. O que fica mais fraco sem Rojo

Sem Rojo, o código não está no git: não há diff do que mudou, o revisor lê o script como está agora,
e o validador só quebra o código de propósito para testar os testes em memória, com o jogo ligado,
e só num place sem `DataStore` (mudar o código mudaria o seu jogo). O
desfazer é o histórico de versões. Quando o projeto crescer, o caminho é migrar para o Rojo, que
põe o código em arquivos; essa migração é uma fase futura do kit.
