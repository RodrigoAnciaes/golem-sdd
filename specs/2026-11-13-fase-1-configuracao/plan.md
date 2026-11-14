# Fase 1: configuração e receita econômica — Plano

Cada grupo fecha com a suíte do ferramental (a linha de resumo lida) e com a revisão da regra 11,
no fluxo de hoje (R10): o revisor e o validador, chamados com o modelo `opus` na própria chamada.
O G1 vai pelo caminho rápido (só documentação e skill, revisor só). O G4 é só texto, mas vai pelo
caminho completo por escolha: é ele que muda o que o agente faz.

## G1 — As decisões de 2026-11-13 (R1)

- [x] `.claude/skills/diagnostico/SKILL.md`: tirar o aviso da linha `python` própria do worktree
  (o "Lê" e o "Escreve", `:9-12`; a variável `raiz`, `:24`; o `grep` da raiz, `:26`; o item
  `:33-34`). A conferência do `.gitignore` e a `:31` ficam.
- [x] `docs/plano-produto.md`, seção 8: as duas decisões de 2026-11-13, com as palavras ("Sim, as
  quatro"), e as quatro respostas desta entrevista (o kit na `economico`, o leitor próprio, o modo
  sem Python mínimo, a `configurar` com a receita e duas etapas).
- [x] `docs/plano-produto.md`, "Detalhes a conferir": o item das duas lições (fase 4); o do
  "pulado sem Python" na `validar-fase`, na `auditar-specs` e na `sessao-gerente` (fase 4); o do
  `tomllib`, resolvido (leitor próprio); o do modelo no Codex, movido para a fase 6; o do
  `systemMessage` de subagente, movido para a fase 4.
- [x] O instalador do Codex, rodado numa cópia: `--conferir` ok.

**Revisão:** revisor (caminho rápido).

## G2 — O `golem.toml`, as receitas e o `aplicar` (R2, R3, R4, R10)

- [x] Reconferir a suíte em `1f9f827` antes do primeiro teste novo: `96 passed`.
- [x] `.claude/golem.py`: o leitor (R2), as receitas (R3), a fusão e a validação, e o `aplicar`
  (R4): o `model:` dos dois agentes e o bloco do `AGENTS.md` entre as marcas.
- [x] `AGENTS.md`: as duas marcas, vazias, entram à mão numa seção "Como o Golem trabalha aqui"
  depois de "Comandos reais". O conteúdo do bloco (a `economico`) e o `model:` de
  `.claude/agents/revisor.md` e `validador.md` saem do `aplicar` rodado no kit, e não à mão.
- [x] `.claude/tests/conftest.py`: a `copia_do_kit` copia também o `AGENTS.md` (R9).
- [x] `.claude/tests/test_credito.py`: o `.claude/golem.py` e o `.claude/tests/test_golem.py` na
  lista `ARQUIVOS_DO_KIT` (R9).
- [x] Testes novos em `.claude/tests/test_golem.py`, no padrão do `test_codex.py`:
  1. `test_le_texto_com_aspas_duplas_e_simples_inteiro_e_comentario`;
  2. `test_le_arquivo_em_crlf`;
  3. `test_sem_golem_toml_vale_a_economico`;
  4. `test_linha_vale_mais_que_a_receita`;
  5. `test_chave_repetida_vale_a_ultima`;
  6. `test_chave_desconhecida_falha_com_o_numero_da_linha`;
  7. `test_valor_fora_da_tabela_falha_e_lista_os_aceitos`;
  8. `test_linha_mal_formada_falha_com_o_numero_da_linha`;
  9. `test_aplicar_escreve_o_model_dos_dois_agentes` (troca a linha que houver; sem ela,
     acrescenta depois do `tools:`);
  10. `test_aplicar_troca_so_o_que_esta_entre_as_marcas`;
  11. `test_aplicar_sem_as_marcas_acrescenta_o_bloco_no_fim`;
  12. `test_aplicar_com_erro_nao_escreve_nada`;
  13. `test_segunda_rodada_do_aplicar_nao_muda_nada`;
  14. `test_bloco_de_cada_receita`, parametrizado nas três receitas (3 casos);
  15. `test_o_agents_md_e_os_agentes_batem_com_o_golem_toml`: o bloco do `AGENTS.md` e o
      `model:` dos dois agentes do projeto são o que o `aplicar` gera a partir do `golem.toml` do
      próprio projeto. No kit, sem `golem.toml`, é a `economico` (R10).

**Revisão:** revisor + validador.

## G3 — O gancho obedece (R5, R9)

- [x] `.claude/hooks/gancho.sh`: ler a linha `gancho` do `golem.toml` da raiz, antes de procurar o
  Python, no padrão do `ler_linha_python`, valendo a última linha; com `desligado`, sair calado.
- [x] `.claude/hooks/licoes_relevantes.py`: o teto pelo leitor do `golem.py`, com o da `economico`
  quando falta o `golem.toml` ou quando ele tem erro. Sem caminho de reserva para a falta do
  `golem.py` (R5).
- [x] `.claude/tests/conftest.py`: o `Acervo` copia o `golem.py`. Os dois testes que contam com o
  teto 4 (`test_gancho.py:68` e `:91`) põem `gancho_teto = 4` na cópia.
- [x] Testes novos em `.claude/tests/test_gancho.py`:
  1. `test_lancador_com_gancho_desligado_sai_calado_sem_python` — o PATH sem Python: código 0, sem
     saída, sem linha no `gancho-falhas.log`;
  2. `test_lancador_com_gancho_desligado_nao_roda_o_python` — um repassador que grava um
     marcador: o marcador não aparece;
  3. `test_lancador_le_o_desligado_com_aspas_simples_crlf_e_comentario` — o arquivo, em CRLF,
     traz `gancho = "ligado"`, depois `gancho = 'desligado' # comentário` e, por último,
     `gancho_teto = 1`: sai calado (a última linha `gancho` vale, e o `gancho_teto` que vem
     depois não conta como `gancho`);
  4. `test_lancador_com_outro_valor_de_gancho_segue` — três arquivos: `gancho = "ligado"`;
     `desligado` sem aspas; e `gancho = "desligado"` seguido de `gancho = "ligado"`. Nos três, a
     lição chega;
  5. `test_teto_vem_da_linha_gancho_teto` — `gancho_teto = 1`, com três lições que casam: chega
     uma;
  6. `test_teto_sem_golem_toml_e_o_da_economico` — chegam duas;
  7. `test_teto_da_receita_completo_e_4` — chegam quatro;
  8. `test_golem_toml_com_erro_o_gancho_usa_o_teto_padrao` — chegam duas, sem erro.

**Revisão:** revisor + validador.

## G4 — As regras e as skills obedecem (R6, R7)

- [x] `AGENTS.md`: as regras 10 e 11, citando o bloco.
- [x] `.claude/skills/implementar-fase/SKILL.md`: o fechamento de grupo, o parar a cada parte, o
  revisor por fase, o `perguntar` e a busca das lições em `docs/licoes/` (R7).
- [x] `.claude/skills/validar-fase/SKILL.md`: a revisão do fechamento conforme o bloco.
- [x] `.claude/skills/spec-de-fase/SKILL.md`: os grupos pequenos com o parar a cada parte.
- [x] `.claude/skills/licao/SKILL.md`: a régua pulada sem Python (R7).
- [x] `docs/operacao-das-conversas.md:156-159`, a description da `implementar-fase` e as descrições
  do `.claude/agents/revisor.md` e do `validador.md`.
- [x] A varredura do R6: `README.md` (`:42`, `:45`), `WORKFLOW.md` (`:9`, `:79`, `:84`, `:88`,
  `:106`, `:110-121`, `:138`), a linha "O que é **gerado**" do `AGENTS.md`, o
  `docs/plano-produto.md:244` e a docstring do `conftest.py:89`. Depois, o `git grep` do R6 roda de
  novo, e o que ele achar ou se corrige ou se justifica na tabela de alterações.
- [x] O `aplicar` rodado de novo, porque os agentes mudaram: a segunda rodada não muda nada.

**Revisão:** revisor + validador.

## G5 — A skill `configurar`, o guia e a varredura (R8, R11)

- [x] `.claude/skills/configurar/SKILL.md`, com as três perguntas, o `golem.toml` com as linhas
  que diferem da receita e as das chaves que ela não pergunta, a busca do Python, o caminho sem Python e o `aplicar`.
- [x] `.claude/skills/diagnostico/SKILL.md`, passo 6: oferecer também o modo sem Python.
- [x] `docs/guia-configuracao.md`, de uma página.
- [x] Teste novo: `test_o_guia_traz_as_receitas_do_golem_py`, em `.claude/tests/test_golem.py` (a
  tabela do guia bate com as receitas do `golem.py`).
- [x] A varredura do R11: `iniciar-sdd`, `WORKFLOW.md`, `test_credito.py`, `README.md` e a seção 3
  do `docs/plano-produto.md`.
- [x] O instalador do Codex, rodado numa cópia, leva a skill nova (`--conferir` ok).

**Revisão:** revisor + validador.

## G6 — Verificação

- [ ] Rodar o `validation.md` inteiro, com a saída colada.
- [ ] As verificações manuais, com o autor do kit (o projeto de teste e a sessão nova são dele).
- [ ] O guardião sobre o diff do PR (`git diff 1f9f827`), num subagente novo.
- [ ] Spec e código reconciliados: as mudanças na tabela abaixo.
- [x] As correções da verificação manual 1 e do guardião (2026-11-13): o frontmatter do
  `revisor.md` volta a ser YAML válido; o teste novo
  `test_o_frontmatter_dos_agentes_e_das_skills_e_yaml_valido` (`.claude/tests/test_codex.py`);
  a busca das lições sem `-i` com dois `-e`; a `diagnostico` pula o passo 7 no modo sem Python e,
  com a `configurar`, troca à mão a linha do gancho no bloco; o caminho rápido condicional na
  `operacao-das-conversas` e no `WORKFLOW`; o bloco diz "antes da verificação"; e as lições
  `frontmatter-invalido-some-com-o-agente-sem-aviso` e
  `o-grep-do-git-for-windows-aborta-com-i-e-varios-e`.

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Decidido por |
|---|---|---|---|
| 2026-11-13 | G6: o frontmatter do `revisor.md` voltou a ser YAML válido, e um teste novo confere o frontmatter de todos os agentes e skills; a contagem vai de 122 para 123. | Na verificação manual 1, a sessão de teste respondeu "Agent type 'revisor' not found": a descrição do G4 tinha "AGENTS.md: por grupo", e o Claude Code descartou o agente calado. Nem a suíte, nem os revisores, nem o guardião viram (lição `frontmatter-invalido-some-com-o-agente-sem-aviso`). | agente (achado da verificação manual 1) |
| 2026-11-13 | G6: a busca das lições da `implementar-fase` usa a busca do agente ou `grep -ilE 'a\|b'`, nunca `-i` com dois `-e`. | O grep 3.0 do Git for Windows aborta nesse caso (os `grep.exe.stackdump` da fase vinham disso, e não do acento); a sessão de teste perdeu a busca (lição `o-grep-do-git-for-windows-aborta-com-i-e-varios-e`). | agente (achado da verificação manual 1) |
| 2026-11-13 | G6: no modo sem Python, a `diagnostico` pula o passo 7 e, com a `configurar`, troca à mão só a linha do gancho no bloco do `AGENTS.md`, pelo texto que o `aplicar` gera (um teste confere que o texto da skill é o do `golem.py`). | O passo 7 diria "o Python rodou" com o gancho desligado, que sai vazio (bloqueio do guardião); e o bloco seguiria dizendo "ligado" a cada turno, sem o R7 chegar à máquina sem Python (guardião). | agente |
| 2026-11-13 | G6: o bloco diz "uma vez por fase, antes da verificação", e não "ao fim do último grupo"; o caminho rápido da `operacao-das-conversas` e do `WORKFLOW` vale "se o revisor roda". | O bloco, que entra em todo turno, ficava ambíguo com o grupo de verificação; a forma curta não passa do teto de 1.200 bytes (o pior bloco media 1.186 em CRLF, e não 1.166 como registrado antes). A `operacao` contradizia a regra 11 na `so-eu` (guardião). | agente |
| 2026-11-13 | G6: na linha `gancho = "desligado" extra`, o `sh` desliga e o `golem.py` acusa erro. Fica assim. | O R5 manda o `sh` ignorar o resto da linha; o `aplicar` acusa o erro ao usuário (guardião, menor). | agente |
| 2026-11-13 | G5: a `diagnostico`, com o sim ao modo sem Python, escreve ela mesma a linha `gancho = "desligado"` no `golem.toml` da raiz (o R8 só pedia a oferta); quando a pergunta vem pela `configurar`, é esta que oferece, uma vez só. | Sem isso, o sim mandava o usuário a outra skill, que repetiria as três perguntas (revisor do G5). | agente |
| 2026-11-13 | G5: o aviso da `configurar` sai pelo resultado: "sem revisão" só com revisor, validador e guardião em `nunca`; sem revisor mas com os outros, diz quais continuam. O guia diz que o parar a cada parte custa um turno a mais por parte. | As duas frases, como estavam, eram falsas para a `completo` com revisor `nunca` e para o custo do turno que relê o contexto (bloqueios do revisor do G5). O R8 dizia "fica sem a leitura independente" para o revisor `nunca`, o que vale só sem os outros dois. | agente |
| 2026-11-13 | G5: o teste do guia confere também a ordem das colunas e as chaves de todas as receitas; a contagem não muda. | O validador do G5 deu "não valida": o cabeçalho com as receitas trocadas e uma chave só numa receita passavam (M3 e M4). Com a correção, os dois mutantes fazem o teste falhar. | agente |
| 2026-11-13 | G5: os `refs` das duas lições que citam a `diagnostico` andaram uma linha (o "Escreve" ganhou uma). | Quem muda, varre. | agente |
| 2026-11-13 | G4: a varredura do R6 alcançou também a `iniciar-sdd`, a `sessao-gerente` (e `references/projeto-modelo.md`), o `templates/fase/plan.md`, o `templates/pull_request_template.md` ("não roda (o bloco)"), a linha GUA do `docs/operacao-das-conversas.md:28` e o `docs/plano-produto.md:34` e `:37` ("desde a fase 1"). | Diziam o fluxo de antes (revisor e validador a cada grupo; guardião opcional com uma conversa só). A linha GUA era o bloqueio do revisor do G4. | agente (quem muda, varre) |
| 2026-11-13 | G4: o que o `git grep` do R6 ainda acha e fica: as frases condicionais novas; o `golem.py` e os testes do bloco; o "fim de turno" do fecho (`README.md:66`, `docs/operacao-das-conversas.md:140`); a CI "a cada grupo" da `implementar-fase`; e o diagnóstico e o desenho datados do `docs/plano-produto.md`. | Falam de outra coisa, ou são condicionais, ou são registro datado (revisor e validador do G4). | agente |
| 2026-11-13 | G4: a regra 11 diz "não passe outro modelo na chamada, salvo se a spec da fase pedir outro"; a revisão por fase roda ao fim do último grupo de implementação, antes do de verificação; sem o bloco, roda-se o `aplicar`, e sem Python vale a `economico`; a `licao` pula a régua só sem Python. | Achados do revisor do G4: a frase sem a ressalva contradizia o R10 desta fase; o "último grupo" era ambíguo; um `AGENTS.md` sem o bloco não tinha regra; gancho desligado não prova falta de Python. | agente |
| 2026-11-13 | G4: nenhum teste protege o texto das regras e das skills (a mutação de voltar a regra 11 passa na suíte). | São instruções ao agente; o comportamento se prova nas verificações manuais 1 e 2 do G6 (validador do G4). | agente (limite registrado) |
| 2026-11-13 | G3: o `licoes_relevantes.py` lê o teto antes de reivindicar as regras de área, e não grava `.claude/__pycache__/` ao carregar o `golem.py` (`sys.dont_write_bytecode`). | Sem o `golem.py`, a falha vinha depois de marcar as regras como entregues, e elas sumiam da sessão; o `exec_module` gravaria bytecode no projeto a cada ação (revisor do G3). | agente |
| 2026-11-13 | G3: o teste 3 também roda um CRLF logo depois da aspa e um comentário colado no valor; a contagem não muda. O `docs/plano-produto.md:35` (seção 1, "o kit hoje") diz que o teto vem do `golem.toml` desde a fase 1. | Os ramos `#` e `
` do `case` não eram exercitados (o mutante sem eles passava; agora faz o teste falhar); a frase do `TETO = 4` ficou falsa (revisor do G3). | agente |
| 2026-11-13 | G2: o título "## Como o Golem trabalha aqui" fica dentro das marcas, gerado pelo `aplicar`; no `AGENTS.md` do kit, só as duas marcas entraram à mão. | Sem as marcas, o bloco acrescentado no fim precisa do próprio título; assim há um caminho só. | agente (achado menor do revisor do G2) |
| 2026-11-13 | G2: o teste 4 mede o tamanho de todo bloco possível, em CRLF (o pior dava 1.210 bytes; o comentário do bloco encurtou, e o pior ficou em 1.166); o teste 12 também prova que, com as marcas incompletas, nada é escrito. A contagem não muda. | O R4 pede até 1.200 bytes, e o teste só media as três receitas (revisor e validador do G2); a escrita antes de conferir as marcas sobrevivia à mutação (validador do G2). | agente |
| 2026-11-13 | G2: no bloco, o `perguntar` diz "e só rode com o sim" na nota final, o `inherit` vira "o da conversa" e o gancho desligado diz o que procurar em `docs/licoes/`. | O texto do bloco é instrução ao agente (G4), e o `grep -ril` sem termo não dizia o que buscar (revisor do G2). | agente |
| 2026-11-13 | G2: o `golem.toml` com BOM (UTF-8 com assinatura) é recusado na linha 1, e o gancho cai no teto padrão. Não tratado. | Nenhum caso visto (regra 10): o Bloco de Notas atual grava sem BOM. Se aparecer, o ajuste é `utf-8-sig` no leitor e no `gancho.sh`. | agente (achado menor do revisor e do validador do G2) |
| 2026-11-13 | G1: os `refs` das lições `sem-python-no-path-nao-e-maquina-sem-python` e `trocar-o-localappdata-nao-esconde-o-python-do-agente` passam a citar as linhas novas da `diagnostico` (`:33-42 e :78-91`, `:65-72`, `:92-98`). | A skill perdeu 5 linhas antes do passo 2, e as citações apontavam para o trecho errado (quem muda, varre). O G5 muda o passo 6 de novo e varre outra vez. | agente (achado do revisor do G1) |

## Estado para a retomada

Spec aprovada em 2026-11-13 ("Aprovo"), com um commit por grupo na branch da fase. G1 a G5
commitados, cada um com revisor e validador. G6: a prova automatizada passou em `1397a98`; a
verificação manual 1 achou o `revisor` fora do ar (frontmatter inválido) e o `grep` que aborta;
o guardião deu "com bloqueio" (o passo 7 da `diagnostico` no modo sem Python). As correções
estão no commit das correções do G6; falta repetir a verificação manual 1 e fazer as 2, 3 e 4,
no projeto de teste do autor do kit.
