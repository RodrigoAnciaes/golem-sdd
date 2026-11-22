# Stack técnica

Modelo para um jogo do Roblox **sem Rojo**: o código mora no place, e a pasta do projeto, com git,
guarda as specs e as lições. Copie para `specs/tech-stack.md` e troque o que não for o seu caso.

## Visão geral

Um jogo do Roblox editado no Roblox Studio. O código (Scripts, LocalScripts e ModuleScripts) mora
no place, salvo no Roblox; a pasta do projeto ao lado, com git local, guarda as specs, as lições e o
`AGENTS.md`. O agente lê e edita o place pelo Studio MCP, o servidor `Roblox_Studio`.

## Núcleo

| Camada | Escolha | Versão fixa | Por quê |
|---|---|---|---|
| Linguagem | Luau | a do Roblox Studio (ele se atualiza sozinho) | é a linguagem do Roblox |
| Editor | Roblox Studio | a instalada | onde o jogo vive |
| Ponte com o agente | Studio MCP oficial (`Roblox_Studio`) | a do Studio | lê, edita e roda Luau no place aberto |

## Dados

Os dados dos jogadores ficam no `DataStore` do Roblox. Por padrão, o Studio não acessa o
`DataStore`; com o acesso às APIs ligado, ele é o do jogo publicado, e um teste ou um script que
escreve nele muda o dado dos jogadores. Os testes não usam `DataStore`.

## Testes e qualidade

O executor mínimo do Golem (`Executor`, em `game.ServerStorage.GolemTestes`), que roda os
ModuleScripts terminados em `_spec` e imprime `N passed, N failed, N skipped`. Ele roda em modo de
jogo, porque em modo de edição o `require` devolve a versão guardada de um módulo. O comando está no
`AGENTS.md`, "Comandos reais". O que não tem teste automático (a física, a sensação de um pulo, a
interface) entra no `validation.md` como passo a passo de playtest.

## Execução

Não há build nem deploy pelo agente: o jogo roda no Studio (pelo botão de jogar do Studio ou pelo
`start_stop_play`) e se publica pelo próprio Studio, quando o usuário quiser. Não há segredo: nada usa chave de API, e as
permissões de Open Cloud do Studio MCP ficam desligadas.

## Convenções

O código no place, nos serviços de sempre (`ServerScriptService` para o servidor,
`ReplicatedStorage` para o que o cliente também usa, `ServerStorage` para o que só o servidor vê). Os
testes são ModuleScripts com o sufixo `_spec`, ao lado do que testam, num dos serviços em que o
executor procura (`ServerScriptService`, `ServerStorage`, `ReplicatedStorage`, `ReplicatedFirst`,
`StarterPlayer`, `StarterGui`, `Workspace`). Antes de cada fase, o agente
salva uma versão do place no Roblox.

## Requisitos não-funcionais

Os do jogo; anote aqui o que valer para o seu (por exemplo, o número de jogadores por servidor).

## O que não usamos

Rojo, Wally, TestEZ e Jest: são dependência nova, e o Rojo fica para quando o projeto pedir (a
migração para o Rojo é uma fase futura do kit). A API Open Cloud: pede chave de API ou permissões que o kit não usa.
