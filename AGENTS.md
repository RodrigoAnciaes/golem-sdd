# AGENTS.md — regras permanentes do projeto

Este arquivo é lido pelo agente em toda sessão. As regras numeradas são **método**: valem para toda
tarefa, em qualquer conversa. Este é o `AGENTS.md` do kit. O modelo que o usuário copia é o
`templates/AGENTS.md`, com as lacunas; as diferenças entre os dois estão no conciliador
(`.claude/tests/test_conciliar.py`).

---

## O projeto

Golem SDD: kit de spec-driven development para Claude Code e Codex, pensado para desenvolvedores de
Roblox iniciantes.

| O quê | Onde |
|---|---|
| Código | `.claude/` (skills, agentes, gancho, régua, `golem.py`, instalador do Codex) e `templates/` |
| Specs | `specs/` (uma pasta por fase) |
| Decisões técnicas | a seção 8 do `docs/plano-produto.md` (o kit não tem `docs/adr/`) |
| Lições | `docs/licoes/` |
| Como as conversas trabalham | `docs/operacao-das-conversas.md` |
| Ferramental do agente | `.claude/` (skills, agentes, ganchos, régua): a fonte |
| Cópias para o Codex | `.agents/skills/` e `.codex/` (agentes e gancho), geradas por `.claude/instalar_codex.py` (o Codex só usa a cópia do kit no projeto), nunca à mão |

**Quem é quem.** O **usuário** decide produto, prioridade, stack, gasto e tudo que sai para fora,
e faz os merges que a lista de nível 3 reserva a ele ("Convenções", abaixo). O agente decide o
detalhe de implementação dentro de uma spec aprovada.

## Ordem de leitura

1. Este arquivo.
2. `docs/operacao-das-conversas.md`: os papéis e o que cada conversa faz sozinha.
3. `docs/plano-produto.md`: a constituição do kit, com o roteiro na seção 7.
4. `specs/AAAA-MM-DD-<fase>/`: a spec da fase em andamento.
5. A seção 8 do `docs/plano-produto.md`: as decisões registradas.

Leia só o que a tarefa de hoje exige. O resto se abre quando for preciso.

---

## Comandos reais

Onde se lê `python`, use um Python 3.8+ com pytest (no Windows, `python` ou `py -3`).

```bash
# setup
nenhum: só a biblioteca padrão; a suíte pede pytest

# testes (a linha de resumo tem de aparecer na saída)
python -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs

# a régua
python .claude/regua.py --conferir

# lint e formatação
não instalado

# subir local
não há: o kit é texto e scripts
```

**Stack:** Python 3.8+ só com a biblioteca padrão (scripts e gancho), `sh` POSIX no gancho,
Markdown nas skills, e pytest só na suíte do kit.

**Contagem esperada de testes:** no `validation.md` de cada fase: a contagem da fase anterior mais
os testes novos.

---

<!-- golem:inicio -->
## Como o Golem trabalha aqui

<!-- Gerado pelo `aplicar` do Golem. Não edite à mão: peça "configurar o Golem". -->

Receita `completo`; o guia é `docs/guia-configuracao.md`.

- **Revisor:** sempre, a cada grupo: o `revisor` lê o diff do grupo. Modelo `opus`.
- **Validador:** sempre, a cada grupo: o `validador` prova o diff do grupo. Modelo `opus`.
- **Guardião:** sempre, antes do merge: o `revisor` lê o diff inteiro do PR.
- **Os comandos do `validation.md`:** sempre, pela própria conversa, com a linha de resumo lida.
- **Parar a cada parte:** nunca: siga grupo a grupo.
- **Conversas:** os papéis de `docs/operacao-das-conversas.md`.
- **Gancho das lições:** ligado, até 4 lições novas por ação.
<!-- golem:fim -->

---

## Convenções

- Commits e PRs em português. Merge por merge commit.
- **Quem libera o merge.** Por padrão, o merge no repositório do projeto é **nível 2**: a conversa
  gerente (GER) libera pelo par PEDIDO → LIBERADO, depois de conferir o head, a base e a prova. Sem
  gerente (uma conversa só), o usuário faz esse papel. É **nível 3**, só com a palavra do usuário
  na conversa que executa:
  - o merge em repositório de terceiros (de outra equipe, de um cliente, um projeto aberto);
  - o merge que vai a produção (uma branch com deploy automático, uma branch de release);
  - o merge local, num projeto sem remoto (não há PR nem GER que confira: quem mergeia é o usuário);
  - nenhum além dos três acima.

  A mesma lista está em `docs/operacao-das-conversas.md`, "Níveis de autonomia": mudou aqui, muda
  lá no mesmo commit. No kit, aquele arquivo guarda a lacuna do modelo, e a regra vale entre ele e o
  `templates/AGENTS.md`.
- **Merge em duas chamadas:** primeiro a conferência do head e da base; depois, noutra chamada e
  com o LIBERADO (mais a palavra do usuário, no nível 3), o merge com o sha lido na saída. Ver
  `docs/operacao-das-conversas.md`, "Merge".
- **Quem muda, varre.** Mudou um caminho, um comando, uma contagem ou o nome de uma variável? Busque
  o nome antigo nos documentos e nos agentes (`.claude/agents/`, quando o projeto os tem) e corrija
  no mesmo commit. Caminho errado num agente não dá erro: ele lê nada e responde com a mesma
  confiança.
- O que é **gerado** (o índice da régua) se refaz pela régua do kit (`regua.py --gerar`; a skill
  `licao` diz o comando), nunca à mão. O bloco "Como o Golem trabalha aqui" (e, na cópia, o
  `model:` dos agentes) sai do `golem.toml` pelo `aplicar` do kit, que a skill `configurar` roda; no
  Golem central, o `golem.toml` do central vale por baixo do deste projeto. Na cópia (o kit dentro
  do projeto), os comandos são `python3 .claude/regua.py --gerar` e `python3 .claude/golem.py
  aplicar`. No Windows, `python` ou `py -3` no lugar de `python3`, aqui e em todo o kit. As cópias
  para o Codex (`.agents/skills/`, `.codex/`), que só usa a cópia, também são geradas: mudou uma
  skill ou um agente em `.claude/`, rode `python3 .claude/instalar_codex.py` e faça o commit das
  cópias junto
  (`--conferir` acusa a
  divergência). O repositório do próprio kit não versiona as cópias: quem instala o kit as gera no
  projeto dele (`README.md` do kit, "Usando com o Codex").
- Nenhum nome de cliente, de outro projeto ou de pessoa entra no kit, fora do crédito (a linha de
  crédito, o `LICENSE`, o `author` e o `owner` dos manifestos em `.claude-plugin/` e a seção
  "Licença e crédito" do `README.md`).

---

## Regras

> **Onde uma regra mora.** Regra que vale para toda tarefa fica aqui, curta e imperativa. A
> evidência que a justifica fica na lição citada (`docs/licoes/`). A regra manda; a lição explica.

1. **Spec antes do código.** Nenhuma implementação começa sem `requirements.md`, `plan.md` e
   `validation.md` da fase escritos e aprovados pelo usuário.
   - **Formato curto, para fase pequena:** a fase sem borda externa (API pública, outro sistema),
     sem deploy e que cabe num dia usa só o `requirements.md` e o `validation.md`, os dois numa
     página, com o plano numa seção "Como fazer" dentro do `requirements.md`. O que não encolhe:
     os critérios continuam sendo comando ou passo a passo (regra 4), e a spec é aprovada antes do
     código. Fora desse formato, ninguém improvisa "spec enxuta".
   *Por quê:* o que não está escrito some na próxima conversa, e o agente preenche o vazio com
   suposição.

2. **Uma fase por branch, mergeável sozinha.** Se o escopo não couber, divida o roadmap em vez de
   inchar a fase.
   *Por quê:* fase grande não se revisa de uma vez, e abandonada no meio deixa a `main` quebrada.

3. **Nenhuma dependência nova sem aprovação do usuário.** Algo fora da linha **Stack** dos
   "Comandos reais", inclusive dependência transitiva relevante: pare e proponha.
   *Por quê:* dependência é mudança de stack, não detalhe de implementação, e sai caro de tirar.

4. **Critério de validação é comando ou passo a passo.** Cada item do `validation.md` diz o comando
   e o resultado esperado, ou os passos que uma pessoa executa e o que ela deve ver. "Funciona
   corretamente" não é critério.
   *Por quê:* o agente diz "pronto" com a mesma confiança quando está errado; só a execução separa.

5. **Nada de credencial, token ou dado sensível no repositório.** Segredo vive fora do Git
   (o kit não tem segredo; o `golem.local.toml`, com o caminho do Python da máquina, fica no
   `.gitignore`). Não leia nem imprima segredo para "conferir".
   *Por quê:* o que entra no histórico do Git não sai mais de verdade.

6. **Não commitar sem o usuário pedir.** Aprovar o plano pode incluir "um commit por grupo na
   branch da fase"; fora disso, o trabalho fica pronto para commit, e quem pede é o usuário.
   *Por quê:* o commit é o ponto em que o usuário assume o que entrou.

7. **Armadilha descoberta vira lição versionada.** Quando **uma hipótese for refutada por
   evidência**, **uma premissa do projeto se revelar falsa**, **um defeito custar mais de uma
   rodada** para diagnosticar, ou **o usuário corrigir** um entendimento seu: registre em
   `docs/licoes/` pela skill `licao`, no formato de `docs/licoes/README.md`, faça o `git add` dela
   e regere o índice pela régua do kit (a skill `licao` diz o comando). Só esses quatro motivos: se
   não dá para escrever "o que se achava", não é lição. Quando a lição implicar ação obrigatória,
   acrescente aqui uma regra curta que a cite, se ela vale para toda tarefa; a que só muda a decisão
   de quem mexe numa área vai ao `docs/regras-de-area.md` (a skill `licao` traz o formato).
   Preferência do usuário e estado do projeto não são lição: vão para a memória.
   *Por quê:* a conversa seguinte não sabe o que esta aprendeu, e o gancho só entrega o que está
   escrito.

8. **Suíte verde só vale com a linha de resumo lida.** Leia o total de testes, as falhas **e as
   puladas** na saída, e compare com a contagem esperada. Pulado a mais é falha até prova em
   contrário. Opção que esconde o resumo (como `-q` em dobro no pytest) não se usa.
   *Por quê:* "passou" sem o resumo pode ser zero testes coletados ou metade deles pulada.

9. **Fato que sustenta spec ou decisão se confere na fonte, na hora.** Todo fato que sustenta uma
   spec, uma opção levada ao usuário ou um texto a terceiros (código, config, versão, contagem,
   quem tem acesso a quê) se cita com `arquivo:linha` (e o commit, quando o código muda) ou com a
   saída do comando. Memória, resumo de contexto, mensagem de outra conversa e a spec anterior são
   **hipótese** até serem conferidos.
   - Resposta do usuário que implica fato técnico ("tenho acesso a X", "isso já existe"): confirme
     o sentido exato e ache o caminho no código ou na config **antes** de escrever na spec.
   - Decisão do usuário entra com **as palavras dele e a data**; o que ela implica tecnicamente fica
     "a conferir" até ser verificado.
   - Na fronteira de cada grupo e depois de toda compactação de contexto, releia do disco o
     `plan.md` e a spec, e reconfira os fatos-chave.
   - Na dúvida, escreva "a conferir" e o que falta, em vez de afirmar.
   *Por quê:* o resumo carrega a conclusão e perde a ressalva, e a spec escrita de memória vira a
   referência que todo mundo cita depois.

10. **Simplicidade: o menor que resolve o problema de hoje.**
    - Nada "por precaução" ou "para o futuro": nem peça nova, nem validação extra, nem camada de
      defesa sem uma falha vista que a justifique. A falha vista pode vir do uso de quem recebe o
      que você entrega (o relato de um usuário, um teste com jogadores, o projeto de quem usa um
      kit), escrita com a fonte, sem precisar aparecer antes no repositório (lição
      `num-produto-a-falha-vista-vem-do-uso`).
    - Reuse o que existe antes de criar. Arquivo, módulo, flag, config ou tabela nova pedem um caso
      real, com exemplo concreto na spec ou no PR.
    - Nada de abstração antes do terceiro uso real: duas cópias parecidas são melhores que uma
      abstração errada.
    - Prefira a mudança que se desfaz sem migração. Teste proporcional ao que mudou.
    - "Não mudar nada" é resposta válida.
    - **Produto e arquitetura são do usuário; o detalhe de implementação é do agente.** Dentro de
      uma spec aprovada, o agente segue grupo a grupo sem pedir licença, salvo com o "parar a cada
      parte" do bloco "Como o Golem trabalha aqui": aí ele para ao fim de cada grupo, mostra o
      diff e espera o ok. Ele pergunta quando a escolha muda o que o usuário ou o cliente vê e a
      spec não traz, ou sai do escopo; aí propõe até duas opções simples, mais "não mudar nada".
    - Antes de entregar: "o que eu posso tirar e ainda resolver o problema?". O que puder sair, sai.
    *Por quê:* agente escreve código barato e mantém código caro; cada peça a mais é peça que alguém
    vai ter de entender, mudar e apagar.

11. **Revisor e validador independentes, conforme a configuração.** O bloco "Como o Golem trabalha
    aqui" diz se cada um roda (`sempre`, `perguntar` ou `nunca`), se por grupo ou uma vez por fase,
    e o guardião; sem o bloco, rode o `aplicar`, e sem Python vale a `economico`. Delegue a
    eles: no Claude Code, são os do kit (`golem:revisor` e `golem:validador` no Golem central, os de
    `.claude/agents/` na cópia), chamados com o modelo que o bloco diz, passado na chamada (outro
    modelo só se a spec da fase pedir): o guardião, com o do revisor; com "o da conversa", o
    modelo desta conversa. No Codex, os de `.codex/agents/` (gerados pelo instalador). Os dois só leem. O revisor dá "sem bloqueio" ou "com bloqueio"; o
    validador dá "valida" ou "não valida". Bloqueio se corrige e volta à revisão.
    - **Os comandos do `validation.md` rodam sempre**, pela própria conversa, com a linha de resumo
      lida (regras 4 e 8), qualquer que seja a configuração.
    - **Com `perguntar`**, a etapa vira uma pergunta com botões na hora em que chega, com o custo
      ("abre 1 conversa extra"); em texto numerado onde não houver botões. Só roda com o sim.
    - **Caminho rápido:** quando o validador rodaria, o grupo ou o PR só de documentação (os `.md`,
      inclusive skills, agentes e lições) ou só de testes leva **só o revisor, se ele roda**. O
      revisor confere fato por fato contra a fonte, e não só a forma. Se ganhar código (inclusive
      script em `.claude/`), ou se o revisor apontar algo importante, volta ao caminho completo. Não
      se fatia uma mudança grande para caber no caminho rápido.
    - **O guardião**, quando roda: antes do merge do PR com código, o agente `revisor` sobre o
      **diff inteiro do PR**, numa conversa nova (ou num subagente novo, sem o contexto de quem
      escreveu). Ele vê o que a revisão grupo a grupo não vê: o efeito somado.
    - Quem revisa trata como achado: afirmação sem fonte, peça sem caso real, abstração prematura e
      escopo além do pedido.
    *Por quê:* quem escreveu lê o que quis escrever; um leitor sem esse viés acha o que o autor não
    vê, e a execução acha o que a leitura não acha.

12. **Nada vai a terceiros sem o usuário.** Comentário em issue ou PR, mensagem a outra pessoa ou
    equipe, texto a cliente, publicação: o agente redige, o usuário lê e dá o ok **na conversa que
    executa**, e só então sai. Agentes não combinam decisões com pessoas ou agentes de fora.
    *Por quê:* o que sai fala em nome do usuário e não se desfaz.

Regras do kit a partir da 13: nenhuma por ora.

---

## Skills e agentes

Versionados em `.claude/skills/` e `.claude/agents/`, e as cópias do Codex em `.agents/skills/` e
`.codex/agents/` (no projeto que usa o kit; ver "Convenções"): clonar o repositório reproduz o
ambiente nos dois agentes.

O fluxo normal é `spec-de-fase` → `implementar-fase` → `validar-fase`, com `licao` sempre que a
regra 7 disparar e `replanejar-roadmap` quando o plano envelhecer. Os agentes `revisor` e
`validador` servem à regra 11. O fluxo inteiro está em `WORKFLOW.md`.

Skill nova só aparece em sessão nova: reinicie o agente (Claude Code ou Codex) depois de adicionar
uma. No Codex (que usa o kit copiado no projeto), rode antes `python3 .claude/instalar_codex.py`.
