"""A régua: gera o índice, confere que ele não envelheceu, e RECUSA a lição que não consegue ler."""
import re
import shutil
import subprocess
import sys

import pytest

from conftest import AMBIENTE, RAIZ


def rodar(raiz, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(raiz / ".claude" / "regua.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=raiz, env=AMBIENTE)


# --------------------------------------------------------------- gerar e conferir


def test_o_indice_do_kit_esta_em_dia():
    """O índice que o kit traz bate com as lições que o kit traz."""
    r = rodar(RAIZ, "--conferir")
    assert r.returncode == 0, f"índice do kit divergente:\n{r.stdout}\n{r.stderr}"


def test_gerar_seguido_de_conferir_passa(copia_do_kit):
    (copia_do_kit / ".claude" / "indice" / "licoes.yaml").unlink()
    r = rodar(copia_do_kit, "--conferir")
    assert r.returncode != 0 and "FALTA" in r.stdout, "conferir sem índice passou"
    r = rodar(copia_do_kit, "--gerar")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "escrito  .claude/indice/licoes.yaml" in r.stdout
    r = rodar(copia_do_kit, "--conferir")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ok       .claude/indice/licoes.yaml" in r.stdout


def test_conferir_falha_com_o_indice_velho(copia_do_kit):
    """O motivo de o `--conferir` existir: índice que envelhece cala a lição nova."""
    assert rodar(copia_do_kit, "--gerar").returncode == 0
    licao = copia_do_kit / "docs" / "licoes" / "suite-verde-so-vale-com-a-linha-de-resumo.md"
    licao.write_text(licao.read_text(encoding="utf-8").replace("area: processo", "area: codigo", 1),
                     encoding="utf-8")
    r = rodar(copia_do_kit, "--conferir")
    assert r.returncode != 0, "índice desencontrado do Markdown passou como ok"
    assert "DIVERGE" in r.stdout


def test_conferir_falha_com_licao_nova_fora_do_indice(acervo):
    acervo.licao("primeira")
    assert acervo.rodar_regua("--gerar").returncode == 0
    acervo.licao("segunda")
    r = acervo.rodar_regua("--conferir")
    assert r.returncode != 0 and "DIVERGE" in r.stdout


def test_o_indice_traz_os_gatilhos_e_o_gancho_os_le(acervo):
    """O campo atravessa os dois lados: a régua escreve em JSON numa linha, o gancho lê."""
    acervo.licao("com-gatilho", gatilhos=[r"'\bgit\s+push\b'", "'specs/.*\\.md$'"])
    acervo.licao("sem-gatilho")
    texto = acervo.gerar()
    assert '    gatilhos: ["\\\\bgit\\\\s+push\\\\b", "specs/.*\\\\.md$"]' in texto
    assert "gatilhos:" not in texto.split("  sem-gatilho:")[1]
    assert texto.rstrip().endswith("total: 2")
    gancho = acervo.regua().carregar_gancho()
    assert sorted(gancho.do_indice()) == [
        ("com-gatilho", "processo", "armadilha", [r"\bgit\s+push\b", r"specs/.*\.md$"]),
        ("sem-gatilho", "processo", "armadilha", []),
    ]


def test_readme_nao_e_licao(acervo):
    acervo.licao("uma")
    (acervo.raiz / "docs" / "licoes" / "README.md").write_text("# Lições\n", encoding="utf-8")
    assert [a.name for a in acervo.regua().arquivos_de_licao()] == ["uma.md"]


# --------------------------------------------------------------- recusa de entrada malformada


def _escrever(acervo, nome: str, frontmatter: str) -> None:
    (acervo.raiz / "docs" / "licoes" / f"{nome}.md").write_text(
        f"---\n{frontmatter}---\n\n**Como perceber da próxima vez:** sinal.\n", encoding="utf-8")


BASE = 'data: 2026-01-01\ncusto: "x"\ngatilho: "x"\n'


@pytest.mark.parametrize("nome, frontmatter, trecho", [
    ("id-trocado", "id: outro-id\narea: processo\ntipo: armadilha\n" + BASE,
     "diferente do nome do arquivo"),
    ("id_com_sublinhado", "id: id_com_sublinhado\narea: processo\ntipo: armadilha\n" + BASE,
     "fora de [a-z0-9-]"),
    ("sem-id", "area: processo\ntipo: armadilha\n" + BASE, "sem campo `id:`"),
    ("sem-area", "id: sem-area\ntipo: armadilha\n" + BASE, "sem campo `area:`"),
    ("area-errada", "id: area-errada\narea: marketing\ntipo: armadilha\n" + BASE,
     "area 'marketing' fora de codigo, deploy, contrato, processo"),
    ("sem-tipo", "id: sem-tipo\narea: processo\n" + BASE, "sem campo `tipo:`"),
    ("tipo-errado", "id: tipo-errado\narea: processo\ntipo: curiosidade\n" + BASE,
     "tipo 'curiosidade' fora de"),
    ("gatilhos-em-linha", "id: gatilhos-em-linha\narea: processo\ntipo: armadilha\n"
     "gatilhos: ['pytest']\n" + BASE, "lista em bloco"),
    ("regex-invalida", "id: regex-invalida\narea: processo\ntipo: armadilha\n"
     "gatilhos:\n  - '(sem-fechar'\n" + BASE, "gatilho '(sem-fechar' não é expressão regular válida"),
    ("aspas-duplas-com-b", "id: aspas-duplas-com-b\narea: processo\ntipo: armadilha\n"
     'gatilhos:\n  - "\\bgit\\b"\n' + BASE, "caractere de controle (\\x08)"),
    ("aspas-sem-fechar", "id: aspas-sem-fechar\narea: processo\ntipo: armadilha\n"
     "gatilhos:\n  - 'sem-fechar\n" + BASE, "aspas que não se lê"),
])
def test_gerar_recusa_e_conferir_acusa(acervo, nome, frontmatter, trecho):
    acervo.licao("boa")
    _escrever(acervo, nome, frontmatter)
    r = acervo.rodar_regua("--gerar")
    assert r.returncode != 0 and "RECUSADO" in r.stdout, r.stdout
    assert trecho in r.stdout, r.stdout
    assert not acervo.indice.exists(), "o --gerar recusado escreveu o índice assim mesmo"
    r = acervo.rodar_regua("--conferir")
    assert r.returncode != 0 and "INVÁLIDO" in r.stdout and trecho in r.stdout, r.stdout


def test_comentario_na_linha_do_campo_nao_entra_no_valor(acervo, sessao):
    """`area: codigo   # codigo | deploy` vale `codigo`; entre aspas, o `#` é texto."""
    _escrever(acervo, "com-comentario",
              "id: com-comentario     # igual ao nome do arquivo\n"
              "area: deploy           # codigo | deploy | contrato | processo\n"
              "tipo: armadilha        # premissa-falsa | armadilha\n"
              'data: 2026-01-01\ncusto: "custa # caro"\ngatilho: "x"\n')
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0, r.stdout
    texto = acervo.indice.read_text(encoding="utf-8")
    assert '    area: "deploy"' in texto and '    tipo: "armadilha"' in texto
    assert acervo.regua().campo(
        (acervo.raiz / "docs" / "licoes" / "com-comentario.md").read_text(encoding="utf-8"),
        "custo") == "custa # caro"
    assert ids_de_contexto(acervo.invocar({"file_path": "deploy/x.sh"}, sessao)) == ["com-comentario"]


def test_o_modelo_do_readme_passa_na_regua(acervo, raiz):
    """O bloco de frontmatter do `docs/licoes/README.md`, salvo como lição, passa na régua."""
    readme = raiz / "docs" / "licoes" / "README.md"
    if not readme.is_file():
        pytest.skip("o kit ainda não tem docs/licoes/README.md")
    m = re.search(r"```(?:yaml|markdown)?\n(---\n.*?\n---\n.*?)```", readme.read_text(encoding="utf-8"),
                  re.S)
    assert m, "o README não traz o modelo num bloco de código que comece com ---"
    modelo = m.group(1)
    ident = acervo.regua().campo(modelo, "id")
    (acervo.raiz / "docs" / "licoes" / f"{ident}.md").write_text(modelo, encoding="utf-8")
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0, r.stdout


def ids_de_contexto(texto: str) -> list:
    return re.findall(r"^\s*-\s+\*\*([a-z0-9][a-z0-9-]+)\*\*", texto, re.M)


def test_licao_sem_frontmatter_e_recusada(acervo):
    (acervo.raiz / "docs" / "licoes" / "solta.md").write_text("# só texto\n", encoding="utf-8")
    r = acervo.rodar_regua("--gerar")
    assert r.returncode != 0 and "sem frontmatter" in r.stdout


def test_comentario_depois_de_gatilhos_e_aceito(regua):
    texto = "---\nid: x\ngatilhos:   # opcional\n  - '\\bgit\\s+push\\b'\n---\n"
    assert regua.erros_de_gatilhos("x.md", texto) == []
    assert regua.gatilhos_de(texto) == [r"\bgit\s+push\b"]


def test_regra_de_area_malformada_e_acusada(acervo):
    acervo.licao("boa")
    (acervo.raiz / "docs" / "regras-de-area.md").write_text(
        "# Regras\n\n## Regra 1 — Certa\nareas: deploy\n\nx\n\n---\n\n"
        "## Regra 2 - Com hífen comum\nareas: deploy\n\nx\n\n---\n\n"
        "## Regra 3 — Sem a linha de áreas\n\nx\n\n---\n\n"
        "## Regra 4 — Área que não existe\nareas: deploy, vendas\n\nx\n", encoding="utf-8")
    r = acervo.rodar_regua("--conferir")
    assert r.returncode != 0
    assert "Regra 2 - Com hífen comum" in r.stdout
    assert "sem a linha `areas:`" in r.stdout
    assert "area 'vendas'" in r.stdout
    assert "Regra 1" not in r.stdout


def test_sem_argumento_mostra_a_ajuda_e_nao_escreve(acervo):
    r = acervo.rodar_regua()
    assert r.returncode == 2 and "--gerar" in r.stdout
    assert not acervo.indice.exists()


# --------------------------------------------------------------- o filtro do git (opcional)


def test_licao_fora_do_git_fica_fora_do_indice_com_aviso(acervo):
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    acervo.licao("rastreada")
    acervo.licao("nova-sem-add")
    for args in (["init", "-q"], ["add", "docs/licoes/rastreada.md"]):
        subprocess.run([git, *args], cwd=acervo.raiz, check=True, capture_output=True)
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0, r.stdout + r.stderr
    indice = acervo.indice.read_text(encoding="utf-8")
    assert "  rastreada:" in indice and "nova-sem-add" not in indice
    assert "docs/licoes/nova-sem-add.md não está no git" in r.stderr


def test_gerar_recusa_o_indice_vazio_quando_nenhuma_licao_esta_no_git(acervo):
    """A instalação nova: o kit copiado, `git init`, e o `--gerar` antes do `git add`. O índice
    sairia com `total: 0` e o gancho calaria todas as lições; a régua recusa em voz alta."""
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    acervo.licao("uma")
    acervo.licao("outra")
    subprocess.run([git, "init", "-q"], cwd=acervo.raiz, check=True, capture_output=True)
    r = acervo.rodar_regua("--gerar")
    assert r.returncode != 0, r.stdout + r.stderr
    assert "RECUSADO" in r.stderr and "nenhuma está no git" in r.stderr, r.stderr
    assert "total: 0" in r.stderr, r.stderr
    assert not acervo.indice.exists(), "o --gerar recusado escreveu o índice vazio assim mesmo"
    # Depois do `git add`, o mesmo comando passa e o índice traz as duas.
    subprocess.run([git, "add", "docs/licoes"], cwd=acervo.raiz, check=True, capture_output=True)
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0, r.stdout + r.stderr
    assert acervo.indice.read_text(encoding="utf-8").rstrip().endswith("total: 2")


def test_conferir_avisa_quando_o_indice_nao_esta_no_stage(acervo):
    """O `--gerar` reescreve o índice e não o põe no stage: o `--conferir` lembra o `git add`,
    sem falhar (a árvore está certa; falta o stage)."""
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    acervo.licao("uma")
    subprocess.run([git, "init", "-q"], cwd=acervo.raiz, check=True, capture_output=True)
    subprocess.run([git, "add", "docs"], cwd=acervo.raiz, check=True, capture_output=True)
    assert acervo.rodar_regua("--gerar").returncode == 0
    subprocess.run([git, "add", ".claude/indice"], cwd=acervo.raiz, check=True, capture_output=True)
    r = acervo.rodar_regua("--conferir")
    assert r.returncode == 0 and "AVISO" not in r.stderr, r.stdout + r.stderr
    acervo.licao("duas")
    subprocess.run([git, "add", "docs"], cwd=acervo.raiz, check=True, capture_output=True)
    assert acervo.rodar_regua("--gerar").returncode == 0
    r = acervo.rodar_regua("--conferir")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "difere do que está no stage" in r.stderr and "git add .claude/indice/licoes.yaml" \
        in r.stderr, r.stderr


def test_gerar_aceita_o_indice_vazio_quando_nao_ha_licao(acervo):
    """Pasta de lições vazia, com git: `total: 0` é a verdade, não um esquecimento."""
    git = shutil.which("git")
    if not git:
        pytest.skip("sem git no PATH")
    subprocess.run([git, "init", "-q"], cwd=acervo.raiz, check=True, capture_output=True)
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0, r.stdout + r.stderr
    assert acervo.indice.read_text(encoding="utf-8").rstrip().endswith("total: 0")
