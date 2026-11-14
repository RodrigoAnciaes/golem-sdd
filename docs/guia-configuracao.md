# Guia de configuração do Golem

O Golem trabalha conforme o `golem.toml`, na raiz do projeto. Sem o arquivo, vale a receita
`economico`. O jeito mais fácil de mudar é pedir **"configurar o Golem"** e responder aos botões:
a skill `configurar` escreve o arquivo e roda o `aplicar`. A configuração nova vale numa conversa
nova.

## As três receitas

As receitas são os recomendados do kit. Cada linha escrita no `golem.toml` vale mais que a receita.

| Chave | `so-eu` | `economico` (o padrão) | `completo` (o fluxo de várias conversas) |
|---|---|---|---|
| `revisor` | `nunca` | `sempre` | `sempre` |
| `revisor_quando` | `por_fase` | `por_fase` | `por_grupo` |
| `modelo_revisor` | `sonnet` | `sonnet` | `opus` |
| `validador` | `nunca` | `nunca` | `sempre` |
| `modelo_validador` | `opus` | `opus` | `opus` |
| `guardiao` | `nunca` | `nunca` | `sempre` |
| `parar_a_cada_parte` | `sempre` | `sempre` | `nunca` |
| `conversas` | `uma` | `uma` | `papeis` |
| `gancho` | `ligado` | `ligado` | `ligado` |
| `gancho_teto` | `2` | `2` | `4` |

- **`so-eu`:** para quem não quer revisão. Nenhuma conversa extra.
- **`economico`:** o padrão, pensado para o plano Pro. Uma conversa extra por fase: um revisor no
  Sonnet sobre o que a fase inteira mudou.
- **`completo`:** o fluxo do projeto de origem do kit. Numa fase de 3 partes, até 7 conversas
  extras: revisor e validador a cada parte, e o guardião.

## O que cada chave faz, e o que custa

- **`revisor`** (`sempre`, `perguntar`, `nunca`): um subagente que lê o que foi feito contra a spec
  e as regras. Cada rodada é uma conversa extra: com o validador, é o maior custo medido do kit
  (`docs/plano-produto.md`, seção 1.2). Com `perguntar`, o agente pergunta na hora, com botões,
  dizendo o custo.
- **`revisor_quando`** (`por_fase`, `por_grupo`): uma vez, ao fim do último grupo, sobre o diff da
  fase inteira; ou a cada grupo. O validador segue o mesmo quando.
- **`modelo_revisor`, `modelo_validador`** (`sonnet`, `opus`, `haiku`, `inherit`): o modelo do
  subagente. O `inherit` usa o da conversa. A conferir: quais modelos o plano Pro mostra no
  `/model`.
- **`validador`** (`sempre`, `perguntar`, `nunca`): um subagente que roda tudo de novo e tenta
  quebrar o código numa cópia (a mutação). Os comandos do `validation.md` rodam sempre, pela própria
  conversa, com ou sem ele.
- **`guardiao`** (`sempre`, `perguntar`, `nunca`): o revisor de novo, sobre o diff inteiro do PR,
  antes do merge.
- **`parar_a_cada_parte`** (`sempre`, `nunca`): com `sempre`, a implementação para ao fim de cada
  grupo, mostra o que mudou e espera o seu ok. Custa um turno a mais por parte, que relê o contexto
  da conversa (`docs/plano-produto.md`, seção 1.2): bem menos que uma conversa extra.
- **`conversas`** (`uma`, `papeis`): uma conversa só, ou os papéis de
  `docs/operacao-das-conversas.md` (gerente e frentes), que valem quando há várias entregas ao mesmo
  tempo. Cada conversa a mais é uma sessão inteira, com o próprio histórico.
- **`gancho`** (`ligado`, `desligado`): o gancho entrega as lições antes de cada ação. Desligado, as
  lições se buscam à mão em `docs/licoes/` (o modo sem Python, abaixo).
- **`gancho_teto`** (de 1 a 10): quantas lições novas o gancho entrega por ação. Cada lição custa
  uns 550 bytes, cerca de 150 tokens.

## O que nenhuma receita corta

A spec com entrevista, a sua aprovação, os critérios como comando, as lições e a regra de
simplicidade. Sem revisor nem validador, fica sem a leitura e a prova independentes, mas os comandos
do `validation.md` continuam rodando.

## Mudar à mão

Abra o `golem.toml`, tire o `#` da linha que quiser mudar (ou escreva-a) e rode:

```bash
python3 .claude/golem.py aplicar
```

No Windows, `python` ou `py -3` no lugar de `python3`. Um valor errado faz o `aplicar` parar sem
escrever nada e dizer a linha. O `aplicar` escreve o bloco "Como o Golem trabalha aqui" do
`AGENTS.md` e o `model:` dos agentes; não edite esses trechos à mão.

```toml
# golem.toml: como o Golem trabalha neste projeto.
# O jeito mais fácil de mudar: peça "configurar o Golem" e responda aos botões.
receita = "economico"            # so-eu | economico | completo

# Opcional. Cada linha abaixo vale mais que a receita; tire o # da que quiser mudar.
# revisor          = "perguntar"   # sempre | perguntar | nunca
# revisor_quando   = "por_fase"    # por_fase | por_grupo
# modelo_revisor   = "sonnet"      # sonnet | opus | haiku | inherit
# validador        = "nunca"       # sempre | perguntar | nunca
# modelo_validador = "opus"
# guardiao         = "nunca"       # sempre | perguntar | nunca
# parar_a_cada_parte = "sempre"    # sempre | nunca
# conversas        = "uma"         # uma | papeis
# gancho           = "ligado"      # ligado | desligado (máquina sem Python)
# gancho_teto      = 2             # lições novas por ação, de 1 a 10
```

## Sem Python

Escrever o `golem.toml` não precisa de Python; aplicá-lo, sim. Sem Python, a linha
`gancho = "desligado"` vale assim mesmo: o gancho a lê em `sh` e para de avisar a cada ação. O resto
da configuração fica escrito, esperando um Python para o `aplicar`. Para achar ou instalar um
Python, peça o diagnóstico do Golem.
