---
id: o-grep-do-git-for-windows-aborta-com-i-e-varios-e
data: 2026-11-13
area: processo
tipo: erro-de-diagnostico
custo: "cinco grep.exe.stackdump na fase 1, buscas refeitas por quatro subagentes e uma busca de lições perdida numa sessão de teste"
gatilho: "a implementar-fase passou a mandar buscar lições com grep -il, e uma sessão rodou grep -il -e python -e teste"
refs:
  - ".claude/skills/implementar-fase/SKILL.md:24-28 (a busca das lições)"
gatilhos:
  - '(?<!git )\bgrep\b[^|;&\n]*\s-e\s[^|;&\n]*\s-e\s'
  - 'stackdump'
---

**O que se achava:** que os `grep.exe.stackdump` da fase 1 vinham de buscas com acento no Git
Bash. Os subagentes passaram a evitar o acento, e a skill recomendou `grep -il <termo>`.

**O que é:** o GNU grep 3.0 do Git for Windows aborta ("Aborted (core dumped)", código 134, e um
`grep.exe.stackdump` na pasta) sempre que o `-i` vem com dois ou mais `-e`, com qualquer conteúdo.
Medido em 2026-11-13: `printf 'a\n' | grep -i -e a -e b` aborta, e o `LC_ALL=C` não muda nada. O
`grep -il python`, o `grep -l -e python -e teste` e o `grep -ilE 'python|teste'` funcionam.

**Como perceber da próxima vez:**
1. "Aborted (core dumped)" ou um `grep.exe.stackdump` novo depois de um `grep`: veja se ele tinha
   `-i` e dois `-e`. Junte os termos num só: `grep -iE 'a|b'`.
2. A saída de um `grep` que abortou não diz nada: "nenhum resultado" ali não é ausência.
3. O `git grep` não tem esse defeito; a ferramenta de busca do agente também não.
