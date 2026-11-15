# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""Injeta as lições relevantes de docs/licoes/ antes de editar arquivo ou rodar comando.

É um gancho PreToolUse do agente (Claude Code ou Codex). Lê o JSON da ferramenta no stdin, decide
a área pelo caminho do arquivo ou pelo comando, testa os `gatilhos:` de cada lição contra a ação,
e devolve em `additionalContext` o id e a seção "Como perceber da próxima vez" das lições
escolhidas.

As entradas que ele entende:
- Claude Code: `tool_input.file_path` (Edit, Write) ou `tool_input.command` (Bash, PowerShell);
- Codex: `tool_name: "Bash"` com `tool_input.command`, como acima; e `tool_name: "apply_patch"`,
  em que `tool_input.command` é o texto do patch: valem só os caminhos do cabeçalho
  (`caminhos_do_patch`), nunca o corpo.

Por que existe: registrar uma armadilha não adianta se nada força a leitura no momento certo.
O agente não relê o acervo antes de cada ação; o gancho entrega o que interessa àquela ação.

Como escolhe:

1. **Lição com `gatilhos:` só é candidata quando um deles casa com a ação**, qualquer que seja
   a área. Cada gatilho é uma expressão regular (sem diferenciar maiúsculas) testada contra o
   caminho do arquivo (absoluto, com `/`) e contra o comando, cru e depois de `sem_texto()`.
   O que vai entre aspas conta para o gatilho, mas não para a área.
2. **Lição sem `gatilhos:` vale pela área** (`POR_CAMINHO` e `POR_COMANDO`, abaixo).
3. A que casou por gatilho vem antes das que vieram só pela área, dentro do mesmo teto.
4. **Cada lição entra uma vez por agente, por sessão.** Sem isso, a mesma lista se repete a
   cada ação da mesma área, e o agente para de ler. O teto (`teto_do_gancho`) vale sobre o que
   é NOVO: a ação seguinte na mesma área entrega as próximas, até esgotar.
5. O sinal sai **inteiro**. Truncar entrega meia verdade, e o agente completa de memória.

Regras de área (opcional): se existir `docs/regras-de-area.md`, cada bloco
`## Regra N — Título` seguido de uma linha `areas: a, b` é entregue, inteiro e sem teto, a quem
toca uma daquelas áreas, também uma vez por sessão. Sem o arquivo, nada muda.

Degradação, sempre para injetar e nunca para o silêncio:
- índice ilegível ou cortado → varre o Markdown de `docs/licoes/` (com aviso no texto);
- marca da sessão ilegível → injeta sem deduplicar;
- regex de gatilho inválida → é ignorada; se nenhuma da lição presta, ela volta a valer pela
  área. Quem acusa a regex inválida é a régua (`regua.py --gerar` recusa, `--conferir` falha).

Só biblioteca padrão, de propósito: uma dependência a mais é um jeito novo de o gancho morrer
num clone recém-feito.

Para adaptar ao seu projeto: edite `POR_CAMINHO` e `POR_COMANDO`. As áreas usadas aqui têm de
estar em `AREAS_VALIDAS` do `.claude/regua.py` (há um teste que confere).
"""
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LICOES = RAIZ / "docs" / "licoes"
INDICE = RAIZ / ".claude" / "indice" / "licoes.yaml"
REGRAS_DE_AREA = RAIZ / "docs" / "regras-de-area.md"


def teto_do_gancho() -> int:
    """Quantas lições NOVAS por injeção: acima disso vira ruído e ninguém lê.

    Vem do `golem.toml` da raiz (a linha `gancho_teto`, ou o da receita), pelo `.claude/golem.py`.
    Sem `golem.toml`, ou com ele com erro, o da receita padrão. Sem o `golem.py` (a `.claude/` não
    foi copiada inteira), o script falha, e o `gancho.sh` avisa.
    """
    sys.dont_write_bytecode = True  # nada de .claude/__pycache__/ no projeto a cada ação
    spec = importlib.util.spec_from_file_location("golem", RAIZ / ".claude" / "golem.py")
    golem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(golem)
    return golem.teto_do_gancho(RAIZ)

# Caminho do arquivo -> área (o caminho, com `/`, CONTÉM o trecho). Exemplos: ajuste ao seu
# projeto. A ordem não importa; um caminho pode acender mais de uma área.
POR_CAMINHO = [
    ("src/", "codigo"),
    ("lib/", "codigo"),
    ("tests/", "codigo"),
    ("deploy/", "deploy"),
    ("Dockerfile", "deploy"),
    ("docker-compose", "deploy"),
    ("infra/", "deploy"),
    ("docs/contratos/", "contrato"),
    ("openapi", "contrato"),
    (".github/", "processo"),
    ("specs/", "processo"),
    ("AGENTS.md", "processo"),
    ("CLAUDE.md", "processo"),
]

# Comando -> áreas. O comando é testado SEM o texto entre aspas e sem corpo de heredoc
# (`sem_texto`): a área sai do que o comando FAZ, não do que ele cita.
POR_COMANDO = [
    (r"\bdocker\b|\bcompose\b|\bkubectl\b|\bhelm\b|\bterraform\b|\bssh\b|\bscp\b", ["deploy"]),
    (r"\bgit\s+(push|merge|rebase|reset|checkout)\b", ["processo"]),
    (r"\bpytest\b|\bpython\b.*-m\s+pytest|\bnpm\s+(run\s+)?test\b", ["processo"]),
    (r"\bcurl\b|\bhttpie\b|\bhttp\s+(get|post|put|patch|delete)\b", ["contrato"]),
]


def campo(texto: str, nome: str) -> str:
    """O valor de um campo de uma linha do frontmatter ('' se não há).

    Como no YAML: entre aspas, vale o que está dentro delas; sem aspas, ` #` em diante é
    comentário. O modelo do README traz `area: codigo   # codigo | deploy | ...`, e sem o corte
    a área lida seria a linha inteira, que não casa com área nenhuma.
    """
    fm = re.match(r"---\s*\n(.*?)\n---", texto, re.S)
    m = re.search(rf"^{nome}:[ \t]*(.*)$", fm.group(1) if fm else texto, re.M)
    if not m:
        return ""
    valor = m.group(1).strip()
    mq = re.match(r'"((?:[^"\\]|\\.)*)"|\'((?:[^\']|\'\')*)\'', valor)
    if mq:
        return mq.group(1) if mq.group(1) is not None else mq.group(2).replace("''", "'")
    return re.split(r"\s+#", valor, maxsplit=1)[0].strip()


def como_perceber(texto: str) -> str:
    """A seção que vale (o sinal observável), INTEIRA.

    Aceita "próxima" e "proxima". Vai até o fim da seção, não até a primeira linha em branco:
    parar no primeiro parágrafo entregava uma fração do sinal sem nenhum `...` para avisar.
    O limite é o próximo rótulo em negrito terminado em dois pontos no começo de linha, um `---`,
    ou o fim do arquivo. Por isso, depois do "Como perceber", atualizações levam rótulo terminado
    em ponto (`**Atualização de AAAA-MM-DD.**`), senão não chegam.
    """
    m = re.search(
        r"\*\*Como perceber da pr[oó]xima vez:\*\*\s*(.*?)"
        r"(?=\n\*\*[A-ZÀ-Úa-z][^:*\n]*:\*\*|\n---\s*\n|\Z)",
        texto, re.S,
    )
    if not m:
        return ""
    # Preserva as quebras: o sinal costuma ser lista numerada, e achatar destrói a estrutura.
    linhas = [l.rstrip() for l in m.group(1).strip().splitlines()]
    return "\n".join(linhas).strip()


def ler_gatilhos(texto: str) -> list:
    """Os itens de `gatilhos:` no frontmatter, como texto. [] = a lição não tem o campo.

    Só a lista em bloco, um item por linha (`  - '\\bgit\\s+push\\b'`). Aspas simples são o jeito
    recomendado (nada é escape lá dentro); aspas duplas seguem os escapes de JSON, que para regex
    são os do YAML; sem aspas, o item vale como está. Como no YAML, ` #` em diante é comentário,
    na linha do campo e na do item (fora das aspas). A régua lê com esta mesma função, então o
    índice e o Markdown não divergem. Item entre aspas malformado sai como `None`: o gancho o
    ignora e a régua o acusa.
    """
    m = re.match(r"---\s*\n(.*?)\n---", texto, re.S)
    if not m:
        return []
    linhas = m.group(1).splitlines()
    inicio = next((i for i, l in enumerate(linhas) if re.match(r"gatilhos:\s*(#.*)?$", l)), None)
    if inicio is None:
        return []
    itens = []
    for linha in linhas[inicio + 1:]:
        mi = re.match(r"\s*-\s+(.*?)\s*$", linha)
        if not mi:
            if linha.strip().startswith("#"):
                continue
            break
        item = mi.group(1)
        if item.startswith("'"):
            mq = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", item)
            itens.append(mq.group(1).replace("''", "'") if mq else None)
        elif item.startswith('"'):
            mq = re.fullmatch(r'("(?:[^"\\]|\\.)*")\s*(?:#.*)?', item)
            try:
                itens.append(json.loads(mq.group(1)) if mq else None)
            except ValueError:
                itens.append(None)
        else:
            # Sem o corte, `\bpush\b  # comentário` virava uma regex que nunca casa: lição muda.
            itens.append(re.split(r"\s+#", item, maxsplit=1)[0])
    return itens


def compilar(gatilhos) -> list:
    """As expressões que compilam. A inválida fica de fora: não pode derrubar o gancho."""
    fora = []
    for g in gatilhos or []:
        try:
            fora.append(re.compile(g, re.I))
        except (re.error, TypeError):
            pass
    return fora


# ------------------------------------------------------------------ o acervo


def do_indice():
    """Lê `.claude/indice/licoes.yaml`. Devolve [(id, area, tipo, gatilhos)] ou None se não der.

    Leitor próprio do formato que a régua escreve, de propósito: depender de PyYAML aqui faria
    o gancho morrer num ambiente sem ele. `gatilhos` vem em JSON numa linha só; JSON que não lê
    é índice ilegível, e o gancho cai no Markdown.

    Devolve None também quando o índice está **truncado**: ele declara `total: N` no fim, e se o
    número de entradas lidas não bater, o arquivo está pela metade. Sem essa conferência, um
    índice cortado seria servido como completo, e as lições do pedaço perdido sumiriam caladas.
    """
    try:
        if not INDICE.is_file():
            return None
        achadas, ident, dados, lidas, total = [], None, {}, 0, None

        def fechar():
            if ident:
                gatilhos = json.loads(dados["gatilhos"]) if "gatilhos" in dados else []
                if not isinstance(gatilhos, list):
                    raise ValueError("gatilhos fora de lista")
                achadas.append((ident, dados.get("area", ""), dados.get("tipo", ""), gatilhos))

        for linha in INDICE.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^total:\s*(\d+)\s*$", linha)
            if m:
                total = int(m.group(1))
                continue
            if linha.startswith("#") or not linha.strip() or linha.startswith("licoes:"):
                continue
            m = re.match(r"^  ([a-z0-9][a-z0-9-]*):\s*$", linha)
            if m:
                fechar()
                ident, dados = m.group(1), {}
                lidas += 1
                continue
            m = re.match(r"^    gatilhos:\s*(.*?)\s*$", linha)
            if m and ident:
                dados["gatilhos"] = m.group(1)
                continue
            m = re.match(r'^    (\w+):\s*"?(.*?)"?\s*$', linha)
            if m and ident:
                dados[m.group(1)] = m.group(2)
        fechar()
        if total is None or lidas != total:
            return None                  # ilegível, ou cortado: não confie
        return achadas
    except Exception:
        return None


def do_markdown():
    """Varredura do acervo: usada só quando o índice não presta."""
    achadas = []
    if not LICOES.is_dir():
        return achadas
    for arq in sorted(LICOES.glob("*.md")):
        if arq.name == "README.md":
            continue
        texto = arq.read_text(encoding="utf-8", errors="ignore")
        achadas.append((campo(texto, "id") or arq.stem, campo(texto, "area"),
                        campo(texto, "tipo"), ler_gatilhos(texto)))
    return achadas


def candidatas(areas, alvos):
    """Devolve (lições, degradou). `degradou` = o índice não prestou e a lista veio do Markdown.

    `alvos` = o caminho e o comando da ação, os textos contra os quais os gatilhos são testados.
    Lição com gatilho que presta só entra se um deles casar, e entra na frente; lição sem gatilho
    (ou só com gatilho inválido) entra pela área.
    """
    acervo = do_indice()
    degradou = acervo is None
    if degradou:
        acervo = do_markdown()
    por_gatilho, por_area = [], []
    for ident, area, tipo, gatilhos in acervo:
        expressoes = compilar(gatilhos)
        if expressoes:
            if any(rx.search(alvo) for rx in expressoes for alvo in alvos):
                por_gatilho.append((ident, area, tipo))
        elif area in areas:
            por_area.append((ident, area, tipo))
    return por_gatilho + por_area, degradou


def regras_para(areas):
    """As regras de área que valem para estas áreas, com o texto INTEIRO. [] sem o arquivo.

    Formato de `docs/regras-de-area.md`: um bloco por regra, `## Regra N — Título` (travessão,
    U+2014), a linha `areas: a, b` logo abaixo, e o corpo até o próximo `## Regra` ou um `---`.
    Regra de área serve para o que só muda a decisão de quem mexe naquela área; o que vale para
    toda tarefa fica no AGENTS.md.
    """
    try:
        texto = REGRAS_DE_AREA.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    fora = []
    for bloco in re.split(r"\n(?=## Regra )", texto):
        m = re.match(r"## Regra (\d+)\s+—\s+(.+)", bloco)
        if not m:
            continue
        ma = re.search(r"^areas:\s*(.+)$", bloco, re.M)
        if not ma:
            continue
        das = {a.strip() for a in ma.group(1).split(",") if a.strip()}
        if not (das & areas):
            continue
        corpo = bloco[ma.end():].strip()
        corpo = re.split(r"\n---\s*$", corpo, maxsplit=1, flags=re.M)[0].strip()
        fora.append((int(m.group(1)), m.group(2).strip(), corpo))
    return fora


def sinal_de(ident: str) -> str:
    """Abre o Markdown de UMA lição: a evidência mora lá, não no índice."""
    arq = LICOES / f"{ident}.md"
    if not arq.is_file():
        return ""
    return como_perceber(arq.read_text(encoding="utf-8", errors="ignore"))


# ------------------------------------------------------------------ a marca da sessão


def pasta_de_marca(dados: dict):
    """A pasta onde cada lição entregue NESTA sessão, a ESTE agente, vira um arquivo vazio.

    **Um arquivo por lição, criado com `O_CREAT | O_EXCL`.** O Claude Code dispara ferramentas
    em paralelo; com um arquivo único (ler, decidir, acrescentar), duas invocações simultâneas
    liam a mesma marca e entregavam as mesmas lições. A criação exclusiva é atômica: só uma
    invocação vence, e só ela entrega.

    **Uma marca por agente.** Um subagente recebe o mesmo `session_id` e o mesmo
    `scratchpad_dir` da conversa que o criou; o que muda é o `agent_id` (ausente na conversa
    principal). Com a marca por sessão, o subagente, que começa com o contexto zerado, herdaria
    a marca e não receberia lição nenhuma que a principal já tivesse recebido.

    Preferência pelo `scratchpad_dir` do stdin (é por sessão e o harness o limpa). Sem ele, cai
    no `session_id` sob o temp do sistema, com limpeza das marcas de mais de 7 dias. Sem os dois,
    ou se a pasta não puder ser criada, devolve None e o gancho injeta sem deduplicar.

    Limite conhecido: depois de uma compactação de contexto, nada no stdin avisa que o agente
    esqueceu; as lições já marcadas não voltam.
    """
    agente = str(dados.get("agent_id") or "principal")
    if not re.fullmatch(r"[\w-]{1,128}", agente):
        agente = "principal"
    scratch = dados.get("scratchpad_dir")
    if scratch:
        try:
            p = Path(scratch) / "licoes-entregues" / agente
            p.mkdir(parents=True, exist_ok=True)
            return p
        except Exception:
            pass
    sessao = dados.get("session_id")
    if sessao and re.fullmatch(r"[\w-]{1,128}", str(sessao)):
        try:
            temp = Path(tempfile.gettempdir())
            limite = time.time() - 7 * 86400
            for velha in temp.glob("claude-licoes-*"):
                try:
                    if velha.stat().st_mtime < limite and velha.is_dir():
                        shutil.rmtree(velha, ignore_errors=True)
                except Exception:
                    pass
            p = temp / f"claude-licoes-{sessao}" / agente
            p.mkdir(parents=True, exist_ok=True)
            return p
        except Exception:
            pass
    return None


def ja_entregues(pasta) -> set:
    """Pré-filtro barato: os ids que já têm arquivo. A palavra final é de `reivindicar`."""
    if pasta is None:
        return set()
    try:
        return {p.name for p in pasta.iterdir()}
    except Exception:
        return set()                     # marca ilegível: trata como vazia, e injeta


def reivindicar(pasta, ident: str) -> bool:
    """True = esta invocação é a dona da entrega. Atômico: só uma invocação vence.

    Qualquer falha que não seja "outra invocação já pegou" devolve True: degrada para injetar,
    nunca para silenciar.
    """
    if pasta is None:
        return True
    try:
        fd = os.open(str(pasta / ident), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        return True


def devolver(pasta, ids) -> None:
    """Desfaz reivindicações de lições que não chegaram a ser entregues."""
    if pasta is None:
        return
    for ident in ids:
        try:
            (pasta / ident).unlink()
        except Exception:
            pass


def sem_texto(comando: str) -> str:
    """O comando sem o texto que ele carrega: corpo de heredoc e trechos entre aspas.

    A área sai do que o comando FAZ. Uma mensagem de commit ou um padrão de grep que cita
    "docker" não é operação de deploy.
    """
    comando = re.sub(r"<<-?\s*(['\"]?)(\w+)\1([^\n]*)\n.*?^\s*\2\s*$", r"\3", comando,
                     flags=re.S | re.M)
    # O que vai dentro de `bash -c "..."` ou `pwsh -Command '...'` é o próprio comando: fica.
    comando = re.sub(r"(-c|-Command)\s+(['\"])(.*?)\2", r"\1 \3", comando, flags=re.S)
    return re.sub(r"'[^']*'|\"[^\"]*\"", "", comando)


_CABECALHO_DO_PATCH = re.compile(
    r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$", re.M)


def caminhos_do_patch(patch: str) -> list:
    """Os caminhos que um patch do Codex (`apply_patch`) toca, com `/`, na ordem em que aparecem.

    Lê só as linhas de cabeçalho (`*** Add File: `, `*** Update File: `, `*** Delete File: ` e
    `*** Move to: `); o resto do patch é conteúdo.
    """
    vistos = []
    for c in _CABECALHO_DO_PATCH.findall(patch):
        c = c.replace("\\", "/")
        if c not in vistos:
            vistos.append(c)
    return vistos


# ------------------------------------------------------------------ main


def main():
    try:
        dados = json.load(sys.stdin)
    except Exception as e:
        # stdin ilegível é defeito, não "nada a entregar". Sair com 3 faz o `gancho.sh` avisar o
        # agente e o usuário. Nunca 2: é o código que bloqueia a ferramenta.
        sys.stderr.write(f"stdin do gancho não é JSON: {type(e).__name__}\n")
        sys.exit(3)
    if not isinstance(dados, dict):
        return

    entrada = dados.get("tool_input") or {}
    if not isinstance(entrada, dict):
        return
    areas = set()

    if dados.get("tool_name") == "apply_patch":
        # Codex: a edição de arquivo chega como um patch em `tool_input.command`. Valem só os
        # caminhos do cabeçalho; o corpo é conteúdo, e casar gatilho contra ele entregaria a lição
        # de `pytest` a quem só escreveu a palavra num arquivo.
        caminhos = caminhos_do_patch(str(entrada.get("command") or ""))
        cru = comando = ""
    else:
        caminho = str(entrada.get("file_path") or "").replace("\\", "/")
        caminhos = [caminho] if caminho else []
        cru = entrada.get("command") or ""
        cru = " ".join(map(str, cru)) if isinstance(cru, list) else str(cru)
        comando = sem_texto(cru)

    for caminho in caminhos:
        for trecho, area in POR_CAMINHO:
            if trecho in caminho:
                areas.add(area)

    if comando:
        for padrao, lista in POR_COMANDO:
            if re.search(padrao, comando, re.I):
                areas.update(lista)

    # Sem área, a ação ainda pode casar com o gatilho de uma lição. O gatilho vê também o comando
    # CRU: o `sem_texto` serve à área, mas apaga o que está entre aspas
    # (`ssh host 'docker compose up -d'` viraria `ssh host `).
    alvos = [t for t in (*caminhos, cru, comando) if t]
    if not alvos:
        return

    licoes, degradou = candidatas(areas, alvos)
    regras = regras_para(areas)
    if not licoes and not regras:
        return

    # O teto antes de qualquer marca: se o golem.py faltar, o script cai aqui, sem ter marcado como
    # entregue uma regra que não chegou.
    teto = teto_do_gancho()
    marca = pasta_de_marca(dados)
    vistas = ja_entregues(marca)

    # As regras vêm primeiro e SEM teto: são mandato, não sinal. O nome do arquivo de marca é
    # `regra-N` (`regra:N` não é nome de arquivo válido no Windows).
    regras_novas = [r for r in regras
                    if f"regra-{r[0]}" not in vistas and reivindicar(marca, f"regra-{r[0]}")]

    # Lições: o pré-filtro descarta as já vistas; a reivindicação atômica decide as disputadas.
    entregar, examinadas = [], 0
    for licao in licoes:
        if licao[0] in vistas:
            continue
        if len(entregar) >= teto:
            break
        examinadas += 1
        if reivindicar(marca, licao[0]):
            entregar.append(licao)
    restantes = sum(1 for l in licoes if l[0] not in vistas) - examinadas

    if not regras_novas and not entregar:
        return  # tudo o que vale aqui já foi entregue nesta sessão

    reivindicadas = [f"regra-{n}" for n, _t, _c in regras_novas] + [i for i, _a, _t in entregar]
    try:
        entregar_saida(areas, degradou, regras_novas, entregar, restantes)
    except BaseException:
        # A marca foi gravada ANTES da entrega (é o que torna a reivindicação atômica). Se a
        # montagem ou a escrita falharem, devolve as lições; senão elas ficariam marcadas e nunca
        # chegariam, o que é silêncio.
        devolver(marca, reivindicadas)
        raise


def entregar_saida(areas, degradou, regras_novas, entregar, restantes) -> None:
    linhas = []
    if degradou:
        linhas.append(
            "⚠️ O índice de lições (`.claude/indice/licoes.yaml`) está ilegível, cortado ou "
            "ausente: entregando pela varredura do Markdown. Rode `python3 .claude/regua.py --gerar`."
        )
        linhas.append("")
    if regras_novas:
        linhas.append(
            f"Regras de área para {', '.join(sorted(areas))} (docs/regras-de-area.md):"
        )
        linhas.append("")
        for numero, titulo, corpo in regras_novas:
            linhas.append(f"**Regra {numero} — {titulo}**")
            linhas.append(corpo)
            linhas.append("")

    if entregar:
        # Ação sem área só chega aqui por gatilho: o rótulo não pode sair vazio.
        linhas.append(
            f"Lições registradas para {', '.join(sorted(areas)) or 'esta ação'} "
            f"(docs/licoes/ — armadilhas registradas neste projeto):"
        )
        linhas.append("")
        for ident, _area, tipo in entregar:
            sinal = sinal_de(ident)
            if not sinal:
                linhas.append(f"- **{ident}** ({tipo})")
            elif "\n" in sinal:
                # Sinal de várias linhas vai como bloco indentado, senão a lista vira parágrafo.
                linhas.append(f"- **{ident}** ({tipo}):")
                linhas.extend("  " + l if l else "" for l in sinal.splitlines())
            else:
                linhas.append(f"- **{ident}** ({tipo}): {sinal}")
        if restantes:
            # Com ações paralelas este número é aproximado; a entrega em si é exata.
            linhas.append(
                f"- (+{restantes} ainda não vistas nessa área: chegam na próxima ação que a "
                f"tocar, ou leia docs/licoes/<id>.md)"
            )

    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n".join(linhas),
        },
        "suppressOutput": True,
    }) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
