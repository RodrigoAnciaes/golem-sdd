# Operação das conversas

Como várias conversas do agente (Claude Code ou Codex) trabalham juntas no mesmo projeto: quem faz o
quê, quem decide o quê, como falam com o usuário e quais travas valem para todas.

Num projeto pequeno, uma conversa só faz tudo e este documento se resume a três seções:
[o fecho](#o-fecho), o [cartão de decisão](#cartão-de-decisão) e o [merge](#merge). Os papéis
valem a pena quando há duas ou mais entregas andando ao mesmo tempo.

**No app, no terminal ou no Codex.** A coordenação entre conversas por mensagem (uma conversa
mandar mensagem a outra, a caixa de pergunta com botões) é só do **app desktop** do Claude Code. No
Codex e no terminal, o usuário repassa as mensagens à mão: copia o PEDIDO da frente para a GER e o
LIBERADO de volta. O método funciona igual; onde este documento diz "manda à GER", leia ali "o
usuário leva à GER".

A memória do agente guarda o que é sobre o usuário e o estado do dia. **A regra de fluxo mora
aqui.** Quando as duas divergirem, este documento manda, e quem notar corrige a memória.

---

## Papéis

| Papel | Conversa | Faz | Não faz |
|---|---|---|---|
| **GER** | a gerente | coordena as conversas; responde ao PEDIDO com LIBERADO (merge, recurso compartilhado, conversa nova); confere head e base antes de merge; mantém o [registro vivo](#o-registro-vivo-da-gerente-gerentemd), o `GERENTE.md` | discutir ideia ou rumo (isso é da EST); escrever código de entrega |
| **EST** | a estratégia | discute prioridade e produto com o usuário; registra as decisões dele, com a pergunta e as palavras; avisa a GER de cada decisão | operar, liberar merge |
| **MET** | o método | cuida de como as conversas trabalham: o `AGENTS.md`, este documento, as skills, os agentes, os ganchos, as lições e a memória; observa o comportamento das conversas e, quando uma regra produz efeito ruim, propõe a correção ao usuário | prioridade e produto (EST); operação e merge (GER); mudar as configurações do usuário (ela propõe, ele aplica) |
| **GUA** | o guardião: o agente `revisor` numa conversa nova (ou num subagente novo, sem o contexto de quem escreveu) | a revisão final do PR com código, quando o bloco "Como o Golem trabalha aqui" do `AGENTS.md` a pede, depois da revisão por grupo e antes do merge: lê o **diff inteiro do PR** contra a spec e as regras | revisar PR só de documentação ou só de testes (basta o revisor, no caminho rápido) |
| frentes | uma conversa por entrega | executam uma fase ou uma correção, no próprio worktree, pelo fluxo do `WORKFLOW.md` | coordenar outra frente direto: o que afeta outra conversa passa pela GER |

**O fluxo das decisões.** O usuário decide na EST, na MET ou na conversa que executa. A EST
registra e avisa a GER; a GER repassa a quem executa. **A GER repassa informação, nunca
autorização:** o ok do usuário para o merge de nível 3, texto a terceiros ou produção vale só dito
na conversa que executa.

Quando o usuário traz uma ideia à GER, ela sugere levar à EST, ou responde ali mesmo se couber em
poucas linhas.

### O registro vivo da gerente: `GERENTE.md`

O estado das frentes mora num arquivo só, o **`GERENTE.md`**, na **raiz do projeto principal**
(a pasta do clone, não a de um worktree), **fora do Git**: ponha `GERENTE.md` no `.gitignore`.

- **O que guarda:** uma entrada por frente e por evento, com **o quê** (o que aconteceu ou está
  em curso), **por quê**, **o próximo passo** e **quem espera** (o usuário, a GER, uma frente, o
  CI, alguém de fora). Também a fila de merges, o que entrou na `main` (data, PR, sha, o que mudou)
  e quem está com cada [trava](#travas).
- **Quando muda:** a cada evento (PEDIDO, LIBERADO, merge, decisão, bloqueio, frente aberta ou
  fechada), na hora, não no fim do dia. O mais novo primeiro.
- **Quem escreve:** só a GER. As outras conversas leem e mandam o texto à GER.
- **Como se lê de um worktree:** a pasta principal é o pai do `git rev-parse --git-common-dir`.
  Leia só a parte mais recente; o resto se busca com `grep` quando a tarefa pedir.
- **Se o registro e o git discordarem**, o git manda: pare e avise a GER, que corrige o registro.

Uma GER nova (outra sessão) abre por este arquivo e reconfere no git o que ele diz.

### Uma conversa, um worktree

- Cada frente trabalha no próprio `git worktree`. Duas conversas nunca escrevem no mesmo.
- A pasta principal do repositório é da GER: outra conversa escreve lá só com LIBERADO.
- A conversa remove o próprio worktree depois do merge, com o `git status` limpo. Worktree com
  arquivo não commitado só se remove depois de olhar o que há nele.
- Com merge por squash, "mergeado" se confere pelo PR (`gh pr view <número> --json state`), nunca
  pela ancestralidade no `git log`.

---

## Níveis de autonomia

Na dúvida sobre o nível, pergunte à GER. << Ajuste as listas ao seu projeto. >>

### Nível 1 — a conversa faz sozinha e só registra

- Trabalho local sem custo no próprio worktree: código, testes, documentos.
- Leituras: repositório, issues, logs, ambientes em modo só leitura.
- Subagentes dentro da própria sessão (revisor, validador, leitor).
- Remover o próprio worktree depois do merge.

### Nível 2 — a gerente libera (PEDIDO → LIBERADO)

- **Merge no repositório do projeto** (o padrão), depois da conferência do head, da base e da
  prova, e com a revisão feita. Sem GER, o usuário faz o papel dela.
- Gasto pago (chamadas de modelo, nuvem) dentro do orçamento que o usuário aprovou na spec.
- Ordem entre frentes, conflito de arquivo, vez num recurso compartilhado.
- Escrita na pasta principal.
- Abrir conversa nova, respeitando o [limite de frentes](#limite-de-frentes-ativas).

### Nível 3 — sempre o usuário

- Tudo que sai para fora: qualquer texto que outra pessoa lê (comentário, issue, revisão,
  mensagem), cliente, publicação.
- Produção em qualquer forma.
- **Merge de nível 3:** o merge em repositório de terceiros (de outra equipe, de um cliente, um
  projeto aberto); o merge que vai a produção (uma branch com deploy automático, uma branch de
  release); o merge local, num projeto sem remoto; << o que mais o projeto listar >>. A mesma lista
  está no `AGENTS.md`, "Convenções": mudou aqui, muda lá.
- Gasto acima do orçamento, conta nova, credencial.
- Dado sensível mudando de lugar.
- Prioridade entre frentes, e qualquer decisão que desfaça uma decisão anterior dele.

**Um ok por pacote.** O que precisa do usuário numa mesma entrega vai a ele junto, num ok só.

### PEDIDO e LIBERADO

O par que dá ordem ao nível 2. Uma linha cada, começando pelo rótulo:

- **`PEDIDO:`** o quê (merge do PR, o recurso, a conversa nova), o **head** e a **base** que a
  conversa leu, e **a prova** (a suíte ou o CI no head, com a linha de resumo, e os vereditos da
  revisão).
- **`LIBERADO:`** o mesmo alvo, com o **head** e a **base** que a GER conferiu e libera.

Exemplo de merge:

```
PEDIDO: merge do PR 12, head 3f9c2ab, base 81d04e7, prova: pytest -q "48 passed, 0 skipped" no head; revisor sem bloqueio, validador valida, guardião sem bloqueio
LIBERADO: PR 12, head 3f9c2ab, base 81d04e7
```

Exemplo de recurso:

```
PEDIDO: Docker, prefixo fase-agenda, subir a pilha para o teste de integração (~40 min)
LIBERADO: Docker, prefixo fase-agenda, trava gravada às 14:05Z
```

A conversa manda o PEDIDO e espera. A GER confere (head e base pelo `git ls-remote`, a prova feita
**nesse** head), registra no `GERENTE.md` e devolve o LIBERADO, ou diz o que falta. Head ou base
diferentes no LIBERADO querem dizer que algo andou: a conversa não mergeia e refaz a conferência.
Sem resposta em uns 10 minutos, a conversa pergunta ao usuário; nunca segue sozinha. Depois do
PEDIDO de merge, nenhum commit novo na branch sem avisar a GER.

O LIBERADO dá a vez, não a autorização do usuário: o merge que é nível 3 espera também a palavra
dele, dita na conversa que executa.

---

## O fecho

O usuário acompanha várias frentes e lê cada mensagem sem ter revisto o contexto. Toda mensagem de
fim de turno termina, nesta ordem, com quatro itens:

1. **Resumo:** o que mudou e para quem, o que ficou provado e o que está pendente. É destino, não a
   lista de passos. Todo identificador (PR, issue, decisão) vem com a frase do que ele é.
2. **O que você faz agora:** numerado, no máximo 5 itens, na ordem da prioridade. Não repete o
   que ele disse que faz depois.
3. **Worktree:** `<caminho absoluto>` (branch `<branch>`), conferido na hora com
   `git rev-parse --show-toplevel` e `git branch --show-current`, nunca de memória. Sem worktree:
   "sem worktree".
4. **Espera:** `<quem> — [<tipo>] <o quê>`, a última linha. `<quem>` é `usuário`, `GER`, `CI`, o
   nome de quem está fora, ou `nada`. A etiqueta é opcional: `[decisão]`, `[texto]`, `[rápido]`,
   `[agenda]`, `[spec]`.

**O fecho curto.** Quando nada espera pelo usuário (a Espera não começa por `usuário`), o Resumo
tem até 3 linhas e o "O que você faz agora" sai; o Worktree e a Espera ficam.

**Uma mensagem por marco, não por passo.** Fim de grupo não é fim de turno, salvo com o "parar a
cada parte" do bloco "Como o Golem trabalha aqui" (`AGENTS.md`), em que o grupo termina esperando o
ok do usuário. Sem ele, com o próximo passo liberado, o status vai numa linha curta e a conversa
segue. O turno termina num bloqueio real (um
PEDIDO, uma decisão do usuário, a espera do CI ou do revisor) ou com a tarefa feita. `Espera: nada`
com trabalho liberado pela frente é o sinal do erro.

**Frase curta pode ser pergunta.** "É só…", "não daria…" sem ponto de interrogação pode ser uma
pergunta: responda antes de agir. Aja só com verbo de ordem claro.

---

## Cartão de decisão

Toda decisão pedida ao usuário traz, **no texto da mensagem** e antes do fecho:

1. **O problema**, para quem não abre a conversa há dias, e **o que acontece se ninguém decidir**.
2. **As opções**, cada uma com a consequência: o que muda e o custo de voltar atrás.
3. **A recomendada**, primeiro, marcada "(recomendo)", com o porquê.
4. **O tamanho**: P, M ou G (ver [Decisões](#decisões)).

Exemplo:

> **O problema:** a rota de busca leva 4 s com 10 mil registros; sem decisão, a fase fecha com o
> critério de 300 ms reprovado.
> **Opções:** (A, recomendo) um índice na coluna `nome`: uma migração, desfaz com outra. (B)
> paginar em 50: muda a resposta da API, e o cliente precisa mudar junto. (C) aceitar os 4 s e
> tirar o critério da fase.
> **Tamanho:** M.

- **Nunca só na caixa do app.** A caixa de pergunta repete o que o texto já explicou; o texto
  escrito antes de uma caixa de opções pode não aparecer. A caixa sozinha fica para opções que se
  explicam nas próprias descrições.
- **O ok de seguir não é decisão nova.** O sim para continuar o que já foi decidido (o commit, o PR,
  o merge do pacote já explicado) vai direto na caixa, sem cartão.
- **Um dono por assunto.** A pergunta que cruza conversas, só o dono faz: prioridade, produto e
  rumo, a EST; operação, merge e a vez nas filas, a GER; o detalhe e os oks da própria entrega, a
  frente. As outras escrevem `Espera: EST — …` ou `Espera: GER — …` e não perguntam.
- **O silêncio nunca vale como sim**, e a recomendação de uma conversa nunca vira "você já tinha
  decidido". Só as palavras do usuário decidem.

### Pergunta autocontida e uma pauta por vez

- Toda pergunta traz **todas as opções na própria pergunta**, cada uma com rótulo e consequência,
  a recomendada primeiro. Nunca "escolha A, B ou C" com as opções quatro telas acima. Mais de
  quatro opções: divida.
- "Não mudar nada" entra quando a pergunta é se algo muda; num sim ou não, não é terceira opção
  automática.
- **Uma decisão aberta por mensagem.** Pergunta do usuário recebe resposta; se a resposta revelar
  uma lacuna, ofereça abrir a pauta numa linha, sem já montar a proposta.
- Ideia nova que chega no meio de uma decisão espera: diga qual fica em espera e por quê, e não a
  traga de volta até a primeira fechar.
- Toda pauta retomada diz de onde veio: as palavras do usuário e a data.

---

## Decisões

As decisões do usuário ficam num registro (<< ex.: `docs/decisoes.md`, ou um arquivo fora do Git
se forem pessoais >>). Só a EST escreve nele; as outras leem. Cada decisão ganha um id
(`DEC-NNN`).

**Tamanhos.** Na dúvida, sobe um tamanho. Desfazer uma decisão anterior é no mínimo M e cita a
anterior com as palavras e a data. O que toca produção, cliente ou outra equipe é sempre G.

| | P — pequena | M — média | G — grande (rumo) |
|---|---|---|---|
| Quando | processo interno que se desfaz em minutos | regra ou fluxo de várias conversas, prioridade entre frentes, desenho técnico interno, gasto dentro do orçamento | o que se entrega, prazo com cliente, arquitetura, produção, custo recorrente |
| Opções | a recomendação basta | duas ou mais, com "não fazer" | duas ou mais, cada uma com o custo de reverter |
| Revisão antes de levar | quem quebra se mudar | mais um revisor | revisor e validador independentes |
| Confirmação | um "ok" | um "ok" | o "ok" e **uma confirmação num turno seguinte** |
| Onde vive | o registro | o registro, mais este documento ou a memória | o registro, mais ADR ou roadmap |

**Decisão G só vale depois do segundo turno:** o usuário dá o ok, recebe o fechamento (o que muda,
o que não se desfaz, quem é avisado) e confirma num turno seguinte. Até lá, ninguém executa.

**O registro de cada decisão** traz:

- **a pergunta como foi feita**, com as opções; o rótulo do botão sozinho ("Opção 1") não basta;
- **as palavras do usuário, literais, com a data**;
- o tamanho e o estado: proposta, decidida, aplicada, revista ou substituída.

Um "ok" cobre só o que estava escrito; acréscimo é decisão nova. A proposta entra no registro como
"proposta" no turno em que sai, para não se perder.

---

## Merge

### Conferir e mergear em chamadas separadas

O `--match-head-commit` protege o head do PR, não a base. Por isso:

1. **Numa chamada, a conferência:** `git ls-remote origin <branch> main` (ou o script de
   conferência do projeto). Leia os shas e compare com o LIBERADO.
2. **Só então, em outra chamada**, com o LIBERADO (e, no merge de nível 3, a palavra do usuário
   na conversa que executa):
   `gh pr merge <número> --<squash|merge> --match-head-commit <sha>`, com o sha copiado da saída
   da conferência, nunca escrito de cabeça.

Encadeado no mesmo comando (`ls-remote … && gh pr merge …`), o merge roda antes de alguém ler o
sha. Se a base andou, pare e avise a GER. O sha do merge só vai a uma mensagem **depois** de lido
na saída do `git log` ou do `gh`.

### O CI uma vez no head final

- A revisão lê o diff **antes**; a prova (a suíte local ou o CI) roda **uma vez**, no head final.
- Se a base mudou depois da prova, a prova refaz.
- Rodar só o que o diff afeta é legítimo; PR só de documentação não precisa de suíte.
- Check vermelho por motivo que não é teste (cobrança, infraestrutura) não vira verde por
  declaração: a prova passa a ser local, com a linha de resumo lida (regra 8), e isso se registra.

### O caminho rápido

PR só de documentação ou só de testes leva **um revisor**, se o bloco "Como o Golem trabalha aqui"
(`AGENTS.md`) o põe para rodar, sem validador e sem guardião. O revisor
confere fato por fato contra a fonte (`arquivo:linha`), não só a forma. Se ganhar código, ou se o
revisor apontar algo importante, volta ao caminho completo. PRs da mesma entrega em sequência
somam: não se fatia uma mudança grande para caber no caminho rápido.

---

## Travas

### Recurso pesado compartilhado

Um recurso que não aguenta duas conversas ao mesmo tempo (o Docker com a pilha inteira, um banco
local, uma cota paga) tem **um arquivo de trava** na pasta principal, por exemplo
`RECURSO-EM-USO.md`:

```
estado: livre
```

ou

```
<conversa> | <prefixo dos contêineres> | <início, UTC> | <o quê>
```

- **Para pegar:** a conversa lê a trava. Se está `livre`, pede à GER (PEDIDO), que grava a linha
  e devolve o LIBERADO. Se as conversas puderem escrever na pasta principal, a própria conversa
  grava.
- **Para soltar:** depois de derrubar o que subiu (`docker compose down -v`, com os volumes
  conferidos), a conversa avisa a GER, e a linha volta a `livre`.
- Ocupada há mais de 2 horas: pergunte à GER.
- Cada conversa usa um prefixo próprio no que cria, para que a limpeza não leve o que é de outra.
- Uma frente pesada por vez na máquina inteira; ao primeiro sinal de lentidão, pare e avise.

### Limite de frentes ativas

No máximo << 6 >> frentes ativas ao mesmo tempo: as que trabalham, esperam o usuário ou pedem
permissão. As conversas permanentes (GER, EST, MET) e a do guardião não contam. A GER cobra o limite
no LIBERADO de conversa nova: com o limite cheio, a nova espera uma fechar, ou o usuário decide a
exceção.

---

## Achado fora do escopo

Defeito ou limitação achado fora da tarefa: a primeira que servir.

1. **Está no escopo:** corrija ali mesmo.
2. **Urgente** (produção, perda de dado, segurança, custo disparando): direto à GER.
3. **Armadilha** que cumpre um dos quatro motivos da regra 7 do `AGENTS.md`: vira lição na hora.
4. **Afeta uma frente em andamento:** à GER.
5. **O resto:** um arquivo curto na caixa de achados (<< ex.: `achados/entrada/` >>), com onde,
   o quê, a evidência, o impacto e o tamanho; a tarefa segue. A EST tria a caixa com o usuário de
   tempos em tempos.
