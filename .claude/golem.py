# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""Configura o Golem neste projeto: junta a receita e as linhas do `golem.toml`, e aplica.

    python3 .claude/golem.py aplicar   # escreve o `model:` dos agentes e o bloco do AGENTS.md
    python3 .claude/golem.py           # os outros comandos (o central, o registro dos jogos)

(No Windows, `python` ou `py -3` no lugar de `python3`.)

O `golem.toml` fica na raiz do projeto, no git: é a escolha do projeto. Sem ele, vale a receita
`economico`. Cada linha escrita vale mais que a receita; a chave repetida vale pela última linha.

O formato é um pedaço do TOML, lido aqui, sem o `tomllib` (que só existe no Python 3.11+): cada
linha é vazia, um comentário (`#`) ou `chave = valor`, com o valor entre aspas duplas ou simples
(sem escape) ou inteiro, e um comentário opcional depois dele.

O `aplicar` escreve:
- o `model:` no frontmatter de `.claude/agents/revisor.md` e de `validador.md`;
- o bloco "Como o Golem trabalha aqui" no `AGENTS.md`, entre `<!-- golem:inicio -->` e
  `<!-- golem:fim -->` (sem as marcas, no fim do arquivo). O `AGENTS.md` entra em todo turno: o
  agente sabe a configuração sem abrir arquivo novo.

O gancho das lições lê o mesmo arquivo: o teto pelo `teto_do_gancho()` daqui, e a linha `gancho`
pelo próprio `gancho.sh`, em `sh`, para valer sem Python. Só biblioteca padrão.

Duas raízes (fase 3, o Golem central):
- `KIT` é a pasta de onde este script roda: no plugin, o kit; na instalação por cópia, o projeto.
- `RAIZ` é a raiz do projeto: a posição, salvo quando a posição é o plugin (a pasta tem
  `.claude-plugin/plugin.json`); aí, o git da pasta corrente (ou a pasta corrente, fora do git).
- **O modo plugin** é a pasta do kit ser o plugin e a raiz do projeto ser outra. Só nele vale o
  central (`central()`): o `golem.toml` dele fica por baixo do do jogo, linha a linha.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]


def eh_plugin(pasta: Path = KIT) -> bool:
    """A pasta é o plugin do Golem (tem o manifesto do plugin)."""
    return (pasta / ".claude-plugin" / "plugin.json").is_file()


def raiz_do_projeto(kit: Path = KIT) -> Path:
    """A posição, salvo no plugin: aí, o git da pasta corrente, ou a pasta corrente."""
    if not eh_plugin(kit):
        return kit
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, encoding="utf-8", timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).resolve()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return Path.cwd().resolve()


def central() -> Path:
    """A pasta do Golem central: `GOLEM_CENTRAL`, senão `$HOME/Golem`, senão a do `Path.home()`.

    A mesma regra do `gancho.sh` (que só tem o `HOME`): no Windows, o `Path.home()` usa o
    `USERPROFILE`, e os dois achariam pastas diferentes com um `HOME` diferente dele.
    """
    pasta = os.environ.get("GOLEM_CENTRAL")
    if pasta:
        return Path(pasta)
    casa = os.environ.get("HOME")
    return (Path(casa) if casa else Path.home()) / "Golem"


def modo_plugin(raiz: Path, kit: Path = KIT) -> bool:
    """O kit é o plugin e o projeto é outro: só aí vale o central."""
    return eh_plugin(kit) and Path(raiz).resolve() != kit.resolve()


RAIZ = raiz_do_projeto()
PADRAO = "economico"
INICIO = "<!-- golem:inicio -->"
FIM = "<!-- golem:fim -->"

ETAPA = ("sempre", "perguntar", "nunca")
MODELOS = ("sonnet", "opus", "haiku", "inherit")
TETO_MIN, TETO_MAX = 1, 10
# O teto de palavras do AGENTS.md, que entra inteiro em toda conversa (a régua avisa acima dele).
AGENTS_TETO = 3000
# As chaves de número: o mínimo e o máximo (None = sem máximo).
INTEIROS = {"gancho_teto": (TETO_MIN, TETO_MAX), "agents_teto": (1, None)}
VALORES = {
    "receita": ("so-eu", "economico", "completo"),
    "revisor": ETAPA,
    "revisor_quando": ("por_fase", "por_grupo"),
    "modelo_revisor": MODELOS,
    "validador": ETAPA,
    "modelo_validador": MODELOS,
    "guardiao": ETAPA,
    "parar_a_cada_parte": ("sempre", "nunca"),
    "conversas": ("uma", "papeis"),
    "gancho": ("ligado", "desligado"),
    "gancho_teto": None,  # um inteiro de TETO_MIN a TETO_MAX
    "agents_teto": None,  # um inteiro de 1 em diante
    "jogos_para_terceiros": ("sim", "nao"),
}
# As chaves que não dependem da receita, com o valor sem a linha. A `jogos_para_terceiros` é a
# resposta da pergunta geral do registro (fase 4b), e só se lê do golem.toml do central.
FORA_DAS_RECEITAS = {"jogos_para_terceiros": "nao"}

# Os recomendados do kit (docs/guia-configuracao.md mostra esta tabela).
RECEITAS = {
    "so-eu": {
        "revisor": "nunca", "revisor_quando": "por_fase", "modelo_revisor": "sonnet",
        "validador": "nunca", "modelo_validador": "opus", "guardiao": "nunca",
        "parar_a_cada_parte": "sempre", "conversas": "uma", "gancho": "ligado", "gancho_teto": 2,
        "agents_teto": AGENTS_TETO,
    },
    "economico": {
        "revisor": "sempre", "revisor_quando": "por_fase", "modelo_revisor": "sonnet",
        "validador": "nunca", "modelo_validador": "opus", "guardiao": "nunca",
        "parar_a_cada_parte": "sempre", "conversas": "uma", "gancho": "ligado", "gancho_teto": 2,
        "agents_teto": AGENTS_TETO,
    },
    "completo": {
        "revisor": "sempre", "revisor_quando": "por_grupo", "modelo_revisor": "opus",
        "validador": "sempre", "modelo_validador": "opus", "guardiao": "sempre",
        "parar_a_cada_parte": "nunca", "conversas": "papeis", "gancho": "ligado", "gancho_teto": 4,
        "agents_teto": AGENTS_TETO,
    },
}

_LINHA = re.compile(r"""^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*=\s*"""
                    r"""(?:"([^"]*)"|'([^']*)'|(-?[0-9]+))\s*(?:#.*)?$""")


class ErroDeConfiguracao(ValueError):
    pass


# ---------------------------------------------------------------- ler


def ler_texto(texto: str, origem: str = "golem.toml") -> dict:
    """{chave: valor} das linhas escritas, já conferidas. Falha com o número da linha."""
    linhas = {}
    for n, linha in enumerate(texto.splitlines(), 1):
        limpa = linha.strip()
        if not limpa or limpa.startswith("#"):
            continue
        m = _LINHA.match(linha)
        if not m:
            raise ErroDeConfiguracao(
                f"{origem}:{n}: a linha não é `chave = valor` (o valor entre aspas, ou um número) "
                f"nem um comentário: {limpa}")
        chave = m.group(1)
        if chave not in VALORES:
            raise ErroDeConfiguracao(
                f"{origem}:{n}: a chave `{chave}` não existe. As que valem: {', '.join(VALORES)}")
        if m.group(4) is not None:
            valor = int(m.group(4))
        else:
            valor = m.group(2) if m.group(2) is not None else m.group(3)
        aceitos = VALORES[chave]
        if chave in INTEIROS:
            minimo, maximo = INTEIROS[chave]
            if (not isinstance(valor, int) or valor < minimo
                    or (maximo is not None and valor > maximo)):
                faixa = f"de {minimo} a {maximo}" if maximo is not None else f"de {minimo} em diante"
                raise ErroDeConfiguracao(
                    f"{origem}:{n}: `{chave}` vale {valor!r}; o aceito é um número {faixa}, "
                    f"sem aspas")
        elif valor not in aceitos:
            raise ErroDeConfiguracao(
                f"{origem}:{n}: `{chave}` vale {valor!r}; os aceitos são "
                f"{', '.join(aceitos)}, entre aspas")
        linhas[chave] = valor
    return linhas


def _linhas(arquivo: Path, origem: str) -> dict:
    return ler_texto(arquivo.read_text(encoding="utf-8"), origem) if arquivo.is_file() else {}


def niveis(raiz: Path = RAIZ) -> tuple:
    """(as linhas do central, as do projeto). Fora do modo plugin, o central não conta.

    As chaves de `FORA_DAS_RECEITAS` só valem no `golem.toml` do central: num projeto que não é o
    central, a linha delas é erro (o `golem.toml` do jogo vai ao git dele)."""
    do_projeto = _linhas(raiz / "golem.toml", "golem.toml")
    do_central = {}
    if modo_plugin(raiz):
        arquivo = central() / "golem.toml"
        do_central = _linhas(arquivo, arquivo.as_posix())
    if not (modo_plugin(raiz) and _mesma_pasta(raiz, central())):
        for chave in FORA_DAS_RECEITAS:
            if chave in do_projeto:
                onde_vale = (f" ({(central() / 'golem.toml').as_posix()})" if modo_plugin(raiz)
                             else ", e aqui não há modo plugin")
                raise ErroDeConfiguracao(
                    f"golem.toml: a chave `{chave}` só vale no golem.toml do Golem central"
                    f"{onde_vale}; tire a linha `{chave}` deste")
    return do_central, do_projeto


def configuracao(raiz: Path = RAIZ) -> dict:
    """A configuração inteira: a receita, com as linhas do central e as do projeto por cima.

    Por chave, vale a linha do projeto, senão a do central, senão a da receita. A receita é a do
    projeto, senão a do central, senão a `economico`.
    """
    do_central, do_projeto = niveis(raiz)
    receita = do_projeto.get("receita", do_central.get("receita", PADRAO))
    return {**FORA_DAS_RECEITAS, **RECEITAS[receita], **do_central, **do_projeto,
            "receita": receita}


def teto_do_gancho(raiz: Path = RAIZ) -> int:
    """O teto do gancho. Com o `golem.toml` com erro, o da receita padrão: quem acusa é o aplicar."""
    try:
        return configuracao(raiz)["gancho_teto"]
    except (ErroDeConfiguracao, OSError, UnicodeDecodeError):
        return RECEITAS[PADRAO]["gancho_teto"]


def teto_do_agents(raiz: Path = RAIZ) -> int:
    """O teto de palavras do AGENTS.md, para a régua. Com o `golem.toml` com erro, o padrão."""
    try:
        return configuracao(raiz)["agents_teto"]
    except (ErroDeConfiguracao, OSError, UnicodeDecodeError):
        return AGENTS_TETO


# ---------------------------------------------------------------- o que o aplicar escreve


def _etapa(valor: str, quando: str, o_que: str) -> str:
    if valor == "nunca":
        return "nunca."
    return f"{valor}, {quando}: {o_que}."


def _modelo(valor: str) -> str:
    return " Modelo: o da conversa." if valor == "inherit" else f" Modelo `{valor}`."


def bloco(c: dict, plugin: bool = False) -> str:
    """O bloco "Como o Golem trabalha aqui", com as marcas, em LF. No plugin, o guia não está no
    projeto: o bloco o aponta pelo pedido."""
    por_fase = c["revisor_quando"] == "por_fase"
    quando = "uma vez por fase, antes da verificação" if por_fase else "a cada grupo"
    diff = "o diff da fase inteira" if por_fase else "o diff do grupo"
    linhas = [
        INICIO,
        "## Como o Golem trabalha aqui",
        "",
        "<!-- Gerado pelo `aplicar` do Golem. Não edite à mão: peça \"configurar o Golem\". -->",
        "",
        f"Receita `{c['receita']}`; o guia " + (
            "vem com o kit (peça \"configurar o Golem\")." if plugin
            else "é `docs/guia-configuracao.md`."),
        "",
        "- **Revisor:** " + _etapa(c["revisor"], quando, f"o `revisor` lê {diff}")
        + ("" if c["revisor"] == "nunca" else _modelo(c["modelo_revisor"])),
        "- **Validador:** " + _etapa(c["validador"], quando, f"o `validador` prova {diff}")
        + ("" if c["validador"] == "nunca" else _modelo(c["modelo_validador"])),
        "- **Guardião:** " + _etapa(c["guardiao"], "antes do merge",
                                    "o `revisor` lê o diff inteiro do PR"),
        "- **Os comandos do `validation.md`:** sempre, pela própria conversa, com a linha de "
        "resumo lida.",
        "- **Parar a cada parte:** " + (
            "sempre: ao fim de cada grupo, mostre o diff e uma linha do que mudou, e espere o ok."
            if c["parar_a_cada_parte"] == "sempre" else "nunca: siga grupo a grupo."),
        "- **Conversas:** " + (
            "uma; os papéis de `docs/operacao-das-conversas.md` são opcionais."
            if c["conversas"] == "uma" else "os papéis de `docs/operacao-das-conversas.md`."),
        "- **Gancho das lições:** " + (
            f"ligado, até {c['gancho_teto']} lições novas por ação." if c["gancho"] == "ligado"
            else "desligado: antes de editar um arquivo ou rodar um comando, procure em "
                 "`docs/licoes/` as lições que citam o nome dele."),
    ]
    if "perguntar" in (c["revisor"], c["validador"], c["guardiao"]):
        linhas += ["", "Com `perguntar`, pergunte com botões na hora, dizendo o custo (\"abre 1 "
                       "conversa extra\"), e só rode com o sim; sem botões, em texto numerado."]
    linhas.append(FIM)
    return "\n".join(linhas) + "\n"


def com_bloco(texto: str, novo: str) -> str:
    """O `AGENTS.md` (em LF) com o bloco trocado entre as marcas, ou acrescentado no fim."""
    i = texto.find(INICIO)
    f = texto.find(FIM, i + len(INICIO)) if i >= 0 else texto.find(FIM)
    if i < 0 and f < 0:
        return texto.rstrip("\n") + "\n\n" + novo
    if i < 0 or f < 0:
        raise ErroDeConfiguracao(f"AGENTS.md: as marcas {INICIO} e {FIM} estão incompletas ou "
                                 "fora de ordem; deixe as duas, nessa ordem, ou apague as duas")
    resto = texto[f + len(FIM):]
    return texto[:i] + novo + (resto[1:] if resto.startswith("\n") else resto)


def com_modelo(texto: str, modelo: str) -> str:
    """O agente (em LF) com a linha `model:` do frontmatter trocada ou acrescentada."""
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    if not m:
        raise ErroDeConfiguracao("o agente não tem frontmatter (bloco `---` no começo)")
    campos = m.group(1).split("\n")
    sem_modelo = [c for c in campos if not c.startswith("model:")]
    pos = next((k + 1 for k, c in enumerate(sem_modelo) if c.startswith("tools:")),
               len(sem_modelo))
    novos = sem_modelo[:pos] + [f"model: {modelo}"] + sem_modelo[pos:]
    return "---\n" + "\n".join(novos) + "\n---\n" + texto[m.end():]


def _ler(caminho: Path) -> tuple:
    """(texto em LF, fim de linha original) de um arquivo."""
    bruto = caminho.read_bytes().decode("utf-8")
    fim = "\r\n" if "\r\n" in bruto else "\n"
    return bruto.replace("\r\n", "\n"), fim


def esperado(raiz: Path = RAIZ) -> dict:
    """{caminho: (texto em LF, fim de linha)} do que o aplicar deixa. Falha antes de escrever."""
    c = configuracao(raiz)
    alvo = {}
    agentes = {"revisor": c["modelo_revisor"], "validador": c["modelo_validador"]}
    for nome, modelo in agentes.items():
        caminho = raiz / ".claude" / "agents" / f"{nome}.md"
        if caminho.is_file():
            texto, fim = _ler(caminho)
            try:
                alvo[caminho] = (com_modelo(texto, modelo), fim)
            except ErroDeConfiguracao as e:
                raise ErroDeConfiguracao(f".claude/agents/{nome}.md: {e}") from None
    agents_md = raiz / "AGENTS.md"
    if agents_md.is_file():
        texto, fim = _ler(agents_md)
        alvo[agents_md] = (com_bloco(texto, bloco(c, modo_plugin(raiz))), fim)
    return alvo


# ---------------------------------------------------------------- aplicar


def aplicar(raiz: Path = RAIZ) -> int:
    try:
        alvo = esperado(raiz)
    except ErroDeConfiguracao as e:
        print(f"  ERRO     {e}\n  Nada foi escrito.")
        return 1
    mudou = 0
    for caminho, (texto, fim) in alvo.items():
        if _ler(caminho)[0] == texto:
            continue
        caminho.write_bytes(texto.replace("\n", fim).encode("utf-8"))
        print(f"  escrito  {caminho.relative_to(raiz).as_posix()}")
        mudou += 1
    for falta in ("AGENTS.md", ".claude/agents/revisor.md", ".claude/agents/validador.md"):
        if (raiz / falta).is_file():
            continue
        if falta != "AGENTS.md" and modo_plugin(raiz):
            print(f"  pulado   {falta}: no Golem central, o agente mora no kit, e o modelo vai na "
                  "chamada (o bloco diz qual)")
        else:
            print(f"  pulado   {falta}: não existe neste projeto")
    if mudou:
        print(f"  {mudou} arquivo(s) mudaram. A configuração nova vale numa conversa nova.")
    else:
        print("  nada mudou: o AGENTS.md e os agentes já seguem o golem.toml")
    return 0


# ---------------------------------------------------------------- o central e os jogos (fase 3)

ID_DO_PLUGIN = "golem@golem"
LIGADO = Path(".claude") / "settings.local.json"
REGISTRO = "jogos.md"
CABECALHO_DO_REGISTRO = (
    "# Os jogos do Golem\n\n"
    "<!-- O registro dos jogos desta máquina. Quem escreve é o kit (\"registrar um jogo\"); uma "
    "linha se apaga à mão. -->\n\n"
    "| Jogo | Pasta | Registrado em | Para terceiros |\n"
    "|---|---|---|---|\n")
# O cabeçalho da fase 3, de três colunas, e o de agora. A quarta coluna (fase 4b) diz se o jogo é
# feito para um estúdio ou outra pessoa: nada dele sobe ao acervo geral. Na linha de três células,
# vale `não`.
_CABECALHOS = (["Jogo", "Pasta", "Registrado em"],
               ["Jogo", "Pasta", "Registrado em", "Para terceiros"])
GOLEM_TOML_DO_CENTRAL = (
    "# golem.toml do Golem central: a configuração de todos os jogos desta máquina.\n"
    "# O golem.toml de um jogo vale por cima, linha a linha. Para mudar, peça \"configurar o "
    "Golem\".\n")


def _escrever(caminho: Path, texto: str, escritos: list) -> None:
    """Escreve só se mudou, e anota o caminho em `escritos`."""
    if caminho.is_file() and caminho.read_bytes() == texto.encode("utf-8"):
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8"))
    escritos.append(caminho)


def _com_ligado(pasta: Path) -> str:
    """O `.claude/settings.local.json` de `pasta` com o "ligado" do Golem, guardando o resto.

    Falha (sem escrever nada) se o arquivo existe e não é um objeto JSON.
    """
    arquivo = pasta / LIGADO
    dados = {}
    if arquivo.is_file():
        try:
            dados = json.loads(_ler(arquivo)[0] or "{}")
        except ValueError as e:
            raise ErroDeConfiguracao(f"{arquivo.as_posix()}: não é um JSON válido ({e}); "
                                     "conserte ou apague o arquivo, e rode de novo") from None
        if not isinstance(dados, dict) or not isinstance(dados.get("enabledPlugins", {}), dict):
            raise ErroDeConfiguracao(f"{arquivo.as_posix()}: o JSON não é um objeto com "
                                     "`enabledPlugins` como objeto; conserte e rode de novo")
    dados.setdefault("enabledPlugins", {})[ID_DO_PLUGIN] = True
    return json.dumps(dados, ensure_ascii=False, indent=2) + "\n"


def _com_gitignore(pasta: Path) -> str:
    """O `.gitignore` de `pasta` com a linha do "ligado" (fora do git), se faltar, no fim de
    linha que o arquivo já usa (como o `aplicar`)."""
    arquivo = pasta / ".gitignore"
    texto, fim = _ler(arquivo) if arquivo.is_file() else ("", "\n")
    linha = LIGADO.as_posix()
    if linha in (l.strip() for l in texto.splitlines()):
        return arquivo.read_bytes().decode("utf-8")      # já tem: fica como está, byte a byte
    if texto and not texto.endswith("\n"):
        texto += "\n"
    texto += ("# O \"ligado\" do Golem é desta máquina (o registro dos jogos também).\n"
              + linha + "\n")
    return texto.replace("\n", fim)


def _linha_do_registro(linha: str):
    """("jogo", [nome, pasta, data, para terceiros]), ("cabecalho", None), ("separador", None)
    ou None (uma linha que não é da tabela). O cabeçalho e o separador se reconhecem pela linha
    inteira: um jogo pode se chamar "Jogo". A linha de três células (a da fase 3) vale `não`, e a
    marca escrita à mão que não é `não` vale `sim`: um erro de digitação não desprotege o jogo."""
    celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
    if not linha.lstrip().startswith("|") or len(celulas) not in (3, 4):
        return None
    if celulas in _CABECALHOS:
        return "cabecalho", None
    if all(c and set(c) <= set("-: ") for c in celulas):
        return "separador", None
    # Na quarta célula, só `não` (ou `nao`) desprotege: outro valor escrito à mão vale `sim`.
    marca = celulas[3].lower() if len(celulas) == 4 else "não"
    return "jogo", celulas[:3] + ["não" if marca in ("não", "nao") else "sim"]


def ler_registro() -> list:
    """[(nome, pasta, data, para terceiros)] do `jogos.md` do central; [] sem o arquivo. O último
    vale `sim` ou `não`."""
    arquivo = central() / REGISTRO
    if not arquivo.is_file():
        return []
    jogos = []
    for linha in _ler(arquivo)[0].splitlines():
        lida = _linha_do_registro(linha)
        if lida and lida[0] == "jogo":
            jogos.append(tuple(lida[1]))
    return jogos


def jogo_do_registro(pasta: Path):
    """A linha do registro do jogo desta pasta, ou None (fora do registro)."""
    return next((j for j in ler_registro() if _mesma_pasta(j[1], pasta)), None)


def _mesma_pasta(a, b) -> bool:
    return os.path.normcase(str(Path(a).resolve())) == os.path.normcase(str(Path(b).resolve()))


def criar_central() -> list:
    """Cria o central (o `golem.toml`, o `jogos.md`, a `jogos/` e o "ligado"), o que faltar."""
    c = central()
    escritos = []
    texto_ligado = _com_ligado(c)
    if not (c / "golem.toml").is_file():
        _escrever(c / "golem.toml", GOLEM_TOML_DO_CENTRAL, escritos)
    if not (c / REGISTRO).is_file():
        _escrever(c / REGISTRO, CABECALHO_DO_REGISTRO, escritos)
    if not (c / "jogos").is_dir():
        (c / "jogos").mkdir(parents=True)
        escritos.append(c / "jogos")
    _escrever(c / LIGADO, texto_ligado, escritos)
    return escritos


def _registro_com(pasta: Path, nome: str, terceiros: bool) -> str:
    """O texto do `jogos.md` com o jogo: a linha dele, se já está (com o `sim` na marca, se
    `terceiros`; sem ele, a marca fica como está), ou uma linha nova no fim. A tabela da fase 3
    passa a quatro colunas, com `não` nas linhas que já existiam."""
    texto = _ler(central() / REGISTRO)[0]
    linhas, achou = [], False
    for linha in texto.splitlines():
        lida = _linha_do_registro(linha)
        if lida is None:
            linhas.append(linha)
        elif lida[0] == "cabecalho":
            linhas.append("| " + " | ".join(_CABECALHOS[1]) + " |")
        elif lida[0] == "separador":
            linhas.append("|---|---|---|---|")
        else:
            celulas = lida[1]
            if _mesma_pasta(celulas[1], pasta):
                achou = True
                if terceiros:
                    celulas[3] = "sim"
            linhas.append("| " + " | ".join(celulas) + " |")
    if not achou:
        hoje = datetime.date.today().isoformat()
        marca = "sim" if terceiros else "não"
        linhas.append(f"| {nome} | {pasta.as_posix()} | {hoje} | {marca} |")
    return "\n".join(linhas) + "\n"


def registrar(pasta: Path, nome: str = None, terceiros: bool = False) -> list:
    """Põe o jogo no registro e o "ligado" nele. Confere tudo antes de escrever.

    `terceiros`: o jogo é feito para um estúdio ou outra pessoa (o `--terceiros`). Só marca: sem
    ele, a marca que já existe fica (desmarcar é à mão, no `jogos.md`)."""
    pasta = Path(pasta).resolve()
    nome = (nome or pasta.name).strip()
    if not nome or "|" in nome or "\n" in nome or "\r" in nome:
        raise ErroDeConfiguracao(f"o nome {nome!r} não serve: sem `|`, sem quebra de linha e "
                                 "não vazio (é uma linha da tabela do jogos.md)")
    if not pasta.is_dir():
        raise ErroDeConfiguracao(f"{pasta.as_posix()}: a pasta do jogo não existe")
    texto_ligado = _com_ligado(pasta)
    texto_gitignore = _com_gitignore(pasta)
    escritos = criar_central()
    _escrever(pasta / LIGADO, texto_ligado, escritos)
    _escrever(pasta / ".gitignore", texto_gitignore, escritos)
    _escrever(central() / REGISTRO, _registro_com(pasta, nome, terceiros), escritos)
    return escritos


def _relatar(escritos: list) -> None:
    for caminho in escritos:
        print(f"  escrito  {caminho.as_posix()}")
    print(f"  {len(escritos)} arquivo(s) mudaram." if escritos else "  nada mudou")


def aplicar_todos() -> int:
    """O `aplicar` em cada jogo do registro; o jogo cuja pasta sumiu sai com um aviso."""
    jogos = ler_registro()
    if not jogos:
        print(f"  nenhum jogo no registro ({(central() / REGISTRO).as_posix()})")
        return 0
    codigo = 0
    for nome, pasta, *_ in jogos:
        print(f"== {nome} ({pasta})")
        if not Path(pasta).is_dir():
            print(f"  pulado   {nome}: a pasta não existe mais (apague a linha do jogos.md, se o "
                  "jogo saiu desta máquina)")
            continue
        codigo = max(codigo, aplicar(Path(pasta)))
    return codigo


def onde(raiz: Path = RAIZ) -> int:
    """Diz a raiz, o modo, o central e de onde vem cada linha da configuração."""
    print(f"  projeto  {raiz.as_posix()}")
    plugin = modo_plugin(raiz)
    if not plugin:
        print("  modo     cópia: o kit mora no próprio projeto (.claude/); o central não conta")
    else:
        c = central()
        print(f"  modo     plugin: o kit mora em {KIT.as_posix()}")
        print(f"  central  {c.as_posix()}" + ("" if c.is_dir() else " (ainda não existe)"))
        jogo = jogo_do_registro(raiz)
        if jogo is None:
            print("  para terceiros: fora do registro (sem ele, nada deste projeto sobe ao "
                  "acervo geral)")
        else:
            print(f"  para terceiros: {jogo[3]}" + (
                " (um estúdio ou outra pessoa: nada deste jogo vai ao acervo geral)"
                if jogo[3] == "sim" else ""))
    try:
        do_central, do_projeto = niveis(raiz)
        cfg = configuracao(raiz)
    except ErroDeConfiguracao as e:
        print(f"  ERRO     {e}")
        return 1
    for chave in VALORES:
        if chave in FORA_DAS_RECEITAS and not plugin:
            continue                      # só vale no central
        if chave in do_projeto:
            origem = "deste projeto"
        elif chave in do_central:
            origem = "do central"
        else:
            origem = "o padrão" if chave == "receita" or chave in FORA_DAS_RECEITAS else "da receita"
        print(f"  {chave}: {cfg[chave]} ({origem})")
    return 0


# ---------------------------------------------------------------- o acervo geral (fase 4b)

SUBIDAS = Path(".claude") / "indice" / "subidas.txt"


def impressao(arquivo: Path) -> str:
    """A impressão (sha256) do texto de uma lição, com as quebras de linha em `\\n`: o
    `core.autocrlf` do Git for Windows não muda a impressão."""
    texto = arquivo.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(texto).hexdigest()


def _linha_de_subida(linha: str):
    """(id, impressão do jogo, impressão do geral, pasta do jogo) de uma linha do `subidas.txt`, ou
    None. A pasta vem por último: ela pode ter espaços."""
    if linha.startswith("#"):
        return None
    partes = linha.split(maxsplit=3)
    return tuple(partes) if len(partes) == 4 else None


def ler_subidas(raiz: Path) -> dict:
    """{id: (impressão da lição do jogo, impressão da versão geral)} das subidas feitas DESTE jogo
    (`raiz`), do `subidas.txt` do central, como estavam na subida; {} sem o arquivo. Uma linha por
    id e jogo: dois jogos que sobem o mesmo id não se atropelam."""
    arquivo = central() / SUBIDAS
    if not arquivo.is_file():
        return {}
    subidas = {}
    for linha in _ler(arquivo)[0].splitlines():
        lida = _linha_de_subida(linha)
        if lida and _mesma_pasta(lida[3], raiz):
            subidas[lida[0]] = (lida[1], lida[2])
    return subidas


def _carregar_regua():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("regua_do_kit", KIT / ".claude" / "regua.py")
    regua = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(regua)
    return regua


def _regua_em(pasta: Path) -> subprocess.CompletedProcess:
    """A régua do kit, `--gerar`, com a pasta corrente em `pasta` (fora do git, a raiz é ela)."""
    return subprocess.run([sys.executable, str(KIT / ".claude" / "regua.py"), "--gerar"],
                          cwd=pasta, capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def _cita_o_projeto(texto: str, nome: str, raiz: Path, refs: list, regua,
                    palavra_comum: bool = False) -> str:
    """O que a lição cita do projeto, ou ''. Sem diferenciar maiúsculas: o nome do jogo e o da
    pasta (como palavra), o caminho da pasta, a ref a um arquivo do jogo e não do kit, a ref a um
    script do place.

    `palavra_comum`: o usuário disse que os nomes que aparecem são a palavra comum, e não o jogo (o
    jogo "Obby" e a lição sobre obbies). Pula só a conferência do nome do jogo e do da pasta; o
    caminho e as refs ficam. A recusa cita todos os nomes que batem: o sim cobre tudo o que pula.
    """
    reescreva = ". Reescreva a lição sem nada do projeto"
    baixo = texto.lower()
    for caminho in (raiz.as_posix(), str(raiz)):
        if caminho.lower() in baixo:
            return f"o texto cita a pasta do jogo ({raiz.as_posix()}){reescreva}"
    citados = [p for p in dict.fromkeys(p for p in (nome, raiz.name) if p)
               if re.search(rf"(?<![\w-]){re.escape(p.lower())}(?![\w-])", baixo)]
    if citados and not palavra_comum:
        nomes = " e ".join(repr(p) for p in citados)
        return (f"o texto cita {nomes}, o nome do jogo ou da pasta dele{reescreva}; se ali é a "
                f"palavra comum, e não o jogo, rode de novo com --palavra-comum (a skill `licao` "
                f"pergunta antes)")
    for item in refs:
        if not isinstance(item, str):
            continue
        if item.startswith("game."):
            return f"a ref {item!r} cita um script do place{reescreva}"
        m = regua._REF.match(item)
        if m and (raiz / m.group(1)).is_file() and not (KIT / m.group(1)).is_file():
            return f"a ref {m.group(1)!r} cita um arquivo do jogo{reescreva}"
    return ""


def subir(arquivo: Path, substituir: bool = False, raiz: Path = RAIZ,
          palavra_comum: bool = False) -> list:
    """Copia ao acervo geral (`<central>/docs/licoes/`) a versão geral de uma lição, regera o
    índice do geral e grava a subida em `<central>/.claude/indice/subidas.txt`. Confere tudo
    antes de escrever; a lição do jogo não muda. `palavra_comum`: ver `_cita_o_projeto`."""
    if not modo_plugin(raiz):
        raise ErroDeConfiguracao("fora do modo plugin não há Golem central: o subir só vale num "
                                 "jogo registrado no central")
    jogo = jogo_do_registro(raiz)
    if jogo is None:
        raise ErroDeConfiguracao(f"{raiz.as_posix()} não está no registro do central "
                                 f"({(central() / REGISTRO).as_posix()}): sem ele, não se sabe se "
                                 "o jogo é para terceiros. Registre o jogo antes")
    if jogo[3] == "sim":
        raise ErroDeConfiguracao("este jogo é para terceiros (um estúdio ou outra pessoa): nada "
                                 "dele vai ao acervo geral, porque o que se aprende nele pertence "
                                 "a quem encomendou")
    arquivo = Path(arquivo).resolve()
    if not arquivo.is_file():
        raise ErroDeConfiguracao(f"{arquivo.as_posix()}: o arquivo não existe")
    if arquivo.suffix != ".md" or arquivo.name == "README.md":
        raise ErroDeConfiguracao(f"{arquivo.as_posix()}: não é uma lição (um `<id>.md`, fora o "
                                 "README.md)")
    do_jogo = raiz / "docs" / "licoes" / arquivo.name
    if not do_jogo.is_file():
        raise ErroDeConfiguracao(f"{do_jogo.as_posix()} não existe: a subida copia uma lição "
                                 "deste jogo, e a versão geral tem o nome do arquivo dela")
    try:
        texto = arquivo.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise ErroDeConfiguracao(f"{arquivo.as_posix()}: o texto não está em UTF-8") from None
    regua = _carregar_regua()
    problema = _cita_o_projeto(texto, jogo[0], raiz, regua._gancho().ler_gatilhos(texto, "refs"),
                               regua, palavra_comum)
    if problema:
        raise ErroDeConfiguracao(problema)
    geral = central() / "docs" / "licoes"
    destino = geral / arquivo.name
    if destino.is_file() and not substituir and not _mesma_pasta(destino, arquivo):
        raise ErroDeConfiguracao(f"{destino.as_posix()} já existe no acervo geral: para trocá-la, "
                                 "rode de novo com --substituir")
    # A régua confere o acervo geral COM a lição nova numa cópia, antes de escrever no central.
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "docs" / "licoes"
        copia.mkdir(parents=True)
        for velha in (geral.glob("*.md") if geral.is_dir() else []):
            shutil.copy2(velha, copia / velha.name)
        (copia / arquivo.name).write_bytes(texto.encode("utf-8"))
        r = _regua_em(Path(tmp))
        if r.returncode != 0:
            raise ErroDeConfiguracao("a régua recusa o acervo geral com esta lição:\n"
                                     + _saida_da_regua(r))
    indice = central() / ".claude" / "indice" / "licoes.yaml"
    antes = {p: p.read_bytes() if p.is_file() else None for p in (destino, indice)}
    pastas_novas = [p for p in (geral, geral.parent) if not p.is_dir()]
    escritos = []
    _escrever(destino, texto, escritos)
    r = _regua_em(central())
    if r.returncode != 0:
        # Desfaz a escrita, e a pasta criada agora: com a `docs/licoes/` vazia no central, o gancho
        # avisaria "índice ilegível" do geral em todo jogo. O "Nada foi escrito" tem de ser verdade.
        for caminho, bruto in antes.items():
            if bruto is None:
                caminho.unlink(missing_ok=True)
            else:
                caminho.write_bytes(bruto)
        for pasta in pastas_novas:
            if pasta.is_dir() and not any(pasta.iterdir()):
                pasta.rmdir()
        saida = ""
        if (central() / ".git").exists():
            saida = (f"\n  Com o central no git: copie a lição à mão a {destino.as_posix()}, faça "
                     "o `git add` dela no central e rode o subir de novo com --substituir.")
        raise ErroDeConfiguracao("a régua não regerou o índice do acervo geral:\n"
                                 + _saida_da_regua(r) + saida)
    for linha in r.stderr.splitlines():
        if "AVISO" in linha:
            print(linha)                  # o central no git: a lição fora dele não entra no índice
    if indice.is_file() and indice.read_bytes() != antes[indice]:
        escritos.append(indice)
    linha = f"{arquivo.stem} {impressao(do_jogo)} {impressao(destino)} {raiz.as_posix()}"
    registro = central() / SUBIDAS
    linhas = _ler(registro)[0].splitlines() if registro.is_file() else [
        "# As subidas ao acervo geral: o id, a impressão da lição do jogo, a da versão geral e a "
        "pasta do jogo, como estavam na subida. Quem escreve é o `golem.py subir`; a régua "
        "compara (fase 4b)."]

    def deste_jogo(l):
        lida = _linha_de_subida(l)
        return lida is not None and lida[0] == arquivo.stem and _mesma_pasta(lida[3], raiz)

    linhas = [l for l in linhas if not deste_jogo(l)] + [linha]
    _escrever(registro, "\n".join(linhas) + "\n", escritos)
    return escritos


def _saida_da_regua(r: subprocess.CompletedProcess) -> str:
    """A saída da régua, sem a frase "Nada foi escrito" dela (o `_rodar` diz a sua)."""
    texto = (r.stdout + r.stderr).replace(" Nada foi escrito.", "").replace("Nada foi escrito.", "")
    return "\n".join(l for l in texto.splitlines() if l.strip()).rstrip()


USO = """uso: python3 .claude/golem.py <comando>

  aplicar            junta a receita e as linhas do golem.toml (no plugin, as do central por
                     baixo) e escreve o `model:` dos agentes e o bloco "Como o Golem trabalha aqui"
                     do AGENTS.md
  aplicar --todos    o mesmo, em cada jogo do registro do central
  central            cria o Golem central, o que faltar ($GOLEM_CENTRAL, senão ~/Golem)
  registrar <pasta> [--nome <nome>] [--terceiros]
                     põe o jogo no registro do central e o liga ("ligado" no
                     .claude/settings.local.json do jogo); o --terceiros marca o jogo como feito
                     para um estúdio ou outra pessoa: nada dele sobe ao acervo geral
  onde               diz a raiz do projeto, o modo, o central e de onde vem cada linha
  subir <arquivo> [--substituir] [--palavra-comum]
                     copia ao acervo geral do central a versão geral de uma lição (sem nada do
                     projeto) e regera o índice dele; só num jogo do registro que não é para
                     terceiros. O --palavra-comum pula só a conferência do nome do jogo e do da
                     pasta, quando aparecem como palavra comum (o jogo "Obby" e a lição sobre
                     obbies); o caminho da pasta e as refs continuam conferidos
"""


def _rodar(funcao, *args) -> int:
    try:
        _relatar(funcao(*args))
    except ErroDeConfiguracao as e:
        print(f"  ERRO     {e}\n  Nada foi escrito.")
        return 1
    return 0


def main(args=None) -> int:
    args = sys.argv[1:] if args is None else args
    if args == ["aplicar"]:
        return aplicar()
    if args == ["aplicar", "--todos"]:
        return aplicar_todos()
    if args == ["central"]:
        return _rodar(criar_central)
    if args == ["onde"]:
        return onde()
    if args[:1] == ["registrar"]:
        resto = [a for a in args[1:] if a != "--terceiros"]
        terceiros = len(resto) < len(args) - 1
        if len(resto) == 1:
            return _rodar(registrar, Path(resto[0]), None, terceiros)
        if len(resto) == 3 and resto[1] == "--nome":
            return _rodar(registrar, Path(resto[0]), resto[2], terceiros)
    if args[:1] == ["subir"]:
        opcoes = {"--substituir", "--palavra-comum"}
        resto = [a for a in args[1:] if a not in opcoes]
        if len(resto) == 1:
            return _rodar(subir, Path(resto[0]), "--substituir" in args, RAIZ,
                          "--palavra-comum" in args)
    print(USO)
    return 2


if __name__ == "__main__":
    sys.exit(main())
