"""Instala o kit para o Codex: gera, a partir de `.claude/`, as cópias que o Codex lê.

    python3 .claude/instalar_codex.py              # escreve as cópias (rode de novo a cada mudança)
    python3 .claude/instalar_codex.py --conferir   # sai != 0 se alguma cópia divergir da fonte

(No Windows, `python` ou `py -3` no lugar de `python3`.)

A fonte é uma só, `.claude/`. As cópias vão para o Git, e o `--conferir` (no CI, ou antes do
commit) impede que elas envelheçam caladas:

- `.claude/skills/<nome>/**`  ->  `.agents/skills/<nome>/**` (o Codex lê as skills dali);
- `.claude/agents/<nome>.md`  ->  `.codex/agents/<nome>.toml` (frontmatter -> `name` e
  `description`; o corpo -> `developer_instructions`);
- o gancho das lições          ->  `.codex/hooks.json`, com duas entradas `PreToolUse`, uma para
  `Bash` e uma para `apply_patch`, e o mesmo aviso de queda do `.claude/settings.json`.

Idempotente: o que já está igual não é reescrito. Arquivo a mais dentro da pasta de uma skill do
kit (em `.agents/skills/<nome>/`) é removido; skill ou agente do Codex que não vem de `.claude/`
fica onde está. Só biblioteca padrão.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE_SKILLS = RAIZ / ".claude" / "skills"
FONTE_AGENTES = RAIZ / ".claude" / "agents"
SETTINGS = RAIZ / ".claude" / "settings.json"
DEST_SKILLS = RAIZ / ".agents" / "skills"
DEST_AGENTES = RAIZ / ".codex" / "agents"
HOOKS = RAIZ / ".codex" / "hooks.json"

# No Codex não há `CLAUDE_PROJECT_DIR`: a raiz vem do git, a partir da pasta da sessão.
LANCADOR = 'sh "$(git rev-parse --show-toplevel)/.claude/hooks/gancho.sh"'
MATCHERS = ("Bash", "apply_patch")


def _lf(dados: bytes) -> bytes:
    return dados.replace(b"\r\n", b"\n")


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


# ---------------------------------------------------------------- o que as cópias devem conter


def agente_toml(md: Path) -> tuple:
    """(nome, texto TOML) de um `.claude/agents/<nome>.md`."""
    texto = md.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", texto, re.S)
    if not m:
        raise ValueError(f"{_rel(md)}: sem frontmatter (bloco `---` no começo)")
    campos = dict(re.findall(r"^(\w+):[ \t]*(.*?)[ \t]*$", m.group(1), re.M))
    nome, descricao = campos.get("name", ""), campos.get("description", "")
    if not nome or not descricao:
        raise ValueError(f"{_rel(md)}: o frontmatter precisa de `name:` e `description:`")
    corpo = m.group(2).strip("\n") + "\n"
    # Literal de várias linhas ('''): nada é escape, e o texto fica legível. Se o corpo tiver
    # ''', cai na string básica, com os escapes do JSON (que o TOML aceita).
    if "'''" in corpo:
        instrucoes = json.dumps(corpo, ensure_ascii=False)
    else:
        instrucoes = "'''\n" + corpo + "'''"
    toml = (f"# GERADO por .claude/instalar_codex.py a partir de {_rel(md)}. NÃO EDITE À MÃO.\n"
            f"name = {json.dumps(nome, ensure_ascii=False)}\n"
            f"description = {json.dumps(descricao, ensure_ascii=False)}\n"
            f"developer_instructions = {instrucoes}\n")
    return nome, toml


def aviso_de_queda() -> str:
    """O `|| printf ...` do `.claude/settings.json`: o mesmo aviso, numa fonte só."""
    config = json.loads(SETTINGS.read_text(encoding="utf-8"))
    comando = config["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    i = comando.find(" || printf ")
    if i < 0:
        raise ValueError(".claude/settings.json: o comando do gancho não tem o `|| printf` de queda")
    return comando[i + len(" || "):]


def hooks_json() -> str:
    comando = f"{LANCADOR} || {aviso_de_queda()}"
    config = {"hooks": {"PreToolUse": [
        {"matcher": m, "hooks": [{"type": "command", "command": comando,
                                  "statusMessage": "Lendo as lições da área..."}]}
        for m in MATCHERS
    ]}}
    return json.dumps(config, ensure_ascii=False, indent=2) + "\n"


def esperado() -> dict:
    """{caminho de destino: bytes} de tudo o que as cópias devem conter."""
    alvo = {}
    for f in sorted(FONTE_SKILLS.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            alvo[DEST_SKILLS / f.relative_to(FONTE_SKILLS)] = f.read_bytes()
    for md in sorted(FONTE_AGENTES.glob("*.md")):
        nome, toml = agente_toml(md)
        alvo[DEST_AGENTES / f"{nome}.toml"] = toml.encode("utf-8")
    alvo[HOOKS] = hooks_json().encode("utf-8")
    return alvo


def sobras(alvo: dict) -> list:
    """Arquivos a mais dentro da pasta de uma skill do kit: a skill mudou e a cópia não."""
    fora = []
    if not FONTE_SKILLS.is_dir():
        return fora
    for pasta in sorted(p for p in FONTE_SKILLS.iterdir() if p.is_dir()):
        destino = DEST_SKILLS / pasta.name
        if destino.is_dir():
            fora += [f for f in sorted(destino.rglob("*"))
                     if f.is_file() and "__pycache__" not in f.parts and f not in alvo]
    return fora


# ---------------------------------------------------------------- instalar / conferir


def instalar() -> int:
    alvo = esperado()
    mudou = 0
    for caminho, dados in alvo.items():
        if caminho.is_file() and _lf(caminho.read_bytes()) == _lf(dados):
            continue
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(dados)
        print(f"  escrito  {_rel(caminho)}")
        mudou += 1
    for f in sobras(alvo):
        f.unlink()
        print(f"  removido {_rel(f)}")
        mudou += 1
    if mudou:
        print(f"  {mudou} arquivo(s) mudaram. Faça o `git add .agents .codex`.")
    else:
        print("  nada mudou: as cópias do Codex já batem com .claude/")
    return 0


def conferir() -> int:
    alvo = esperado()
    problema = False
    for caminho, dados in alvo.items():
        if not caminho.is_file():
            print(f"  FALTA    {_rel(caminho)}: rode .claude/instalar_codex.py")
            problema = True
        elif _lf(caminho.read_bytes()) != _lf(dados):
            print(f"  DIVERGE  {_rel(caminho)}: a fonte em .claude/ mudou, ou a cópia foi editada "
                  f"à mão; rode .claude/instalar_codex.py")
            problema = True
    for f in sobras(alvo):
        print(f"  SOBRA    {_rel(f)}: não existe mais em .claude/skills/; rode o instalador")
        problema = True
    if not problema:
        print(f"  ok       {len(alvo)} arquivos do Codex batem com .claude/")
    return 1 if problema else 0


USO = """uso: python3 .claude/instalar_codex.py [--conferir]

  (sem argumento)  escreve .agents/skills/, .codex/agents/ e .codex/hooks.json a partir de .claude/
  --conferir       sai != 0 se alguma cópia divergir da fonte
"""


def main(args=None) -> int:
    args = sys.argv[1:] if args is None else args
    if args == []:
        return instalar()
    if args == ["--conferir"]:
        return conferir()
    print(USO)
    return 2


if __name__ == "__main__":
    sys.exit(main())
