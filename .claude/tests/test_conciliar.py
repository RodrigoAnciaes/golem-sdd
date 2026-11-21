# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O conciliador: o `AGENTS.md` do kit e o modelo que o usuário copia (`templates/AGENTS.md`).

O modelo é a fonte; o `AGENTS.md` da raiz é o do desenvolvimento do kit, editado à mão. Toda
diferença entre os dois que não estiver em `PERMITIDAS` reprova. Quando reprovar, a MET decide:
a mudança vai ao modelo (o produto), ou entra em `PERMITIDAS` com o motivo (fica só no kit).

O bloco "Como o Golem trabalha aqui" fica fora da comparação: o da raiz é escrito pelo `golem.py
aplicar` com o `golem.toml` do kit e conferido pelo `test_golem.py`; o do modelo é o da
`economico`, conferido aqui por `test_o_modelo_traz_o_bloco_da_economico`.

Fora do repositório do kit (no projeto do usuário, que recebe a `.claude/tests/` até a fundação
do Golem central), o módulo se pula: lá o `AGENTS.md` da raiz é o dele, não o do kit.
"""
import difflib
from pathlib import Path

import pytest

from conftest import RAIZ, carregar

golem = carregar("golem", RAIZ / ".claude" / "golem.py")

MODELO = RAIZ / "templates" / "AGENTS.md"
KIT = RAIZ / "AGENTS.md"
FRASE_DO_KIT = "Este é o `AGENTS.md` do kit."


def ler(caminho: Path) -> str:
    return golem._ler(caminho)[0]


def _so_espacos(texto: str) -> str:
    return " ".join(texto.split())


pytestmark = pytest.mark.skipif(
    not KIT.is_file() or FRASE_DO_KIT not in _so_espacos(ler(KIT)),
    reason="não é o repositório do kit: o conciliador só roda lá (o AGENTS.md da raiz não traz a "
           "frase de abertura do kit)")


# (o trecho do modelo, o trecho do kit, o motivo). Cada trecho do modelo aparece uma vez só nele.
PERMITIDAS = [
    ("tarefa, em qualquer conversa. Os trechos entre `<< >>` são do projeto: preencha antes de usar.",
     "tarefa, em qualquer conversa. Este é o `AGENTS.md` do kit. O modelo que o usuário copia é o\n"
     "`templates/AGENTS.md`, com as lacunas; as diferenças entre os dois estão no conciliador\n"
     "(`.claude/tests/test_conciliar.py`).",
     "no kit não há lacuna: a abertura diz que este é o do kit e onde está o modelo"),
    ('<< Uma frase: o que o projeto é e para quem. Ex.: "API de agendamento para clínicas pequenas." >>',
     "Golem SDD: kit de spec-driven development para Claude Code e Codex, pensado para desenvolvedores de\n"
     "Roblox iniciantes.",
     "a lacuna do projeto, preenchida com o kit"),
    ("| Código | << ex.: `src/` >> |\n"
     "| Specs | `specs/` (a constituição e uma pasta por fase) |\n"
     "| Decisões técnicas | `docs/adr/` |",
     "| Código | `.claude/` (skills, agentes, gancho, régua, `golem.py`, instalador do Codex) e `templates/` |\n"
     "| Specs | `specs/` (uma pasta por fase) |\n"
     "| Decisões técnicas | a seção 8 do `docs/plano-produto.md` (o kit não tem `docs/adr/`) |",
     "o código do kit; o kit não tem constituição em specs/ nem docs/adr/: ficam no plano de produto"),
    ("3. `specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`: a constituição.",
     "3. `docs/plano-produto.md`: a constituição do kit, com o roteiro na seção 7.",
     "a constituição do kit é o plano de produto"),
    ("5. `docs/adr/`: as decisões registradas, com o gatilho de revisão de cada uma.",
     "5. A seção 8 do `docs/plano-produto.md`: as decisões registradas.",
     "as decisões do kit ficam na seção 8 do plano de produto"),
    ("<< Preencha com os comandos que funcionam hoje, copiados de quem roda. Sem eles, as regras 4 e 8\n"
     "ficam no ar. >>",
     "Onde se lê `python`, use um Python 3.8+ com pytest (no Windows, `python` ou `py -3`).",
     "a lacuna que abre os comandos reais: no kit, como ler o `python` dos comandos"),
    ("<< ex.: python -m venv .venv && .venv/bin/pip install -r requirements.txt >>",
     "nenhum: só a biblioteca padrão; a suíte pede pytest",
     "o setup do kit"),
    ("<< ex.: .venv/bin/python -m pytest -q >>",
     "python -m pytest .claude/tests -o addopts= -q -p no:cacheprovider -rs\n"
     "\n"
     "# a régua\n"
     "python .claude/regua.py --conferir",
     "a suíte e a régua do kit"),
    ('<< ex.: ruff check . && ruff format --check . — ou "não instalado" >>',
     "não instalado",
     "o kit não tem lint"),
    ("<< ex.: docker compose up -d >>",
     "não há: o kit é texto e scripts",
     "o kit não sobe nada"),
    ("**Stack:** << linguagem e versão, framework, banco. O detalhe vive em `specs/tech-stack.md`. >>",
     "**Stack:** Python 3.8+ só com a biblioteca padrão (scripts e gancho), `sh` POSIX no gancho,\n"
     "Markdown nas skills, e pytest só na suíte do kit.",
     "a stack do kit; ele não tem specs/tech-stack.md"),
    ("**Contagem esperada de testes:** << onde ela vive: um índice gerado ou o `validation.md` da fase.\n"
     "Nunca um número escrito à mão em prosa, que envelhece sem avisar. >>",
     "**Contagem esperada de testes:** no `validation.md` de cada fase: a contagem da fase anterior mais\n"
     "os testes novos.",
     "onde vive a contagem do kit"),
    ("- Commits e PRs em << português >>. Merge por << squash | merge commit >>.",
     "- Commits e PRs em português. Merge por merge commit.",
     "as convenções do kit (git log --merges: todo PR por merge commit)"),
    ("  - << o que mais o projeto listar >>.",
     "  - nenhum além dos três acima.",
     "o kit não tem nível 3 a mais; o docs/operacao-das-conversas.md, uma cópia só, guarda a lacuna"),
    ("  lá no mesmo commit.\n",
     "  lá no mesmo commit. No kit, aquele arquivo guarda a lacuna do modelo, e a regra vale entre ele e o\n"
     "  `templates/AGENTS.md`.\n",
     "no kit, a lista de nível 3 difere da do docs/operacao-das-conversas.md, que serve ao modelo"),
    ("`--conferir` acusa a\n  divergência).\n",
     "`--conferir` acusa a\n  divergência). O repositório do próprio kit não versiona as cópias: quem instala o kit as gera no\n"
     "  projeto dele (`README.md` do kit, \"Usando com o Codex\").\n",
     "só o repositório do kit deixa de versionar as cópias do Codex"),
    ("- << convenções do projeto: estrutura de pastas, nomes, tratamento de erro >>",
     "- Nenhum nome de cliente, de outro projeto ou de pessoa entra no kit, fora do crédito (a linha de\n"
     "  crédito, o `LICENSE` e a seção \"Licença e crédito\" do `README.md`).",
     "a convenção do kit sobre nomes"),
    ("Algo fora de `specs/tech-stack.md`,\n   inclusive",
     "Algo fora da linha **Stack** dos\n   \"Comandos reais\", inclusive",
     "a regra 3 aponta a stack do kit, que não tem specs/tech-stack.md"),
    ("   (<< ex.: `.env`, no `.gitignore` >>). Não leia nem imprima segredo para \"conferir\".",
     "   (o kit não tem segredo; o `golem.local.toml`, com o caminho do Python da máquina, fica no\n"
     "   `.gitignore`). Não leia nem imprima segredo para \"conferir\".",
     "o kit não tem segredo"),
    ("<< Regras do projeto: acrescente a partir da 13, cada uma curta, imperativa e citando a lição que a\n"
     "justifica. >>",
     "Regras do kit a partir da 13: nenhuma por ora.",
     "o kit não tem regra própria"),
]


def sem_bloco(texto: str, nome: str) -> str:
    """O texto com o bloco gerado trocado só pelas marcas."""
    i, f = texto.find(golem.INICIO), texto.find(golem.FIM)
    assert 0 <= i < f, f"o {nome} perdeu as marcas do bloco gerado"
    return texto[:i] + golem.INICIO + "\n" + texto[f:]


def test_cada_diferenca_permitida_tem_motivo_e_acha_o_trecho():
    modelo = ler(MODELO)
    problemas = []
    for n, (de, _para, motivo) in enumerate(PERMITIDAS, 1):
        if not motivo.strip():
            problemas.append(f"PERMITIDAS[{n}]: sem motivo")
        vezes = modelo.count(de)
        if vezes != 1:
            problemas.append(f"PERMITIDAS[{n}] ({motivo or 'sem motivo'}): o trecho aparece {vezes} "
                             f"vez(es) no templates/AGENTS.md; esperada 1. A permissão envelheceu ou "
                             f"ficou ambígua:\n    {de!r}")
    assert not problemas, "\n".join(problemas)


def test_o_agents_md_do_kit_concilia_com_o_modelo():
    esperado = sem_bloco(ler(MODELO), "templates/AGENTS.md")
    for de, para, _motivo in PERMITIDAS:
        esperado = esperado.replace(de, para, 1)
    kit = sem_bloco(ler(KIT), "AGENTS.md da raiz")
    if esperado == kit:
        return
    diff = "".join(difflib.unified_diff(
        esperado.splitlines(keepends=True), kit.splitlines(keepends=True),
        "templates/AGENTS.md (com as PERMITIDAS)", "AGENTS.md (do kit)"))
    pytest.fail("O AGENTS.md do kit e o modelo divergem fora das diferenças permitidas. A MET "
                "decide: leve a mudança ao templates/AGENTS.md (vai ao produto) ou acrescente-a a "
                "PERMITIDAS, em .claude/tests/test_conciliar.py, com o motivo (fica só no kit).\n"
                + diff)


def test_o_modelo_traz_o_bloco_da_economico(tmp_path):
    modelo = ler(MODELO)
    i, f = modelo.find(golem.INICIO), modelo.find(golem.FIM)
    assert 0 <= i < f, "o templates/AGENTS.md perdeu as marcas do bloco gerado"
    bloco = modelo[i:f + len(golem.FIM)] + "\n"
    esperado = golem.bloco(golem.configuracao(tmp_path))  # pasta sem golem.toml: a economico
    assert bloco == esperado, ("o bloco do templates/AGENTS.md não é o da economico: copie-o do "
                               "golem.bloco da receita padrão")
