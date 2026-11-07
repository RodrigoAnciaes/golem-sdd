---
id: conferir-e-agir-em-chamadas-separadas
data: 2026-11-06
area: processo
tipo: armadilha
custo: "uma ação irreversível (merge, push, deploy) feita sobre um estado que a conferência, lida depois, mostrava ser outro"
gatilho: "conferência e ação na mesma chamada de ferramenta (encadeadas com && ou ;) ou em chamadas paralelas da mesma mensagem"
gatilhos:
  - '\bgh\s+pr\s+merge\b'
  - '\bgit\s+(push|merge)\b'
  - '\bgit\s+ls-remote\b.*(&&|;)'
refs:
  - "agentes (Claude Code, Codex): as chamadas de ferramenta da mesma resposta podem rodar em paralelo; nenhuma vê a saída da outra"
  - "shell: em `a && b`, o b só deixa de rodar se o a sair com código diferente de zero"
---

**O que se achava:** que pôr a conferência antes da ação no mesmo comando (`git ls-remote ... &&
gh pr merge ...`), ou na mesma leva de chamadas, protege a ação.

**O que é:** a conferência só protege se alguém **lê o resultado e decide** antes de agir. Num
`conferir && agir`, o `&&` só para quando a conferência sai com erro; um comando que apenas imprime
um estado (um sha, uma lista, um status) sai com zero, e a ação roda qualquer que seja o valor
impresso. Em chamadas paralelas é pior: as duas partem juntas, e a saída da conferência chega
quando a ação já foi feita. Nos dois casos a conferência vira enfeite no registro.

**Como perceber da próxima vez:**
1. Antes de uma ação irreversível, olhe a sua própria chamada: se a conferência e a ação estão no
   mesmo comando, ou na mesma mensagem, a conferência não decide nada.
2. Faça em dois passos: uma chamada que confere, a leitura da saída, a comparação com o esperado,
   e só então outra chamada que age.
3. Quando a ferramenta oferece trava, use-a no lugar do encadeamento: `gh pr merge
   --match-head-commit <sha>`, `git push --force-with-lease=<ref>:<sha>`. A trava falha sozinha se
   o estado mudou entre a conferência e a ação.
