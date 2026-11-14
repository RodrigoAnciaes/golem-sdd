---
name: implementar-fase
description: Executa o plan.md da fase em andamento, grupo por grupo, com a revisão independente que a configuração do projeto pede (revisor e validador, por grupo ou por fase), mantendo a spec e o código em sincronia e parando quando algo exigir decisão humana. Use quando o usuário disser "implementar a fase", "executar o plano", "seguir com o grupo N", "pode implementar" ou invocar /implementar-fase.
license: "MIT. © 2026 Rodrigo Anciães Patelli. Golem SDD, https://github.com/RodrigoAnciaes/golem-sdd (texto em .claude/LICENSE)"
---

# Implementar a fase

**Lê:** `specs/AAAA-MM-DD-<fase>/plan.md` e `requirements.md` primeiro; o código depois, só o que o
grupo em execução toca.
**Escreve:** o código da fase, e a **própria spec** quando a realidade a contradiz. Spec e código
saem sincronizados ou a fase não fechou.
**Decide:** o detalhe de implementação, sozinha. Para e pergunta quando o plano não cobre um caso
que o usuário final vê, quando aparece dependência nova ou quando a mudança toca uma fronteira com
outro sistema ou outra equipe.

## Antes de escrever código

1. Confirme a branch: precisa ser a da fase, nunca a `main`.
2. Leia, nesta ordem: `requirements.md`, `plan.md`, `validation.md` da fase, e depois
   `specs/tech-stack.md`.
3. Leia o arquivo apontado em "padrões a seguir" no `requirements.md`. Copie o padrão de lá em vez
   de inventar um novo.
4. Busque as lições da área que vai tocar direto em `docs/licoes/` (por exemplo,
   `grep -il <termo> docs/licoes/*.md`, com o nome do arquivo, do comando ou da ferramenta), aqui e
   de novo antes de rodar os testes. Vale com ou sem gancho: sem Python, o gancho pode estar
   desligado e o índice envelhece. Armadilha registrada não se paga duas vezes.
5. Leia o bloco "Como o Golem trabalha aqui" do `AGENTS.md`: ele diz que revisão roda, quando, e
   se a implementação para a cada grupo. Sem o bloco (um `AGENTS.md` sem as marcas), rode
   `python3 .claude/golem.py aplicar`; sem Python, siga a receita `economico`
   (`docs/guia-configuracao.md`).

## Execução

- **Um grupo do plano por vez**, na ordem. O grupo fecha com:
  1. a suíte da pasta tocada, com a linha de resumo lida (total, falhas, puladas). Erro acumulado
     entre grupos custa muito mais caro para diagnosticar;
  2. a revisão que o bloco pede, por subagentes que não escreveram o código (o revisor lê o diff
     contra a spec; o validador roda os critérios e confere a evidência):
     - **por grupo:** o revisor e o validador que estiverem em `sempre`, sobre o diff do grupo;
     - **por fase:** nada aqui. Os que estiverem em `sempre` (ou em `perguntar`, com o sim) rodam
       uma vez, ao fim do último grupo de implementação (antes do grupo de verificação), sobre o
       diff da fase inteira. Com bloqueio, corrija e revise de novo antes de seguir;
     - **`perguntar`:** antes de rodar, a pergunta com botões e o custo (regra 11); só roda com o
       sim. O caminho rápido também é da regra 11;
  3. **se o usuário pediu commits ao aprovar o plano** (regra 6 do `AGENTS.md`), o commit do
     grupo na branch da fase, por caminho explícito (`git add <arquivos>`, nunca `git add -A`);
     sem esse pedido, o trabalho fica pronto para commit;
  4. as tarefas marcadas `[x]` no `plan.md`;
  5. **com o parar a cada parte:** o que o grupo mudou (o `git show --stat HEAD` com o commit do
     grupo, ou o `git diff --stat` sem ele, e o trecho que importa) e uma linha do que mudou, e o
     turno termina esperando o ok do usuário. No último grupo de implementação, a revisão por
     fase, se houver, roda antes dessa parada, e o veredito vai junto.
- **Sem o parar a cada parte, fim de grupo não é fim de turno.** Com o plano aprovado, diga numa
  linha curta, sem fecho, o que mudou, e comece o próximo grupo no mesmo turno. O turno só termina
  num bloqueio real (um PEDIDO à conversa gerente, a GER; uma decisão ou um gasto do usuário; a
  espera da CI; o "Pare e pergunte quando" abaixo) ou com o plano feito. Esperar o revisor do grupo em segundo plano também
  termina o turno, com `Espera: nada — revisor do grupo N`; quando o veredito chega, aplique-o, faça
  o commit do grupo (se o usuário pediu commits) e siga sem perguntar. Fechar com `Espera: nada` e
  grupos pela frente, sem revisor em curso, é o sinal do erro.
- **Fim de grupo também não é PR pronto.** Com grupo pela frente, o PR fica em rascunho.
- **Só toque no que a fase pede.** Achou problema fora do escopo? Na primeira que servir: urgente,
  à GER; armadilha que cumpre um dos quatro motivos da regra 7, lição na hora (skill `licao`); afeta
  uma frente em andamento, à GER; o resto, uma linha em "Depois (não planejado)" do
  `specs/roadmap.md`, ou no lugar que `docs/operacao-das-conversas.md` indicar. Registre, siga a
  fase e cite o registro na mensagem final.
- **Ao retomar depois de uma compactação de contexto**, releia do disco o `plan.md` e a spec, e
  reconfira na fonte os fatos-chave (heads, citações `arquivo:linha`). Resumo automático carrega a
  conclusão e perde a ressalva.

## Quando a realidade contradiz a spec

Acontece, e é sinal de que a spec está viva. A ordem é sempre a mesma:

1. Pare de implementar.
2. Explique ao usuário o que foi descoberto e as opções, cada uma com a consequência e a
   recomendada primeiro.
3. Atualize `requirements.md` (seção Decisões) e `plan.md`.
4. Só então volte ao código.

Registre a mudança na tabela "Alterações de escopo durante a fase" do `plan.md`.

## Pare e pergunte quando

- for preciso algo fora de `specs/tech-stack.md`, inclusive dependência transitiva
- a spec for ambígua a ponto de duas implementações razoáveis divergirem no que o usuário final vê
- o caminho mais simples exigir mexer em área marcada como frágil ou sensível
- surgir migração de dados destrutiva, mudança de schema em produção ou alteração de credencial
- a próxima ação gastar dinheiro além do teto aprovado na spec

## Ao terminar o último grupo

- `plan.md` reflete o que realmente foi feito
- As suítes das pastas tocadas passando, com o total e as puladas conferidos
- A revisão por fase, se o bloco a pede, feita sobre o diff da fase inteira
- Diga explicitamente o que **não** foi feito e por quê
- A CI (ou a prova local, se a CI não roda) não precisa rodar a cada grupo: a revisão lê o diff
  antes, e a prova roda uma vez no head final (ordem em `validar-fase`)
- Ofereça a skill `validar-fase` como próximo passo. Não faça merge por conta própria
