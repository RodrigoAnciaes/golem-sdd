# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O gancho das lições: entrega a lição que casa, cala a que não casa, e nunca cai."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import AMBIENTE, GANCHO, RAIZ as RAIZ_DO_KIT, contexto_de, invocar_gancho


def ids_de(texto: str) -> list:
    return re.findall(r"^\s*-\s+\*\*([a-z0-9][a-z0-9-]+)\*\*", texto, re.M)


# --------------------------------------------------------------- o essencial: casa ou não casa


def test_injeta_a_licao_cujo_gatilho_casa(acervo, sessao):
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    texto = acervo.invocar({"command": "PYTEST -q tests"}, sessao)  # sem diferenciar maiúsculas
    assert ids_de(texto) == ["so-no-pytest"]
    assert "sinal de so-no-pytest" in texto, "a lição saiu sem o sinal 'como perceber'"


def test_nao_injeta_a_licao_cujo_gatilho_nao_casa(acervo, sessao):
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.licao("so-no-push", gatilhos=[r"'\bgit\s+push\b'"])
    acervo.gerar()
    assert ids_de(acervo.invocar({"command": "git push origin x"}, sessao)) == ["so-no-push"]
    assert acervo.invocar({"command": "ls -la"}, sessao) == ""


def test_gatilho_casa_com_o_caminho_do_arquivo(acervo, sessao):
    """O caminho chega com `\\` no Windows; o gancho o troca por `/` antes de testar."""
    acervo.licao("do-plano", gatilhos=[r"'specs/[^/]+/plan\.md$'"])
    acervo.gerar()
    texto = acervo.invocar({"file_path": "C:\\repo\\specs\\fase-1\\plan.md"}, sessao)
    assert ids_de(texto) == ["do-plano"]
    assert "Lições registradas para" in texto


def test_licao_com_gatilho_nao_entra_so_pela_area(acervo, sessao):
    """`specs/` acende `processo`, mas o gatilho não casa: só a lição sem gatilho sai."""
    acervo.licao("so-no-pytest", "processo", [r"'\bpytest\b'"])
    acervo.licao("toda-a-area", "processo")
    acervo.gerar()
    assert ids_de(acervo.invocar({"file_path": "specs/x/plan.md"}, sessao)) == ["toda-a-area"]


def test_gatilho_vale_fora_da_propria_area(acervo, sessao):
    acervo.licao("de-deploy-no-pytest", "deploy", [r"'\bpytest\b'"])
    acervo.gerar()
    assert ids_de(acervo.invocar({"command": "pytest -q"}, sessao)) == ["de-deploy-no-pytest"]


def test_a_que_casou_por_gatilho_vem_antes_das_da_area(acervo, sessao):
    for n in range(5):
        acervo.licao(f"a-da-area-{n}", "processo")
    acervo.licao("z-do-push", "processo", [r"'\bgit\s+push\b'"])
    acervo.gerar()
    primeira = ids_de(acervo.invocar({"command": "git push origin x"}, sessao))
    assert primeira[0] == "z-do-push" and len(primeira) == 4, primeira


def test_gatilho_ve_o_texto_entre_aspas_e_a_area_nao(acervo, tmp_path):
    acervo.licao("do-compose-up", "deploy", [r"'docker\s+compose\s+up'"])
    acervo.licao("toda-a-area-deploy", "deploy")
    acervo.gerar()
    for i, (comando, esperado) in enumerate([
        # O gatilho vê o comando cru; a área (deploy, pelo `ssh`) também acende.
        ("ssh host 'docker compose up -d'", ["do-compose-up", "toda-a-area-deploy"]),
        # Mensagem de commit que cita docker não é operação de deploy.
        ('git commit -m "docker compose up quebrou"', ["do-compose-up"]),
        ("cat <<'EOF' > nota.md\ndocker no texto\nEOF", []),
    ]):
        scratch = tmp_path / f"s{i}"
        scratch.mkdir()
        assert ids_de(acervo.invocar({"command": comando}, scratch)) == esperado, comando


# --------------------------------------------------------------- uma vez por sessão, por agente


def test_segunda_acao_nao_repete_e_a_area_esgota(acervo, sessao):
    """O teto de 4 vale sobre o que é NOVO: a área inteira chega, sem repetir."""
    ids = [f"processo-{n:02d}" for n in range(10)]
    for ident in ids:
        acervo.licao(ident, "processo")
    acervo.gerar()
    vistas, rodadas = [], []
    while len(rodadas) < 10:
        got = ids_de(acervo.invocar({"file_path": "specs/x.md"}, sessao))
        if not got:
            break
        rodadas.append(len(got))
        vistas += got
    assert len(vistas) == len(set(vistas)), "alguma lição saiu duas vezes"
    assert sorted(vistas) == ids
    assert rodadas == [4, 4, 2], rodadas


def test_subagente_recebe_o_que_a_principal_ja_recebeu(acervo, sessao):
    acervo.licao("do-deploy", "deploy")
    acervo.gerar()
    entrada = {"file_path": "deploy/x.sh"}
    assert ids_de(acervo.invocar(entrada, sessao)) == ["do-deploy"]
    assert ids_de(acervo.invocar(entrada, sessao)) == []
    assert ids_de(acervo.invocar(entrada, sessao, agent_id="sub-1")) == ["do-deploy"]


def test_acoes_paralelas_nao_reentregam(acervo, sessao):
    from concurrent.futures import ThreadPoolExecutor
    ids = [f"processo-{n:02d}" for n in range(12)]
    for ident in ids:
        acervo.licao(ident, "processo")
    acervo.gerar()
    with ThreadPoolExecutor(6) as ex:
        saidas = list(ex.map(
            lambda _: ids_de(acervo.invocar({"file_path": "specs/x.md"}, sessao)), range(6)))
    todas = [i for s in saidas for i in s]
    assert len(todas) == len(set(todas)), f"reentrega em paralelo: {sorted(todas)}"
    assert sorted(todas) == ids


# --------------------------------------------------------------- não cai


@pytest.mark.parametrize("payload", ["{}", "[]", '"texto"', "null", '{"tool_input": null}',
                                     '{"tool_input": {}}', '{"tool_input": "x"}',
                                     '{"tool_input": {"command": ""}}'])
def test_entrada_vazia_ou_estranha_nao_cai_e_nao_injeta(payload):
    r = invocar_gancho(GANCHO, payload)
    assert r.returncode == 0, f"{payload!r}: código {r.returncode}, {r.stderr[:300]}"
    assert r.stdout.strip() == "", f"{payload!r} injetou lixo: {r.stdout[:200]}"


@pytest.mark.parametrize("payload", ["", "nao e json"])
def test_stdin_ilegivel_sai_com_codigo_controlado(payload):
    """stdin que não é JSON é defeito: sai 3, sem traceback, e o `gancho.sh` vira isso em aviso.
    Nunca 2, que bloquearia a ferramenta."""
    r = invocar_gancho(GANCHO, payload)
    assert r.returncode == 3, f"{payload!r}: código {r.returncode}"
    assert "não é JSON" in r.stderr and "Traceback" not in r.stderr


def test_licao_malformada_nao_derruba_o_gancho(acervo, sessao):
    """Sem frontmatter, regex inválida, id trocado, bytes inválidos: o gancho segue entregando a
    lição boa. Quem acusa as ruins é a régua."""
    acervo.licao("boa", gatilhos=[r"'\bpytest\b'"])
    acervo.licao("regex-quebrada", gatilhos=["'(sem-fechar'", r"'\bpytest\b'"])
    acervo.licao("id-trocado", arquivo="outro-nome")
    pasta = acervo.raiz / "docs" / "licoes"
    (pasta / "sem-frontmatter.md").write_text("só texto, nada de ---\n", encoding="utf-8")
    (pasta / "binario.md").write_bytes(b"---\nid: \xff\xfe\x00\n---\n\x00\x01")
    (pasta / "aspas-abertas.md").write_text(
        "---\nid: aspas-abertas\narea: processo\ntipo: armadilha\ngatilhos:\n  - 'sem-fechar\n---\n",
        encoding="utf-8")
    # Pelo índice (gerado sem as validações) e pelo Markdown (índice ausente).
    acervo.gerar()
    assert "boa" in ids_de(acervo.invocar({"command": "pytest -q"}, sessao))
    acervo.indice.unlink()
    outra = sessao.parent / "outra"
    outra.mkdir()
    texto = acervo.invocar({"command": "pytest -q"}, outra)
    assert "boa" in ids_de(texto)
    assert "ilegível, cortado ou ausente" in texto


def test_indice_corrompido_degrada_para_o_markdown(acervo, sessao):
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.indice.write_text("isto nao e o indice\n:::\n", encoding="utf-8")
    texto = acervo.invocar({"command": "pytest -q"}, sessao)
    assert "ilegível, cortado ou ausente" in texto
    assert ids_de(texto) == ["so-no-pytest"]


def test_indice_cortado_degrada_para_o_markdown(acervo, sessao):
    """O índice declara `total: N`; se as entradas lidas não baterem, ele está pela metade."""
    acervo.licao("a-primeira", gatilhos=[r"'\bpytest\b'"])
    acervo.licao("b-segunda", gatilhos=[r"'\bpytest\b'"])
    texto = acervo.gerar()
    cortado = texto.split("  b-segunda:")[0] + "total: 2\n"
    acervo.indice.write_text(cortado, encoding="utf-8")
    saida = acervo.invocar({"command": "pytest -q"}, sessao)
    assert "ilegível, cortado ou ausente" in saida
    assert ids_de(saida) == ["a-primeira", "b-segunda"]


def test_marca_corrompida_ainda_entrega(acervo, sessao):
    acervo.licao("do-deploy", "deploy")
    acervo.gerar()
    (sessao / "licoes-entregues").write_bytes(b"\x00 lixo no lugar da pasta \x00")
    import uuid
    payload = {"session_id": "t-" + uuid.uuid4().hex[:10], "scratchpad_dir": str(sessao),
               "tool_input": {"file_path": "deploy/x.sh"}}
    assert ids_de(contexto_de(invocar_gancho(acervo.script, payload))) == ["do-deploy"]


def test_ids_hostis_nao_escapam_da_pasta_e_ainda_entregam(acervo, sessao):
    acervo.licao("do-deploy", "deploy")
    acervo.gerar()
    payload = {"session_id": "../../fora", "agent_id": "../../fora", "scratchpad_dir": str(sessao),
               "tool_input": {"file_path": "deploy/x.sh"}}
    assert ids_de(contexto_de(invocar_gancho(acervo.script, payload))) == ["do-deploy"]
    assert not (sessao.parent / "fora").exists()


def test_licoes_voltam_quando_a_entrega_falha(acervo, sessao, monkeypatch):
    """A marca é gravada ANTES da entrega; se a montagem falhar, ela é desfeita."""
    import io
    acervo.licao("do-deploy", "deploy")
    acervo.gerar()
    gancho = acervo.regua().carregar_gancho()

    def explode(_ident):
        raise FileNotFoundError("a lição sumiu entre o is_file e a leitura")

    monkeypatch.setattr(gancho, "sinal_de", explode)
    payload = json.dumps({"session_id": "s", "scratchpad_dir": str(sessao),
                          "tool_input": {"file_path": "deploy/x.sh"}})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    with pytest.raises(FileNotFoundError):
        gancho.main()
    pasta = sessao / "licoes-entregues" / "principal"
    sobras = sorted(p.name for p in pasta.iterdir()) if pasta.is_dir() else []
    assert sobras == [], f"lições ficaram marcadas sem ter sido entregues: {sobras}"


# --------------------------------------------------------------- regras de área (opcional)


def test_regra_de_area_chega_uma_vez_e_so_a_quem_toca_a_area(acervo, tmp_path):
    (acervo.raiz / "docs" / "regras-de-area.md").write_text(
        "# Regras de área\n\n## Regra 1 — Nada de segredo no compose\nareas: deploy\n\n"
        "Credencial vem do cofre, nunca do arquivo.\n\n---\n\n"
        "## Regra 2 - Hífen comum não é lido\nareas: deploy\n\nx\n", encoding="utf-8")
    acervo.gerar()
    s1, s2 = tmp_path / "s1", tmp_path / "s2"
    s1.mkdir()
    s2.mkdir()
    texto = acervo.invocar({"file_path": "deploy/compose.yaml"}, s1)
    assert "**Regra 1 — Nada de segredo no compose**" in texto
    assert "Credencial vem do cofre" in texto and "Regra 2" not in texto
    assert acervo.invocar({"file_path": "deploy/compose.yaml"}, s1) == ""
    assert acervo.invocar({"file_path": "specs/x.md"}, s2) == ""


def test_sem_arquivo_de_regras_nada_muda(acervo, sessao):
    acervo.gerar()
    assert acervo.invocar({"file_path": "deploy/x.sh"}, sessao) == ""


# --------------------------------------------------------------- consistência e leitura


def test_areas_do_gancho_sao_validas(gancho, regua):
    """As áreas de `POR_CAMINHO` e `POR_COMANDO` têm de existir no vocabulário da régua."""
    usadas = {a for _t, a in gancho.POR_CAMINHO} | {a for _p, l in gancho.POR_COMANDO for a in l}
    assert usadas <= set(regua.AREAS_VALIDAS), usadas - set(regua.AREAS_VALIDAS)


def test_ler_gatilhos_aspas_simples_duplas_sem_aspas_e_comentario(gancho):
    texto = ("---\nid: x\narea: processo\ngatilhos:   # opcional\n"
             "  - '\\bit''s\\b'\n"
             '  - "\\\\bpytest\\\\b"   # entre aspas duplas\n'
             "  # comentário no meio da lista\n"
             "  - \\bpush\\b  # sem aspas\n"
             "  - 'a#b'\n"
             "refs:\n  - nao-e-gatilho\n---\n\ngatilhos:\n  - nem-isto\n")
    assert gancho.ler_gatilhos(texto) == [r"\bit's\b", r"\bpytest\b", r"\bpush\b", "a#b"]
    assert gancho.ler_gatilhos("---\nid: x\narea: processo\n---\n") == []
    assert gancho.ler_gatilhos("---\ngatilhos:\n  - 'sem-fechar\n---\n") == [None]


def test_sinal_sai_inteiro(gancho):
    texto = ("---\nid: x\n---\n\n**Como perceber da próxima vez:**\n1. primeiro.\n\n"
             "2. segundo, depois da linha em branco.\n\n**Atualização de 2026-01-01.** ainda conta.\n")
    sinal = gancho.como_perceber(texto)
    assert "segundo, depois da linha em branco" in sinal and "ainda conta" in sinal
    assert "fora" not in gancho.como_perceber(texto + "\n**Outro rótulo:** fora.\n")


# --------------------------------------------------------------- as lições de exemplo do kit


def test_licoes_de_exemplo_chegam_na_acao_certa(sessao, tmp_path):
    """Com o índice e as lições que o kit traz, pelo gancho de verdade."""
    assert ids_de(contexto_de(invocar_gancho(GANCHO, {"tool_input": {"command": "pytest -q"}},
                                             sessao))) == ["suite-verde-so-vale-com-a-linha-de-resumo"]
    outra = tmp_path / "outra"
    outra.mkdir()
    assert ids_de(contexto_de(invocar_gancho(GANCHO, {"tool_input": {"command": "gh pr merge 7"}},
                                             outra))) == ["conferir-e-agir-em-chamadas-separadas"]
    terceira = tmp_path / "terceira"
    terceira.mkdir()
    assert contexto_de(invocar_gancho(GANCHO, {"tool_input": {"command": "ls -la"}}, terceira)) == ""
    # Pelo caminho: editar a configuração do pytest (onde mora o `addopts`) também traz a lição.
    quarta = tmp_path / "quarta"
    quarta.mkdir()
    assert ids_de(contexto_de(invocar_gancho(
        GANCHO, {"tool_input": {"file_path": "C:\\repo\\pyproject.toml"}}, quarta))) == [
        "suite-verde-so-vale-com-a-linha-de-resumo"]


# --------------------------------------------------------------- o lançador


def _sh():
    """O `sh` do PATH; no Windows, o do Git for Windows (`<git>/cmd/git.exe` -> `<git>/bin/sh.exe`),
    que é o que o Claude Code usa para rodar o comando do gancho."""
    sh = shutil.which("sh")
    if not sh and shutil.which("git"):
        candidato = Path(shutil.which("git")).resolve().parents[1] / "bin" / "sh.exe"
        sh = str(candidato) if candidato.is_file() else None
    if not sh:
        pytest.skip("sem `sh` no PATH nem junto do git")
    return sh


def _repassador(py: Path) -> None:
    """Um script `sh` que repassa ao Python desta suíte."""
    py.parent.mkdir(parents=True, exist_ok=True)
    executavel = Path(sys.executable).as_posix()
    py.write_text(f'#!/bin/sh\nexec "{executavel}" "$@"\n', encoding="utf-8", newline="\n")
    os.chmod(py, 0o755)


def test_lancador_entrega_e_nunca_bloqueia(acervo, sessao):
    sh = _sh()
    _repassador(acervo.raiz / ".venv" / "bin" / "python")   # o lançador acha o venv da raiz
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    lancador = acervo.raiz / ".claude" / "hooks" / "gancho.sh"
    payload = json.dumps({"session_id": "s", "scratchpad_dir": str(sessao),
                          "tool_input": {"command": "pytest -q"}})
    r = subprocess.run([sh, str(lancador)], input=payload, capture_output=True, text=True,
                       encoding="utf-8", env=AMBIENTE)
    assert r.returncode == 0, r.stderr[:300]
    assert ids_de(json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]

    # stdin vazio: o Python sai 3, e o lançador transforma em aviso ao agente e ao usuário.
    r = subprocess.run([sh, str(lancador)], input="", capture_output=True, text=True,
                       encoding="utf-8", env=AMBIENTE)
    assert r.returncode == 0
    saida = json.loads(r.stdout)
    assert "systemMessage" in saida and "código 3" in saida["systemMessage"]
    assert "falhou" in saida["hookSpecificOutput"]["additionalContext"]
    assert (acervo.raiz / ".claude" / "gancho-falhas.log").is_file()


def test_lancador_sem_venv_usa_o_python_do_path(acervo, sessao, tmp_path):
    """Sem `.venv` na raiz nem repositório git: o lançador cai no `python3` do PATH."""
    sh = _sh()
    bin_ = tmp_path / "bin-falso"
    _repassador(bin_ / "python3")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    payload = json.dumps({"session_id": "s", "scratchpad_dir": str(sessao),
                          "tool_input": {"command": "pytest -q"}})
    ambiente = {**AMBIENTE, "PATH": str(bin_) + os.pathsep + os.environ.get("PATH", "")}
    r = subprocess.run([sh, str(acervo.raiz / ".claude" / "hooks" / "gancho.sh")], input=payload,
                       capture_output=True, text=True, encoding="utf-8", env=ambiente)
    assert r.returncode == 0, r.stderr[:300]
    saida = json.loads(r.stdout)
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def _quebrado(py: Path) -> None:
    """Um 'Python' que existe e não roda (o atalho da loja, o venv cujo Python sumiu)."""
    py.parent.mkdir(parents=True, exist_ok=True)
    py.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8", newline="\n")
    os.chmod(py, 0o755)


def _path_sem_python(tmp_path: Path) -> dict:
    """O PATH com `python3`, `python` e `py` quebrados na frente: só o caminho testado salva.

    Os lugares do instalador do Windows (`LOCALAPPDATA`, `PROGRAMFILES`) apontam para pastas
    vazias, senão o lançador acharia o Python real da máquina; e a pasta temporária (`TMPDIR`), onde
    ficam as marcas do aviso, é do teste. O `PROGRAMFILES` só vale pelo `_comando_do_lancador`.
    """
    bin_ = tmp_path / "bin-quebrado"
    for nome in ("python3", "python", "py"):
        _quebrado(bin_ / nome)
    vazias = tmp_path / "lugares-vazios"
    for nome in ("localappdata", "programfiles", "tmp"):
        (vazias / nome).mkdir(parents=True, exist_ok=True)
    return {**AMBIENTE, "PATH": str(bin_) + os.pathsep + os.environ.get("PATH", ""),
            "LOCALAPPDATA": str(vazias / "localappdata"),
            "PROGRAMFILES": str(vazias / "programfiles"), "TMPDIR": str(vazias / "tmp")}


def _comando_do_lancador(sh: str, lancador: Path, ambiente: dict) -> list:
    """O comando que roda o lançador com o `PROGRAMFILES` do `ambiente`, ou sem ele, se o
    `ambiente` não o tiver. No Windows, o sistema reescreve o `PROGRAMFILES` de todo processo novo,
    qualquer que seja o ambiente dado; só um `sh` o troca para o `sh` que ele chama."""
    if "PROGRAMFILES" in ambiente:
        return [sh, "-c", 'PROGRAMFILES="$2"; export PROGRAMFILES; exec sh "$1"', "sh",
                str(lancador), ambiente["PROGRAMFILES"]]
    return [sh, "-c", 'unset PROGRAMFILES; exec sh "$1"', "sh", str(lancador)]


def _rodar_lancador(sh: str, lancador: Path, sessao: Path, ambiente: dict, cwd=None) -> dict:
    payload = json.dumps({"session_id": "s", "scratchpad_dir": str(sessao),
                          "tool_input": {"command": "pytest -q"}})
    r = subprocess.run(_comando_do_lancador(sh, lancador, ambiente), input=payload,
                       capture_output=True, text=True, encoding="utf-8", env=ambiente, cwd=cwd)
    assert r.returncode == 0, r.stderr[:300]
    return json.loads(r.stdout)


def test_lancador_pula_o_venv_que_nao_roda(acervo, sessao, tmp_path):
    """O `.venv` da raiz existe e não roda: o lançador o testa como testa o PATH, e segue."""
    sh = _sh()
    _quebrado(acervo.raiz / ".venv" / "bin" / "python")
    bin_ = tmp_path / "bin-bom"
    _repassador(bin_ / "python3")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    ambiente = {**AMBIENTE, "PATH": str(bin_) + os.pathsep + os.environ.get("PATH", "")}
    saida = _rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao, ambiente)
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def test_lancador_usa_py_menos_3(acervo, sessao, tmp_path):
    """Sem `.venv` e com `python3` e `python` quebrados, o `py -3` (o lançador do Windows) salva."""
    sh = _sh()
    ambiente = _path_sem_python(tmp_path)
    py = Path(ambiente["PATH"].split(os.pathsep)[0]) / "py"
    executavel = Path(sys.executable).as_posix()
    # Só repassa se receber o `-3` primeiro: prova que o lançador chama `py -3`, não `py`.
    py.write_text(f'#!/bin/sh\n[ "$1" = "-3" ] || exit 9\nshift\nexec "{executavel}" "$@"\n',
                  encoding="utf-8", newline="\n")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    saida = _rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao, ambiente)
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def test_lancador_no_worktree_acha_o_venv_da_pasta_principal(acervo, sessao, tmp_path):
    """O worktree não tem `.venv` (ele é ignorado e não viaja); o da pasta principal serve.

    O PATH só tem Pythons quebrados: se a busca pela pasta principal sumir, o teste falha.
    """
    sh = _sh()
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    principal = acervo.raiz
    _repassador(principal / ".venv" / "bin" / "python")
    shutil.copy2(RAIZ_DO_KIT / ".gitattributes", principal / ".gitattributes")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    wt = tmp_path / "worktree-da-fase"
    identidade = ["-c", "user.name=teste", "-c", "user.email=teste@exemplo.invalid"]
    for args in (["init", "-q"], ["add", ".gitattributes", ".claude", "docs"],
                 [*identidade, "commit", "-q", "-m", "base"],
                 ["worktree", "add", "-q", str(wt)]):
        subprocess.run([git, *args], cwd=principal, check=True, capture_output=True)
    assert not (wt / ".venv").exists() and (wt / ".claude" / "hooks" / "gancho.sh").is_file()
    saida = _rodar_lancador(sh, wt / ".claude" / "hooks" / "gancho.sh", sessao,
                            _path_sem_python(tmp_path), cwd=wt)
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


# ------------------------------------------- a linha `python` e os lugares do instalador (fase 0)


def _golem_local(pasta: Path, caminho, crlf: bool = False) -> None:
    """Um `golem.local.toml` com a linha `python`, entre aspas simples, como a skill grava."""
    fim = "\r\n" if crlf else "\n"
    texto = f"# gravado pela skill diagnostico{fim}python = '{caminho}'  # comentário{fim}"
    (pasta / "golem.local.toml").write_bytes(texto.encode("utf-8"))


def _entrega_sem_aviso(saida: dict) -> None:
    assert "systemMessage" not in saida, saida.get("systemMessage")
    assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]


def test_lancador_usa_a_linha_python(acervo, sessao, tmp_path):
    """Sem `.venv` e com o PATH quebrado, só a linha `python` do golem.local.toml salva."""
    sh = _sh()
    py = tmp_path / "python-da-linha" / "python"
    _repassador(py)
    _golem_local(acervo.raiz, py)
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       _path_sem_python(tmp_path)))


def test_lancador_prefere_a_linha_python_ao_venv(acervo, sessao, tmp_path):
    """Com um `.venv` bom e a linha `python`, a linha vence: o `.venv` nem é chamado."""
    sh = _sh()
    executavel = Path(sys.executable).as_posix()
    marcas = {nome: tmp_path / f"chamou-{nome}" for nome in ("linha", "venv")}
    for nome, py in (("linha", tmp_path / "python-da-linha" / "python"),
                     ("venv", acervo.raiz / ".venv" / "bin" / "python")):
        py.parent.mkdir(parents=True, exist_ok=True)
        py.write_text(f'#!/bin/sh\n: > "{marcas[nome].as_posix()}"\nexec "{executavel}" "$@"\n',
                      encoding="utf-8", newline="\n")
        os.chmod(py, 0o755)
        if nome == "linha":
            _golem_local(acervo.raiz, py)
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       _path_sem_python(tmp_path)))
    assert marcas["linha"].is_file(), "o Python da linha python não foi chamado"
    assert not marcas["venv"].exists(), "o .venv foi chamado: a linha python não veio primeiro"


def test_lancador_no_worktree_acha_o_golem_local_da_pasta_principal(acervo, sessao, tmp_path):
    """O golem.local.toml é ignorado pelo git e não viaja ao worktree: vale o da pasta principal."""
    sh = _sh()
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    principal = acervo.raiz
    py = tmp_path / "python-da-linha" / "python"
    _repassador(py)
    _golem_local(principal, py)
    shutil.copy2(RAIZ_DO_KIT / ".gitattributes", principal / ".gitattributes")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    wt = tmp_path / "worktree-da-fase"
    identidade = ["-c", "user.name=teste", "-c", "user.email=teste@exemplo.invalid"]
    for args in (["init", "-q"], ["add", ".gitattributes", ".claude", "docs"],
                 [*identidade, "commit", "-q", "-m", "base"],
                 ["worktree", "add", "-q", str(wt)]):
        subprocess.run([git, *args], cwd=principal, check=True, capture_output=True)
    assert not (wt / "golem.local.toml").exists() and not (wt / ".venv").exists()
    _entrega_sem_aviso(_rodar_lancador(sh, wt / ".claude" / "hooks" / "gancho.sh", sessao,
                                       _path_sem_python(tmp_path), cwd=wt))


def test_lancador_le_a_linha_com_crlf_e_comentario(acervo, sessao, tmp_path):
    """O arquivo salvo em CRLF (o Bloco de Notas) e com comentário depois da aspa ainda vale."""
    sh = _sh()
    py = tmp_path / "python-da-linha" / "python"
    _repassador(py)
    _golem_local(acervo.raiz, py, crlf=True)
    assert b"\r\n" in (acervo.raiz / "golem.local.toml").read_bytes()
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       _path_sem_python(tmp_path)))


def test_lancador_pula_a_linha_python_que_nao_roda(acervo, sessao, tmp_path):
    """A linha aponta para um caminho que não existe: o lançador segue, em silêncio, até o PATH."""
    sh = _sh()
    _golem_local(acervo.raiz, tmp_path / "nao-existe" / "python.exe")
    bin_ = tmp_path / "bin-bom"
    _repassador(bin_ / "python3")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    ambiente = _path_sem_python(tmp_path)
    ambiente["PATH"] = str(bin_) + os.pathsep + ambiente["PATH"]
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       ambiente))


def test_lancador_acha_o_python_em_localappdata(acervo, sessao, tmp_path):
    """O instalador oficial põe o Python em `%LOCALAPPDATA%\\Programs\\Python\\Python3XY`, fora do
    PATH: o lançador o acha lá."""
    sh = _sh()
    ambiente = _path_sem_python(tmp_path)
    _repassador(Path(ambiente["LOCALAPPDATA"]) / "Programs" / "Python" / "Python312" / "python.exe")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       ambiente))


def test_lancador_acha_o_py_do_launcher_com_menos_3(acervo, sessao, tmp_path):
    """Só o `Launcher\\py.exe`, que repassa apenas se receber `-3` primeiro."""
    sh = _sh()
    ambiente = _path_sem_python(tmp_path)
    py = Path(ambiente["LOCALAPPDATA"]) / "Programs" / "Python" / "Launcher" / "py.exe"
    py.parent.mkdir(parents=True)
    executavel = Path(sys.executable).as_posix()
    py.write_text(f'#!/bin/sh\n[ "$1" = "-3" ] || exit 9\nshift\nexec "{executavel}" "$@"\n',
                  encoding="utf-8", newline="\n")
    os.chmod(py, 0o755)
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       ambiente))


def test_lancador_acha_o_python_em_programfiles(acervo, sessao, tmp_path):
    """O instalador "para todos os usuários" põe o Python em `%PROGRAMFILES%\\Python3XY`."""
    sh = _sh()
    ambiente = _path_sem_python(tmp_path)
    _repassador(Path(ambiente["PROGRAMFILES"]) / "Python312" / "python.exe")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    _entrega_sem_aviso(_rodar_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh", sessao,
                                       ambiente))


def test_lancador_sem_lugares_de_costume_avisa_sem_erro_de_sh(acervo, sessao, tmp_path):
    """`LOCALAPPDATA` vazio e `PROGRAMFILES` ausente (o Linux, o macOS): o aviso sai, e o stderr só
    traz a linha do próprio aviso, nenhum erro do `sh`."""
    sh = _sh()
    ambiente = _path_sem_python(tmp_path)
    ambiente["LOCALAPPDATA"] = ""
    del ambiente["PROGRAMFILES"]
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    payload = json.dumps({"session_id": "s", "scratchpad_dir": str(sessao),
                          "tool_input": {"command": "pytest -q"}})
    r = subprocess.run(_comando_do_lancador(sh, acervo.raiz / ".claude" / "hooks" / "gancho.sh",
                                            ambiente), input=payload,
                       capture_output=True, text=True, encoding="utf-8", env=ambiente)
    assert r.returncode == 0, r.stderr[:300]
    assert "nenhum Python" in json.loads(r.stdout)["systemMessage"]
    estranhas = [l for l in r.stderr.splitlines() if l and not l.startswith("gancho das lições:")]
    assert estranhas == [], estranhas


def test_o_comando_exato_do_settings_json_entrega(acervo, tmp_path):
    """Roda o `command` de cada gancho do `.claude/settings.json` como o Claude Code roda: pelo
    `sh`, com `CLAUDE_PROJECT_DIR` apontando para o projeto e a pasta corrente em outro lugar.

    Um caminho errado no settings.json não dá erro de sintaxe: cai no `|| printf` ("quebrou").
    """
    sh = _sh()
    _repassador(acervo.raiz / ".venv" / "bin" / "python")
    acervo.licao("so-no-pytest", gatilhos=[r"'\bpytest\b'"])
    acervo.gerar()
    config = json.loads((RAIZ_DO_KIT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entradas = config["hooks"]["PreToolUse"]
    matchers = {e["matcher"] for e in entradas}
    assert any("Edit" in m and "Write" in m for m in matchers), matchers
    assert any("Bash" in m for m in matchers), matchers
    fora = tmp_path / "outra-pasta"
    fora.mkdir()
    for i, entrada in enumerate(entradas):
        for gancho_ in entrada["hooks"]:
            scratch = tmp_path / f"sessao-{i}"
            scratch.mkdir(exist_ok=True)
            payload = json.dumps({"session_id": "s", "scratchpad_dir": str(scratch),
                                  "tool_input": {"command": "pytest -q"}})
            r = subprocess.run([sh, "-c", gancho_["command"]], input=payload,
                               capture_output=True, text=True, encoding="utf-8", cwd=fora,
                               env={**AMBIENTE, "CLAUDE_PROJECT_DIR": str(acervo.raiz)})
            assert r.returncode == 0, r.stderr[:300]
            saida = json.loads(r.stdout)
            assert "systemMessage" not in saida, (entrada["matcher"], saida.get("systemMessage"))
            assert ids_de(saida["hookSpecificOutput"]["additionalContext"]) == ["so-no-pytest"]
