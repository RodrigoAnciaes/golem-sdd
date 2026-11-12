# Fase 0: o gancho acha o Python — Plano

Cada grupo fecha com a suíte do ferramental (a linha de resumo lida) e com o revisor e o validador
(regra 11). O G1 e o G2 têm código. O G3 é skill, documentação e uma linha de teste, e vai pelo
caminho completo por escolha: a skill nova é o que o usuário vê.

## G1 — A linha `python` e a ordem de procura (R1, R2, R5)

- [x] `.claude/hooks/gancho.sh`: ler a linha `python` pela regra do R1, do `golem.local.toml` da
  raiz e, se não houver, do da pasta principal; tentá-la antes do `.venv`.
- [x] `.claude/hooks/gancho.sh`: o passo 5 do R2, depois do PATH. Cada candidato só vale com o
  `[ -f ]` e o `roda_py38`; o `py.exe` do `Launcher` entra com `-3`, pelo `py_arg` de hoje.
- [x] `.gitignore`: a linha `golem.local.toml`.
- [x] `.claude/tests/test_gancho.py`: o `_path_sem_python` (linha 382) passa a isolar também o
  `LOCALAPPDATA` e o `PROGRAMFILES`, em pastas vazias do `tmp_path`, e o `TMPDIR`, num `tmp_path`
  (R5). Assim, os testes que já o usam continuam provando o que dizem.
- [x] Testes novos em `.claude/tests/test_gancho.py`, no padrão das linhas 314-454. Todos partem
  do `_path_sem_python`, salvo onde o teste aponta uma das variáveis de propósito:
  1. `test_lancador_usa_a_linha_python` — a linha aponta para um `_repassador`, com o PATH
     quebrado: a lição chega;
  2. `test_lancador_prefere_a_linha_python_ao_venv` — um `.venv` bom e a linha apontando para
     outro repassador, que grava um marcador: o marcador prova que o da linha venceu;
  3. `test_lancador_no_worktree_acha_o_golem_local_da_pasta_principal` — o arquivo só na pasta
     principal: a lição chega;
  4. `test_lancador_le_a_linha_com_crlf_e_comentario` — o arquivo em CRLF e com `# comentário`
     depois da aspa: a linha é lida;
  5. `test_lancador_pula_a_linha_python_que_nao_roda` — a linha com um caminho que não existe e
     um Python bom no PATH: a lição chega, sem aviso;
  6. `test_lancador_acha_o_python_em_localappdata` — `LOCALAPPDATA` com
     `Programs/Python/Python312/python.exe` falso e o PATH quebrado: a lição chega;
  7. `test_lancador_acha_o_py_do_launcher_com_menos_3` — só o `Launcher/py.exe`, que repassa
     apenas se receber `-3`: a lição chega;
  8. `test_lancador_acha_o_python_em_programfiles` — só o `PROGRAMFILES/Python312/python.exe`
     falso: a lição chega;
  9. `test_lancador_sem_lugares_de_costume_avisa_sem_erro_de_sh` — `LOCALAPPDATA` vazio e
     `PROGRAMFILES` ausente: o aviso sai, sem mensagem de erro do `sh` no stderr.

**Revisão:** revisor + validador.

## G2 — O aviso uma vez por sessão (R3, R5)

- [x] `.claude/hooks/gancho.sh`: no caminho da falha "nenhum Python", ler o stdin com `read`
  embutido e extrair o `session_id` e o `agent_id` por expansão de parâmetro, tolerando espaço
  depois dos dois-pontos. Validar cada id com `case` (`*[!A-Za-z0-9_-]*` invalida); um id com mais
  de 128 caracteres também. O agente ausente é `principal`.
- [x] Duas marcas na pasta temporária (`${TMPDIR:-${TEMP:-/tmp}}`), criadas com `set -C` e `>`,
  com o ponto como separador, que os ids não podem ter: `golem-aviso.<sessao>` (a do usuário) e
  `golem-aviso.<sessao>.<agente>`.
  - A marca do usuário só é tentada pela conversa principal. Quem a cria põe o `systemMessage`.
  - Quem cria a do agente põe o `additionalContext`.
  - Sem marca nova, o gancho sai calado.
  - Sem `session_id` válido, avisa em toda ação.
- [x] O texto do aviso (R3), em texto fixo, sem aspas nem barra invertida, com a frase da linha
  `python` quando ela existe e não roda.
- [x] O `gancho-falhas.log` recebe a linha também nas ações caladas.
- [x] Testes novos em `.claude/tests/test_gancho.py`, todos a partir do `_path_sem_python` (sem
  Python achável e com o `TMPDIR` num `tmp_path`):
  10. `test_aviso_sai_uma_vez_na_conversa_principal` — duas ações com `session_id` e sem
      `agent_id`: a primeira traz o `systemMessage` e o `additionalContext`, a segunda sai vazia;
  11. `test_aviso_ao_subagente_sem_repetir_ao_usuario` — depois da conversa principal, um
      `agent_id` novo: só o `additionalContext`, sem `systemMessage`;
  12. `test_aviso_sem_session_id_sai_em_toda_acao` — duas ações sem `session_id`: as duas avisam;
  13. `test_aviso_cita_a_linha_python_que_nao_roda` — a linha aponta para um caminho que não
      existe: o aviso traz a frase da linha `python`;
  14. `test_aviso_cita_a_licao_e_o_diagnostico` — o aviso traz
      `sem-python-no-path-nao-e-maquina-sem-python` e "diagnóstico";
  15. `test_aviso_com_ids_hostis_nao_escapa_da_pasta` — `session_id` com `../` e barra: nada é
      criado fora da pasta temporária, e o aviso sai como se não houvesse id;
  16. `test_aviso_le_o_json_com_espacos` — `"session_id" : "s1"` com espaços: a marca vale, e a
      segunda ação sai vazia; um `tool_input` com o valor `"agent_id"` e um `\"session_id\"`
      escapado não engana a leitura;
  17. `test_aviso_ao_usuario_mesmo_se_o_subagente_falhar_primeiro` — primeiro um `agent_id` de
      subagente (só o `additionalContext`), depois a conversa principal: ela ainda traz o
      `systemMessage`;
  18. `test_aviso_sem_pasta_temporaria_gravavel_avisa_em_toda_acao` — o `TMPDIR` aponta para uma
      pasta que não existe: as duas ações avisam (acrescentado na revisão do G2).

**Revisão:** revisor + validador.

## G3 — A skill `diagnostico` mínima e a varredura (R4, R6)

- [ ] O id do `winget` conferido (a pergunta em aberto) antes de a skill citá-lo.
- [ ] `.claude/skills/diagnostico/SKILL.md`, com a tabela do R4, a gravação na pasta principal,
  a recusa do caminho com aspa simples, a busca nos passos 4 e 5 do R2 e o teste final do gancho
  sem `session_id`. O frontmatter traz `name`, `description` e `license` (a linha de crédito).
- [ ] `.claude/tests/test_credito.py`: `diagnostico` na lista `SKILLS`.
- [ ] A varredura do R6:
  - os Requisitos e o passo 2 do `README.md`;
  - a lista de skills esperadas da `iniciar-sdd`;
  - a tabela "Em volta de tudo" do `WORKFLOW.md`;
  - os `refs` da lição, com o índice regerado (`regua.py --gerar`) e o `git add` do índice.
- [ ] O instalador do Codex, rodado numa cópia, leva a skill nova (`--conferir` ok).

**Revisão:** revisor + validador.

## G4 — Verificação

- [ ] rodar o `validation.md` inteiro, com a saída colada;
- [ ] o passo a passo manual nesta máquina (Python fora do PATH);
- [ ] spec e código reconciliados.

## Alterações de escopo durante a fase

| Data | O que mudou | Por quê | Decidido por |
|---|---|---|---|
| 2026-11-12 | G1: os testes do lançador que usam o `_rodar_lancador` passam a lançá-lo pelo `_comando_do_lancador`, que põe o `PROGRAMFILES` de dentro de um `sh` (ou o tira). Os testes 8 e 9 dependem disso. | No Windows, o sistema reescreve o `PROGRAMFILES` de todo processo novo, e o `env=` do teste não o troca (lição `o-windows-muda-o-que-o-sh-recebe-do-python`). | agente (detalhe de teste, sem efeito para o usuário) |
| 2026-11-12 | G1: o `test_lancador_sem_o_proprio_caminho_acha_a_raiz_pelo_git` (`test_codex.py`) passa o texto do lançador ao `sh -c` por dentro de um `sh`. A contagem não muda. | O `gancho.sh` passou de 8 mil caracteres, e um argumento desse tamanho chega cortado ao `sh` quando vem do Python (mesma lição). O Claude Code e o Codex rodam `sh <arquivo>` e não são afetados. | agente (detalhe de teste) |
| 2026-11-12 | G1: o `gancho.sh` não tira o `\r` do fim da linha, que o R1 pedia; o R1 foi ajustado. | O validador mostrou que a linha não tinha efeito (mutante equivalente em 16 arquivos, 4 com CR): o valor é cortado na segunda aspa, e o `\r` fica depois dela. O teste 4 continua provando que o CRLF é lido. | agente (regra 10, sem efeito para o usuário) |
| 2026-11-12 | G2: a leitura dos ids parte o JSON nas aspas (`ids_da_entrada`), em vez de cortar a entrada com `${entrada#*\"id\"}`. | O corte era quadrático: 4 s em 80 KB sem `agent_id`, o caso de toda ação da conversa principal; e um valor `"agent_id"` no `tool_input` o enganava. Partir é linear: 2 MB quase sem aspas em 0,04 s; 1,56 MB cheios de aspas em 5,9 s, medido pelo revisor. | agente (achado do revisor do G2) |
| 2026-11-12 | G2: o teste 18 (pasta temporária sem escrita) entra, e a contagem do fim da fase vai de 93 para 94. | A marca que não pôde ser criada conta como nova (o R3: só sai calado quando as marcas existem), e nada provava isso. | agente (achado do revisor do G2) |

## Estado para a retomada

Spec aprovada em 2026-11-12, com um commit por grupo na branch da fase. G1 e G2 feitos (revisor sem bloqueio, validador valida). Em andamento: G3.
