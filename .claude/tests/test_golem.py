# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""A configuração do Golem: o leitor do `golem.toml`, as receitas e o `golem.py aplicar`."""
import itertools
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import AMBIENTE, RAIZ, carregar

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
    # A tabela do R3 da spec da fase 1, escrita aqui por extenso de propósito.
    assert c == {"receita": "economico", "revisor": "sempre", "revisor_quando": "por_fase",
                 "modelo_revisor": "sonnet", "validador": "nunca", "modelo_validador": "opus",
                 "guardiao": "nunca", "parar_a_cada_parte": "sempre", "conversas": "uma",
                 "gancho": "ligado", "gancho_teto": 2}


def test_linha_vale_mais_que_a_receita(tmp_path):
    escrever(tmp_path, 'receita = "completo"\nrevisor = "perguntar"\n')
    c = golem.configuracao(tmp_path)
    assert c["revisor"] == "perguntar" and c["validador"] == "sempre" and c["gancho_teto"] == 4
    assert "Com `perguntar`, pergunte com botões" in golem.bloco(c)
    assert "Com `perguntar`" not in golem.bloco(golem.configuracao(tmp_path / "vazia"))
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


def test_linha_mal_formada_falha_com_o_numero_da_linha():
    msg = erro_de('# ok\nreceita = "so-eu"\ngancho = desligado\n')
    assert "golem.toml:3" in msg and "gancho = desligado" in msg, msg


# ---------------------------------------------------------------- o aplicar


def test_aplicar_escreve_o_model_dos_dois_agentes(copia_do_kit):
    agentes = copia_do_kit / ".claude" / "agents"
    # O revisor sem `model:` e em CRLF; o validador com um `model:` velho, em LF.
    revisor = (agentes / "revisor.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    revisor = "\n".join(l for l in revisor.split("\n") if not l.startswith("model:"))
    escrever(agentes, revisor.replace("\n", "\r\n"), "revisor.md")
    validador = (agentes / "validador.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    validador = "\n".join(l for l in validador.split("\n") if not l.startswith("model:"))
    escrever(agentes, validador.replace("tools: ", "model: sonnet\ntools: ", 1), "validador.md")
    escrever(copia_do_kit, 'modelo_revisor = "haiku"\n')

    assert golem.aplicar(copia_do_kit) == 0

    r = (agentes / "revisor.md").read_bytes().decode("utf-8")
    assert "\ntools: Read, Grep, Glob, Bash\r\nmodel: haiku\r\n---\r\n" in r, r[:600]
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
    assert texto == antes + golem.bloco(golem.configuracao(copia_do_kit)) + depois[1:], texto
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
    """O que o aplicar gera a partir do golem.toml deste projeto é o que está no disco. No kit, sem
    golem.toml, é a `economico`: é o que o usuário copia até a fase 4."""
    divergentes = [p.relative_to(RAIZ).as_posix() for p, (texto, _) in golem.esperado(RAIZ).items()
                   if golem._ler(p)[0] != texto]
    assert not divergentes, f"rode `python3 .claude/golem.py aplicar`: {divergentes}"
