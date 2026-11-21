---
name: configurar
description: Configura como o Golem trabalha neste projeto e quanto ele gasta. Pergunta com botões a receita (so-eu, economico ou completo), o revisor e se a implementação para a cada parte, escreve o golem.toml e roda o golem aplicar. Use quando o usuário disser "configurar o Golem", "mudar a receita", "quero gastar menos", "não quero o revisor", "parar a cada parte" ou invocar /configurar.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Configurar o Golem

**Lê:** o `golem.toml` da raiz, se existir, e a linha `python` do `golem.local.toml`.
**Escreve:** o `golem.toml` da raiz. Pelo `aplicar`, escreve também o bloco "Como o Golem trabalha
aqui" do `AGENTS.md` e o `model:` dos agentes `revisor` e `validador`. Sem Python, com o modo sem
Python aceito, troca à mão só a linha do gancho nesse bloco.
**Decide:** nada sozinha. Pergunta, mostra o arquivo e só grava depois do ok. O commit é do
usuário.

As receitas, cada chave e o que ela custa estão em `docs/guia-configuracao.md`. Abra o guia só se o
usuário perguntar algo que esta skill não responde.

## 1. Ver o que já existe

```bash
cat golem.toml 2>/dev/null || echo "sem golem.toml: vale a receita economico"
```

Se o arquivo existe, ponha-o inteiro no texto da primeira pergunta do passo 2: um texto à parte,
entre a leitura e a pergunta, se perde (lição `o-aviso-entre-duas-perguntas-fica-no-raciocinio`).
As linhas das chaves que esta skill não pergunta (todas, menos
`receita`, `revisor` e `parar_a_cada_parte`) ficam como estão.

## 2. Perguntar

Pergunte com botões (no Claude Code, a ferramenta de pergunta), em duas chamadas: primeiro a
receita, sozinha; depois as outras duas, já sabendo a receita. Onde não houver botões, faça em texto
numerado. Cada opção tem um rótulo curto ("Sempre") e o resto na descrição. A recomendada vem
primeiro.

**Nunca ofereça "o da receita"**: quem configura pela primeira vez não sabe o que a receita faz.
Diga o valor por extenso e de qual receita ele vem, pela tabela do guia.

1. **"Como o Golem deve trabalhar neste projeto?"**
   - `economico` (recomendado): um revisor, no Sonnet, uma vez por fase; para ao fim de cada parte
     para o seu ok;
   - `so-eu`: nenhuma conversa extra; ninguém além desta conversa lê o que foi feito; para ao fim
     de cada parte para o seu ok;
   - `completo`: revisor e validador, no Opus, a cada parte, mais o guardião antes do merge (até 7
     conversas extras numa fase de 3 partes); segue sem parar.
2. **"O revisor, uma conversa extra que lê o que foi feito:"** as três opções, com a da receita
   escolhida primeiro e marcada como recomendada. Na `economico`, por exemplo:
   - "Sempre": uma vez por fase, no Sonnet (recomendado: é o que a `economico` faz);
   - "Perguntar na hora": antes de rodar, pergunta com botões (abre 1 conversa extra se você
     aceitar);
   - "Nunca": "O revisor não roda. Sem revisão, ninguém além desta conversa lê o que foi feito; os
     comandos do `validation.md` continuam rodando."

   A descrição do "Nunca" é o aviso do que fica sem revisão, e vai inteira no botão, não num texto
   à parte. Ela segue o `golem.toml` que vai sair: com o validador e o guardião em `nunca` (a
   `so-eu`, a `economico`), é a frase acima; senão (a `completo`), é "O revisor não roda;
   continuam" e cada um dos dois que não está em `nunca`, com o quando da tabela do guia: o
   validador "a cada parte" ou "uma vez por fase", pelo `revisor_quando`, e o guardião "antes do
   merge"; em `perguntar`, acrescente "se você aceitar". Na `completo`, o "Sempre" é "a cada parte,
   no Opus"; na `so-eu`, a recomendada é o "Nunca".
3. **"Parar ao fim de cada parte para você aprovar?"** do mesmo jeito: "Sim", para e espera o seu
   ok (recomendado: é o que a `economico` faz), e "Não", segue sem parar; na `completo`, a
   recomendada é o "Não".

Se o `golem.toml` já tem uma linha `revisor` ou `parar_a_cada_parte`, marque "(o atual)" na opção
de mesmo valor. Não há opção "manter": o valor atual já é uma das opções.

A escolha é do usuário.

## 3. Escrever o `golem.toml`

Escreva a `receita` e só as linhas que diferem dela: o `revisor`, se a resposta for diferente do
valor da receita; o `parar_a_cada_parte` (`sempre` para sim, `nunca` para não), pela mesma regra.
Uma linha `revisor` ou `parar_a_cada_parte` que já existia sai quando a resposta é o valor da
receita. Mantenha as linhas das outras chaves e os comentários que já existiam. A tabela das
receitas está no guia.

```toml
# golem.toml: como o Golem trabalha neste projeto.
# O jeito mais fácil de mudar: peça "configurar o Golem" e responda aos botões.
receita = "economico"            # so-eu | economico | completo
```

Peça o ok com botões ("Gravar e aplicar" ou "Não gravar"), e ponha o arquivo inteiro, com os
comentários, dentro do texto da própria pergunta, depois da frase "Gravo este `golem.toml` e rodo o
`golem aplicar`?". Um resumo dos valores não basta, e um texto à parte, antes da pergunta, se perde.
Grave só depois do ok.

## 4. Achar o Python

O `aplicar` precisa de um Python 3.8+. Procure na ordem do gancho (`.claude/hooks/gancho.sh`): a
linha `python` do `golem.local.toml`, o `.venv` da raiz e o da pasta principal, o PATH e os lugares
do instalador do Windows.

```bash
principal=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
grep -h '^[[:space:]]*python[[:space:]]*=' golem.local.toml "$principal/golem.local.toml" 2>/dev/null
ls .venv/Scripts/python.exe .venv/bin/python \
   "$principal"/.venv/Scripts/python.exe "$principal"/.venv/bin/python 2>/dev/null
command -v python3 python py
ls "$LOCALAPPDATA"/Programs/Python/Python3*/python.exe \
   "$LOCALAPPDATA"/Programs/Python/Launcher/py.exe \
   "$PROGRAMFILES"/Python3*/python.exe 2>/dev/null
```

Rode em cada candidato o teste do passo 4 da skill `diagnostico` (para o `py`, com `-3`). O `PY` é
o caminho que o primeiro a passar imprime (o `sys.executable`), e não o nome do candidato: assim o
`"$PY"` do passo 5 funciona também quando quem achou foi o `py -3`.

**Sem nenhum Python:** faça a pergunta do Python da skill `diagnostico`, passos 2 a 6, sem a oferta
do modo sem Python do passo 6 (ela vem aqui, uma vez só). Se ainda não houver Python:
- o `golem.toml` fica escrito;
- ofereça o modo sem Python, com botões ("Desligar o gancho das lições?", sim ou não), e ponha no
  texto da própria pergunta que o `aplicar` fica pendente e que o bloco do `AGENTS.md` continua com
  a configuração anterior até o `aplicar` rodar numa máquina com Python. Com o sim,
  ponha `gancho = "desligado"` no `golem.toml`. Isso vale já, sem Python: o gancho para de avisar a
  cada ação, e as lições passam a ser buscadas à mão em `docs/licoes/`. Troque também, à mão, no
  bloco do `AGENTS.md`, só a linha do gancho pela que o `aplicar` gera (o texto está no passo 6 da
  skill `diagnostico`): sem isso, o bloco continua dizendo "ligado" a cada turno.

## 5. Aplicar

```bash
"$PY" .claude/golem.py aplicar
```

- Mostre a saída. Se vier `ERRO`, mostre a linha que ele cita e corrija o `golem.toml` com o
  usuário.
- Diga que a configuração nova vale numa **conversa nova**: o `AGENTS.md` desta já foi lido.
- Diga o que mudou (o `golem.toml`, o `AGENTS.md`, os agentes) e que o commit é dele.
