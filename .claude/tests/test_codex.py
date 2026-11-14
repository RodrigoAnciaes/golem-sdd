# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O kit no Codex: a entrada dele no gancho, o instalador e o comando do `.codex/hooks.json`.

E o lançador sem `CLAUDE_PROJECT_DIR`: a raiz vem do `git rev-parse --show-toplevel`.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from conftest import AMBIENTE, RAIZ, contexto_de, invocar_gancho

INSTALADOR = RAIZ / ".claude" / "instalar_codex.py"


def ids_de(texto: str) -> list:
    return re.findall(r"^\s*-\s+\*\*([a-z0-9][a-z0-9-]+)\*\*", texto, re.M)


def codex(tool_name: str, command: str) -> dict:
    """A entrada do Codex: sem `scratchpad_dir`, com `session_id` novo (a marca vai ao temp)."""
    return {"tool_name": tool_name, "tool_input": {"command": command},
            "session_id": "t-" + uuid.uuid4().hex[:12], "cwd": "/repo",
            "hook_event_name": "PreToolUse"}


def patch(*cabecalhos_e_corpo: str) -> str:
    return "*** Begin Patch\n" + "\n".join(cabecalhos_e_corpo) + "\n*** End Patch\n"


def sem_claude_project_dir() -> dict:
    return {k: v for k, v in AMBIENTE.items() if k != "CLAUDE_PROJECT_DIR"}


def _sh():
    sh = shutil.which("sh")
    if not sh and shutil.which("git"):
        candidato = Path(shutil.which("git")).resolve().parents[1] / "bin" / "sh.exe"
        sh = str(candidato) if candidato.is_file() else None
    if not sh:
        pytest.skip("sem `sh` no PATH nem junto do git")
    return sh


def _git():
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    return git


def _repassador(py: Path) -> None:
    py.parent.mkdir(parents=True, exist_ok=True)
    py.write_text(f'#!/bin/sh\nexec "{Path(sys.executable).as_posix()}" "$@"\n',
                  encoding="utf-8", newline="\n")
    os.chmod(py, 0o755)


# --------------------------------------------------------------- a entrada do Codex no gancho


def test_codex_bash_entrega_a_licao(acervo):
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    r = invocar_gancho(acervo.script, codex("Bash", "pytest -q"))
    assert ids_de(contexto_de(r)) == ["so-no-pytest"]


def test_codex_apply_patch_entrega_pela_area_do_caminho_e_nao_pelo_conteudo(acervo):
    acervo.licao("do-deploy", "deploy")
    acervo.licao("do-compose", "processo", [r"'compose\.yaml$'"])
    acervo.licao("so-no-pytest", "processo", [r"'\bpytest\b'"])
    acervo.gerar()
    # O corpo cita `pytest` e `docker compose up`: nada disso conta. Só o caminho.
    corpo = ["@@", "-x: 1", "+# rode pytest -q e docker compose up -d antes"]
    r = invocar_gancho(acervo.script, codex("apply_patch", patch(
        "*** Update File: deploy/compose.yaml", *corpo)))
    assert ids_de(contexto_de(r)) == ["do-compose", "do-deploy"]
    r = invocar_gancho(acervo.script, codex("apply_patch", patch(
        "*** Add File: notas/leia-me.md", "+rode pytest -q e git push depois")))
    assert contexto_de(r) == "", "o corpo do patch casou com gatilho ou acendeu área"


def test_codex_apply_patch_le_os_quatro_cabecalhos(gancho):
    texto = patch("*** Add File: a/novo.py", "+x", "*** Update File: b\\velho.py",
                  "*** Move to: deploy/movido.py", "@@", "-y", "+*** Add File: falso.py",
                  "*** Delete File: c/apagado.md")
    assert gancho.caminhos_do_patch(texto) == [
        "a/novo.py", "b/velho.py", "deploy/movido.py", "c/apagado.md"]


def test_codex_apply_patch_move_to_acende_a_area_do_destino(acervo):
    acervo.licao("do-deploy", "deploy")
    acervo.gerar()
    r = invocar_gancho(acervo.script, codex("apply_patch", patch(
        "*** Update File: notas/x.sh", "*** Move to: deploy/x.sh", "@@", "-a", "+b")))
    assert ids_de(contexto_de(r)) == ["do-deploy"]


# --------------------------------------------------------------- o instalador


def rodar_instalador(raiz: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(raiz / ".claude" / "instalar_codex.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=raiz,
                          env=AMBIENTE)


def _fotografia(raiz: Path) -> dict:
    return {p.relative_to(raiz).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for pasta in (raiz / ".agents", raiz / ".codex") for p in pasta.rglob("*")
            if p.is_file()}


def test_instalador_gera_as_copias_e_a_segunda_rodada_nao_muda_nada(copia_do_kit):
    tomllib = pytest.importorskip("tomllib")
    r = rodar_instalador(copia_do_kit)
    assert r.returncode == 0, r.stdout + r.stderr
    fonte = copia_do_kit / ".claude"
    # As skills: cópia byte a byte, inclusive as referências.
    for f in (fonte / "skills").rglob("*"):
        if f.is_file():
            copia = copia_do_kit / ".agents" / "skills" / f.relative_to(fonte / "skills")
            assert copia.read_bytes() == f.read_bytes(), copia
    # Os agentes: o frontmatter vira name/description; o corpo, developer_instructions.
    for nome in ("revisor", "validador"):
        md = (fonte / "agents" / f"{nome}.md").read_text(encoding="utf-8")
        dados = tomllib.loads((copia_do_kit / ".codex" / "agents" / f"{nome}.toml")
                              .read_text(encoding="utf-8"))
        assert dados["name"] == nome
        assert dados["description"] == re.search(r"^description: (.*)$", md, re.M).group(1)
        assert dados["developer_instructions"].strip() == md.split("\n---\n", 1)[1].strip()
    # O gancho: duas entradas, Bash e apply_patch, com a raiz pelo git e o aviso de queda.
    hooks = json.loads((copia_do_kit / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    entradas = hooks["hooks"]["PreToolUse"]
    assert [e["matcher"] for e in entradas] == ["Bash", "apply_patch"]
    for e in entradas:
        comando = e["hooks"][0]["command"]
        assert comando.startswith('sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"')
        assert "|| printf" in comando and "quebrou" in comando
    antes = _fotografia(copia_do_kit)
    r = rodar_instalador(copia_do_kit)
    assert r.returncode == 0 and "nada mudou" in r.stdout, r.stdout
    assert _fotografia(copia_do_kit) == antes, "a segunda rodada reescreveu arquivos"


def test_conferir_do_instalador_pega_a_divergencia(copia_do_kit):
    r = rodar_instalador(copia_do_kit, "--conferir")
    assert r.returncode != 0 and "FALTA" in r.stdout, "conferir antes de instalar passou"
    assert rodar_instalador(copia_do_kit).returncode == 0
    r = rodar_instalador(copia_do_kit, "--conferir")
    assert r.returncode == 0 and "ok" in r.stdout, r.stdout

    # A cópia editada à mão.
    skill = copia_do_kit / ".agents" / "skills" / "licao" / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nmudança à mão\n", encoding="utf-8")
    r = rodar_instalador(copia_do_kit, "--conferir")
    assert r.returncode != 0 and "DIVERGE  .agents/skills/licao/SKILL.md" in r.stdout, r.stdout
    assert rodar_instalador(copia_do_kit).returncode == 0

    # A fonte mudou e a cópia não.
    agente = copia_do_kit / ".claude" / "agents" / "revisor.md"
    agente.write_text(agente.read_text(encoding="utf-8") + "\nUma linha nova.\n",
                      encoding="utf-8")
    r = rodar_instalador(copia_do_kit, "--conferir")
    assert r.returncode != 0 and "DIVERGE  .codex/agents/revisor.toml" in r.stdout, r.stdout
    assert rodar_instalador(copia_do_kit).returncode == 0

    # Arquivo que sumiu da fonte e ficou na cópia.
    (copia_do_kit / ".agents" / "skills" / "licao" / "velho.md").write_text("x", encoding="utf-8")
    r = rodar_instalador(copia_do_kit, "--conferir")
    assert r.returncode != 0 and "SOBRA    .agents/skills/licao/velho.md" in r.stdout, r.stdout
    assert rodar_instalador(copia_do_kit).returncode == 0
    assert not (copia_do_kit / ".agents" / "skills" / "licao" / "velho.md").exists()
    assert rodar_instalador(copia_do_kit, "--conferir").returncode == 0


# --------------------------------------------------------------- o comando do .codex/hooks.json


def _arvore_com_git(acervo) -> Path:
    """O acervo com o settings.json e o instalador do kit, um venv repassador, e `git init`.
    Devolve uma subpasta, de onde os comandos rodam."""
    _repassador(acervo.raiz / ".venv" / "bin" / "python")
    shutil.copy2(RAIZ / ".claude" / "settings.json", acervo.raiz / ".claude" / "settings.json")
    shutil.copy2(INSTALADOR, acervo.raiz / ".claude" / "instalar_codex.py")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.licao("do-contrato", "contrato")
    acervo.gerar()
    subprocess.run([_git(), "init", "-q"], cwd=acervo.raiz, check=True, capture_output=True)
    sub = acervo.raiz / "src" / "modulo"
    sub.mkdir(parents=True)
    return sub


def test_o_comando_do_hooks_json_do_codex_roda_de_uma_subpasta(acervo):
    sh = _sh()
    sub = _arvore_com_git(acervo)
    assert rodar_instalador(acervo.raiz).returncode == 0
    entradas = json.loads((acervo.raiz / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    por_matcher = {e["matcher"]: e["hooks"][0]["command"] for e in entradas["hooks"]["PreToolUse"]}
    casos = {
        "Bash": (codex("Bash", "pytest -q"), ["so-no-pytest"]),
        "apply_patch": (codex("apply_patch", patch("*** Update File: docs/contratos/api.md",
                                                   "@@", "-a", "+pytest")), ["do-contrato"]),
    }
    assert set(por_matcher) == set(casos)
    for matcher, (payload, esperado) in casos.items():
        r = subprocess.run([sh, "-c", por_matcher[matcher]], input=json.dumps(payload),
                           capture_output=True, text=True, encoding="utf-8", cwd=sub,
                           env=sem_claude_project_dir())
        assert r.returncode == 0, r.stderr[:300]
        saida = json.loads(r.stdout)
        assert "systemMessage" not in saida, (matcher, saida.get("systemMessage"))
        assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == esperado, matcher


def test_settings_json_sem_claude_project_dir_acha_a_raiz_pelo_git(acervo):
    """O Claude Code sem a variável, numa subpasta: o `${CLAUDE_PROJECT_DIR:-...}` cai no git."""
    sh = _sh()
    sub = _arvore_com_git(acervo)
    config = json.loads((acervo.raiz / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for i, entrada in enumerate(config["hooks"]["PreToolUse"]):
        payload = {"session_id": "s", "scratchpad_dir": str(acervo.raiz.parent / f"s-{i}"),
                   "tool_input": {"command": "pytest -q"}}
        r = subprocess.run([sh, "-c", entrada["hooks"][0]["command"]], input=json.dumps(payload),
                           capture_output=True, text=True, encoding="utf-8", cwd=sub,
                           env=sem_claude_project_dir())
        assert r.returncode == 0, r.stderr[:300]
        saida = json.loads(r.stdout)
        assert "systemMessage" not in saida, (entrada["matcher"], saida.get("systemMessage"))
        assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def test_lancador_sem_o_proprio_caminho_acha_a_raiz_pelo_git(acervo):
    """O lançador lido por `sh -c` (o `$0` não aponta para ele), de uma subpasta: a raiz vem do
    `git rev-parse --show-toplevel`, e a lição chega.

    O texto passa ao `sh -c` de dentro de um `sh`, como no `sh -c "$(cat …)"`: dado direto pelo
    Python, um argumento de mais de uns 8 mil caracteres chega cortado ao `sh` do Git Bash."""
    sh = _sh()
    sub = _arvore_com_git(acervo)
    lancador = acervo.raiz / ".claude" / "hooks" / "gancho.sh"
    r = subprocess.run([sh, "-c", 'exec sh -c "$(cat "$1")"', "sh", str(lancador)],
                       input=json.dumps(codex("Bash", "pytest -q")),
                       capture_output=True, text=True, encoding="utf-8", cwd=sub,
                       env=sem_claude_project_dir())
    assert r.returncode == 0, r.stderr[:300]
    saida = json.loads(r.stdout)
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def _problema_yaml(valor: str):
    """Por que um valor de uma linha, sem aspas, não é texto simples no YAML (None se é)."""
    v = valor.strip()
    if not v:
        return None
    if v[0] in "\"'":
        return None if len(v) > 1 and v[-1] == v[0] else "aspas sem fechar"
    if v[0] in "[{*&!|>%@`" or v[:2] in ("- ", "? "):
        return "começa com um caractere especial do YAML"
    if ": " in v or v.endswith(":"):
        return "': ' num valor sem aspas"
    if " #" in v:
        return "' #' num valor sem aspas (o resto vira comentário)"
    return None


def test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido():
    """Um frontmatter que não é YAML válido some sem aviso: o Claude Code não carrega o agente (visto
    na fase 1, com "AGENTS.md: por grupo" na descrição do revisor; lição
    `frontmatter-invalido-some-com-o-agente-sem-aviso`)."""
    arquivos = sorted((RAIZ / ".claude" / "agents").glob("*.md"))
    arquivos += sorted((RAIZ / ".claude" / "skills").glob("*/SKILL.md"))
    problemas = []
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8").replace("\r\n", "\n")
        m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
        if not m:
            problemas.append(f"{arquivo.relative_to(RAIZ).as_posix()}: sem frontmatter")
            continue
        for n, linha in enumerate(m.group(1).split("\n"), 2):
            campo = re.match(r"^([A-Za-z_-]+):(.*)$", linha)
            motivo = _problema_yaml(campo.group(2)) if campo else "a linha não é `chave: valor`"
            if motivo:
                problemas.append(f"{arquivo.relative_to(RAIZ).as_posix()}:{n}: {motivo}")
    assert arquivos and not problemas, "\n".join(problemas)
