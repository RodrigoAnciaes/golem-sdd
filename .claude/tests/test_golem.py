# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""A configuração do Golem: o leitor do `golem.toml`, as receitas e o `golem.py aplicar`."""
import itertools
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import AMBIENTE, RAIZ, carregar, escrever_licao

golem = carregar("golem", RAIZ / ".claude" / "golem.py")


def escrever(raiz: Path, texto: str, nome: str = "golem.toml") -> Path:
    caminho = raiz / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto.encode("utf-8"))
    return caminho


def rodar_aplicar(raiz: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(raiz / ".claude" / "golem.py"), "aplicar"],
                          capture_output=True, text=True, encoding="utf-8", cwd=raiz,
                          env=AMBIENTE)


def erro_de(texto: str) -> str:
    with pytest.raises(golem.ErroDeConfiguracao) as e:
        golem.ler_texto(texto)
    return str(e.value)


def entre_as_marcas(texto: str) -> str:
    return texto[texto.index(golem.INICIO):texto.index(golem.FIM) + len(golem.FIM)]


# ---------------------------------------------------------------- o leitor


def test_le_texto_com_aspas_duplas_e_simples_inteiro_e_comentario():
    texto = ('# golem.toml de teste\n\nreceita = "completo"\n'
             "revisor = 'nunca'   # sem revisor\n  gancho_teto=3 # menos lições\n")
    assert golem.ler_texto(texto) == {"receita": "completo", "revisor": "nunca", "gancho_teto": 3}


def test_le_arquivo_em_crlf(tmp_path):
    escrever(tmp_path, 'receita = "so-eu"\r\nparar_a_cada_parte = "nunca"\r\n')
    c = golem.configuracao(tmp_path)
    assert c["receita"] == "so-eu" and c["parar_a_cada_parte"] == "nunca"


def test_sem_golem_toml_vale_a_economico(tmp_path):
    c = golem.configuracao(tmp_path)
    # A tabela do R3 da spec da fase 1, escrita aqui por extenso de propósito (com o
    # `agents_teto` do R3 da fase 4, e a `jogos_para_terceiros` da fase 4b, fora das receitas).
    assert c == {"receita": "economico", "revisor": "sempre", "revisor_quando": "por_fase",
                 "modelo_revisor": "sonnet", "validador": "nunca", "modelo_validador": "opus",
                 "guardiao": "nunca", "parar_a_cada_parte": "sempre", "conversas": "uma",
                 "gancho": "ligado", "gancho_teto": 2, "agents_teto": 3000,
                 "jogos_para_terceiros": "nao"}


def test_linha_vale_mais_que_a_receita(tmp_path):
    escrever(tmp_path, 'receita = "completo"\nrevisor = "perguntar"\n')
    c = golem.configuracao(tmp_path)
    assert c["revisor"] == "perguntar" and c["validador"] == "sempre" and c["gancho_teto"] == 4
    assert "Com `perguntar`, pergunte com botões" in golem.bloco(c)
    assert "Com `perguntar`" not in golem.bloco(golem.configuracao(tmp_path / "vazia"))
    # Sem Python, a skill diagnostico manda trocar à mão a linha do gancho pela que o aplicar gera.
    desligado = golem.bloco({**c, "gancho": "desligado"})
    linha = next(l for l in desligado.splitlines() if l.startswith("- **Gancho das lições:**"))
    skill = (RAIZ / ".claude" / "skills" / "diagnostico" / "SKILL.md").read_text(encoding="utf-8")
    assert linha in skill.splitlines(), linha
    # Todo bloco possível cabe no teto do R4, contado em CRLF, como o `wc -c` do validation.md o
    # conta no Windows. O teto 10 é o de dois dígitos.
    maior = 0
    for receita, (rev, val, gua), (m_rev, m_val), quando, gancho, conversas in itertools.product(
            golem.RECEITAS, itertools.product(golem.ETAPA, repeat=3),
            itertools.product(golem.MODELOS, repeat=2), golem.VALORES["revisor_quando"],
            golem.VALORES["gancho"], golem.VALORES["conversas"]):
        c = {"receita": receita, **golem.RECEITAS[receita], "revisor": rev, "validador": val,
             "guardiao": gua, "modelo_revisor": m_rev, "modelo_validador": m_val,
             "revisor_quando": quando, "gancho": gancho, "conversas": conversas,
             "gancho_teto": 10}
        maior = max(maior, len(golem.bloco(c).replace("\n", "\r\n").encode("utf-8")))
    assert maior <= 1200, maior


def test_chave_repetida_vale_a_ultima():
    assert golem.ler_texto('gancho = "desligado"\ngancho = "ligado"\n') == {"gancho": "ligado"}


def test_chave_desconhecida_falha_com_o_numero_da_linha():
    msg = erro_de('receita = "economico"\nrevisr = "nunca"\n')
    assert "golem.toml:2" in msg and "revisr" in msg and "revisor" in msg, msg


def test_valor_fora_da_tabela_falha_e_lista_os_aceitos():
    msg = erro_de('revisor = "talvez"\n')
    assert "golem.toml:1" in msg and "sempre, perguntar, nunca" in msg, msg
    assert "1 a 10" in erro_de("gancho_teto = 11\n")
    assert "1 a 10" in erro_de('gancho_teto = "2"\n')
    assert "entre aspas" in erro_de("revisor = 3\n")


def test_agents_teto_aceita_um_inteiro_e_recusa_texto_e_zero():
    assert golem.ler_texto("agents_teto = 4500\n") == {"agents_teto": 4500}
    msg = erro_de('receita = "so-eu"\nagents_teto = "muito"\n')
    assert "golem.toml:2" in msg and "1 em diante" in msg, msg
    assert "golem.toml:1" in erro_de("agents_teto = 0\n")
    assert all(r["agents_teto"] == golem.AGENTS_TETO == 3000 for r in golem.RECEITAS.values())


def test_linha_mal_formada_falha_com_o_numero_da_linha():
    msg = erro_de('# ok\nreceita = "so-eu"\ngancho = desligado\n')
    assert "golem.toml:3" in msg and "gancho = desligado" in msg, msg


# ---------------------------------------------------------------- o aplicar


def test_aplicar_escreve_o_model_dos_dois_agentes(copia_do_kit):
    agentes = copia_do_kit / ".claude" / "agents"
    # O revisor sem `model:` e em CRLF; o validador com um `model:` velho, em LF.
    revisor = (agentes / "revisor.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    revisor = "\n".join(l for l in revisor.split("\n") if not l.startswith("model:"))
    tools = next(l for l in revisor.split("\n") if l.startswith("tools: "))
    escrever(agentes, revisor.replace("\n", "\r\n"), "revisor.md")
    validador = (agentes / "validador.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    validador = "\n".join(l for l in validador.split("\n") if not l.startswith("model:"))
    escrever(agentes, validador.replace("tools: ", "model: sonnet\ntools: ", 1), "validador.md")
    escrever(copia_do_kit, 'modelo_revisor = "haiku"\n')

    assert golem.aplicar(copia_do_kit) == 0

    r = (agentes / "revisor.md").read_bytes().decode("utf-8")
    # A linha `tools:` sai inteira (com as ferramentas do Studio, fase 2) e o `model:` vem depois.
    assert f"\n{tools}\r\nmodel: haiku\r\n---\r\n" in r, r[:600]
    assert "\n" not in r.replace("\r\n", ""), "o CRLF do revisor se perdeu"
    v = (agentes / "validador.md").read_bytes().decode("utf-8")
    assert v.count("model:") == 1 and "\nmodel: opus\n---\n" in v, v[:600]
    assert "\r\n" not in v, "o LF do validador virou CRLF"


def test_aplicar_troca_so_o_que_esta_entre_as_marcas(copia_do_kit):
    antes, depois = "# Projeto\n\nTexto de antes.\n\n", "\n\n---\n\n## Depois\n\nFim.\n"
    escrever(copia_do_kit, f"{antes}{golem.INICIO}\nlixo velho\n{golem.FIM}{depois}", "AGENTS.md")
    escrever(copia_do_kit, 'receita = "so-eu"\n')
    assert golem.aplicar(copia_do_kit) == 0
    texto = (copia_do_kit / "AGENTS.md").read_text(encoding="utf-8")
    # o módulo é o do kit, que tem o manifesto: chamado com outra raiz, é o modo plugin
    esperado = golem.bloco(golem.configuracao(copia_do_kit), golem.modo_plugin(copia_do_kit))
    assert texto == antes + esperado + depois[1:], texto
    assert "lixo velho" not in texto and "Receita `so-eu`" in texto


def test_aplicar_sem_as_marcas_acrescenta_o_bloco_no_fim(copia_do_kit):
    escrever(copia_do_kit, "# Projeto\n\nAs regras dele.\n\n", "AGENTS.md")
    assert golem.aplicar(copia_do_kit) == 0
    texto = (copia_do_kit / "AGENTS.md").read_text(encoding="utf-8")
    assert texto.startswith("# Projeto\n\nAs regras dele.\n\n" + golem.INICIO), texto
    assert texto.endswith(golem.FIM + "\n") and texto.count(golem.INICIO) == 1


def test_aplicar_com_erro_nao_escreve_nada(copia_do_kit):
    arquivos = [copia_do_kit / "AGENTS.md", copia_do_kit / ".claude" / "agents" / "revisor.md",
                copia_do_kit / ".claude" / "agents" / "validador.md"]
    escrever(copia_do_kit, 'receita = "completo"\nrevisr = "nunca"\n')
    antes = [p.read_bytes() for p in arquivos]
    r = rodar_aplicar(copia_do_kit)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "golem.toml:2" in r.stdout and "revisr" in r.stdout and "Nada foi escrito" in r.stdout
    assert [p.read_bytes() for p in arquivos] == antes
    # O golem.toml certo, mas o AGENTS.md com uma marca só: os agentes também ficam como estão.
    escrever(copia_do_kit, 'receita = "completo"\n')
    escrever(copia_do_kit, f"# Projeto\n\n{golem.INICIO}\nsem a marca de fim\n", "AGENTS.md")
    antes = [p.read_bytes() for p in arquivos]
    r = rodar_aplicar(copia_do_kit)
    assert r.returncode == 1 and "fora de ordem" in r.stdout, r.stdout
    assert [p.read_bytes() for p in arquivos] == antes


def test_segunda_rodada_do_aplicar_nao_muda_nada(copia_do_kit):
    escrever(copia_do_kit, 'receita = "completo"\n')
    r = rodar_aplicar(copia_do_kit)
    assert r.returncode == 0 and "escrito  AGENTS.md" in r.stdout, r.stdout
    arquivos = [copia_do_kit / "AGENTS.md", *(copia_do_kit / ".claude" / "agents").glob("*.md")]
    antes = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in arquivos}
    r = rodar_aplicar(copia_do_kit)
    assert r.returncode == 0 and "nada mudou" in r.stdout, r.stdout
    assert {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in arquivos} == antes


@pytest.mark.parametrize("receita, trechos", [
    ("so-eu", ["Receita `so-eu`", "**Revisor:** nunca.", "**Validador:** nunca.",
               "**Guardião:** nunca.", "**Parar a cada parte:** sempre", "até 2 lições"]),
    ("economico", ["Receita `economico`", "**Revisor:** sempre, uma vez por fase",
                   "diff da fase inteira. Modelo `sonnet`.", "**Validador:** nunca.",
                   "**Guardião:** nunca.", "**Parar a cada parte:** sempre", "**Conversas:** uma",
                   "até 2 lições"]),
    ("completo", ["Receita `completo`", "**Revisor:** sempre, a cada grupo", "Modelo `opus`.",
                  "**Validador:** sempre, a cada grupo", "**Guardião:** sempre, antes do merge",
                  "**Parar a cada parte:** nunca", "os papéis de", "até 4 lições"]),
])
def test_bloco_de_cada_receita(tmp_path, receita, trechos):
    escrever(tmp_path, f'receita = "{receita}"\n')
    texto = golem.bloco(golem.configuracao(tmp_path))
    faltam = [t for t in trechos if t not in texto]
    assert not faltam, f"faltam {faltam} em:\n{texto}"
    assert "**Os comandos do `validation.md`:** sempre" in texto
    assert len(texto.encode("utf-8")) <= 1200, len(texto.encode("utf-8"))


def test_o_agents_md_e_os_agentes_batem_com_o_golem_toml():
    """O que o aplicar gera a partir do golem.toml deste projeto é o que está no disco. No kit, é a
    `completo` do golem.toml dele; o modelo que o usuário copia (`templates/AGENTS.md`), na
    `economico`, é conferido pelo test_conciliar.py."""
    divergentes = [p.relative_to(RAIZ).as_posix() for p, (texto, _) in golem.esperado(RAIZ).items()
                   if golem._ler(p)[0] != texto]
    assert not divergentes, f"rode `python3 .claude/golem.py aplicar`: {divergentes}"


def test_o_guia_traz_as_receitas_do_golem_py():
    """A tabela das receitas do docs/guia-configuracao.md é a do golem.py, célula por célula."""
    texto = (RAIZ / "docs" / "guia-configuracao.md").read_text(encoding="utf-8")
    linhas = [l for l in texto.splitlines() if l.startswith("| `")]
    tabela = {}
    for linha in linhas:
        celulas = [c.strip().strip("`") for c in linha.strip("|").split("|")]
        tabela[celulas[0]] = celulas[1:]
    receitas = list(golem.RECEITAS)
    chaves = set().union(*(golem.RECEITAS[r] for r in receitas))
    esperado = {chave: [str(golem.RECEITAS[r].get(chave)) for r in receitas] for chave in chaves}
    assert tabela == esperado
    # As colunas, na ordem do golem.py: a tabela é lida nessa ordem.
    cabecalho = next(l for l in texto.splitlines() if l.startswith("| Chave |"))
    posicoes = [cabecalho.find(f"`{r}`") for r in receitas]
    assert -1 not in posicoes and posicoes == sorted(posicoes), cabecalho


# ------------------------------------------- o modo plugin (fase 3, o Golem central)


def _golem_de(kit: Path):
    return carregar(f"golem_{abs(hash(str(kit)))}", kit / ".claude" / "golem.py")


def test_a_configuracao_do_jogo_vale_por_cima_da_do_central(plugin, monkeypatch):
    monkeypatch.setenv("GOLEM_CENTRAL", str(plugin.central))
    g = _golem_de(plugin.kit)
    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text('receita = "completo"\nrevisor = "nunca"\n',
                                               encoding="utf-8")
    c = g.configuracao(plugin.jogo)
    assert (c["receita"], c["revisor"], c["modelo_revisor"]) == ("completo", "nunca", "opus")
    (plugin.jogo / "golem.toml").write_text('revisor = "perguntar"\n', encoding="utf-8")
    assert g.configuracao(plugin.jogo)["revisor"] == "perguntar"
    (plugin.jogo / "golem.toml").write_text('receita = "so-eu"\n', encoding="utf-8")
    c = g.configuracao(plugin.jogo)
    # a receita do jogo vence a do central; a linha do central vence a receita
    assert (c["receita"], c["revisor"], c["modelo_revisor"]) == ("so-eu", "nunca", "sonnet")


def test_fora_do_modo_plugin_o_golem_toml_do_central_e_ignorado(copia_do_kit, plugin,
                                                                 monkeypatch):
    monkeypatch.setenv("GOLEM_CENTRAL", str(plugin.central))
    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text('revisor = "nunca"\n', encoding="utf-8")
    g = _golem_de(copia_do_kit)            # a cópia não tem o manifesto do plugin
    assert g.configuracao(plugin.jogo)["revisor"] == "sempre"
    assert g.configuracao(copia_do_kit)["revisor"] == "sempre"
    # o kit COM o manifesto, com a raiz nele mesmo (quem desenvolve o kit): também ignora
    assert _golem_de(plugin.kit).configuracao(plugin.kit)["revisor"] == "sempre"


def test_o_teto_do_gancho_vem_do_central_e_cai_no_padrao_com_erro(plugin, monkeypatch):
    monkeypatch.setenv("GOLEM_CENTRAL", str(plugin.central))
    g = _golem_de(plugin.kit)
    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text("gancho_teto = 3\n", encoding="utf-8")
    assert g.teto_do_gancho(plugin.jogo) == 3
    (plugin.central / "golem.toml").write_text("isto nao e toml\n", encoding="utf-8")
    assert g.teto_do_gancho(plugin.jogo) == golem.RECEITAS[golem.PADRAO]["gancho_teto"]


def test_o_aplicar_do_kit_trabalha_no_jogo_e_acusa_o_central_com_erro(plugin):
    (plugin.jogo / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")
    agentes_antes = (plugin.kit / ".claude" / "agents" / "revisor.md").read_bytes()
    r = plugin.rodar("golem.py", "aplicar")
    assert r.returncode == 0, r.stdout + r.stderr
    texto = (plugin.jogo / "AGENTS.md").read_text(encoding="utf-8")
    assert golem.INICIO in texto and 'o guia vem com o kit (peça "configurar o Golem")' in texto
    assert "docs/guia-configuracao.md" not in texto, "o guia não vai ao jogo"
    assert "o agente mora no kit, e o modelo vai na chamada" in r.stdout, r.stdout
    assert (plugin.kit / ".claude" / "agents" / "revisor.md").read_bytes() == agentes_antes
    assert (plugin.jogo / ".claude" / "indice" / "licoes.yaml").is_file()   # a régua, no fixture
    assert not (plugin.kit / ".claude" / "indice").exists()
    sobras = [p.name for p in (plugin.jogo / ".claude").rglob("*.py")]
    assert sobras == [], f"o jogo ganhou script do kit: {sobras}"

    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text("revisor = talvez\n", encoding="utf-8")
    antes = (plugin.jogo / "AGENTS.md").read_bytes()
    r = plugin.rodar("golem.py", "aplicar")
    assert r.returncode == 1 and f"{plugin.central.as_posix()}/golem.toml:1" in r.stdout, r.stdout
    assert (plugin.jogo / "AGENTS.md").read_bytes() == antes


def test_a_regua_e_o_aplicar_do_kit_fora_de_um_git_trabalham_na_pasta_corrente(plugin, tmp_path):
    solta = tmp_path / "solta"
    solta.mkdir()
    (solta / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")
    escrever_licao(solta, "licao-solta")
    antes = sorted(p.relative_to(plugin.kit).as_posix() for p in plugin.kit.rglob("*"))
    r = plugin.rodar("golem.py", "aplicar", cwd=solta)
    assert r.returncode == 0, r.stdout + r.stderr
    assert golem.INICIO in (solta / "AGENTS.md").read_text(encoding="utf-8")
    r = plugin.rodar("regua.py", "--gerar", cwd=solta)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "licao-solta" in (solta / ".claude" / "indice" / "licoes.yaml").read_text(encoding="utf-8")
    depois = sorted(p.relative_to(plugin.kit).as_posix() for p in plugin.kit.rglob("*")
                    if "__pycache__" not in p.parts)
    assert depois == [x for x in antes if "__pycache__" not in x], "o kit mudou"


def test_o_central_segue_o_golem_central_senao_o_home(monkeypatch, tmp_path):
    monkeypatch.setenv("GOLEM_CENTRAL", str(tmp_path / "c"))
    assert golem.central() == tmp_path / "c"
    monkeypatch.delenv("GOLEM_CENTRAL")
    monkeypatch.setenv("HOME", str(tmp_path / "casa"))
    assert golem.central() == tmp_path / "casa" / "Golem"
    monkeypatch.delenv("HOME")
    assert golem.central() == Path.home() / "Golem"


# ------------------------------------------- o central e o registro dos jogos (fase 3, G3)


def _git(pasta: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=pasta, capture_output=True, text=True,
                          encoding="utf-8")


def test_o_central_nasce_com_as_quatro_pecas_e_sem_claude_md(plugin):
    r = plugin.rodar("golem.py", "central")
    assert r.returncode == 0 and "4 arquivo(s) mudaram" in r.stdout, r.stdout + r.stderr
    c = plugin.central
    assert (c / "golem.toml").is_file() and (c / "jogos").is_dir()
    assert "| Jogo | Pasta | Registrado em |" in (c / "jogos.md").read_text(encoding="utf-8")
    ligado = json.loads((c / ".claude" / "settings.local.json").read_text(encoding="utf-8"))
    assert ligado == {"enabledPlugins": {"golem@golem": True}}
    assert not list(c.rglob("CLAUDE.md")), "o central não pode ter CLAUDE.md (R3 da fase 3)"
    r = plugin.rodar("golem.py", "central")
    assert r.returncode == 0 and "nada mudou" in r.stdout, r.stdout


def test_o_registrar_poe_o_jogo_no_registro_e_o_liga_uma_vez(plugin):
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "Meu Jogo")
    assert r.returncode == 0, r.stdout + r.stderr
    linhas = [l for l in (plugin.central / "jogos.md").read_text(encoding="utf-8").splitlines()
              if l.startswith("| Meu Jogo |")]
    assert len(linhas) == 1 and plugin.jogo.resolve().as_posix() in linhas[0], linhas
    ligado = json.loads((plugin.jogo / ".claude" / "settings.local.json").read_text(encoding="utf-8"))
    assert ligado["enabledPlugins"]["golem@golem"] is True
    assert not list(plugin.central.rglob("CLAUDE.md"))
    antes = (plugin.central / "jogos.md").read_bytes()
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo))
    assert r.returncode == 0 and "nada mudou" in r.stdout, r.stdout
    assert (plugin.central / "jogos.md").read_bytes() == antes


def test_o_registrar_tira_o_ligado_do_git_do_jogo(plugin, tmp_path):
    """Sem `.gitignore`, ele o cria; com um sem a linha, a acrescenta uma vez só."""
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo))
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(plugin.jogo, "check-ignore", ".claude/settings.local.json").returncode == 0

    outro = tmp_path / "outro"
    outro.mkdir()
    _git(outro, "init", "-q")
    (outro / ".gitignore").write_text("node_modules/", encoding="utf-8")   # sem \n no fim
    for _ in range(2):
        assert plugin.rodar("golem.py", "registrar", str(outro)).returncode == 0
    texto = (outro / ".gitignore").read_text(encoding="utf-8")
    assert texto.startswith("node_modules/\n") and texto.count(".claude/settings.local.json") == 1
    assert _git(outro, "check-ignore", ".claude/settings.local.json").returncode == 0


def test_um_jogo_chamado_jogo_nao_e_lido_como_o_cabecalho(plugin, tmp_path):
    pasta = tmp_path / "outros" / "Jogo"   # a "jogo" do fixture é a mesma pasta no Windows
    pasta.mkdir(parents=True)
    for _ in range(2):
        assert plugin.rodar("golem.py", "registrar", str(pasta)).returncode == 0
    texto = (plugin.central / "jogos.md").read_text(encoding="utf-8")
    assert texto.count(f"| Jogo | {pasta.resolve().as_posix()} |") == 1, texto
    (pasta / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")
    r = plugin.rodar("golem.py", "aplicar", "--todos")
    assert f"== Jogo ({pasta.resolve().as_posix()})" in r.stdout, r.stdout


def test_o_registrar_guarda_o_fim_de_linha_do_gitignore(plugin):
    (plugin.jogo / ".gitignore").write_bytes(b"node_modules/\r\n*.log\r\n")
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    bruto = (plugin.jogo / ".gitignore").read_bytes()
    assert bruto.startswith(b"node_modules/\r\n*.log\r\n") and b".claude/settings.local.json\r\n" in bruto
    assert b"\n" not in bruto.replace(b"\r\n", b""), "uma linha ficou em LF"


def test_o_registrar_guarda_as_outras_chaves_do_settings_local(plugin):
    arquivo = plugin.jogo / ".claude" / "settings.local.json"
    arquivo.parent.mkdir(exist_ok=True)
    arquivo.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]},
                                   "enabledPlugins": {"outro@mkt": False}}), encoding="utf-8")
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados["permissions"] == {"allow": ["Bash(ls)"]}
    assert dados["enabledPlugins"] == {"outro@mkt": False, "golem@golem": True}


def test_o_registrar_com_o_settings_local_quebrado_nao_escreve_nada(plugin):
    arquivo = plugin.jogo / ".claude" / "settings.local.json"
    arquivo.parent.mkdir(exist_ok=True)
    arquivo.write_text("{ quebrado", encoding="utf-8")
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo))
    assert r.returncode == 1 and "settings.local.json" in r.stdout and "Nada foi escrito" in r.stdout
    assert arquivo.read_text(encoding="utf-8") == "{ quebrado"
    assert not plugin.central.exists() and not (plugin.jogo / ".gitignore").exists()


def test_o_registrar_recusa_o_nome_com_barra_vertical(plugin):
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "um|dois")
    assert r.returncode == 1 and "`|`" in r.stdout, r.stdout
    assert not plugin.central.exists()


def test_o_aplicar_todos_passa_em_cada_jogo_e_segue_sem_o_que_sumiu(plugin, tmp_path):
    jogos = []
    for nome in ("a", "sumiu", "b"):
        pasta = tmp_path / f"jogo-{nome}"
        pasta.mkdir()
        (pasta / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")
        assert plugin.rodar("golem.py", "registrar", str(pasta)).returncode == 0
        jogos.append(pasta)
    shutil.rmtree(jogos[1])
    (plugin.central / "golem.toml").write_text('revisor = "nunca"\n', encoding="utf-8")
    r = plugin.rodar("golem.py", "aplicar", "--todos")
    assert r.returncode == 0, r.stdout + r.stderr
    for pasta in (jogos[0], jogos[2]):      # o de depois do sumido também
        assert "- **Revisor:** nunca." in (pasta / "AGENTS.md").read_text(encoding="utf-8")
    assert "pulado   jogo-sumiu" in r.stdout, r.stdout


def test_o_onde_diz_o_modo_e_de_onde_vem_cada_linha(plugin, copia_do_kit):
    plugin.central.mkdir()
    (plugin.central / "golem.toml").write_text('revisor = "nunca"\n', encoding="utf-8")
    (plugin.jogo / "golem.toml").write_text('validador = "sempre"\n', encoding="utf-8")
    r = plugin.rodar("golem.py", "onde")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "modo     plugin" in r.stdout and plugin.central.as_posix() in r.stdout
    assert "revisor: nunca (do central)" in r.stdout
    assert "validador: sempre (deste projeto)" in r.stdout
    assert "guardiao: nunca (da receita)" in r.stdout
    r = subprocess.run([sys.executable, str(copia_do_kit / ".claude" / "golem.py"), "onde"],
                       capture_output=True, text=True, encoding="utf-8", cwd=copia_do_kit,
                       env=plugin.env)
    assert "modo     cópia" in r.stdout and "revisor: sempre (da receita)" in r.stdout, r.stdout


# ------------------------------------------- a marca de terceiros e o subir (fase 4b)


def _registro(plugin) -> str:
    return (plugin.central / "jogos.md").read_text(encoding="utf-8")


def _versao(pasta: Path, ident: str, refs=("x",), corpo: str = "") -> Path:
    """A versão geral de uma lição, numa pasta fora do jogo (como a `licao` a grava)."""
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / f"{ident}.md"
    arq.write_text(
        f"---\nid: {ident}\ndata: 2026-01-01\narea: processo\ntipo: armadilha\n"
        f'custo: "x"\ngatilho: "x"\ngatilhos:\n  - \'\\bcomando-geral\\b\'\nrefs:\n'
        + "".join(f"  - {r}\n" for r in refs)
        + f"---\n\n**O que se achava:** x.\n\n**O que é:** y.{corpo}\n\n"
        f"**Como perceber da próxima vez:** sinal de {ident}.\n", encoding="utf-8")
    return arq


def test_o_cabecalho_novo_tem_a_coluna_para_terceiros(plugin):
    assert plugin.rodar("golem.py", "central").returncode == 0
    assert "| Jogo | Pasta | Registrado em | Para terceiros |\n|---|---|---|---|\n" in _registro(plugin)


def test_o_registro_de_tres_colunas_e_lido_e_passa_a_quatro(plugin, tmp_path):
    plugin.central.mkdir()
    velho = tmp_path / "velho"
    velho.mkdir()
    (plugin.central / "jogos.md").write_text(
        "# Os jogos do Golem\n\n| Jogo | Pasta | Registrado em |\n|---|---|---|\n"
        f"| Velho | {velho.resolve().as_posix()} | 2026-11-21 |\n", encoding="utf-8")
    g = carregar("golem_registro", plugin.kit / ".claude" / "golem.py")
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOLEM_CENTRAL", str(plugin.central))
        assert g.ler_registro() == [("Velho", velho.resolve().as_posix(), "2026-11-21", "não")]
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "Novo").returncode == 0
    texto = _registro(plugin)
    assert "| Jogo | Pasta | Registrado em | Para terceiros |\n|---|---|---|---|\n" in texto
    assert f"| Velho | {velho.resolve().as_posix()} | 2026-11-21 | não |" in texto
    assert f"| Novo | {plugin.jogo.resolve().as_posix()} |" in texto and texto.endswith(" | não |\n")
    assert "| Registrado em |\n" not in texto


def test_o_registrar_com_terceiros_marca_e_sem_ele_nao_desmarca(plugin):
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "A").returncode == 0
    assert _registro(plugin).count(" | não |") == 1
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--terceiros")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _registro(plugin).count(" | sim |") == 1 and " | não |" not in _registro(plugin)
    antes = _registro(plugin)
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo))
    assert r.returncode == 0 and "nada mudou" in r.stdout, r.stdout
    assert _registro(plugin) == antes
    assert _registro(plugin).count(plugin.jogo.resolve().as_posix()) == 1


def test_a_chave_jogos_para_terceiros(plugin, tmp_path):
    g = carregar("golem_chave", plugin.kit / ".claude" / "golem.py")
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOLEM_CENTRAL", str(plugin.central))
        assert g.configuracao(plugin.jogo)["jogos_para_terceiros"] == "nao"
        escrever(plugin.central, 'jogos_para_terceiros = "sim"\n')
        assert g.configuracao(plugin.jogo)["jogos_para_terceiros"] == "sim"
        escrever(plugin.central, 'jogos_para_terceiros = "talvez"\n')
        with pytest.raises(g.ErroDeConfiguracao, match="jogos_para_terceiros"):
            g.configuracao(plugin.jogo)


def test_o_onde_diz_se_o_jogo_e_para_terceiros(plugin, tmp_path):
    r = plugin.rodar("golem.py", "onde")
    assert "para terceiros: fora do registro" in r.stdout, r.stdout
    assert "jogos_para_terceiros: nao (o padrão)" in r.stdout, r.stdout
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    assert "para terceiros: não" in plugin.rodar("golem.py", "onde").stdout
    outro = tmp_path / "estudio"
    outro.mkdir()
    assert plugin.rodar("golem.py", "registrar", str(outro), "--terceiros").returncode == 0
    r = plugin.rodar("golem.py", "onde", cwd=outro)
    assert "para terceiros: sim" in r.stdout and "cliente" not in r.stdout.lower(), r.stdout


@pytest.fixture
def registrado(plugin):
    """O jogo do `Plugin`, registrado com o nome `Moedas Turbo`, que não é para terceiros, com a
    lição `geral-a` no acervo dele (a subida copia uma lição do jogo)."""
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "Moedas Turbo")
    assert r.returncode == 0, r.stdout + r.stderr
    escrever_licao(plugin.jogo, "geral-a", r"'\bcomando-geral\b'")
    return plugin


def _estado(plugin) -> dict:
    if not plugin.central.is_dir():
        return {}
    return {p.relative_to(plugin.central).as_posix(): p.read_bytes()
            for p in plugin.central.rglob("*") if p.is_file()}


def _recusa(plugin, arq: Path, *extra, motivo: str = "") -> None:
    """O `subir` sai com ERRO e o motivo, e nada muda no central."""
    antes = _estado(plugin)
    r = plugin.rodar("golem.py", "subir", str(arq), *extra)
    assert r.returncode == 1 and "ERRO" in r.stdout and "Nada foi escrito" in r.stdout, \
        r.stdout + r.stderr
    assert motivo in r.stdout, r.stdout
    assert _estado(plugin) == antes


def test_o_subir_recusa_fora_do_modo_plugin(registrado, tmp_path):
    (registrado.kit / ".claude-plugin" / "plugin.json").unlink()
    _recusa(registrado, _versao(tmp_path / "v", "geral-a"), motivo="modo plugin")


def test_o_subir_recusa_fora_do_registro(plugin, tmp_path):
    _recusa(plugin, _versao(tmp_path / "v", "geral-a"), motivo="registro")


def test_o_subir_recusa_no_jogo_para_terceiros(plugin, tmp_path):
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--terceiros").returncode == 0
    _recusa(plugin, _versao(tmp_path / "v", "geral-a"), motivo="para terceiros")
    r = plugin.rodar("golem.py", "subir", str(_versao(tmp_path / "v", "geral-a")))
    assert "cliente" not in r.stdout.lower(), r.stdout


def test_o_registrar_com_nome_e_terceiros_juntos(plugin):
    r = plugin.rodar("golem.py", "registrar", str(plugin.jogo), "--nome", "Do Estudio",
                     "--terceiros")
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"| Do Estudio | {plugin.jogo.resolve().as_posix()} |" in _registro(plugin)
    assert _registro(plugin).rstrip().endswith("| sim |")


def test_a_marca_escrita_a_mao_que_nao_e_nao_vale_sim(plugin):
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    arq = plugin.central / "jogos.md"
    arq.write_text(arq.read_text(encoding="utf-8").replace("| não |", "| x |"), encoding="utf-8")
    assert "para terceiros: sim" in plugin.rodar("golem.py", "onde").stdout
    assert plugin.rodar("golem.py", "registrar", str(plugin.jogo)).returncode == 0
    assert _registro(plugin).rstrip().endswith("| sim |")


def test_a_chave_de_terceiros_no_golem_toml_do_jogo_e_erro(plugin):
    escrever(plugin.jogo, 'jogos_para_terceiros = "nao"\n')
    r = plugin.rodar("golem.py", "onde")
    assert r.returncode == 1 and "só vale no golem.toml do Golem central" in r.stdout, r.stdout
    # Na sessão aberta no próprio central, o golem.toml da raiz é o do central: vale.
    escrever(plugin.central, 'jogos_para_terceiros = "sim"\n')
    r = plugin.rodar("golem.py", "onde", cwd=plugin.central)
    assert r.returncode == 0 and "jogos_para_terceiros: sim" in r.stdout, r.stdout


@pytest.mark.parametrize("corpo, refs, motivo", [
    (" Visto no MOEDAS TURBO.", ("x",), "Moedas Turbo"),
    (" Visto em JOGO, a pasta.", ("x",), "'jogo'"),
    ("", ("x",), "a pasta do jogo"),
    ("", ("'src/moedas.lua:3 `local x`'",), "src/moedas.lua"),
    ("", ("game.ServerScriptService.Moedas",), "script do place"),
])
def test_o_subir_recusa_o_que_cita_o_projeto(registrado, tmp_path, corpo, refs, motivo):
    (registrado.jogo / "src").mkdir()
    (registrado.jogo / "src" / "moedas.lua").write_text("a\nb\nlocal x\n", encoding="utf-8")
    if motivo == "a pasta do jogo":
        corpo = f" Rodado em {registrado.jogo.resolve().as_posix().upper()}."
    _recusa(registrado, _versao(tmp_path / "v", "geral-a", refs, corpo), motivo=motivo)


def test_o_subir_recusa_o_frontmatter_que_a_regua_recusa(registrado, tmp_path):
    arq = _versao(tmp_path / "v", "geral-a")
    arq.write_text(arq.read_text(encoding="utf-8").replace("area: processo", "area: nenhuma"),
                   encoding="utf-8")
    _recusa(registrado, arq, motivo="a régua recusa")
    assert "area" in registrado.rodar("golem.py", "subir", str(arq)).stdout


def test_o_subir_recusa_as_bordas_da_entrada(registrado, tmp_path):
    _recusa(registrado, tmp_path / "v" / "nao-existe.md", motivo="não existe")
    _recusa(registrado, _versao(tmp_path / "r", "README"), motivo="não é uma lição")
    _recusa(registrado, _versao(tmp_path / "v", "so-fora-do-jogo"), motivo="não existe")
    latin = _versao(tmp_path / "v", "geral-a")
    latin.write_bytes(latin.read_bytes() + "ação".encode("latin-1"))
    _recusa(registrado, latin, motivo="UTF-8")


def test_a_regua_que_falha_no_central_desfaz_a_escrita(registrado, tmp_path):
    """O central no git, sem nenhuma lição rastreada: a régua recusa o índice, e o subir desfaz."""
    registrado.central.mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=registrado.central, check=True, capture_output=True)
    _recusa(registrado, _versao(tmp_path / "v", "geral-a"), motivo="não regerou")
    assert not (registrado.central / "docs").exists(), "a pasta criada agora sai com a lição"
    r = registrado.rodar("golem.py", "subir", str(_versao(tmp_path / "v", "geral-a")))
    assert "git add" in r.stdout and "--substituir" in r.stdout, r.stdout


def test_o_subir_repassa_o_aviso_da_regua_do_central(registrado, tmp_path):
    """O central no git com uma lição rastreada: a nova fica fora do índice, e o subir o diz."""
    escrever_licao(registrado.central, "geral-velha", r"'\boutro\b'")
    subprocess.run(["git", "init", "-q"], cwd=registrado.central, check=True, capture_output=True)
    subprocess.run(["git", "add", "docs"], cwd=registrado.central, check=True, capture_output=True)
    r = registrado.rodar("golem.py", "subir", str(_versao(tmp_path / "v", "geral-a")))
    aviso = [l for l in r.stdout.splitlines() if "AVISO" in l]
    assert r.returncode == 0 and aviso, r.stdout + r.stderr
    assert "geral-a.md não está no git" in aviso[0], aviso


def test_o_subir_escreve_no_geral_e_a_licao_do_jogo_fica_igual(registrado, tmp_path):
    do_jogo = registrado.jogo / "docs" / "licoes" / "geral-a.md"
    bruto = do_jogo.read_bytes()
    # O mesmo caminho no jogo e no kit: a ref ao arquivo do kit passa (a exceção do kit).
    (registrado.jogo / ".claude" / "golem.py").write_text("# Golem SDD\n", encoding="utf-8")
    arq = _versao(tmp_path / "v", "geral-a",
                  ("'.claude/golem.py:1 `Golem SDD`'", "a conversa da fase 4b"))
    r = registrado.rodar("golem.py", "subir", str(arq))
    assert r.returncode == 0, r.stdout + r.stderr
    destino = registrado.central / "docs" / "licoes" / "geral-a.md"
    assert destino.read_bytes() == arq.read_bytes() and do_jogo.read_bytes() == bruto
    indice = (registrado.central / ".claude" / "indice" / "licoes.yaml").read_text(encoding="utf-8")
    assert "  geral-a:" in indice and "total: 1" in indice
    for caminho in (destino, registrado.central / ".claude" / "indice" / "licoes.yaml",
                    registrado.central / ".claude" / "indice" / "subidas.txt"):
        assert f"escrito  {caminho.as_posix()}" in r.stdout, r.stdout
    # A própria versão geral, subida de novo sem o --substituir (o caminho da divergência): passa.
    r = registrado.rodar("golem.py", "subir", str(destino))
    assert r.returncode == 0, r.stdout + r.stderr
    g = carregar("golem_subidas", registrado.kit / ".claude" / "golem.py")
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("GOLEM_CENTRAL", str(registrado.central))
        assert g.ler_subidas() == {"geral-a": (g.impressao(do_jogo), g.impressao(destino))}
    # De novo, sem o --substituir: recusa; com ele, troca a linha, sem duplicar.
    _recusa(registrado, arq, motivo="--substituir")
    arq.write_text(arq.read_text(encoding="utf-8") + "\nMais evidência.\n", encoding="utf-8")
    r = registrado.rodar("golem.py", "subir", str(arq), "--substituir")
    assert r.returncode == 0, r.stdout + r.stderr
    subidas = (registrado.central / ".claude" / "indice" / "subidas.txt").read_text(encoding="utf-8")
    assert subidas.count("geral-a ") == 1 and g.impressao(destino) in subidas
    assert "Mais evidência." in destino.read_text(encoding="utf-8")


def test_a_licao_subida_chega_pelo_gancho_em_outro_jogo(registrado, tmp_path):
    arq = _versao(tmp_path / "v", "geral-a")
    assert registrado.rodar("golem.py", "subir", str(arq)).returncode == 0
    outro = tmp_path / "outro-jogo"
    outro.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=outro, check=True, capture_output=True)
    escrever_licao(outro, "licao-do-outro")
    subprocess.run(["git", "add", "docs"], cwd=outro, check=True, capture_output=True)
    assert registrado.rodar("regua.py", "--gerar", cwd=outro).returncode == 0
    assert registrado.rodar("golem.py", "registrar", str(outro)).returncode == 0
    payload = json.dumps({"session_id": "s", "tool_input": {"command": "comando-geral"},
                          "scratchpad_dir": str(tmp_path / "sessao")})
    r = subprocess.run([sys.executable, str(registrado.kit / ".claude" / "hooks" /
                                            "licoes_relevantes.py")],
                       input=payload, capture_output=True, text=True, encoding="utf-8",
                       env={**registrado.env, "CLAUDE_PROJECT_DIR": str(outro)})
    assert r.returncode == 0, r.stderr
    texto = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "Lições do acervo geral" in texto and "**geral-a**" in texto, texto
