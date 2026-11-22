# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O esqueleto do plugin (fase 3, o Golem central): o próprio kit é o plugin e o marketplace.

O `.claude-plugin/plugin.json` aponta as skills, os agentes e o gancho para dentro de `.claude/`,
onde o kit também os usa para se desenvolver. O `.claude/hooks/hooks.json` é o gancho do
`.claude/settings.json` com o lançador no `${CLAUDE_PLUGIN_ROOT}`: os dois não podem divergir.
"""
import json

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
