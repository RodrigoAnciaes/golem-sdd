---
id: suite-verde-so-vale-com-a-linha-de-resumo
data: 2026-11-06
area: processo
tipo: armadilha
custo: "uma entrega dada por testada em que parte da suíte não rodou: pulada, não coletada ou sem resumo para conferir"
gatilho: "rodar a suíte com o -q do arquivo de configuração somado ao -q da linha de comando, ou num ambiente sem a variável ou o dado que alguns testes exigem"
gatilhos:
  - '\bpytest\b'
  - '\bnpm\s+(run\s+)?test\b'
  - '\bmake\s+test'
  - '(^|/)(pytest\.ini|pyproject\.toml|setup\.cfg|tox\.ini)$'
refs:
  - "pytest: -q diminui a verbosidade, e cada -q a mais diminui de novo; com -qq a linha de resumo não sai"
  - "pytest: -o addopts= anula o addopts do pytest.ini, do pyproject.toml ou do setup.cfg"
  - "pytest: -rs lista o motivo de cada teste pulado"
---

**O que se achava:** que "não apareceu falha" quer dizer "a suíte passou", e que teste pulado é
ruído de ambiente.

**O que é:** a suíte mente de três jeitos sem acusar erro. (1) O arquivo de configuração já traz
`-q` no `addopts`; passar `-q` de novo vira `-qq`, e com `-qq` o pytest **não imprime a linha de
resumo**: sobram os pontinhos, e quem lê vê "verde" sem saber quantos testes rodaram. (2) Teste
que depende de uma variável de ambiente, de um serviço ou de um arquivo de dados costuma se pular
quando não os acha: a suíte termina verde sem ter exercitado o que importava. (3) Um teste com nome
fora do padrão de coleta (`test_*.py`, `test_*`) nem entra na conta.

**Como perceber da próxima vez:**
1. Rode com `-o addopts= -q` e **leia a linha de resumo** (`N passed, M skipped in Xs`). Sem essa
   linha não há resultado para relatar, só a ausência de erro.
2. Compare o total **e o número de pulados** com o da última rodada registrada. Pulado a mais é
   falha até prova em contrário; `-rs` mostra o motivo de cada um, e um motivo do tipo "variável
   não definida" é um teste que não rodou.
3. Total menor que o esperado, sem falha nenhuma: procure o arquivo que deixou de ser coletado.
