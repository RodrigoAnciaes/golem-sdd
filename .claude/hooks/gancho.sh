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
#        a. a linha `python = '<caminho>'` do `golem.local.toml` (fora do git) da raiz ou, se a
#           raiz não tiver a linha, da PASTA PRINCIPAL; quem a grava é a skill `diagnostico`;
#        b. o `.venv` da raiz;
#        c. o `.venv` da PASTA PRINCIPAL do repositório (o pai de `git rev-parse --git-common-dir`),
#           para quem trabalha em worktree;
#        d. `python3`, `python` e `py -3` do PATH (no Windows, o `python3` do PATH pode ser um
#           atalho da loja que não executa nada; o `py` é o lançador do instalador oficial);
#        e. os lugares do instalador oficial do Windows, que costumam ficar fora do PATH:
#           `$LOCALAPPDATA/Programs/Python/Python3*`, o `Launcher/py.exe` (com `-3`) e
#           `$PROGRAMFILES/Python3*` (lição sem-python-no-path-nao-e-maquina-sem-python);
#      o gancho só usa biblioteca padrão, então qualquer Python 3.8+ serve;
#   3. qualquer falha avisa os DOIS: o usuário pelo `systemMessage` e o agente pelo
#      `additionalContext`, mais uma linha em `.claude/gancho-falhas.log` (ponha no .gitignore).
#      Na falha "nenhum Python", o usuário é avisado uma vez por sessão e cada agente uma vez; sem
#      `session_id`, em toda ação (o porquê está lá embaixo). O log recebe a linha sempre.
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

# Quem recebe o aviso: `ao_usuario` (o `systemMessage`) e `ao_agente` (o `additionalContext`), 1
# ou 0. Só o caminho "nenhum Python" os muda, para avisar uma vez por sessão; o log sempre recebe.
ao_usuario=1
ao_agente=1

avisar() {
    # $1 (o motivo) e $2 (frases a mais, opcional, terminadas em ". ") vão dentro de uma string
    # JSON: só texto fixo, sem aspas nem barra invertida.
    printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$raiz" "$1" \
        >> "$raiz/.claude/gancho-falhas.log" 2>/dev/null
    [ "$ao_usuario" = 1 ] || [ "$ao_agente" = 1 ] || exit 0
    printf 'gancho das lições: %s (pasta: %s)\n' "$1" "$raiz" >&2
    separador=""
    printf '{'
    # `systemMessage` é o que chega ao USUÁRIO: com saída 0, o stderr só aparece no modo verbose.
    if [ "$ao_usuario" = 1 ]; then
        printf '"systemMessage":"⚠️ Gancho das lições falhou (%s). %sDetalhe em .claude/gancho-falhas.log."' "$1" "$2"
        separador=","
    fi
    if [ "$ao_agente" = 1 ]; then
        printf '%s"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"⚠️ O gancho das lições falhou (%s): nenhuma lição nem regra de área foi injetada nesta ação. Leia docs/licoes/ à mão (índice em .claude/indice/licoes.yaml) e avise o usuário. %sDetalhe em .claude/gancho-falhas.log."}' "$separador" "$1" "$2"
    fi
    printf '}\n'
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

achar_no_instalador() {
    # Um glob que não casa devolve o padrão literal: o `[ -f ]` o descarta.
    if [ -n "$LOCALAPPDATA" ]; then
        for candidato in "$LOCALAPPDATA"/Programs/Python/Python3*/python.exe; do
            if [ -f "$candidato" ] && roda_py38 "$candidato"; then
                py="$candidato"
                return 0
            fi
        done
        candidato="$LOCALAPPDATA/Programs/Python/Launcher/py.exe"
        if [ -f "$candidato" ] && roda_py38 "$candidato" -3; then
            py="$candidato"
            py_arg="-3"
            return 0
        fi
    fi
    if [ -n "$PROGRAMFILES" ]; then
        for candidato in "$PROGRAMFILES"/Python3*/python.exe; do
            if [ -f "$candidato" ] && roda_py38 "$candidato"; then
                py="$candidato"
                return 0
            fi
        done
    fi
    return 1
}

# A linha `python = '<caminho>'` de um golem.local.toml ($1), em `linha_python`. Vale a primeira
# linha que começa com `python` seguido de espaços opcionais e `=`; o valor vai da primeira aspa
# simples até a seguinte, e o resto da linha (um comentário) é ignorado. O `-r` guarda as barras
# invertidas do caminho do Windows. O `\r` de um arquivo em CRLF fica depois da segunda aspa e
# cai junto com o resto da linha.
linha_python=""
ler_linha_python() {
    [ -f "$1" ] || return 1
    while read -r linha || [ -n "$linha" ]; do
        case $linha in
            python*=*) ;;
            *) continue ;;
        esac
        meio=${linha#python}
        meio=${meio%%=*}
        case $meio in
            *[!' 	']*) continue ;;
        esac
        case $linha in
            *\'*\'*) ;;
            *) return 1 ;;
        esac
        linha_python=${linha#*\'}
        linha_python=${linha_python%%\'*}
        return 0
    done < "$1"
    return 1
}

# Limites conhecidos, todos terminando em AVISO, nunca em silêncio: repositório bare com worktrees
# ou `--separate-git-dir` (o common-dir não fica dentro da pasta principal); e git < 2.31, que não
# conhece `--path-format`. Nesses casos o PATH e o instalador ainda podem salvar.
principal=""
comum=$(git -C "$raiz" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
[ -z "$comum" ] || principal=$(dirname "$comum")

py=""
linha_quebrada=""
if ler_linha_python "$raiz/golem.local.toml" \
    || { [ -n "$principal" ] && ler_linha_python "$principal/golem.local.toml"; }; then
    if [ -f "$linha_python" ] && roda_py38 "$linha_python"; then
        py="$linha_python"
    else
        linha_quebrada="A linha python do golem.local.toml aponta para algo que não roda um Python 3.8+. "
    fi
fi
[ -n "$py" ] || py=$(achar_venv "$raiz")
if [ -z "$py" ] && [ -n "$principal" ]; then
    py=$(achar_venv "$principal")
fi
[ -n "$py" ] || achar_no_path
[ -n "$py" ] || achar_no_instalador

# Um id só vale com `[A-Za-z0-9_-]`, até 128 caracteres, como no `pasta_de_marca` do
# licoes_relevantes.py: ele vira nome de arquivo, e nada nele pode sair da pasta temporária.
id_valido() {
    case $1 in "" | *[!A-Za-z0-9_-]*) return 1 ;; esac
    [ ${#1} -le 128 ]
}

# O `session_id` e o `agent_id` da entrada do gancho (o JSON em `entrada`), em `sessao` e `agente`;
# vazios se faltarem ou não valerem. O JSON é partido nas aspas: uma chave é um pedaço seguido de
# outro que só tem `:` e espaços, e o valor vem logo depois. Dentro de um texto, as aspas vêm
# escapadas (`\"`), e o pedaço fica com a barra: não engana. Partir é linear; cortar a entrada com
# `${entrada#*\"agent_id\"}`, que testa cada prefixo, levava 4 s numa entrada de 80 KB. A primeira
# chave achada vence, mesmo aninhada: hoje nenhum `tool_input` dos matchers do settings.json tem
# uma chave `session_id` ou `agent_id`.
ids_da_entrada() {
    sessao=""
    agente=""
    set -f
    ifs_antes=$IFS
    IFS='"'
    set -- $entrada
    IFS=$ifs_antes
    set +f
    while [ $# -ge 3 ]; do
        case $2 in
            *[!' :']*) ;;
            *:*)
                case $1 in
                    session_id) [ -n "$sessao" ] || sessao=$3 ;;
                    agent_id) [ -n "$agente" ] || agente=$3 ;;
                esac
                ;;
        esac
        shift
    done
    id_valido "$sessao" || sessao=""
    id_valido "$agente" || agente=""
}

# Sai 0 se esta chamada criou a marca `$1`. O `set -C` faz o `>` falhar se ela já existe, de uma
# vez só: duas ferramentas em paralelo não criam a mesma marca. Se a marca não existe e não pôde
# ser criada (a pasta temporária sem escrita), conta como nova: o aviso sai em vez de calar.
marca_nova() {
    ( set -C; : > "$1" ) 2>/dev/null || [ ! -e "$1" ]
}

# Sem Python: o aviso sai uma vez por sessão. O `systemMessage` só pela conversa principal (um
# subagente pode ser o primeiro a falhar, e não se sabe se o aviso dele chega ao usuário); o
# `additionalContext` uma vez por agente, porque um subagente começa sem o contexto de quem o
# chamou. Sem `session_id` válido, avisa em toda ação. O stdin só é lido aqui, onde nenhum Python
# vai lê-lo, com o `read` embutido. Limite conhecido: a marca é por sessão, então um agente que
# compacta o contexto perde o aviso e não o recebe de novo.
if [ -z "$py" ]; then
    entrada=""
    while IFS= read -r pedaco || [ -n "$pedaco" ]; do
        entrada="$entrada$pedaco"
    done
    ids_da_entrada
    agente=${agente:-principal}
    if [ -n "$sessao" ]; then
        pasta_tmp=${TMPDIR:-${TEMP:-/tmp}}
        ao_usuario=0
        if [ "$agente" = principal ] && marca_nova "$pasta_tmp/golem-aviso.$sessao"; then
            ao_usuario=1
        fi
        ao_agente=0
        marca_nova "$pasta_tmp/golem-aviso.$sessao.$agente" && ao_agente=1
    fi
    avisar "nenhum Python 3.8+ encontrado: procurei na linha python do golem.local.toml, no .venv da pasta da sessão e no da principal, em python3, python e py -3 no PATH e nos lugares do instalador do Windows" \
        "${linha_quebrada}O Python pode existir fora desses lugares (lição sem-python-no-path-nao-e-maquina-sem-python). Peça o diagnóstico do Golem. "
fi

# O stdout do gancho só sai se ele terminar bem: JSON pela metade seguido do aviso quebraria o
# parse do harness. O stdin (o JSON da ferramenta) passa direto, e o stderr dele vai ao usuário.
# `$py_arg` sem aspas de propósito: vazio, some; `-3`, vira um argumento.
saida=$("$py" $py_arg "$aqui/licoes_relevantes.py")
codigo=$?
[ "$codigo" -eq 0 ] || avisar "licoes_relevantes.py saiu com código $codigo"
[ -z "$saida" ] || printf '%s\n' "$saida"
exit 0
