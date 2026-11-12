---
id: o-windows-muda-o-que-o-sh-recebe-do-python
data: 2026-11-12
area: processo
tipo: armadilha
custo: "duas rodadas da fase 0: uma hipótese errada sobre aspas, desfeita, e um teste que passaria sem provar nada"
gatilho: "testes do gancho.sh que rodam o sh do Git Bash pelo subprocess do Python, no Windows"
refs:
  - ".claude/tests/test_gancho.py (_comando_do_lancador: o PROGRAMFILES posto de dentro do sh)"
  - ".claude/tests/test_codex.py (test_lancador_sem_o_proprio_caminho_acha_a_raiz_pelo_git: o texto passa ao sh -c por um sh)"
gatilhos:
  - '\bPROGRAMFILES\b'
  - '(^|/)\.claude/tests/test_(gancho|codex)\.py$'
---

**O que se achava:** que o `subprocess.run` do Python entrega ao `sh` do Git Bash exatamente o
ambiente (`env=`) e os argumentos dados. Os testes do lançador contavam com isso para trocar o
`PROGRAMFILES` e para passar o texto inteiro do `gancho.sh` ao `sh -c`.

**O que é:** no Windows, duas coisas mudam no caminho, sem erro nenhum:
1. O sistema reescreve o `PROGRAMFILES` de todo processo criado fora do `sh` do Git Bash (visto
   com o Python e o `cmd`). Com
   `env={..., "PROGRAMFILES": "C:\\x\\y"}`, o `sh` e o `cmd` viam `C:\Program Files`, e tirar a
   chave do `env` dava o mesmo. De dentro do `sh`, `PROGRAMFILES=/c/x/y sh -c 'echo $PROGRAMFILES'`
   imprime `/c/x/y`, e o `unset` também passa ao `sh` filho.
2. Um argumento de mais de uns 8 mil caracteres chega cortado ao `sh`. Com
   `['sh', '-c', '#' + 'x' * 8000 + '\necho FIM']`, saía `FIM`; com 8190, saía vazio, código 0. O
   `gancho.sh` passou de uns 8 mil caracteres na fase 0, e o teste quebrou com
   `line 180: e: command not found`: o `exit 0` do fim, cortado. De dentro do `sh`, um
   `sh -c "$(cat gancho.sh)"` com 20 mil caracteres passa inteiro.

**Como perceber da próxima vez:**
1. Um teste que troca o `PROGRAMFILES` pelo `env=` e "passa" no Windows não trocou nada: o `sh` vê
   o valor real. Troque-o num `sh` intermediário (`sh -c 'PROGRAMFILES="$2"; export PROGRAMFILES;
   exec sh "$1"'`).
2. Um `sh -c` que sai vazio ou com `<pedaço de palavra>: command not found` na última linha, só
   quando o texto vem de fora do `sh` (visto com o Python), é o argumento cortado. Não é aspa.
   Passe o texto por um `sh` (`sh -c 'exec sh -c "$(cat "$1")"' sh <arquivo>`) ou rode o arquivo
   direto.
