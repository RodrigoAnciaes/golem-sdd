# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O esqueleto do plugin (fase 3, o Golem central): o próprio kit é o plugin e o marketplace.

O `.claude-plugin/plugin.json` aponta as skills, os agentes e o gancho para dentro de `.claude/`,
onde o kit também os usa para se desenvolver. O `.claude/hooks/hooks.json` é o gancho do
`.claude/settings.json` com o lançador no `${CLAUDE_PLUGIN_ROOT}`: os dois não podem divergir.
"""
import json
import re

from conftest import RAIZ
from test_credito import NOME, URL

PLUGIN = RAIZ / ".claude-plugin" / "plugin.json"
MARKETPLACE = RAIZ / ".claude-plugin" / "marketplace.json"
LANCADOR_DO_PROJETO = ('sh "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}'
                       '/.claude/hooks/gancho.sh"')
LANCADOR_DO_PLUGIN = 'sh "${CLAUDE_PLUGIN_ROOT}/.claude/hooks/gancho.sh"'


def _json(caminho):
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_o_manifesto_aponta_todas_as_skills_e_todos_os_agentes_do_kit():
    p = _json(PLUGIN)
    assert p["name"] == "golem"
    assert p["skills"] == "./.claude/skills/"
    assert (RAIZ / p["skills"]).is_dir()
    agentes = sorted(p["agents"])
    no_kit = sorted(f"./.claude/agents/{a.name}" for a in (RAIZ / ".claude" / "agents").glob("*.md"))
    assert agentes == no_kit, "o manifesto e a pasta .claude/agents/ divergem"
    assert all((RAIZ / a).is_file() for a in agentes)
    assert p["hooks"] == "./.claude/hooks/hooks.json" and (RAIZ / p["hooks"]).is_file()


def test_o_manifesto_traz_o_credito_e_nasce_desligado():
    p = _json(PLUGIN)
    assert p["author"]["name"] == NOME
    assert p["homepage"] == URL
    assert p["license"] == "MIT"
    assert p["defaultEnabled"] is False, "sem isto, o plugin liga em todo projeto do usuário"


def test_o_marketplace_lista_o_proprio_kit():
    m = _json(MARKETPLACE)
    assert m["name"] == "golem"
    assert m["owner"]["name"] == NOME
    assert [(e["name"], e["source"]) for e in m["plugins"]] == [("golem", "./")]


def test_o_gancho_do_plugin_e_o_do_settings_com_o_lancador_trocado():
    """Os mesmos `matcher`, `timeout`, `statusMessage` e a mesma queda (o `|| printf`)."""
    settings = _json(RAIZ / ".claude" / "settings.json")["hooks"]
    for grupo in settings["PreToolUse"]:
        for gancho in grupo["hooks"]:
            assert gancho["command"].startswith(LANCADOR_DO_PROJETO), gancho["command"][:80]
            gancho["command"] = LANCADOR_DO_PLUGIN + gancho["command"][len(LANCADOR_DO_PROJETO):]
    assert _json(RAIZ / ".claude" / "hooks" / "hooks.json") == {"hooks": settings}


# ------------------------------------------- as skills acham o kit pela pasta delas (G4)

SKILLS = RAIZ / ".claude" / "skills"
DO_KIT = re.compile(r"\.claude/(golem|regua|instalar_codex)\.py|\.claude/hooks/")
# A única menção sem o prefixo: o texto literal do aviso do gancho, citado pela `diagnostico`.
CITACOES = ('"não achei .claude/hooks/licoes_relevantes.py"',)


def _arquivos_md():
    return sorted(list(SKILLS.rglob("*.md")) + list((RAIZ / ".claude" / "agents").glob("*.md")))


def test_nenhuma_skill_nem_agente_chama_um_arquivo_do_kit_pelo_caminho_do_projeto():
    """No plugin, o jogo não tem `.claude/regua.py` nem `.claude/hooks/`: o caminho sai da pasta da
    skill (`${CLAUDE_SKILL_DIR}/../../regua.py`, que não cita `.claude/`, ou
    `${CLAUDE_SKILL_DIR}/../../../.claude/regua.py`) ou do `$KIT` que a `iniciar-sdd` calcula dela."""
    soltas = []
    for md in _arquivos_md():
        for n, linha in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if any(c in linha for c in CITACOES):
                continue
            for m in DO_KIT.finditer(linha):
                antes = linha[:m.start()]
                if not (antes.endswith("${CLAUDE_SKILL_DIR}/../../../") or antes.endswith("$KIT/")):
                    soltas.append(f"{md.relative_to(RAIZ).as_posix()}:{n}: {linha.strip()}")
    assert not soltas, "chamadas pelo caminho do projeto:\n" + "\n".join(soltas)


def test_todo_caminho_pela_pasta_da_skill_existe_no_kit():
    faltam = []
    for md in sorted(SKILLS.glob("*/SKILL.md")):
        for m in re.finditer(r"\$\{CLAUDE_SKILL_DIR\}((?:/\.\.)+)/([\w./-]*\w)", md.read_text(encoding="utf-8")):
            subidas, resto = m.group(1).count(".."), m.group(2)
            if subidas not in (2, 3):
                faltam.append(f"{md.parent.name}: sobe {subidas} pastas ({m.group(0)})")
                continue
            alvo = (md.parent / m.group(1).lstrip("/") / resto).resolve()
            if not alvo.exists():
                faltam.append(f"{md.parent.name}: {m.group(0)} -> {alvo}")
    assert not faltam, "\n".join(faltam)
