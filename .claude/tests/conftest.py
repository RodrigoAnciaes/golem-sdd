# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""Suíte do ferramental do agente: o gancho das lições, a régua do índice, as cópias do Codex e o
crédito do kit.

Rode da raiz do projeto:

    python3 -m pytest .claude/tests -o addopts= -q -p no:cacheprovider

(No Windows, `python` ou `py -3` no lugar de `python3`.)

Só biblioteca padrão e pytest. Os testes que precisam quebrar coisas de propósito (lição
malformada, índice velho, índice corrompido) trabalham numa CÓPIA da árvore em `tmp_path`,
nunca no `docs/licoes/` de verdade: uma interrupção no meio deixaria lixo versionado.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
GANCHO = RAIZ / ".claude" / "hooks" / "licoes_relevantes.py"
REGUA = RAIZ / ".claude" / "regua.py"
# Os subprocessos falam UTF-8 com a suíte, qualquer que seja a página de código do sistema.
AMBIENTE = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def invocar_gancho(script: Path, payload, scratch=None) -> subprocess.CompletedProcess:
    """Roda o gancho como o harness roda: JSON no stdin, JSON no stdout."""
    if isinstance(payload, dict):
        payload = dict(payload)
        payload.setdefault("session_id", "s1")
        if scratch is not None:
            payload.setdefault("scratchpad_dir", str(scratch))
        payload = json.dumps(payload)
    return subprocess.run([sys.executable, str(script)], input=payload,
                          capture_output=True, text=True, encoding="utf-8", env=AMBIENTE)


def contexto_de(r: subprocess.CompletedProcess) -> str:
    """O `additionalContext` da saída do gancho ('' se ele não injetou nada)."""
    assert r.returncode == 0, f"o gancho saiu {r.returncode}: {r.stderr[:400]}"
    if not r.stdout.strip():
        return ""
    return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


@pytest.fixture(scope="session")
def raiz() -> Path:
    return RAIZ


@pytest.fixture(scope="session")
def gancho():
    return carregar("licoes_relevantes", GANCHO)


@pytest.fixture(scope="session")
def regua():
    return carregar("regua", REGUA)


@pytest.fixture
def sessao(tmp_path) -> Path:
    """Um `scratchpad_dir` limpo: uma sessão nova do agente."""
    d = tmp_path / "scratch"
    d.mkdir()
    return d


class Acervo:
    """Uma árvore mínima: o gancho, a régua e SÓ as lições que o teste escreve.

    Com o acervo de verdade, o teto de 4 e as lições de exemplo interfeririam no que o teste quer
    provar ("não entregou" passaria por falta de vaga, e não pelo gatilho).
    """

    def __init__(self, raiz: Path):
        self.raiz = raiz
        (raiz / ".claude" / "hooks").mkdir(parents=True)
        (raiz / ".claude" / "indice").mkdir(parents=True)
        (raiz / "docs" / "licoes").mkdir(parents=True)
        shutil.copy2(GANCHO, raiz / ".claude" / "hooks" / "licoes_relevantes.py")
        shutil.copy2(RAIZ / ".claude" / "hooks" / "gancho.sh", raiz / ".claude" / "hooks" / "gancho.sh")
        shutil.copy2(REGUA, raiz / ".claude" / "regua.py")
        self.indice = raiz / ".claude" / "indice" / "licoes.yaml"
        self.script = raiz / ".claude" / "hooks" / "licoes_relevantes.py"

    def licao(self, ident: str, area: str = "processo", gatilhos=None, tipo="armadilha",
              arquivo: str | None = None) -> Path:
        """`gatilhos` = os itens como vão no YAML, já com as aspas (ex.: r"'\\bpytest\\b'")."""
        texto = (f"---\nid: {ident}\ndata: 2026-01-01\narea: {area}\ntipo: {tipo}\n"
                 f'custo: "x"\ngatilho: "x"\n')
        if gatilhos is not None:
            texto += "gatilhos:\n" + "".join(f"  - {g}\n" for g in gatilhos)
        texto += (f"refs:\n  - x\n---\n\n**O que se achava:** x.\n\n**O que é:** y.\n\n"
                  f"**Como perceber da próxima vez:** sinal de {ident}.\n")
        destino = self.raiz / "docs" / "licoes" / f"{arquivo or ident}.md"
        destino.write_text(texto, encoding="utf-8")
        return destino

    def regua(self):
        """A régua DA CÓPIA (a raiz dela é esta árvore), sem o filtro do git."""
        mod = carregar(f"regua_{uuid.uuid4().hex[:8]}", self.raiz / ".claude" / "regua.py")
        mod._RASTREADOS = None            # None = sem git = não filtra
        return mod

    def gerar(self) -> str:
        """Escreve o índice pelo gerador da régua (sem as validações do `--gerar`)."""
        texto = self.regua().gerar_licoes()
        self.indice.write_text(texto, encoding="utf-8")
        return texto

    def rodar_regua(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.raiz / ".claude" / "regua.py"), *args],
                              capture_output=True, text=True, encoding="utf-8", cwd=self.raiz,
                              env=AMBIENTE)

    def invocar(self, entrada: dict, scratch: Path, agent_id=None) -> str:
        payload = {"tool_input": entrada}
        if agent_id:
            payload["agent_id"] = agent_id
        return contexto_de(invocar_gancho(self.script, payload, scratch))


@pytest.fixture
def acervo(tmp_path) -> Acervo:
    return Acervo(tmp_path / "arvore-minima")


@pytest.fixture
def copia_do_kit(tmp_path) -> Path:
    """Uma cópia do kit inteiro (o `.claude/`, as lições de exemplo e o `AGENTS.md`), para
    sabotar à vontade."""
    destino = tmp_path / "kit"
    shutil.copytree(RAIZ / ".claude", destino / ".claude",
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "tests"))
    shutil.copytree(RAIZ / "docs" / "licoes", destino / "docs" / "licoes")
    shutil.copy2(RAIZ / "AGENTS.md", destino / "AGENTS.md")
    return destino
