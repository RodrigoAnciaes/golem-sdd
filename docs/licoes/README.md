# Lições

Armadilhas técnicas e erros de diagnóstico do projeto. Uma lição por arquivo, com frontmatter YAML
para a busca e o gancho, e prosa curta para o resto.

**O que é uma lição:** *"achávamos X, era Y, e descobrir isso custou caro."*

## Onde cada coisa mora

| Lugar | O que guarda | Modo |
|---|---|---|
| `AGENTS.md` | as regras a seguir | imperativo, curto |
| `docs/adr/` | as decisões caras de reverter | contexto, opções, consequências |
| `specs/` | o que foi construído e por quê | por fase |
| `CHANGELOG.md` | o que mudou, por data | cronológico |
| **`docs/licoes/`** | **a armadilha que custou caro descobrir** | o que se achava × o que é |

Uma lição vira **também** regra no `AGENTS.md` quando implica ação obrigatória daqui para frente.
A regra fica lá, curta, e cita a lição; a lição fica aqui, com o porquê e a evidência. A regra não
repete a lição.

## Quando escrever uma

Não é a cada pergunta: um acervo cheio de trivialidades é tão inútil quanto nenhum. Escreva quando
**um** destes quatro motivos acontecer (não confunda com o campo `gatilhos:`, mais abaixo, que diz
em que ação a lição chega):

1. **uma hipótese foi refutada por evidência**: você afirmou algo e a medição mostrou outra coisa;
2. **uma premissa do projeto se revelou falsa**: "o serviço usa o cache", e não usava;
3. **um defeito custou mais de uma rodada** para diagnosticar;
4. **o usuário corrigiu** um entendimento seu.

Se você não consegue escrever a seção "O que se achava", não é lição: é documentação, e o lugar
dela é outro. Preferência do usuário e estado do projeto vão para a memória do agente.

## Atualizar em vez de criar

Antes de criar, procure (abaixo, "Como buscar"). Se já existe uma lição sobre a mesma armadilha:

- **o mesmo erro voltou noutra forma:** acrescente o caso novo na lição existente, com a data;
- **o sinal mudou ou ficou mais preciso:** reescreva o "Como perceber da próxima vez";
- **a lição estava errada:** corrija e diga, numa linha, o que mudou e quando.

Lição de um sistema que saiu de uso vai para `docs/licoes/arquivo/`: continua consultável, mas sai
do índice e o gancho não a entrega mais. Lição fundida noutra vai para o mesmo lugar, com uma linha
no topo dizendo qual vale.

## Formato

Nome do arquivo: `<id>.md`.

```markdown
---
id: kebab-case-curto-e-descritivo     # igual ao nome do arquivo, sem .md
data: AAAA-MM-DD                      # quando foi descoberta
area: codigo                          # codigo | deploy | contrato | processo
tipo: armadilha                       # premissa-falsa | armadilha | erro-de-diagnostico | custo-escondido
custo: "uma linha: tempo, rodadas, deploy, dinheiro"
gatilho: "em que circunstância apareceu"
refs:
  - caminho/do/arquivo.py:123
  - specs/AAAA-MM-DD-nome/validation.md
gatilhos:                             # opcional: em que ação o gancho entrega (ver abaixo)
  - '\bpytest\b'
---

**O que se achava:** duas a quatro linhas.

**O que é:** duas a quatro linhas, com a evidência.

**Como perceber da próxima vez:** o sinal observável. É a seção mais importante.
```

A terceira seção é a que dá valor ao acervo. "Tome cuidado" não serve; serve *"a lista de horários
vem vazia só para os médicos cujo expediente passa da meia-noite"*.

Os dois campos de nome parecido: **`gatilho:`** (singular) é a circunstância, em prosa, em que a
armadilha apareceu, para quem lê; **`gatilhos:`** (plural, opcional) é a lista de expressões
regulares que dizem ao gancho em que ação entregar a lição (abaixo).

**Depois do "Como perceber", nenhum rótulo em negrito terminado em dois pontos no começo de
linha.** O gancho entrega a seção até o próximo rótulo assim, e o que vem depois não chega. Uma
atualização leva rótulo terminado em ponto: `**Atualização de AAAA-MM-DD: o que mudou.**`.

## Vocabulário controlado

Mantenha `area` e `tipo` nestes valores: é o que faz a busca por campo funcionar. Valor novo só com
motivo, e atualize junto esta lista e o `AREAS_VALIDAS` ou o `TIPOS_VALIDOS` do `.claude/regua.py`
(a régua recusa valor fora deles). Área nova também pede o `POR_CAMINHO` e o `POR_COMANDO` do
`.claude/hooks/licoes_relevantes.py`, que dizem em que ação cada área acende.

### `area`

- **`codigo`**: o comportamento do código da aplicação e das bibliotecas.
- **`deploy`**: subir, configurar e operar os ambientes (contêineres, nuvem, variáveis, segredos).
- **`contrato`**: a fronteira com outro sistema: API, formato de dados, quem consome o quê.
- **`processo`**: o próprio método: testes, revisão, git, specs, as conversas.

### `tipo`

- **`premissa-falsa`**: acreditávamos em algo sobre o sistema que não era verdade.
- **`armadilha`**: o comportamento é correto, mas engana quem não sabe.
- **`erro-de-diagnostico`**: a leitura da evidência estava errada, não o sistema.
- **`custo-escondido`**: funcionava, mas cobrava um preço que ninguém tinha medido.

## Como o gancho entrega as lições

O gancho em `.claude/hooks/` roda antes de uma ação do agente (editar ou escrever um arquivo,
rodar um comando) e põe no contexto o "Como perceber da próxima vez" das lições que importam para
aquela ação. Ele não lê os arquivos de lição um a um: lê o **índice** que a régua gera
(`.claude/indice/licoes.yaml`). Por isso, **depois de criar ou editar uma lição, rode:**

```bash
git add docs/licoes/<id>.md          # a régua só indexa o que o git conhece
python3 .claude/regua.py --gerar     # no Windows, python ou py -3
```

Lição fora do índice não é entregue a ninguém. Confira: o id novo tem de aparecer no diff do
índice. Se não aparecer, o arquivo não foi visto (faltou o `git add`).

### `gatilhos:` — em que ação a lição chega

Sem `gatilhos:`, o gancho decide pela `area`: toda lição da área da ação é candidata. Para áreas
largas (`processo` acende com qualquer rodada de testes ou `git push`), isso traz lição demais, e
o agente passa a ignorar todas.

Com `gatilhos:`, a lição só é candidata quando um deles casa com a ação, e passa na frente das que
vieram só pela área. A `area` continua obrigatória: é ela que a busca usa.

- Cada item é uma **expressão regular** (Python, sem diferenciar maiúsculas), testada contra o
  **caminho do arquivo** da ação e contra o **comando** inteiro. Basta um casar.
- O caminho pode chegar absoluto. Não ancore com `^`: escreva `/specs/` ou
  `specs/[^/]+/plan\.md$`, nunca `^specs/`.
- **Lista em bloco, um item por linha, entre aspas simples** (`  - '\bpytest\b'`): dentro delas,
  nada é escape. Entre aspas duplas, o YAML come a barra (`"\b"` vira outro caractere).
- **Não ponha gatilho que case com tudo.** `.`, `.*`, `git`, `py` ou `docs/` casam com quase toda
  ação e trazem de volta o ruído. O gatilho descreve a ação em que o erro acontece:
  `\bgit\s+push\b`, não `git`. Antes de gravar, pense em três ações comuns que **não** deveriam
  receber a lição e confira que nenhuma casa.
- Regex inválida não derruba o gancho: ele a ignora. Quem acusa é a régua, no `--gerar`.

## Como buscar

Exclua este `README.md` da busca: ele contém o modelo e aparece em toda busca por campo.

```bash
# por área
grep -l '^area: deploy' docs/licoes/*.md | grep -v README.md

# por tipo
grep -l '^tipo: premissa-falsa' docs/licoes/*.md | grep -v README.md

# por assunto, no texto todo
grep -il 'cache' docs/licoes/*.md | grep -v README.md

# o que toca um arquivo específico
grep -l 'src/agenda/' docs/licoes/*.md | grep -v README.md
```

Exemplos de lições prontas estão nesta pasta.
