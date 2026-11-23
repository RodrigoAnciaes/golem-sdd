# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""A régua: gera o índice, confere que ele não envelheceu, e RECUSA a lição que não consegue ler."""
import re
import shutil
import subprocess
import sys

import pytest

from conftest import AMBIENTE, RAIZ, carregar, escrever_licao


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
    """O motivo de o `--conferir` existir: o índice que envelhece entrega a lição velha."""
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


# --------------------------------------------------------------- as refs das lições (fase 4, D2)

ALVO = "linha um\nlinha dois\nlinha tres\nlinha dois de novo\n"


def _com_refs(acervo, ident: str, refs: list) -> None:
    """Uma lição com as `refs:` dadas (os itens já com as aspas), e o arquivo `alvo.py` citado."""
    (acervo.raiz / "alvo.py").write_text(ALVO, encoding="utf-8")
    arq = acervo.licao(ident)
    texto = arq.read_text(encoding="utf-8")
    arq.write_text(texto.replace("refs:\n  - x\n", "refs:\n" + "".join(f"  - {r}\n" for r in refs)),
                   encoding="utf-8")


@pytest.mark.parametrize("item, esperado", [
    ("nao-existe.py:3 `x`", "o arquivo não existe"),
    ("alvo.py:99", "a linha 99 não existe"),
    ("alvo.py:2", "linha sem âncora"),
    ("alvo.py:2 `nada disso`", "a âncora `nada disso` não está no arquivo"),
    ("alvo.py `nada disso`", "a âncora `nada disso` não está no arquivo"),
    ("alvo.py:1 `linha tres`", "a âncora `linha tres` está agora na :3"),
    # Mais de uma linha com a âncora: a primeira depois da citada; sem ela, a primeira do arquivo.
    ("alvo.py:3 `linha dois`", "a âncora `linha dois` está agora na :4"),
    ("alvo.py:4-4 `linha um`", "a âncora `linha um` está agora na :1"),
    # O caminho seguido de dois pontos, ponto ou `#` também se confere (não é prosa).
    ("nao-existe.py: a descrição", "o arquivo não existe"),
    ("alvo.py:2: a descrição", "linha sem âncora"),
    ("alvo.py:99.", "a linha 99 não existe"),
    ("nao-existe.md#secao", "o arquivo não existe"),
])
def test_a_ref_que_nao_bate_da_o_aviso(acervo, item, esperado):
    _com_refs(acervo, "com-ref", [f"'{item}'"])
    problemas = acervo.regua().problemas_de_refs()
    assert len(problemas) == 1 and esperado in problemas[0], problemas
    assert problemas[0].startswith("com-ref: a ref "), problemas


@pytest.mark.parametrize("item", [
    "alvo.py:2 `linha dois` (a descrição)",
    "alvo.py:1-3 `linha tres`",
    "alvo.py `linha um`",
    "alvo.py, a descrição sem linha",
    "a correção do usuário, 2026-11-21: «alvo.py:99»",
    "pytest: -q diminui a verbosidade",
    "game.ServerStorage.Moedas (o script do place)",
])
def test_a_ref_em_dia_e_a_prosa_nao_dao_aviso(acervo, item):
    _com_refs(acervo, "com-ref", [f"'{item}'"])
    assert acervo.regua().problemas_de_refs() == []


def test_a_ref_entre_aspas_que_nao_se_le_da_o_aviso(acervo):
    """A aspa simples da âncora sem dobrar: o leitor não lê o item, e a régua avisa em vez de pular."""
    _com_refs(acervo, "com-ref", ["'alvo.py:1 `print('oi')`'", "'alvo.py:1 `print(''oi'')`'"])
    problemas = acervo.regua().problemas_de_refs()
    assert any("com-ref: uma ref entre aspas que não se lê" in p for p in problemas), problemas
    assert any("`print('oi')` não está no arquivo" in p for p in problemas), problemas


def test_o_aviso_de_ref_nao_muda_o_codigo_de_saida(acervo):
    _com_refs(acervo, "com-ref", ["'alvo.py:1 `linha tres`'"])
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0 and "AVISO    com-ref: a ref alvo.py:1:" in r.stderr, r.stderr
    r = acervo.rodar_regua("--conferir")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "está agora na :3" in r.stderr and "ok       .claude/indice/licoes.yaml" in r.stdout


def test_as_refs_das_licoes_do_kit_estao_em_dia(regua):
    """No kit, sem folga: quem muda um arquivo citado por uma lição, muda a ref junto. Estrito: o
    arquivo ausente conta também nas lições do kit."""
    assert regua.problemas_de_refs(estrito=True) == []


def test_toda_licao_do_kit_traz_a_origem_kit(regua):
    """A marca que cala o arquivo ausente na cópia do jogo. Lição nova no kit leva `origem: kit`."""
    sem = [a.name for a in regua.arquivos_de_licao(todos=True)
           if regua.campo(regua.ler(a), "origem") != "kit"]
    assert sem == [], f"ponha `origem: kit` no frontmatter (logo abaixo do `tipo:`): {sem}"


def test_na_licao_do_kit_o_arquivo_ausente_cala_e_a_linha_mudada_avisa(acervo):
    _com_refs(acervo, "do-kit", ["'nao-existe.py:3 `x`'", "'alvo.py:1 `linha tres`'"])
    arq = acervo.raiz / "docs" / "licoes" / "do-kit.md"
    arq.write_text(arq.read_text(encoding="utf-8").replace("tipo: armadilha\n",
                                                           "tipo: armadilha\norigem: kit\n"),
                   encoding="utf-8")
    regua = acervo.regua()
    problemas = regua.problemas_de_refs()
    assert len(problemas) == 1 and "está agora na :3" in problemas[0], problemas
    assert any("o arquivo não existe" in p for p in regua.problemas_de_refs(estrito=True))


def test_a_copia_do_kit_nasce_sem_aviso_de_ref(copia_do_kit):
    """A instalação por cópia leva as lições do kit, e não os testes nem as specs que elas citam."""
    assert not (copia_do_kit / "specs").exists() and not (copia_do_kit / ".claude" / "tests").exists()
    r = rodar(copia_do_kit, "--conferir")
    assert r.returncode == 0 and "a ref" not in r.stderr, r.stderr


def test_no_plugin_a_ref_a_um_arquivo_do_kit_nao_da_aviso(plugin):
    """As lições do kit chegam ao jogo pela cópia e citam arquivos que só existem no kit."""
    licao = plugin.jogo / "docs" / "licoes" / "licao-do-jogo.md"
    texto = licao.read_text(encoding="utf-8").replace(
        "refs:\n  - x\n", "refs:\n  - '.claude/golem.py `def teto_do_agents`'\n"
                         "  - '.claude/so-no-jogo.py'\n")
    licao.write_text(texto, encoding="utf-8")
    r = plugin.rodar("regua.py", "--conferir")
    assert ".claude/golem.py" not in r.stderr, r.stderr
    assert "so-no-jogo.py: o arquivo não existe" in r.stderr, r.stderr


# --------------------------------------------------------------- o teto do AGENTS.md (fase 4, D3)


def _agents(acervo, palavras: int) -> None:
    (acervo.raiz / "AGENTS.md").write_text(" ".join(["palavra"] * palavras) + "\n",
                                           encoding="utf-8")


def test_o_agents_acima_do_teto_da_o_aviso_e_abaixo_nao(acervo):
    _agents(acervo, 3000)
    assert acervo.regua().aviso_do_teto() is None
    _agents(acervo, 3001)
    aviso = acervo.regua().aviso_do_teto()
    assert "3001 palavras" in aviso and "teto de 3000" in aviso, aviso
    assert "docs/regras-de-area.md" in aviso and "agents_teto" in aviso, aviso
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0 and "AVISO    AGENTS.md tem 3001 palavras" in r.stderr, r.stderr
    r = acervo.rodar_regua("--conferir")
    assert r.returncode == 0 and "AVISO    AGENTS.md tem 3001 palavras" in r.stderr, r.stderr


def test_no_plugin_o_teto_do_central_vale_e_o_do_jogo_vence(plugin):
    (plugin.jogo / "AGENTS.md").write_text(" ".join(["palavra"] * 11) + "\n", encoding="utf-8")
    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text("agents_teto = 10\n", encoding="utf-8")
    r = plugin.rodar("regua.py", "--conferir")
    assert "AGENTS.md tem 11 palavras, acima do teto de 10" in r.stderr, r.stderr
    (plugin.jogo / "golem.toml").write_text("agents_teto = 20\n", encoding="utf-8")
    r = plugin.rodar("regua.py", "--conferir")
    assert "AGENTS.md tem" not in r.stderr, r.stderr


def test_o_teto_vem_da_linha_agents_teto(acervo):
    _agents(acervo, 3001)
    (acervo.raiz / "golem.toml").write_text("agents_teto = 4000\n", encoding="utf-8")
    assert acervo.regua().aviso_do_teto() is None
    # O golem.toml com erro: o teto padrão, e quem acusa o erro é o aplicar.
    (acervo.raiz / "golem.toml").write_text('agents_teto = "muito"\n', encoding="utf-8")
    assert "teto de 3000" in acervo.regua().aviso_do_teto()


@pytest.mark.parametrize("quebra", ["sem", "sintaxe"])
def test_sem_o_golem_py_o_teto_e_o_padrao(acervo, quebra):
    """Sem o golem.py, ou com ele sem carregar, a régua usa os 3.000 e não cai."""
    _agents(acervo, 3001)
    (acervo.raiz / "golem.toml").write_text("agents_teto = 5000\n", encoding="utf-8")
    golem = acervo.raiz / ".claude" / "golem.py"
    if quebra == "sem":
        golem.unlink()
    else:
        golem.write_text("isto nao e python (\n", encoding="utf-8")
    assert "teto de 3000" in acervo.regua().aviso_do_teto()
    r = acervo.rodar_regua("--gerar")
    assert r.returncode == 0 and "teto de 3000" in r.stderr, r.stdout + r.stderr


def test_sem_agents_nao_ha_aviso_do_teto(acervo):
    assert acervo.regua().aviso_do_teto() is None


def test_o_teto_padrao_da_regua_e_o_do_golem(regua):
    golem = carregar("golem_do_teto", RAIZ / ".claude" / "golem.py")
    assert regua.AGENTS_TETO_PADRAO == golem.AGENTS_TETO


def test_o_modelo_do_agents_cabe_no_teto_padrao(regua):
    """O jogo não nasce com o aviso: o modelo que ele copia fica abaixo do teto."""
    palavras = len((RAIZ / "templates" / "AGENTS.md").read_text(encoding="utf-8").split())
    assert palavras <= regua.AGENTS_TETO_PADRAO, palavras
    assert regua.aviso_do_teto() is None, "o AGENTS.md do kit passou do teto"


def test_no_central_sem_git_a_regua_indexa_o_disco(plugin):
    """O acervo geral (fase 4b): a régua do kit, com a pasta corrente no central, que não é git,
    gera o índice do central com as lições do disco, e o `--conferir` passa."""
    escrever_licao(plugin.central, "licao-geral", r"'\bcomando-geral\b'")
    r = plugin.rodar("regua.py", "--gerar", cwd=plugin.central)
    assert r.returncode == 0, r.stdout + r.stderr
    indice = (plugin.central / ".claude" / "indice" / "licoes.yaml").read_text(encoding="utf-8")
    assert "  licao-geral:" in indice and "total: 1" in indice
    assert not (plugin.jogo / ".claude" / "indice" / "licoes.yaml").read_text(
        encoding="utf-8").count("licao-geral"), "o índice do jogo não muda"
    r = plugin.rodar("regua.py", "--conferir", cwd=plugin.central)
    assert r.returncode == 0, r.stdout + r.stderr


# ------------------------------------------- a divergência com o acervo geral (fase 4b)

DIVERGIU = "desde a subida ao acervo geral"


def _subido(plugin):
    """O jogo do `Plugin` registrado, com a lição `geral-a` no git e subida ao acervo geral."""
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    licao = escrever_licao(plugin.jogo, "geral-a", r"'\bcomando-geral\b'")
    subprocess.run(["git", "add", "docs"], cwd=plugin.jogo, check=True, capture_output=True)
    assert plugin.rodar("regua.py", "--gerar").returncode == 0
    r = plugin.rodar("golem.py", "subir", str(licao))
    assert r.returncode == 0, r.stdout + r.stderr
    return licao, plugin.central / "docs" / "licoes" / "geral-a.md"


def test_logo_depois_da_subida_a_regua_nao_avisa(plugin):
    _subido(plugin)
    r = plugin.rodar("regua.py", "--conferir")
    assert r.returncode == 0 and DIVERGIU not in r.stderr, r.stdout + r.stderr


def test_a_licao_do_jogo_mudada_sai_no_aviso_e_a_regua_sai_0(plugin):
    licao, geral = _subido(plugin)
    licao.write_text(licao.read_text(encoding="utf-8") + "\nEvidência nova.\n", encoding="utf-8")
    r = plugin.rodar("regua.py", "--conferir")
    assert r.returncode == 0, r.stdout + r.stderr
    aviso = [l for l in r.stderr.splitlines() if DIVERGIU in l]
    assert len(aviso) == 1 and "AVISO" in aviso[0] and "a lição deste jogo mudou" in aviso[0]
    assert "docs/licoes/geral-a.md" in aviso[0] and geral.as_posix() in aviso[0]
    assert "--substituir" in aviso[0]
    # Subir de novo, com o --substituir, renova a conferência: o aviso some.
    r = plugin.rodar("golem.py", "subir", str(licao), "--substituir")
    assert r.returncode == 0, r.stdout + r.stderr
    r = plugin.rodar("regua.py", "--conferir")
    assert r.returncode == 0 and DIVERGIU not in r.stderr, r.stdout + r.stderr


def test_a_versao_geral_mudada_ou_apagada_sai_no_aviso(plugin):
    _licao, geral = _subido(plugin)
    geral.write_text(geral.read_text(encoding="utf-8") + "\nMudada à mão.\n", encoding="utf-8")
    assert "a versão geral mudou" in plugin.rodar("regua.py", "--conferir").stderr
    geral.unlink()
    assert "a versão geral sumiu" in plugin.rodar("regua.py", "--conferir").stderr


def test_so_o_fim_de_linha_trocado_nao_avisa(plugin):
    licao, _geral = _subido(plugin)
    bruto = licao.read_bytes()
    em_lf = bruto.replace(b"\r\n", b"\n")
    # O outro fim de linha (o Windows grava o texto em CRLF; noutro sistema, em LF).
    licao.write_bytes(em_lf.replace(b"\n", b"\r\n") if bruto == em_lf else em_lf)
    assert licao.read_bytes() != bruto
    r = plugin.rodar("regua.py", "--conferir")
    assert r.returncode == 0 and DIVERGIU not in r.stderr, r.stdout + r.stderr


def test_fora_do_modo_plugin_a_divergencia_nao_conta(plugin, copia_do_kit):
    """A instalação por cópia, com o `GOLEM_CENTRAL` no ambiente e um `subidas.txt` que não bate
    com a lição dela: nenhum aviso de divergência."""
    _subido(plugin)
    escrever_licao(copia_do_kit, "geral-a", r"'\boutra-coisa\b'")
    r = subprocess.run([sys.executable, str(copia_do_kit / ".claude" / "regua.py"), "--gerar"],
                       capture_output=True, text=True, encoding="utf-8", cwd=copia_do_kit,
                       env=plugin.env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert DIVERGIU not in r.stderr, r.stderr


def test_no_proprio_kit_com_o_manifesto_a_divergencia_nao_conta(plugin):
    """O repositório do kit tem o manifesto, mas a raiz é o próprio kit: não é o modo plugin, e o
    `subidas.txt` do central do ambiente não conta, mesmo citando uma lição do kit."""
    indice = plugin.central / ".claude" / "indice"
    indice.mkdir(parents=True)
    (indice / "subidas.txt").write_text(
        f"licao-do-kit {'0' * 64} {'1' * 64} {plugin.kit.resolve().as_posix()}\n", encoding="utf-8")
    r = plugin.rodar("regua.py", "--gerar", cwd=plugin.kit)
    assert r.returncode == 0 and DIVERGIU not in r.stderr, r.stdout + r.stderr


def test_dois_jogos_com_o_mesmo_id_nao_se_atropelam(plugin, tmp_path):
    """Do guardião: o jogo B sobe a mesma lição geral (o passo 1 da `licao`), com --substituir. O
    jogo A vê a verdade, "a versão geral mudou", e não um aviso falso sobre a lição dele; subindo a
    versão geral de hoje, os dois ficam em dia."""
    _licao_a, geral = _subido(plugin)
    outro = tmp_path / "jogo-b"
    outro.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=outro, check=True, capture_output=True)
    licao_b = escrever_licao(outro, "geral-a", r"'\bcomando-geral\b'")
    licao_b.write_text(licao_b.read_text(encoding="utf-8") + "\nEvidência de um segundo caso.\n",
                       encoding="utf-8")
    subprocess.run(["git", "add", "docs"], cwd=outro, check=True, capture_output=True)
    assert plugin.rodar("regua.py", "--gerar", cwd=outro).returncode == 0
    assert plugin.rodar("golem.py", "registrar", str(outro)).returncode == 0
    r = plugin.rodar("golem.py", "subir", str(licao_b), "--substituir", cwd=outro)
    assert r.returncode == 0, r.stdout + r.stderr
    no_a = plugin.rodar("regua.py", "--conferir").stderr
    assert "a versão geral mudou" in no_a and "a lição deste jogo mudou" not in no_a, no_a
    assert DIVERGIU not in plugin.rodar("regua.py", "--conferir", cwd=outro).stderr
    r = plugin.rodar("golem.py", "subir", str(geral))
    assert r.returncode == 0, r.stdout + r.stderr
    assert DIVERGIU not in plugin.rodar("regua.py", "--conferir").stderr
    assert DIVERGIU not in plugin.rodar("regua.py", "--conferir", cwd=outro).stderr


def _reescrita(plugin, tmp_path, ident: str = "geral-a"):
    """Uma versão geral reescrita (outro texto que o da lição do jogo), subida com --substituir:
    o caso real, em que a versão geral sai sem nada do projeto."""
    versao = tmp_path / "versao" / f"{ident}.md"
    versao.parent.mkdir(exist_ok=True)
    texto = (plugin.jogo / "docs" / "licoes" / f"{ident}.md").read_text(encoding="utf-8")
    versao.write_text(texto.replace("sinal de", "sinal reescrito de"), encoding="utf-8")
    r = plugin.rodar("golem.py", "subir", str(versao), "--substituir")
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_sessao_no_proprio_central_nao_avisa_a_divergencia(plugin, tmp_path):
    """No central, as lições são as versões gerais: comparar com as do jogo daria aviso falso."""
    _subido(plugin)
    _reescrita(plugin, tmp_path)
    assert DIVERGIU not in plugin.rodar("regua.py", "--conferir").stderr, "no jogo, em dia"
    r = plugin.rodar("regua.py", "--conferir", cwd=plugin.central)
    assert r.returncode == 0 and DIVERGIU not in r.stderr, r.stdout + r.stderr
