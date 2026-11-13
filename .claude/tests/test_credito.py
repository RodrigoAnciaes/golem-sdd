# Golem SDD · © 2026 Rodrigo Anciães Patelli · licença MIT (.claude/LICENSE) · https://github.com/RodrigoAnciaes/golem-sdd
"""O crédito do kit: o `.claude/LICENSE` existe, e cada arquivo do kit traz a linha de crédito.

A condição da MIT é manter o aviso de copyright e o texto da licença em toda cópia do kit. A
instalação copia a pasta `.claude/` inteira, e o `LICENSE` vai dentro dela.

`ARQUIVOS_DO_KIT` é uma lista fechada de propósito. As skills, os agentes e os scripts que o
usuário cria no próprio projeto são dele e não levam o crédito do kit. Um arquivo da lista que o
usuário apagou não reprova: só se confere o que existe. Quem acrescentar uma skill, um agente ou
um script AO KIT põe a linha de crédito nele e o caminho aqui.
"""
from conftest import RAIZ

NOME = "Rodrigo Anciães Patelli"
URL = "https://github.com/RodrigoAnciaes/golem-sdd"
LINHA = f"Golem SDD · © 2026 {NOME} · licença MIT (.claude/LICENSE) · {URL}"
LICENSE_DA_SKILL = f'license: "MIT. © 2026 {NOME}. Golem SDD, {URL} (texto em .claude/LICENSE)"'

SKILLS = ["adr", "auditar-specs", "changelog", "constituicao", "implementar-fase",
          "iniciar-conversa", "iniciar-sdd", "licao", "replanejar-roadmap", "sessao-gerente",
          "spec-de-fase", "validar-fase"]
ARQUIVOS_DO_KIT = (
    [(f".claude/skills/{s}/SKILL.md", LICENSE_DA_SKILL) for s in SKILLS]
    + [(f".claude/agents/{a}.md", f"<!-- {LINHA} -->") for a in ("revisor", "validador")]
    + [(caminho, f"# {LINHA}") for caminho in (
        ".claude/hooks/gancho.sh",
        ".claude/hooks/licoes_relevantes.py",
        ".claude/instalar_codex.py",
        ".claude/regua.py",
        ".claude/tests/conftest.py",
        ".claude/tests/test_codex.py",
        ".claude/tests/test_credito.py",
        ".claude/tests/test_gancho.py",
        ".claude/tests/test_regua.py",
    )]
)


def test_o_license_do_kit_viaja_dentro_de_claude():
    licenca = RAIZ / ".claude" / "LICENSE"
    assert licenca.is_file(), ".claude/LICENSE sumiu: é a condição da MIT (README, 'Licença e crédito')"
    texto = licenca.read_text(encoding="utf-8")
    assert texto.startswith("MIT License"), texto[:80]
    assert f"Copyright (c) 2026 {NOME}" in texto
    assert "shall be included in all" in texto


def test_cada_arquivo_do_kit_traz_a_linha_de_credito_uma_vez():
    sem_credito = []
    for caminho, linha in ARQUIVOS_DO_KIT:
        arquivo = RAIZ / caminho
        if not arquivo.is_file():
            continue
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        if linhas.count(linha) != 1:
            sem_credito.append(f"{caminho}: {linhas.count(linha)} linha(s) de crédito, esperada 1")
    assert not sem_credito, "\n".join(sem_credito)
