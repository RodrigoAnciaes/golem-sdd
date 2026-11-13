#!/bin/sh
# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
# Lançador do gancho das lições: acha um Python e roda licoes_relevantes.py.
#
# Por que existe: chamar `./.venv/bin/python ... 2>/dev/null || true` direto do settings.json é
# relativo à pasta da sessão. Um worktree não tem `.venv` (é ignorado pelo git, não viaja): o
# comando sai 127, o `|| true` esconde, e a sessão inteira trabalha sem lição sem ninguém saber.
#
# O que faz:
#   1. se localiza pelo próprio caminho: a raiz do projeto é `../..` daqui (nunca depende do cwd);
#   2. procura um Python, nesta ordem, e só aceita o candidato que RODA um Python 3.8+ de verdade
#      (senão passa ao próximo):
#        a. o `.venv` da raiz;
#        b. o `.venv` da PASTA PRINCIPAL do repositório (o pai de `git rev-parse --git-common-dir`),
#           para quem trabalha em worktree;
#        c. `python3`, `python` e `py -3` do PATH (no Windows, o `python3` do PATH pode ser um
#           atalho da loja que não executa nada; o `py` é o lançador do instalador oficial);
#      o gancho só usa biblioteca padrão, então qualquer Python 3.8+ serve;
#   3. qualquer falha avisa os DOIS: o usuário pelo `systemMessage` e o agente pelo
#      `additionalContext`, mais uma linha em `.claude/gancho-falhas.log` (ponha no .gitignore).
#      Sai sempre 0: o 2 é o código que bloqueia a ferramenta, e o 1 só chegaria ao usuário
#      (o agente seguiria sem lição e sem saber).
#
# ⚠️ Nada de junction/symlink de `.venv` dentro do worktree: um `git clean -x` pode atravessar o
# link e apagar o venv da pasta principal. A resolução é por caminho.
# ⚠️ Este arquivo tem de ter fim de linha LF. No `.gitattributes`: `*.sh text eol=lf`. Com CRLF o
# `sh` quebra antes de chegar aqui, e aí quem avisa é o `|| printf` do settings.json.

aqui=$(cd "$(dirname "$0")" && pwd)
raiz=$(cd "$aqui/../.." && pwd)
# Sem o próprio caminho (o lançador lido por `sh -c "$(cat …)"`, ou por um agente que não o
# chama pelo arquivo), a raiz vem do git, a partir da pasta corrente; vale para o Claude Code sem
# `CLAUDE_PROJECT_DIR` e para o Codex, que não tem essa variável.
if [ ! -f "$aqui/licoes_relevantes.py" ]; then
    topo=$(git rev-parse --show-toplevel 2>/dev/null)
    if [ -n "$topo" ] && [ -f "$topo/.claude/hooks/licoes_relevantes.py" ]; then
        raiz=$(cd "$topo" && pwd)
        aqui="$raiz/.claude/hooks"
    fi
fi

avisar() {
    # $1 vai dentro de uma string JSON: só texto fixo, sem aspas nem barra invertida.
    printf 'gancho das lições: %s (pasta: %s)\n' "$1" "$raiz" >&2
    printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$raiz" "$1" \
        >> "$raiz/.claude/gancho-falhas.log" 2>/dev/null
    # `systemMessage` é o que chega ao USUÁRIO: com saída 0, o stderr só aparece no modo verbose.
    printf '{"systemMessage":"⚠️ Gancho das lições falhou (%s). Detalhe em .claude/gancho-falhas.log.","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"⚠️ O gancho das lições falhou (%s): nenhuma lição nem regra de área foi injetada nesta ação. Leia docs/licoes/ à mão (índice em .claude/indice/licoes.yaml) e avise o usuário. Detalhe em .claude/gancho-falhas.log."}}\n' "$1" "$1"
    exit 0
}

[ -f "$aqui/licoes_relevantes.py" ] || avisar "não achei .claude/hooks/licoes_relevantes.py, nem pelo caminho do lançador, nem pelo git a partir da pasta corrente"

# Sai 0 se o comando ("$@") roda um Python 3.8+. Vale para o .venv e para o PATH: um venv
# quebrado (o Python de origem desinstalado) ou velho não pode vencer um Python bom do PATH.
roda_py38() {
    "$@" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1
}

achar_venv() {
    for candidato in "$1/.venv/Scripts/python.exe" "$1/.venv/bin/python"; do
        if [ -f "$candidato" ] && roda_py38 "$candidato"; then
            printf '%s\n' "$candidato"
            return 0
        fi
    done
    return 1
}

# `py_arg` guarda o argumento extra do candidato (o `-3` do `py`), separado do caminho: um caminho
# com espaço não pode ser partido em palavras.
py_arg=""

achar_no_path() {
    for nome in python3 python; do
        if command -v "$nome" >/dev/null 2>&1 && roda_py38 "$nome"; then
            py="$nome"
            return 0
        fi
    done
    if command -v py >/dev/null 2>&1 && roda_py38 py -3; then
        py="py"
        py_arg="-3"
        return 0
    fi
    return 1
}

py=$(achar_venv "$raiz")
# Limites conhecidos, todos terminando em AVISO, nunca em silêncio: repositório bare com worktrees
# ou `--separate-git-dir` (o common-dir não fica dentro da pasta principal); e git < 2.31, que não
# conhece `--path-format`. Nesses casos o PATH ainda pode salvar.
if [ -z "$py" ]; then
    comum=$(git -C "$raiz" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
    if [ -n "$comum" ]; then
        py=$(achar_venv "$(dirname "$comum")")
    fi
fi
[ -n "$py" ] || achar_no_path
[ -n "$py" ] || avisar "nenhum Python 3.8+ encontrado (nem .venv na pasta da sessão ou na principal, nem python3, python ou py -3 no PATH)"

# O stdout do gancho só sai se ele terminar bem: JSON pela metade seguido do aviso quebraria o
# parse do harness. O stdin (o JSON da ferramenta) passa direto, e o stderr dele vai ao usuário.
# `$py_arg` sem aspas de propósito: vazio, some; `-3`, vira um argumento.
saida=$("$py" $py_arg "$aqui/licoes_relevantes.py")
codigo=$?
[ "$codigo" -eq 0 ] || avisar "licoes_relevantes.py saiu com código $codigo"
[ -z "$saida" ] || printf '%s\n' "$saida"
exit 0
