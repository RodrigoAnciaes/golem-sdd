# Regras de área: riscos do Roblox

Modelo do Golem para um jogo do Roblox. Copie para `docs/regras-de-area.md` do seu projeto: o gancho
das lições entrega cada regra, inteira, a quem edita um script do place (a área `codigo`), uma vez
por sessão. Cada uma diz o risco, o porquê com a fonte na documentação da Roblox e o que o agente
faz.

**Avisar e deixar.** Quando o pedido do usuário bate num destes riscos, o agente faz o que foi
pedido e põe, no resumo da parte (ou no fim do grupo), uma linha de aviso com três saídas: corrigir,
deixar assim, me explica. Não bloqueia. O que o agente escreve por conta própria já sai do jeito
seguro.

## Regra 1 — O servidor não confia no que o cliente manda
areas: codigo

O que chega de um cliente por um `RemoteEvent` ou uma `RemoteFunction` pode ter sido forjado: o
servidor valida cada argumento (o tipo, o limite, se a ação é possível) antes de agir. Fonte:
"Never trust the client" e "all critical logic must be validated server-side or run exclusively on
the server" (https://create.roblox.com/docs/scripting/security/security-tactics). Avisar e deixar:
se o pedido usa um valor do cliente sem validar, faça e avise no resumo, com as três saídas:
corrigir, deixar assim, me explica.

## Regra 2 — A chamada de `DataStore` vai dentro de `pcall`
areas: codigo

Uma chamada de `DataStore` pode falhar por motivos passageiros: ela vai dentro de `pcall`, e a falha
passageira se tenta de novo, com espera crescente e um limite de tentativas. Fonte: "Wrap requests
in `pcall()` and retry transient failures with exponential backoff"
(https://create.roblox.com/docs/cloud-services/data-stores/best-practices). Avisar e deixar: se o
pedido chama o `DataStore` sem `pcall`, faça e avise no resumo, com as três saídas:
corrigir, deixar assim, me explica.

## Regra 3 — O `DataStore` tem limite de pedidos
areas: codigo

Passar do limite de pedidos faz o Roblox enfileirar e atrasar os pedidos do jogo, e, com a fila
cheia, o pedido falha: nada de chamar o `DataStore` dentro de um laço apertado ou a cada quadro.
Fonte: "If an experience exceeds these limits, the service automatically throttles the
experience's data store usage" e "When the limit of a queue is reached, requests fail"
(https://create.roblox.com/docs/cloud-services/data-stores/error-codes-and-limits). Avisar e deixar:
se o pedido chama o `DataStore` muitas vezes seguidas, faça e avise no resumo, com as três saídas:
corrigir, deixar assim, me explica.

## Regra 4 — O que o cliente não pode ver fica no servidor
areas: codigo

O conteúdo do `ReplicatedStorage` vai para todos os clientes; o do `ServerStorage` e o do
`ServerScriptService` fica só no servidor. Regra do jogo, preço e dado que não é do jogador ficam no
servidor. Fontes: "A container service for objects that are replicated to all clients"
(https://create.roblox.com/docs/reference/engine/classes/ReplicatedStorage), "Objects descending
from ServerStorage will not replicate to the client"
(https://create.roblox.com/docs/reference/engine/classes/ServerStorage) e "The contents are never
replicated to player clients at all"
(https://create.roblox.com/docs/reference/engine/classes/ServerScriptService). Avisar e deixar: se o pedido
põe no `ReplicatedStorage` algo que só o servidor deveria ver, faça e avise no resumo, com as três
saídas: corrigir, deixar assim, me explica.

## Regra 5 — O dado do jogador se salva também no `BindToClose`
areas: codigo

Quando o servidor desliga, o `PlayerRemoving` pode não dar tempo de salvar: quem usa `DataStore`
liga também uma função de salvar no `game:BindToClose`. Fonte: "When you use DataStoreService, you
should also use BindToClose to bind a function saving all unsaved data"
(https://create.roblox.com/docs/reference/engine/classes/DataModel, `BindToClose`). Avisar e deixar:
se o pedido salva o jogador só no `PlayerRemoving`, faça e avise no resumo, com as três saídas:
corrigir, deixar assim, me explica.

## Regra 6 — A conexão que não serve mais se desconecta
areas: codigo

Um `Connect` devolve uma conexão. A que não serve mais, num objeto que continua existindo (o fim
de uma rodada, um evento de um serviço), se desconecta com `Disconnect()`, ou a função continua
sendo chamada. Quando o objeto é destruído (o `Player` que saiu do jogo), as conexões dele se
desconectam sozinhas. Fonte: "If you connect a function to an event, but don't want to call the
function the next time an event fires [...] disconnect it" e "When Luau destroys an event's
object, such as the Player object when a user leaves the game, all of its non-deferred
connections disconnect automatically" (https://create.roblox.com/docs/scripting/events). Avisar
e deixar: se o pedido conecta a cada rodada, num objeto que continua existindo, sem desconectar,
faça e avise no resumo, com as três saídas: corrigir, deixar assim, me explica.

## Regra 7 — `task.wait`, e não `wait`
areas: codigo

O `wait()` global está obsoleto e pode atrasar mais do que o pedido; o `task.wait()` é o que se usa.
Fonte: "Unlike the deprecated global `wait()`, this function does not throttle"
(https://create.roblox.com/docs/reference/engine/libraries/task, `task.wait`). Avisar e deixar: se o
pedido usa `wait()`, faça e avise no resumo, com as três saídas: corrigir, deixar assim, me explica.
