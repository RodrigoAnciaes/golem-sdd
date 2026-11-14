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

Se o arquivo existe, mostre-o. As linhas das chaves que esta skill não pergunta (todas, menos
`receita`, `revisor` e `parar_a_cada_parte`) ficam como estão.

## 2. Perguntar

Faça as três perguntas numa chamada só, com botões (no Claude Code, a ferramenta de pergunta). Onde
não houver botões, faça em texto numerado. A recomendada vem primeiro.

1. **"Como o Golem deve trabalhar neste projeto?"**
   - `economico` (recomendado): um revisor, no Sonnet, uma vez por fase; para ao fim de cada parte
     para o seu ok;
   - `so-eu`: nenhuma conversa extra; ninguém além desta conversa lê o que foi feito; para ao fim
     de cada parte para o seu ok;
   - `completo`: revisor e validador, no Opus, a cada parte, mais o guardião antes do merge (até 7
     conversas extras numa fase de 3 partes); segue sem parar.
2. **"O revisor, uma conversa extra que lê o que foi feito:"**
   - o da receita (recomendado); se o `golem.toml` já tem uma linha `revisor`, esta opção vira
     "manter o atual (`<valor>`)";
   - sempre;
   - perguntar na hora (com o custo);
   - nunca.
3. **"Parar ao fim de cada parte para você aprovar?"**
   - o da receita (recomendado); com uma linha `parar_a_cada_parte` no arquivo, "manter o atual";
   - sim;
   - não.

Se o resultado ficar sem revisor, sem validador e sem guardião (a `so-eu`, ou a `economico` com o
revisor `nunca`), diga numa linha: "Sem revisão, ninguém além desta conversa lê o que foi feito; os
comandos do `validation.md` continuam rodando." Se ficar sem revisor, mas com o validador ou o
guardião, diga que o revisor sai e quais deles continuam. A escolha é do usuário.

## 3. Escrever o `golem.toml`

Escreva a `receita` e só as linhas que diferem dela: o `revisor`, se a resposta não for "o da
receita" e for diferente do valor da receita; o `parar_a_cada_parte` (`sempre` para sim, `nunca` para
não), pela mesma regra. Uma linha `revisor` ou `parar_a_cada_parte` que já existia sai quando a
resposta é "o da receita"; com "manter o atual", ela fica. Mantenha as linhas das outras chaves
e os comentários que já existiam. A tabela das receitas está no guia.

```toml
# golem.toml: como o Golem trabalha neste projeto.
# O jeito mais fácil de mudar: peça "configurar o Golem" e responda aos botões.
receita = "economico"            # so-eu | economico | completo
```

Mostre o arquivo inteiro e grave depois do ok.

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
- diga que o `aplicar` fica pendente e que o bloco do `AGENTS.md` continua com a configuração
  anterior até o `aplicar` rodar numa máquina com Python;
- ofereça o modo sem Python, com botões ("Desligar o gancho das lições?", sim ou não). Com o sim,
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
