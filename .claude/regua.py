# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""Régua das lições: gera o índice `.claude/indice/licoes.yaml` e confere que ele não envelheceu.

    python3 .claude/regua.py --gerar      # valida as lições e escreve o índice
    python3 .claude/regua.py --conferir   # sai != 0 se alguma lição for inválida ou o índice divergir

(No Windows, `python` ou `py -3` no lugar de `python3`.)

Princípio de desenho: **o índice filtra, o Markdown prova.** O YAML não contém a evidência: diz
onde ela está e em que ação a lição vale. A fonte é o frontmatter de `docs/licoes/*.md`; o índice
é derivado, e o `--conferir` (no CI, ou num gancho de pre-commit) é o que impede que ele vire um
gêmeo mantido à mão, que desencontra em silêncio.

Valida o frontmatter de cada lição:
- `id` presente, em `[a-z0-9-]`, e igual ao nome do arquivo (o gancho busca o sinal pelo id);
- `area` presente e em `AREAS_VALIDAS`;
- `tipo` presente e em `TIPOS_VALIDOS`;
- `gatilhos` (opcional) em lista de bloco, cada item uma expressão regular que compila e sem
  caractere de controle (entre aspas duplas, `\\b` vira backspace e a regex nunca casa).
E, se existir `docs/regras-de-area.md`, que todo `## Regra N` tenha a linha `areas:` e áreas válidas.

Avisa no stderr, sem mudar o código de saída (fase 4), no `--gerar` e no `--conferir`:
- a ref das lições (`refs:`) que começa por um caminho e não bate com ele: o arquivo que não
  existe, a linha que não existe ou a âncora (o primeiro trecho entre crases depois do caminho)
  que não está na linha citada. No plugin, o arquivo se procura também na pasta do kit, porque as
  lições do kit chegam ao jogo pela cópia e citam arquivos do kit. Na lição com `origem: kit`, o
  arquivo que não existe não avisa: a instalação por cópia não leva o que elas citam (o teste do
  kit confere sem essa folga, com `estrito`). A prosa e o `game.…` não se conferem;
- o `AGENTS.md` da raiz acima do teto de palavras: a linha `agents_teto` do `golem.toml`, lida
  pelo `golem.py`, com 3.000 por padrão;
- no modo plugin (fase 4b), a lição do jogo que divergiu da versão subida ao acervo geral do
  central: ela, ou a versão geral, mudou desde a subida (as impressões do `subidas.txt` do
  central, que o `golem.py subir` grava), ou a versão geral sumiu.

ONDE MUDAR O VOCABULÁRIO: `AREAS_VALIDAS` e `TIPOS_VALIDOS`, logo abaixo. Ao mudar uma área,
ajuste junto o `POR_CAMINHO` e o `POR_COMANDO` de `.claude/hooks/licoes_relevantes.py` (o teste
`test_areas_do_gancho_sao_validas` confere) e a lista do `docs/licoes/README.md`.

Só biblioteca padrão. O git é opcional: com ele, o índice só vê as lições que o git rastreia (o
índice descreve o repositório, não o disco), e a lição nova sem `git add` gera um aviso. Se há
lições em `docs/licoes/` e NENHUMA está no git, o `--gerar` recusa (sai 1, nada escrito): o índice
sairia com `total: 0` e o gancho calaria todas, sem erro nenhum.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]


def raiz_do_projeto(kit: Path = KIT) -> Path:
    """A posição, salvo no plugin (a pasta tem `.claude-plugin/plugin.json`): aí, o git da pasta
    corrente, ou a pasta corrente. A mesma regra do `golem.py` (fase 3, o Golem central)."""
    if not (kit / ".claude-plugin" / "plugin.json").is_file():
        return kit
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, encoding="utf-8", timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).resolve()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return Path.cwd().resolve()


# Os dados (as lições, o índice) vêm da raiz do projeto; o gancho, irmão deste script, da posição.
RAIZ = raiz_do_projeto()
LICOES = RAIZ / "docs" / "licoes"
INDICE = RAIZ / ".claude" / "indice"
GANCHO = KIT / ".claude" / "hooks" / "licoes_relevantes.py"
REGRAS_DE_AREA = RAIZ / "docs" / "regras-de-area.md"

# O vocabulário controlado. Valor novo só com motivo, e atualize o README das lições junto.
AREAS_VALIDAS = ("codigo", "deploy", "contrato", "processo")
TIPOS_VALIDOS = ("premissa-falsa", "armadilha", "erro-de-diagnostico", "custo-escondido")

# O teto de palavras do AGENTS.md quando o golem.py não se lê: o mesmo `AGENTS_TETO` dele (um
# teste confere). O teto de verdade é a linha `agents_teto` do golem.toml.
AGENTS_TETO_PADRAO = 3000


def ler(caminho: Path) -> str:
    if not caminho.is_file():
        return ""
    return caminho.read_text(encoding="utf-8", errors="ignore")


def campo(texto: str, nome: str) -> str:
    """Lido pela MESMA função do gancho, pelo mesmo motivo dos gatilhos (abaixo)."""
    return _gancho().campo(texto, nome)


# ---------------------------------------------------------------- o que o git rastreia

_RASTREADOS: set | None | bool = False   # False = ainda não consultado; None = sem git


def rastreados() -> set | None:
    """Os caminhos que o git rastreia (forma posix, relativos à raiz). None = sem git.

    O índice descreve o **repositório**, não o disco: sem este filtro ele inclui o trabalho não
    commitado que estiver na árvore, e o `--conferir` reprova num clone limpo. Sem git (pasta
    solta, ou o git ausente), não filtra nada: melhor indexar demais do que calar uma lição.
    """
    global _RASTREADOS
    if _RASTREADOS is False:
        try:
            r = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z"], cwd=RAIZ,
                               capture_output=True, timeout=60)
            if r.returncode == 0:
                nomes = r.stdout.decode("utf-8", errors="replace").split("\0")
                _RASTREADOS = {n for n in nomes if n}
            else:
                _RASTREADOS = None
        except Exception:
            _RASTREADOS = None
    return _RASTREADOS


def e_rastreado(caminho: Path) -> bool:
    conhecidos = rastreados()
    if conhecidos is None:
        return True                      # sem git: não filtra
    try:
        return caminho.resolve().relative_to(RAIZ.resolve()).as_posix() in conhecidos
    except Exception:
        return True


def arquivos_de_licao(todos: bool = False) -> list:
    """Os .md de docs/licoes/ que são lição: o README não é, e o não rastreado também não."""
    if not LICOES.is_dir():
        return []
    return [a for a in sorted(LICOES.glob("*.md"))
            if a.name != "README.md" and (todos or e_rastreado(a))]


def avisar_nao_rastreados() -> None:
    """Aviso no stderr, sem mudar o código de saída: a lição fora do git fica fora do índice."""
    if rastreados() is None:
        return
    vistos = set(arquivos_de_licao())
    for arq in arquivos_de_licao(todos=True):
        if arq not in vistos:
            print(f"  AVISO    docs/licoes/{arq.name} não está no git: o índice não a vê. "
                  f"Faça `git add` e rode --gerar de novo.", file=sys.stderr)


# ---------------------------------------------------------------- os gatilhos

_GANCHO = None


def carregar_gancho():
    """Importa o gancho: os gatilhos são lidos pela MESMA função que ele usa.

    Duas leituras do mesmo campo divergiriam um dia, e o índice e a degradação para o Markdown
    entregariam lições diferentes sem ninguém notar.
    """
    spec = importlib.util.spec_from_file_location("licoes_relevantes", GANCHO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _gancho():
    global _GANCHO
    if _GANCHO is None:
        _GANCHO = carregar_gancho()
    return _GANCHO


def gatilhos_de(texto: str) -> list:
    return _gancho().ler_gatilhos(texto)


def erros_de_gatilhos(nome: str, texto: str) -> list:
    """O que o gancho ignoraria em silêncio num `gatilhos:`; aqui vira erro com o motivo."""
    erros = []
    fm = re.match(r"---\s*\n(.*?)\n---", texto, re.S)
    # Comentário depois dos dois pontos é permitido (`gatilhos:   # opcional`).
    if fm and re.search(r"^gatilhos:[ \t]*[^\s#]", fm.group(1), re.M):
        erros.append(f"{nome}: `gatilhos:` na mesma linha. Use a lista em bloco, um "
                     f"`  - '<regex>'` por linha; o gancho não lê esta forma")
    for g in gatilhos_de(texto):
        if g is None:
            erros.append(f"{nome}: gatilho entre aspas que não se lê (aspas sem fechar, ou "
                         f"texto depois delas). Prefira aspas simples, onde nada é escape")
            continue
        controle = sorted({c for c in g if ord(c) < 32 or ord(c) == 127})
        if controle:
            codigos = ", ".join(f"\\x{ord(c):02x}" for c in controle)
            erros.append(f"{nome}: gatilho com caractere de controle ({codigos}). Entre aspas "
                         f"duplas `\\b` vira backspace; use aspas simples: - '\\bgit\\b'")
            continue
        try:
            re.compile(g, re.I)
        except re.error as e:
            erros.append(f"{nome}: gatilho '{g}' não é expressão regular válida ({e}). O "
                         f"gancho o ignora, e a lição sem gatilho válido volta a valer pela área")
    return erros


# ---------------------------------------------------------------- validação


def validar_licoes() -> list:
    """Erros que impedem uma lição de ser indexada ou entregue. Vazio = tudo bem."""
    erros = []
    for arq in arquivos_de_licao():
        texto = ler(arq)
        if not re.match(r"---\s*\n.*?\n---", texto, re.S):
            erros.append(f"{arq.name}: sem frontmatter (bloco `---` no começo do arquivo)")
            continue
        ident = campo(texto, "id")
        if not ident:
            erros.append(f"{arq.name}: sem campo `id:`")
        else:
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", ident):
                erros.append(f"{arq.name}: id {ident!r} fora de [a-z0-9-]. O gancho não o lê no "
                             f"índice, e os campos dele vazariam para a lição anterior")
            if ident != arq.stem:
                erros.append(f"{arq.name}: id {ident!r} diferente do nome do arquivo. O sinal "
                             f"'como perceber' é buscado pelo id, e a lição sairia sem sinal")
        area = campo(texto, "area")
        if not area:
            erros.append(f"{arq.name}: sem campo `area:`")
        elif area not in AREAS_VALIDAS:
            erros.append(f"{arq.name}: area {area!r} fora de {', '.join(AREAS_VALIDAS)} "
                         f"(o vocabulário mora em AREAS_VALIDAS, no .claude/regua.py)")
        tipo = campo(texto, "tipo")
        if not tipo:
            erros.append(f"{arq.name}: sem campo `tipo:`")
        elif tipo not in TIPOS_VALIDOS:
            erros.append(f"{arq.name}: tipo {tipo!r} fora de {', '.join(TIPOS_VALIDOS)} "
                         f"(o vocabulário mora em TIPOS_VALIDOS, no .claude/regua.py)")
        erros.extend(erros_de_gatilhos(arq.name, texto))
    return erros


def validar_regras_de_area() -> list:
    """Todo `## Regra N` de docs/regras-de-area.md é lido pelo gancho? Sem o arquivo, nada a ver.

    Uma regra sem a linha `areas:` ou com hífen comum no lugar do travessão existe no Markdown e
    não é entregue a ninguém. O gancho não pode acusar (não pode cair); quem acusa é a régua.
    """
    texto = ler(REGRAS_DE_AREA)
    if not texto:
        return []
    erros = []
    for bloco in re.split(r"\n(?=## Regra )", "\n" + texto):
        if not bloco.startswith("## Regra "):
            continue
        cabecalho = bloco.splitlines()[0]
        if not re.match(r"## Regra \d+\s+—\s+\S", cabecalho):
            erros.append(f"docs/regras-de-area.md: {cabecalho!r} fora do formato "
                         f"`## Regra N — Título` (travessão, U+2014). A regra não é entregue")
            continue
        ma = re.search(r"^areas:\s*(.+)$", bloco, re.M)
        if not ma:
            erros.append(f"docs/regras-de-area.md: {cabecalho!r} sem a linha `areas:` logo "
                         f"abaixo. A regra não é entregue")
            continue
        for a in (x.strip() for x in ma.group(1).split(",")):
            if a and a not in AREAS_VALIDAS:
                erros.append(f"docs/regras-de-area.md: {cabecalho!r} com area {a!r} fora de "
                             f"{', '.join(AREAS_VALIDAS)}")
    return erros


def validar_tudo() -> list:
    return validar_licoes() + validar_regras_de_area()


# ---------------------------------------------------------------- as refs e o teto (fase 4)

# O caminho com extensão no começo do item, com `:N` ou `:N-M`; o resto é descrição.
_REF = re.compile(r"([\w.-]+(?:/[\w.-]+)*\.[A-Za-z0-9]+)(?::(\d+)(?:-(\d+))?)?(?![\w/])")
_ANCORA = re.compile(r"`([^`]+)`")


def onde_procurar() -> list:
    """A raiz do projeto e, no plugin, a pasta do kit (as lições do kit citam arquivos dele)."""
    return [RAIZ] if KIT.resolve() == RAIZ.resolve() else [RAIZ, KIT]


def problema_da_ref(item, do_kit: bool = False) -> str | None:
    """O que não bate numa ref, ou None: em dia, ou um item que a régua não confere (prosa, um
    caminho `game.…` do place do Roblox, o item entre aspas que não se lê).

    `do_kit`: a lição veio do kit (`origem: kit`). Nela, o arquivo que não existe não é aviso: a
    instalação por cópia leva as lições do kit, e não os testes e as specs que elas citam (decisão
    do autor do kit, 2026-11-22). A linha que mudou continua avisando.
    """
    if not isinstance(item, str) or item.startswith("game."):
        return None
    m = _REF.match(item)
    if not m:
        return None
    caminho, inicio, fim = m.group(1), m.group(2), m.group(3)
    arq = next((p / caminho for p in onde_procurar() if (p / caminho).is_file()), None)
    if arq is None:
        return None if do_kit else "o arquivo não existe"
    ma = _ANCORA.search(item, m.end())
    ancora = ma.group(1) if ma else None
    linhas = ler(arq).splitlines()
    if inicio is None:
        if ancora is not None and not any(ancora in l for l in linhas):
            return f"a âncora `{ancora}` não está no arquivo"
        return None
    n, k = int(inicio), int(fim or inicio)
    if ancora is None:
        if n > len(linhas):
            return f"a linha {n} não existe (o arquivo tem {len(linhas)})"
        return ("linha sem âncora: a régua não confere o que ela cita. Ponha entre crases, depois "
                "do caminho, um trecho da linha")
    if any(ancora in l for l in linhas[n - 1:k]):
        return None
    achadas = [i for i, l in enumerate(linhas, 1) if ancora in l]
    if not achadas:
        return f"a âncora `{ancora}` não está no arquivo"
    depois = [i for i in achadas if i > k]
    return f"a âncora `{ancora}` está agora na :{(depois or achadas)[0]}"


def problemas_de_refs(estrito: bool = False) -> list:
    """Uma linha por ref que não bate, com o id da lição. Vazio = as refs em dia.

    `estrito`: o arquivo ausente é aviso também na lição do kit (o teste do kit usa).
    """
    fora = []
    for arq in arquivos_de_licao():
        texto = ler(arq)
        do_kit = not estrito and campo(texto, "origem") == "kit"
        for item in _gancho().ler_gatilhos(texto, "refs"):
            if item is None:
                fora.append(f"{arq.stem}: uma ref entre aspas que não se lê (aspas sem fechar, ou "
                            f"a aspa simples de dentro sem dobrar): a régua não a confere")
                continue
            problema = problema_da_ref(item, do_kit)
            if problema:
                fora.append(f"{arq.stem}: a ref {_REF.match(item).group(0)}: {problema}")
    return fora


def _carregar_golem():
    """O `golem.py` do kit, ou None se ele falta ou não carrega."""
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("golem", KIT / ".claude" / "golem.py")
        golem = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(golem)
        return golem
    except (OSError, ImportError, SyntaxError):
        return None


def teto_do_agents() -> int:
    """A linha `agents_teto` do golem.toml (no plugin, com o central por baixo), pelo golem.py.
    Sem ele, ou com o golem.toml com erro, o padrão: quem acusa o erro é o `aplicar`."""
    teto = getattr(_carregar_golem(), "teto_do_agents", None)
    if teto is None:
        return AGENTS_TETO_PADRAO        # o golem.py falta ou não carrega
    return teto(RAIZ)


def avisos_de_divergencia() -> list:
    """As lições deste jogo que divergiram da versão subida ao acervo geral (fase 4b): no modo
    plugin, a lição cujo id está no `subidas.txt` do central e cuja impressão, ou a da versão
    geral, não é a gravada na subida (ou a versão geral sumiu). Vazio fora do modo plugin, na
    sessão aberta no próprio central e sem o `subidas.txt`."""
    if not (KIT / ".claude-plugin" / "plugin.json").is_file():
        return []                         # o kit e a cópia: nem carrega o golem.py
    golem = _carregar_golem()
    if golem is None or not golem.modo_plugin(RAIZ):
        return []
    central = golem.central()
    if golem._mesma_pasta(RAIZ, central):
        return []                         # ali, as lições são as versões gerais
    subidas = golem.ler_subidas(RAIZ)
    fora = []
    for arq in arquivos_de_licao(todos=True):
        if arq.stem not in subidas:
            continue
        do_jogo, do_geral = subidas[arq.stem]
        geral = central / "docs" / "licoes" / arq.name
        if golem.impressao(arq) != do_jogo:
            motivo = "a lição deste jogo mudou"
        elif not geral.is_file():
            motivo = "a versão geral sumiu"
        elif golem.impressao(geral) != do_geral:
            motivo = "a versão geral mudou (à mão, ou subida de novo por outro jogo)"
        else:
            continue
        saida = ("suba de novo uma versão geral dela (a skill `licao` faz isso)"
                 if motivo == "a versão geral sumiu" else
                 "confira a versão geral e suba de novo com `golem.py subir <a versão geral> "
                 "--substituir` (a skill `licao` faz isso)")
        fora.append(f"{arq.stem}: {motivo} desde a subida ao acervo geral (docs/licoes/{arq.name} "
                    f"e {geral.as_posix()}). Para pôr em dia, {saida}: a subida renova a "
                    f"conferência")
    return fora


def aviso_do_teto() -> str | None:
    """O aviso do AGENTS.md da raiz acima do teto, ou None (abaixo dele, ou sem o arquivo)."""
    arq = RAIZ / "AGENTS.md"
    if not arq.is_file():
        return None
    palavras = len(ler(arq).split())
    teto = teto_do_agents()
    if palavras <= teto:
        return None
    return (f"AGENTS.md tem {palavras} palavras, acima do teto de {teto}. Ele entra inteiro em "
            f"toda conversa: a regra que só vale para quem mexe numa área vai ao "
            f"docs/regras-de-area.md (a regra 7 e a skill `licao`). O teto é a linha "
            f"`agents_teto` do golem.toml.")


def avisar_refs_e_teto() -> None:
    """Avisos no stderr, sem mudar o código de saída: uma ref velha nunca impede o índice."""
    for problema in problemas_de_refs():
        print(f"  AVISO    {problema}", file=sys.stderr)
    aviso = aviso_do_teto()
    if aviso:
        print(f"  AVISO    {aviso}", file=sys.stderr)
    for divergencia in avisos_de_divergencia():
        print(f"  AVISO    {divergencia}", file=sys.stderr)


# ---------------------------------------------------------------- gerar / conferir


def gerar_licoes() -> str:
    """`licoes.yaml` a partir do frontmatter: o Markdown é a fonte, isto é derivado.

    Guarda o id, a área, o tipo, a data, o gatilho (a circunstância, em prosa), os `gatilhos`
    (quando há) e o caminho. NÃO guarda o corpo: a evidência fica no Markdown.
    """
    arquivos = arquivos_de_licao()
    linhas = [
        "# GERADO por .claude/regua.py --gerar. NÃO EDITE À MÃO.",
        "# A fonte é o frontmatter de docs/licoes/*.md. `--conferir` falha se divergirem.",
        "licoes:",
    ]
    for arq in arquivos:
        texto = ler(arq)
        ident = campo(texto, "id") or arq.stem
        linhas.append(f"  {ident}:")
        for nome in ("area", "tipo", "data", "gatilho"):
            linhas.append(f"    {nome}: {json.dumps(campo(texto, nome), ensure_ascii=False)}")
        # `gatilhos` (a lista de regex que o gancho testa) só aparece em quem tem: JSON numa
        # linha, que o leitor próprio do gancho lê sem PyYAML.
        gatilhos = gatilhos_de(texto)
        if gatilhos:
            linhas.append(f"    gatilhos: {json.dumps(gatilhos, ensure_ascii=False)}")
        linhas.append(f"    arquivo: docs/licoes/{arq.name}")
    # O gancho confere este número: se as entradas lidas não baterem, o índice está cortado e ele
    # degrada para o Markdown, com aviso.
    linhas.append(f"total: {len(arquivos)}")
    return "\n".join(linhas) + "\n"


GERADORES = {
    "licoes.yaml": gerar_licoes,
}


def nenhuma_rastreada() -> bool:
    """Há lições no disco e o git não rastreia nenhuma: o índice sairia com `total: 0`.

    É o caso da instalação nova (o kit copiado e o `--gerar` antes do `git add`) e da pasta de
    lições recém-criada. Um índice vazio não é erro de formato, e o gancho o leria como "não há
    lição": o silêncio que a régua existe para impedir.
    """
    if rastreados() is None:
        return False                     # sem git: não filtra, o índice vê o disco
    return bool(arquivos_de_licao(todos=True)) and not arquivos_de_licao()


def comando_gerar() -> int:
    erros = validar_tudo()
    if erros:
        print("  RECUSADO: entrada que o gerador não consegue ler:")
        for e in erros:
            print(f"    - {e}")
        print("  Nada foi escrito. Corrija o Markdown e rode de novo.")
        return 1
    if nenhuma_rastreada():
        n = len(arquivos_de_licao(todos=True))
        print(f"  RECUSADO: há {n} lição(ões) em docs/licoes/ e nenhuma está no git: o índice "
              f"sairia com `total: 0` e o gancho não entregaria nenhuma.\n"
              f"  Faça `git add docs/licoes` (ou `git add .claude docs ...`, como no README) e "
              f"rode --gerar de novo. Nada foi escrito.", file=sys.stderr)
        return 1
    INDICE.mkdir(parents=True, exist_ok=True)
    for nome, gerador in GERADORES.items():
        (INDICE / nome).write_text(gerador(), encoding="utf-8", newline="\n")
        print(f"  escrito  .claude/indice/{nome}")
    avisar_nao_rastreados()
    avisar_refs_e_teto()
    return 0


def comando_conferir() -> int:
    """Regenera em memória e compara com o disco.

    Confere **antes** se o Markdown é legível: sem isso, uma entrada malformada some dos dois
    lados da comparação (derivado contra derivado) e o `--conferir` diz "ok".
    """
    problema = False
    for e in validar_tudo():
        print(f"  INVÁLIDO {e}")
        problema = True
    for nome, gerador in GERADORES.items():
        alvo = INDICE / nome
        if not alvo.is_file():
            print(f"  FALTA    .claude/indice/{nome}: rode --gerar")
            problema = True
        elif ler(alvo).replace("\r\n", "\n") != gerador():
            print(f"  DIVERGE  .claude/indice/{nome}: o Markdown mudou e o índice não; rode --gerar")
            problema = True
        else:
            print(f"  ok       .claude/indice/{nome}")
    avisar_nao_rastreados()
    avisar_indice_fora_do_stage()
    avisar_refs_e_teto()
    return 1 if problema else 0


def avisar_indice_fora_do_stage() -> None:
    """Aviso no stderr, sem mudar o código de saída: o índice da árvore difere do que está no stage.

    O `--gerar` reescreve o índice, mas não o põe no stage; o commit da lição sairia com o índice
    velho, e quem clonar receberia a lição sem a entrega.
    """
    if rastreados() is None:
        return
    for nome in GERADORES:
        rel = f".claude/indice/{nome}"
        if not (INDICE / nome).is_file():
            continue
        try:
            r = subprocess.run(["git", "show", f":{rel}"], cwd=RAIZ, capture_output=True,
                               timeout=60)
        except Exception:
            continue
        if r.returncode != 0:
            print(f"  AVISO    {rel} não está no git: faça `git add {rel}`.", file=sys.stderr)
        elif r.stdout.replace(b"\r\n", b"\n") != (INDICE / nome).read_bytes().replace(b"\r\n", b"\n"):
            print(f"  AVISO    {rel} difere do que está no stage do git: faça `git add {rel}` "
                  f"antes do commit.", file=sys.stderr)


USO = """uso: python3 .claude/regua.py --gerar | --conferir

  --gerar     valida as lições e escreve .claude/indice/licoes.yaml
  --conferir  sai != 0 se alguma lição for inválida ou o índice divergir do Markdown
"""


def main(args=None) -> int:
    args = sys.argv[1:] if args is None else args
    if args == ["--gerar"]:
        return comando_gerar()
    if args == ["--conferir"]:
        return comando_conferir()
    print(USO)
    return 2


if __name__ == "__main__":
    sys.exit(main())
